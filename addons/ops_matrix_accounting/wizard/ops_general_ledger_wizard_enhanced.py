# -*- coding: utf-8 -*-
"""
OPS Matrix Financial Intelligence Engine
=========================================

The "Big 8" Unified Financial Reporting Wizard with Matrix Dimension filtering.
Consolidates all core financial reports into a single, powerful interface.

Reports Supported:
- General Ledger (GL)
- Trial Balance (TB)
- Profit & Loss (PL)
- Balance Sheet (BS)
- Cash Flow Statement (CF)
- Aged Partner Balance (AGED)
- Partner Ledger (PARTNER)
- Statement of Account (SOA)

Author: OPS Matrix Framework
Version: 2.0 (Phase 2 - Big 8 Consolidation)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils, float_round
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
import xlsxwriter
from io import BytesIO
import base64
from ..report.excel_styles import get_corporate_excel_formats

_logger = logging.getLogger(__name__)


class OpsGeneralLedgerWizardEnhanced(models.TransientModel):
    """Matrix Financial Intelligence - Unified Reporting Engine"""
    _name = 'ops.general.ledger.wizard.enhanced'
    _inherit = 'ops.base.report.wizard'
    _description = 'Matrix Financial Intelligence'

    # Template domain override
    report_template_id = fields.Many2one(
        domain="[('engine', '=', 'financial'), '|', ('is_global', '=', True), ('user_id', '=', uid)]"
    )

    # ============================================
    # 0. REPORT TYPE SELECTOR (THE BIG 8)
    # ============================================
    report_type = fields.Selection([
        ('gl', 'General Ledger'),
        ('tb', 'Trial Balance'),
        ('pl', 'Profit & Loss'),
        ('bs', 'Balance Sheet'),
        ('cf', 'Cash Flow Statement'),
        ('aged', 'Aged Partner Balance'),
        ('partner', 'Partner Ledger'),
        ('soa', 'Statement of Account'),
    ], string='Report Type', required=True, default='gl',
       help='Select the type of financial report to generate')

    # ============================================
    # 1. PERIOD FILTERS
    # ============================================
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: date_utils.start_of(datetime.now(), 'year')
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: date_utils.end_of(datetime.now(), 'month')
    )

    # For Balance Sheet - single date
    as_of_date = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        help='Balance Sheet date (shows cumulative balances up to this date)'
    )

    # ============================================
    # 2. COMPANY & JOURNALS
    # ============================================
    # company_id inherited from ops.base.report.wizard
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journals',
        help='Leave empty for all journals'
    )

    # ============================================
    # 3. MATRIX DIMENSION FILTERS
    # ============================================
    branch_ids = fields.Many2many(
        'ops.branch',
        'gl_wizard_branch_rel',
        'wizard_id',
        'branch_id',
        string='Branches',
        help='Filter by specific branches. Leave empty for all branches.'
    )

    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'gl_wizard_bu_rel',
        'wizard_id',
        'bu_id',
        string='Business Units',
        help='Filter by specific business units. Leave empty for all BUs.'
    )

    matrix_filter_mode = fields.Selection([
        ('any', 'Any Dimension (Branch OR BU)'),
        ('both', 'Both Dimensions (Branch AND BU)'),
        ('exact', 'Exact Combination'),
    ], string='Matrix Filter Mode', default='any', help="""
        - Any: Show transactions that match ANY selected branch/BU
        - Both: Show transactions that match BOTH selected branch AND BU
        - Exact: Show transactions with exact branch/BU combinations
    """)

    # ============================================
    # 4. ACCOUNT FILTERS
    # ============================================
    account_ids = fields.Many2many(
        'account.account',
        'gl_wizard_account_rel',
        'wizard_id',
        'account_id',
        string='Accounts',
        help='Filter by specific accounts. Leave empty for all accounts.'
    )

    account_type_ids = fields.Selection(
        selection=[
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
        ],
        string='Account Type',
        help='Filter by specific account type'
    )

    display_account = fields.Selection([
        ('all', 'All Accounts'),
        ('movement', 'With Movements'),
        ('not_zero', 'With Balance Not Zero'),
    ], string='Display Accounts', default='movement', required=True)

    # ============================================
    # 5. TRANSACTION FILTERS
    # ============================================
    target_move = fields.Selection([
        ('posted', 'Posted Entries'),
        ('all', 'All Entries'),
    ], string='Target Moves', default='posted', required=True)

    reconciled = fields.Selection([
        ('all', 'All Items'),
        ('reconciled', 'Reconciled Only'),
        ('unreconciled', 'Unreconciled Only'),
    ], string='Reconciliation Status', default='all', required=True)

    # ============================================
    # 6. PARTNER FILTERS (For Partner Reports)
    # ============================================
    partner_ids = fields.Many2many(
        'res.partner',
        'gl_wizard_partner_rel',
        'wizard_id',
        'partner_id',
        string='Partners',
        help='Filter by specific partners. Required for Statement of Account.'
    )

    partner_type = fields.Selection([
        ('all', 'All Partners'),
        ('customer', 'Customers Only'),
        ('supplier', 'Suppliers Only'),
    ], string='Partner Type', default='all',
       help='Filter partners by type for aged/partner reports')

    # ============================================
    # 7. AGED REPORT SPECIFIC
    # ============================================
    aging_type = fields.Selection([
        ('receivable', 'Receivable (Customers)'),
        ('payable', 'Payable (Suppliers)'),
        ('both', 'Both'),
    ], string='Aging Type', default='receivable',
       help='Type of aged balance to calculate')

    period_length = fields.Integer(
        string='Period Length (days)',
        default=30,
        help='Number of days per aging period'
    )

    # ============================================
    # 8. CONSOLIDATION & GROUPING OPTIONS
    # ============================================
    consolidate_by_branch = fields.Boolean(
        string='Consolidate by Branch',
        help='Show totals grouped by branch',
        default=False
    )

    consolidate_by_bu = fields.Boolean(
        string='Consolidate by Business Unit',
        help='Show totals grouped by business unit',
        default=False
    )

    consolidate_by_partner = fields.Boolean(
        string='Consolidate by Partner',
        help='Show totals grouped by partner',
        default=False
    )

    group_by_date = fields.Selection([
        ('none', 'No Grouping'),
        ('day', 'Daily'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('quarter', 'Quarterly'),
        ('year', 'Yearly'),
    ], string='Group by Date', default='none', required=True)

    # ============================================
    # 9. OUTPUT OPTIONS
    # ============================================
    report_format = fields.Selection([
        ('detailed', 'Detailed Lines'),
        ('summary', 'Summary Only'),
        ('both', 'Both Detailed and Summary'),
    ], string='Report Format', default='detailed', required=True)

    sort_by = fields.Selection([
        ('date', 'Date'),
        ('account', 'Account'),
        ('partner', 'Partner'),
        ('branch', 'Branch'),
        ('bu', 'Business Unit'),
    ], string='Sort By', default='date', required=True)

    include_initial_balance = fields.Boolean(
        string='Include Initial Balance',
        default=True,
        help='Show opening balance before period'
    )

    # ============================================
    # 10. COMPUTED FIELDS (inherited from base, with overrides)
    # ============================================
    # filter_summary, record_count, report_title inherited from base
    # currency_id inherited from base

    # ============================================
    # BASE CLASS HOOK IMPLEMENTATIONS
    # ============================================

    def _get_engine_name(self):
        """Return engine name for template filtering."""
        return 'financial'

    def _get_report_titles(self):
        """Return mapping of report_type to human-readable title."""
        return {
            'gl': 'General Ledger',
            'tb': 'Trial Balance',
            'pl': 'Profit & Loss Statement',
            'bs': 'Balance Sheet',
            'cf': 'Cash Flow Statement',
            'aged': 'Aged Partner Balance',
            'partner': 'Partner Ledger',
            'soa': 'Statement of Account',
        }

    def _get_scalar_fields_for_template(self):
        """Return scalar fields for template save/load."""
        return [
            'report_type', 'target_move', 'reconciled', 'display_account',
            'matrix_filter_mode', 'report_format', 'sort_by', 'group_by_date',
            'consolidate_by_branch', 'consolidate_by_bu', 'consolidate_by_partner',
            'include_initial_balance', 'aging_type', 'period_length', 'partner_type',
            'account_type_ids',
        ]

    def _get_m2m_fields_for_template(self):
        """Return Many2many fields for template save/load."""
        return ['branch_ids', 'business_unit_ids', 'account_ids', 'journal_ids', 'partner_ids']

    def _get_report_template_xmlid(self):
        """Return XML ID of report template based on report_type."""
        self.ensure_one()

        template_mapping = {
            'gl': 'ops_matrix_accounting.report_general_ledger',
            'tb': 'ops_matrix_accounting.report_trial_balance',
            'pl': 'ops_matrix_accounting.report_profit_loss',
            'bs': 'ops_matrix_accounting.report_balance_sheet',
            'cf': 'ops_matrix_accounting.report_cash_flow',
            'aged_receivable': 'ops_matrix_accounting.report_aged_receivable',
            'aged_payable': 'ops_matrix_accounting.report_aged_payable',
            'partner': 'ops_matrix_accounting.report_partner_ledger',
            'statement': 'ops_matrix_accounting.report_statement_account',
        }

        return template_mapping.get(self.report_type, 'ops_matrix_accounting.report_general_ledger')

    def _add_filter_summary_parts(self, parts):
        """Add financial-specific filter descriptions."""
        # Date handling differs by report type
        if self.report_type == 'bs':
            if self.as_of_date:
                # Replace generic date range with as_of_date
                parts[:] = [p for p in parts if not p.startswith('Period:')]
                parts.append(f"As of: {self.as_of_date}")

        # Matrix dimensions
        if self.branch_ids:
            if len(self.branch_ids) <= 3:
                branch_names = self.branch_ids.mapped('code')
                parts.append(f"Branches: {', '.join(branch_names)}")
            else:
                parts.append(f"Branches: {len(self.branch_ids)} selected")

        if self.business_unit_ids:
            if len(self.business_unit_ids) <= 3:
                bu_names = self.business_unit_ids.mapped('code')
                parts.append(f"BUs: {', '.join(bu_names)}")
            else:
                parts.append(f"BUs: {len(self.business_unit_ids)} selected")

        # Partners
        if self.partner_ids:
            parts.append(f"Partners: {len(self.partner_ids)} selected")

        # Transaction filters
        if self.target_move == 'posted':
            parts.append("Posted only")

    def _validate_filters_extra(self):
        """Perform financial-specific validation."""
        # SoA requires partner selection
        if self.report_type == 'soa' and not self.partner_ids:
            raise ValidationError(_(
                "Statement of Account requires at least one partner to be selected."
            ))

        # Matrix exact mode validation
        if self.matrix_filter_mode == 'exact' and (not self.branch_ids or not self.business_unit_ids):
            raise ValidationError(_(
                "Exact combination mode requires both Branch and Business Unit filters."
            ))

        # Large dataset warnings
        date_diff = (self.date_to - self.date_from).days
        if date_diff > 365 and self.report_format == 'detailed' and not self.account_ids:
            return {
                'warning': {
                    'title': _('Large Date Range'),
                    'message': _(
                        'You are generating a detailed report for more than 1 year. '
                        'Consider using summary format or filtering by accounts.'
                    ),
                }
            }

        if self.record_count > 50000 and self.report_format == 'detailed':
            return {
                'warning': {
                    'title': _('Large Result Set'),
                    'message': _(
                        'Approximately %(count)d records. Consider summary format.'
                    ) % {'count': self.record_count},
                }
            }

        return True

    def _estimate_record_count(self):
        """Estimate number of account move lines matching filters."""
        if not self.date_from or not self.date_to:
            return 0
        domain = self._build_domain()
        return self.env['account.move.line'].search_count(domain)

    # ============================================
    # DOMAIN BUILDING METHODS
    # ============================================

    def _build_domain(self):
        """Build complete domain for account move line query."""
        self.ensure_one()

        # Date handling differs by report type
        if self.report_type == 'bs':
            # Balance Sheet: cumulative to as_of_date
            domain = [
                ('date', '<=', self.as_of_date or self.date_to),
                ('company_id', '=', self.company_id.id),
            ]
        else:
            domain = [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', '=', self.company_id.id),
            ]

        # Target moves filter
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))

        # Reconciliation filter (not for P&L/BS)
        if self.report_type not in ('pl', 'bs', 'cf'):
            if self.reconciled == 'unreconciled':
                domain.append(('reconciled', '=', False))
            elif self.reconciled == 'reconciled':
                domain.append(('reconciled', '=', True))

        # Account type filters based on report type
        domain += self._get_account_type_domain()

        # Account filters
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))

        if self.account_type_ids:
            account_ids = self.env['account.account'].search([
                ('account_type', '=', self.account_type_ids),
                ('company_ids', 'in', [self.company_id.id])
            ])
            domain.append(('account_id', 'in', account_ids.ids))

        # Journal filters
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))

        # Partner filter
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        elif self.report_type in ('aged', 'partner', 'soa'):
            # For partner reports, filter by partner type
            if self.partner_type == 'customer':
                domain.append(('partner_id.customer_rank', '>', 0))
            elif self.partner_type == 'supplier':
                domain.append(('partner_id.supplier_rank', '>', 0))

        # Matrix dimension filters
        matrix_domain = self._build_matrix_domain()
        if matrix_domain:
            domain += matrix_domain

        return domain

    def _get_account_type_domain(self):
        """Get account type domain based on report type."""
        self.ensure_one()

        if self.report_type == 'pl':
            # P&L: Income and Expense accounts
            return [('account_id.account_type', 'in', [
                'income', 'income_other',
                'expense', 'expense_depreciation', 'expense_direct_cost'
            ])]
        elif self.report_type == 'bs':
            # BS: Asset, Liability, Equity accounts
            return [('account_id.account_type', 'in', [
                'asset_receivable', 'asset_cash', 'asset_current',
                'asset_non_current', 'asset_prepayments', 'asset_fixed',
                'liability_payable', 'liability_credit_card',
                'liability_current', 'liability_non_current',
                'equity', 'equity_unaffected'
            ])]
        elif self.report_type == 'cf':
            # CF: Bank and Cash accounts primarily
            return [('account_id.account_type', 'in', ['asset_cash'])]
        elif self.report_type == 'aged':
            # Aged: Receivable or Payable based on aging_type
            if self.aging_type == 'receivable':
                return [('account_id.account_type', '=', 'asset_receivable')]
            elif self.aging_type == 'payable':
                return [('account_id.account_type', '=', 'liability_payable')]
            else:
                return [('account_id.account_type', 'in', ['asset_receivable', 'liability_payable'])]
        elif self.report_type in ('partner', 'soa'):
            # Partner reports: Receivable and Payable
            return [('account_id.account_type', 'in', ['asset_receivable', 'liability_payable'])]

        return []

    def _build_matrix_domain(self):
        """Build matrix dimension domain based on filter mode."""
        matrix_domain = []

        if not self.branch_ids and not self.business_unit_ids:
            return matrix_domain

        branch_domain = []
        if self.branch_ids:
            branch_domain = [('ops_branch_id', 'in', self.branch_ids.ids)]

        bu_domain = []
        if self.business_unit_ids:
            bu_domain = [('ops_business_unit_id', 'in', self.business_unit_ids.ids)]

        if self.matrix_filter_mode == 'any':
            if branch_domain and bu_domain:
                matrix_domain = ['|'] + branch_domain + bu_domain
            elif branch_domain:
                matrix_domain = branch_domain
            elif bu_domain:
                matrix_domain = bu_domain
        elif self.matrix_filter_mode == 'both':
            if branch_domain and bu_domain:
                matrix_domain = branch_domain + bu_domain
            else:
                matrix_domain = branch_domain or bu_domain
        elif self.matrix_filter_mode == 'exact':
            matrix_domain = []
            if branch_domain:
                matrix_domain += branch_domain
            if bu_domain:
                matrix_domain += bu_domain

        return matrix_domain

    def _get_exact_matrix_combinations(self):
        """Get list of exact branch-BU combinations for exact filter mode."""
        combinations = set()
        if self.branch_ids and self.business_unit_ids:
            for branch in self.branch_ids:
                for bu in self.business_unit_ids:
                    if branch in bu.branch_ids:
                        combinations.add((branch.id, bu.id))
        return combinations

    # ============================================
    # REPORT DISPATCH & GENERATION
    # ============================================
    # action_generate_report inherited from base class

    def _get_report_data(self):
        """Dispatch to appropriate report data method."""
        self.ensure_one()

        dispatch = {
            'gl': self._get_gl_data,
            'tb': self._get_trial_balance_data,
            'pl': self._get_financial_statement_data,
            'bs': self._get_financial_statement_data,
            'cf': self._get_cash_flow_data,
            'aged': self._get_aged_partner_data,
            'partner': self._get_partner_ledger_data,
            'soa': self._get_statement_of_account_data,
        }

        handler = dispatch.get(self.report_type, self._get_gl_data)
        return handler()

    # ============================================
    # GENERAL LEDGER DATA
    # ============================================

    def _get_gl_data(self):
        """Get General Ledger report data."""
        self.ensure_one()

        domain = self._build_domain()
        MoveLine = self.env['account.move.line']

        # Initial balances
        initial_balances = {}
        if self.include_initial_balance:
            initial_balances = self._get_initial_balances()

        # Get move lines
        order_by = self._get_sort_order()
        lines = MoveLine.search(domain, order=order_by)

        # Apply exact matrix filtering if needed
        if self.matrix_filter_mode == 'exact' and self.branch_ids and self.business_unit_ids:
            exact_combinations = self._get_exact_matrix_combinations()
            lines = lines.filtered(
                lambda l: (l.ops_branch_id.id, l.ops_business_unit_id.id) in exact_combinations
            )

        # Process based on format
        if self.report_format == 'summary':
            processed_data = self._process_summary_data(lines)
        elif self.report_format == 'detailed':
            processed_data = self._process_detailed_data(lines)
        else:
            processed_data = {
                'summary': self._process_summary_data(lines),
                'detailed': self._process_detailed_data(lines),
            }

        return self._build_report_dict(lines, processed_data, initial_balances)

    # ============================================
    # TRIAL BALANCE DATA
    # ============================================

    def _get_trial_balance_data(self):
        """Get Trial Balance report data."""
        self.ensure_one()

        MoveLine = self.env['account.move.line']
        Account = self.env['account.account']

        # Get all accounts with activity
        domain = self._build_domain()

        # Get initial balances
        initial_domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
        ]
        initial_domain += self._build_matrix_domain()

        # Read group for period and initial
        period_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )

        initial_data = MoveLine._read_group(
            domain=initial_domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )

        # Build initial balance map
        initial_map = {}
        for item in initial_data:
            account = item[0]
            if account:
                initial_map[account.id] = {
                    'debit': item[1] or 0,
                    'credit': item[2] or 0,
                    'balance': item[3] or 0,
                }

        # Build trial balance lines
        tb_lines = []
        total_initial_debit = total_initial_credit = 0
        total_period_debit = total_period_credit = 0
        total_ending_debit = total_ending_credit = 0

        for item in period_data:
            account = item[0]
            if not account:
                continue

            period_debit = item[1] or 0
            period_credit = item[2] or 0

            initial = initial_map.get(account.id, {'debit': 0, 'credit': 0, 'balance': 0})
            initial_balance = initial['balance']

            ending_balance = initial_balance + (period_debit - period_credit)

            # Determine debit/credit presentation
            ending_debit = ending_balance if ending_balance > 0 else 0
            ending_credit = abs(ending_balance) if ending_balance < 0 else 0

            tb_lines.append({
                'account_id': account.id,
                'account_code': account.code,
                'account_name': account.name,
                'account_type': account.account_type,
                'initial_debit': initial['debit'],
                'initial_credit': initial['credit'],
                'initial_balance': initial_balance,
                'period_debit': period_debit,
                'period_credit': period_credit,
                'ending_debit': ending_debit,
                'ending_credit': ending_credit,
                'ending_balance': ending_balance,
            })

            total_initial_debit += initial['debit']
            total_initial_credit += initial['credit']
            total_period_debit += period_debit
            total_period_credit += period_credit
            total_ending_debit += ending_debit
            total_ending_credit += ending_credit

        # Sort by account code
        tb_lines.sort(key=lambda x: x['account_code'])

        return {
            'report_type': 'tb',
            'report_title': 'Trial Balance',
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'filters': self._get_filter_summary_dict(),
            'data': tb_lines,
            'totals': {
                'initial_debit': total_initial_debit,
                'initial_credit': total_initial_credit,
                'period_debit': total_period_debit,
                'period_credit': total_period_credit,
                'ending_debit': total_ending_debit,
                'ending_credit': total_ending_credit,
                'line_count': len(tb_lines),
            },
        }

    # ============================================
    # FINANCIAL STATEMENT DATA (P&L, BS)
    # ============================================

    def _get_financial_statement_data(self):
        """
        Get P&L or Balance Sheet report data.
        Phase 14: Now returns hierarchical CoA structure for audit-grade reports.
        """
        self.ensure_one()

        MoveLine = self.env['account.move.line']
        domain = self._build_domain()

        # Phase 14: Build hierarchical data
        hierarchy = self._get_hierarchical_financial_data()
        hierarchical_data = self._flatten_hierarchy_for_template(hierarchy, self.report_type)

        # Also get flat data for backward compatibility
        data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id', 'account_id.account_type'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )

        # Organize by account type (flat structure for backward compatibility)
        sections = {}
        for item in data:
            account = item[0]
            account_type = item[1]
            if not account:
                continue

            if account_type not in sections:
                sections[account_type] = {
                    'type': account_type,
                    'label': self._get_account_type_label(account_type),
                    'accounts': [],
                    'total_debit': 0,
                    'total_credit': 0,
                    'total_balance': 0,
                }

            debit = item[2] or 0
            credit = item[3] or 0
            balance = item[4] or 0

            sections[account_type]['accounts'].append({
                'account_id': account.id,
                'account_code': account.code,
                'account_name': account.name,
                'debit': debit,
                'credit': credit,
                'balance': balance,
            })
            sections[account_type]['total_debit'] += debit
            sections[account_type]['total_credit'] += credit
            sections[account_type]['total_balance'] += balance

        # Calculate totals based on report type
        if self.report_type == 'pl':
            income_total = sum(
                s['total_balance'] for k, s in sections.items()
                if k in ('income', 'income_other')
            )
            expense_total = sum(
                s['total_balance'] for k, s in sections.items()
                if k in ('expense', 'expense_depreciation', 'expense_direct_cost')
            )
            # Income is credit-based (negative balance), expense is debit-based (positive)
            net_income = abs(income_total) - expense_total

            # Get COGS for gross profit calculation
            cogs_total = sum(
                s['total_balance'] for k, s in sections.items()
                if k == 'expense_direct_cost'
            )

            summary = {
                'total_income': abs(income_total),
                'total_expense': expense_total,
                'cogs_total': cogs_total,
                'gross_profit': abs(income_total) - cogs_total,
                'net_income': net_income,
            }
        else:  # Balance Sheet
            asset_total = sum(
                s['total_balance'] for k, s in sections.items()
                if k.startswith('asset_')
            )
            liability_total = sum(
                s['total_balance'] for k, s in sections.items()
                if k.startswith('liability_')
            )
            equity_total = sum(
                s['total_balance'] for k, s in sections.items()
                if k.startswith('equity')
            )

            summary = {
                'total_assets': asset_total,
                'total_liabilities': abs(liability_total),
                'total_equity': abs(equity_total),
                'check_balance': asset_total + liability_total + equity_total,
            }

        return {
            'report_type': self.report_type,
            'report_title': 'Profit & Loss Statement' if self.report_type == 'pl' else 'Balance Sheet',
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from) if self.report_type == 'pl' else None,
            'date_to': str(self.date_to) if self.report_type == 'pl' else None,
            'as_of_date': str(self.as_of_date) if self.report_type == 'bs' else None,
            'filters': self._get_filter_summary_dict(),
            'sections': list(sections.values()),
            'summary': summary,
            # Phase 14: Hierarchical data for audit-grade rendering
            'hierarchy': hierarchical_data,
            'use_hierarchy': True,  # Flag to enable hierarchical rendering
        }

    def _get_account_type_label(self, account_type):
        """Get human-readable label for account type."""
        labels = {
            'asset_receivable': 'Accounts Receivable',
            'asset_cash': 'Bank and Cash',
            'asset_current': 'Current Assets',
            'asset_non_current': 'Non-current Assets',
            'asset_prepayments': 'Prepayments',
            'asset_fixed': 'Fixed Assets',
            'liability_payable': 'Accounts Payable',
            'liability_credit_card': 'Credit Card',
            'liability_current': 'Current Liabilities',
            'liability_non_current': 'Non-current Liabilities',
            'equity': 'Equity',
            'equity_unaffected': 'Current Year Earnings',
            'income': 'Operating Income',
            'income_other': 'Other Income',
            'expense': 'Operating Expenses',
            'expense_depreciation': 'Depreciation',
            'expense_direct_cost': 'Cost of Revenue',
            'off_balance': 'Off-Balance Sheet',
        }
        return labels.get(account_type, account_type)

    # ============================================
    # PHASE 14: HIERARCHICAL COA LOGIC
    # "The Boardroom Standard" - Audit-Grade Reports
    # ============================================

    def _get_hierarchical_financial_data(self):
        """
        Build hierarchical Chart of Accounts structure for audit-grade reports.
        Returns data organized by: Group -> Sub-groups -> Accounts
        Shows 0.00 balances for relevant accounts.
        """
        self.ensure_one()

        MoveLine = self.env['account.move.line']
        Account = self.env['account.account']
        AccountGroup = self.env['account.group']

        domain = self._build_domain()

        # Get balances grouped by account
        balance_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )

        # Build balance map: account_id -> {debit, credit, balance}
        balance_map = {}
        for item in balance_data:
            account = item[0]
            if account:
                balance_map[account.id] = {
                    'debit': item[1] or 0,
                    'credit': item[2] or 0,
                    'balance': item[3] or 0,
                }

        # Get all relevant accounts for this report type
        account_type_filter = self._get_account_types_for_report()
        all_accounts = Account.search([
            ('account_type', 'in', account_type_filter),
            ('company_ids', 'in', [self.company_id.id]),
        ], order='code')

        # Get all account groups
        all_groups = AccountGroup.search([
            ('company_id', '=', self.company_id.id),
        ], order='code_prefix_start')

        # Build hierarchical structure
        hierarchy = self._build_account_hierarchy(all_accounts, all_groups, balance_map)

        return hierarchy

    def _get_account_types_for_report(self):
        """Get account types relevant for the current report type."""
        if self.report_type == 'pl':
            return [
                'income', 'income_other',
                'expense', 'expense_depreciation', 'expense_direct_cost'
            ]
        elif self.report_type == 'bs':
            return [
                'asset_receivable', 'asset_cash', 'asset_current',
                'asset_non_current', 'asset_prepayments', 'asset_fixed',
                'liability_payable', 'liability_credit_card',
                'liability_current', 'liability_non_current',
                'equity', 'equity_unaffected'
            ]
        return []

    def _build_account_hierarchy(self, accounts, groups, balance_map):
        """
        Build a nested hierarchy of groups and accounts.
        Returns list of top-level groups with children.
        """
        # Build group tree structure
        group_map = {g.id: {
            'id': g.id,
            'name': g.name,
            'code_prefix': g.code_prefix_start or '',
            'parent_id': g.parent_id.id if g.parent_id else None,
            'children': [],
            'accounts': [],
            'total_debit': 0,
            'total_credit': 0,
            'total_balance': 0,
            'level': 0,
            'is_group': True,
        } for g in groups}

        # Build parent-child relationships for groups
        root_groups = []
        for group_id, group_data in group_map.items():
            parent_id = group_data['parent_id']
            if parent_id and parent_id in group_map:
                group_map[parent_id]['children'].append(group_data)
            else:
                root_groups.append(group_data)

        # Assign accounts to their groups
        ungrouped_accounts = []
        for account in accounts:
            account_data = {
                'id': account.id,
                'code': account.code,
                'name': account.name,
                'account_type': account.account_type,
                'debit': balance_map.get(account.id, {}).get('debit', 0),
                'credit': balance_map.get(account.id, {}).get('credit', 0),
                'balance': balance_map.get(account.id, {}).get('balance', 0),
                'is_group': False,
            }

            # Find the most specific group for this account based on code prefix
            assigned = False
            best_match = None
            best_match_len = 0

            for group in groups:
                prefix_start = group.code_prefix_start or ''
                prefix_end = group.code_prefix_end or prefix_start
                if prefix_start and account.code:
                    if account.code >= prefix_start and account.code <= prefix_end + 'z':
                        if len(prefix_start) > best_match_len:
                            best_match = group
                            best_match_len = len(prefix_start)

            if best_match and best_match.id in group_map:
                group_map[best_match.id]['accounts'].append(account_data)
                assigned = True

            if not assigned:
                ungrouped_accounts.append(account_data)

        # Calculate totals recursively
        def calculate_totals(node):
            total_debit = 0
            total_credit = 0
            total_balance = 0

            for account in node.get('accounts', []):
                total_debit += account['debit']
                total_credit += account['credit']
                total_balance += account['balance']

            for child in node.get('children', []):
                calculate_totals(child)
                total_debit += child['total_debit']
                total_credit += child['total_credit']
                total_balance += child['total_balance']

            node['total_debit'] = total_debit
            node['total_credit'] = total_credit
            node['total_balance'] = total_balance

        for group in root_groups:
            calculate_totals(group)

        # Assign levels for indentation
        def assign_levels(node, level=0):
            node['level'] = level
            for child in node.get('children', []):
                assign_levels(child, level + 1)

        for group in root_groups:
            assign_levels(group)

        # Sort groups by code prefix
        root_groups.sort(key=lambda x: x['code_prefix'])

        # Sort accounts within each group by code
        def sort_accounts(node):
            node['accounts'].sort(key=lambda x: x['code'])
            for child in node['children']:
                sort_accounts(child)
            node['children'].sort(key=lambda x: x['code_prefix'])

        for group in root_groups:
            sort_accounts(group)

        return {
            'groups': root_groups,
            'ungrouped': ungrouped_accounts,
        }

    def _flatten_hierarchy_for_template(self, hierarchy, report_type='pl'):
        """
        Flatten hierarchical data into a list suitable for template rendering.
        Each item has: type (group/account), indent_level, data
        """
        lines = []

        def process_node(node, indent=0):
            if node.get('is_group'):
                # Add group header line
                lines.append({
                    'type': 'group',
                    'indent': indent,
                    'code': node.get('code_prefix', ''),
                    'name': node['name'],
                    'debit': node['total_debit'],
                    'credit': node['total_credit'],
                    'balance': node['total_balance'],
                    'is_subtotal': False,
                })

                # Process child groups
                for child in node.get('children', []):
                    process_node(child, indent + 1)

                # Process accounts in this group
                for account in node.get('accounts', []):
                    lines.append({
                        'type': 'account',
                        'indent': indent + 1,
                        'code': account['code'],
                        'name': account['name'],
                        'account_type': account['account_type'],
                        'debit': account['debit'],
                        'credit': account['credit'],
                        'balance': account['balance'],
                        'is_subtotal': False,
                    })

                # Add subtotal line for this group (if it has accounts or children)
                if node.get('accounts') or node.get('children'):
                    lines.append({
                        'type': 'subtotal',
                        'indent': indent,
                        'code': '',
                        'name': f"Total {node['name']}",
                        'debit': node['total_debit'],
                        'credit': node['total_credit'],
                        'balance': node['total_balance'],
                        'is_subtotal': True,
                    })

        # Process by category for P&L
        if report_type == 'pl':
            income_groups = []
            expense_groups = []

            for group in hierarchy.get('groups', []):
                prefix = group.get('code_prefix', '')
                # Typically income accounts start with 4, expenses with 5-6
                if prefix.startswith('4'):
                    income_groups.append(group)
                elif prefix.startswith(('5', '6', '7')):
                    expense_groups.append(group)

            # Process income section
            income_lines = []
            income_total = 0
            for group in income_groups:
                process_node(group, 0)
                income_total += abs(group['total_balance'])
            income_lines = lines.copy()
            lines.clear()

            # Process expense section
            expense_lines = []
            expense_total = 0
            for group in expense_groups:
                process_node(group, 0)
                expense_total += abs(group['total_balance'])
            expense_lines = lines.copy()

            return {
                'income_hierarchy': income_lines,
                'expense_hierarchy': expense_lines,
                'income_total': income_total,
                'expense_total': expense_total,
                'net_profit': income_total - expense_total,
            }

        # Process for Balance Sheet
        elif report_type == 'bs':
            asset_groups = []
            liability_groups = []
            equity_groups = []

            for group in hierarchy.get('groups', []):
                prefix = group.get('code_prefix', '')
                # Typically: 1=assets, 2=liabilities, 3=equity
                if prefix.startswith('1'):
                    asset_groups.append(group)
                elif prefix.startswith('2'):
                    liability_groups.append(group)
                elif prefix.startswith('3'):
                    equity_groups.append(group)

            # Process each section
            asset_lines = []
            asset_total = 0
            for group in asset_groups:
                process_node(group, 0)
                asset_total += group['total_balance']
            asset_lines = lines.copy()
            lines.clear()

            liability_lines = []
            liability_total = 0
            for group in liability_groups:
                process_node(group, 0)
                liability_total += abs(group['total_balance'])
            liability_lines = lines.copy()
            lines.clear()

            equity_lines = []
            equity_total = 0
            for group in equity_groups:
                process_node(group, 0)
                equity_total += abs(group['total_balance'])
            equity_lines = lines.copy()

            return {
                'asset_hierarchy': asset_lines,
                'liability_hierarchy': liability_lines,
                'equity_hierarchy': equity_lines,
                'asset_total': asset_total,
                'liability_total': liability_total,
                'equity_total': equity_total,
            }

        return {'lines': lines}

    # ============================================
    # CASH FLOW DATA
    # ============================================

    def _get_cash_flow_data(self):
        """Get Cash Flow Statement data."""
        self.ensure_one()

        MoveLine = self.env['account.move.line']
        domain = self._build_domain()

        # Get cash account movements
        data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id', 'journal_id'],
            aggregates=['debit:sum', 'credit:sum']
        )

        # Categorize cash flows
        operating = []
        investing = []
        financing = []

        for item in data:
            account = item[0]
            journal = item[1]
            if not account or not journal:
                continue

            inflow = item[2] or 0  # debit to cash = inflow
            outflow = item[3] or 0  # credit from cash = outflow
            net = inflow - outflow

            line = {
                'account_code': account.code,
                'account_name': account.name,
                'journal_name': journal.name,
                'inflow': inflow,
                'outflow': outflow,
                'net': net,
            }

            # Simple categorization based on journal type
            if journal.type in ('sale', 'purchase', 'general'):
                operating.append(line)
            elif journal.type == 'bank':
                financing.append(line)
            else:
                investing.append(line)

        # Calculate totals
        total_operating = sum(l['net'] for l in operating)
        total_investing = sum(l['net'] for l in investing)
        total_financing = sum(l['net'] for l in financing)
        net_change = total_operating + total_investing + total_financing

        return {
            'report_type': 'cf',
            'report_title': 'Cash Flow Statement',
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'filters': self._get_filter_summary_dict(),
            'sections': {
                'operating': {'lines': operating, 'total': total_operating},
                'investing': {'lines': investing, 'total': total_investing},
                'financing': {'lines': financing, 'total': total_financing},
            },
            'summary': {
                'total_operating': total_operating,
                'total_investing': total_investing,
                'total_financing': total_financing,
                'net_change': net_change,
            },
        }

    # ============================================
    # AGED PARTNER BALANCE DATA
    # ============================================

    def _get_aged_partner_data(self):
        """Get Aged Partner Balance data."""
        self.ensure_one()

        MoveLine = self.env['account.move.line']
        today = self.date_to
        period = self.period_length

        # Build domain for open items
        domain = self._build_domain()
        domain.append(('reconciled', '=', False))

        # Get unreconciled items
        lines = MoveLine.search(domain)

        # Apply matrix filtering
        if self.matrix_filter_mode == 'exact' and self.branch_ids and self.business_unit_ids:
            exact_combinations = self._get_exact_matrix_combinations()
            lines = lines.filtered(
                lambda l: (l.ops_branch_id.id, l.ops_business_unit_id.id) in exact_combinations
            )

        # Age the balances
        aged_data = {}
        for line in lines:
            partner = line.partner_id
            if not partner:
                partner_key = 0
                partner_name = 'Unknown'
            else:
                partner_key = partner.id
                partner_name = partner.name

            if partner_key not in aged_data:
                aged_data[partner_key] = {
                    'partner_id': partner_key,
                    'partner_name': partner_name,
                    'current': 0,
                    'period_1': 0,  # 1-30
                    'period_2': 0,  # 31-60
                    'period_3': 0,  # 61-90
                    'period_4': 0,  # 91-120
                    'older': 0,
                    'total': 0,
                }

            # Calculate age
            due_date = line.date_maturity or line.date
            if due_date:
                age_days = (today - due_date).days
            else:
                age_days = 0

            amount = line.amount_residual if hasattr(line, 'amount_residual') else line.balance

            # Bucket the amount
            if age_days <= 0:
                aged_data[partner_key]['current'] += amount
            elif age_days <= period:
                aged_data[partner_key]['period_1'] += amount
            elif age_days <= period * 2:
                aged_data[partner_key]['period_2'] += amount
            elif age_days <= period * 3:
                aged_data[partner_key]['period_3'] += amount
            elif age_days <= period * 4:
                aged_data[partner_key]['period_4'] += amount
            else:
                aged_data[partner_key]['older'] += amount

            aged_data[partner_key]['total'] += amount

        # Convert to list and sort
        aged_list = list(aged_data.values())
        aged_list.sort(key=lambda x: x['total'], reverse=True)

        # Calculate totals
        totals = {
            'current': sum(p['current'] for p in aged_list),
            'period_1': sum(p['period_1'] for p in aged_list),
            'period_2': sum(p['period_2'] for p in aged_list),
            'period_3': sum(p['period_3'] for p in aged_list),
            'period_4': sum(p['period_4'] for p in aged_list),
            'older': sum(p['older'] for p in aged_list),
            'total': sum(p['total'] for p in aged_list),
        }

        return {
            'report_type': 'aged',
            'report_title': f"Aged {'Receivables' if self.aging_type == 'receivable' else 'Payables'}",
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'as_of_date': str(self.date_to),
            'period_length': period,
            'aging_type': self.aging_type,
            'filters': self._get_filter_summary_dict(),
            'period_labels': {
                'current': 'Current',
                'period_1': f'1-{period}',
                'period_2': f'{period+1}-{period*2}',
                'period_3': f'{period*2+1}-{period*3}',
                'period_4': f'{period*3+1}-{period*4}',
                'older': f'>{period*4}',
            },
            'data': aged_list,
            'totals': totals,
        }

    # ============================================
    # PARTNER LEDGER DATA
    # ============================================

    def _get_partner_ledger_data(self):
        """Get Partner Ledger data."""
        self.ensure_one()

        MoveLine = self.env['account.move.line']
        domain = self._build_domain()

        # Group by partner
        order_by = 'partner_id, date, id'
        lines = MoveLine.search(domain, order=order_by)

        # Apply matrix filtering
        if self.matrix_filter_mode == 'exact' and self.branch_ids and self.business_unit_ids:
            exact_combinations = self._get_exact_matrix_combinations()
            lines = lines.filtered(
                lambda l: (l.ops_branch_id.id, l.ops_business_unit_id.id) in exact_combinations
            )

        # Group by partner
        partner_data = {}
        for line in lines:
            partner = line.partner_id
            partner_key = partner.id if partner else 0
            partner_name = partner.name if partner else 'No Partner'

            if partner_key not in partner_data:
                partner_data[partner_key] = {
                    'partner_id': partner_key,
                    'partner_name': partner_name,
                    'lines': [],
                    'total_debit': 0,
                    'total_credit': 0,
                    'balance': 0,
                }

            partner_data[partner_key]['lines'].append({
                'date': str(line.date),
                'move_name': line.move_id.name,
                'account_code': line.account_id.code,
                'ref': line.ref or '',
                'name': line.name,
                'debit': line.debit,
                'credit': line.credit,
                'balance': line.balance,
            })
            partner_data[partner_key]['total_debit'] += line.debit
            partner_data[partner_key]['total_credit'] += line.credit
            partner_data[partner_key]['balance'] += line.balance

        # Convert to list
        partner_list = list(partner_data.values())
        partner_list.sort(key=lambda x: x['partner_name'])

        return {
            'report_type': 'partner',
            'report_title': 'Partner Ledger',
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'filters': self._get_filter_summary_dict(),
            'data': partner_list,
            'totals': {
                'total_debit': sum(p['total_debit'] for p in partner_list),
                'total_credit': sum(p['total_credit'] for p in partner_list),
                'balance': sum(p['balance'] for p in partner_list),
                'partner_count': len(partner_list),
            },
        }

    # ============================================
    # STATEMENT OF ACCOUNT DATA
    # ============================================

    def _get_statement_of_account_data(self):
        """Get Statement of Account data for selected partners."""
        self.ensure_one()

        if not self.partner_ids:
            raise UserError(_("Please select at least one partner for Statement of Account."))

        MoveLine = self.env['account.move.line']

        # Get opening balance (before date_from)
        opening_domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
            ('partner_id', 'in', self.partner_ids.ids),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
        ]
        opening_domain += self._build_matrix_domain()

        opening_data = MoveLine._read_group(
            domain=opening_domain,
            groupby=['partner_id'],
            aggregates=['balance:sum']
        )
        opening_map = {item[0].id: item[1] or 0 for item in opening_data if item[0]}

        # Get period transactions
        domain = self._build_domain()
        lines = MoveLine.search(domain, order='partner_id, date, id')

        # Apply matrix filtering
        if self.matrix_filter_mode == 'exact' and self.branch_ids and self.business_unit_ids:
            exact_combinations = self._get_exact_matrix_combinations()
            lines = lines.filtered(
                lambda l: (l.ops_branch_id.id, l.ops_business_unit_id.id) in exact_combinations
            )

        # Build SoA per partner
        statements = []
        for partner in self.partner_ids:
            partner_lines = lines.filtered(lambda l: l.partner_id.id == partner.id)

            opening_balance = opening_map.get(partner.id, 0)
            running_balance = opening_balance

            soa_lines = []
            for line in partner_lines:
                running_balance += line.balance
                soa_lines.append({
                    'date': str(line.date),
                    'move_name': line.move_id.name,
                    'ref': line.ref or '',
                    'name': line.name,
                    'debit': line.debit,
                    'credit': line.credit,
                    'balance': running_balance,
                })

            closing_balance = running_balance

            statements.append({
                'partner_id': partner.id,
                'partner_name': partner.name,
                'partner_ref': partner.ref or '',
                'opening_balance': opening_balance,
                'lines': soa_lines,
                'closing_balance': closing_balance,
                'total_debit': sum(l.debit for l in partner_lines),
                'total_credit': sum(l.credit for l in partner_lines),
            })

        return {
            'report_type': 'soa',
            'report_title': 'Statement of Account',
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'filters': self._get_filter_summary_dict(),
            'statements': statements,
        }

    # ============================================
    # HELPER METHODS
    # ============================================

    def _get_initial_balances(self):
        """Get initial balances for accounts before the period."""
        self.ensure_one()

        MoveLine = self.env['account.move.line']

        domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
        ]

        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        matrix_domain = self._build_matrix_domain()
        if matrix_domain:
            domain += matrix_domain

        groupby_fields = ['account_id']
        if self.consolidate_by_branch and self.branch_ids:
            groupby_fields.append('ops_branch_id')
        if self.consolidate_by_bu and self.business_unit_ids:
            groupby_fields.append('ops_business_unit_id')
        if self.consolidate_by_partner and self.partner_ids:
            groupby_fields.append('partner_id')

        initial_data = MoveLine._read_group(
            domain=domain,
            groupby=groupby_fields,
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )

        balances = {}
        for item in initial_data:
            # Build key from groupby fields
            key_parts = []
            for i, field in enumerate(groupby_fields):
                val = item[i]
                if hasattr(val, 'id'):
                    key_parts.append(str(val.id))
                else:
                    key_parts.append(str(val) if val else '0')
            # Use string key for JSON serialization compatibility
            key = '_'.join(key_parts)

            # Get aggregates (after groupby fields)
            offset = len(groupby_fields)
            balances[key] = {
                'debit': item[offset] or 0,
                'credit': item[offset + 1] or 0,
                'balance': item[offset + 2] or 0,
            }

        return balances

    def _process_summary_data(self, lines):
        """Process lines into summary format with grouping."""
        self.ensure_one()

        groupby_fields = ['account_id']
        if self.consolidate_by_branch:
            groupby_fields.append('ops_branch_id')
        if self.consolidate_by_bu:
            groupby_fields.append('ops_business_unit_id')
        if self.consolidate_by_partner:
            groupby_fields.append('partner_id')

        grouped_data = {}
        for line in lines:
            key_parts = [str(line.account_id.id)]
            if self.consolidate_by_branch:
                key_parts.append(str(line.ops_branch_id.id) if line.ops_branch_id else '0')
            if self.consolidate_by_bu:
                key_parts.append(str(line.ops_business_unit_id.id) if line.ops_business_unit_id else '0')
            if self.consolidate_by_partner:
                key_parts.append(str(line.partner_id.id) if line.partner_id else '0')

            # Use string key for JSON serialization compatibility
            key = '_'.join(key_parts)

            if key not in grouped_data:
                grouped_data[key] = {
                    'account_id': line.account_id.id,
                    'account_code': line.account_id.code,
                    'account_name': line.account_id.name,
                    'debit': 0,
                    'credit': 0,
                    'balance': 0,
                    'count': 0,
                }

                if self.consolidate_by_branch:
                    grouped_data[key]['branch_id'] = line.ops_branch_id.id if line.ops_branch_id else False
                    grouped_data[key]['branch_name'] = line.ops_branch_id.name if line.ops_branch_id else ''
                if self.consolidate_by_bu:
                    grouped_data[key]['bu_id'] = line.ops_business_unit_id.id if line.ops_business_unit_id else False
                    grouped_data[key]['bu_name'] = line.ops_business_unit_id.name if line.ops_business_unit_id else ''
                if self.consolidate_by_partner:
                    grouped_data[key]['partner_id'] = line.partner_id.id if line.partner_id else False
                    grouped_data[key]['partner_name'] = line.partner_id.name if line.partner_id else ''

            grouped_data[key]['debit'] += line.debit
            grouped_data[key]['credit'] += line.credit
            grouped_data[key]['balance'] += line.balance
            grouped_data[key]['count'] += 1

        return list(grouped_data.values())

    def _process_detailed_data(self, lines):
        """Process lines into detailed format."""
        self.ensure_one()

        detailed_data = []
        running_balance = 0

        for line in lines:
            running_balance += line.balance

            detailed_data.append({
                'id': line.id,
                'date': str(line.date),
                'move_id': line.move_id.id,
                'move_name': line.move_id.name,
                'journal_code': line.journal_id.code,
                'account_code': line.account_id.code,
                'account_name': line.account_id.name,
                'partner_name': line.partner_id.name if line.partner_id else '',
                'branch_code': line.ops_branch_id.code if line.ops_branch_id else '',
                'branch_name': line.ops_branch_id.name if line.ops_branch_id else '',
                'bu_code': line.ops_business_unit_id.code if line.ops_business_unit_id else '',
                'bu_name': line.ops_business_unit_id.name if line.ops_business_unit_id else '',
                'name': line.name,
                'ref': line.ref or '',
                'debit': line.debit,
                'credit': line.credit,
                'balance': line.balance,
                'running_balance': running_balance,
                'reconciled': line.reconciled,
                'currency_id': line.currency_id.name if line.currency_id else '',
                'amount_currency': line.amount_currency,
            })

        return detailed_data

    def _get_sort_order(self):
        """Get sort order based on wizard selection."""
        sort_mapping = {
            'date': 'date, move_id, id',
            'account': 'account_id, date, id',
            'partner': 'partner_id, date, id',
            'branch': 'ops_branch_id, date, id',
            'bu': 'ops_business_unit_id, date, id',
        }
        return sort_mapping.get(self.sort_by, 'date, move_id, id')

    def _get_filter_summary_dict(self):
        """Get filter summary as dictionary for report."""
        return {
            'report_type': self.report_type,
            'report_title': self.report_title,
            'branch_count': len(self.branch_ids),
            'branch_names': self.branch_ids.mapped('name') if self.branch_ids else [],
            'bu_count': len(self.business_unit_ids),
            'bu_names': self.business_unit_ids.mapped('name') if self.business_unit_ids else [],
            'account_count': len(self.account_ids),
            'journal_count': len(self.journal_ids),
            'partner_count': len(self.partner_ids),
            'date_range': f"{self.date_from} to {self.date_to}",
            'target_move': self.target_move,
            'reconciled': self.reconciled,
            'matrix_filter_mode': self.matrix_filter_mode,
            'consolidate_by_branch': self.consolidate_by_branch,
            'consolidate_by_bu': self.consolidate_by_bu,
            'consolidate_by_partner': self.consolidate_by_partner,
            'group_by_date': self.group_by_date,
            'display_account': self.display_account,
            'include_initial_balance': self.include_initial_balance,
        }

    def _build_report_dict(self, lines, processed_data, initial_balances):
        """Build standard report dictionary."""
        return {
            'report_type': self.report_type,
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'filters': self._get_filter_summary_dict(),
            'initial_balances': initial_balances,
            'data': processed_data,
            'report_format': self.report_format,
            'totals': {
                'total_debit': sum(line.debit for line in lines),
                'total_credit': sum(line.credit for line in lines),
                'total_balance': sum(line.balance for line in lines),
                'line_count': len(lines),
            },
        }

    def _return_report_action(self, data):
        """Return appropriate report action based on report type."""
        # Corporate report action XML IDs (Phase 4 redesigned templates)
        report_xml_ids = {
            'gl': 'ops_matrix_accounting.action_report_general_ledger_corporate',
            'tb': 'ops_matrix_accounting.action_report_trial_balance_corporate',
            'pl': 'ops_matrix_accounting.action_report_profit_loss_corporate',
            'bs': 'ops_matrix_accounting.action_report_balance_sheet_corporate',
            'cf': 'ops_matrix_accounting.action_report_cash_flow_corporate',
            'aged': 'ops_matrix_accounting.action_report_aged_partner_corporate',
            'partner': 'ops_matrix_accounting.action_report_general_ledger_corporate',  # Partner ledger uses GL template
            'soa': 'ops_matrix_accounting.action_report_general_ledger_corporate',  # Statement of Account uses GL template
        }

        xml_id = report_xml_ids.get(self.report_type, report_xml_ids['gl'])
        report = self.env.ref(xml_id)
        return report.report_action(self, data=data)

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_export_to_excel(self):
        """Export report to Excel with corporate formatting."""
        self.ensure_one()

        # Security check
        self._check_intelligence_access(self._get_engine_name())

        # Get report data
        report_data = self._get_report_data()

        # Create Excel workbook
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Get corporate formats
        formats = get_corporate_excel_formats(workbook, self.company_id)

        # Create worksheet
        report_titles = {
            'gl': 'General Ledger',
            'tb': 'Trial Balance',
            'pl': 'Profit & Loss',
            'bs': 'Balance Sheet',
            'cf': 'Cash Flow',
            'aged': 'Aged Partner Balance',
            'partner_ledger': 'Partner Ledger',
            'soa': 'Statement of Account',
        }
        sheet_name = report_titles.get(self.report_type, 'Report')[:31]
        worksheet = workbook.add_worksheet(sheet_name)

        # Set column widths
        worksheet.set_column('A:A', 12)  # Date
        worksheet.set_column('B:B', 15)  # Journal/Code
        worksheet.set_column('C:C', 20)  # Reference
        worksheet.set_column('D:D', 25)  # Partner/Account
        worksheet.set_column('E:E', 35)  # Description
        worksheet.set_column('F:H', 15)  # Numbers

        row = 0

        # Company header
        worksheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Report title
        worksheet.write(row, 0, sheet_name, formats['report_title'])
        row += 1

        # Period
        period_text = f"Period: {self.date_from} to {self.date_to}"
        worksheet.write(row, 0, period_text, formats['metadata'])
        row += 1

        # Generated info
        generated_text = f"Generated: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.env.user.name}"
        worksheet.write(row, 0, generated_text, formats['metadata'])
        row += 2

        # Filter bar
        filter_parts = []
        if self.branch_ids:
            filter_parts.append(f"Branches: {', '.join(self.branch_ids.mapped('name'))}")
        if self.business_unit_ids:
            filter_parts.append(f"BUs: {', '.join(self.business_unit_ids.mapped('name'))}")
        filter_text = ' | '.join(filter_parts) if filter_parts else 'All Data'
        worksheet.merge_range(row, 0, row, 7, f"Scope: {filter_text} | Currency: {self.company_id.currency_id.name}", formats['filter_bar'])
        row += 2

        # Table headers
        headers = ['Date', 'Journal', 'Reference', 'Partner', 'Description', 'Debit', 'Credit', 'Balance']
        for col, header in enumerate(headers):
            fmt = formats['table_header_num'] if col >= 5 else formats['table_header']
            worksheet.write(row, col, header, fmt)
        row += 1

        # Freeze panes
        worksheet.freeze_panes(row, 0)

        # Data rows
        lines = report_data.get('lines', []) or report_data.get('accounts', []) or []

        # Handle different data structures based on report format
        if not lines:
            data = report_data.get('data', {})
            if isinstance(data, dict):
                if 'detailed' in data:
                    lines = data['detailed']
                elif 'summary' in data:
                    lines = data['summary']
            elif isinstance(data, list):
                lines = data

        total_debit = 0
        total_credit = 0

        for idx, line in enumerate(lines):
            alt = idx % 2 == 1

            # Get values based on data structure
            date_val = line.get('date', '')
            journal = line.get('journal', line.get('journal_code', line.get('code', '')))
            ref = line.get('reference', line.get('ref', line.get('move_name', '')))
            partner = line.get('partner', line.get('partner_name', ''))
            desc = line.get('description', line.get('name', line.get('label', line.get('account_name', ''))))
            debit = float(line.get('debit', 0) or 0)
            credit = float(line.get('credit', 0) or 0)
            balance = float(line.get('balance', debit - credit) or 0)

            total_debit += debit
            total_credit += credit

            # Write text columns
            worksheet.write(row, 0, str(date_val), formats['text_alt'] if alt else formats['text'])
            worksheet.write(row, 1, journal, formats['text_alt'] if alt else formats['text'])
            worksheet.write(row, 2, ref, formats['text_alt'] if alt else formats['text'])
            worksheet.write(row, 3, partner, formats['text_alt'] if alt else formats['text'])
            worksheet.write(row, 4, desc, formats['text_alt'] if alt else formats['text'])

            # Write number columns with value-based formatting
            for col, value in [(5, debit), (6, credit), (7, balance)]:
                if abs(value) < 0.01:
                    fmt = formats['number_zero_alt'] if alt else formats['number_zero']
                elif value < 0:
                    fmt = formats['number_negative_alt'] if alt else formats['number_negative']
                else:
                    fmt = formats['number_alt'] if alt else formats['number']
                worksheet.write(row, col, abs(value) if col < 7 else value, fmt)

            row += 1

        # Total row
        worksheet.write(row, 0, 'GRAND TOTAL', formats['total_label'])
        for col in range(1, 5):
            worksheet.write(row, col, '', formats['total_label'])
        worksheet.write(row, 5, total_debit, formats['total_number'])
        worksheet.write(row, 6, total_credit, formats['total_number'])
        worksheet.write(row, 7, total_debit - total_credit, formats['total_number'])

        # Print settings
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_paper(9)  # A4

        workbook.close()
        output.seek(0)

        # Create attachment
        filename = f"{sheet_name.replace(' ', '_')}_{fields.Date.today()}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(output.read()),
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_view_transactions(self):
        """Open filtered journal entries in list view."""
        self.ensure_one()

        domain = self._build_domain()
        lines = self.env['account.move.line'].search(domain)

        if self.matrix_filter_mode == 'exact' and self.branch_ids and self.business_unit_ids:
            exact_combinations = self._get_exact_matrix_combinations()
            lines = lines.filtered(
                lambda l: (l.ops_branch_id.id, l.ops_business_unit_id.id) in exact_combinations
            )

        move_ids = lines.mapped('move_id').ids

        return {
            'name': _('Journal Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', move_ids)],
            'context': {
                'search_default_group_by_date': 1 if self.group_by_date != 'none' else 0,
            },
        }

    def action_view_account_moves(self):
        """View moves for specific account (called from report)."""
        self.ensure_one()

        account_id = self.env.context.get('account_id')
        if not account_id:
            raise UserError(_("No account specified"))

        domain = self._build_domain()
        domain.append(('account_id', '=', account_id))

        return {
            'name': _('Account Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'list,form',
            'domain': domain,
        }

    # ============================================
    # ONCHANGE METHODS
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Adjust options based on report type."""
        if self.report_type == 'bs':
            # Balance Sheet uses as_of_date
            self.as_of_date = self.date_to
        if self.report_type == 'aged':
            # Default to unreconciled for aged reports
            self.reconciled = 'unreconciled'
        if self.report_type in ('pl', 'bs'):
            # Clear reconciliation filter for financial statements
            self.reconciled = 'all'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Reset filters when company changes."""
        if self.company_id:
            self.branch_ids = False
            self.business_unit_ids = False
            self.account_ids = False
            self.journal_ids = False
            self.partner_ids = False

    @api.onchange('branch_ids')
    def _onchange_branch_ids(self):
        """Update BU domain when branches change."""
        if self.branch_ids:
            return {
                'domain': {
                    'business_unit_ids': [('branch_ids', 'in', self.branch_ids.ids)]
                }
            }
        return {}

    @api.onchange('business_unit_ids')
    def _onchange_business_unit_ids(self):
        """Update branch domain when BUs change."""
        if self.business_unit_ids:
            branch_ids = self.business_unit_ids.mapped('branch_ids').ids
            return {
                'domain': {
                    'branch_ids': [('id', 'in', branch_ids)]
                }
            }
        return {}

    @api.onchange('report_format')
    def _onchange_report_format(self):
        """Adjust options based on report format."""
        if self.report_format == 'summary':
            if not any([self.consolidate_by_branch, self.consolidate_by_bu, self.consolidate_by_partner]):
                self.consolidate_by_branch = bool(self.branch_ids)
                self.consolidate_by_bu = bool(self.business_unit_ids)

    @api.onchange('aging_type')
    def _onchange_aging_type(self):
        """Update partner type filter based on aging type."""
        if self.aging_type == 'receivable':
            self.partner_type = 'customer'
        elif self.aging_type == 'payable':
            self.partner_type = 'supplier'
        else:
            self.partner_type = 'all'

    # ============================================
    # SMART TEMPLATE METHODS
    # ============================================
    # _onchange_report_template_id, _get_template_config, action_save_template
    # are inherited from ops.base.report.wizard
