# -*- coding: utf-8 -*-
"""
OPS Configurable Financial Report Structure
Adopted from OM accounting_pdf_reports, enhanced with branch filtering.

This allows users to define custom Balance Sheet and P&L structures
with hierarchical groupings and flexible account assignments.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsFinancialReportConfig(models.Model):
    """
    Configurable Financial Report Line Definition.
    Supports hierarchical structure for BS/PL reports.
    """
    _name = 'ops.financial.report.config'
    _description = 'Financial Report Configuration'
    _order = 'sequence, id'
    _parent_store = True
    _parent_order = 'sequence, id'

    name = fields.Char(string='Report Line Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company
    )

    # Hierarchy
    parent_id = fields.Many2one(
        'ops.financial.report.config',
        string='Parent',
        ondelete='cascade',
        domain="[('company_id', '=', company_id)]"
    )
    children_ids = fields.One2many(
        'ops.financial.report.config',
        'parent_id',
        string='Children'
    )
    parent_path = fields.Char(index=True, unaccent=False)

    level = fields.Integer(
        string='Level',
        compute='_compute_level',
        store=True
    )

    # Report Type (Adopted from OM)
    type = fields.Selection([
        ('sum', 'View (Sum of Children)'),
        ('accounts', 'Specific Accounts'),
        ('account_type', 'Account Types'),
        ('report_value', 'Report Line Value'),
    ], string='Type', required=True, default='sum',
       help="""
       • View: Shows sum of all child lines
       • Specific Accounts: Sum of selected accounts
       • Account Types: Sum of accounts matching selected types
       • Report Line Value: References another report line's value
       """)

    # Account Selection (for type='accounts')
    account_ids = fields.Many2many(
        'account.account',
        'ops_financial_report_account_rel',
        'report_id', 'account_id',
        string='Accounts'
    )

    # Account Type Selection (for type='account_type') - Odoo 19 uses account_type field
    account_type_selection = fields.Selection([
        ('asset_receivable', 'Receivable'),
        ('asset_cash', 'Bank and Cash'),
        ('asset_current', 'Current Assets'),
        ('asset_non_current', 'Non-current Assets'),
        ('asset_prepayments', 'Prepayments'),
        ('asset_fixed', 'Fixed Assets'),
        ('liability_payable', 'Payable'),
        ('liability_credit_card', 'Credit Card'),
        ('liability_current', 'Current Liabilities'),
        ('liability_non_current', 'Non-current Liabilities'),
        ('equity', 'Equity'),
        ('equity_unaffected', 'Current Year Earnings'),
        ('income', 'Income'),
        ('income_other', 'Other Income'),
        ('expense', 'Expenses'),
        ('expense_depreciation', 'Depreciation'),
        ('expense_direct_cost', 'Cost of Revenue'),
        ('off_balance', 'Off-Balance Sheet'),
    ], string='Account Type Filter')

    # Multiple account types support
    account_type_ids = fields.Many2many(
        'ir.model.fields.selection',
        'ops_financial_report_account_type_rel',
        'report_id', 'selection_id',
        string='Account Types (Multiple)',
        domain="[('field_id.name', '=', 'account_type'), ('field_id.model', '=', 'account.account')]",
        help='Select multiple account types to include in this line'
    )

    # Report Line Reference (for type='report_value')
    report_line_id = fields.Many2one(
        'ops.financial.report.config',
        string='Source Report Line',
        domain="[('id', '!=', id), ('company_id', '=', company_id)]"
    )

    # Display Options
    sign = fields.Selection([
        ('1', 'Preserve Sign'),
        ('-1', 'Reverse Sign'),
    ], string='Sign', default='1', required=True,
       help='Reverse sign to show expenses/liabilities as positive')

    display_detail = fields.Selection([
        ('no_detail', 'No Detail'),
        ('detail_flat', 'With Detail (Flat)'),
        ('detail_hierarchy', 'With Detail (Hierarchy)'),
    ], string='Display Detail', default='no_detail')

    style = fields.Selection([
        ('normal', 'Normal'),
        ('bold', 'Bold'),
        ('italic', 'Italic'),
        ('bold_italic', 'Bold Italic'),
        ('header', 'Header Style'),
        ('total', 'Total Style'),
    ], string='Style', default='normal')

    # Report Assignment
    report_type = fields.Selection([
        ('balance_sheet', 'Balance Sheet'),
        ('profit_loss', 'Profit & Loss'),
        ('cash_flow', 'Cash Flow'),
        ('custom', 'Custom Report'),
    ], string='Report Type', required=True, default='custom')

    active = fields.Boolean(default=True)

    @api.depends('parent_id', 'parent_path')
    def _compute_level(self):
        for line in self:
            if line.parent_path:
                line.level = line.parent_path.count('/') - 1
            else:
                line.level = 0

    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive report lines.'))

    def get_balance(self, date_from, date_to, branch_ids=None, target_move='posted'):
        """
        Calculate the balance for this report line.

        Args:
            date_from: Start date
            date_to: End date
            branch_ids: List of branch IDs to filter (None = all)
            target_move: 'posted' or 'all'

        Returns:
            float: Calculated balance
        """
        self.ensure_one()

        if self.type == 'sum':
            # Sum of children
            balance = sum(
                child.get_balance(date_from, date_to, branch_ids, target_move)
                for child in self.children_ids
            )

        elif self.type == 'accounts':
            # Sum of specific accounts
            balance = self._get_account_balance(
                self.account_ids, date_from, date_to, branch_ids, target_move
            )

        elif self.type == 'account_type':
            # Sum of accounts matching type
            accounts = self._get_accounts_by_type()
            balance = self._get_account_balance(
                accounts, date_from, date_to, branch_ids, target_move
            )

        elif self.type == 'report_value':
            # Value from another line
            if self.report_line_id:
                balance = self.report_line_id.get_balance(
                    date_from, date_to, branch_ids, target_move
                )
            else:
                balance = 0.0

        else:
            balance = 0.0

        # Apply sign
        if self.sign == '-1':
            balance = -balance

        return balance

    def _get_accounts_by_type(self):
        """Get accounts matching the selected account type."""
        self.ensure_one()

        domain = [('company_id', '=', self.company_id.id)]

        if self.account_type_selection:
            domain.append(('account_type', '=', self.account_type_selection))

        return self.env['account.account'].search(domain)

    def _get_account_balance(self, accounts, date_from, date_to, branch_ids, target_move):
        """
        Get balance for given accounts using read_group for performance.
        """
        if not accounts:
            return 0.0

        # Build domain
        domain = [
            ('account_id', 'in', accounts.ids),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('company_id', '=', self.company_id.id),
        ]

        if target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))

        if branch_ids:
            domain.append(('ops_branch_id', 'in', branch_ids))

        # Use read_group for performance
        result = self.env['account.move.line'].read_group(
            domain=domain,
            fields=['balance:sum'],
            groupby=[]
        )

        return result[0]['balance'] if result else 0.0

    def get_report_lines_data(self, date_from, date_to, branch_ids=None,
                              target_move='posted', comparison_date_from=None,
                              comparison_date_to=None):
        """
        Get hierarchical report data with optional comparison period.

        Returns list of dictionaries with line data for report rendering.
        """
        self.ensure_one()

        lines = []
        self._collect_report_lines(
            lines, date_from, date_to, branch_ids, target_move,
            comparison_date_from, comparison_date_to
        )
        return lines

    def _collect_report_lines(self, lines, date_from, date_to, branch_ids,
                              target_move, comparison_date_from, comparison_date_to,
                              level=0):
        """Recursively collect report line data."""
        self.ensure_one()

        balance = self.get_balance(date_from, date_to, branch_ids, target_move)

        comparison_balance = 0.0
        variance = 0.0
        variance_pct = 0.0

        if comparison_date_from and comparison_date_to:
            comparison_balance = self.get_balance(
                comparison_date_from, comparison_date_to, branch_ids, target_move
            )
            variance = balance - comparison_balance
            if comparison_balance:
                variance_pct = (variance / abs(comparison_balance)) * 100

        line_data = {
            'id': self.id,
            'name': self.name,
            'level': level,
            'type': self.type,
            'style': self.style,
            'balance': balance,
            'comparison_balance': comparison_balance,
            'variance': variance,
            'variance_pct': variance_pct,
        }

        # Add account details if requested
        if self.display_detail != 'no_detail' and self.type in ('accounts', 'account_type'):
            line_data['account_details'] = self._get_account_details(
                date_from, date_to, branch_ids, target_move
            )

        lines.append(line_data)

        # Process children for sum type
        if self.type == 'sum':
            for child in self.children_ids.sorted('sequence'):
                child._collect_report_lines(
                    lines, date_from, date_to, branch_ids, target_move,
                    comparison_date_from, comparison_date_to, level + 1
                )

    def _get_account_details(self, date_from, date_to, branch_ids, target_move):
        """Get account-level details for detail display modes."""
        self.ensure_one()

        if self.type == 'accounts':
            accounts = self.account_ids
        elif self.type == 'account_type':
            accounts = self._get_accounts_by_type()
        else:
            return []

        details = []
        for account in accounts.sorted('code'):
            domain = [
                ('account_id', '=', account.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('company_id', '=', self.company_id.id),
            ]

            if target_move == 'posted':
                domain.append(('parent_state', '=', 'posted'))

            if branch_ids:
                domain.append(('ops_branch_id', 'in', branch_ids))

            result = self.env['account.move.line'].read_group(
                domain=domain,
                fields=['balance:sum'],
                groupby=[]
            )

            balance = result[0]['balance'] if result else 0.0

            if balance:  # Only include accounts with activity
                # Apply sign
                if self.sign == '-1':
                    balance = -balance

                details.append({
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance': balance,
                })

        return details

    @api.model
    def generate_default_balance_sheet(self, company_id=None):
        """Generate default Balance Sheet structure."""
        company = self.env['res.company'].browse(company_id) if company_id else self.env.company

        # Check if already exists
        existing = self.search([
            ('company_id', '=', company.id),
            ('report_type', '=', 'balance_sheet'),
            ('parent_id', '=', False)
        ])
        if existing:
            return existing[0]

        # Create structure
        bs_root = self.create({
            'name': 'Balance Sheet',
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'style': 'header',
            'sequence': 1,
        })

        # ASSETS
        assets = self.create({
            'name': 'ASSETS',
            'parent_id': bs_root.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'style': 'bold',
            'sequence': 10,
        })

        # Current Assets Section
        current_assets = self.create({
            'name': 'Current Assets',
            'parent_id': assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'sequence': 11,
        })

        self.create({
            'name': 'Bank and Cash',
            'parent_id': current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'asset_cash',
            'sequence': 12,
        })

        self.create({
            'name': 'Receivables',
            'parent_id': current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'asset_receivable',
            'sequence': 13,
        })

        self.create({
            'name': 'Current Assets',
            'parent_id': current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'asset_current',
            'sequence': 14,
        })

        self.create({
            'name': 'Prepayments',
            'parent_id': current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'asset_prepayments',
            'sequence': 15,
        })

        # Total Current Assets
        self.create({
            'name': 'Total Current Assets',
            'parent_id': current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'report_value',
            'report_line_id': current_assets.id,
            'style': 'total',
            'sequence': 19,
        })

        # Non-Current Assets Section
        non_current_assets = self.create({
            'name': 'Non-Current Assets',
            'parent_id': assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'sequence': 20,
        })

        self.create({
            'name': 'Fixed Assets',
            'parent_id': non_current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'asset_fixed',
            'sequence': 21,
        })

        self.create({
            'name': 'Non-current Assets',
            'parent_id': non_current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'asset_non_current',
            'sequence': 22,
        })

        # Total Non-Current Assets
        self.create({
            'name': 'Total Non-Current Assets',
            'parent_id': non_current_assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'report_value',
            'report_line_id': non_current_assets.id,
            'style': 'total',
            'sequence': 29,
        })

        # TOTAL ASSETS
        self.create({
            'name': 'TOTAL ASSETS',
            'parent_id': assets.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'report_value',
            'report_line_id': assets.id,
            'style': 'total',
            'sequence': 99,
        })

        # LIABILITIES
        liabilities = self.create({
            'name': 'LIABILITIES',
            'parent_id': bs_root.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'style': 'bold',
            'sign': '-1',
            'sequence': 100,
        })

        # Current Liabilities
        current_liabilities = self.create({
            'name': 'Current Liabilities',
            'parent_id': liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'sign': '-1',
            'sequence': 110,
        })

        self.create({
            'name': 'Payables',
            'parent_id': current_liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'liability_payable',
            'sign': '-1',
            'sequence': 111,
        })

        self.create({
            'name': 'Credit Cards',
            'parent_id': current_liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'liability_credit_card',
            'sign': '-1',
            'sequence': 112,
        })

        self.create({
            'name': 'Current Liabilities',
            'parent_id': current_liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'liability_current',
            'sign': '-1',
            'sequence': 113,
        })

        # Total Current Liabilities
        self.create({
            'name': 'Total Current Liabilities',
            'parent_id': current_liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'report_value',
            'report_line_id': current_liabilities.id,
            'style': 'total',
            'sequence': 119,
        })

        # Non-Current Liabilities
        self.create({
            'name': 'Non-Current Liabilities',
            'parent_id': liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'liability_non_current',
            'sign': '-1',
            'sequence': 120,
        })

        # TOTAL LIABILITIES
        self.create({
            'name': 'TOTAL LIABILITIES',
            'parent_id': liabilities.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'report_value',
            'report_line_id': liabilities.id,
            'style': 'total',
            'sequence': 199,
        })

        # EQUITY
        equity = self.create({
            'name': 'EQUITY',
            'parent_id': bs_root.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'style': 'bold',
            'sign': '-1',
            'sequence': 200,
        })

        self.create({
            'name': 'Equity',
            'parent_id': equity.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'equity',
            'sign': '-1',
            'sequence': 210,
        })

        self.create({
            'name': 'Current Year Unallocated Earnings',
            'parent_id': equity.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'account_type',
            'account_type_selection': 'equity_unaffected',
            'sign': '-1',
            'sequence': 220,
        })

        # TOTAL EQUITY
        self.create({
            'name': 'TOTAL EQUITY',
            'parent_id': equity.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'report_value',
            'report_line_id': equity.id,
            'style': 'total',
            'sequence': 299,
        })

        # TOTAL LIABILITIES + EQUITY
        self.create({
            'name': 'TOTAL LIABILITIES + EQUITY',
            'parent_id': bs_root.id,
            'company_id': company.id,
            'report_type': 'balance_sheet',
            'type': 'sum',
            'style': 'total',
            'sequence': 999,
        })

        _logger.info(f"Generated default Balance Sheet structure for {company.name}")
        return bs_root

    @api.model
    def generate_default_profit_loss(self, company_id=None):
        """Generate default Profit & Loss structure."""
        company = self.env['res.company'].browse(company_id) if company_id else self.env.company

        # Check if already exists
        existing = self.search([
            ('company_id', '=', company.id),
            ('report_type', '=', 'profit_loss'),
            ('parent_id', '=', False)
        ])
        if existing:
            return existing[0]

        # Create structure
        pl_root = self.create({
            'name': 'Profit & Loss',
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'sum',
            'style': 'header',
            'sequence': 1,
        })

        # INCOME
        income = self.create({
            'name': 'INCOME',
            'parent_id': pl_root.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'sum',
            'style': 'bold',
            'sign': '-1',
            'sequence': 10,
        })

        self.create({
            'name': 'Operating Income',
            'parent_id': income.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'account_type',
            'account_type_selection': 'income',
            'sign': '-1',
            'sequence': 11,
        })

        self.create({
            'name': 'Other Income',
            'parent_id': income.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'account_type',
            'account_type_selection': 'income_other',
            'sign': '-1',
            'sequence': 12,
        })

        # TOTAL INCOME
        self.create({
            'name': 'TOTAL INCOME',
            'parent_id': income.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'report_value',
            'report_line_id': income.id,
            'style': 'total',
            'sequence': 19,
        })

        # COST OF SALES
        cogs = self.create({
            'name': 'COST OF SALES',
            'parent_id': pl_root.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'account_type',
            'account_type_selection': 'expense_direct_cost',
            'style': 'bold',
            'sequence': 20,
        })

        # GROSS PROFIT
        self.create({
            'name': 'GROSS PROFIT',
            'parent_id': pl_root.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'sum',
            'style': 'total',
            'sequence': 30,
        })

        # OPERATING EXPENSES
        expenses = self.create({
            'name': 'OPERATING EXPENSES',
            'parent_id': pl_root.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'sum',
            'style': 'bold',
            'sequence': 40,
        })

        self.create({
            'name': 'Expenses',
            'parent_id': expenses.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'account_type',
            'account_type_selection': 'expense',
            'sequence': 41,
        })

        self.create({
            'name': 'Depreciation',
            'parent_id': expenses.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'account_type',
            'account_type_selection': 'expense_depreciation',
            'sequence': 42,
        })

        # TOTAL OPERATING EXPENSES
        self.create({
            'name': 'TOTAL OPERATING EXPENSES',
            'parent_id': expenses.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'report_value',
            'report_line_id': expenses.id,
            'style': 'total',
            'sequence': 49,
        })

        # NET PROFIT
        self.create({
            'name': 'NET PROFIT',
            'parent_id': pl_root.id,
            'company_id': company.id,
            'report_type': 'profit_loss',
            'type': 'sum',
            'style': 'total',
            'sequence': 100,
        })

        _logger.info(f"Generated default P&L structure for {company.name}")
        return pl_root
