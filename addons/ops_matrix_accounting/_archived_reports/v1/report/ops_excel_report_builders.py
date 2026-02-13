# -*- coding: utf-8 -*-
"""
OPS Matrix — Report-Specific Excel Builders
=============================================
Each financial report gets its own Excel layout matching its PDF hierarchy.
Uses shared corporate format factory from excel_styles.py.

Wave 1: Trial Balance, Profit & Loss, Balance Sheet, Cash Flow
"""

from odoo import fields


class ExcelReportBuilder:
    """Base class for report-specific Excel builders."""

    def __init__(self, workbook, formats, company, wizard):
        self.workbook = workbook
        self.formats = formats
        self.company = company
        self.wizard = wizard

    def _write_corporate_header(self, ws, row=0):
        """Write standard corporate header block. Returns next row."""
        f = self.formats
        ws.write(row, 0, self.company.name, f['company_name'])
        row += 1
        ws.write(row, 0, self.report_title, f['report_title'])
        row += 1

        if hasattr(self.wizard, 'date_from') and self.wizard.date_from:
            period = f"Period: {self.wizard.date_from} to {self.wizard.date_to}"
        elif hasattr(self.wizard, 'as_of_date') and self.wizard.as_of_date:
            period = f"As of: {self.wizard.as_of_date}"
        else:
            period = ""
        if period:
            ws.write(row, 0, period, f['metadata'])
            row += 1

        gen = f"Generated: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.wizard.env.user.name}"
        ws.write(row, 0, gen, f['metadata'])
        row += 2  # blank row

        # Filter bar
        filter_parts = []
        if self.wizard.branch_ids:
            filter_parts.append(f"Branches: {', '.join(self.wizard.branch_ids.mapped('name'))}")
        if self.wizard.business_unit_ids:
            filter_parts.append(f"BUs: {', '.join(self.wizard.business_unit_ids.mapped('name'))}")
        scope = ' | '.join(filter_parts) if filter_parts else 'All Data'
        currency = self.company.currency_id.name or 'USD'
        ws.merge_range(row, 0, row, self.last_col,
                       f"Scope: {scope} | Currency: {currency}",
                       f['filter_bar'])
        row += 2
        return row

    def _write_number(self, ws, row, col, value, alt=False):
        """Write a number with appropriate format based on value sign."""
        f = self.formats
        value = float(value or 0)
        if abs(value) < 0.01:
            fmt = f['number_zero_alt'] if alt else f['number_zero']
        elif value < 0:
            fmt = f['number_negative_alt'] if alt else f['number_negative']
        else:
            fmt = f['number_alt'] if alt else f['number']
        ws.write_number(row, col, value, fmt)

    def build(self, data):
        raise NotImplementedError


class TrialBalanceExcelBuilder(ExcelReportBuilder):
    """
    Trial Balance: Account Code | Account Name | Initial Dr/Cr |
                   Period Dr/Cr | Ending Dr/Cr | Balance
    """
    report_title = 'Trial Balance'
    last_col = 8

    def build(self, data):
        ws = self.workbook.add_worksheet('Trial Balance')
        f = self.formats

        ws.set_column('A:A', 14)
        ws.set_column('B:B', 35)
        ws.set_column('C:I', 16)

        row = self._write_corporate_header(ws)

        headers = [
            ('Account Code', False), ('Account Name', False),
            ('Initial Debit', True), ('Initial Credit', True),
            ('Period Debit', True), ('Period Credit', True),
            ('Ending Debit', True), ('Ending Credit', True),
            ('Balance', True),
        ]
        for col, (label, is_num) in enumerate(headers):
            fmt = f['table_header_num'] if is_num else f['table_header']
            ws.write(row, col, label, fmt)
        row += 1
        ws.freeze_panes(row, 2)

        lines = data.get('data', [])
        for idx, line in enumerate(lines):
            alt = idx % 2 == 1
            text_fmt = f['text_alt'] if alt else f['text']

            ws.write(row, 0, line.get('account_code', ''), text_fmt)
            ws.write(row, 1, line.get('account_name', ''), text_fmt)
            self._write_number(ws, row, 2, line.get('initial_debit', 0), alt)
            self._write_number(ws, row, 3, line.get('initial_credit', 0), alt)
            self._write_number(ws, row, 4, line.get('period_debit', 0), alt)
            self._write_number(ws, row, 5, line.get('period_credit', 0), alt)
            self._write_number(ws, row, 6, line.get('ending_debit', 0), alt)
            self._write_number(ws, row, 7, line.get('ending_credit', 0), alt)
            self._write_number(ws, row, 8, line.get('ending_balance', 0), alt)
            row += 1

        totals = data.get('totals', {})
        ws.write(row, 0, 'GRAND TOTAL', f['total_label'])
        ws.write(row, 1, f"{totals.get('line_count', 0)} accounts", f['total_label'])
        ws.write_number(row, 2, totals.get('initial_debit', 0), f['total_number'])
        ws.write_number(row, 3, totals.get('initial_credit', 0), f['total_number'])
        ws.write_number(row, 4, totals.get('period_debit', 0), f['total_number'])
        ws.write_number(row, 5, totals.get('period_credit', 0), f['total_number'])
        ws.write_number(row, 6, totals.get('ending_debit', 0), f['total_number'])
        ws.write_number(row, 7, totals.get('ending_credit', 0), f['total_number'])
        ws.write_number(row, 8,
                        totals.get('ending_debit', 0) - totals.get('ending_credit', 0),
                        f['total_number'])

        ws.set_landscape()
        ws.fit_to_pages(1, 0)
        ws.set_paper(9)
        return ws


