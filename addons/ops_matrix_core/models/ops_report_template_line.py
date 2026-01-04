from odoo import models, fields, api, _

class OpsReportTemplateLine(models.Model):
    _name = 'ops.report.template.line'
    _description = 'Report Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one('ops.report.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    section_name = fields.Char(string='Section Name', required=True)
    is_section_header = fields.Boolean(string='Is Section Header')
    show_subtotal = fields.Boolean(string='Show Subtotal')
    account_type = fields.Selection([
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense')
    ], string='Account Type')
    account_code_pattern = fields.Char(string='Account Code Pattern (LIKE)')
    account_ids = fields.Many2many('account.account', string='Specific Accounts')
    sort_by = fields.Selection([
        ('code', 'Account Code'),
        ('name', 'Account Name')
    ], string='Sort By', default='code')

    def _get_accounts(self, date_from, date_to, branch_id=False, bu_id=False):
        self.ensure_one()
        domain = [('company_id', '=', self.template_id.company_id.id)]

        if self.account_ids:
            domain.append(('id', 'in', self.account_ids.ids))
        else:
            if self.account_type:
                domain.append(('account_type', '=', self.account_type))
            if self.account_code_pattern:
                domain.append(('code', 'ilike', self.account_code_pattern))
        
        # The branch and BU filtering will be implemented later

        accounts = self.env['account.account'].search(domain, order=self.sort_by)
        return accounts
