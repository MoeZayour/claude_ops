# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .ops_corporate_report_parsers import get_report_colors

class OpsAssetRegisterReport(models.AbstractModel):
    _name = 'report.ops_matrix_accounting.report_asset_register'
    _description = 'Asset Register Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Main method to prepare the data for the Asset Register report.
        """
        # If the report is triggered from a wizard, 'data' will contain its values
        # Otherwise, we search for all 'in_use' or 'disposed' assets.
        domain = [('state', 'in', ['in_use', 'disposed'])]
        if data and data.get('form'):
            form_data = data.get('form')
            if form_data.get('asset_category_id'):
                domain.append(('category_id', '=', form_data['asset_category_id'][0]))
            if form_data.get('branch_id'):
                domain.append(('branch_id', '=', form_data['branch_id'][0]))

        assets = self.env['ops.asset'].search(domain, order='purchase_date asc')

        company = self.env.company
        colors = get_report_colors(company)

        result = {
            'doc_ids': assets.ids,
            'doc_model': 'ops.asset',
            'docs': assets,
            'data': data,
            'company': company,
        }
        result.update(colors)
        return result

# Wizard to launch the report with filters
class AssetRegisterWizard(models.TransientModel):
    _name = 'ops.asset.register.wizard'
    _description = 'Asset Register Report Wizard'

    asset_category_id = fields.Many2one(
        'ops.asset.category',
        string='Asset Category'
    )
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch'
    )

    def _prepare_report_data(self):
        self.ensure_one()
        return {
            'form': {
                'asset_category_id': self.asset_category_id.id if self.asset_category_id else False,
                'branch_id': self.branch_id.id if self.branch_id else False,
            }
        }

    def action_print_report(self):
        """
        Called by the 'Print' button, this method prepares the data
        and returns the action to render the QWeb report.
        """
        data = self._prepare_report_data()
        return self.env.ref('ops_matrix_accounting.action_report_asset_register').report_action(None, data=data)