class ProfitLossExcelBuilder(ExcelReportBuilder):
    """
    P&L: Hierarchical Revenue > COGS > Gross Profit > Expenses > Net Income
    """
    report_title = 'Profit & Loss Statement'
    last_col = 2

    def build(self, data):
        ws = self.workbook.add_worksheet('Profit & Loss')
        f = self.formats

        ws.set_column('A:A', 16)
        ws.set_column('B:B', 45)
        ws.set_column('C:C', 20)

        row = self._write_corporate_header(ws)

        ws.write(row, 0, 'Code', f['table_header'])
        ws.write(row, 1, 'Description', f['table_header'])
        ws.write(row, 2, 'Amount', f['table_header_num'])
        row += 1
        ws.freeze_panes(row, 0)

        summary = data.get('summary', {})
        sections = data.get('sections', [])
        hierarchy = data.get('hierarchy', {})

        # REVENUE
        row = self._write_section_header(ws, row, 'REVENUE')
        if hierarchy and hierarchy.get('income_hierarchy'):
            row = self._write_hierarchy_lines(ws, row, hierarchy['income_hierarchy'])
        else:
            row = self._write_flat_section(ws, row, sections, ['income', 'income_other'])
        row = self._write_subtotal(ws, row, 'Total Revenue', summary.get('total_income', 0))

        # COST OF REVENUE
        cogs = summary.get('cogs_total', 0)
        if abs(cogs) > 0.01:
            row += 1
            row = self._write_section_header(ws, row, 'COST OF REVENUE')
            row = self._write_flat_section(ws, row, sections, ['expense_direct_cost'])
            row = self._write_subtotal(ws, row, 'Total Cost of Revenue', cogs)
            row += 1
            gross = summary.get('gross_profit', 0)
            ws.write(row, 0, '', f['subtotal_label'])
            ws.write(row, 1, 'GROSS PROFIT', f['subtotal_label'])
            ws.write_number(row, 2, gross, f['subtotal_number'])
            row += 1

        # EXPENSES
        row += 1
        row = self._write_section_header(ws, row, 'OPERATING EXPENSES')
        if hierarchy and hierarchy.get('expense_hierarchy'):
            row = self._write_hierarchy_lines(ws, row, hierarchy['expense_hierarchy'])
        else:
            row = self._write_flat_section(ws, row, sections, ['expense', 'expense_depreciation'])
        row = self._write_subtotal(ws, row, 'Total Expenses', summary.get('total_expense', 0))

        # NET INCOME
        row += 1
        net = summary.get('net_income', 0)
        ws.write(row, 0, '', f['total_label'])
        ws.write(row, 1, 'NET INCOME', f['total_label'])
        ws.write_number(row, 2, net, f['total_number'])

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_paper(9)
        return ws

    def _write_section_header(self, ws, row, title):
        f = self.formats
        for col in range(3):
            ws.write(row, col, title if col == 1 else '', f['subtotal_label'])
        return row + 1

    def _write_subtotal(self, ws, row, label, amount):
        f = self.formats
        ws.write(row, 0, '', f['subtotal_label'])
        ws.write(row, 1, label, f['subtotal_label'])
        ws.write_number(row, 2, abs(float(amount or 0)), f['subtotal_number'])
        return row + 1

    def _write_hierarchy_lines(self, ws, row, lines):
        f = self.formats
        idx = 0
        for line in lines:
            ltype = line.get('type', 'account')
            indent = line.get('indent', 0)
            name = line.get('name', '')
            balance = abs(float(line.get('balance', 0)))

            if ltype == 'group':
                ws.write(row, 0, '', f['subtotal_label'])
                ws.write(row, 1, ('  ' * indent) + name, f['subtotal_label'])
                ws.write(row, 2, '', f['subtotal_label'])
            elif ltype == 'subtotal':
                ws.write(row, 0, '', f['subtotal_label'])
                ws.write(row, 1, ('  ' * indent) + name, f['subtotal_label'])
                ws.write_number(row, 2, balance, f['subtotal_number'])
            else:
                alt = idx % 2 == 1
                text_fmt = f['text_alt'] if alt else f['text']
                ws.write(row, 0, line.get('code', ''), text_fmt)
                ws.write(row, 1, ('  ' * indent) + name, text_fmt)
                self._write_number(ws, row, 2, balance, alt)
                idx += 1
            row += 1
        return row

    def _write_flat_section(self, ws, row, sections, type_keys):
        f = self.formats
        idx = 0
        for section in sections:
            if isinstance(section, dict) and section.get('type') in type_keys:
                for acct in section.get('accounts', []):
                    alt = idx % 2 == 1
                    text_fmt = f['text_alt'] if alt else f['text']
                    ws.write(row, 0, acct.get('account_code', ''), text_fmt)
                    ws.write(row, 1, acct.get('account_name', ''), text_fmt)
                    self._write_number(ws, row, 2, abs(float(acct.get('balance', 0))), alt)
                    row += 1
                    idx += 1
        return row


