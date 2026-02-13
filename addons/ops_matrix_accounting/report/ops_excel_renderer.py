# -*- coding: utf-8 -*-
"""
OPS Generic Excel Renderer
===========================

Shape-aware XLSX renderer that reads data contracts produced by any wizard's
``_get_report_data()`` and writes a branded workbook.  Contains ZERO
report-specific code -- everything is driven by the data contract.

Shapes handled:
  - **lines** (Shape A): Grouped journal entry lines.
  - **hierarchy** (Shape B): Recursive financial hierarchy.
  - **matrix** (Shape C): Dynamic-column tabular data.

The renderer honours company colors from the ``colors`` dict that every
data contract carries (see ``ops_report_contracts.ReportColors``).
"""

import io
import xlsxwriter
from odoo import models, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

# Column-key to human-readable label (identical to QWeb template mapping)
COL_LABELS = {
    'date': 'Date',
    'entry': 'Entry',
    'journal': 'Jnl',
    'account_code': 'Code',
    'account_name': 'Account',
    'label': 'Description',
    'ref': 'Reference',
    'partner': 'Partner',
    'branch': 'Branch',
    'bu': 'BU',
    'debit': 'Debit',
    'credit': 'Credit',
    'balance': 'Balance',
    'currency': 'Curr',
    'amount_currency': 'FCY Amount',
}

# Numeric column keys -- right-aligned and formatted as numbers
NUMERIC_COLS = {'debit', 'credit', 'balance', 'amount_currency'}

# Default widths per column key
DEFAULT_WIDTHS = {
    'date': 12,
    'entry': 16,
    'journal': 8,
    'account_code': 12,
    'account_name': 30,
    'label': 36,
    'ref': 14,
    'partner': 24,
    'branch': 14,
    'bu': 14,
    'debit': 16,
    'credit': 16,
    'balance': 16,
    'currency': 8,
    'amount_currency': 16,
}


