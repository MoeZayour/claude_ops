# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Enhanced General Ledger Wizard
======================================================

Comprehensive General Ledger wizard with matrix dimension filtering
(Branch and Business Unit) and advanced consolidation options.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils, float_round
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsGeneralLedgerWizardEnhanced(models.TransientModel):
    """Enhanced General Ledger Report Wizard with Matrix Dimensions"""
    _name = 'ops.general.ledger.wizard.enhanced'
    _description = 'General Ledger Report Wizard with Matrix Dimensions'
    
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
    
    # ============================================
    # 2. COMPANY & JOURNALS
    # ============================================
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journals',
        help='Leave empty for all journals'
    )
    
    # ============================================
    # 3. MATRIX DIMENSION FILTERS
    # ============================================
    
    # Branch Filter
    branch_ids = fields.Many2many(
        'ops.branch',
        'gl_wizard_branch_rel',
        'wizard_id',
        'branch_id',
        string='Branches',
        help='Filter by specific branches. Leave empty for all branches.'
    )
    
    # Business Unit Filter
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'gl_wizard_bu_rel',
        'wizard_id',
        'bu_id',
        string='Business Units',
        help='Filter by specific business units. Leave empty for all BUs.'
    )
    
    # Matrix Combination Mode
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
    
    # Partner Filter
    partner_ids = fields.Many2many(
        'res.partner',
        'gl_wizard_partner_rel',
        'wizard_id',
        'partner_id',
        string='Partners',
        help='Filter by specific partners'
    )
    
    # ============================================
    # 6. CONSOLIDATION & GROUPING OPTIONS
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
    # 7. OUTPUT OPTIONS
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
    # 8. COMPUTED FIELDS
    # ============================================
    filter_summary = fields.Char(
        compute='_compute_filter_summary',
        string='Filter Summary',
        help='Summary of active filters'
    )
    
    record_count = fields.Integer(
        compute='_compute_record_count',
        string='Estimated Records',
        help='Estimated number of records matching filters'
    )
    
    # ============================================
    # COMPUTED METHODS
    # ============================================
    
    @api.depends('branch_ids', 'business_unit_ids', 'account_ids', 'journal_ids', 
                 'date_from', 'date_to', 'target_move', 'reconciled', 'partner_ids')
    def _compute_filter_summary(self):
        """Compute human-readable summary of active filters."""
        for wizard in self:
            parts = []
            
            # Date range
            if wizard.date_from and wizard.date_to:
                parts.append(f"Period: {wizard.date_from} to {wizard.date_to}")
            
            # Matrix dimensions
            if wizard.branch_ids:
                if len(wizard.branch_ids) <= 3:
                    branch_names = wizard.branch_ids.mapped('code')
                    parts.append(f"Branches: {', '.join(branch_names)}")
                else:
                    parts.append(f"Branches: {len(wizard.branch_ids)} selected")
            
            if wizard.business_unit_ids:
                if len(wizard.business_unit_ids) <= 3:
                    bu_names = wizard.business_unit_ids.mapped('code')
                    parts.append(f"BUs: {', '.join(bu_names)}")
                else:
                    parts.append(f"BUs: {len(wizard.business_unit_ids)} selected")
            
            # Accounts and journals
            if wizard.account_ids:
                parts.append(f"Accounts: {len(wizard.account_ids)} selected")
            
            if wizard.journal_ids:
                parts.append(f"Journals: {len(wizard.journal_ids)} selected")
            
            # Partners
            if wizard.partner_ids:
                parts.append(f"Partners: {len(wizard.partner_ids)} selected")
            
            # Transaction filters
            if wizard.target_move == 'posted':
                parts.append("Posted only")
            
            if wizard.reconciled == 'unreconciled':
                parts.append("Unreconciled")
            elif wizard.reconciled == 'reconciled':
                parts.append("Reconciled")
            
            wizard.filter_summary = " | ".join(parts) if parts else "No filters applied"
    
    @api.depends('date_from', 'date_to', 'company_id', 'branch_ids', 'business_unit_ids', 
                 'account_ids', 'target_move', 'journal_ids', 'partner_ids')
    def _compute_record_count(self):
        """Estimate number of records matching current filters."""
        for wizard in self:
            if not wizard.date_from or not wizard.date_to:
                wizard.record_count = 0
                continue
            
            try:
                # Build domain
                domain = wizard._build_domain()
                
                # Count records
                count = self.env['account.move.line'].search_count(domain)
                wizard.record_count = count
            except Exception as e:
                _logger.error(f"Error counting records: {e}")
                wizard.record_count = 0
    
    # ============================================
    # DOMAIN BUILDING METHODS
    # ============================================
    
    def _build_domain(self):
        """Build complete domain for account move line query."""
        self.ensure_one()
        
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        
        # Target moves filter
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        
        # Reconciliation filter
        if self.reconciled == 'unreconciled':
            domain.append(('reconciled', '=', False))
        elif self.reconciled == 'reconciled':
            domain.append(('reconciled', '=', True))
        
        # Account filters
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))
        
        if self.account_type_ids:
            # Note: account.account uses 'company_ids' (Many2many) not 'company_id'
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
        
        # Matrix dimension filters
        matrix_domain = self._build_matrix_domain()
        if matrix_domain:
            domain += matrix_domain
        
        return domain
    
    def _build_matrix_domain(self):
        """Build matrix dimension domain based on filter mode."""
        matrix_domain = []
        
        # If no matrix filters, return empty
        if not self.branch_ids and not self.business_unit_ids:
            return matrix_domain
        
        # Build branch domain
        branch_domain = []
        if self.branch_ids:
            branch_domain = [('ops_branch_id', 'in', self.branch_ids.ids)]
        
        # Build BU domain
        bu_domain = []
        if self.business_unit_ids:
            bu_domain = [('ops_business_unit_id', 'in', self.business_unit_ids.ids)]
        
        # Apply filter mode
        if self.matrix_filter_mode == 'any':
            # OR condition: Branch OR BU
            if branch_domain and bu_domain:
                matrix_domain = ['|'] + branch_domain + bu_domain
            elif branch_domain:
                matrix_domain = branch_domain
            elif bu_domain:
                matrix_domain = bu_domain
        
        elif self.matrix_filter_mode == 'both':
            # AND condition: Branch AND BU
            if branch_domain and bu_domain:
                matrix_domain = branch_domain + bu_domain
            else:
                # If only one dimension selected in "both" mode, treat as "any"
                matrix_domain = branch_domain or bu_domain
        
        elif self.matrix_filter_mode == 'exact':
            # Exact combinations: apply both filters, post-filter in Python
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
                    # Check if BU actually operates in this branch
                    if branch in bu.branch_ids:
                        combinations.add((branch.id, bu.id))
        return combinations
    
    # ============================================
    # VALIDATION METHODS
    # ============================================
    
    def _validate_filters(self):
        """Validate wizard filters before generating report."""
        self.ensure_one()
        
        if self.date_from > self.date_to:
            raise ValidationError(_("From date cannot be after To date."))
        
        # Check matrix filter logic
        if self.matrix_filter_mode == 'exact' and (not self.branch_ids or not self.business_unit_ids):
            raise ValidationError(_(
                "Exact combination mode requires both Branch and Business Unit filters."
            ))
        
        # Check for very large date ranges
        date_diff = (self.date_to - self.date_from).days
        if date_diff > 365 and self.report_format == 'detailed' and not self.account_ids:
            return {
                'warning': {
                    'title': _('Large Date Range'),
                    'message': _(
                        'You are generating a detailed report for more than 1 year without account filter. '
                        'This may take a long time. Consider using summary format or filtering by accounts.'
                    ),
                }
            }
        
        # Check for large result sets
        if self.record_count > 50000 and self.report_format == 'detailed':
            return {
                'warning': {
                    'title': _('Large Result Set'),
                    'message': _(
                        'This filter will return approximately %(count)d records. '
                        'Consider using summary format or applying additional filters.'
                    ) % {'count': self.record_count},
                }
            }
        
        return True
    
    # ============================================
    # REPORT GENERATION METHODS
    # ============================================
    
    def action_generate_report(self):
        """Generate the general ledger report with matrix filters."""
        self.ensure_one()
        
        # Validate filters
        validation_result = self._validate_filters()
        if isinstance(validation_result, dict) and 'warning' in validation_result:
            # Return warning but allow user to proceed
            pass
        
        # Generate report data
        report_data = self._prepare_report_data()
        
        # Return report action
        return self._return_report_action(report_data)
    
    def _prepare_report_data(self):
        """Prepare complete report data."""
        self.ensure_one()
        
        domain = self._build_domain()
        MoveLine = self.env['account.move.line']
        
        # Get initial balances if requested
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
        
        # Process lines based on report format
        if self.report_format == 'summary':
            processed_data = self._process_summary_data(lines)
        elif self.report_format == 'detailed':
            processed_data = self._process_detailed_data(lines)
        else:  # both
            processed_data = {
                'summary': self._process_summary_data(lines),
                'detailed': self._process_detailed_data(lines),
            }
        
        # Prepare final report data
        report_data = {
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
        
        return report_data
    
    def _get_initial_balances(self):
        """Get initial balances for accounts before the period."""
        self.ensure_one()
        
        MoveLine = self.env['account.move.line']
        
        # Build domain for transactions before period
        domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
        ]
        
        # Apply same filters as main report
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        
        # Matrix filters
        matrix_domain = self._build_matrix_domain()
        if matrix_domain:
            domain += matrix_domain
        
        # Group by account (and other dimensions if consolidating)
        groupby_fields = ['account_id']
        if self.consolidate_by_branch and self.branch_ids:
            groupby_fields.append('ops_branch_id')
        if self.consolidate_by_bu and self.business_unit_ids:
            groupby_fields.append('ops_business_unit_id')
        if self.consolidate_by_partner and self.partner_ids:
            groupby_fields.append('partner_id')
        
        # Aggregate initial balances
        _read_group(
            domain=domain,
            groupby=groupby_fields,
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        
        # Process into dictionary
        balances = {}
        for item in initial_data:
            key = tuple(item.get(field, False) for field in groupby_fields)
            balances[key] = {
                'debit': item.get('debit', 0),
                'credit': item.get('credit', 0),
                'balance': item.get('balance', 0),
            }
        
        return balances
    
    def _process_summary_data(self, lines):
        """Process lines into summary format with grouping."""
        self.ensure_one()
        
        # Determine grouping
        groupby_fields = ['account_id']
        if self.consolidate_by_branch:
            groupby_fields.append('ops_branch_id')
        if self.consolidate_by_bu:
            groupby_fields.append('ops_business_unit_id')
        if self.consolidate_by_partner:
            groupby_fields.append('partner_id')
        
        # Group data
        grouped_data = {}
        for line in lines:
            # Create group key
            key_parts = []
            key_parts.append(line.account_id.id)
            if self.consolidate_by_branch:
                key_parts.append(line.ops_branch_id.id if line.ops_branch_id else False)
            if self.consolidate_by_bu:
                key_parts.append(line.ops_business_unit_id.id if line.ops_business_unit_id else False)
            if self.consolidate_by_partner:
                key_parts.append(line.partner_id.id if line.partner_id else False)
            
            key = tuple(key_parts)
            
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
    
    def _return_report_action(self, data):
        """Return appropriate report action."""
        return {
            'type': 'ir.actions.report',
            'report_name': 'ops_matrix_accounting.report_general_ledger_matrix',
            'report_type': 'qweb-pdf',
            'data': data,
            'config': False,
        }
    
    # ============================================
    # ACTION METHODS
    # ============================================
    
    def action_export_to_excel(self):
        """Export report to Excel format."""
        self.ensure_one()
        
        # Prepare report data
        report_data = self._prepare_report_data()
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'ops_matrix_accounting.report_general_ledger_matrix_xlsx',
            'report_type': 'xlsx',
            'data': report_data,
            'config': False,
        }
    
    def action_view_transactions(self):
        """Open filtered journal entries in tree view."""
        self.ensure_one()
        
        domain = self._build_domain()
        
        # Get move IDs
        lines = self.env['account.move.line'].search(domain)
        
        # Apply exact matrix filtering if needed
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
            'view_mode': 'tree,form',
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
            'view_mode': 'tree,form',
            'domain': domain,
        }
    
    # ============================================
    # ONCHANGE METHODS
    # ============================================
    
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
            # Enable consolidation for summary
            if not any([self.consolidate_by_branch, self.consolidate_by_bu, self.consolidate_by_partner]):
                self.consolidate_by_branch = bool(self.branch_ids)
                self.consolidate_by_bu = bool(self.business_unit_ids)
