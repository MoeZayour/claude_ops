# -*- coding: utf-8 -*-
"""
OPS Matrix - Centralized Excel Style Factory
=============================================

Provides consistent styling across all XLSX reports.
Use these style definitions instead of defining inline styles.

v19.0.4.0: Phase 5 - Corporate Design System (BEM Architecture)

Color Palette (matching CSS Design Tokens):
    --ops-primary: #0056b3 (Corporate Blue)
    --ops-secondary: #f8f9fa (Light Background)
    --ops-danger: #dc3545 (Negative/Warning)
    --ops-success: #28a745 (Positive/Success)

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

    Corporate color scheme (BEM Design System):
    - Primary: #0056b3 (Corporate Blue)
    - Primary Dark: #004494
    - Header BG: #0056b3 with white text
    - Subheader BG: #e9ecef (Light gray)
    - Total BG: #e7f1ff (Primary light)
    - Grand Total: #0056b3 (Primary blue)
    - Success: #28a745 (Green)
    - Warning: #ffc107 (Yellow/Orange)
    - Danger: #dc3545 (Red)
    - Info: #17a2b8 (Teal)
    """

    # Corporate Color Palette (matching CSS Design Tokens)
    COLORS = {
        'primary': '#0056b3',
        'primary_dark': '#004494',
        'primary_light': '#e7f1ff',
        'secondary': '#f8f9fa',
        'secondary_dark': '#e9ecef',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'muted': '#6c757d',
        'dark': '#343a40',
        'light': '#f8f9fa',
        'white': '#ffffff',
        'header_bg': '#0056b3',
        'subheader_bg': '#e9ecef',
        'total_bg': '#e7f1ff',
        'grand_total_bg': '#0056b3',
        'row_even': '#f8f9fa',
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


# ===========================================
# CORPORATE EXCEL FORMATS (Phase 5)
# ===========================================

def get_corporate_excel_formats(workbook, company):
    """
    Generate OPS corporate Excel formats based on company primary color.

    This function creates a complete set of xlsxwriter format objects for
    corporate-branded Excel exports, matching the visual design of PDF reports.

    Args:
        workbook: xlsxwriter workbook object
        company: res.company record

    Returns:
        dict: Format objects keyed by name
            - company_name: Company header (16pt bold)
            - report_title: Report title (14pt bold)
            - metadata: Report metadata (9pt gray)
            - filter_bar: Filter summary bar (primary color light bg)
            - table_header: Column headers (primary bg, white text)
            - table_header_num: Column headers for numbers (right-aligned)
            - text: Regular text cell
            - text_alt: Alternating row text cell
            - number: Number cell (positive)
            - number_alt: Alternating row number
            - number_negative: Negative number (red with parentheses)
            - number_negative_alt: Alternating negative
            - number_zero: Zero value (gray)
            - number_zero_alt: Alternating zero
            - subtotal_label: Subtotal row label
            - subtotal_number: Subtotal row number
            - total_label: Grand total label
            - total_number: Grand total number
            - percentage: Percentage format

    Usage:
        formats = get_corporate_excel_formats(workbook, self.company_id)
        worksheet.write(0, 0, company.name, formats['company_name'])
        worksheet.write(row, col, value, formats['number'])
    """
    primary_hex = company.primary_color or '#5B6BBB'

    # Convert hex to RGB for xlsxwriter
    hex_color = primary_hex.lstrip('#')
    try:
        primary_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        primary_rgb = (91, 107, 187)  # Default OPS blue

    # Calculate light version (15% opacity with white)
    light_rgb = tuple(int(c * 0.15 + 255 * 0.85) for c in primary_rgb)
    light_hex = '#{:02x}{:02x}{:02x}'.format(*light_rgb)

    formats = {
        # Company header
        'company_name': workbook.add_format({
            'font_size': 16,
            'bold': True,
            'font_color': '#1e293b',
            'font_name': 'Arial',
        }),

        # Report title
        'report_title': workbook.add_format({
            'font_size': 14,
            'bold': True,
            'font_color': '#1e293b',
            'font_name': 'Arial',
        }),

        # Report metadata
        'metadata': workbook.add_format({
            'font_size': 9,
            'font_color': '#64748b',
            'font_name': 'Arial',
        }),

        # Filter bar
        'filter_bar': workbook.add_format({
            'font_size': 9,
            'bg_color': light_hex,
            'border': 1,
            'border_color': primary_hex,
            'font_name': 'Arial',
        }),

        # Table header
        'table_header': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'font_color': '#ffffff',
            'bg_color': primary_hex,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': False,
            'font_name': 'Arial',
        }),

        # Table header (right-aligned for numbers)
        'table_header_num': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'font_color': '#ffffff',
            'bg_color': primary_hex,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'font_name': 'Arial',
        }),

        # Regular text cell
        'text': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'font_name': 'Arial',
        }),

        # Regular text cell (alternating row)
        'text_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'font_name': 'Arial',
        }),

        # Number cell (positive)
        'number': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        }),

        # Number cell (positive, alternating row)
        'number_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        }),

        # Number cell (negative)
        'number_negative': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '(#,##0.00)',
            'font_color': '#dc2626',
            'font_name': 'Consolas',
        }),

        # Number cell (negative, alternating row)
        'number_negative_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'align': 'right',
            'num_format': '(#,##0.00)',
            'font_color': '#dc2626',
            'font_name': 'Consolas',
        }),

        # Number cell (zero)
        'number_zero': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_color': '#94a3b8',
            'font_name': 'Consolas',
        }),

        # Number cell (zero, alternating row)
        'number_zero_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_color': '#94a3b8',
            'font_name': 'Consolas',
        }),

        # Subtotal row
        'subtotal_label': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': light_hex,
            'font_color': '#475569',
            'font_name': 'Arial',
        }),

        'subtotal_number': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': light_hex,
            'align': 'right',
            'num_format': '#,##0.00',
            'font_color': '#475569',
            'font_name': 'Consolas',
        }),

        # Total row
        'total_label': workbook.add_format({
            'font_size': 10,
            'bold': True,
            'border': 2,
            'border_color': '#1e293b',
            'bg_color': primary_hex,
            'font_color': '#ffffff',
            'font_name': 'Arial',
        }),

        'total_number': workbook.add_format({
            'font_size': 10,
            'bold': True,
            'border': 2,
            'border_color': '#1e293b',
            'bg_color': primary_hex,
            'font_color': '#ffffff',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        }),

        # Percentage format
        'percentage': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '0.0%',
            'font_name': 'Consolas',
        }),
    }

    return formats
