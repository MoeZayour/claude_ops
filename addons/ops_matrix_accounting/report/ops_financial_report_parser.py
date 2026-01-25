# -*- coding: utf-8 -*-
from odoo import models, api


class OpsFinancialReportParser(models.AbstractModel):
    """Financial Report Parser - Fixed for Odoo 19 CE."""
    _name = 'report.ops_matrix_accounting.report_ops_financial_document'
    _description = 'Financial Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Detect which wizard model to use based on context or data
        active_model = self.env.context.get('active_model', 'ops.financial.report.wizard')

        # Try enhanced wizard first if indicated
        if active_model == 'ops.general.ledger.wizard.enhanced':
            wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
            if wizard.exists():
                return self._get_enhanced_wizard_values(wizard, docids, data)

        # Fall back to original wizard
        wizard = self.env['ops.financial.report.wizard'].browse(docids)
        if not wizard.exists():
            wizard = self.env['ops.financial.report.wizard'].browse(
                self.env.context.get('active_id')
            )

        # If still no wizard found, try enhanced wizard
        if not wizard.exists():
            wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
            if wizard.exists():
                return self._get_enhanced_wizard_values(wizard, docids, data)

        report_data = self._get_report_data(wizard)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.financial.report.wizard',
            'docs': wizard,
            'report_data': report_data,
        }

    def _get_enhanced_wizard_values(self, wizard, docids, data=None):
        """Get report values for the enhanced wizard."""
        # If data was passed, use it; otherwise generate from wizard
        if data and isinstance(data, dict) and 'report_type' in data:
            raw_data = data
        else:
            raw_data = wizard._get_report_data()

        # Transform to template format
        report_data = self._transform_enhanced_data(wizard, raw_data)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.general.ledger.wizard.enhanced',
            'docs': wizard,
            'report_data': report_data,
        }

    def _transform_enhanced_data(self, wizard, data):
        """Transform enhanced wizard data to template format."""
        if not wizard or not data:
            return {}

        report_type = data.get('report_type', 'gl')

        result = {
            'title': data.get('report_title', 'Financial Report'),
            'company': data.get('company_name', ''),
            'branch': ', '.join(data.get('filters', {}).get('branch_names', [])) or 'All Branches',
            'user': self.env.user.name,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
            'target_move': data.get('filters', {}).get('target_move', 'posted'),
        }

        if report_type == 'gl':
            result.update(self._transform_gl_from_enhanced(data))
        elif report_type == 'pl':
            result.update(self._transform_pl_from_enhanced(data))
        elif report_type == 'bs':
            result.update(self._transform_bs_from_enhanced(data))
        elif report_type == 'tb':
            result.update(self._transform_tb_from_enhanced(data))
        elif report_type == 'cf':
            result.update(self._transform_cf_from_enhanced(data))
        elif report_type == 'aged':
            result.update(self._transform_aged_from_enhanced(data))
        elif report_type in ('partner', 'soa'):
            result.update(self._transform_partner_from_enhanced(data))

        return result

    def _transform_gl_from_enhanced(self, data):
        """Transform GL data from enhanced wizard."""
        lines = []
        report_data = data.get('data', [])
        if isinstance(report_data, dict):
            detailed = report_data.get('detailed', report_data.get('summary', []))
        else:
            detailed = report_data

        for line in detailed:
            lines.append({
                'date': line.get('date', ''),
                'move_name': line.get('move_name', ''),
                'move_id': line.get('move_id'),
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'partner': line.get('partner_name', ''),
                'label': line.get('name', ''),
                'debit': line.get('debit', 0),
                'credit': line.get('credit', 0),
                'balance': line.get('balance', 0),
            })
        return {'headers': ['Date', 'Entry', 'Account', 'Partner', 'Label', 'Debit', 'Credit', 'Balance'], 'lines': lines}

    def _transform_pl_from_enhanced(self, data):
        """Transform P&L data from enhanced wizard."""
        income_lines, expense_lines = [], []
        income_total, expense_total, cogs_total = 0, 0, 0

        for section in data.get('sections', []):
            section_type = section.get('type', '')
            for acc in section.get('accounts', []):
                line = {
                    'account': f"{acc.get('account_code', '')} - {acc.get('account_name', '')}",
                    'account_id': acc.get('account_id'),
                    'amount': abs(acc.get('balance', 0)),
                }
                if 'income' in section_type:
                    income_lines.append(line)
                    income_total += line['amount']
                elif 'expense' in section_type:
                    expense_lines.append(line)
                    expense_total += line['amount']
                    if 'direct_cost' in section_type:
                        cogs_total += line['amount']

        summary = data.get('summary', {})
        return {
            'headers': ['Account', 'Amount'],
            'income_lines': income_lines,
            'expense_lines': expense_lines,
            'income_total': summary.get('total_income', income_total),
            'expense_total': summary.get('total_expense', expense_total),
            'cogs_total': cogs_total,
            'gross_profit': summary.get('total_income', income_total) - cogs_total,
            'net_profit': summary.get('net_income', income_total - expense_total),
            'lines': income_lines + expense_lines,
        }

    def _transform_bs_from_enhanced(self, data):
        """Transform Balance Sheet data from enhanced wizard."""
        asset_lines, liability_lines, equity_lines = [], [], []

        for section in data.get('sections', []):
            section_type = section.get('type', '')
            for acc in section.get('accounts', []):
                line = {'account': f"{acc.get('account_code', '')} - {acc.get('account_name', '')}", 'amount': acc.get('balance', 0)}
                if section_type.startswith('asset'):
                    asset_lines.append(line)
                elif section_type.startswith('liability'):
                    liability_lines.append(line)
                elif section_type.startswith('equity'):
                    equity_lines.append(line)

        summary = data.get('summary', {})
        return {
            'headers': ['Account', 'Amount'],
            'asset_lines': asset_lines, 'liability_lines': liability_lines, 'equity_lines': equity_lines,
            'asset_total': summary.get('total_assets', 0),
            'liability_total': summary.get('total_liabilities', 0),
            'equity_total': summary.get('total_equity', 0),
            'lines': asset_lines + liability_lines + equity_lines,
        }

    def _transform_tb_from_enhanced(self, data):
        """Transform Trial Balance data from enhanced wizard."""
        lines = []
        total_debit, total_credit = 0, 0
        for line in data.get('data', []):
            lines.append({
                'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                'debit': line.get('ending_debit', 0),
                'credit': line.get('ending_credit', 0),
                'balance': line.get('ending_balance', 0),
            })
            total_debit += line.get('ending_debit', 0)
            total_credit += line.get('ending_credit', 0)
        totals = data.get('totals', {})
        return {
            'headers': ['Account', 'Debit', 'Credit', 'Balance'], 'lines': lines,
            'total_debit': totals.get('ending_debit', total_debit),
            'total_credit': totals.get('ending_credit', total_credit),
        }

    def _transform_cf_from_enhanced(self, data):
        """Transform Cash Flow data from enhanced wizard."""
        lines = []
        for section_data in data.get('sections', {}).values():
            for line in section_data.get('lines', []):
                lines.append({
                    'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                    'inflow': line.get('inflow', 0), 'outflow': line.get('outflow', 0), 'net': line.get('net', 0),
                })
        summary = data.get('summary', {})
        return {
            'headers': ['Account', 'Inflow', 'Outflow', 'Net'], 'lines': lines,
            'total_inflow': summary.get('total_operating', 0), 'total_outflow': 0,
            'net_cash_flow': summary.get('net_change', 0),
        }

    def _transform_aged_from_enhanced(self, data):
        """Transform Aged data from enhanced wizard."""
        lines = []
        for line in data.get('data', []):
            lines.append({
                'partner': line.get('partner_name', ''),
                'debit': line.get('total', 0) if line.get('total', 0) > 0 else 0,
                'credit': abs(line.get('total', 0)) if line.get('total', 0) < 0 else 0,
                'balance': line.get('total', 0),
            })
        return {'headers': ['Partner', 'Debit', 'Credit', 'Balance'], 'lines': lines}

    def _transform_partner_from_enhanced(self, data):
        """Transform Partner Ledger/SoA data from enhanced wizard."""
        lines = []
        for partner_data in data.get('data', data.get('statements', [])):
            for line in partner_data.get('lines', []):
                lines.append({
                    'partner': partner_data.get('partner_name', ''), 'date': line.get('date', ''),
                    'move_name': line.get('move_name', ''), 'debit': line.get('debit', 0),
                    'credit': line.get('credit', 0), 'balance': line.get('balance', 0),
                })
        return {'headers': ['Partner', 'Date', 'Entry', 'Debit', 'Credit', 'Balance'], 'lines': lines}

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
        elif wizard.report_type == 'tb':
            return self._process_tb_data(wizard, domain)
        elif wizard.report_type == 'cf':
            return self._process_cf_data(wizard, domain)
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

    def _process_tb_data(self, wizard, domain):
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        lines = []
        total_debit = 0.0
        total_credit = 0.0
        for result in grouped_data:
            account = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not account:
                continue
            lines.append({
                'account': f"{account.code} - {account.name}",
                'debit': debit_sum or 0.0,
                'credit': credit_sum or 0.0,
                'balance': balance_sum or 0.0,
            })
            total_debit += debit_sum or 0.0
            total_credit += credit_sum or 0.0
        return {
            'title': 'Trial Balance',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
            'total_debit': total_debit,
            'total_credit': total_credit,
        }

    def _process_cf_data(self, wizard, domain):
        # Simplified Cash Flow: Filter by liquidity accounts
        cf_domain = domain + [('account_id.account_type', '=', 'asset_cash')]
        MoveLine = self.env['account.move.line']
        grouped_data = MoveLine._read_group(
            domain=cf_domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum']
        )
        lines = []
        total_inflow = 0.0
        total_outflow = 0.0
        for result in grouped_data:
            account = result[0] if result else None
            debit_sum = result[1] if len(result) > 1 else 0.0
            credit_sum = result[2] if len(result) > 2 else 0.0
            balance_sum = result[3] if len(result) > 3 else 0.0
            if not account:
                continue
            lines.append({
                'account': f"{account.code} - {account.name}",
                'inflow': debit_sum or 0.0,
                'outflow': credit_sum or 0.0,
                'net': balance_sum or 0.0,
            })
            total_inflow += debit_sum or 0.0
            total_outflow += credit_sum or 0.0
        return {
            'title': 'Cash Flow Statement',
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
            'branch': wizard.branch_id.name if wizard.branch_id else 'All Branches',
            'company': wizard.company_id.name,
            'user': self.env.user.name,
            'target_move': dict(wizard._fields['target_move'].selection).get(wizard.target_move),
            'headers': ['Account', 'Inflow', 'Outflow', 'Net'],
            'lines': lines,
            'total_inflow': total_inflow,
            'total_outflow': total_outflow,
            'net_cash_flow': total_inflow - total_outflow,
        }
