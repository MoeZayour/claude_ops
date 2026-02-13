# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsSessionManager(models.Model):
    """
    Enterprise Session Management System

    Features:
    - Track all active user sessions
    - Enforce session timeouts
    - Limit concurrent sessions per user
    - Detect suspicious activity (IP changes)
    - Force logout capability
    - Auto-cleanup expired sessions
    """
    _name = 'ops.session.manager'
    _description = 'OPS Session Manager'
    _order = 'last_activity desc'
    _rec_name = 'session_id'

    # ========================================================================
    # FIELDS
    # ========================================================================

    session_id = fields.Char(
        string='Session ID',
        required=True,
        readonly=True,
        index=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        readonly=True,
        ondelete='cascade',
        index=True
    )

    ip_address = fields.Char(
        string='IP Address',
        readonly=True,
        index=True
    )

    user_agent = fields.Char(
        string='User Agent',
        readonly=True
    )

    login_time = fields.Datetime(
        string='Login Time',
        required=True,
        readonly=True,
        default=fields.Datetime.now
    )

    last_activity = fields.Datetime(
        string='Last Activity',
        required=True,
        readonly=True,
        default=fields.Datetime.now,
        index=True
    )

    is_active = fields.Boolean(
        string='Active',
        default=True,
        index=True
    )

    logout_time = fields.Datetime(
        string='Logout Time',
        readonly=True
    )

    logout_reason = fields.Selection([
        ('normal', 'Normal Logout'),
        ('timeout', 'Session Timeout'),
        ('forced', 'Forced Logout'),
        ('concurrent_limit', 'Concurrent Session Limit'),
        ('suspicious', 'Suspicious Activity'),
        ('expired', 'Auto Cleanup'),
    ], string='Logout Reason', readonly=True)

    ip_changes = fields.Integer(
        string='IP Changes',
        default=0,
        readonly=True,
        help='Number of times IP address changed during session'
    )

    is_suspicious = fields.Boolean(
        string='Suspicious Activity',
        default=False,
        index=True,
        help='Flagged for suspicious activity'
    )

    suspicious_reason = fields.Text(
        string='Suspicious Reason',
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True
    )

    forced_by_user_id = fields.Many2one(
        'res.users',
        string='Forced By',
        readonly=True,
        help='User who forced logout'
    )

    session_duration = fields.Integer(
        string='Duration (minutes)',
        compute='_compute_session_duration',
        store=True
    )

    # ========================================================================
    # COMPUTE METHODS
    # ========================================================================

    @api.depends('login_time', 'logout_time', 'last_activity')
    def _compute_session_duration(self):
        """Calculate session duration in minutes."""
        for session in self:
            if session.logout_time:
                delta = session.logout_time - session.login_time
            elif session.is_active:
                delta = session.last_activity - session.login_time
            else:
                delta = timedelta(0)

            session.session_duration = int(delta.total_seconds() / 60)

    # ========================================================================
    # SESSION TRACKING
    # ========================================================================

    @api.model
    def track_session(self, session_id, user_id, ip_address=None, user_agent=None):
        """
        Track or update a session.
        Called on each request to update last activity.

        Returns:
            tuple: (session_record, is_new)
        """
        # Get or create session
        session = self.search([
            ('session_id', '=', session_id),
            ('user_id', '=', user_id),
            ('is_active', '=', True)
        ], limit=1)

        now = fields.Datetime.now()

        if session:
            # Update existing session
            updates = {'last_activity': now}

            # Check for IP change
            if ip_address and session.ip_address and ip_address != session.ip_address:
                updates['ip_changes'] = session.ip_changes + 1
                updates['ip_address'] = ip_address

                # Flag as suspicious if too many IP changes
                if updates['ip_changes'] >= 3:
                    updates['is_suspicious'] = True
                    updates['suspicious_reason'] = f"Multiple IP changes detected: {updates['ip_changes']}"

                    # Log security event
                    self.env['ops.security.audit'].sudo().create({
                        'user_id': user_id,
                        'event_type': 'session_suspicious',
                        'details': f"Session {session_id} flagged: {updates['suspicious_reason']}",
                        'ip_address': ip_address,
                        'session_id': session_id,
                        'severity': 'critical',
                    })

            session.sudo().write(updates)
            return session, False
        else:
            # Check concurrent session limit
            self._check_concurrent_limit(user_id)

            # Create new session
            session = self.sudo().create({
                'session_id': session_id,
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'login_time': now,
                'last_activity': now,
                'company_id': self.env.company.id,
            })

            # Log session creation
            self.env['ops.security.audit'].sudo().create({
                'user_id': user_id,
                'event_type': 'session_created',
                'details': f"New session created from IP {ip_address}",
                'ip_address': ip_address,
                'session_id': session_id,
                'severity': 'info',
            })

            return session, True

    @api.model
    def _check_concurrent_limit(self, user_id):
        """
        Check if user has exceeded concurrent session limit.
        Closes oldest sessions if limit exceeded.
        """
        # Get config
        config = self.env['ir.config_parameter'].sudo()
        max_concurrent = int(config.get_param('ops.session.max_concurrent', default=5))

        # Count active sessions
        active_sessions = self.search([
            ('user_id', '=', user_id),
            ('is_active', '=', True)
        ], order='last_activity desc')

        if len(active_sessions) >= max_concurrent:
            # Close oldest sessions
            sessions_to_close = active_sessions[max_concurrent-1:]
            for session in sessions_to_close:
                session.sudo().close_session('concurrent_limit')

            _logger.warning(
                f"User {user_id} exceeded concurrent session limit. "
                f"Closed {len(sessions_to_close)} oldest sessions."
            )

    # ========================================================================
    # SESSION TIMEOUT ENFORCEMENT
    # ========================================================================

    @api.model
    def check_session_timeout(self, session_id, user_id):
        """
        Check if session has timed out.

        Returns:
            bool: True if session is valid, False if timed out
        """
        session = self.search([
            ('session_id', '=', session_id),
            ('user_id', '=', user_id),
            ('is_active', '=', True)
        ], limit=1)

        if not session:
            return False

        # Get timeout config (in minutes)
        config = self.env['ir.config_parameter'].sudo()
        timeout_minutes = int(config.get_param('ops.session.timeout_minutes', default=60))

        # Check timeout
        now = fields.Datetime.now()
        timeout_delta = timedelta(minutes=timeout_minutes)

        if (now - session.last_activity) > timeout_delta:
            # Session timed out
            session.sudo().close_session('timeout')

            _logger.info(f"Session {session_id} timed out after {timeout_minutes} minutes of inactivity")
            return False

        return True

    # ========================================================================
    # SESSION CLOSURE
    # ========================================================================

    def close_session(self, reason='normal'):
        """Close session with specified reason."""
        self.ensure_one()

        if not self.is_active:
            return

        self.sudo().write({
            'is_active': False,
            'logout_time': fields.Datetime.now(),
            'logout_reason': reason,
        })

        # Log session closure
        self.env['ops.security.audit'].sudo().create({
            'user_id': self.user_id.id,
            'event_type': 'session_closed',
            'details': f"Session closed: {dict(self._fields['logout_reason'].selection).get(reason)}",
            'ip_address': self.ip_address,
            'session_id': self.session_id,
            'severity': 'info' if reason == 'normal' else 'warning',
        })

    def action_force_logout(self):
        """
        Force logout session (admin action).
        Requires admin permissions.
        """
        self.ensure_one()

        # Check permissions
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only system administrators can force logout sessions."))

        if not self.is_active:
            raise UserError(_("Session is already closed."))

        # Record who forced the logout
        self.sudo().write({
            'forced_by_user_id': self.env.user.id,
        })

        self.close_session('forced')

        _logger.warning(
            f"Admin {self.env.user.name} forced logout of session {self.session_id} "
            f"for user {self.user_id.name}"
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Session Closed'),
                'message': _('Session has been forcefully terminated.'),
                'type': 'success',
                'sticky': False,
            }
        }

    # ========================================================================
    # CLEANUP & MAINTENANCE
    # ========================================================================

    @api.model
    def cleanup_expired_sessions(self):
        """
        Auto-cleanup expired sessions.
        Called by cron job.
        """
        # Get timeout config
        config = self.env['ir.config_parameter'].sudo()
        timeout_minutes = int(config.get_param('ops.session.timeout_minutes', default=60))

        # Find expired sessions
        timeout_threshold = fields.Datetime.now() - timedelta(minutes=timeout_minutes)

        expired_sessions = self.search([
            ('is_active', '=', True),
            ('last_activity', '<', timeout_threshold)
        ])

        count = len(expired_sessions)

        # Close expired sessions
        for session in expired_sessions:
            session.close_session('expired')

        _logger.info(f"Cleaned up {count} expired sessions")

        return count

    @api.model
    def cleanup_old_records(self, days=90):
        """
        Clean up old session records.
        Keep suspicious sessions indefinitely.
        """
        threshold_date = fields.Datetime.now() - timedelta(days=days)

        old_sessions = self.search([
            ('is_active', '=', False),
            ('logout_time', '<', threshold_date),
            ('is_suspicious', '=', False),  # Keep suspicious sessions
        ])

        count = len(old_sessions)
        old_sessions.unlink()

        _logger.info(f"Cleaned up {count} old session records (>{days} days)")

        return count

    # ========================================================================
    # REPORTING & ANALYTICS
    # ========================================================================

    @api.model
    def get_active_sessions_count(self):
        """Get count of active sessions."""
        return self.search_count([('is_active', '=', True)])

    @api.model
    def get_user_active_sessions(self, user_id):
        """Get active sessions for a specific user."""
        return self.search([
            ('user_id', '=', user_id),
            ('is_active', '=', True)
        ], order='last_activity desc')

    @api.model
    def get_suspicious_sessions(self, days=7):
        """Get suspicious sessions in last N days."""
        date_from = fields.Datetime.now() - timedelta(days=days)

        return self.search([
            ('is_suspicious', '=', True),
            ('login_time', '>=', date_from)
        ], order='login_time desc')

    @api.model
    def get_session_statistics(self):
        """Get session statistics for dashboard."""
        now = fields.Datetime.now()

        return {
            'active_sessions': self.search_count([('is_active', '=', True)]),
            'suspicious_sessions_24h': self.search_count([
                ('is_suspicious', '=', True),
                ('login_time', '>=', now - timedelta(hours=24))
            ]),
            'forced_logouts_24h': self.search_count([
                ('logout_reason', '=', 'forced'),
                ('logout_time', '>=', now - timedelta(hours=24))
            ]),
            'timeout_logouts_24h': self.search_count([
                ('logout_reason', '=', 'timeout'),
                ('logout_time', '>=', now - timedelta(hours=24))
            ]),
            'avg_session_duration': self._get_avg_session_duration(),
        }

    def _get_avg_session_duration(self):
        """Calculate average session duration in minutes."""
        self.env.cr.execute("""
            SELECT AVG(session_duration)
            FROM ops_session_manager
            WHERE logout_time >= NOW() - INTERVAL '7 days'
            AND is_active = FALSE
        """)

        result = self.env.cr.fetchone()
        return int(result[0]) if result and result[0] else 0

    # ========================================================================
    # SECURITY
    # ========================================================================

    def write(self, vals):
        """Restrict updates to specific fields."""
        # Only allow updates to tracking fields
        allowed_fields = {'last_activity', 'ip_address', 'ip_changes',
                         'is_suspicious', 'suspicious_reason', 'is_active',
                         'logout_time', 'logout_reason', 'forced_by_user_id'}

        if not self.env.su and not all(key in allowed_fields for key in vals.keys()):
            raise UserError(_("Session records can only be updated by the system."))

        return super(OpsSessionManager, self).write(vals)

    def unlink(self):
        """Prevent deletion of suspicious sessions."""
        if any(session.is_suspicious for session in self):
            raise UserError(_("Suspicious session records cannot be deleted."))

        return super(OpsSessionManager, self).unlink()
