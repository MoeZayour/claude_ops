# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class OpsCorporateAuditLog(models.Model):
    """
    Corporate Audit Log - Comprehensive CRUD & Event Tracking
    
    Complements existing specialized logs:
    - ops.audit.log (API requests)
    - ops.report.audit (report generation)
    - ops.security.audit (security events)
    - ops.segregation.of.duties.log (SoD violations)
    
    This model provides:
    - General CRUD operation logging
    - Authentication event tracking
    - Field-level change history
    - Financial compliance audit trail
    - Approval workflow audit
    - Data export tracking
    """
    _name = 'ops.corporate.audit.log'
    _description = 'OPS Corporate Audit Log'
    _order = 'create_date desc, id desc'
    _rec_name = 'display_name'
    
    # =========================================================================
    # CORE IDENTIFICATION
    # =========================================================================
    
    name = fields.Char(
        string='Reference',
        readonly=True,
        copy=False,
        default=lambda self: _('New')
    )
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True
    )
    
    # =========================================================================
    # EVENT CLASSIFICATION
    # =========================================================================
    
    event_type = fields.Selection([
        # Authentication
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('login_failed', 'Failed Login Attempt'),
        ('password_change', 'Password Changed'),
        ('session_timeout', 'Session Timeout'),
        # CRUD Operations
        ('create', 'Record Created'),
        ('write', 'Record Modified'),
        ('unlink', 'Record Deleted'),
        ('read', 'Sensitive Data Accessed'),
        # Data Operations
        ('export', 'Data Exported'),
        ('import', 'Data Imported'),
        ('print', 'Document Printed'),
        # Workflow
        ('approval', 'Approval Granted'),
        ('rejection', 'Approval Rejected'),
        ('recall', 'Approval Recalled'),
        ('state_change', 'Workflow State Change'),
        ('escalation', 'Approval Escalated'),
        # Financial
        ('price_change', 'Price/Amount Changed'),
        ('discount_change', 'Discount Modified'),
        ('payment', 'Payment Processed'),
        ('reversal', 'Transaction Reversed'),
        # Security
        ('permission_change', 'Permission Modified'),
        ('group_change', 'Group Assignment Changed'),
        ('sod_violation', 'SoD Violation Blocked'),
        ('branch_violation', 'Branch Access Blocked'),
        # Configuration
        ('config_change', 'System Configuration Changed'),
        ('rule_change', 'Business Rule Modified'),
        # API (links to ops.audit.log)
        ('api_call', 'API Request'),
        # Other
        ('custom', 'Custom Event'),
    ], string='Event Type', required=True, index=True)
    
    event_category = fields.Selection([
        ('authentication', 'Authentication'),
        ('data', 'Data Operation'),
        ('workflow', 'Workflow'),
        ('financial', 'Financial'),
        ('security', 'Security'),
        ('configuration', 'Configuration'),
        ('api', 'API'),
        ('other', 'Other'),
    ], string='Event Category', compute='_compute_event_category', store=True)
    
    severity = fields.Selection([
        ('debug', 'Debug'),
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ], string='Severity', default='info', index=True)
    
    # =========================================================================
    # USER CONTEXT
    # =========================================================================
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        index=True,
        readonly=True,
        ondelete='set null'
    )
    user_login = fields.Char(string='Username', readonly=True, index=True)
    user_name = fields.Char(string='User Full Name', readonly=True)
    
    # Session context
    session_id = fields.Char(string='Session ID', readonly=True)
    ip_address = fields.Char(string='IP Address', index=True, readonly=True)
    user_agent = fields.Char(string='User Agent', readonly=True)
    
    # Organizational context
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        index=True,
        readonly=True,
        ondelete='set null'
    )
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        index=True,
        readonly=True,
        ondelete='set null'
    )
    persona_id = fields.Many2one(
        'ops.persona',
        string='Persona',
        readonly=True,
        ondelete='set null'
    )
    
    # =========================================================================
    # TARGET RESOURCE
    # =========================================================================
    
    res_model = fields.Char(string='Model', index=True, readonly=True)
    res_model_name = fields.Char(string='Model Description', readonly=True)
    res_id = fields.Integer(string='Record ID', index=True, readonly=True)
    res_name = fields.Char(string='Record Name', readonly=True)
    res_reference = fields.Char(
        string='Record Reference',
        compute='_compute_res_reference',
        store=True
    )
    
    # =========================================================================
    # EVENT DETAILS
    # =========================================================================
    
    action = fields.Char(string='Action', readonly=True)
    description = fields.Text(string='Description', readonly=True)
    
    # Field-level change tracking
    changed_fields = fields.Char(string='Changed Fields', readonly=True)
    old_values = fields.Text(string='Old Values (JSON)', readonly=True)
    new_values = fields.Text(string='New Values (JSON)', readonly=True)
    
    # Computed change summary
    change_summary = fields.Text(
        string='Change Summary',
        compute='_compute_change_summary'
    )
    
    # =========================================================================
    # COMPLIANCE
    # =========================================================================
    
    compliance_category = fields.Selection([
        ('sox', 'SOX Compliance'),
        ('gdpr', 'GDPR/Privacy'),
        ('iso27001', 'ISO 27001'),
        ('financial', 'Financial Control'),
        ('operational', 'Operational'),
        ('none', 'No Specific Category'),
    ], string='Compliance Category', default='none', index=True)
    
    requires_review = fields.Boolean(
        string='Requires Review',
        default=False,
        index=True,
        help='Flag for events requiring human review'
    )
    reviewed = fields.Boolean(
        string='Reviewed',
        default=False,
        index=True
    )
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By',
        ondelete='set null'
    )
    reviewed_date = fields.Datetime(string='Review Date')
    review_notes = fields.Text(string='Review Notes')
    
    # =========================================================================
    # LINKING
    # =========================================================================
    
    # Link to related audit logs
    api_audit_id = fields.Many2one(
        'ops.audit.log',
        string='Related API Log',
        readonly=True,
        ondelete='set null'
    )
    security_audit_id = fields.Many2one(
        'ops.security.audit',
        string='Related Security Log',
        readonly=True,
        ondelete='set null'
    )
    
    # =========================================================================
    # COMPUTED FIELDS
    # =========================================================================
    
    @api.depends('event_type', 'user_login', 'res_model', 'create_date')
    def _compute_display_name(self):
        for record in self:
            parts = [
                record.event_type or 'unknown',
                record.res_model or 'system',
                record.user_login or 'anonymous',
            ]
            record.display_name = ' - '.join(parts)
    
    @api.depends('event_type')
    def _compute_event_category(self):
        category_map = {
            'login': 'authentication',
            'logout': 'authentication',
            'login_failed': 'authentication',
            'password_change': 'authentication',
            'session_timeout': 'authentication',
            'create': 'data',
            'write': 'data',
            'unlink': 'data',
            'read': 'data',
            'export': 'data',
            'import': 'data',
            'print': 'data',
            'approval': 'workflow',
            'rejection': 'workflow',
            'recall': 'workflow',
            'state_change': 'workflow',
            'escalation': 'workflow',
            'price_change': 'financial',
            'discount_change': 'financial',
            'payment': 'financial',
            'reversal': 'financial',
            'permission_change': 'security',
            'group_change': 'security',
            'sod_violation': 'security',
            'branch_violation': 'security',
            'config_change': 'configuration',
            'rule_change': 'configuration',
            'api_call': 'api',
        }
        for record in self:
            record.event_category = category_map.get(record.event_type, 'other')
    
    @api.depends('res_model', 'res_id', 'res_name')
    def _compute_res_reference(self):
        for record in self:
            if record.res_model and record.res_id:
                record.res_reference = f"{record.res_model},{record.res_id}"
            else:
                record.res_reference = False
    
    @api.depends('old_values', 'new_values', 'changed_fields')
    def _compute_change_summary(self):
        for record in self:
            if not record.changed_fields:
                record.change_summary = False
                continue
            
            try:
                old = json.loads(record.old_values or '{}')
                new = json.loads(record.new_values or '{}')
                fields_list = record.changed_fields.split(',') if record.changed_fields else []
                
                lines = []
                for field in fields_list:
                    old_val = old.get(field, 'N/A')
                    new_val = new.get(field, 'N/A')
                    lines.append(f"• {field}: {old_val} → {new_val}")
                
                record.change_summary = '\n'.join(lines) if lines else False
            except Exception:
                _logger.debug('Failed to compute change summary for audit log %s', record.id, exc_info=True)
                record.change_summary = record.changed_fields
    
    # =========================================================================
    # CRUD OVERRIDES (IMMUTABILITY)
    # =========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ops.corporate.audit.log'
                ) or _('AUDIT-NEW')
        return super().create(vals_list)
    
    def write(self, vals):
        """Only allow review-related fields to be modified."""
        allowed_fields = {
            'reviewed', 'reviewed_by', 'reviewed_date', 'review_notes',
            'requires_review'  # Allow admin to unflag
        }
        
        # Check if trying to modify non-allowed fields
        if not self.env.user.has_group('base.group_system'):
            restricted_fields = set(vals.keys()) - allowed_fields
            if restricted_fields:
                raise UserError(_(
                    "Audit logs are immutable. Only review fields can be modified.\n"
                    "Attempted to modify: %s"
                ) % ', '.join(restricted_fields))
        
        return super().write(vals)
    
    def unlink(self):
        """Prevent deletion of audit logs."""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_(
                "Audit logs cannot be deleted for compliance reasons."
            ))
        
        # Even system admin gets a warning
        _logger.warning(
            "AUDIT LOG DELETION by %s: %s records",
            self.env.user.login,
            len(self)
        )
        return super().unlink()
    
    # =========================================================================
    # LOGGING METHODS (Primary Interface)
    # =========================================================================
    
    @api.model
    def log_event(self, event_type, **kwargs):
        """
        Central logging method for all audit events.
        
        Args:
            event_type: One of the defined event types
            **kwargs:
                res_model: Target model name
                res_id: Target record ID
                res_name: Target record display name
                action: Specific action taken
                description: Human-readable description
                old_values: Dict of old field values
                new_values: Dict of new field values
                changed_fields: List of changed field names
                severity: debug/info/warning/error/critical
                compliance_category: sox/gdpr/iso27001/financial/operational
                requires_review: Boolean
                
        Returns:
            Created audit log record (or False if logging fails silently)
        """
        try:
            user = self.env.user
            
            # Get HTTP request context if available
            ip_address = None
            user_agent = None
            session_id = None
            
            try:
                from odoo.http import request
                if request and hasattr(request, 'httprequest'):
                    ip_address = request.httprequest.remote_addr
                    if request.httprequest.user_agent:
                        user_agent = str(request.httprequest.user_agent)[:500]
                    if hasattr(request, 'session') and request.session:
                        session_id = request.session.sid
            except Exception:
                _logger.debug('Failed to retrieve HTTP request context for audit log', exc_info=True)
                pass  # Not in HTTP context
            
            # Get branch/persona if available
            branch_id = False
            persona_id = False
            if hasattr(user, 'ops_branch_id') and user.ops_branch_id:
                branch_id = user.ops_branch_id.id
            if hasattr(user, 'ops_persona_id') and user.ops_persona_id:
                persona_id = user.ops_persona_id.id
            
            # Get model description
            res_model = kwargs.get('res_model')
            res_model_name = None
            if res_model:
                try:
                    model_obj = self.env['ir.model'].sudo().search(
                        [('model', '=', res_model)], limit=1
                    )
                    if model_obj:
                        res_model_name = model_obj.name
                except Exception:
                    _logger.debug('Failed to look up model description for %s', res_model, exc_info=True)
                    res_model_name = res_model
            
            # Serialize values
            old_values = kwargs.get('old_values')
            new_values = kwargs.get('new_values')
            changed_fields = kwargs.get('changed_fields', [])
            
            vals = {
                'event_type': event_type,
                'user_id': user.id,
                'user_login': user.login,
                'user_name': user.name,
                'company_id': user.company_id.id if user.company_id else False,
                'branch_id': branch_id,
                'persona_id': persona_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_id': session_id,
                'res_model': res_model,
                'res_model_name': res_model_name or kwargs.get('res_model_name'),
                'res_id': kwargs.get('res_id'),
                'res_name': kwargs.get('res_name'),
                'action': kwargs.get('action'),
                'description': kwargs.get('description'),
                'old_values': json.dumps(old_values) if old_values else None,
                'new_values': json.dumps(new_values) if new_values else None,
                'changed_fields': ','.join(changed_fields) if changed_fields else None,
                'severity': kwargs.get('severity', 'info'),
                'compliance_category': kwargs.get('compliance_category', 'none'),
                'requires_review': kwargs.get('requires_review', False),
            }
            
            # Use sudo to ensure logging always succeeds
            return self.sudo().create(vals)
            
        except Exception as e:
            _logger.error("Failed to create audit log: %s", str(e))
            return False
    
    @api.model
    def log_crud(self, operation, model, record_id, record_name=None,
                 old_values=None, new_values=None, changed_fields=None):
        """Convenience method for CRUD operations."""
        return self.log_event(
            operation,
            res_model=model,
            res_id=record_id,
            res_name=record_name,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            compliance_category='operational'
        )
    
    @api.model
    def log_authentication(self, event_type, success=True, username=None, reason=None):
        """Log authentication events."""
        severity = 'info' if success else 'warning'
        if event_type == 'login_failed':
            severity = 'warning'
        
        return self.log_event(
            event_type,
            action=f"Authentication: {event_type}",
            description=reason or f"{event_type} - {'success' if success else 'failed'}",
            severity=severity,
            compliance_category='iso27001',
            requires_review=not success  # Review failed attempts
        )
    
    @api.model
    def log_financial_change(self, model, record_id, record_name, field_name,
                             old_value, new_value):
        """Log financial field changes for SOX compliance."""
        return self.log_event(
            'price_change' if 'price' in field_name.lower() else 'write',
            res_model=model,
            res_id=record_id,
            res_name=record_name,
            old_values={field_name: old_value},
            new_values={field_name: new_value},
            changed_fields=[field_name],
            description=f"Financial change: {field_name} from {old_value} to {new_value}",
            severity='info',
            compliance_category='sox',
            requires_review=True  # All financial changes need review
        )
    
    @api.model
    def log_approval(self, event_type, model, record_id, record_name, approver=None):
        """Log approval workflow events."""
        return self.log_event(
            event_type,
            res_model=model,
            res_id=record_id,
            res_name=record_name,
            action=f"Approval: {event_type}",
            description=f"{event_type} by {approver or self.env.user.name}",
            compliance_category='sox',
            requires_review=event_type in ('rejection', 'recall')
        )
    
    @api.model
    def log_export(self, model, record_count, export_format, filters=None):
        """Log data export events."""
        return self.log_event(
            'export',
            res_model=model,
            action=f"Export to {export_format}",
            description=f"Exported {record_count} records from {model} ({export_format})",
            new_values={'format': export_format, 'count': record_count, 'filters': filters},
            severity='info',
            compliance_category='gdpr',
            requires_review=record_count > 1000  # Review large exports
        )
    
    # =========================================================================
    # REVIEW ACTIONS
    # =========================================================================
    
    def action_mark_reviewed(self):
        """Mark log entry as reviewed."""
        self.write({
            'reviewed': True,
            'reviewed_by': self.env.user.id,
            'reviewed_date': fields.Datetime.now(),
        })
    
    def action_request_review(self):
        """Flag entry for review."""
        self.write({
            'requires_review': True,
            'reviewed': False,
        })
    
    # =========================================================================
    # ANALYTICS & REPORTING
    # =========================================================================
    
    @api.model
    def get_activity_summary(self, days=7, user_id=None):
        """Get activity summary for dashboard."""
        date_from = fields.Datetime.now() - timedelta(days=days)
        domain = [('create_date', '>=', date_from)]
        if user_id:
            domain.append(('user_id', '=', user_id))
        
        logs = self.search(domain)
        
        return {
            'total_events': len(logs),
            'by_type': dict(logs.read_group(domain, ['event_type'], ['event_type'])),
            'by_category': dict(logs.read_group(domain, ['event_category'], ['event_category'])),
            'requires_review': len(logs.filtered(lambda l: l.requires_review and not l.reviewed)),
            'critical_events': len(logs.filtered(lambda l: l.severity in ('error', 'critical'))),
        }
    
    @api.model
    def cleanup_old_logs(self, days=365):
        """Archive or delete logs older than specified days."""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only system administrators can cleanup audit logs."))
        
        cutoff = fields.Datetime.now() - timedelta(days=days)
        
        # Never delete compliance-critical logs
        old_logs = self.search([
            ('create_date', '<', cutoff),
            ('compliance_category', 'in', ['none', 'operational']),
            ('severity', 'in', ['debug', 'info']),
        ])
        
        count = len(old_logs)
        if count > 0:
            _logger.info("Cleaning up %d old audit logs", count)
            old_logs.sudo().unlink()
        
        return count