class BalanceSheetExcelBuilder(ExcelReportBuilder):
    """
    Balance Sheet: Assets | Liabilities | Equity with balance check
    """
    report_title = 'Balance Sheet'
    last_col = 2

    def build(self, data):
        ws = self.workbook.add_worksheet('Balance Sheet')
        f = self.formats

        ws.set_column('A:A', 16)
        ws.set_column('B:B', 45)
        ws.set_column('C:C', 20)

        row = self._write_corporate_header(ws)

        ws.write(row, 0, 'Code', f['table_header'])
        ws.write(row, 1, 'Description', f['table_header'])
        ws.write(row, 2, 'Amount', f['table_header_num'])
        row += 1
        ws.freeze_panes(row, 0)

        summary = data.get('summary', {})
        sections = data.get('sections', [])
        hierarchy = data.get('hierarchy', {})

        # ASSETS
        row = self._write_section_header(ws, row, 'ASSETS')
        if hierarchy and hierarchy.get('asset_hierarchy'):
            row = self._write_hierarchy_lines(ws, row, hierarchy['asset_hierarchy'])
        else:
            row = self._write_flat_section(ws, row, sections,
                ['asset_receivable', 'asset_cash', 'asset_current',
                 'asset_non_current', 'asset_prepayments', 'asset_fixed'])
        row = self._write_subtotal(ws, row, 'Total Assets', summary.get('total_assets', 0))

        # LIABILITIES
        row += 1
        row = self._write_section_header(ws, row, 'LIABILITIES')
        if hierarchy and hierarchy.get('liability_hierarchy'):
            row = self._write_hierarchy_lines(ws, row, hierarchy['liability_hierarchy'])
        else:
            row = self._write_flat_section(ws, row, sections,
                ['liability_payable', 'liability_credit_card',
                 'liability_current', 'liability_non_current'])
        row = self._write_subtotal(ws, row, 'Total Liabilities', summary.get('total_liabilities', 0))

        # EQUITY
        row += 1
        row = self._write_section_header(ws, row, 'EQUITY')
        if hierarchy and hierarchy.get('equity_hierarchy'):
            row = self._write_hierarchy_lines(ws, row, hierarchy['equity_hierarchy'])
        else:
            row = self._write_flat_section(ws, row, sections, ['equity', 'equity_unaffected'])
        row = self._write_subtotal(ws, row, 'Total Equity', summary.get('total_equity', 0))

        # TOTAL L+E
        row += 1
        total_le = summary.get('total_liabilities', 0) + summary.get('total_equity', 0)
        ws.write(row, 0, '', f['total_label'])
        ws.write(row, 1, 'TOTAL LIABILITIES + EQUITY', f['total_label'])
        ws.write_number(row, 2, total_le, f['total_number'])
        row += 1

        # Balance check
        check = summary.get('check_balance', 0)
        if abs(check) > 0.01:
            row += 1
            warn_fmt = self.workbook.add_format({
                'font_size': 10, 'bold': True, 'font_color': '#dc2626', 'font_name': 'Arial',
            })
            ws.write(row, 1, f"Warning: Balance check difference: {check:,.2f}", warn_fmt)

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_paper(9)
        return ws

    # Reuse P&L helpers
    _write_section_header = ProfitLossExcelBuilder._write_section_header
    _write_subtotal = ProfitLossExcelBuilder._write_subtotal
    _write_hierarchy_lines = ProfitLossExcelBuilder._write_hierarchy_lines
    _write_flat_section = ProfitLossExcelBuilder._write_flat_section


