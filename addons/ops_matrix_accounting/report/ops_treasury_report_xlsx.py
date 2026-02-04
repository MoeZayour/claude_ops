# -*- coding: utf-8 -*-
"""
OPS Matrix - Treasury Intelligence XLSX Export
===============================================

Phase 5: Corporate Excel Structure with Branding
Supports: PDC Registry, Maturity Analysis, PDCs in Hand

Author: OPS Matrix Framework
Version: 19.0.5.0 (Phase 5 - Corporate Design System)
"""

from odoo import models
from odoo.exceptions import UserError
from datetime import datetime
from .excel_styles import get_corporate_excel_formats


class OpsTreasuryReportXlsx(models.AbstractModel):
    """
    Treasury Intelligence XLSX Export for PDC reports.
    Uses Phase 5 corporate Excel structure with dynamic branding.
    """
    _name = 'report.ops_matrix_accounting.report_treasury_xlsx'
    _description = 'Treasury Intelligence XLSX Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizards):
        """
        Generate XLSX report using xlsxwriter with Phase 5 corporate structure.

        Args:
            workbook: xlsxwriter.Workbook instance
            data: Report data dict from wizard
            wizards: Wizard recordset (docids)
        """
        try:
            # Get wizard and ensure data
            wizard = wizards[0] if wizards else None
            if not wizard or not wizard.exists():
                raise UserError("Invalid wizard context for Treasury report export.")

            # Get report data with security checks
            report_data = wizard._get_report_data()
            if not report_data:
                raise UserError("No data available for export.")

            # Get company and corporate formats
            company = wizard.company_id
            formats = get_corporate_excel_formats(workbook, company)

            # Route to appropriate report handler
            report_type = report_data.get('report_type', 'registry')
            handlers = {
                'registry': self._generate_registry_sheet,
                'maturity': self._generate_maturity_sheet,
                'on_hand': self._generate_on_hand_sheet,
            }

            handler = handlers.get(report_type, self._generate_registry_sheet)
            handler(workbook, formats, report_data, company)

        except Exception as e:
            raise UserError(f"Error generating Treasury XLSX report: {str(e)}")

    # ============================================
    # PDC REGISTRY REPORT
    # ============================================

    def _generate_registry_sheet(self, workbook, formats, data, company):
        """Generate PDC Registry sheet with Phase 5 corporate structure."""
        worksheet = workbook.add_worksheet('PDC Registry')

        # Phase 5 Structure:
        # Row 0: Company name
        # Row 1: Report title
        # Row 2: Period/date
        # Row 3: Generated timestamp and user
        # Row 5: Filter bar merged
        # Row 7: Table headers
        # Row 8+: Data with alternating rows

        row = 0

        # Row 0: Company name
        worksheet.merge_range(row, 0, row, 7, company.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        report_title = data.get('report_title', 'PDC Registry Report')
        worksheet.merge_range(row, 0, row, 7, report_title, formats['report_title'])
        row += 1

        # Row 2: Period/date
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        if date_from and date_to:
            period_text = f"Period: {date_from} to {date_to}"
        elif date_from:
            period_text = f"From: {date_from}"
        elif date_to:
            period_text = f"To: {date_to}"
        else:
            period_text = "Period: All dates"
        worksheet.merge_range(row, 0, row, 7, period_text, formats['metadata'])
        row += 1

        # Row 3: Generated timestamp and user
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        user_name = self.env.user.name
        gen_text = f"Generated on {timestamp} by {user_name}"
        worksheet.merge_range(row, 0, row, 7, gen_text, formats['metadata'])
        row += 1

        # Row 4: Blank
        row += 1

        # Row 5: Filter bar merged
        filters = data.get('filters', {})
        filter_parts = []
        if filters.get('branch_count', 0) > 0:
            filter_parts.append(f"{filters['branch_count']} branches")
        if filters.get('partner_count', 0) > 0:
            filter_parts.append(f"{filters['partner_count']} partners")
        if filters.get('state_filter', 'all') != 'all':
            filter_parts.append(f"Status: {filters['state_filter']}")

        filter_text = "Filters: " + (", ".join(filter_parts) if filter_parts else "None")
        worksheet.merge_range(row, 0, row, 7, filter_text, formats['filter_bar'])
        row += 1

        # Row 6: Blank
        row += 1

        # Set column widths
        worksheet.set_column(0, 0, 12)  # Check Number
        worksheet.set_column(1, 1, 12)  # Check Date
        worksheet.set_column(2, 2, 12)  # Maturity Date
        worksheet.set_column(3, 3, 25)  # Partner
        worksheet.set_column(4, 4, 20)  # Bank
        worksheet.set_column(5, 5, 15)  # Branch
        worksheet.set_column(6, 6, 15)  # Amount
        worksheet.set_column(7, 7, 12)  # Status

        # Row 7: Table headers
        headers = ['Check #', 'Check Date', 'Maturity Date', 'Partner', 'Bank', 'Branch', 'Amount', 'Status']
        for col, header in enumerate(headers):
            if col == 6:  # Amount column - right-aligned header
                worksheet.write(row, col, header, formats['table_header_num'])
            else:
                worksheet.write(row, col, header, formats['table_header'])
        row += 1

        # Freeze panes at row 8 (after headers)
        worksheet.freeze_panes(row, 0)

        # Process both inbound and outbound PDCs
        pdc_type = data.get('pdc_type', 'inbound')
        inbound_data = data.get('inbound', {}).get('data', [])
        outbound_data = data.get('outbound', {}).get('data', [])

        data_start_row = row

        # Write inbound PDCs if applicable
        if pdc_type in ('inbound', 'both') and inbound_data:
            # Section header
            worksheet.merge_range(row, 0, row, 7, 'Receivable PDCs (Inbound)', formats['subtotal_label'])
            row += 1

            for pdc in inbound_data:
                alt_row = (row - data_start_row) % 2 == 1
                self._write_pdc_row(worksheet, formats, row, pdc, alt_row)
                row += 1

            # Subtotal
            inbound_total = data.get('inbound', {}).get('total', 0.0)
            inbound_count = data.get('inbound', {}).get('count', 0)
            worksheet.merge_range(row, 0, row, 5, f'Subtotal Receivable ({inbound_count} checks)', formats['subtotal_label'])
            worksheet.write(row, 6, inbound_total, formats['subtotal_number'])
            worksheet.write(row, 7, '', formats['subtotal_label'])
            row += 1

        # Write outbound PDCs if applicable
        if pdc_type in ('outbound', 'both') and outbound_data:
            # Section header
            worksheet.merge_range(row, 0, row, 7, 'Payable PDCs (Outbound)', formats['subtotal_label'])
            row += 1

            for pdc in outbound_data:
                alt_row = (row - data_start_row) % 2 == 1
                self._write_pdc_row(worksheet, formats, row, pdc, alt_row)
                row += 1

            # Subtotal
            outbound_total = data.get('outbound', {}).get('total', 0.0)
            outbound_count = data.get('outbound', {}).get('count', 0)
            worksheet.merge_range(row, 0, row, 5, f'Subtotal Payable ({outbound_count} checks)', formats['subtotal_label'])
            worksheet.write(row, 6, outbound_total, formats['subtotal_number'])
            worksheet.write(row, 7, '', formats['subtotal_label'])
            row += 1

        # Grand total row
        row += 1
        totals = data.get('totals', {})
        total_count = totals.get('total_count', 0)

        if pdc_type == 'both':
            # Show net position for both types
            net_position = totals.get('net_position', 0.0)
            worksheet.merge_range(row, 0, row, 5, f'Net Position ({total_count} total checks)', formats['total_label'])
            worksheet.write(row, 6, net_position, formats['total_number'])
            worksheet.write(row, 7, '', formats['total_label'])
        elif pdc_type == 'inbound':
            inbound_total = totals.get('inbound_total', 0.0)
            worksheet.merge_range(row, 0, row, 5, f'Total Receivable ({total_count} checks)', formats['total_label'])
            worksheet.write(row, 6, inbound_total, formats['total_number'])
            worksheet.write(row, 7, '', formats['total_label'])
        else:  # outbound
            outbound_total = totals.get('outbound_total', 0.0)
            worksheet.merge_range(row, 0, row, 5, f'Total Payable ({total_count} checks)', formats['total_label'])
            worksheet.write(row, 6, outbound_total, formats['total_number'])
            worksheet.write(row, 7, '', formats['total_label'])

        # Set page layout: Landscape, A4, fit to 1 page wide
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.fit_to_pages(1, 0)  # 1 page wide, unlimited height

    def _write_pdc_row(self, worksheet, formats, row, pdc, alt_row=False):
        """Write a single PDC data row with value-based formatting."""
        # Determine formats based on alternating row
        text_fmt = formats['text_alt'] if alt_row else formats['text']

        # Amount formatting based on value
        amount = pdc.get('amount', 0.0)
        if amount > 0:
            amount_fmt = formats['number_alt'] if alt_row else formats['number']
        elif amount < 0:
            amount_fmt = formats['number_negative_alt'] if alt_row else formats['number_negative']
        else:
            amount_fmt = formats['number_zero_alt'] if alt_row else formats['number_zero']

        # Write cells
        worksheet.write(row, 0, pdc.get('check_number', ''), text_fmt)
        worksheet.write(row, 1, pdc.get('check_date', ''), text_fmt)
        worksheet.write(row, 2, pdc.get('maturity_date', ''), text_fmt)
        worksheet.write(row, 3, pdc.get('partner_name', ''), text_fmt)
        worksheet.write(row, 4, pdc.get('bank_name', ''), text_fmt)
        worksheet.write(row, 5, pdc.get('branch_name', ''), text_fmt)
        worksheet.write(row, 6, amount, amount_fmt)
        worksheet.write(row, 7, pdc.get('state_label', ''), text_fmt)

    # ============================================
    # MATURITY ANALYSIS REPORT
    # ============================================

    def _generate_maturity_sheet(self, workbook, formats, data, company):
        """Generate PDC Maturity Analysis sheet with Phase 5 corporate structure."""
        worksheet = workbook.add_worksheet('PDC Maturity Analysis')

        row = 0

        # Row 0: Company name
        worksheet.merge_range(row, 0, row, 4, company.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        report_title = data.get('report_title', 'PDC Maturity Analysis')
        worksheet.merge_range(row, 0, row, 4, report_title, formats['report_title'])
        row += 1

        # Row 2: As of date
        as_of_date = data.get('as_of_date', '')
        worksheet.merge_range(row, 0, row, 4, f"As of Date: {as_of_date}", formats['metadata'])
        row += 1

        # Row 3: Generated timestamp and user
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        user_name = self.env.user.name
        gen_text = f"Generated on {timestamp} by {user_name}"
        worksheet.merge_range(row, 0, row, 4, gen_text, formats['metadata'])
        row += 1

        # Row 4: Blank
        row += 1

        # Row 5: Filter bar
        period_length = data.get('period_length', 30)
        filter_text = f"Period Length: {period_length} days"
        worksheet.merge_range(row, 0, row, 4, filter_text, formats['filter_bar'])
        row += 1

        # Row 6: Blank
        row += 1

        # Set column widths
        worksheet.set_column(0, 0, 25)  # Period
        worksheet.set_column(1, 1, 12)  # Inbound Count
        worksheet.set_column(2, 2, 18)  # Inbound Amount
        worksheet.set_column(3, 3, 12)  # Outbound Count
        worksheet.set_column(4, 4, 18)  # Outbound Amount

        # Row 7: Table headers
        pdc_type = data.get('pdc_type', 'inbound')
        if pdc_type == 'both':
            headers = ['Aging Period', 'Inbound #', 'Inbound Amount', 'Outbound #', 'Outbound Amount']
        elif pdc_type == 'inbound':
            headers = ['Aging Period', 'Count', 'Amount', '', '']
        else:  # outbound
            headers = ['Aging Period', 'Count', 'Amount', '', '']

        for col, header in enumerate(headers):
            if col in (2, 4):  # Amount columns - right-aligned
                worksheet.write(row, col, header, formats['table_header_num'])
            else:
                worksheet.write(row, col, header, formats['table_header'])
        row += 1

        # Freeze panes
        worksheet.freeze_panes(row, 0)

        # Write aging buckets
        aging_buckets = data.get('aging_buckets', [])
        data_start_row = row

        for bucket in aging_buckets:
            alt_row = (row - data_start_row) % 2 == 1
            text_fmt = formats['text_alt'] if alt_row else formats['text']

            worksheet.write(row, 0, bucket.get('label', ''), text_fmt)

            if pdc_type == 'both':
                # Inbound count and amount
                inbound_count = bucket.get('inbound_count', 0)
                inbound_amount = bucket.get('inbound', 0.0)
                worksheet.write(row, 1, inbound_count, text_fmt)
                worksheet.write(row, 2, inbound_amount,
                              formats['number_alt'] if alt_row else formats['number'])

                # Outbound count and amount
                outbound_count = bucket.get('outbound_count', 0)
                outbound_amount = bucket.get('outbound', 0.0)
                worksheet.write(row, 3, outbound_count, text_fmt)
                worksheet.write(row, 4, outbound_amount,
                              formats['number_alt'] if alt_row else formats['number'])
            elif pdc_type == 'inbound':
                count = bucket.get('inbound_count', 0)
                amount = bucket.get('inbound', 0.0)
                worksheet.write(row, 1, count, text_fmt)
                worksheet.write(row, 2, amount,
                              formats['number_alt'] if alt_row else formats['number'])
                worksheet.write(row, 3, '', text_fmt)
                worksheet.write(row, 4, '', text_fmt)
            else:  # outbound
                count = bucket.get('outbound_count', 0)
                amount = bucket.get('outbound', 0.0)
                worksheet.write(row, 1, count, text_fmt)
                worksheet.write(row, 2, amount,
                              formats['number_alt'] if alt_row else formats['number'])
                worksheet.write(row, 3, '', text_fmt)
                worksheet.write(row, 4, '', text_fmt)

            row += 1

        # Grand total row
        row += 1
        totals = data.get('totals', {})

        if pdc_type == 'both':
            worksheet.write(row, 0, 'Total', formats['total_label'])
            worksheet.write(row, 1, '', formats['total_label'])
            worksheet.write(row, 2, totals.get('inbound_total', 0.0), formats['total_number'])
            worksheet.write(row, 3, '', formats['total_label'])
            worksheet.write(row, 4, totals.get('outbound_total', 0.0), formats['total_number'])
        elif pdc_type == 'inbound':
            worksheet.merge_range(row, 0, row, 1, 'Total Receivable', formats['total_label'])
            worksheet.write(row, 2, totals.get('inbound_total', 0.0), formats['total_number'])
            worksheet.write(row, 3, '', formats['total_label'])
            worksheet.write(row, 4, '', formats['total_label'])
        else:  # outbound
            worksheet.merge_range(row, 0, row, 1, 'Total Payable', formats['total_label'])
            worksheet.write(row, 2, totals.get('outbound_total', 0.0), formats['total_number'])
            worksheet.write(row, 3, '', formats['total_label'])
            worksheet.write(row, 4, '', formats['total_label'])

        # Set page layout
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.fit_to_pages(1, 0)

    # ============================================
    # PDCs IN HAND REPORT
    # ============================================

    def _generate_on_hand_sheet(self, workbook, formats, data, company):
        """Generate PDCs in Hand sheet with Phase 5 corporate structure."""
        # Reuse registry structure for on-hand (same columns, filtered data)
        worksheet = workbook.add_worksheet('PDCs in Hand')

        row = 0

        # Row 0: Company name
        worksheet.merge_range(row, 0, row, 7, company.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        report_title = data.get('report_title', 'PDCs in Hand Report')
        worksheet.merge_range(row, 0, row, 7, report_title, formats['report_title'])
        row += 1

        # Row 2: As of date
        as_of_date = data.get('as_of_date', '')
        worksheet.merge_range(row, 0, row, 7, f"As of Date: {as_of_date}", formats['metadata'])
        row += 1

        # Row 3: Generated timestamp and user
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        user_name = self.env.user.name
        gen_text = f"Generated on {timestamp} by {user_name}"
        worksheet.merge_range(row, 0, row, 7, gen_text, formats['metadata'])
        row += 1

        # Row 4: Blank
        row += 1

        # Row 5: Filter bar
        group_by = data.get('group_by', 'none')
        filter_text = f"Grouping: {group_by.replace('_', ' ').title()}"
        worksheet.merge_range(row, 0, row, 7, filter_text, formats['filter_bar'])
        row += 1

        # Row 6: Blank
        row += 1

        # Set column widths (same as registry)
        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(4, 4, 20)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 12)

        # Row 7: Table headers
        headers = ['Check #', 'Check Date', 'Maturity Date', 'Partner', 'Bank', 'Branch', 'Amount', 'Status']
        for col, header in enumerate(headers):
            if col == 6:
                worksheet.write(row, col, header, formats['table_header_num'])
            else:
                worksheet.write(row, col, header, formats['table_header'])
        row += 1

        # Freeze panes
        worksheet.freeze_panes(row, 0)

        # Process PDCs (only open/in-hand ones)
        pdc_type = data.get('pdc_type', 'inbound')
        inbound_data = data.get('inbound', {}).get('data', [])
        outbound_data = data.get('outbound', {}).get('data', [])

        data_start_row = row

        # Write inbound PDCs
        if pdc_type in ('inbound', 'both') and inbound_data:
            worksheet.merge_range(row, 0, row, 7, 'Receivable PDCs in Hand', formats['subtotal_label'])
            row += 1

            for pdc in inbound_data:
                alt_row = (row - data_start_row) % 2 == 1
                self._write_pdc_row(worksheet, formats, row, pdc, alt_row)
                row += 1

            # Subtotal
            inbound_total = data.get('inbound', {}).get('total', 0.0)
            inbound_count = data.get('inbound', {}).get('count', 0)
            worksheet.merge_range(row, 0, row, 5, f'Subtotal Receivable ({inbound_count} checks)', formats['subtotal_label'])
            worksheet.write(row, 6, inbound_total, formats['subtotal_number'])
            worksheet.write(row, 7, '', formats['subtotal_label'])
            row += 1

        # Write outbound PDCs
        if pdc_type in ('outbound', 'both') and outbound_data:
            worksheet.merge_range(row, 0, row, 7, 'Payable PDCs in Hand', formats['subtotal_label'])
            row += 1

            for pdc in outbound_data:
                alt_row = (row - data_start_row) % 2 == 1
                self._write_pdc_row(worksheet, formats, row, pdc, alt_row)
                row += 1

            # Subtotal
            outbound_total = data.get('outbound', {}).get('total', 0.0)
            outbound_count = data.get('outbound', {}).get('count', 0)
            worksheet.merge_range(row, 0, row, 5, f'Subtotal Payable ({outbound_count} checks)', formats['subtotal_label'])
            worksheet.write(row, 6, outbound_total, formats['subtotal_number'])
            worksheet.write(row, 7, '', formats['subtotal_label'])
            row += 1

        # Grand total
        row += 1
        totals = data.get('totals', {})
        total_count = totals.get('total_count', 0)

        if pdc_type == 'both':
            net_position = totals.get('net_position', 0.0)
            worksheet.merge_range(row, 0, row, 5, f'Net Position ({total_count} checks in hand)', formats['total_label'])
            worksheet.write(row, 6, net_position, formats['total_number'])
            worksheet.write(row, 7, '', formats['total_label'])
        elif pdc_type == 'inbound':
            inbound_total = totals.get('inbound_total', 0.0)
            worksheet.merge_range(row, 0, row, 5, f'Total Receivable ({total_count} checks in hand)', formats['total_label'])
            worksheet.write(row, 6, inbound_total, formats['total_number'])
            worksheet.write(row, 7, '', formats['total_label'])
        else:  # outbound
            outbound_total = totals.get('outbound_total', 0.0)
            worksheet.merge_range(row, 0, row, 5, f'Total Payable ({total_count} checks in hand)', formats['total_label'])
            worksheet.write(row, 6, outbound_total, formats['total_number'])
            worksheet.write(row, 7, '', formats['total_label'])

        # Set page layout
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.fit_to_pages(1, 0)
