# -*- coding: utf-8 -*-
"""
General Ledger XLSX Export
==========================

Uses centralized OPSExcelStyles for consistent branding.
v19.0.2.5: Phase 5 - Applied corporate branding via excel_styles.
"""

from odoo import models
from odoo.exceptions import UserError
from .excel_styles import OPSExcelStyles, COLUMN_WIDTHS, apply_standard_widths


class OpsGeneralLedgerXlsx(models.AbstractModel):
    """
    General Ledger XLSX Export.
    Uses in-memory generation to maintain "Zero DB Bloat" design.
    """
    _name = 'report.ops_matrix_accounting.report_general_ledger_xlsx'
    _description = 'General Ledger XLSX Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        """
        Generate XLSX report using xlsxwriter.

        Args:
            workbook: xlsxwriter.Workbook instance
            data: Report data dict from wizard
            partners: Wizard recordset (docids)
        """
        try:
            # Initialize centralized styles
            styles = OPSExcelStyles(workbook)

            # Get report data from the parser
            report_parser = self.env['report.ops_matrix_accounting.report_general_ledger']
            report_values = report_parser._get_report_values(partners.ids, data)

            # Create worksheet
            worksheet = workbook.add_worksheet('General Ledger')

            # Apply standard column widths
            apply_standard_widths(worksheet, [
                'date', 'journal', 'partner', 'name', 'reference',
                'currency', 'currency', 'currency'
            ])

            # Write report header
            row = 0
            worksheet.merge_range(row, 0, row, 7, 'GENERAL LEDGER REPORT', styles.title)
            row += 1

            # Write metadata section
            company = report_values.get('company')
            worksheet.write(row, 0, 'Company:', styles.meta_label)
            worksheet.write(row, 1, company.name if company else '', styles.meta_value)
            row += 1

            worksheet.write(row, 0, 'Period:', styles.meta_label)
            period_text = f"{data.get('date_from', '')} to {data.get('date_to', '')}"
            worksheet.write(row, 1, period_text, styles.meta_value)
            row += 1

            worksheet.write(row, 0, 'Target Moves:', styles.meta_label)
            worksheet.write(row, 1, data.get('target_move', 'posted'), styles.meta_value)
            row += 2

            # Process accounts
            accounts = report_values.get('accounts', [])

            for account in accounts:
                # Account header
                account_title = f"{account['account_code']} - {account['account_name']}"
                worksheet.merge_range(row, 0, row, 7, account_title, styles.subheader)
                row += 1

                # Column headers
                headers = ['Date', 'Journal', 'Partner', 'Label', 'Reference', 'Debit', 'Credit', 'Balance']
                for col, header in enumerate(headers):
                    worksheet.write(row, col, header, styles.header)
                row += 1

                # Account lines with zebra striping
                line_start_row = row
                for line_idx, line in enumerate(account.get('lines', [])):
                    text_style = styles.get_row_style(line_idx, is_currency=False)
                    currency_style = styles.get_row_style(line_idx, is_currency=True)

                    worksheet.write(row, 0, line['move_date'], styles.date)
                    worksheet.write(row, 1, line['journal'], text_style)
                    worksheet.write(row, 2, line['partner'] or '-', text_style)
                    worksheet.write(row, 3, line['label'], text_style)
                    worksheet.write(row, 4, line['reference'] or '-', text_style)

                    # Debit with conditional color
                    debit_style = styles.currency_positive if line['debit'] > 0 else styles.currency
                    worksheet.write(row, 5, line['debit'], debit_style)

                    # Credit with conditional color
                    credit_style = styles.currency_negative if line['credit'] > 0 else styles.currency
                    worksheet.write(row, 6, line['credit'], credit_style)

                    # Balance with conditional color
                    balance_style = styles.get_currency_style(line['balance'])
                    worksheet.write(row, 7, line['balance'], balance_style)
                    row += 1

                # Account totals
                worksheet.write(row, 4, 'Account Total:', styles.total)
                worksheet.write(row, 5, account['total_debit'], styles.total_currency)
                worksheet.write(row, 6, account['total_credit'], styles.total_currency)
                worksheet.write(row, 7, account['total_balance'], styles.total_currency)
                row += 2

            # Grand totals
            grand_total = report_values.get('grand_total', {})
            worksheet.merge_range(row, 0, row, 4, 'GRAND TOTAL', styles.grand_total)
            worksheet.write(row, 5, grand_total.get('debit', 0.0), styles.grand_total_currency)
            worksheet.write(row, 6, grand_total.get('credit', 0.0), styles.grand_total_currency)
            worksheet.write(row, 7, grand_total.get('balance', 0.0), styles.grand_total_currency)
            row += 2

            # Balance verification row
            balance_check = abs(grand_total.get('debit', 0) - grand_total.get('credit', 0))
            if balance_check < 0.01:
                worksheet.merge_range(
                    row, 0, row, 7,
                    'Books Balanced: Debits equal credits. Ledger is in balance.',
                    styles.badge_success
                )
            else:
                worksheet.merge_range(
                    row, 0, row, 7,
                    f'Balance Difference: {balance_check:.2f} - Review required.',
                    styles.badge_warning
                )
            row += 2

            # Footer
            worksheet.merge_range(
                row, 0, row, 7,
                'Generated by OPS Matrix | All data sourced from posted journal entries',
                styles.meta_value
            )

        except Exception as e:
            raise UserError(f"Error generating XLSX report: {str(e)}")

    def _get_objs_for_report(self, docids, data):
        """
        Override to provide wizard data to the report.
        This method is called by the abstract XLSX report class.
        """
        if data:
            return self.env['ops.general.ledger.wizard'].browse(docids)
        return self.env['ops.general.ledger.wizard']
