# -*- coding: utf-8 -*-

"""
OPS Matrix API Audit Log
Comprehensive audit logging for all API requests
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsAuditLog(models.Model):
    """
    API Audit Log Model for OPS Matrix Framework
    
    Records all API requests for security auditing, compliance, and debugging.
    This is a read-only model from the UI perspective - logs are created by
    the API controller automatically.
    """
    _name = 'ops.audit.log'
    _description = 'OPS Matrix API Audit Log'
    _order = 'timestamp desc'
    _rec_name = 'endpoint'
    
    # Disable standard tracking
    _log_access = True
    
    # ========================================================================
    # FIELDS
    # ========================================================================
    
    timestamp = fields.Datetime(
        string='Timestamp',
        required=True,
        default=fields.Datetime.now,
        index=True,  # Index for performance on time-based queries
        readonly=True,
        help='When the API request was made'
    )
    
    api_key_id = fields.Many2one(
        'ops.api.key',
        string='API Key',
        ondelete='set null',
        index=True,
        readonly=True,
        help='The API key used for this request'
    )
    
    persona_id = fields.Many2one(
        'ops.persona',
        string='Persona',
        ondelete='set null',
        index=True,
        readonly=True,
        help='The persona associated with the API key'
    )
    
    endpoint = fields.Char(
        string='API Endpoint',
        required=True,
        index=True,
        readonly=True,
        help='The API endpoint URL that was called'
    )
    
    http_method = fields.Selection(
        [
            ('GET', 'GET'),
            ('POST', 'POST'),
            ('PUT', 'PUT'),
            ('DELETE', 'DELETE'),
            ('PATCH', 'PATCH'),
            ('OPTIONS', 'OPTIONS'),
            ('HEAD', 'HEAD')
        ],
        string='HTTP Method',
        required=True,
        readonly=True,
        index=True,
        help='HTTP method used for the request'
    )
    
    ip_address = fields.Char(
        string='IP Address',
        readonly=True,
        index=True,
        help='Client IP address that made the request'
    )
    
    user_agent = fields.Text(
        string='User Agent',
        readonly=True,
        help='Client user agent string'
    )
    
    status_code = fields.Integer(
        string='HTTP Status Code',
        readonly=True,
        index=True,
        help='HTTP response status code (200, 401, 500, etc.)'
    )
    
    response_time = fields.Float(
        string='Response Time (seconds)',
        readonly=True,
        digits=(10, 4),
        help='Time taken to process the request in seconds'
    )
    
    error_message = fields.Text(
        string='Error Message',
        readonly=True,
        help='Error message if the request failed'
    )
    
    # Additional context
    request_params = fields.Text(
        string='Request Parameters',
        readonly=True,
        help='Query parameters or request body (sanitized)'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        index=True,
        help='Company context at time of request'
    )
    
    # Computed fields for analytics
    success = fields.Boolean(
        string='Success',
        compute='_compute_success',
        store=True,
        readonly=True,
        help='Whether the request was successful (status code 200-299)'
    )
    
    date = fields.Date(
        string='Date',
        compute='_compute_date',
        store=True,
        index=True,
        readonly=True,
        help='Date of the request (for daily analytics)'
    )
    
    # ========================================================================
    # COMPUTE METHODS
    # ========================================================================
    
    @api.depends('status_code')
    def _compute_success(self):
        """
        Determine if request was successful based on status code
        2xx status codes are considered successful
        """
        for record in self:
            record.success = 200 <= (record.status_code or 0) < 300
    
    @api.depends('timestamp')
    def _compute_date(self):
        """
        Extract date from timestamp for easier daily analytics
        """
        for record in self:
            record.date = record.timestamp.date() if record.timestamp else False
    
    # ========================================================================
    # CONSTRAINTS
    # ========================================================================
    
    _sql_constraints = [
        ('check_status_code', 'CHECK(status_code >= 100 AND status_code < 600)', 
         'Invalid HTTP status code!'),
        ('check_response_time', 'CHECK(response_time >= 0)', 
         'Response time cannot be negative!')
    ]
    
    # ========================================================================
    # ORM METHODS
    # ========================================================================
    
    @api.model
    def create(self, vals):
        """
        Override create to ensure audit log integrity
        """
        # Always mark as readonly after creation
        record = super(OpsAuditLog, self).create(vals)
        
        _logger.debug(
            f"Audit log created: {record.endpoint} [{record.http_method}] "
            f"Status: {record.status_code} IP: {record.ip_address}"
        )
        
        return record
    
    def write(self, vals):
        """
        Prevent modification of audit logs (integrity requirement)
        """
        if self.env.user.has_group('base.group_system'):
            # Only allow system admin to modify (for data correction if needed)
            _logger.warning(
                f"Audit log modified by system admin {self.env.user.name}: "
                f"IDs {self.ids}"
            )
            return super(OpsAuditLog, self).write(vals)
        else:
            raise UserError(_('Audit logs cannot be modified to maintain integrity.'))
    
    def unlink(self):
        """
        Prevent deletion of audit logs (except by system admin)
        """
        if self.env.user.has_group('base.group_system'):
            _logger.warning(
                f"Audit logs deleted by system admin {self.env.user.name}: "
                f"IDs {self.ids}"
            )
            return super(OpsAuditLog, self).unlink()
        else:
            raise UserError(_('Audit logs cannot be deleted to maintain integrity.'))
    
    # ========================================================================
    # BUSINESS METHODS
    # ========================================================================
    
    @api.model
    def log_api_request(self, api_key_id=None, endpoint=None, http_method=None,
                       ip_address=None, user_agent=None, status_code=None,
                       response_time=None, error_message=None, request_params=None):
        """
        Create an audit log entry for an API request
        
        This is the main method called by the API controller to log requests.
        
        Args:
            api_key_id (int): ID of the API key used
            endpoint (str): API endpoint URL
            http_method (str): HTTP method (GET, POST, etc.)
            ip_address (str): Client IP address
            user_agent (str): Client user agent
            status_code (int): HTTP response status code
            response_time (float): Request processing time in seconds
            error_message (str): Error message if any
            request_params (str): Request parameters (sanitized)
            
        Returns:
            ops.audit.log: Created audit log record
        """
        vals = {
            'timestamp': fields.Datetime.now(),
            'endpoint': endpoint,
            'http_method': http_method,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'status_code': status_code,
            'response_time': response_time,
            'error_message': error_message,
            'request_params': request_params,
        }
        
        # Add API key and persona if provided
        if api_key_id:
            vals['api_key_id'] = api_key_id
            api_key = self.env['ops.api.key'].sudo().browse(api_key_id)
            if api_key.exists():
                vals['persona_id'] = api_key.persona_id.id
                vals['company_id'] = api_key.company_id.id
        
        # Create log entry using sudo to bypass permissions
        return self.sudo().create(vals)
    
    @api.model
    def cleanup_old_logs(self, days=90):
        """
        Clean up audit logs older than specified days
        
        This should be called by a scheduled action (cron job)
        
        Args:
            days (int): Number of days to retain logs (default 90)
            
        Returns:
            int: Number of logs deleted
        """
        cutoff_date = fields.Datetime.now() - fields.Datetime.to_datetime(f'{days} days')
        
        old_logs = self.sudo().search([('timestamp', '<', cutoff_date)])
        count = len(old_logs)
        
        if count > 0:
            _logger.info(f"Cleaning up {count} audit logs older than {days} days")
            old_logs.unlink()
        
        return count
    
    # ========================================================================
    # ANALYTICS METHODS
    # ========================================================================
    
    @api.model
    def get_api_usage_stats(self, date_from=None, date_to=None):
        """
        Get API usage statistics for a date range
        
        Args:
            date_from (date): Start date
            date_to (date): End date
            
        Returns:
            dict: Usage statistics
        """
        domain = []
        
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        
        logs = self.search(domain)
        
        if not logs:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0.0,
                'unique_api_keys': 0,
                'by_endpoint': {},
                'by_status_code': {}
            }
        
        # Calculate statistics
        total = len(logs)
        successful = len(logs.filtered(lambda l: l.success))
        failed = total - successful
        
        # Average response time
        response_times = logs.filtered(lambda l: l.response_time).mapped('response_time')
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Unique API keys
        unique_keys = len(logs.mapped('api_key_id'))
        
        # Group by endpoint
        by_endpoint = {}
        for log in logs:
            endpoint = log.endpoint or 'Unknown'
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = 0
            by_endpoint[endpoint] += 1
        
        # Group by status code
        by_status_code = {}
        for log in logs:
            status = log.status_code or 0
            if status not in by_status_code:
                by_status_code[status] = 0
            by_status_code[status] += 1
        
        return {
            'total_requests': total,
            'successful_requests': successful,
            'failed_requests': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'avg_response_time': round(avg_response_time, 4),
            'unique_api_keys': unique_keys,
            'by_endpoint': by_endpoint,
            'by_status_code': by_status_code
        }
    
    def action_view_api_key(self):
        """
        Navigate to the API key record
        """
        self.ensure_one()
        
        if not self.api_key_id:
            raise UserError(_('No API key associated with this log entry.'))
        
        return {
            'name': _('API Key'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.api.key',
            'res_id': self.api_key_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    @api.model
    def cron_cleanup_old_logs(self, days=90):
        """Alias for cleanup_old_logs for compatibility."""
        return self.cleanup_old_logs(days=days)
