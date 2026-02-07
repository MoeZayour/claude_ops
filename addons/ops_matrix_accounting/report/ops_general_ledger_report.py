from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class OpsGeneralLedgerReportMinimal(models.AbstractModel):
    """
    General Ledger Report Parser for Minimal Template.
    Optimized for Odoo 19 with search_read() for better performance.

    This parser is used by both:
    - ops.general.ledger.wizard (original wizard)
    - ops.general.ledger.wizard.enhanced (Matrix Financial Intelligence)

    Data Flow:
    - Wizard calls _get_report_data() → returns {data: [...], totals: {...}}
    - Wizard calls report.report_action(self, data=report_data)
    - Parser receives docids (wizard IDs) and data (pre-computed report data)
    - Parser transforms data to template format: {accounts: [...], grand_total: {...}}
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger_minimal'
    _description = 'General Ledger Report Parser (Minimal)'

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
                pass
            # Fall back to original wizard
            if not wizard or not wizard.exists():
                try:
                    wizard = self.env['ops.general.ledger.wizard'].browse(docids)
                    if wizard.exists():
                        doc_model = 'ops.general.ledger.wizard'
                        wizard = wizard[0] if len(wizard) > 1 else wizard
                except Exception:
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

    def _transform_wizard_data(self, docids, doc_model, wizard, data):
        """
        Transform wizard's pre-computed data to template format.

        Wizard returns: {data: [...], totals: {...}, date_from, date_to, ...}
        Template expects: {accounts: [...], grand_total: {...}, date_from, date_to, ...}
        """
        # Get dates from data or wizard
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        company_name = data.get('company_name', '')

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
        report_format = data.get('report_format', 'detailed')

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
                    'lines': [],
                    'total_debit': 0.0,
                    'total_credit': 0.0,
                    'total_balance': 0.0,
                }

            debit = line.get('debit', 0) or 0
            credit = line.get('credit', 0) or 0
            balance = line.get('balance', debit - credit)

            # Build line data for template
            line_data = {
                'account_code': account_code,
                'account_name': account_name,
                'move_date': line.get('date', ''),
                'journal': line.get('journal_code', ''),
                'partner': line.get('partner_name', ''),
                'label': line.get('name', ''),
                'reference': line.get('ref', ''),
                'debit': debit,
                'credit': credit,
                'balance': balance,
            }
            accounts_data[account_code]['lines'].append(line_data)
            accounts_data[account_code]['total_debit'] += debit
            accounts_data[account_code]['total_credit'] += credit
            accounts_data[account_code]['total_balance'] += balance

        # Sort accounts by code
        sorted_accounts = sorted(accounts_data.values(), key=lambda x: x['account_code'])

        # Build grand totals from wizard totals or calculated
        grand_total = {
            'debit': totals.get('total_debit', sum(acc['total_debit'] for acc in accounts_data.values())),
            'credit': totals.get('total_credit', sum(acc['total_credit'] for acc in accounts_data.values())),
            'balance': totals.get('total_balance', sum(acc['total_balance'] for acc in accounts_data.values())),
        }

        return {
            'doc_ids': docids,
            'doc_model': doc_model,
            'docs': wizard,
            'data': data,
            'accounts': sorted_accounts,
            'grand_total': grand_total,
            'date_from': date_from,
            'date_to': date_to,
            'company': company,
        }

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
        # This fetches dict list directly, avoiding heavy Recordset instantiation
        move_lines_data = self.env['account.move.line'].search_read(
            domain,
            ['account_id', 'date', 'journal_id', 'partner_id', 'name', 'ref', 'debit', 'credit'],
            order='account_id, date, id'
        )

        # Group by account
        accounts_data = {}
        for line_dict in move_lines_data:
            # Get account data from the tuple returned by search_read
            account_id = line_dict['account_id'][0] if line_dict.get('account_id') else False
            if not account_id:
                continue

            account = self.env['account.account'].browse(account_id)
            account_code = account.code
            account_name = account.name

            if account_code not in accounts_data:
                accounts_data[account_code] = {
                    'account_code': account_code,
                    'account_name': account_name,
                    'account_type': account.account_type or '',
                    'lines': [],
                    'total_debit': 0.0,
                    'total_credit': 0.0,
                    'total_balance': 0.0,
                }

            balance = line_dict['debit'] - line_dict['credit']

            line_data = {
                'account_code': account_code,
                'account_name': account_name,
                'move_date': line_dict['date'],
                'journal': line_dict['journal_id'][1] if line_dict.get('journal_id') else '',
                'partner': line_dict['partner_id'][1] if line_dict.get('partner_id') else '',
                'label': line_dict['name'],
                'reference': line_dict['ref'] or '',
                'debit': line_dict['debit'],
                'credit': line_dict['credit'],
                'balance': balance,
            }
            accounts_data[account_code]['lines'].append(line_data)
            accounts_data[account_code]['total_debit'] += line_dict['debit']
            accounts_data[account_code]['total_credit'] += line_dict['credit']
            accounts_data[account_code]['total_balance'] += balance

        # Sort accounts by code
        sorted_accounts = sorted(accounts_data.values(), key=lambda x: x['account_code'])

        # Calculate grand totals
        grand_total = {
            'debit': sum(acc['total_debit'] for acc in accounts_data.values()),
            'credit': sum(acc['total_credit'] for acc in accounts_data.values()),
            'balance': sum(acc['total_balance'] for acc in accounts_data.values()),
        }

        return {
            'doc_ids': docids,
            'doc_model': doc_model,
            'docs': wizard,
            'data': data,
            'accounts': sorted_accounts,
            'grand_total': grand_total,
            'date_from': date_from,
            'date_to': date_to,
            'company': company,
        }


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
