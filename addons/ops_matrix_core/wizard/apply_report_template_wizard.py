# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ApplyReportTemplateWizard(models.TransientModel):
    _name = 'apply.report.template.wizard'
    _description = 'Apply Report Template Wizard'
    
    template_id = fields.Many2one('ops.report.template', 'Template', required=True)
    date_from = fields.Date('From Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date('To Date', required=True, default=fields.Date.context_today)
    branch_id = fields.Many2one('ops.branch', 'Branch')
    business_unit_id = fields.Many2one('ops.business.unit', 'Business Unit')
    
    def action_apply_template(self):
        """Apply selected template to current report."""
        self.ensure_one()
        report_id = self.env.context.get('active_id')
        
        return self.template_id.action_apply_to_report(
            report_id=report_id,
            date_from=self.date_from,
            date_to=self.date_to,
            branch_id=self.branch_id.id if self.branch_id else False,
            bu_id=self.business_unit_id.id if self.business_unit_id else False
        )
