# -*- coding: utf-8 -*-
from odoo import models, api


class OpsFinancialReportParser(models.AbstractModel):
    """Financial Report Parser - Fixed for Odoo 19 CE."""
    _name = 'report.ops_matrix_accounting.report_ops_financial_document'
    _description = 'Financial Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.financial.report.wizard'].browse(docids)
        if not wizard:
            wizard = self.env['ops.financial.report.wizard'].browse(
                self.env.context.get('active_id')
            )
        report_data = self._get_report_data(wizard)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.financial.report.wizard',
            'docs': wizard,
            'report_data': report_data,
        }

    def _get_report_data(self, wizard):
        wizard.ensure_one()
        domain = wizard._get_domain()
        if wizard.report_type == 'pl':
            return self._process_pl_data(wizard, domain)
        elif wizard.report_type == 'bs':
            return self._process_bs_data(wizard, domain)
        elif wizard.report_type == 'gl':
            return self._process_gl_data(wizard, domain)
        elif wizard.report_type == 'aged':
            return self._process_aged_data(wizard, domain)
        return {}

    def _process_gl_data(self, wizard, domain):
        lines_data = self.env['account.move.line'].search_read(
            domain,
            ['date', 'move_id', 'account_id', 'partner_id', 'name', 'debit', 'credit', 'balance'],
            order='date, account_id, move_id',
            limit=10000
        )
        lines = []
        account_totals = {}
        for line_dict in lines_data:
            account = self.env['account.account'].browse(
                line_dict['account_id'][0]
            ) if line_dict.get('account_id') else False
            account_code = account.code if account else ''
            account_name = account.name if account else ''
            account_key = f"{account_code} - {account_name}"
            if account_key not in account_totals:
                account_totals[account_key] = {'debit': 0.0, 'credit': 0.0, 'balance': 0.0}
            account_totals[account_key]['debit'] += line_dict['debit']
            account_totals[account_key]['credit'] += line_dict['credit']
            account_totals[account_key]['balance'] += line_dict['balance']
            lines.append({
                'date': line_dict['date'],
                'move_name': line_dict['move_id'][1] if line_dict.get('move_id') else '',
                'move_id': line_dict['move_id'][0] if line_dict.get('move_id') else False,
                'account': account_key,
                'account_id': account.id if account else False,
                'partner': line_dict['partner_id'][1] if line_dict.get('partner_id') else '',
                'label': line_dict['name'] or '',
                'debit': line_dict['debit'],
                'credit': line_dict['credit'],
                'balance': line_dict['balance'],
            })
        return {
            'title': 'General Ledger',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Date', 'Entry', 'Account', 'Partner', 'Label', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
            'account_totals': account_totals,
        }

    def _process_pl_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        income_lines = []
        expense_lines = []
        income_total = 0.0
        expense_total = 0.0
        cogs_total = 0.0
        for result in grouped_data:
            account = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            if not account:
                continue
            account_key = f"{account.code} - {account.name}"
            account_type = account.account_type
            if account_type in ['income', 'income_other']:
                amount = (credit_sum or 0.0) - (debit_sum or 0.0)
                income_total += amount
                income_lines.append({'account': account_key, 'account_id': account.id, 'amount': amount})
            elif account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
                amount = (debit_sum or 0.0) - (credit_sum or 0.0)
                expense_total += amount
                if account_type == 'expense_direct_cost':
                    cogs_total += amount
                expense_lines.append({'account': account_key, 'account_id': account.id, 'amount': amount})
        gross_profit = income_total - cogs_total
        net_profit = income_total - expense_total
        return {
            'title': 'Profit & Loss',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Amount'],
            'income_lines': income_lines,
            'expense_lines': expense_lines,
            'income_total': income_total,
            'expense_total': expense_total,
            'cogs_total': cogs_total,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'lines': income_lines + expense_lines,
        }

    def _process_bs_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        asset_lines, liability_lines, equity_lines = [], [], []
        asset_total, liability_total, equity_total = 0.0, 0.0, 0.0
        for result in grouped_data:
            account = result[0] if result else None
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not account:
                continue
            account_key = f"{account.code} - {account.name}"
            account_type = account.account_type
            balance = balance_sum or 0.0
            if account_type in ['asset_receivable', 'asset_cash', 'asset_current',
                               'asset_prepayments', 'asset_fixed', 'asset_non_current']:
                asset_total += balance
                asset_lines.append({'account': account_key, 'amount': balance})
            elif account_type in ['liability_payable', 'liability_current', 'liability_non_current']:
                liability_total += balance
                liability_lines.append({'account': account_key, 'amount': balance})
            elif account_type == 'equity':
                equity_total += balance
                equity_lines.append({'account': account_key, 'amount': balance})
        return {
            'title': 'Balance Sheet',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Amount'],
            'asset_lines': asset_lines,
            'liability_lines': liability_lines,
            'equity_lines': equity_lines,
            'asset_total': asset_total,
            'liability_total': liability_total,
            'equity_total': equity_total,
            'lines': asset_lines + liability_lines + equity_lines,
        }

    def _process_aged_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['partner_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        lines = []
        for result in grouped_data:
            partner = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not partner:
                continue
            lines.append({
                'partner': partner.name,
                'debit': debit_sum or 0.0,
                'credit': credit_sum or 0.0,
                'balance': balance_sum or 0.0,
            })
        return {
            'title': 'Aged Partner Report',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Partner', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
        }
