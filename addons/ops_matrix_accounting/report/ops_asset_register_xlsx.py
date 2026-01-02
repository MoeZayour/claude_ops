# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from datetime import datetime

class AssetRegisterXLSX(models.AbstractModel):
    """
    This model generates an XLSX report for the asset register, providing a detailed
    overview of all company assets, their valuation, depreciation, and status.
    It inherits from 'report.report_xlsx.abstract' to leverage Odoo's XLSX reporting
    capabilities.
    """
    _name = 'report.ops_matrix_accounting.report_asset_register_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Asset Register XLSX Report'

    def generate_xlsx_report(self, workbook, data, assets):
        """
        Generates the XLSX report content.

        Args:
            workbook: The XLSX workbook object.
            data (dict): Data passed from the wizard or report action.
            assets (recordset): The 'ops.asset' recordset to be reported on.
        """
        sheet = workbook.add_worksheet('Asset Register')

        # Define styles
        title_style = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
        header_style = workbook.add_format({'bold': True, 'bg_color': '#E0E0E0', 'border': 1, 'align': 'center'})
        cell_style = workbook.add_format({'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        bold_style = workbook.add_format({'bold': True})

        # Set column widths for better readability
        sheet.set_column('A:A', 35)  # Asset Name
        sheet.set_column('B:B', 20)  # Asset Code
        sheet.set_column('C:C', 25)  # Category
        sheet.set_column('D:D', 15)  # Purchase Date
        sheet.set_column('E:E', 15)  # Purchase Value
        sheet.set_column('F:F', 22)  # Depreciation Start Date
        sheet.set_column('G:G', 15)  # Book Value
        sheet.set_column('H:H', 15)  # Status

        # Report Title and Generation Time
        sheet.merge_range('A1:H1', 'Asset Register Report', title_style)
        sheet.write('A2', f"Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", bold_style)

        # Table Headers
        headers = [
            'Asset Name', 'Asset Code', 'Category', 'Purchase Date',
            'Purchase Value', 'Depreciation Start Date', 'Book Value', 'Status'
        ]
        for col_num, header in enumerate(headers):
            sheet.write(3, col_num, header, header_style)

        # Data Rows
        row_num = 4
        for asset in assets:
            state_label = dict(asset._fields['state'].selection).get(asset.state, '')
            
            sheet.write(row_num, 0, asset.name or '', cell_style)
            sheet.write(row_num, 1, asset.code or '', cell_style)
            sheet.write(row_num, 2, asset.category_id.name or '', cell_style)
            sheet.write(row_num, 3, asset.purchase_date, date_format)
            sheet.write(row_num, 4, asset.purchase_value, money_format)
            sheet.write(row_num, 5, asset.depreciation_start_date, date_format)
            sheet.write(row_num, 6, asset.book_value, money_format)
            sheet.write(row_num, 7, state_label, cell_style)
            row_num += 1
