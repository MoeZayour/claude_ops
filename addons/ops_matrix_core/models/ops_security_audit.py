from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class OpsSecurityAudit(models.Model):
    """Log security-related events for audit purposes."""
    _name = 'ops.security.audit'
    _description = 'OPS Security Audit Log'
    _order = 'timestamp desc'
    _rec_name = 'event_type'
    
    # ========================================================================
    # FIELDS
    # ========================================================================
    
    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        required=True,
        readonly=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        readonly=True,
        ondelete='restrict'
    )
    
    event_type = fields.Selection([
        ('access_denied', 'Access Denied'),
        ('rule_violation', 'Rule Violation'),
        ('matrix_change', 'Matrix Access Change'),
        ('delegation_change', 'Delegation Change'),
        ('override_used', 'Security Override Used'),
        ('login_attempt', 'Login Attempt'),
        ('permission_escalation', 'Permission Escalation'),
        # Phase 5 additions
        ('session_created', 'Session Created'),
        ('session_closed', 'Session Closed'),
        ('session_suspicious', 'Suspicious Session Activity'),
        ('session_timeout', 'Session Timeout'),
        ('ip_blocked', 'IP Blocked'),
        ('ip_rule_created', 'IP Rule Created'),
        ('ip_rule_modified', 'IP Rule Modified'),
        ('ip_rule_deleted', 'IP Rule Deleted'),
        ('brute_force_detected', 'Brute Force Attack Detected'),
        ('data_archived', 'Data Archived'),
        ('performance_alert', 'Performance Alert'),
    ], string='Event Type', required=True, readonly=True)
    
    model_name = fields.Char(
        string='Model',
        readonly=True
    )
    
    record_id = fields.Integer(
        string='Record ID',
        readonly=True
    )
    
    record_name = fields.Char(
        string='Record Name',
        readonly=True
    )
    
    details = fields.Text(
        string='Event Details',
        readonly=True
    )
    
    ip_address = fields.Char(
        string='IP Address',
        readonly=True
    )
    
    session_id = fields.Char(
        string='Session ID',
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True
    )
    
    branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        readonly=True
    )
    
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        readonly=True
    )
    
    severity = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Severity', default='info', readonly=True)

    # ========================================================================
    # PHASE 5: ENHANCED AUDIT FIELDS
    # ========================================================================

    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ], string='Risk Level', compute='_compute_risk_level', store=True, index=True)

    status = fields.Selection([
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ], string='Status', default='open', index=True)

    assigned_to_user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        help='Security team member investigating this event'
    )

    resolution_notes = fields.Text(
        string='Resolution Notes',
        help='Notes about investigation and resolution'
    )

    resolved_date = fields.Datetime(
        string='Resolved Date',
        readonly=True
    )

    resolved_by_user_id = fields.Many2one(
        'res.users',
        string='Resolved By',
        readonly=True
    )

    related_audit_ids = fields.Many2many(
        'ops.security.audit',
        'ops_security_audit_related_rel',
        'audit_id',
        'related_audit_id',
        string='Related Events',
        help='Related security events (e.g., multiple failed logins from same IP)'
    )

    failed_login_count = fields.Integer(
        string='Failed Login Count',
        default=0,
        help='Number of failed login attempts (for brute force detection)'
    )
    
    # ========================================================================
    # COMPUTE METHODS
    # ========================================================================

    @api.depends('event_type', 'severity', 'failed_login_count')
    def _compute_risk_level(self):
        """Auto-classify risk level based on event type and context."""
        for audit in self:
            # Critical events
            if audit.event_type in ['override_used', 'permission_escalation',
                                   'brute_force_detected', 'session_suspicious']:
                audit.risk_level = 'critical'
            # High risk events
            elif audit.event_type in ['rule_violation', 'ip_rule_deleted'] or \
                 (audit.event_type == 'login_attempt' and audit.failed_login_count >= 5):
                audit.risk_level = 'high'
            # Medium risk events
            elif audit.event_type in ['access_denied', 'ip_blocked', 'session_timeout'] or \
                 audit.severity == 'critical':
                audit.risk_level = 'medium'
            # Low risk events
            else:
                audit.risk_level = 'low'

    # ========================================================================
    # LOGGING METHODS
    # ========================================================================
    
    @api.model
    def log_access_denied(self, model_name, record_id, details=None):
        """Log when access is denied to a record."""
        try:
            record = self.env[model_name].sudo().browse(record_id)
            record_name = record.display_name if record.exists() else f"ID: {record_id}"
            
            self.sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'access_denied',
                'model_name': model_name,
                'record_id': record_id,
                'record_name': record_name,
                'details': details or f"Access denied to {model_name} {record_name}",
                'ip_address': self._get_client_ip(),
                'session_id': self._get_session_id(),
                'company_id': self.env.company.id,
                'severity': 'warning',
            })
            
            _logger.warning(
                f"Access denied: User {self.env.user.name} (ID: {self.env.user.id}) "
                f"attempted to access {model_name} {record_name}"
            )
        except Exception as e:
            _logger.error(f"Failed to log access denial: {str(e)}")
    
    @api.model
    def log_matrix_change(self, target_user_id, details=None):
        """Log when matrix access rights change for a user."""
        try:
            target_user = self.env['res.users'].sudo().browse(target_user_id)
            
            self.sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'matrix_change',
                'model_name': 'res.users',
                'record_id': target_user_id,
                'record_name': target_user.name,
                'details': details or f"Matrix access changed for user {target_user.name}",
                'ip_address': self._get_client_ip(),
                'session_id': self._get_session_id(),
                'company_id': self.env.company.id,
                'severity': 'info',
            })
            
            _logger.info(
                f"Matrix change: User {self.env.user.name} modified access for {target_user.name}"
            )
        except Exception as e:
            _logger.error(f"Failed to log matrix change: {str(e)}")
    
    @api.model
    def log_delegation_change(self, delegation_id, action, details=None):
        """Log delegation creation, modification, or deletion."""
        try:
            delegation = self.env['ops.persona.delegation'].sudo().browse(delegation_id)
            
            self.sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'delegation_change',
                'model_name': 'ops.persona.delegation',
                'record_id': delegation_id,
                'record_name': delegation.display_name if delegation.exists() else f"ID: {delegation_id}",
                'details': details or f"Delegation {action}: {delegation.display_name}",
                'ip_address': self._get_client_ip(),
                'session_id': self._get_session_id(),
                'company_id': self.env.company.id,
                'severity': 'info',
            })
            
            _logger.info(
                f"Delegation {action}: User {self.env.user.name} performed {action} on delegation {delegation_id}"
            )
        except Exception as e:
            _logger.error(f"Failed to log delegation change: {str(e)}")
    
    @api.model
    def log_security_override(self, model_name, record_id, reason):
        """Log when a security override is used."""
        try:
            record = self.env[model_name].sudo().browse(record_id)
            
            self.sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'override_used',
                'model_name': model_name,
                'record_id': record_id,
                'record_name': record.display_name if record.exists() else f"ID: {record_id}",
                'details': f"Security override used: {reason}",
                'ip_address': self._get_client_ip(),
                'session_id': self._get_session_id(),
                'company_id': self.env.company.id,
                'severity': 'critical',
            })
            
            _logger.warning(
                f"Security override: User {self.env.user.name} used override on {model_name} {record_id}"
            )
        except Exception as e:
            _logger.error(f"Failed to log security override: {str(e)}")
    
    @api.model
    def log_rule_violation(self, rule_name, details):
        """Log when a security rule is violated."""
        try:
            self.sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'rule_violation',
                'details': f"Rule violation: {rule_name} - {details}",
                'ip_address': self._get_client_ip(),
                'session_id': self._get_session_id(),
                'company_id': self.env.company.id,
                'severity': 'critical',
            })
            
            _logger.error(
                f"Rule violation: User {self.env.user.name} violated rule {rule_name}"
            )
        except Exception as e:
            _logger.error(f"Failed to log rule violation: {str(e)}")
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @api.model
    def _get_client_ip(self):
        """Get client IP address from context or request."""
        # Try to get from context
        ip = self.env.context.get('remote_addr', 'Unknown')
        
        # Try to get from HTTP request
        try:
            from odoo.http import request
            if request and hasattr(request, 'httprequest'):
                ip = request.httprequest.environ.get('REMOTE_ADDR', ip)
        except:
            pass
        
        return ip
    
    @api.model
    def _get_session_id(self):
        """Get session ID from context or request."""
        # Try to get from HTTP request
        try:
            from odoo.http import request
            if request and hasattr(request, 'session'):
                return request.session.sid
        except:
            pass
        
        return 'CLI'
    
    # ========================================================================
    # REPORTING METHODS
    # ========================================================================
    
    @api.model
    def get_access_denied_summary(self, days=30):
        """Get summary of access denials in last N days."""
        date_from = fields.Datetime.now() - fields.timedelta(days=days)
        
        denials = self.search([
            ('event_type', '=', 'access_denied'),
            ('timestamp', '>=', date_from)
        ])
        
        summary = {
            'total': len(denials),
            'by_user': {},
            'by_model': {},
            'by_day': {},
        }
        
        for denial in denials:
            # By user
            user_name = denial.user_id.name
            summary['by_user'][user_name] = summary['by_user'].get(user_name, 0) + 1
            
            # By model
            model = denial.model_name or 'Unknown'
            summary['by_model'][model] = summary['by_model'].get(model, 0) + 1
            
            # By day
            day = denial.timestamp.date().isoformat()
            summary['by_day'][day] = summary['by_day'].get(day, 0) + 1
        
        return summary
    
    @api.model
    def get_critical_events(self, days=7):
        """Get critical security events in last N days."""
        date_from = fields.Datetime.now() - fields.timedelta(days=days)
        
        return self.search([
            ('severity', '=', 'critical'),
            ('timestamp', '>=', date_from)
        ], order='timestamp desc')
    
    @api.model
    def cleanup_old_logs(self, days=90):
        """Clean up audit logs older than N days."""
        date_threshold = fields.Datetime.now() - fields.timedelta(days=days)
        
        old_logs = self.search([
            ('timestamp', '<', date_threshold),
            ('severity', '!=', 'critical')  # Keep critical logs
        ])
        
        count = len(old_logs)
        # Use context flag to allow unlink during cleanup
        old_logs.with_context(audit_cleanup_mode=True).unlink()
        
        _logger.info(f"Cleaned up {count} old security audit logs")
        return count
    
    # ========================================================================
    # IMMUTABILITY ENFORCEMENT
    # ========================================================================
    
    def write(self, vals):
        """Override write to make audit logs mostly immutable, allow workflow fields."""
        # Allow updates to workflow/investigation fields
        allowed_fields = {'status', 'assigned_to_user_id', 'resolution_notes',
                         'resolved_date', 'resolved_by_user_id', 'related_audit_ids'}

        if not self.env.su and not all(key in allowed_fields for key in vals.keys()):
            raise UserError(_("Audit log entries cannot be modified after creation (except investigation fields)."))

        return super(OpsSecurityAudit, self).write(vals)
    
    def unlink(self):
        """Override unlink to make audit logs immutable except via cleanup."""
        # Allow unlinking only when called from cleanup_old_logs method
        # Check if we're in the cleanup context
        if not self.env.context.get('audit_cleanup_mode'):
            raise UserError(_("Audit log entries cannot be deleted manually. Use the automated cleanup process."))
        return super(OpsSecurityAudit, self).unlink()

    # ========================================================================
    # PHASE 5: ENHANCED AUDIT METHODS
    # ========================================================================

    @api.model
    def detect_brute_force(self, user_id=None, ip_address=None, window_minutes=15):
        """
        Detect brute force login attempts.

        Args:
            user_id: Check for specific user (optional)
            ip_address: Check for specific IP (optional)
            window_minutes: Time window to check (default 15 minutes)

        Returns:
            dict: Detection results with details
        """
        threshold_time = fields.Datetime.now() - fields.timedelta(minutes=window_minutes)

        domain = [
            ('event_type', '=', 'login_attempt'),
            ('timestamp', '>=', threshold_time),
            ('details', 'ilike', 'failed'),  # Only failed attempts
        ]

        if user_id:
            domain.append(('user_id', '=', user_id))
        if ip_address:
            domain.append(('ip_address', '=', ip_address))

        failed_attempts = self.search(domain)

        # Group by user and IP
        attempts_by_user = {}
        attempts_by_ip = {}

        for attempt in failed_attempts:
            # By user
            if attempt.user_id.id not in attempts_by_user:
                attempts_by_user[attempt.user_id.id] = []
            attempts_by_user[attempt.user_id.id].append(attempt)

            # By IP
            if attempt.ip_address:
                if attempt.ip_address not in attempts_by_ip:
                    attempts_by_ip[attempt.ip_address] = []
                attempts_by_ip[attempt.ip_address].append(attempt)

        # Detect brute force (5+ attempts in window)
        brute_force_threshold = 5
        detected = []

        for user_id, attempts in attempts_by_user.items():
            if len(attempts) >= brute_force_threshold:
                detected.append({
                    'type': 'user',
                    'user_id': user_id,
                    'attempt_count': len(attempts),
                    'ips': list(set([a.ip_address for a in attempts if a.ip_address]))
                })

                # Create brute force alert
                self.sudo().create({
                    'user_id': user_id,
                    'event_type': 'brute_force_detected',
                    'details': f"Brute force detected: {len(attempts)} failed login attempts in {window_minutes} minutes",
                    'severity': 'critical',
                    'failed_login_count': len(attempts),
                })

        for ip, attempts in attempts_by_ip.items():
            if len(attempts) >= brute_force_threshold:
                detected.append({
                    'type': 'ip',
                    'ip_address': ip,
                    'attempt_count': len(attempts),
                    'users': list(set([a.user_id.id for a in attempts]))
                })

        return {
            'detected': len(detected) > 0,
            'details': detected,
            'total_failed_attempts': len(failed_attempts),
        }

    def action_assign_to_me(self):
        """Assign this security event to current user for investigation."""
        self.ensure_one()

        self.write({
            'status': 'investigating',
            'assigned_to_user_id': self.env.user.id,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Assigned'),
                'message': _('Security event assigned to you for investigation.'),
                'type': 'success',
            }
        }

    def action_resolve(self):
        """Mark security event as resolved (wizard would be better)."""
        self.ensure_one()

        if self.status == 'resolved':
            raise UserError(_("This event is already resolved."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Resolve Security Event'),
            'res_model': 'ops.security.resolve.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_audit_id': self.id},
        }

    def action_mark_false_positive(self):
        """Mark event as false positive."""
        self.write({
            'status': 'false_positive',
            'resolved_date': fields.Datetime.now(),
            'resolved_by_user_id': self.env.user.id,
        })

    def action_view_related_events(self):
        """View related security events."""
        self.ensure_one()

        # Find related events (same user, similar time window, similar type)
        time_window = timedelta(hours=1)
        domain = [
            ('id', '!=', self.id),
            ('user_id', '=', self.user_id.id),
            ('timestamp', '>=', self.timestamp - time_window),
            ('timestamp', '<=', self.timestamp + time_window),
        ]

        return {
            'type': 'ir.actions.act_window',
            'name': _('Related Security Events'),
            'res_model': self._name,
            'view_mode': 'tree,form',
            'domain': domain,
        }

    @api.model
    def get_security_dashboard_data(self):
        """Get data for security dashboard."""
        now = fields.Datetime.now()

        return {
            'open_events': self.search_count([('status', '=', 'open')]),
            'critical_events_24h': self.search_count([
                ('risk_level', '=', 'critical'),
                ('timestamp', '>=', now - timedelta(hours=24)),
                ('status', '!=', 'resolved'),
            ]),
            'brute_force_24h': self.search_count([
                ('event_type', '=', 'brute_force_detected'),
                ('timestamp', '>=', now - timedelta(hours=24)),
            ]),
            'suspicious_sessions_24h': self.search_count([
                ('event_type', '=', 'session_suspicious'),
                ('timestamp', '>=', now - timedelta(hours=24)),
            ]),
            'ip_blocks_24h': self.search_count([
                ('event_type', '=', 'ip_blocked'),
                ('timestamp', '>=', now - timedelta(hours=24)),
            ]),
            'investigating': self.search_count([('status', '=', 'investigating')]),
        }


class OpsSecurityResolveWizard(models.TransientModel):
    """Wizard to resolve security events."""
    _name = 'ops.security.resolve.wizard'
    _description = 'Resolve Security Event'

    audit_id = fields.Many2one('ops.security.audit', string='Security Event', required=True)
    resolution_notes = fields.Text(string='Resolution Notes', required=True)

    def action_resolve(self):
        """Resolve the security event."""
        self.audit_id.write({
            'status': 'resolved',
            'resolution_notes': self.resolution_notes,
            'resolved_date': fields.Datetime.now(),
            'resolved_by_user_id': self.env.user.id,
        })

        return {'type': 'ir.actions.act_window_close'}
