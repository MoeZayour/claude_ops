from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class OpsSecurityRules(models.AbstractModel):
    """Additional security logic for complex matrix rules."""
    _name = 'ops.security.rules'
    _description = 'OPS Security Rule Engine'
    
    @api.model
    def _check_record_access(self, model_name, record_id, operation='read'):
        """
        Check if current user can access a specific record.
        Used for custom security checks beyond standard rules.
        
        Args:
            model_name: Name of the model
            record_id: ID of the record
            operation: Operation type ('read', 'write', 'create', 'unlink')
            
        Returns:
            bool: True if access allowed
        """
        user = self.env.user
        
        # System administrators bypass all checks
        if user.has_group('base.group_system'):
            return True
        
        # Get the record
        record = self.env[model_name].browse(record_id)
        if not record.exists():
            return False
        
        # Model-specific checks
        if model_name == 'sale.order':
            # Check branch and BU access
            if record.ops_branch_id and record.ops_business_unit_id:
                branch_access = user.can_access_branch(record.ops_branch_id.id)
                bu_access = user.can_access_business_unit(record.ops_business_unit_id.id)
                return branch_access and bu_access
            return True  # Legacy records
        
        elif model_name == 'account.move':
            # Similar check for invoices
            if record.move_type in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
                if record.ops_branch_id and record.ops_business_unit_id:
                    branch_access = user.can_access_branch(record.ops_branch_id.id)
                    bu_access = user.can_access_business_unit(record.ops_business_unit_id.id)
                    return branch_access and bu_access
            return True
        
        elif model_name == 'stock.picking':
            # Check branch access
            if record.ops_branch_id:
                return user.can_access_branch(record.ops_branch_id.id)
            return True
        
        elif model_name == 'purchase.order':
            # Check branch and BU access
            if record.ops_branch_id and record.ops_business_unit_id:
                branch_access = user.can_access_branch(record.ops_branch_id.id)
                bu_access = user.can_access_business_unit(record.ops_business_unit_id.id)
                return branch_access and bu_access
            return True
        
        # Default: use standard rules
        return True
    
    @api.model
    def _get_accessible_records(self, model_name, domain=None):
        """
        Get records accessible to current user.
        Used for reports and dashboards.
        
        Args:
            model_name: Name of the model
            domain: Optional additional domain filter
            
        Returns:
            RecordSet: Accessible records
        """
        user = self.env.user
        
        # System administrators see everything
        if user.has_group('base.group_system'):
            return self.env[model_name].search(domain or [])
        
        # Apply matrix filters
        accessible_domain = self._get_matrix_domain(model_name)
        if domain:
            accessible_domain = ['&'] + accessible_domain + domain
        
        return self.env[model_name].search(accessible_domain)
    
    @api.model
    def _get_matrix_domain(self, model_name):
        """
        Generate domain for matrix access based on model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            list: Domain filter for matrix access
        """
        user = self.env.user
        
        if model_name == 'sale.order':
            return ['|', '|',
                ('ops_branch_id', '=', False),
                ('company_id', 'in', user.company_ids.ids),
                '&',
                    ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids),
                    ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)
            ]
        
        elif model_name == 'account.move':
            return ['|', '|', '|',
                ('ops_branch_id', '=', False),
                ('company_id', 'in', user.company_ids.ids),
                ('move_type', 'not in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']),
                '&',
                    ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids),
                    ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)
            ]
        
        elif model_name == 'stock.picking':
            return ['|', '|',
                ('ops_branch_id', '=', False),
                ('company_id', 'in', user.company_ids.ids),
                ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)
            ]
        
        elif model_name == 'purchase.order':
            return ['|', '|',
                ('ops_branch_id', '=', False),
                ('company_id', 'in', user.company_ids.ids),
                '&',
                    ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids),
                    ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)
            ]
        
        elif model_name == 'ops.business.unit':
            return [('id', 'in', user.ops_allowed_business_unit_ids.ids)]
        
        # Default: company restriction only
        return [('company_id', 'in', user.company_ids.ids)]
    
    @api.model
    def check_matrix_access_raise(self, model_name, record_id, operation='read'):
        """
        Check access and raise AccessError if denied.
        
        Args:
            model_name: Name of the model
            record_id: ID of the record
            operation: Operation type
            
        Raises:
            AccessError: If access is denied
        """
        if not self._check_record_access(model_name, record_id, operation):
            # Log the denial
            audit_model = self.env['ops.security.audit'].sudo()
            record = self.env[model_name].sudo().browse(record_id)
            
            audit_model.log_access_denied(
                model_name,
                record_id,
                f"User {self.env.user.name} denied {operation} access to {record.display_name}"
            )
            
            raise AccessError(_(
                "You do not have permission to %(operation)s this %(model)s record. "
                "Contact your administrator for matrix access rights."
            ) % {
                'operation': operation,
                'model': model_name
            })
    
    @api.model
    def get_user_accessible_branches(self):
        """Get branches accessible to current user."""
        user = self.env.user
        
        if user.has_group('base.group_system'):
            return self.env['res.company'].search([])
        
        return user.ops_allowed_branch_ids
    
    @api.model
    def get_user_accessible_business_units(self):
        """Get business units accessible to current user."""
        user = self.env.user
        
        if user.has_group('base.group_system'):
            return self.env['ops.business.unit'].search([])
        
        return user.ops_allowed_business_unit_ids
    
    @api.model
    def get_matrix_access_summary(self):
        """
        Get a summary of current user's matrix access.
        
        Returns:
            dict: Summary of access rights
        """
        user = self.env.user
        
        return {
            'user_id': user.id,
            'user_name': user.name,
            'is_system_admin': user.has_group('base.group_system'),
            'is_matrix_admin': user.is_matrix_administrator,
            'is_cross_branch_leader': user.is_cross_branch_bu_leader,
            'allowed_branches': user.ops_allowed_branch_ids.ids,
            'allowed_business_units': user.ops_allowed_business_unit_ids.ids,
            'branch_count': len(user.ops_allowed_branch_ids),
            'bu_count': len(user.ops_allowed_business_unit_ids),
            'companies': user.company_ids.ids,
        }
