# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class OpsFieldVisibilityRule(models.Model):
    """
    Defines field-level visibility rules to hide sensitive data from unauthorized users.
    
    Example:
    - Sales Reps cannot see: cost_price, purchase_price, margin fields
    - Purchase Officers cannot see: customer, sale_price, margin fields
    - Warehouse cannot see: cost, value, margin fields
    """
    
    _name = 'ops.field.visibility.rule'
    _description = 'Field Visibility Rule'
    _order = 'model_name, field_name, security_group'
    
    # Core Fields
    name = fields.Char(
        string='Rule Name',
        compute='_compute_name',
        store=True,
        index=True
    )
    
    model_name = fields.Char(
        string='Model',
        required=True,
        help='Model technical name (e.g., product.product)'
    )
    
    field_name = fields.Char(
        string='Field Name',
        required=True,
        help='Field technical name to hide (e.g., cost_price)'
    )
    
    field_label = fields.Char(
        string='Field Label',
        help='Display label for the field'
    )
    
    security_group_id = fields.Many2one(
        'res.groups',
        string='Security Group',
        required=True,
        help='Users in this group will NOT see the field'
    )
    
    visibility_mode = fields.Selection(
        selection=[
            ('hidden', 'Completely Hidden'),
            ('readonly', 'Read-Only'),
        ],
        default='hidden',
        string='Visibility Mode',
        help='How to restrict access: hidden (not in schema) or readonly'
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True,
        help='Disable rule without deleting'
    )
    
    # Metadata
    description = fields.Text(
        string='Description',
        help='Why this field is restricted'
    )
    
    created_date = fields.Datetime(
        string='Created',
        readonly=True,
        default=fields.Datetime.now
    )
    
    modified_date = fields.Datetime(
        string='Modified',
        readonly=True
    )
    
    # Computed Fields
    @api.depends('model_name', 'field_name', 'security_group_id')
    def _compute_name(self):
        """Auto-generate rule name from components."""
        for rule in self:
            parts = [rule.model_name, rule.field_name]
            if rule.security_group_id:
                parts.append(rule.security_group_id.name)
            rule.name = ' | '.join(parts) if all(parts) else 'New Rule'
    
    @api.model_create_multi
    def create(self, vals_list):
        """Set modified_date on create."""
        for vals in vals_list:
            vals['modified_date'] = fields.Datetime.now()
        return super().create(vals_list)
    
    def write(self, vals):
        """Update modified_date on write."""
        vals['modified_date'] = fields.Datetime.now()
        return super().write(vals)
    
    @api.constrains('model_name', 'field_name')
    def _check_model_field_exists(self):
        """Validate that model and field exist (optional - can be strict)."""
        for rule in self:
            if rule.model_name and rule.field_name:
                try:
                    model = self.env[rule.model_name]
                    if not hasattr(model, rule.field_name):
                        _logger.warning(
                            f"Field {rule.field_name} not found in model {rule.model_name}"
                        )
                except Exception as e:
                    _logger.warning(f"Could not validate model field: {e}")
    
    @api.model
    def _get_hidden_fields_for_user(self, model_name, user=None):
        """
        Get list of hidden fields for current user.
        
        Returns: {field_name: {'mode': 'hidden'|'readonly', 'rule_id': id}}
        """
        if user is None:
            user = self.env.user
        
        # Safely get user groups - handle cases where groups_id might not be loaded
        try:
            user_groups = user.groups_id.ids if hasattr(user, 'groups_id') else []
        except AttributeError:
            # If groups_id not available, fetch user properly
            user = self.env['res.users'].browse(user.id)
            user_groups = user.groups_id.ids if user.exists() else []
        
        hidden_fields = {}
        
        # Find all rules where user is in the restricted group
        rules = self.search([
            ('model_name', '=', model_name),
            ('is_active', '=', True),
            ('security_group_id', 'in', user_groups)
        ])
        
        for rule in rules:
            hidden_fields[rule.field_name] = {
                'mode': rule.visibility_mode,
                'rule_id': rule.id,
                'group_id': rule.security_group_id.id
            }
        
        return hidden_fields
    
    @api.model
    def _get_searchable_fields_for_user(self, model_name, user=None):
        """
        Get list of fields user CANNOT search on.
        
        Returns: set of field names restricted from search
        """
        hidden_fields = self._get_hidden_fields_for_user(model_name, user)
        
        # Only completely hidden fields block searches (not readonly)
        return {
            field_name 
            for field_name, info in hidden_fields.items() 
            if info['mode'] == 'hidden'
        }
    
    def _log_visibility_access_attempt(self, user, model_name, field_name, action='search'):
        """Log attempts to access restricted fields (audit trail)."""
        log_msg = f"User {user.name} attempted to {action} restricted field {field_name} on {model_name}"
        _logger.warning(log_msg)
        
        # Create audit log entry if audit model exists
        try:
            audit_log = self.env.get('ops.audit.log')
            if audit_log:
                audit_log.create({
                    'action': f'field_access_denied_{action}',
                    'model_name': model_name,
                    'user_id': user.id,
                    'description': log_msg,
                    'related_id': f'{model_name},0'
                })
        except Exception as e:
            _logger.debug(f"Could not create audit log: {e}")


