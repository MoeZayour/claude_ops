from odoo import models, api

class OpsGeneralLedgerReportMinimal(models.AbstractModel):
    """
    General Ledger Report Parser for Minimal Template.
    Optimized for Odoo 19 with search_read() for better performance.

    This parser is used by both:
    - ops.general.ledger.wizard (original wizard)
    - ops.general.ledger.wizard.enhanced (Matrix Financial Intelligence)
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

        The wizard can pass pre-computed data or filter parameters.
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
            except Exception:
                pass
            # Fall back to original wizard
            if not wizard or not wizard.exists():
                try:
                    wizard = self.env['ops.general.ledger.wizard'].browse(docids)
                    doc_model = 'ops.general.ledger.wizard'
                except Exception:
                    wizard = None

        # Extract parameters from wizard or data dict
        if wizard and wizard.exists():
            wizard = wizard[0] if len(wizard) > 1 else wizard
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
