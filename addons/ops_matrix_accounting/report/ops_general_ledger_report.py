from odoo import models, api

class OpsGeneralLedgerReport(models.AbstractModel):
    """
    General Ledger Report Parser.
    Optimized for Odoo 19 with search_read() for better performance.
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger'
    _description = 'General Ledger Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            data = {}
        
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        target_move = data.get('target_move', 'posted')
        journal_ids = data.get('journal_ids', [])
        account_ids = data.get('account_ids', [])
        company_id = data.get('company_id')

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

        # Calculate grand totals
        grand_total = {
            'debit': sum(acc['total_debit'] for acc in accounts_data.values()),
            'credit': sum(acc['total_credit'] for acc in accounts_data.values()),
            'balance': sum(acc['total_balance'] for acc in accounts_data.values()),
        }

        return {
            'doc_ids': docids,
            'doc_model': 'ops.general.ledger.wizard',
            'data': data,
            'accounts': list(accounts_data.values()),
            'grand_total': grand_total,
            'date_from': date_from,
            'date_to': date_to,
            'company': self.env['res.company'].browse(company_id) if company_id else self.env.company,
        }