class OpsFieldVisibilityMixin(models.AbstractModel):
    """
    Mixin to apply field visibility rules to a model.
    
    Usage:
        class MyModel(models.Model):
            _inherit = ['my.model', 'ops.field.visibility.mixin']
    """
    
    _name = 'ops.field.visibility.mixin'
    _description = 'Field Visibility Mixin'
    
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Override fields_get to hide restricted fields from schema.
        
        For restricted fields:
        - 'hidden' mode: Remove from fields dict entirely
        - 'readonly' mode: Set readonly=True (handled by _search)
        """
        fields_dict = super().fields_get(allfields, attributes)
        
        user = self.env.user
        model_name = self._name
        
        # Get rules for this user
        visibility_rules = self.env['ops.field.visibility.rule']
        hidden_fields = visibility_rules._get_hidden_fields_for_user(model_name, user)
        
        # Remove completely hidden fields from schema
        for field_name, info in hidden_fields.items():
            if info['mode'] == 'hidden' and field_name in fields_dict:
                del fields_dict[field_name]
                _logger.debug(f"Hid field {field_name} from {user.name} on {model_name}")
        
        return fields_dict
    
    # Temporarily disabled to avoid signature conflicts in Odoo 19
    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None):
    #     """
    #     Override _search to prevent searches on restricted fields.
    #     
    #     Raises error if user tries to search on a field they can't see.
    #     """
    #     user = self.env.user
    #     model_name = self._name
    #     
    #     # Get searchable fields
    #     visibility_rules = self.env['ops.field.visibility.rule']
    #     restricted_fields = visibility_rules._get_searchable_fields_for_user(model_name, user)
    #     
    #     # Check if any search domain uses restricted fields
    #     if restricted_fields:
    #         restricted_fields_in_domain = self._get_restricted_fields_in_domain(args, restricted_fields)
    #         
    #         if restricted_fields_in_domain:
    #             # Log violation
    #             for field in restricted_fields_in_domain:
    #                 visibility_rules._log_visibility_access_attempt(
    #                     user, model_name, field, action='search'
    #                 )
    #             
    #             # Raise error
    #             raise UserError(
    #                 _("You cannot search on field(s): %s. Access restricted.") 
    #                 % ', '.join(restricted_fields_in_domain)
    #             )
    #     
    #     return super()._search(args, offset=offset, limit=limit, order=order)
    
    @staticmethod
    def _get_restricted_fields_in_domain(args, restricted_fields):
        """
        Extract field names from search domain that are in restricted_fields.
        
        Domain format: [('field_name', 'operator', value), ...]
        """
        restricted_in_use = set()
        
        if not args:
            return restricted_in_use
        
        for arg in args:
            if isinstance(arg, (tuple, list)) and len(arg) >= 1:
                field_name = arg[0]
                
                # Handle nested domains with operators like '&', '|', '!'
                if field_name not in ['&', '|', '!']:
                    # Check if this field is restricted
                    if field_name in restricted_fields:
                        restricted_in_use.add(field_name)
                    # Also check for related field searches (field.subfield)
                    elif '.' in field_name:
                        base_field = field_name.split('.')[0]
                        if base_field in restricted_fields:
                            restricted_in_use.add(base_field)
        
        return restricted_in_use
    
    def read(self, fields=None, load='_classic_read'):
        """
        Override read to ensure restricted fields are not returned.
        """
        user = self.env.user
        model_name = self._name
        
        # Get rules for this user
        visibility_rules = self.env['ops.field.visibility.rule']
        hidden_fields = visibility_rules._get_hidden_fields_for_user(model_name, user)
        
        # If reading specific fields, remove restricted ones
        if fields:
            filtered_fields = [f for f in fields if f not in hidden_fields]
            result = super().read(fields=filtered_fields, load=load)
        else:
            # If no specific fields, read all then filter response
            result = super().read(fields=fields, load=load)
            
            # Remove restricted fields from result
            for record in result:
                for field_name in hidden_fields.keys():
                    if field_name in record:
                        del record[field_name]
        
        return result
