# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OpsAssetDepreciationWizard(models.TransientModel):
    _name = 'ops.asset.depreciation.wizard'
    _description = 'Asset Depreciation Batch Wizard'

    date = fields.Date(
        string='Depreciation Date',
        required=True,
        default=fields.Date.context_today,
        help="Depreciate assets up to this date."
    )
    asset_category_id = fields.Many2one(
        'ops.asset.category',
        string='Asset Category',
        help="Limit the depreciation to a specific asset category. Leave empty for all."
    )
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        help="Limit to a specific branch. Leave empty for all."
    )

    def _get_domain(self):
        """Constructs the domain to find assets needing depreciation."""
        domain = [
            ('state', '=', 'in_use'),
            ('depreciation_start_date', '<=', self.date),
        ]
        if self.asset_category_id:
            domain.append(('category_id', '=', self.asset_category_id.id))
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        return domain

    def _create_depreciation_entry(self, asset):
        """Creates a depreciation line for a given asset."""
        
        # This will be replaced by a more robust calculation based on the last depreciation date
        # For now, we calculate a simple monthly amount
        # Ensure we don't depreciate past the salvage value
        
        # Dummy logic - to be replaced with actual depreciation calculation
        # This logic should find the last depreciation date and calculate the periods since.
        # For this phase, we just create a placeholder entry.
        
        amount_to_depreciate = (asset.purchase_value - asset.salvage_value) / asset.depreciation_months
        
        # Check if already fully depreciated
        if asset.accumulated_depreciation >= (asset.purchase_value - asset.salvage_value):
            return None # Skip creating a line
            
        return self.env['ops.asset.depreciation'].create({
            'asset_id': asset.id,
            'date': self.date,
            'amount': amount_to_depreciate, # Placeholder
            'state': 'draft',
        })

    def action_run_depreciation(self):
        """Main action to generate depreciation entries."""
        self.ensure_one()
        
        domain = self._get_domain()
        assets = self.env['ops.asset'].search(domain)
        
        if not assets:
            raise UserError(_("No assets found for the selected criteria that require depreciation."))
            
        created_depreciations = self.env['ops.asset.depreciation']
        for asset in assets:
            dep_line = self._create_depreciation_entry(asset)
            if dep_line:
                created_depreciations |= dep_line
                
        if not created_depreciations:
            raise UserError(_("All selected assets are already fully depreciated."))

        # Return an action to show the created depreciation entries
        return {
            'name': _('Generated Depreciation Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.asset.depreciation',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_depreciations.ids)],
            'context': {'default_state': 'draft'},
        }

    def action_confirm_and_post(self):
        """Generate, confirm, and post the journal entries in one go."""
        self.ensure_one()
        
        # This is an enhanced action that will not only create but also post
        # For now, it calls the creation and then we would loop to post
        
        response = self.action_run_depreciation()
        if response and response.get('domain'):
            depreciation_lines = self.env['ops.asset.depreciation'].search(response['domain'])
            depreciation_lines.action_confirm()
            depreciation_lines.action_post()
            
            # Re-query to get the posted state for the final view
            posted_lines = self.env['ops.asset.depreciation'].search(response['domain'])
            
            return {
                'name': _('Posted Depreciation Entries'),
                'type': 'ir.actions.act_window',
                'res_model': 'ops.asset.depreciation',
                'view_mode': 'list,form',
                'domain': [('id', 'in', posted_lines.ids)],
            }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Depreciation'),
                'message': _('No depreciation entries were generated or posted.'),
                'sticky': False,
            }
        }
