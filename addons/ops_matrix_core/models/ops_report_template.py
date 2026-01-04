from odoo import models, fields, api, _

class OpsReportTemplate(models.Model):
    _name = 'ops.report.template'
    _description = 'Report Template'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    report_type = fields.Selection([
        ('profit_loss', 'Profit & Loss'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow'),
        ('trial_balance', 'Trial Balance'),
        ('custom', 'Custom')
    ], string='Report Type', required=True)
    template_line_ids = fields.One2many('ops.report.template.line', 'template_id', string='Template Lines')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    is_system_template = fields.Boolean(string='System Template', help="System templates cannot be deleted.")

    def action_apply_to_report(self, report_id, date_from, date_to, branch_id=False, bu_id=False):
        self.ensure_one()
        report = self.env['account.report'].browse(report_id)

        # Clear existing lines
        report.line_ids.unlink()

        for line in self.template_line_ids:
            accounts = line._get_accounts(date_from, date_to, branch_id, bu_id)
            if accounts:
                if line.is_section_header:
                    self.env['account.report.line'].create({
                        'report_id': report.id,
                        'name': line.section_name,
                        'level': 1, # Adjust level as needed
                        'code': line.section_name.replace(' ', '').upper(),
                    })

                for account in accounts:
                    self.env['account.report.line'].create({
                        'report_id': report.id,
                        'account_id': account.id,
                        'name': account.name,
                        'level': 2, # Adjust level as needed
                    })

                if line.show_subtotal:
                    self.env['account.report.line'].create({
                        'report_id': report.id,
                        'name': _('Subtotal %s') % line.section_name,
                        'level': 1, # Adjust level as needed
                        'code': 'SUBTOTAL_' + line.section_name.replace(' ', '').upper(),
                    })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Applied'),
                'message': _('The report has been updated with the selected template.'),
                'sticky': False,
            }
        }
