# -*- coding: utf-8 -*-
"""
OPS Matrix - Asset Intelligence Excel Export
=============================================

Phase 5 Corporate Excel Implementation - Asset Register

Supports all 4 Asset Intelligence reports:
- Asset Register (with NBV as of date)
- Depreciation Forecast (future depreciation schedule)
- Disposal Analysis (asset movements & disposals)
- Asset Movement (additions in period)

v19.0.5.0: Phase 5 - Corporate design system applied
"""

from odoo import models
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AssetIntelligenceXLSX(models.AbstractModel):
    """
    Asset Intelligence XLSX Report Generator.

    Generates corporate-branded Excel reports for Asset Intelligence engine.
    Uses Phase 5 corporate format structure with company branding.
    """
    _name = 'report.ops_matrix_accounting.report_asset_xlsx'
    _inherit = 'ops.xlsx.abstract'
    _description = 'Asset Intelligence Excel Report'
    _report_model = 'ops.asset.report.wizard'

    def generate_xlsx_report(self, workbook, data, wizards):
        """
        Generate Asset Intelligence XLSX report.

        Args:
            workbook: xlsxwriter workbook object
            data: Report data dictionary from wizard
            wizards: Wizard recordset (ops.asset.report.wizard)
        """
        self.ensure_one()
        wizard = wizards[0] if wizards else self.env['ops.asset.report.wizard'].browse(data.get('wizard_id'))

        # Import corporate formats
        from .excel_styles import get_corporate_excel_formats
        formats = get_corporate_excel_formats(workbook, wizard.company_id)

        # Dispatch to appropriate report generator
        report_type = data.get('report_type', 'register')

        if report_type == 'register':
            self._generate_asset_register(workbook, data, wizard, formats)
        elif report_type == 'forecast':
            self._generate_depreciation_forecast(workbook, data, wizard, formats)
        elif report_type == 'disposal':
            self._generate_disposal_analysis(workbook, data, wizard, formats)
        elif report_type == 'movement':
            self._generate_asset_movement(workbook, data, wizard, formats)
        else:
            self._generate_asset_register(workbook, data, wizard, formats)

    # ============================================
    # ASSET REGISTER REPORT
    # ============================================

    def _generate_asset_register(self, workbook, data, wizard, formats):
        """Generate Asset Register Excel report (Phase 5 corporate structure)."""
        sheet = workbook.add_worksheet('Asset Register')

        # Column definitions
        columns = [
            ('Asset Code', 15),
            ('Asset Name', 35),
            ('Category', 20),
            ('Branch', 15),
            ('Purchase Date', 12),
            ('Purchase Value', 16),
            ('Salvage Value', 16),
            ('Accum. Depreciation', 16),
            ('Net Book Value', 16),
            ('Status', 12),
        ]

        # Set column widths
        for col_idx, (_, width) in enumerate(columns):
            sheet.set_column(col_idx, col_idx, width)

        row = 0

        # Row 0: Company Name
        sheet.merge_range(row, 0, row, len(columns) - 1, wizard.company_id.name, formats['company_name'])
        sheet.set_row(row, 20)
        row += 1

        # Row 1: Report Title
        report_title = data.get('report_title', 'Fixed Asset Register')
        sheet.merge_range(row, 0, row, len(columns) - 1, report_title, formats['report_title'])
        sheet.set_row(row, 18)
        row += 1

        # Row 2: As of Date
        as_of_date = data.get('as_of_date', wizard.as_of_date or datetime.now().date())
        sheet.merge_range(row, 0, row, len(columns) - 1, f"As of: {as_of_date}", formats['metadata'])
        row += 1

        # Row 3: Generated timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        generated_by = self.env.user.name
        sheet.merge_range(row, 0, row, len(columns) - 1,
                         f"Generated: {timestamp} by {generated_by}", formats['metadata'])
        row += 1

        # Row 4: Empty
        row += 1

        # Row 5: Filter bar
        filter_parts = []
        filters = data.get('filters', {})
        if filters.get('branch_count'):
            filter_parts.append(f"Branches: {filters['branch_count']}")
        if filters.get('category_count'):
            filter_parts.append(f"Categories: {filters['category_count']}")
        if filters.get('asset_state') != 'all':
            filter_parts.append(f"Status: {filters['asset_state']}")

        filter_text = ' | '.join(filter_parts) if filter_parts else 'All Assets'
        sheet.merge_range(row, 0, row, len(columns) - 1, f"Filters: {filter_text}", formats['filter_bar'])
        row += 1

        # Row 6: Empty
        row += 1

        # Row 7: Table headers
        for col_idx, (header, _) in enumerate(columns):
            if col_idx >= 5:  # Number columns
                sheet.write(row, col_idx, header, formats['table_header_num'])
            else:
                sheet.write(row, col_idx, header, formats['table_header'])
        header_row = row
        row += 1

        # Data rows
        assets = data.get('data', [])
        totals = data.get('totals', {})

        data_start_row = row
        for idx, asset in enumerate(assets):
            alt = idx % 2 == 1

            # Asset Code
            sheet.write(row, 0, asset.get('code', ''), formats['text_alt'] if alt else formats['text'])

            # Asset Name
            sheet.write(row, 1, asset.get('name', ''), formats['text_alt'] if alt else formats['text'])

            # Category
            sheet.write(row, 2, asset.get('category_name', ''), formats['text_alt'] if alt else formats['text'])

            # Branch
            sheet.write(row, 3, asset.get('branch_name', ''), formats['text_alt'] if alt else formats['text'])

            # Purchase Date
            sheet.write(row, 4, asset.get('purchase_date', ''), formats['text_alt'] if alt else formats['text'])

            # Purchase Value
            purchase_val = asset.get('purchase_value', 0.0)
            fmt = self._get_number_format(purchase_val, alt, formats)
            sheet.write_number(row, 5, purchase_val, fmt)

            # Salvage Value
            salvage_val = asset.get('salvage_value', 0.0)
            fmt = self._get_number_format(salvage_val, alt, formats)
            sheet.write_number(row, 6, salvage_val, fmt)

            # Accumulated Depreciation
            accum_dep = asset.get('accumulated_depreciation', 0.0)
            fmt = self._get_number_format(accum_dep, alt, formats)
            sheet.write_number(row, 7, accum_dep, fmt)

            # Net Book Value
            nbv = asset.get('book_value', 0.0)
            fmt = self._get_number_format(nbv, alt, formats)
            sheet.write_number(row, 8, nbv, fmt)

            # Status
            sheet.write(row, 9, asset.get('state_label', ''), formats['text_alt'] if alt else formats['text'])

            row += 1

        # Grand Total row
        sheet.write(row, 0, 'GRAND TOTAL', formats['total_label'])
        sheet.write(row, 1, '', formats['total_label'])
        sheet.write(row, 2, '', formats['total_label'])
        sheet.write(row, 3, '', formats['total_label'])
        sheet.write(row, 4, f"{totals.get('asset_count', 0)} Assets", formats['total_label'])
        sheet.write_number(row, 5, totals.get('total_gross_value', 0.0), formats['total_number'])
        sheet.write(row, 6, '', formats['total_number'])
        sheet.write_number(row, 7, totals.get('total_accumulated_depreciation', 0.0), formats['total_number'])
        sheet.write_number(row, 8, totals.get('total_net_book_value', 0.0), formats['total_number'])
        sheet.write(row, 9, '', formats['total_label'])

        # Freeze panes at header row
        sheet.freeze_panes(header_row + 1, 0)

        # Page setup
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.fit_to_pages(1, 0)  # Fit to 1 page wide

    # ============================================
    # DEPRECIATION FORECAST REPORT
    # ============================================

    def _generate_depreciation_forecast(self, workbook, data, wizard, formats):
        """Generate Depreciation Forecast Excel report."""
        sheet = workbook.add_worksheet('Depreciation Forecast')

        columns = [
            ('Date', 12),
            ('Asset Code', 15),
            ('Asset Name', 35),
            ('Category', 20),
            ('Branch', 15),
            ('Amount', 16),
            ('Status', 12),
        ]

        for col_idx, (_, width) in enumerate(columns):
            sheet.set_column(col_idx, col_idx, width)

        row = 0

        # Header rows (Phase 5 structure)
        sheet.merge_range(row, 0, row, len(columns) - 1, wizard.company_id.name, formats['company_name'])
        sheet.set_row(row, 20)
        row += 1

        sheet.merge_range(row, 0, row, len(columns) - 1,
                         data.get('report_title', 'Depreciation Forecast'), formats['report_title'])
        sheet.set_row(row, 18)
        row += 1

        date_range = f"Period: {data.get('date_from', '')} to {data.get('date_to', '')}"
        sheet.merge_range(row, 0, row, len(columns) - 1, date_range, formats['metadata'])
        row += 1

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.merge_range(row, 0, row, len(columns) - 1,
                         f"Generated: {timestamp} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        # Filter bar
        filters = data.get('filters', {})
        filter_text = f"State: {filters.get('depreciation_state', 'all')}"
        sheet.merge_range(row, 0, row, len(columns) - 1, f"Filters: {filter_text}", formats['filter_bar'])
        row += 1
        row += 1

        # Table headers
        for col_idx, (header, _) in enumerate(columns):
            if col_idx == 5:  # Amount column
                sheet.write(row, col_idx, header, formats['table_header_num'])
            else:
                sheet.write(row, col_idx, header, formats['table_header'])
        header_row = row
        row += 1

        # Data rows
        dep_lines = data.get('data', [])
        totals = data.get('totals', {})

        for idx, line in enumerate(dep_lines):
            alt = idx % 2 == 1

            sheet.write(row, 0, line.get('depreciation_date', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 1, line.get('asset_code', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 2, line.get('asset_name', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 3, line.get('category_name', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 4, line.get('branch_name', ''), formats['text_alt'] if alt else formats['text'])

            amount = line.get('amount', 0.0)
            fmt = self._get_number_format(amount, alt, formats)
            sheet.write_number(row, 5, amount, fmt)

            sheet.write(row, 6, line.get('state_label', ''), formats['text_alt'] if alt else formats['text'])
            row += 1

        # Grand Total
        sheet.write(row, 0, 'GRAND TOTAL', formats['total_label'])
        for col_idx in range(1, 5):
            sheet.write(row, col_idx, '', formats['total_label'])
        sheet.write_number(row, 5, totals.get('total_depreciation', 0.0), formats['total_number'])
        sheet.write(row, 6, f"{totals.get('line_count', 0)} entries", formats['total_label'])

        sheet.freeze_panes(header_row + 1, 0)
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.fit_to_pages(1, 0)

    # ============================================
    # DISPOSAL ANALYSIS REPORT
    # ============================================

    def _generate_disposal_analysis(self, workbook, data, wizard, formats):
        """Generate Asset Disposal Analysis Excel report."""
        sheet = workbook.add_worksheet('Disposal Analysis')

        columns = [
            ('Asset Code', 15),
            ('Asset Name', 35),
            ('Category', 20),
            ('Disposal Date', 12),
            ('Purchase Value', 16),
            ('Accum. Depreciation', 16),
            ('NBV at Disposal', 16),
            ('Holding Days', 12),
        ]

        for col_idx, (_, width) in enumerate(columns):
            sheet.set_column(col_idx, col_idx, width)

        row = 0

        # Header rows
        sheet.merge_range(row, 0, row, len(columns) - 1, wizard.company_id.name, formats['company_name'])
        sheet.set_row(row, 20)
        row += 1

        sheet.merge_range(row, 0, row, len(columns) - 1,
                         data.get('report_title', 'Asset Disposal Analysis'), formats['report_title'])
        sheet.set_row(row, 18)
        row += 1

        date_range = f"Period: {data.get('date_from', '')} to {data.get('date_to', '')}"
        sheet.merge_range(row, 0, row, len(columns) - 1, date_range, formats['metadata'])
        row += 1

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.merge_range(row, 0, row, len(columns) - 1,
                         f"Generated: {timestamp} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        sheet.merge_range(row, 0, row, len(columns) - 1,
                         "Filters: Closed Assets (Sold/Disposed)", formats['filter_bar'])
        row += 1
        row += 1

        # Table headers
        for col_idx, (header, _) in enumerate(columns):
            if col_idx >= 4:  # Number columns
                sheet.write(row, col_idx, header, formats['table_header_num'])
            else:
                sheet.write(row, col_idx, header, formats['table_header'])
        header_row = row
        row += 1

        # Data rows
        disposals = data.get('data', [])
        totals = data.get('totals', {})

        for idx, asset in enumerate(disposals):
            alt = idx % 2 == 1

            sheet.write(row, 0, asset.get('code', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 1, asset.get('name', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 2, asset.get('category_name', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 3, asset.get('disposal_date', ''), formats['text_alt'] if alt else formats['text'])

            purchase = asset.get('purchase_value', 0.0)
            fmt = self._get_number_format(purchase, alt, formats)
            sheet.write_number(row, 4, purchase, fmt)

            accum = asset.get('accumulated_depreciation', 0.0)
            fmt = self._get_number_format(accum, alt, formats)
            sheet.write_number(row, 5, accum, fmt)

            nbv = asset.get('book_value_at_disposal', 0.0)
            fmt = self._get_number_format(nbv, alt, formats)
            sheet.write_number(row, 6, nbv, fmt)

            days = asset.get('holding_period_days', 0)
            sheet.write_number(row, 7, days, formats['number_alt'] if alt else formats['number'])
            row += 1

        # Grand Total
        sheet.write(row, 0, 'GRAND TOTAL', formats['total_label'])
        sheet.write(row, 1, '', formats['total_label'])
        sheet.write(row, 2, '', formats['total_label'])
        sheet.write(row, 3, f"{totals.get('total_count', 0)} Assets", formats['total_label'])
        sheet.write_number(row, 4, totals.get('total_gross_value', 0.0), formats['total_number'])
        sheet.write(row, 5, '', formats['total_number'])
        sheet.write_number(row, 6, totals.get('total_nbv_at_disposal', 0.0), formats['total_number'])
        sheet.write(row, 7, '', formats['total_number'])

        sheet.freeze_panes(header_row + 1, 0)
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.fit_to_pages(1, 0)

    # ============================================
    # ASSET MOVEMENT REPORT
    # ============================================

    def _generate_asset_movement(self, workbook, data, wizard, formats):
        """Generate Asset Movement Excel report (additions in period)."""
        sheet = workbook.add_worksheet('Asset Movement')

        columns = [
            ('Purchase Date', 12),
            ('Asset Code', 15),
            ('Asset Name', 35),
            ('Category', 20),
            ('Branch', 15),
            ('Purchase Value', 16),
            ('Useful Life (Years)', 12),
        ]

        for col_idx, (_, width) in enumerate(columns):
            sheet.set_column(col_idx, col_idx, width)

        row = 0

        # Header rows
        sheet.merge_range(row, 0, row, len(columns) - 1, wizard.company_id.name, formats['company_name'])
        sheet.set_row(row, 20)
        row += 1

        sheet.merge_range(row, 0, row, len(columns) - 1,
                         data.get('report_title', 'Asset Movement Report'), formats['report_title'])
        sheet.set_row(row, 18)
        row += 1

        date_range = f"Period: {data.get('date_from', '')} to {data.get('date_to', '')}"
        sheet.merge_range(row, 0, row, len(columns) - 1, date_range, formats['metadata'])
        row += 1

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.merge_range(row, 0, row, len(columns) - 1,
                         f"Generated: {timestamp} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        sheet.merge_range(row, 0, row, len(columns) - 1,
                         "Filters: Asset Additions in Period", formats['filter_bar'])
        row += 1
        row += 1

        # Table headers
        for col_idx, (header, _) in enumerate(columns):
            if col_idx >= 5:  # Number columns
                sheet.write(row, col_idx, header, formats['table_header_num'])
            else:
                sheet.write(row, col_idx, header, formats['table_header'])
        header_row = row
        row += 1

        # Data rows
        movements = data.get('data', [])
        totals = data.get('totals', {})

        for idx, asset in enumerate(movements):
            alt = idx % 2 == 1

            sheet.write(row, 0, asset.get('purchase_date', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 1, asset.get('code', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 2, asset.get('name', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 3, asset.get('category_name', ''), formats['text_alt'] if alt else formats['text'])
            sheet.write(row, 4, asset.get('branch_name', ''), formats['text_alt'] if alt else formats['text'])

            purchase = asset.get('purchase_value', 0.0)
            fmt = self._get_number_format(purchase, alt, formats)
            sheet.write_number(row, 5, purchase, fmt)

            life = asset.get('useful_life_years', 0)
            sheet.write_number(row, 6, life, formats['number_alt'] if alt else formats['number'])
            row += 1

        # Grand Total
        sheet.write(row, 0, 'GRAND TOTAL', formats['total_label'])
        sheet.write(row, 1, '', formats['total_label'])
        sheet.write(row, 2, '', formats['total_label'])
        sheet.write(row, 3, '', formats['total_label'])
        sheet.write(row, 4, f"{totals.get('additions_count', 0)} Additions", formats['total_label'])
        sheet.write_number(row, 5, totals.get('total_additions_value', 0.0), formats['total_number'])
        sheet.write(row, 6, '', formats['total_number'])

        sheet.freeze_panes(header_row + 1, 0)
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.fit_to_pages(1, 0)

    # ============================================
    # HELPER METHODS
    # ============================================

    def _get_number_format(self, value, is_alt_row, formats):
        """
        Get appropriate number format based on value and row type.

        Args:
            value: Numeric value
            is_alt_row: Boolean indicating alternating row
            formats: Format dictionary

        Returns:
            xlsxwriter format object
        """
        if value < 0:
            return formats['number_negative_alt'] if is_alt_row else formats['number_negative']
        elif value == 0:
            return formats['number_zero_alt'] if is_alt_row else formats['number_zero']
        else:
            return formats['number_alt'] if is_alt_row else formats['number']
