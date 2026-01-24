# -*- coding: utf-8 -*-
"""
OPS Matrix - Centralized Excel Style Factory
=============================================

Provides consistent styling across all XLSX reports.
Use these style definitions instead of defining inline styles.

v19.0.2.5: Phase 5 - Corporate Branding & Visual Polish

Usage:
    from .excel_styles import OPSExcelStyles

    class MyXlsxReport(models.AbstractModel):
        def generate_xlsx_report(self, workbook, data, partners):
            styles = OPSExcelStyles(workbook)

            # Use predefined styles
            worksheet.write(row, col, 'Header', styles.header)
            worksheet.write(row, col, 123.45, styles.currency)
            worksheet.write(row, col, date_val, styles.date)
"""


class OPSExcelStyles:
    """
    Centralized Excel style factory for OPS Matrix reports.

    Corporate color scheme:
    - Primary: #2f6fad (Blue)
    - Header BG: #2f6fad with white text
    - Subheader BG: #E9ECEF (Light gray)
    - Total BG: #e8eef5 (Light blue)
    - Grand Total: #2f6fad (Primary blue)
    - Success: #4CAF50 (Green)
    - Warning: #FF9800 (Orange)
    - Danger: #f44336 (Red)
    """

    # Corporate Color Palette
    COLORS = {
        'primary': '#2f6fad',
        'primary_dark': '#1d4d7a',
        'secondary': '#667eea',
        'accent': '#764ba2',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#f44336',
        'info': '#2196F3',
        'muted': '#6c757d',
        'light': '#f8f9fa',
        'header_bg': '#2f6fad',
        'subheader_bg': '#E9ECEF',
        'total_bg': '#e8eef5',
        'grand_total_bg': '#2f6fad',
        'row_even': '#fafbfc',
        'row_odd': '#ffffff',
        'border': '#dee2e6',
    }

    def __init__(self, workbook):
        """
        Initialize styles for the given workbook.

        Args:
            workbook: xlsxwriter.Workbook instance
        """
        self.workbook = workbook
        self._create_styles()

    def _create_styles(self):
        """Create all standard style formats."""

        # ===========================================
        # HEADER STYLES
        # ===========================================

        # Main report title (merged header row)
        self.title = self.workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': 'white',
            'bg_color': self.COLORS['primary'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.COLORS['primary_dark'],
        })

        # Column headers (table header row)
        self.header = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': 'white',
            'bg_color': self.COLORS['header_bg'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': self.COLORS['primary_dark'],
            'text_wrap': True,
        })

        # Section/Account header
        self.subheader = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'bg_color': self.COLORS['subheader_bg'],
            'border': 1,
            'valign': 'vcenter',
        })

        # ===========================================
        # DATA CELL STYLES
        # ===========================================

        # Standard text cell
        self.text = self.workbook.add_format({
            'font_size': 10,
            'border': 1,
            'valign': 'vcenter',
        })

        # Text centered
        self.text_center = self.workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })

        # Text right-aligned
        self.text_right = self.workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Bold text
        self.text_bold = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'border': 1,
            'valign': 'vcenter',
        })

        # ===========================================
        # NUMBER STYLES
        # ===========================================

        # Currency format (standard)
        self.currency = self.workbook.add_format({
            'font_size': 10,
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Currency positive (green)
        self.currency_positive = self.workbook.add_format({
            'font_size': 10,
            'num_format': '#,##0.00',
            'font_color': self.COLORS['success'],
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Currency negative (red, bold)
        self.currency_negative = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'num_format': '#,##0.00',
            'font_color': self.COLORS['danger'],
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Integer format
        self.integer = self.workbook.add_format({
            'font_size': 10,
            'num_format': '#,##0',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Percentage format
        self.percent = self.workbook.add_format({
            'font_size': 10,
            'num_format': '0.00%',
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # ===========================================
        # DATE STYLES
        # ===========================================

        # Date format (YYYY-MM-DD)
        self.date = self.workbook.add_format({
            'font_size': 10,
            'num_format': 'yyyy-mm-dd',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })

        # Date-time format
        self.datetime = self.workbook.add_format({
            'font_size': 10,
            'num_format': 'yyyy-mm-dd hh:mm',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })

        # ===========================================
        # TOTAL STYLES
        # ===========================================

        # Row total (subtotal)
        self.total = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'bg_color': self.COLORS['total_bg'],
            'border': 1,
            'valign': 'vcenter',
        })

        # Row total with currency
        self.total_currency = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'num_format': '#,##0.00',
            'bg_color': self.COLORS['total_bg'],
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Grand total row
        self.grand_total = self.workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'bg_color': self.COLORS['grand_total_bg'],
            'border': 1,
            'valign': 'vcenter',
        })

        # Grand total currency
        self.grand_total_currency = self.workbook.add_format({
            'bold': True,
            'font_size': 11,
            'num_format': '#,##0.00',
            'font_color': 'white',
            'bg_color': self.COLORS['grand_total_bg'],
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # ===========================================
        # ZEBRA ROW STYLES
        # ===========================================

        # Even row (light background)
        self.row_even = self.workbook.add_format({
            'font_size': 10,
            'bg_color': self.COLORS['row_even'],
            'border': 1,
            'valign': 'vcenter',
        })

        self.row_even_currency = self.workbook.add_format({
            'font_size': 10,
            'num_format': '#,##0.00',
            'bg_color': self.COLORS['row_even'],
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # Odd row (white background)
        self.row_odd = self.workbook.add_format({
            'font_size': 10,
            'bg_color': self.COLORS['row_odd'],
            'border': 1,
            'valign': 'vcenter',
        })

        self.row_odd_currency = self.workbook.add_format({
            'font_size': 10,
            'num_format': '#,##0.00',
            'bg_color': self.COLORS['row_odd'],
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
        })

        # ===========================================
        # STATUS/BADGE STYLES
        # ===========================================

        # Success badge (green)
        self.badge_success = self.workbook.add_format({
            'bold': True,
            'font_size': 9,
            'font_color': 'white',
            'bg_color': self.COLORS['success'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        # Warning badge (orange)
        self.badge_warning = self.workbook.add_format({
            'bold': True,
            'font_size': 9,
            'font_color': 'white',
            'bg_color': self.COLORS['warning'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        # Danger badge (red)
        self.badge_danger = self.workbook.add_format({
            'bold': True,
            'font_size': 9,
            'font_color': 'white',
            'bg_color': self.COLORS['danger'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        # Info badge (blue)
        self.badge_info = self.workbook.add_format({
            'bold': True,
            'font_size': 9,
            'font_color': 'white',
            'bg_color': self.COLORS['info'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        # Muted badge (gray)
        self.badge_muted = self.workbook.add_format({
            'font_size': 9,
            'font_color': 'white',
            'bg_color': self.COLORS['muted'],
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        # ===========================================
        # METADATA STYLES (Report info section)
        # ===========================================

        # Metadata label
        self.meta_label = self.workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': self.COLORS['primary'],
        })

        # Metadata value
        self.meta_value = self.workbook.add_format({
            'font_size': 10,
        })

    # ===========================================
    # HELPER METHODS
    # ===========================================

    def get_currency_style(self, value):
        """
        Return appropriate currency style based on value.

        Args:
            value: Numeric value to format

        Returns:
            xlsxwriter format object
        """
        if value > 0:
            return self.currency_positive
        elif value < 0:
            return self.currency_negative
        else:
            return self.currency

    def get_row_style(self, row_index, is_currency=False):
        """
        Return zebra-striped row style.

        Args:
            row_index: Row number (0-based)
            is_currency: Whether to use currency format

        Returns:
            xlsxwriter format object
        """
        if row_index % 2 == 0:
            return self.row_even_currency if is_currency else self.row_even
        else:
            return self.row_odd_currency if is_currency else self.row_odd

    def get_status_badge(self, status):
        """
        Return badge style based on status string.

        Args:
            status: Status string (success, warning, danger, info, muted)

        Returns:
            xlsxwriter format object
        """
        status_map = {
            'success': self.badge_success,
            'active': self.badge_success,
            'done': self.badge_success,
            'paid': self.badge_success,
            'reconciled': self.badge_success,
            'warning': self.badge_warning,
            'pending': self.badge_warning,
            'partial': self.badge_warning,
            'danger': self.badge_danger,
            'error': self.badge_danger,
            'failed': self.badge_danger,
            'overdue': self.badge_danger,
            'info': self.badge_info,
            'draft': self.badge_info,
        }
        return status_map.get(status.lower(), self.badge_muted)


# ===========================================
# STANDARD COLUMN WIDTHS
# ===========================================

COLUMN_WIDTHS = {
    'date': 12,
    'datetime': 18,
    'code': 15,
    'name': 35,
    'name_short': 25,
    'description': 45,
    'reference': 15,
    'journal': 15,
    'partner': 25,
    'amount': 15,
    'currency': 15,
    'quantity': 12,
    'percentage': 10,
    'status': 12,
    'id': 8,
}


def apply_standard_widths(worksheet, columns):
    """
    Apply standard column widths.

    Args:
        worksheet: xlsxwriter Worksheet instance
        columns: List of column type strings from COLUMN_WIDTHS

    Example:
        apply_standard_widths(worksheet, ['date', 'journal', 'partner', 'name', 'currency', 'currency', 'currency'])
    """
    for col_idx, col_type in enumerate(columns):
        width = COLUMN_WIDTHS.get(col_type, 15)
        worksheet.set_column(col_idx, col_idx, width)
