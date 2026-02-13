from odoo import models, api
import logging
import hashlib
from datetime import datetime

_logger = logging.getLogger(__name__)

# Account type to badge mapping (accounting convention colors via CSS classes)
ACCOUNT_TYPE_BADGES = {
    'asset_receivable': ('Asset', 'badge-asset'),
    'asset_cash': ('Asset', 'badge-asset'),
    'asset_current': ('Asset', 'badge-asset'),
    'asset_non_current': ('Asset', 'badge-asset'),
    'asset_prepayments': ('Asset', 'badge-asset'),
    'asset_fixed': ('Asset', 'badge-asset'),
    'liability_payable': ('Liability', 'badge-liability'),
    'liability_credit_card': ('Liability', 'badge-liability'),
    'liability_current': ('Liability', 'badge-liability'),
    'liability_non_current': ('Liability', 'badge-liability'),
    'equity': ('Equity', 'badge-equity'),
    'equity_unaffected': ('Equity', 'badge-equity'),
    'income': ('Income', 'badge-income'),
    'income_other': ('Income', 'badge-income'),
    'expense': ('Expense', 'badge-expense'),
    'expense_depreciation': ('Expense', 'badge-expense'),
    'expense_direct_cost': ('Expense', 'badge-expense'),
    'off_balance': ('Off-Balance', 'badge-asset'),
}


