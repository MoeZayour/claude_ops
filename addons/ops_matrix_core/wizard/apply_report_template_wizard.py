from odoo import models, fields, api, _

class ApplyReportTemplateWizard(models.TransientModel):
    _name = 'apply.report.template.wizard'
    _description = 'Apply Report Template Wizard'

    template_id = fields.Many2one('ops.report.template', string='Template', required=True)
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    branch_id = fields.Many2one('ops.branch', string='Branch')
    business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')

    def action_apply_template(self):
        self.ensure_one()
        report_id = self.env.context.get('active_id')
        return self.template_id.action_apply_to_report(
            report_id,
            self.date_from,
            self.date_to,
            branch_id=self.branch_id,
            bu_id=self.business_unit_id
        )
