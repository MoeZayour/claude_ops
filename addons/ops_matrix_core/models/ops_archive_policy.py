from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from dateutil.relativedelta import relativedelta

class OpsArchivePolicy(models.Model):
    _name = 'ops.archive.policy'
    _description = 'Data Archiving Policy'

    name = fields.Char(string='Policy Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    domain_code = fields.Text(string='Domain Filter', default='[]', help="Python domain to filter records for archiving.")
    retention_months = fields.Integer(string='Retention (Months)', default=12, required=True)
    active = fields.Boolean(default=True)

    @api.constrains('model_id')
    def _check_financial_safety(self):
        forbidden_models = [
            'account.move',
            'account.move.line',
            'stock.move',
            'stock.valuation.layer'
        ]
        for record in self:
            if record.model_id.model in forbidden_models:
                raise UserError(_("Safety Violation: Archiving financial or stock valuation data (%s) is strictly prohibited.") % record.model_id.model)

    def _cron_archive_records(self):
        policies = self.search([('active', '=', True)])
        for policy in policies:
            model = self.env[policy.model_id.model]
            cutoff_date = fields.Datetime.now() - relativedelta(months=policy.retention_months)
            
            # Construct domain - use safe_eval to prevent code injection
            try:
                domain = safe_eval(policy.domain_code or '[]')
                if not isinstance(domain, list):
                    domain = []
            except Exception:
                domain = []
            
            domain += [('create_date', '<', cutoff_date)]
            
            # Search and unlink in batches
            records = model.search(domain, limit=1000)
            if records:
                records.unlink()

    def cron_execute_archive_policies(self):
        """Alias for _cron_archive_records for compatibility."""
        return self._cron_archive_records()
