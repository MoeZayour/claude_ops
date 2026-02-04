from odoo import models, fields, api

class OpsGeneralLedgerWizard(models.TransientModel):
    _name = 'ops.general.ledger.wizard'
    _inherit = 'ops.financial.report.wizard'
    _description = 'General Ledger Report Wizard'

    account_ids = fields.Many2many('account.account', string='Accounts', 
                                     help='Leave empty to include all accounts')

    def action_print_pdf(self):
        self.ensure_one()
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_move': self.target_move,
            'journal_ids': self.journal_ids.ids,
            'account_ids': self.account_ids.ids if self.account_ids else [],
            'company_id': self.company_id.id,
        }
        return self.env.ref('ops_matrix_accounting.action_report_general_ledger').report_action(self, data=data)
