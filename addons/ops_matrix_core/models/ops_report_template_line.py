# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class OpsReportTemplateLine(models.Model):
    _name = 'ops.report.template.line'
    _description = 'Report Template Line'
    _order = 'sequence, id'
    
    template_id = fields.Many2one('ops.report.template', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    
    section_name = fields.Char('Section Name', required=True)
    is_section_header = fields.Boolean('Show Section Header', default=True)
    show_subtotal = fields.Boolean('Show Subtotal', default=True)
    
    # Account Selection Criteria
    account_type = fields.Selection([
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ], 'Account Type')
    
    account_code_pattern = fields.Char(
        'Account Code Pattern',
        help='SQL LIKE pattern (e.g., "5%" for codes starting with 5)'
    )
    
    account_ids = fields.Many2many(
        'account.account',
        'report_template_line_account_rel',
        'line_id',
        'account_id',
        'Specific Accounts',
        help='If specified, use these accounts instead of filters'
    )
    
    sort_by = fields.Selection([
        ('code', 'Account Code'),
        ('name', 'Account Name'),
    ], default='code')
    
    def _get_accounts(self, date_from, date_to, branch_id=False, bu_id=False):
        """Get accounts matching this template line criteria."""
        self.ensure_one()
        
        if self.account_ids:
            return self.account_ids
        
        domain = [('company_id', '=', self.template_id.company_id.id)]
        
        if self.account_type:
            domain.append(('account_type', '=', self.account_type))
        
        if self.account_code_pattern:
            domain.append(('code', 'like', self.account_code_pattern))
        
        # Branch filter (if accounts have branch field)
        if branch_id and hasattr(self.env['account.account'], 'ops_branch_id'):
            domain.append(('ops_branch_id', '=', branch_id))
        
        accounts = self.env['account.account'].search(domain)
        
        if self.sort_by == 'code':
            accounts = accounts.sorted(lambda a: a.code)
        else:
            accounts = accounts.sorted(lambda a: a.name)
        
        return accounts