class OpsExcelRenderer(models.AbstractModel):
    """Generic Excel renderer driven entirely by data contracts."""

    _name = 'ops.excel.renderer'
    _description = 'OPS Generic Excel Renderer'

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, report_data):
        """Main entry point.  Returns raw binary XLSX content.

        Args:
            report_data (dict): Data contract dict produced by a wizard's
                ``_get_report_data()`` (Shape A / B / C).

        Returns:
            bytes: Raw XLSX binary content.

        Raises:
            AccessError: If the current user lacks the export permission.
        """
        if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
            raise AccessError(_("You do not have permission to export data."))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        meta = report_data.get('meta', {})
        colors = report_data.get('colors', {})
        formats = self._create_formats(workbook, colors)

        shape = meta.get('shape', 'matrix')
        if shape == 'lines':
            self._render_lines(workbook, formats, report_data)
        elif shape == 'hierarchy':
            self._render_hierarchy(workbook, formats, report_data)
        else:
            self._render_matrix(workbook, formats, report_data)

        workbook.close()
        output.seek(0)
        return output.read()

    # ------------------------------------------------------------------
    # Format factory
    # ------------------------------------------------------------------

    def _create_formats(self, workbook, colors):
        """Create all named xlsxwriter formats from the color config.

        Args:
            workbook: xlsxwriter.Workbook
            colors (dict): ReportColors-compatible dict.

        Returns:
            dict: keyed format objects.
        """
        primary = colors.get('primary', '#5B6BBB')
        primary_dark = colors.get('primary_dark', '#44508c')
        primary_light = colors.get('primary_light', '#edeef5')
        text_on_primary = colors.get('text_on_primary', '#FFFFFF')
        body_text = colors.get('body_text', '#1a1a1a')
        danger = colors.get('danger', '#dc2626')
        zero_color = colors.get('zero', '#94a3b8')
        border_color = colors.get('border', '#e5e7eb')

        common = {
            'font_name': 'Arial',
            'font_size': 9,
            'valign': 'vcenter',
        }

        f = {}

        # Title: company name (row 0)
        f['title'] = workbook.add_format({
            **common,
            'font_size': 16,
            'bold': True,
            'font_color': '#1e293b',
        })

        # Company sub-info (VAT etc.)
        f['company'] = workbook.add_format({
            **common,
            'font_size': 8,
            'font_color': '#6b7280',
        })

        # Report title (right-hand header)
        f['report_title'] = workbook.add_format({
            **common,
            'font_size': 13,
            'bold': True,
            'font_color': primary,
            'align': 'right',
        })

        # Dates and generation info
        f['report_date'] = workbook.add_format({
            **common,
            'font_size': 8,
            'font_color': '#6b7280',
            'align': 'right',
        })

        # Column header (left-aligned)
        f['header'] = workbook.add_format({
            **common,
            'bold': True,
            'font_color': text_on_primary,
            'bg_color': primary,
            'border': 1,
            'border_color': primary_dark,
            'text_wrap': True,
        })

        # Column header (right-aligned -- for numeric columns)
        f['header_right'] = workbook.add_format({
            **common,
            'bold': True,
            'font_color': text_on_primary,
            'bg_color': primary,
            'border': 1,
            'border_color': primary_dark,
            'align': 'right',
            'text_wrap': True,
        })

        # Detail text cell
        f['detail'] = workbook.add_format({
            **common,
            'border': 1,
            'border_color': border_color,
        })

        # Detail text cell (bold, for group/indent label)
        f['detail_bold'] = workbook.add_format({
            **common,
            'bold': True,
            'border': 1,
            'border_color': border_color,
        })

        # Detail number (positive or zero)
        f['detail_number'] = workbook.add_format({
            **common,
            'num_format': '#,##0.00',
            'align': 'right',
            'border': 1,
            'border_color': border_color,
            'font_name': 'Consolas',
        })

        # Detail number (negative -- red)
        f['detail_negative'] = workbook.add_format({
            **common,
            'num_format': '#,##0.00',
            'align': 'right',
            'border': 1,
            'border_color': border_color,
            'font_color': danger,
            'font_name': 'Consolas',
        })

        # Detail number (zero -- gray)
        f['detail_zero'] = workbook.add_format({
            **common,
            'num_format': '#,##0.00',
            'align': 'right',
            'border': 1,
            'border_color': border_color,
            'font_color': zero_color,
            'font_name': 'Consolas',
        })

        # Percentage
        f['detail_percentage'] = workbook.add_format({
            **common,
            'num_format': '0.0%',
            'align': 'right',
            'border': 1,
            'border_color': border_color,
            'font_name': 'Consolas',
        })

        # Group header (merged row, light bg)
        f['group_header'] = workbook.add_format({
            **common,
            'font_size': 10,
            'bold': True,
            'bg_color': primary_light,
            'border': 1,
            'border_color': border_color,
        })

        # Section header (hierarchy Shape B)
        f['section'] = workbook.add_format({
            **common,
            'font_size': 10,
            'bold': True,
            'bg_color': primary_light,
            'border': 1,
            'border_color': border_color,
        })

        # Section number (right-aligned, bold, light bg)
        f['section_number'] = workbook.add_format({
            **common,
            'font_size': 10,
            'bold': True,
            'bg_color': primary_light,
            'border': 1,
            'border_color': border_color,
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        })

        # Total row (bold, top border, light bg)
        f['total'] = workbook.add_format({
            **common,
            'bold': True,
            'bg_color': primary_light,
            'border': 1,
            'border_color': border_color,
            'top': 2,
            'top_color': primary,
        })

        # Total number
        f['total_number'] = workbook.add_format({
            **common,
            'bold': True,
            'bg_color': primary_light,
            'num_format': '#,##0.00',
            'align': 'right',
            'border': 1,
            'border_color': border_color,
            'top': 2,
            'top_color': primary,
            'font_name': 'Consolas',
        })

        # Grand total row (primary bg, white text)
        f['grand_total'] = workbook.add_format({
            **common,
            'font_size': 10,
            'bold': True,
            'bg_color': primary,
            'font_color': text_on_primary,
            'border': 2,
            'border_color': primary_dark,
        })

        # Grand total number
        f['grand_total_number'] = workbook.add_format({
            **common,
            'font_size': 10,
            'bold': True,
            'bg_color': primary,
            'font_color': text_on_primary,
            'num_format': '#,##0.00',
            'align': 'right',
            'border': 2,
            'border_color': primary_dark,
            'font_name': 'Consolas',
        })

        # Filter label / value (metadata section)
        f['filter_label'] = workbook.add_format({
            **common,
            'bold': True,
            'font_color': primary,
        })

        f['filter_value'] = workbook.add_format({
            **common,
        })

        return f

    # ------------------------------------------------------------------
    # Report header (shared by all shapes)
    # ------------------------------------------------------------------

    def _write_report_header(self, ws, formats, meta, row=0):
        """Write company name, report title, date range, and filters.

        Args:
            ws: xlsxwriter Worksheet
            formats (dict): Formats dict from _create_formats
            meta (dict): Report meta dict from data contract
            row (int): Starting row (default 0)

        Returns:
            int: Next available row after the header.
        """
        # Row 0: Company name + report title
        ws.write(row, 0, meta.get('company_name', ''), formats['title'])
        ws.write(row, 4, meta.get('report_title', _('Report')), formats['report_title'])
        row += 1

        # Row 1: VAT / Date range
        if meta.get('company_vat'):
            ws.write(row, 0, _('VAT: %s') % meta['company_vat'], formats['company'])
        date_str = ''
        if meta.get('date_from') and meta.get('date_to'):
            date_str = '%s to %s' % (meta['date_from'], meta['date_to'])
        elif meta.get('as_of_date'):
            date_str = _('As of %s') % meta['as_of_date']
        if date_str:
            ws.write(row, 4, date_str, formats['report_date'])
        row += 1

        # Row 2: Generated at
        if meta.get('generated_at'):
            ws.write(row, 4, _('Generated: %s') % meta['generated_at'], formats['report_date'])
        row += 1

        # Filters
        filters = meta.get('filters', {})
        if filters:
            for key, val in filters.items():
                label = key.replace('_', ' ').title()
                if isinstance(val, (list, tuple)):
                    display = ', '.join(str(v) for v in val)
                else:
                    display = str(val)
                ws.write(row, 0, label + ':', formats['filter_label'])
                ws.write(row, 1, display, formats['filter_value'])
                row += 1

        # Blank separator row
        row += 1
        return row

    # ------------------------------------------------------------------
    # Number-formatting helper
    # ------------------------------------------------------------------

    def _write_number(self, ws, row, col, value, formats):
        """Write a numeric cell with sign-aware formatting.

        Args:
            ws: Worksheet
            row, col: Cell coordinates
            value: Numeric value (int or float)
            formats (dict): Formats dict
        """
        if value is None or value == '' or value is False:
            ws.write_number(row, col, 0, formats['detail_zero'])
        elif isinstance(value, (int, float)):
            if value < 0:
                ws.write_number(row, col, value, formats['detail_negative'])
            elif value == 0:
                ws.write_number(row, col, 0, formats['detail_zero'])
            else:
                ws.write_number(row, col, value, formats['detail_number'])
        else:
            # Non-numeric -- write as string
            ws.write(row, col, str(value), formats['detail'])

    # ------------------------------------------------------------------
    # Auto-fit helper
    # ------------------------------------------------------------------

    def _autofit_columns(self, ws, col_widths):
        """Apply tracked column widths.

        Args:
            ws: Worksheet
            col_widths (dict): {col_index: max_char_width}
        """
        for col_idx, width in col_widths.items():
            # Add a small padding, cap at 50
            final = min(max(width + 2, 8), 50)
            ws.set_column(col_idx, col_idx, final)

    def _track_width(self, col_widths, col_idx, value):
        """Track max width for a column.

        Args:
            col_widths (dict): Mutable dict of {col_idx: width}
            col_idx (int): Column index
            value: Cell value (will be converted to string for length)
        """
        if value is None or value is False:
            return
        length = len(str(value))
        if col_idx not in col_widths or length > col_widths[col_idx]:
            col_widths[col_idx] = length

    # ------------------------------------------------------------------
    # Shape A -- Lines (GL, Partner Ledger, Cash Book, etc.)
    # ------------------------------------------------------------------

    def _render_lines(self, workbook, formats, data):
        """Render a Shape A (line-based) report.

        Args:
            workbook: xlsxwriter.Workbook
            formats (dict): Format dict
            data (dict): ShapeAReport-compatible dict
        """
        meta = data.get('meta', {})
        title = meta.get('report_title', _('Report'))
        ws_name = title[:31]  # Excel max 31 chars
        ws = workbook.add_worksheet(ws_name)
        ws.set_landscape()

        visible_cols = data.get('visible_columns', [
            'date', 'entry', 'label', 'debit', 'credit', 'balance',
        ])
        num_cols = len(visible_cols)
        col_widths = {}

        # Apply default widths from DEFAULT_WIDTHS mapping
        for ci, col_key in enumerate(visible_cols):
            if col_key in DEFAULT_WIDTHS:
                col_widths[ci] = DEFAULT_WIDTHS[col_key]

        # Report header
        row = self._write_report_header(ws, formats, meta)

        # Groups
        groups = data.get('groups', [])
        for group in groups:
            # -- Group header (merged row)
            group_label = '%s \u2014 %s' % (
                group.get('group_key', ''),
                group.get('group_name', ''),
            )
            if num_cols > 1:
                ws.merge_range(row, 0, row, num_cols - 1, group_label, formats['group_header'])
            else:
                ws.write(row, 0, group_label, formats['group_header'])
            self._track_width(col_widths, 0, group_label)
            row += 1

            # -- Column headers
            for ci, col_key in enumerate(visible_cols):
                label = COL_LABELS.get(col_key, col_key.replace('_', ' ').title())
                fmt = formats['header_right'] if col_key in NUMERIC_COLS else formats['header']
                ws.write(row, ci, label, fmt)
                self._track_width(col_widths, ci, label)
            row += 1

            # -- Opening balance
            opening = group.get('opening_balance', 0)
            if opening:
                for ci, col_key in enumerate(visible_cols):
                    if col_key == 'label':
                        ws.write(row, ci, _('Opening Balance'), formats['detail'])
                    elif col_key == 'balance':
                        self._write_number(ws, row, ci, opening, formats)
                    else:
                        ws.write(row, ci, '', formats['detail'])
                row += 1

            # -- Detail lines
            for line in group.get('lines', []):
                for ci, col_key in enumerate(visible_cols):
                    cell_val = line.get(col_key, '')
                    if col_key in NUMERIC_COLS:
                        self._write_number(ws, row, ci, cell_val, formats)
                    else:
                        ws.write(row, ci, cell_val if cell_val else '', formats['detail'])
                        self._track_width(col_widths, ci, cell_val)
                row += 1

            # -- Group total row
            for ci, col_key in enumerate(visible_cols):
                if col_key == 'label':
                    ws.write(row, ci, _('Total %s') % group.get('group_name', ''), formats['total'])
                elif col_key == 'debit':
                    ws.write_number(row, ci, group.get('total_debit', 0), formats['total_number'])
                elif col_key == 'credit':
                    ws.write_number(row, ci, group.get('total_credit', 0), formats['total_number'])
                elif col_key == 'balance':
                    ws.write_number(row, ci, group.get('closing_balance', 0), formats['total_number'])
                else:
                    ws.write(row, ci, '', formats['total'])
            row += 1

            # Blank separator row between groups
            row += 1

        # Grand totals
        gt = data.get('grand_totals', {})
        if gt:
            for ci, col_key in enumerate(visible_cols):
                if col_key == 'label':
                    ws.write(row, ci, _('Grand Total'), formats['grand_total'])
                elif col_key == 'debit':
                    ws.write_number(row, ci, gt.get('total_debit', 0), formats['grand_total_number'])
                elif col_key == 'credit':
                    ws.write_number(row, ci, gt.get('total_credit', 0), formats['grand_total_number'])
                elif col_key == 'balance':
                    ws.write_number(row, ci, gt.get('closing_balance', 0), formats['grand_total_number'])
                else:
                    ws.write(row, ci, '', formats['grand_total'])

        # Apply column widths
        self._autofit_columns(ws, col_widths)

    # ------------------------------------------------------------------
    # Shape B -- Hierarchy (P&L, BS, CF, Budget vs Actual, Consolidation)
    # ------------------------------------------------------------------

    def _render_hierarchy(self, workbook, formats, data):
        """Render a Shape B (hierarchy-based) report.

        Args:
            workbook: xlsxwriter.Workbook
            formats (dict): Format dict
            data (dict): ShapeBReport-compatible dict
        """
        meta = data.get('meta', {})
        title = meta.get('report_title', _('Report'))
        ws_name = title[:31]
        ws = workbook.add_worksheet(ws_name)
        ws.set_landscape()

        value_columns = data.get('value_columns', [])
        col_widths = {}

        # Report header
        row = self._write_report_header(ws, formats, meta)

        # Column headers: Name | value_col_1 | value_col_2 | ...
        ws.write(row, 0, _('Account'), formats['header'])
        col_widths[0] = 40
        for vi, vc in enumerate(value_columns):
            label = vc.get('label', vc.get('key', ''))
            ws.write(row, vi + 1, label, formats['header_right'])
            self._track_width(col_widths, vi + 1, label)
            if col_widths.get(vi + 1, 0) < 16:
                col_widths[vi + 1] = 16
        row += 1

        # Render sections recursively
        for section in data.get('sections', []):
            row = self._render_hierarchy_node(ws, formats, value_columns, section, row, col_widths)

        # Net result row
        nr = data.get('net_result')
        if nr:
            name = nr.get('name', _('Net Result'))
            ws.write(row, 0, name, formats['grand_total'])
            for vi, vc in enumerate(value_columns):
                val = nr.get('values', {}).get(vc.get('key', ''), 0)
                if val and isinstance(val, (int, float)):
                    ws.write_number(row, vi + 1, val, formats['grand_total_number'])
                else:
                    ws.write(row, vi + 1, '', formats['grand_total'])

        # Apply column widths
        self._autofit_columns(ws, col_widths)

    def _render_hierarchy_node(self, ws, formats, value_columns, node, row, col_widths):
        """Recursively render a hierarchy node and its children.

        Args:
            ws: Worksheet
            formats (dict): Format dict
            value_columns (list): List of value column dicts
            node (dict): HierarchyNode-compatible dict
            row (int): Current row number
            col_widths (dict): Mutable width tracker

        Returns:
            int: Next available row.
        """
        style = node.get('style', 'detail')
        level = node.get('level', 0)
        code = node.get('code', '')
        name = node.get('name', '')
        values = node.get('values', {})

        # Build display label with optional code and indentation
        if code:
            display_name = '%s%s \u2014 %s' % ('  ' * level, code, name)
        else:
            display_name = '%s%s' % ('  ' * level, name)

        self._track_width(col_widths, 0, display_name)

        if style == 'section':
            ws.write(row, 0, display_name, formats['section'])
            for vi, vc in enumerate(value_columns):
                val = values.get(vc.get('key', ''), 0)
                if val and isinstance(val, (int, float)):
                    ws.write_number(row, vi + 1, val, formats['section_number'])
                else:
                    ws.write(row, vi + 1, '', formats['section'])
            row += 1

        elif style == 'group':
            ws.write(row, 0, display_name, formats['detail_bold'])
            for vi, vc in enumerate(value_columns):
                val = values.get(vc.get('key', ''), 0)
                if val and isinstance(val, (int, float)):
                    self._write_number(ws, row, vi + 1, val, formats)
                else:
                    ws.write(row, vi + 1, '', formats['detail'])
            row += 1

        elif style == 'total':
            ws.write(row, 0, display_name, formats['total'])
            for vi, vc in enumerate(value_columns):
                val = values.get(vc.get('key', ''), 0)
                if val and isinstance(val, (int, float)):
                    ws.write_number(row, vi + 1, val, formats['total_number'])
                else:
                    ws.write(row, vi + 1, '', formats['total'])
            row += 1

        elif style == 'grand_total':
            ws.write(row, 0, display_name, formats['grand_total'])
            for vi, vc in enumerate(value_columns):
                val = values.get(vc.get('key', ''), 0)
                if val and isinstance(val, (int, float)):
                    ws.write_number(row, vi + 1, val, formats['grand_total_number'])
                else:
                    ws.write(row, vi + 1, '', formats['grand_total'])
            row += 1

        else:
            # detail (default)
            ws.write(row, 0, display_name, formats['detail'])
            for vi, vc in enumerate(value_columns):
                val = values.get(vc.get('key', ''), 0)
                self._write_number(ws, row, vi + 1, val, formats)
            row += 1

        # Recurse into children
        for child in node.get('children', []):
            row = self._render_hierarchy_node(ws, formats, value_columns, child, row, col_widths)

        return row

    # ------------------------------------------------------------------
    # Shape C -- Matrix (TB, Aged, Asset, Treasury, Inventory)
    # ------------------------------------------------------------------

    def _render_matrix(self, workbook, formats, data):
        """Render a Shape C (matrix/table-based) report.

        Args:
            workbook: xlsxwriter.Workbook
            formats (dict): Format dict
            data (dict): ShapeCReport-compatible dict
        """
        meta = data.get('meta', {})
        title = meta.get('report_title', _('Report'))
        ws_name = title[:31]
        ws = workbook.add_worksheet(ws_name)
        ws.set_landscape()

        columns = data.get('columns', [])
        col_widths = {}

        # Report header
        row = self._write_report_header(ws, formats, meta)

        # Column headers
        for ci, col_def in enumerate(columns):
            label = col_def.get('label', col_def.get('key', ''))
            col_type = col_def.get('col_type', 'string')
            align = col_def.get('align', 'left')
            is_numeric = col_type in ('number', 'currency', 'percentage') or align == 'right'
            fmt = formats['header_right'] if is_numeric else formats['header']
            ws.write(row, ci, label, fmt)
            self._track_width(col_widths, ci, label)
            # Set minimum width for numeric columns
            if col_type in ('number', 'currency'):
                col_widths[ci] = max(col_widths.get(ci, 0), 16)
        row += 1

        # Data rows
        for data_row in data.get('rows', []):
            row_style = data_row.get('style', 'detail')
            row_level = data_row.get('level', 0)
            row_values = data_row.get('values', {})

            for ci, col_def in enumerate(columns):
                col_key = col_def.get('key', '')
                col_type = col_def.get('col_type', 'string')
                cell_val = row_values.get(col_key, '')

                # Determine format based on row style
                if row_style == 'header':
                    self._write_matrix_cell(ws, row, ci, cell_val, col_type, formats,
                                            text_fmt='group_header', num_fmt='section_number')
                elif row_style in ('subtotal', 'total'):
                    self._write_matrix_cell(ws, row, ci, cell_val, col_type, formats,
                                            text_fmt='total', num_fmt='total_number')
                elif row_style == 'grand_total':
                    self._write_matrix_cell(ws, row, ci, cell_val, col_type, formats,
                                            text_fmt='grand_total', num_fmt='grand_total_number')
                else:
                    # detail
                    if ci == 0 and row_level > 0:
                        # Indent first column for nested rows
                        indent_val = '%s%s' % ('  ' * row_level, cell_val if cell_val else '')
                        ws.write(row, ci, indent_val, formats['detail'])
                        self._track_width(col_widths, ci, indent_val)
                    elif col_type in ('number', 'currency'):
                        self._write_number(ws, row, ci, cell_val, formats)
                    elif col_type == 'percentage':
                        if cell_val and isinstance(cell_val, (int, float)):
                            ws.write_number(row, ci, cell_val, formats['detail_percentage'])
                        else:
                            ws.write(row, ci, '', formats['detail'])
                    else:
                        ws.write(row, ci, cell_val if cell_val else '', formats['detail'])
                        self._track_width(col_widths, ci, cell_val)
            row += 1

        # Totals row from data['totals']
        totals = data.get('totals', {})
        if totals:
            for ci, col_def in enumerate(columns):
                col_key = col_def.get('key', '')
                col_type = col_def.get('col_type', 'string')
                cell_val = totals.get(col_key, '')
                self._write_matrix_cell(ws, row, ci, cell_val, col_type, formats,
                                        text_fmt='grand_total', num_fmt='grand_total_number')

        # Apply column widths
        self._autofit_columns(ws, col_widths)

    def _write_matrix_cell(self, ws, row, col, value, col_type, formats,
                           text_fmt='detail', num_fmt='detail_number'):
        """Write a single matrix cell with appropriate format.

        Args:
            ws: Worksheet
            row, col: Cell coordinates
            value: Cell value
            col_type (str): Column type ('string', 'number', 'currency', 'percentage', 'date')
            formats (dict): Format dict
            text_fmt (str): Key into formats for text cells
            num_fmt (str): Key into formats for numeric cells
        """
        if col_type in ('number', 'currency'):
            if value and isinstance(value, (int, float)):
                ws.write_number(row, col, value, formats[num_fmt])
            elif value is None or value == '' or value is False or value == 0:
                ws.write_number(row, col, 0, formats[num_fmt])
            else:
                ws.write(row, col, str(value), formats[text_fmt])
        elif col_type == 'percentage':
            if value and isinstance(value, (int, float)):
                ws.write_number(row, col, value, formats.get('detail_percentage', formats[num_fmt]))
            else:
                ws.write(row, col, '', formats[text_fmt])
        else:
            ws.write(row, col, value if value else '', formats[text_fmt])
