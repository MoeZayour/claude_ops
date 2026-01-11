# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import AccessError

class IrExports(models.Model):
    _inherit = 'ir.exports'
    
    @api.model
    def create(self, vals):
        """Override export creation to enforce security"""
        # Check if user is IT Admin or System Admin
        # In Odoo 19, check for appropriate groups.
        if not self.env.user.has_group('ops_matrix_core.group_ops_it_admin') and \
           not self.env.user.has_group('base.group_system'):
            raise AccessError(_(
                'Direct export is disabled for security reasons. '
                'Please use the Secure Excel Export Wizard from the Reporting menu.'
            ))
        return super(IrExports, self).create(vals)


class BaseModel(models.AbstractModel):
    _inherit = 'base'
    
    def export_data(self, fields_to_export):
        """Override export_data to restrict native export"""
        # Allow IT Admin and System Admin
        if self.env.user.has_group('ops_matrix_core.group_ops_it_admin') or \
           self.env.user.has_group('base.group_system'):
            return super(BaseModel, self).export_data(fields_to_export)
        
        # Block for all other users
        raise AccessError(_(
            'Direct data export is disabled for security reasons.\n\n'
            'Please use the Secure Excel Export Wizard:\n'
            'Reporting → Export Tools → Secure Excel Export\n\n'
            'This ensures:\n'
            '• Field-level security is enforced\n'
            '• Branch filtering is applied\n'
            '• Export activity is logged\n'
            '• Data is properly formatted'
        ))
