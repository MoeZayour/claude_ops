# -*- coding: utf-8 -*-

"""
OPS Matrix API Key Management
Provides secure API key generation and management for external integrations
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import secrets
import logging

_logger = logging.getLogger(__name__)


class OpsApiKey(models.Model):
    """
    API Key Model for OPS Matrix Framework
    
    Manages API keys for external system integrations with persona-based access control.
    Keys are automatically generated using cryptographically secure tokens.
    """
    _name = 'ops.api.key'
    _description = 'OPS Matrix API Key'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    # ========================================================================
    # FIELDS
    # ========================================================================
    
    name = fields.Char(
        string='API Key Name',
        required=True,
        help='Descriptive name for this API key (e.g., "Production Integration", "Mobile App")'
    )
    
    key = fields.Char(
        string='API Key Token',
        required=True,
        readonly=True,
        copy=False,
        index=True,
        help='The actual API key token - auto-generated and readonly for security'
    )
    
    persona_id = fields.Many2one(
        'ops.persona',
        string='Persona',
        required=True,
        ondelete='cascade',
        help='The persona this API key is linked to - determines access rights and data visibility'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Inactive keys cannot be used for authentication'
    )
    
    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True,
        help='When this API key was created'
    )
    
    last_used = fields.Datetime(
        string='Last Used',
        readonly=True,
        help='Last time this API key was used for authentication'
    )
    
    usage_count = fields.Integer(
        string='Usage Count',
        default=0,
        readonly=True,
        help='Total number of times this API key has been used'
    )
    
    # Additional metadata
    description = fields.Text(
        string='Description',
        help='Additional notes about this API key and its purpose'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
        help='User who created this API key'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # ========================================================================
    # CONSTRAINTS
    # ========================================================================
    
    _sql_constraints = [
        ('unique_key', 'UNIQUE(key)', 'API Key must be unique!'),
        ('check_usage_count', 'CHECK(usage_count >= 0)', 'Usage count cannot be negative!')
    ]
    
    # ========================================================================
    # ORM METHODS
    # ========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to auto-generate secure API key token
        """
        for vals in vals_list:
            if 'key' not in vals or not vals.get('key'):
                # Generate cryptographically secure API key
                vals['key'] = self._generate_api_key()
        
        records = super(OpsApiKey, self).create(vals_list)
        
        for record in records:
            _logger.info(f"API Key created: {record.name} (ID: {record.id}) for persona {record.persona_id.name}")
        
        return records
    
    def write(self, vals):
        """
        Override write to prevent modification of key field
        """
        if 'key' in vals and any(rec.id for rec in self):
            raise ValidationError(_('API Key token cannot be modified after creation for security reasons.'))
        
        return super(OpsApiKey, self).write(vals)
    
    def unlink(self):
        """
        Override unlink to log deletion
        """
        for record in self:
            _logger.warning(f"API Key deleted: {record.name} (ID: {record.id})")
        
        return super(OpsApiKey, self).unlink()
    
    # ========================================================================
    # BUSINESS METHODS
    # ========================================================================
    
    def _generate_api_key(self):
        """
        Generate a cryptographically secure API key token
        
        Uses secrets.token_urlsafe(32) which generates a URL-safe text string
        containing 32 random bytes in Base64 encoding (approximately 43 characters)
        
        Returns:
            str: Secure API key token
        """
        return secrets.token_urlsafe(32)
    
    def regenerate_key(self):
        """
        Regenerate the API key token (useful if compromised)
        
        This is the only way to change the key after creation.
        """
        self.ensure_one()
        
        if not self.env.user.has_group('base.group_system'):
            raise ValidationError(_('Only system administrators can regenerate API keys.'))
        
        old_key_preview = self.key[:8] + '...' if self.key else 'N/A'
        new_key = self._generate_api_key()
        
        # Use SQL to bypass write() restriction
        self.env.cr.execute(
            "UPDATE ops_api_key SET key = %s WHERE id = %s",
            (new_key, self.id)
        )
        
        # Invalidate cache
        self.invalidate_recordset(['key'])
        
        _logger.warning(
            f"API Key regenerated: {self.name} (ID: {self.id}) "
            f"Old: {old_key_preview}, New: {new_key[:8]}... "
            f"By: {self.env.user.name}"
        )
        
        # Post message to chatter
        self.message_post(
            body=_('API Key regenerated by %s') % self.env.user.name,
            subject=_('API Key Regenerated')
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Regenerated'),
                'message': _('The API key has been regenerated. Please update your integration with the new key.'),
                'type': 'warning',
                'sticky': True
            }
        }
    
    def increment_usage(self):
        """
        Increment usage counter and update last used timestamp
        
        Called by API authentication decorator on each successful request
        """
        self.ensure_one()
        
        # Use SQL for performance (avoid ORM overhead on each API call)
        self.env.cr.execute("""
            UPDATE ops_api_key 
            SET usage_count = usage_count + 1, 
                last_used = NOW() AT TIME ZONE 'UTC'
            WHERE id = %s
        """, (self.id,))
        
        # No need to invalidate cache for readonly fields
    
    @api.model
    def validate_key(self, api_key_token):
        """
        Validate an API key token and return the associated key record
        
        Args:
            api_key_token (str): The API key token to validate
            
        Returns:
            ops.api.key: The API key record if valid and active, False otherwise
        """
        if not api_key_token:
            return False
        
        key_record = self.sudo().search([
            ('key', '=', api_key_token),
            ('active', '=', True)
        ], limit=1)
        
        return key_record if key_record else False
    
    def action_deactivate(self):
        """
        Deactivate API key (from UI button)
        """
        self.ensure_one()
        self.active = False
        
        _logger.info(f"API Key deactivated: {self.name} (ID: {self.id}) by {self.env.user.name}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Deactivated'),
                'message': _('This API key is now inactive and cannot be used for authentication.'),
                'type': 'success'
            }
        }
    
    def action_activate(self):
        """
        Activate API key (from UI button)
        """
        self.ensure_one()
        self.active = True
        
        _logger.info(f"API Key activated: {self.name} (ID: {self.id}) by {self.env.user.name}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Activated'),
                'message': _('This API key is now active and can be used for authentication.'),
                'type': 'success'
            }
        }
    
    # ========================================================================
    # VIEWS
    # ========================================================================
    
    def action_view_audit_logs(self):
        """
        Open audit logs for this API key
        """
        self.ensure_one()
        
        return {
            'name': _('Audit Logs - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'ops.audit.log',
            'view_mode': 'tree,form',
            'domain': [('api_key_id', '=', self.id)],
            'context': {'default_api_key_id': self.id}
        }