class OpsGeneralLedgerReportMinimal(models.AbstractModel):
    """
    General Ledger Report Parser for Minimal Template.
    Optimized for Odoo 19 with search_read() for better performance.

    This parser is used by both:
    - ops.general.ledger.wizard (original wizard)
    - ops.general.ledger.wizard.enhanced (Matrix Financial Intelligence)

    Data Flow:
    - Wizard calls _get_report_data() -> returns {data: [...], totals: {...}}
    - Wizard calls report.report_action(self, data=report_data)
    - Parser receives docids (wizard IDs) and data (pre-computed report data)
    - Parser transforms data to template format: {accounts: [...], grand_total: {...}}
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger_minimal'
    _description = 'General Ledger Report Parser (Minimal)'

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _format_date(self, date_val):
        """Format date to DD MMM YYYY for display."""
        if not date_val:
            return ''
        if isinstance(date_val, str):
            try:
                date_obj = datetime.strptime(date_val, '%Y-%m-%d')
                return date_obj.strftime('%d %b %Y')
            except (ValueError, TypeError):
                return date_val
        if hasattr(date_val, 'strftime'):
            return date_val.strftime('%d %b %Y')
        return str(date_val)

    def _clean_description(self, reference, description):
        """Remove duplicate reference prefix from description."""
        if not description:
            return reference or ''
        if not reference:
            return description
        # Remove reference prefix from description if present
        if description.startswith(reference):
            cleaned = description[len(reference):].lstrip(' -/:')
            return cleaned if cleaned else description
        return description

    def _generate_report_run_id(self):
        """Generate unique report run ID for audit trail."""
        now = datetime.now()
        run_hash = hashlib.md5(
            f"{now.isoformat()}{self.env.uid}".encode()
        ).hexdigest()[:4].upper()
        return f"GL-{now.strftime('%Y%m%d-%H%M%S')}-{run_hash}"

    def _compute_running_balances(self, accounts_data):
        """Compute per-account running balances including opening balance."""
        for account in accounts_data.values():
            running = account.get('initial_balance', 0)
            for line in account.get('lines', []):
                running += (line['debit'] - line['credit'])
                line['balance'] = running

    def _get_primary_color(self, company):
        """Get company report primary color with safe fallback."""
        try:
            color = company.ops_report_primary_color
            if color:
                return color
        except (AttributeError, Exception):
            pass
        return '#5B6BBB'

    def _get_report_colors(self, company):
        """Get all report color values from company settings."""
        primary = self._get_primary_color(company)
        try:
            text_on_primary = company.ops_report_text_on_primary or '#FFFFFF'
        except (AttributeError, Exception):
            text_on_primary = '#FFFFFF'
        try:
            body_text_color = company.ops_report_body_text_color or '#1a1a1a'
        except (AttributeError, Exception):
            body_text_color = '#1a1a1a'
        try:
            primary_light = company.get_report_primary_light()
        except (AttributeError, Exception):
            primary_light = '#edeef5'
        try:
            primary_dark = company.get_report_primary_dark()
        except (AttributeError, Exception):
            primary_dark = '#44508c'
        return {
            'primary_color': primary,
            'text_on_primary': text_on_primary,
            'body_text_color': body_text_color,
            'primary_light': primary_light,
            'primary_dark': primary_dark,
        }

    def _add_type_badges(self, accounts_data):
        """Add type label and badge CSS class to each account dict."""
        for acc in accounts_data.values():
            type_info = ACCOUNT_TYPE_BADGES.get(
                acc.get('account_type', ''), ('Other', 'badge-asset')
            )
            acc['type_label'] = type_info[0]
            acc['type_badge_class'] = type_info[1]

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Get report values for the General Ledger template.

        Supports both:
        - ops.general.ledger.wizard (original)
        - ops.general.ledger.wizard.enhanced (Matrix Financial Intelligence)

        Priority:
        1. Use pre-computed data from wizard if available
        2. Fall back to database query if no pre-computed data
        """
        if not data:
            data = {}

        # Get the wizard record(s) if docids provided
        wizard = None
        doc_model = 'ops.general.ledger.wizard'
        if docids:
            # Try enhanced wizard first
            try:
                wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
                if wizard.exists():
                    doc_model = 'ops.general.ledger.wizard.enhanced'
                    wizard = wizard[0] if len(wizard) > 1 else wizard
            except Exception:
                _logger.debug('Failed to browse enhanced GL wizard', exc_info=True)
            # Fall back to original wizard
            if not wizard or not wizard.exists():
                try:
                    wizard = self.env['ops.general.ledger.wizard'].browse(docids)
                    if wizard.exists():
                        doc_model = 'ops.general.ledger.wizard'
                        wizard = wizard[0] if len(wizard) > 1 else wizard
                except Exception:
                    _logger.debug('Failed to browse standard GL wizard', exc_info=True)
                    wizard = None

        # =====================================================================
        # PRIORITY 1: Use pre-computed data from wizard
        # =====================================================================
        if data and isinstance(data, dict) and data.get('data'):
            _logger.info("GL Report: Using pre-computed data from wizard")
            return self._transform_wizard_data(docids, doc_model, wizard, data)

        # =====================================================================
        # PRIORITY 2: Fall back to database query
        # =====================================================================
        _logger.info("GL Report: Querying database (no pre-computed data)")
        return self._query_and_build_data(docids, doc_model, wizard, data)

    # =========================================================================
    # DATA TRANSFORMATION (from wizard pre-computed data)
    # =========================================================================

    def _transform_wizard_data(self, docids, doc_model, wizard, data):
        """
        Transform wizard's pre-computed data to template format.

        Wizard returns: {data: [...], totals: {...}, date_from, date_to, ...}
        Template expects: {accounts: [...], grand_total: {...}, date_from, date_to, ...}
        """
        # Get dates from data or wizard
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if wizard:
            if not date_from:
                date_from = wizard.date_from
            if not date_to:
                date_to = wizard.date_to
            company = wizard.company_id or self.env.company
        else:
            company = self.env.company

        # Get the raw data lines from wizard
        raw_data = data.get('data', [])
        totals = data.get('totals', {})

        # Handle different data formats
        if isinstance(raw_data, dict):
            # Format: {detailed: [...], summary: [...]}
            lines = raw_data.get('detailed', raw_data.get('summary', []))
        else:
            lines = raw_data

        # Transform lines to accounts grouped structure
        accounts_data = {}
        for line in lines:
            account_code = line.get('account_code', '')
            account_name = line.get('account_name', '')

            if not account_code:
                continue

            if account_code not in accounts_data:
                accounts_data[account_code] = {
                    'account_code': account_code,
                    'account_name': account_name,
                    'account_type': line.get('account_type', ''),
                    'lines': [],
                    'total_debit': 0.0,
                    'total_credit': 0.0,
                    'total_balance': 0.0,
                    'initial_balance': 0.0,
                    'initial_debit': 0.0,
                    'initial_credit': 0.0,
                }

            debit = line.get('debit', 0) or 0
            credit = line.get('credit', 0) or 0

            # Clean reference/description overlap
            ref = line.get('ref', '')
            name = line.get('name', '')

            # Build line data for template
            line_data = {
                'account_code': account_code,
                'account_name': account_name,
                'move_date': self._format_date(line.get('date', '')),
                'journal': line.get('journal_code', ''),
                'partner': line.get('partner_name', ''),
                'label': self._clean_description(ref, name),
                'reference': ref,
                'debit': debit,
                'credit': credit,
                'balance': 0,  # Computed as running balance below
                'reconciled': line.get('reconciled', False),
            }
            accounts_data[account_code]['lines'].append(line_data)
            accounts_data[account_code]['total_debit'] += debit
            accounts_data[account_code]['total_credit'] += credit

        # Apply initial balances from wizard data
        initial_balances = data.get('initial_balances', {})
        if initial_balances:
            # Keys are account_id strings (or composite keys like "42_5_3")
            # Need to map account_id -> account_code
            account_ids = []
            for k in initial_balances.keys():
                try:
                    account_ids.append(int(k.split('_')[0]))
                except (ValueError, TypeError):
                    pass
            if account_ids:
                accounts = self.env['account.account'].browse(account_ids)
                id_to_code = {str(acc.id): acc.code for acc in accounts}
                for key, bal_data in initial_balances.items():
                    account_id_str = key.split('_')[0]
                    account_code = id_to_code.get(account_id_str)
                    if account_code and account_code in accounts_data:
                        accounts_data[account_code]['initial_balance'] = bal_data.get('balance', 0)
                        accounts_data[account_code]['initial_debit'] = bal_data.get('debit', 0)
                        accounts_data[account_code]['initial_credit'] = bal_data.get('credit', 0)

        # Compute per-account running balances (starting from opening)
        self._compute_running_balances(accounts_data)

        # Recompute total_balance to include initial balance
        for acc in accounts_data.values():
            acc['total_balance'] = acc['initial_balance'] + acc['total_debit'] - acc['total_credit']

        # Add type badges to accounts
        self._add_type_badges(accounts_data)

        # Sort accounts by code
        sorted_accounts = sorted(accounts_data.values(), key=lambda x: x['account_code'])

        # Build grand totals from wizard totals or calculated
        grand_total = {
            'debit': totals.get('total_debit', sum(acc['total_debit'] for acc in accounts_data.values())),
            'credit': totals.get('total_credit', sum(acc['total_credit'] for acc in accounts_data.values())),
            'balance': totals.get('total_balance', sum(acc['total_balance'] for acc in accounts_data.values())),
        }

        currency_name = data.get('company_currency') or company.currency_id.name or ''
        colors = self._get_report_colors(company)

        result = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'docs': wizard,
            'data': data,
            'accounts': sorted_accounts,
            'grand_total': grand_total,
            'date_from': self._format_date(date_from),
            'date_to': self._format_date(date_to),
            'company': company,
            'currency_name': currency_name,
            'report_run_id': self._generate_report_run_id(),
            'account_count': len(sorted_accounts),
        }
        result.update(colors)
        return result

    # =========================================================================
    # DATABASE QUERY (fallback when no pre-computed data)
    # =========================================================================

    def _query_and_build_data(self, docids, doc_model, wizard, data):
        """
        Query database and build report data (fallback method).
        Used when no pre-computed data is available.
        """
        # Extract parameters from wizard or data dict
        if wizard and wizard.exists():
            date_from = wizard.date_from
            date_to = wizard.date_to
            target_move = getattr(wizard, 'target_move', 'posted')
            journal_ids = wizard.journal_ids.ids if hasattr(wizard, 'journal_ids') and wizard.journal_ids else []
            account_ids = wizard.account_ids.ids if hasattr(wizard, 'account_ids') and wizard.account_ids else []
            company_id = wizard.company_id.id if hasattr(wizard, 'company_id') and wizard.company_id else self.env.company.id
            company = wizard.company_id if hasattr(wizard, 'company_id') and wizard.company_id else self.env.company
        else:
            # Fall back to data dict parameters
            date_from = data.get('date_from')
            date_to = data.get('date_to')
            target_move = data.get('target_move', 'posted')
            journal_ids = data.get('journal_ids', [])
            account_ids = data.get('account_ids', [])
            company_id = data.get('company_id') or self.env.company.id
            company = self.env['res.company'].browse(company_id) if company_id else self.env.company

        # Build domain conditions
        domain = []

        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        if target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        if journal_ids:
            domain.append(('journal_id', 'in', journal_ids))
        if account_ids:
            domain.append(('account_id', 'in', account_ids))
        if company_id:
            domain.append(('company_id', '=', company_id))

        # Add matrix dimension filters if using enhanced wizard
        if wizard and hasattr(wizard, 'branch_ids') and wizard.branch_ids:
            domain.append(('ops_branch_id', 'in', wizard.branch_ids.ids))
        if wizard and hasattr(wizard, 'business_unit_ids') and wizard.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', wizard.business_unit_ids.ids))
        if wizard and hasattr(wizard, 'partner_ids') and wizard.partner_ids:
            domain.append(('partner_id', 'in', wizard.partner_ids.ids))

        # PERFORMANCE OPTIMIZATION: Use search_read instead of search
        move_lines_data = self.env['account.move.line'].search_read(
            domain,
            ['account_id', 'date', 'journal_id', 'partner_id', 'name', 'ref',
             'debit', 'credit', 'reconciled'],
            order='account_id, date, id'
        )

        # Group by account
        accounts_data = {}
        account_cache = {}  # Cache account lookups for performance
        for line_dict in move_lines_data:
            # Get account data from the tuple returned by search_read
            account_id = line_dict['account_id'][0] if line_dict.get('account_id') else False
            if not account_id:
                continue

            if account_id not in account_cache:
                account = self.env['account.account'].browse(account_id)
                account_cache[account_id] = {
                    'code': account.code,
                    'name': account.name,
                    'account_type': account.account_type or '',
                }

            acc_info = account_cache[account_id]
            account_code = acc_info['code']
            account_name = acc_info['name']

            if account_code not in accounts_data:
                accounts_data[account_code] = {
                    'account_code': account_code,
                    'account_name': account_name,
                    'account_type': acc_info['account_type'],
                    'lines': [],
                    'total_debit': 0.0,
                    'total_credit': 0.0,
                    'total_balance': 0.0,
                    'initial_balance': 0.0,
                    'initial_debit': 0.0,
                    'initial_credit': 0.0,
                }

            # Clean reference/description overlap
            ref = line_dict['ref'] or ''
            name = line_dict['name'] or ''

            line_data = {
                'account_code': account_code,
                'account_name': account_name,
                'move_date': self._format_date(line_dict['date']),
                'journal': line_dict['journal_id'][1] if line_dict.get('journal_id') else '',
                'partner': line_dict['partner_id'][1] if line_dict.get('partner_id') else '',
                'label': self._clean_description(ref, name),
                'reference': ref,
                'debit': line_dict['debit'],
                'credit': line_dict['credit'],
                'balance': 0,  # Computed as running balance below
                'reconciled': line_dict.get('reconciled', False),
            }
            accounts_data[account_code]['lines'].append(line_data)
            accounts_data[account_code]['total_debit'] += line_dict['debit']
            accounts_data[account_code]['total_credit'] += line_dict['credit']

        # Compute initial balances (before date_from)
        if date_from:
            init_domain = [
                ('date', '<', date_from),
                ('company_id', '=', company_id),
                ('move_id.state', '=', 'posted'),
            ]
            if account_ids:
                init_domain.append(('account_id', 'in', account_ids))
            if journal_ids:
                init_domain.append(('journal_id', 'in', journal_ids))
            if wizard and hasattr(wizard, 'branch_ids') and wizard.branch_ids:
                init_domain.append(('ops_branch_id', 'in', wizard.branch_ids.ids))
            if wizard and hasattr(wizard, 'business_unit_ids') and wizard.business_unit_ids:
                init_domain.append(('ops_business_unit_id', 'in', wizard.business_unit_ids.ids))

            init_data = self.env['account.move.line']._read_group(
                domain=init_domain,
                groupby=['account_id'],
                aggregates=['debit:sum', 'credit:sum', 'balance:sum']
            )
            for item in init_data:
                acc_record = item[0]  # account.account recordset
                init_debit = item[1] or 0
                init_credit = item[2] or 0
                init_balance = item[3] or 0
                acc_code = acc_record.code
                if acc_code in accounts_data:
                    accounts_data[acc_code]['initial_balance'] = init_balance
                    accounts_data[acc_code]['initial_debit'] = init_debit
                    accounts_data[acc_code]['initial_credit'] = init_credit

        # Compute per-account running balances (starting from opening)
        self._compute_running_balances(accounts_data)

        # Recompute total_balance to include initial balance
        for acc in accounts_data.values():
            acc['total_balance'] = acc['initial_balance'] + acc['total_debit'] - acc['total_credit']

        # Add type badges to accounts
        self._add_type_badges(accounts_data)

        # Sort accounts by code
        sorted_accounts = sorted(accounts_data.values(), key=lambda x: x['account_code'])

        # Calculate grand totals
        grand_total = {
            'debit': sum(acc['total_debit'] for acc in accounts_data.values()),
            'credit': sum(acc['total_credit'] for acc in accounts_data.values()),
            'balance': sum(acc['total_balance'] for acc in accounts_data.values()),
        }

        currency_name = company.currency_id.name or ''
        colors = self._get_report_colors(company)

        result = {
            'doc_ids': docids,
            'doc_model': doc_model,
            'docs': wizard,
            'data': data,
            'accounts': sorted_accounts,
            'grand_total': grand_total,
            'date_from': self._format_date(date_from),
            'date_to': self._format_date(date_to),
            'company': company,
            'currency_name': currency_name,
            'report_run_id': self._generate_report_run_id(),
            'account_count': len(sorted_accounts),
        }
        result.update(colors)
        return result


class OpsGeneralLedgerReportLegacy(models.AbstractModel):
    """
    Backward-compatible alias for the old report parser name.
    This ensures any references to the old report template still work.
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger'
    _inherit = 'report.ops_matrix_accounting.report_general_ledger_minimal'
    _description = 'General Ledger Report Parser (Legacy)'


class OpsGeneralLedgerReportCorporate(models.AbstractModel):
    """
    Report parser for the Corporate GL template.
    Used by GL, Partner Ledger, and SOA reports (all share the same template).
    Inherits all logic from the minimal parser.
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger_corporate'
    _inherit = 'report.ops_matrix_accounting.report_general_ledger_minimal'
    _description = 'General Ledger Report Parser (Corporate)'
