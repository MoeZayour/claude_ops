# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import AccessError

class IrExports(models.Model):
    _inherit = 'ir.exports'
    
    @api.model
    def create(self, vals):
        """Override export template creation to enforce security"""
        # Allow IT Admin and System Admin to create export templates
        if not self.env.user.has_group('ops_matrix_core.group_ops_it_admin') and \
           not self.env.user.has_group('base.group_system'):
            raise AccessError(_(
                'Saving export templates is disabled for security reasons.\n'
                'You can still export data using the export button.'
            ))
        return super(IrExports, self).create(vals)


# Note: We do NOT override export_data() here.
# The JS export_interceptor.js handles redirection to secure wizard.
# This allows the export button to remain active while JS intercepts the click.
