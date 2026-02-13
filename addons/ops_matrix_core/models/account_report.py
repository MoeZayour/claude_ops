from odoo import models, fields, api, _

class AccountReport(models.Model):
    _inherit = 'account.report'

    def action_open_apply_template_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Apply Report Template'),
            'res_model': 'apply.report.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_report_id': self.id,
            }
        }