class CashFlowExcelBuilder(ExcelReportBuilder):
    """
    Cash Flow: Operating | Investing | Financing with Inflow/Outflow/Net
    """
    report_title = 'Cash Flow Statement'
    last_col = 4

    def build(self, data):
        ws = self.workbook.add_worksheet('Cash Flow')
        f = self.formats

        ws.set_column('A:A', 16)
        ws.set_column('B:B', 35)
        ws.set_column('C:E', 18)

        row = self._write_corporate_header(ws)

        sections_data = data.get('sections', {})
        summary = data.get('summary', {})

        section_map = [
            ('OPERATING ACTIVITIES', 'operating', 'total_operating'),
            ('INVESTING ACTIVITIES', 'investing', 'total_investing'),
            ('FINANCING ACTIVITIES', 'financing', 'total_financing'),
        ]

        for section_title, section_key, total_key in section_map:
            # Section header
            ws.merge_range(row, 0, row, 4, section_title, f['subtotal_label'])
            row += 1

            ws.write(row, 0, 'Account', f['table_header'])
            ws.write(row, 1, 'Journal', f['table_header'])
            ws.write(row, 2, 'Inflow', f['table_header_num'])
            ws.write(row, 3, 'Outflow', f['table_header_num'])
            ws.write(row, 4, 'Net', f['table_header_num'])
            row += 1

            section = sections_data.get(section_key, {})
            lines = section.get('lines', [])

            for idx, line in enumerate(lines):
                alt = idx % 2 == 1
                text_fmt = f['text_alt'] if alt else f['text']
                ws.write(row, 0, line.get('account_code', ''), text_fmt)
                ws.write(row, 1, line.get('journal_name', ''), text_fmt)
                self._write_number(ws, row, 2, line.get('inflow', 0), alt)
                self._write_number(ws, row, 3, line.get('outflow', 0), alt)
                self._write_number(ws, row, 4, line.get('net', 0), alt)
                row += 1

            section_total = summary.get(total_key, 0)
            ws.write(row, 0, '', f['subtotal_label'])
            ws.write(row, 1, f'Net {section_title.title()}', f['subtotal_label'])
            ws.write(row, 2, '', f['subtotal_label'])
            ws.write(row, 3, '', f['subtotal_label'])
            ws.write_number(row, 4, section_total, f['subtotal_number'])
            row += 2

        # Net Change
        net_change = summary.get('net_change', 0)
        ws.write(row, 0, '', f['total_label'])
        ws.write(row, 1, 'NET CHANGE IN CASH', f['total_label'])
        ws.write(row, 2, '', f['total_label'])
        ws.write(row, 3, '', f['total_label'])
        ws.write_number(row, 4, net_change, f['total_number'])

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_paper(9)
        return ws


# Builder registry
EXCEL_BUILDERS = {
    'tb': TrialBalanceExcelBuilder,
    'pl': ProfitLossExcelBuilder,
    'bs': BalanceSheetExcelBuilder,
    'cf': CashFlowExcelBuilder,
}
