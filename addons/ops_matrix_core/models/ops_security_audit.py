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
        """Override write to make audit logs immutable."""
        raise UserError(_("Audit log entries cannot be modified after creation."))
    
    def unlink(self):
        """Override unlink to make audit logs immutable except via cleanup."""
        # Allow unlinking only when called from cleanup_old_logs method
        # Check if we're in the cleanup context
        if not self.env.context.get('audit_cleanup_mode'):
            raise UserError(_("Audit log entries cannot be deleted manually. Use the automated cleanup process."))
        return super(OpsSecurityAudit, self).unlink()
