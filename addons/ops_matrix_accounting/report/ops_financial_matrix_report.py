# -*- coding: utf-8 -*-
"""
Financial Matrix Report Parser
==============================

Report parser for the Financial Intelligence (Big 8) wizard.
Uses the wizard's _get_report_data() method for data generation.

v19.0.1.0: Initial implementation
"""

from odoo import models, api


class OpsFinancialMatrixReportParser(models.AbstractModel):
    """
    Report parser for the Enhanced GL Wizard (Financial Intelligence).

    This parser retrieves the wizard and uses its built-in data generation
    methods to provide report data to QWeb templates.
    """
    _name = 'report.ops_matrix_accounting.report_financial_matrix'
    _description = 'Financial Matrix Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Get report values for QWeb template rendering.

        Args:
            docids: List of wizard IDs
            data: Optional data dict passed to report

        Returns:
            Dict with docs, report_data, and other template variables
        """
        # Get wizard record
        wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
        if not wizard:
            # Try from context
            wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(
                self.env.context.get('active_id')
            )

        # If data was passed directly, use it; otherwise generate from wizard
        if data and isinstance(data, dict) and 'report_type' in data:
            report_data = data
        elif wizard:
            report_data = wizard._get_report_data()
        else:
            report_data = {}

        # Transform data to match template expectations
        template_data = self._transform_to_template_format(wizard, report_data)

        return {
            'doc_ids': docids,
            'doc_model': 'ops.general.ledger.wizard.enhanced',
            'docs': wizard,
            'report_data': template_data,
        }

    def _transform_to_template_format(self, wizard, data):
        """
        Transform the wizard's report data to the format expected by
        the existing QWeb template (report_ops_financial_document).

        The template expects keys like: title, company, branch, user,
        date_from, date_to, target_move, lines, income_lines, etc.
        """
        if not wizard or not data:
            return {}

        report_type = data.get('report_type', 'gl')

        # Common fields
        result = {
            'title': data.get('report_title', 'Financial Report'),
            'company': data.get('company_name', ''),
            'branch': ', '.join(data.get('filters', {}).get('branch_names', [])) or 'All Branches',
            'user': self.env.user.name,
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
            'target_move': data.get('filters', {}).get('target_move', 'posted'),
        }

        # Report type specific transformations
        if report_type == 'gl':
            result.update(self._transform_gl_data(data))
        elif report_type == 'pl':
            result.update(self._transform_pl_data(data))
        elif report_type == 'bs':
            result.update(self._transform_bs_data(data))
        elif report_type == 'tb':
            result.update(self._transform_tb_data(data))
        elif report_type == 'cf':
            result.update(self._transform_cf_data(data))
        elif report_type == 'aged':
            result.update(self._transform_aged_data(data))
        elif report_type in ('partner', 'soa'):
            result.update(self._transform_partner_data(data))

        return result

    def _transform_gl_data(self, data):
        """Transform GL data to template format."""
        lines = []
        report_data = data.get('data', [])

        # Handle both list and dict formats
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

        return {
            'headers': ['Date', 'Entry', 'Account', 'Partner', 'Label', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
        }

    def _transform_pl_data(self, data):
        """Transform P&L data to template format."""
        income_lines = []
        expense_lines = []
        income_total = 0
        expense_total = 0
        cogs_total = 0

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

    def _transform_bs_data(self, data):
        """Transform Balance Sheet data to template format."""
        asset_lines = []
        liability_lines = []
        equity_lines = []

        for section in data.get('sections', []):
            section_type = section.get('type', '')
            for acc in section.get('accounts', []):
                line = {
                    'account': f"{acc.get('account_code', '')} - {acc.get('account_name', '')}",
                    'amount': acc.get('balance', 0),
                }

                if section_type.startswith('asset'):
                    asset_lines.append(line)
                elif section_type.startswith('liability'):
                    liability_lines.append(line)
                elif section_type.startswith('equity'):
                    equity_lines.append(line)

        summary = data.get('summary', {})

        return {
            'headers': ['Account', 'Amount'],
            'asset_lines': asset_lines,
            'liability_lines': liability_lines,
            'equity_lines': equity_lines,
            'asset_total': summary.get('total_assets', 0),
            'liability_total': summary.get('total_liabilities', 0),
            'equity_total': summary.get('total_equity', 0),
            'lines': asset_lines + liability_lines + equity_lines,
        }

    def _transform_tb_data(self, data):
        """Transform Trial Balance data to template format."""
        lines = []
        total_debit = 0
        total_credit = 0

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
            'headers': ['Account', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
            'total_debit': totals.get('ending_debit', total_debit),
            'total_credit': totals.get('ending_credit', total_credit),
        }

    def _transform_cf_data(self, data):
        """Transform Cash Flow data to template format."""
        lines = []

        sections = data.get('sections', {})
        for section_data in sections.values():
            for line in section_data.get('lines', []):
                lines.append({
                    'account': f"{line.get('account_code', '')} - {line.get('account_name', '')}",
                    'inflow': line.get('inflow', 0),
                    'outflow': line.get('outflow', 0),
                    'net': line.get('net', 0),
                })

        summary = data.get('summary', {})

        return {
            'headers': ['Account', 'Inflow', 'Outflow', 'Net'],
            'lines': lines,
            'total_inflow': summary.get('total_operating', 0) + summary.get('total_investing', 0) + summary.get('total_financing', 0),
            'total_outflow': 0,  # Calculate if needed
            'net_cash_flow': summary.get('net_change', 0),
        }

    def _transform_aged_data(self, data):
        """Transform Aged data to template format."""
        lines = []

        for line in data.get('data', []):
            lines.append({
                'partner': line.get('partner_name', ''),
                'debit': line.get('total', 0) if line.get('total', 0) > 0 else 0,
                'credit': abs(line.get('total', 0)) if line.get('total', 0) < 0 else 0,
                'balance': line.get('total', 0),
            })

        return {
            'headers': ['Partner', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
        }

    def _transform_partner_data(self, data):
        """Transform Partner Ledger/SoA data to template format."""
        lines = []

        # Handle both partner ledger and SoA formats
        for partner_data in data.get('data', data.get('statements', [])):
            for line in partner_data.get('lines', []):
                lines.append({
                    'partner': partner_data.get('partner_name', ''),
                    'date': line.get('date', ''),
                    'move_name': line.get('move_name', ''),
                    'debit': line.get('debit', 0),
                    'credit': line.get('credit', 0),
                    'balance': line.get('balance', 0),
                })

        return {
            'headers': ['Partner', 'Date', 'Entry', 'Debit', 'Credit', 'Balance'],
            'lines': lines,
        }
