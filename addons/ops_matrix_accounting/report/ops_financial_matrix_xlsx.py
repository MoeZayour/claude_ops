# -*- coding: utf-8 -*-
"""
Financial Matrix XLSX Export
============================

XLSX report for the Financial Intelligence (Big 8) wizard.
Supports: GL, TB, P&L, BS, CF, Aged, Partner Ledger, SoA

v19.0.1.0: Initial implementation
"""

from odoo import models
from odoo.exceptions import UserError

try:
    from .excel_styles import OPSExcelStyles, apply_standard_widths
except ImportError:
    OPSExcelStyles = None


class OpsFinancialMatrixXlsx(models.AbstractModel):
    """
    Financial Matrix XLSX Export for the Enhanced GL Wizard.
    Handles all 8 report types with unified styling.
    """
    _name = 'report.ops_matrix_accounting.report_financial_matrix_xlsx'
    _description = 'Financial Matrix XLSX Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizards):
        """
        Generate XLSX report using xlsxwriter.

        Args:
            workbook: xlsxwriter.Workbook instance
            data: Report data dict from wizard
            wizards: Wizard recordset (docids)
        """
        try:
            # Initialize styles
            if OPSExcelStyles:
                styles = OPSExcelStyles(workbook)
            else:
                styles = self._create_basic_styles(workbook)

            # Get data - either from data param or generate from wizard
            report_data = data if data else {}
            if not report_data and wizards:
                wizard = wizards[0]
                report_data = wizard._get_report_data()

            report_type = report_data.get('report_type', 'gl')
            report_title = report_data.get('report_title', 'Financial Report')

            # Create worksheet
            worksheet = workbook.add_worksheet(report_title[:31])  # Excel limit

            # Dispatch to appropriate handler
            handlers = {
                'gl': self._generate_gl_sheet,
                'tb': self._generate_tb_sheet,
                'pl': self._generate_pl_sheet,
                'bs': self._generate_bs_sheet,
                'cf': self._generate_cf_sheet,
                'aged': self._generate_aged_sheet,
                'partner': self._generate_partner_sheet,
                'soa': self._generate_soa_sheet,
            }

            handler = handlers.get(report_type, self._generate_gl_sheet)
            handler(workbook, worksheet, styles, report_data)

        except Exception as e:
            raise UserError(f"Error generating XLSX report: {str(e)}")

    def _create_basic_styles(self, workbook):
        """Create basic styles if OPSExcelStyles not available."""
        class BasicStyles:
            def __init__(self, wb):
                self.title = wb.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
                self.header = wb.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'border': 1})
                self.subheader = wb.add_format({'bold': True, 'bg_color': '#D9E2F3', 'border': 1})
                self.meta_label = wb.add_format({'bold': True})
                self.meta_value = wb.add_format({})
                self.text = wb.add_format({'border': 1})
                self.currency = wb.add_format({'num_format': '#,##0.00', 'border': 1})
                self.currency_positive = wb.add_format({'num_format': '#,##0.00', 'border': 1, 'font_color': 'green'})
                self.currency_negative = wb.add_format({'num_format': '#,##0.00', 'border': 1, 'font_color': 'red'})
                self.total = wb.add_format({'bold': True, 'border': 1, 'bg_color': '#E2EFDA'})
                self.total_currency = wb.add_format({'bold': True, 'num_format': '#,##0.00', 'border': 1, 'bg_color': '#E2EFDA'})
                self.grand_total = wb.add_format({'bold': True, 'border': 2, 'bg_color': '#4472C4', 'font_color': 'white'})
                self.grand_total_currency = wb.add_format({'bold': True, 'num_format': '#,##0.00', 'border': 2, 'bg_color': '#4472C4', 'font_color': 'white'})
                self.date = wb.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})

            def get_row_style(self, idx, is_currency=False):
                return self.currency if is_currency else self.text

            def get_currency_style(self, value):
                if value > 0:
                    return self.currency_positive
                elif value < 0:
                    return self.currency_negative
                return self.currency

        return BasicStyles(workbook)

    def _write_header(self, worksheet, styles, report_data, row=0):
        """Write common report header."""
        report_title = report_data.get('report_title', 'Financial Report')
        worksheet.merge_range(row, 0, row, 7, report_title.upper(), styles.title)
        row += 2

        # Metadata
        worksheet.write(row, 0, 'Company:', styles.meta_label)
        worksheet.write(row, 1, report_data.get('company_name', ''), styles.meta_value)
        row += 1

        filters = report_data.get('filters', {})
        date_range = filters.get('date_range', '')
        if report_data.get('as_of_date'):
            worksheet.write(row, 0, 'As of Date:', styles.meta_label)
            worksheet.write(row, 1, report_data.get('as_of_date', ''), styles.meta_value)
        else:
            worksheet.write(row, 0, 'Period:', styles.meta_label)
            worksheet.write(row, 1, date_range, styles.meta_value)
        row += 1

        worksheet.write(row, 0, 'Currency:', styles.meta_label)
        worksheet.write(row, 1, report_data.get('company_currency', 'USD'), styles.meta_value)
        row += 2

        return row

    def _generate_gl_sheet(self, workbook, worksheet, styles, data):
        """Generate General Ledger sheet."""
        row = self._write_header(worksheet, styles, data)

        # Set column widths
        worksheet.set_column(0, 0, 12)  # Date
        worksheet.set_column(1, 1, 15)  # Move
        worksheet.set_column(2, 2, 10)  # Journal
        worksheet.set_column(3, 3, 12)  # Account
        worksheet.set_column(4, 4, 20)  # Partner
        worksheet.set_column(5, 5, 30)  # Name
        worksheet.set_column(6, 6, 12)  # Debit
        worksheet.set_column(7, 7, 12)  # Credit
        worksheet.set_column(8, 8, 14)  # Balance

        # Headers
        headers = ['Date', 'Entry', 'Journal', 'Account', 'Partner', 'Description', 'Debit', 'Credit', 'Balance']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        # Data
        report_data = data.get('data', [])
        if isinstance(report_data, dict):
            # Handle both formats
            lines = report_data.get('detailed', report_data.get('summary', []))
        else:
            lines = report_data

        for line in lines:
            worksheet.write(row, 0, line.get('date', ''), styles.date if hasattr(styles, 'date') else styles.text)
            worksheet.write(row, 1, line.get('move_name', ''), styles.text)
            worksheet.write(row, 2, line.get('journal_code', ''), styles.text)
            worksheet.write(row, 3, line.get('account_code', ''), styles.text)
            worksheet.write(row, 4, line.get('partner_name', ''), styles.text)
            worksheet.write(row, 5, line.get('name', ''), styles.text)
            worksheet.write(row, 6, line.get('debit', 0), styles.currency)
            worksheet.write(row, 7, line.get('credit', 0), styles.currency)
            worksheet.write(row, 8, line.get('balance', 0), styles.get_currency_style(line.get('balance', 0)))
            row += 1

        # Totals
        totals = data.get('totals', {})
        row += 1
        worksheet.write(row, 5, 'TOTAL:', styles.grand_total)
        worksheet.write(row, 6, totals.get('total_debit', 0), styles.grand_total_currency)
        worksheet.write(row, 7, totals.get('total_credit', 0), styles.grand_total_currency)
        worksheet.write(row, 8, totals.get('total_balance', 0), styles.grand_total_currency)

    def _generate_tb_sheet(self, workbook, worksheet, styles, data):
        """Generate Trial Balance sheet."""
        row = self._write_header(worksheet, styles, data)

        worksheet.set_column(0, 0, 12)  # Code
        worksheet.set_column(1, 1, 35)  # Name
        worksheet.set_column(2, 2, 14)  # Initial Debit
        worksheet.set_column(3, 3, 14)  # Initial Credit
        worksheet.set_column(4, 4, 14)  # Period Debit
        worksheet.set_column(5, 5, 14)  # Period Credit
        worksheet.set_column(6, 6, 14)  # Ending Debit
        worksheet.set_column(7, 7, 14)  # Ending Credit

        headers = ['Code', 'Account Name', 'Init. Debit', 'Init. Credit', 'Period Debit', 'Period Credit', 'End. Debit', 'End. Credit']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        for line in data.get('data', []):
            worksheet.write(row, 0, line.get('account_code', ''), styles.text)
            worksheet.write(row, 1, line.get('account_name', ''), styles.text)
            worksheet.write(row, 2, line.get('initial_debit', 0), styles.currency)
            worksheet.write(row, 3, line.get('initial_credit', 0), styles.currency)
            worksheet.write(row, 4, line.get('period_debit', 0), styles.currency)
            worksheet.write(row, 5, line.get('period_credit', 0), styles.currency)
            worksheet.write(row, 6, line.get('ending_debit', 0), styles.currency)
            worksheet.write(row, 7, line.get('ending_credit', 0), styles.currency)
            row += 1

        totals = data.get('totals', {})
        row += 1
        worksheet.write(row, 0, 'TOTAL', styles.grand_total)
        worksheet.write(row, 1, '', styles.grand_total)
        worksheet.write(row, 2, totals.get('initial_debit', 0), styles.grand_total_currency)
        worksheet.write(row, 3, totals.get('initial_credit', 0), styles.grand_total_currency)
        worksheet.write(row, 4, totals.get('period_debit', 0), styles.grand_total_currency)
        worksheet.write(row, 5, totals.get('period_credit', 0), styles.grand_total_currency)
        worksheet.write(row, 6, totals.get('ending_debit', 0), styles.grand_total_currency)
        worksheet.write(row, 7, totals.get('ending_credit', 0), styles.grand_total_currency)

    def _generate_pl_sheet(self, workbook, worksheet, styles, data):
        """Generate Profit & Loss sheet."""
        row = self._write_header(worksheet, styles, data)

        worksheet.set_column(0, 0, 12)  # Code
        worksheet.set_column(1, 1, 40)  # Name
        worksheet.set_column(2, 2, 15)  # Amount

        # Income Section
        worksheet.merge_range(row, 0, row, 2, 'INCOME', styles.subheader)
        row += 1

        headers = ['Code', 'Account Name', 'Amount']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        sections = data.get('sections', [])
        income_total = 0
        expense_total = 0

        for section in sections:
            section_type = section.get('type', '')
            if 'income' in section_type:
                for acc in section.get('accounts', []):
                    worksheet.write(row, 0, acc.get('account_code', ''), styles.text)
                    worksheet.write(row, 1, acc.get('account_name', ''), styles.text)
                    amount = abs(acc.get('balance', 0))
                    worksheet.write(row, 2, amount, styles.currency_positive)
                    income_total += amount
                    row += 1

        worksheet.write(row, 1, 'Total Income', styles.total)
        worksheet.write(row, 2, income_total, styles.total_currency)
        row += 2

        # Expense Section
        worksheet.merge_range(row, 0, row, 2, 'EXPENSES', styles.subheader)
        row += 1

        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        for section in sections:
            section_type = section.get('type', '')
            if 'expense' in section_type:
                for acc in section.get('accounts', []):
                    worksheet.write(row, 0, acc.get('account_code', ''), styles.text)
                    worksheet.write(row, 1, acc.get('account_name', ''), styles.text)
                    amount = abs(acc.get('balance', 0))
                    worksheet.write(row, 2, amount, styles.currency_negative)
                    expense_total += amount
                    row += 1

        worksheet.write(row, 1, 'Total Expenses', styles.total)
        worksheet.write(row, 2, expense_total, styles.total_currency)
        row += 2

        # Net Profit
        summary = data.get('summary', {})
        net_income = summary.get('net_income', income_total - expense_total)
        worksheet.write(row, 1, 'NET PROFIT / (LOSS)', styles.grand_total)
        net_style = styles.grand_total_currency
        worksheet.write(row, 2, net_income, net_style)

    def _generate_bs_sheet(self, workbook, worksheet, styles, data):
        """Generate Balance Sheet."""
        row = self._write_header(worksheet, styles, data)

        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 40)
        worksheet.set_column(2, 2, 15)

        sections = data.get('sections', [])
        summary = data.get('summary', {})

        # Assets
        worksheet.merge_range(row, 0, row, 2, 'ASSETS', styles.subheader)
        row += 1

        headers = ['Code', 'Account Name', 'Amount']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        asset_total = 0
        for section in sections:
            if section.get('type', '').startswith('asset'):
                for acc in section.get('accounts', []):
                    worksheet.write(row, 0, acc.get('account_code', ''), styles.text)
                    worksheet.write(row, 1, acc.get('account_name', ''), styles.text)
                    worksheet.write(row, 2, acc.get('balance', 0), styles.currency)
                    asset_total += acc.get('balance', 0)
                    row += 1

        worksheet.write(row, 1, 'Total Assets', styles.total)
        worksheet.write(row, 2, summary.get('total_assets', asset_total), styles.total_currency)
        row += 2

        # Liabilities
        worksheet.merge_range(row, 0, row, 2, 'LIABILITIES', styles.subheader)
        row += 1
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        for section in sections:
            if section.get('type', '').startswith('liability'):
                for acc in section.get('accounts', []):
                    worksheet.write(row, 0, acc.get('account_code', ''), styles.text)
                    worksheet.write(row, 1, acc.get('account_name', ''), styles.text)
                    worksheet.write(row, 2, abs(acc.get('balance', 0)), styles.currency)
                    row += 1

        worksheet.write(row, 1, 'Total Liabilities', styles.total)
        worksheet.write(row, 2, summary.get('total_liabilities', 0), styles.total_currency)
        row += 2

        # Equity
        worksheet.merge_range(row, 0, row, 2, 'EQUITY', styles.subheader)
        row += 1
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        for section in sections:
            if section.get('type', '').startswith('equity'):
                for acc in section.get('accounts', []):
                    worksheet.write(row, 0, acc.get('account_code', ''), styles.text)
                    worksheet.write(row, 1, acc.get('account_name', ''), styles.text)
                    worksheet.write(row, 2, abs(acc.get('balance', 0)), styles.currency)
                    row += 1

        worksheet.write(row, 1, 'Total Equity', styles.total)
        worksheet.write(row, 2, summary.get('total_equity', 0), styles.total_currency)

    def _generate_cf_sheet(self, workbook, worksheet, styles, data):
        """Generate Cash Flow sheet."""
        row = self._write_header(worksheet, styles, data)

        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 2, 14)
        worksheet.set_column(3, 3, 14)
        worksheet.set_column(4, 4, 14)

        headers = ['Account', 'Journal', 'Inflow', 'Outflow', 'Net']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        sections = data.get('sections', {})
        for section_name, section_data in sections.items():
            worksheet.merge_range(row, 0, row, 4, section_name.upper(), styles.subheader)
            row += 1

            for line in section_data.get('lines', []):
                worksheet.write(row, 0, line.get('account_code', ''), styles.text)
                worksheet.write(row, 1, line.get('journal_name', ''), styles.text)
                worksheet.write(row, 2, line.get('inflow', 0), styles.currency_positive)
                worksheet.write(row, 3, line.get('outflow', 0), styles.currency_negative)
                worksheet.write(row, 4, line.get('net', 0), styles.get_currency_style(line.get('net', 0)))
                row += 1

            worksheet.write(row, 3, f'Total {section_name}:', styles.total)
            worksheet.write(row, 4, section_data.get('total', 0), styles.total_currency)
            row += 1

        summary = data.get('summary', {})
        row += 1
        worksheet.write(row, 3, 'NET CASH FLOW:', styles.grand_total)
        worksheet.write(row, 4, summary.get('net_change', 0), styles.grand_total_currency)

    def _generate_aged_sheet(self, workbook, worksheet, styles, data):
        """Generate Aged Partner Balance sheet."""
        row = self._write_header(worksheet, styles, data)

        period_labels = data.get('period_labels', {})
        worksheet.set_column(0, 0, 30)
        for i in range(1, 8):
            worksheet.set_column(i, i, 14)

        headers = ['Partner',
                   period_labels.get('current', 'Current'),
                   period_labels.get('period_1', '1-30'),
                   period_labels.get('period_2', '31-60'),
                   period_labels.get('period_3', '61-90'),
                   period_labels.get('period_4', '91-120'),
                   period_labels.get('older', '>120'),
                   'Total']
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, styles.header)
        row += 1

        for line in data.get('data', []):
            worksheet.write(row, 0, line.get('partner_name', ''), styles.text)
            worksheet.write(row, 1, line.get('current', 0), styles.currency)
            worksheet.write(row, 2, line.get('period_1', 0), styles.currency)
            worksheet.write(row, 3, line.get('period_2', 0), styles.currency)
            worksheet.write(row, 4, line.get('period_3', 0), styles.currency)
            worksheet.write(row, 5, line.get('period_4', 0), styles.currency)
            worksheet.write(row, 6, line.get('older', 0), styles.currency)
            worksheet.write(row, 7, line.get('total', 0), styles.get_currency_style(line.get('total', 0)))
            row += 1

        totals = data.get('totals', {})
        row += 1
        worksheet.write(row, 0, 'TOTAL', styles.grand_total)
        worksheet.write(row, 1, totals.get('current', 0), styles.grand_total_currency)
        worksheet.write(row, 2, totals.get('period_1', 0), styles.grand_total_currency)
        worksheet.write(row, 3, totals.get('period_2', 0), styles.grand_total_currency)
        worksheet.write(row, 4, totals.get('period_3', 0), styles.grand_total_currency)
        worksheet.write(row, 5, totals.get('period_4', 0), styles.grand_total_currency)
        worksheet.write(row, 6, totals.get('older', 0), styles.grand_total_currency)
        worksheet.write(row, 7, totals.get('total', 0), styles.grand_total_currency)

    def _generate_partner_sheet(self, workbook, worksheet, styles, data):
        """Generate Partner Ledger sheet."""
        row = self._write_header(worksheet, styles, data)

        worksheet.set_column(0, 0, 30)
        worksheet.set_column(1, 1, 14)
        worksheet.set_column(2, 2, 14)
        worksheet.set_column(3, 3, 14)

        for partner_data in data.get('data', []):
            worksheet.merge_range(row, 0, row, 3, partner_data.get('partner_name', 'Unknown'), styles.subheader)
            row += 1

            headers = ['Date / Entry', 'Debit', 'Credit', 'Balance']
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, styles.header)
            row += 1

            for line in partner_data.get('lines', []):
                worksheet.write(row, 0, f"{line.get('date', '')} - {line.get('move_name', '')}", styles.text)
                worksheet.write(row, 1, line.get('debit', 0), styles.currency)
                worksheet.write(row, 2, line.get('credit', 0), styles.currency)
                worksheet.write(row, 3, line.get('balance', 0), styles.get_currency_style(line.get('balance', 0)))
                row += 1

            worksheet.write(row, 0, 'Partner Total:', styles.total)
            worksheet.write(row, 1, partner_data.get('total_debit', 0), styles.total_currency)
            worksheet.write(row, 2, partner_data.get('total_credit', 0), styles.total_currency)
            worksheet.write(row, 3, partner_data.get('balance', 0), styles.total_currency)
            row += 2

    def _generate_soa_sheet(self, workbook, worksheet, styles, data):
        """Generate Statement of Account sheet."""
        row = self._write_header(worksheet, styles, data)

        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 14)
        worksheet.set_column(4, 4, 14)
        worksheet.set_column(5, 5, 14)

        for statement in data.get('statements', []):
            worksheet.merge_range(row, 0, row, 5, f"Partner: {statement.get('partner_name', '')}", styles.subheader)
            row += 1

            worksheet.write(row, 0, 'Opening Balance:', styles.meta_label)
            worksheet.write(row, 1, statement.get('opening_balance', 0), styles.currency)
            row += 1

            headers = ['Date', 'Entry', 'Description', 'Debit', 'Credit', 'Balance']
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, styles.header)
            row += 1

            for line in statement.get('lines', []):
                worksheet.write(row, 0, line.get('date', ''), styles.text)
                worksheet.write(row, 1, line.get('move_name', ''), styles.text)
                worksheet.write(row, 2, line.get('name', ''), styles.text)
                worksheet.write(row, 3, line.get('debit', 0), styles.currency)
                worksheet.write(row, 4, line.get('credit', 0), styles.currency)
                worksheet.write(row, 5, line.get('balance', 0), styles.get_currency_style(line.get('balance', 0)))
                row += 1

            worksheet.write(row, 4, 'Closing Balance:', styles.grand_total)
            worksheet.write(row, 5, statement.get('closing_balance', 0), styles.grand_total_currency)
            row += 2
