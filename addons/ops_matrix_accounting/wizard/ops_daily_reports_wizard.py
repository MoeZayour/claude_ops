# -*- coding: utf-8 -*-
"""
OPS Daily Financial Reports
Adopted from OM om_account_daily_reports, enhanced with:
- Branch filtering
- Excel export
- OPS Matrix integration
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging
import io
import base64

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False

_logger = logging.getLogger(__name__)


class OpsCashBookWizard(models.TransientModel):
    """Cash Book Report Wizard."""
    _name = 'ops.cash.book.wizard'
    _inherit = 'ops.intelligence.security.mixin'
    _description = 'Cash Book Report'

    def _get_engine_name(self):
        """Return engine name for security checks."""
        return 'financial'

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )

    # OPS Enhancement: Branch filter
    ops_branch_ids = fields.Many2many(
        'ops.branch', string='Branches',
        help='Leave empty for all branches'
    )

    journal_ids = fields.Many2many(
        'account.journal',
        'ops_cash_book_journal_rel',
        'wizard_id', 'journal_id',
        string='Cash Journals',
        required=True,
        domain="[('type', '=', 'cash'), ('company_id', '=', company_id)]",
        default=lambda self: self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.env.company.id)
        ])
    )

    target_move = fields.Selection([
        ('posted', 'Posted Entries'),
        ('all', 'All Entries'),
    ], string='Target Moves', default='posted', required=True)

    sort_by = fields.Selection([
        ('date', 'Date'),
        ('name', 'Reference'),
    ], string='Sort By', default='date')

    display_account = fields.Selection([
        ('all', 'All'),
        ('movement', 'With Movements'),
    ], string='Display Accounts', default='movement')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Update journal selection when company changes."""
        if self.company_id:
            cash_journals = self.env['account.journal'].search([
                ('type', '=', 'cash'),
                ('company_id', '=', self.company_id.id)
            ])
            self.journal_ids = cash_journals.ids
        else:
            self.journal_ids = []

    def _get_report_data(self):
        """Get cash book report data."""
        self.ensure_one()

        domain = [
            ('journal_id', 'in', self.journal_ids.ids),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]

        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))

        if self.ops_branch_ids:
            domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))

        # Get opening balance
        opening_domain = [
            ('journal_id', 'in', self.journal_ids.ids),
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('parent_state', '=', 'posted'),
        ]
        if self.ops_branch_ids:
            opening_domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))

        opening_result = self.env['account.move.line'].read_group(
            opening_domain, ['balance:sum'], []
        )
        opening_balance = opening_result[0]['balance'] if opening_result else 0.0

        # Get transactions
        order = 'date asc, id asc' if self.sort_by == 'date' else 'move_name asc, id asc'
        move_lines = self.env['account.move.line'].search(domain, order=order)

        lines = []
        running_balance = opening_balance

        for ml in move_lines:
            running_balance += ml.balance
            lines.append({
                'date': ml.date,
                'ref': ml.move_id.name,
                'partner': ml.partner_id.name or '',
                'account': ml.account_id.display_name,
                'label': ml.name or '',
                'debit': ml.debit,
                'credit': ml.credit,
                'balance': running_balance,
                'branch': ml.ops_branch_id.name if hasattr(ml, 'ops_branch_id') and ml.ops_branch_id else '',
            })

        return {
            'company': self.company_id.name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'journals': ', '.join(self.journal_ids.mapped('name')),
            'branches': ', '.join(self.ops_branch_ids.mapped('name')) or 'All',
            'target_move': dict(self._fields['target_move'].selection).get(self.target_move),
            'opening_balance': opening_balance,
            'lines': lines,
            'closing_balance': running_balance,
            'total_debit': sum(l['debit'] for l in lines),
            'total_credit': sum(l['credit'] for l in lines),
            'currency': self.company_id.currency_id,
        }

    def action_view_report(self):
        """Open report in UI View mode (browser preview with toolbar)."""
        self.ensure_one()

        # Get report template name
        template_name = self._get_report_template_xmlid()

        # Return action to open in new tab with controller
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f'{base_url}/ops/report/html/{template_name}?wizard_id={self.id}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_generate_report(self):
        """Alias for action_print_pdf for UI consistency."""
        return self.action_print_pdf()

    def action_print_pdf(self):
        """Generate PDF report with security checks."""
        self.ensure_one()
        # Security: IT Admin Blindness & Persona Access
        self._check_intelligence_access('financial')
        data = {'wizard_id': self.id, 'report_data': self._get_report_data()}
        return self.env.ref('ops_matrix_accounting.action_report_cash_book').report_action(self, data=data)

    def action_export_excel(self):
        """Export to Excel using Phase 5 corporate design."""
        if not XLSXWRITER_AVAILABLE:
            raise UserError(_('xlsxwriter library is required for Excel export. Please install it.'))

        from ..report.excel_styles import get_corporate_excel_formats

        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Cash Book')

        # Get corporate formats
        formats = get_corporate_excel_formats(workbook, self.company_id)

        # Phase 5 Corporate Header Structure
        row = 0
        # Row 0: Company name
        worksheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        worksheet.write(row, 0, 'Cash Book', formats['report_title'])
        row += 1

        # Row 2: Report period
        worksheet.write(row, 0, f"Period: {data['date_from']} to {data['date_to']}", formats['metadata'])
        row += 1

        # Row 3: Generated timestamp and user
        generated = fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
        worksheet.write(row, 0, f"Generated: {generated} by {self.env.user.name}", formats['metadata'])
        row += 2

        # Row 5: Filter bar with journal and currency info
        filter_text = f"Journal: {data['journals']} | Currency: {self.company_id.currency_id.name} | Branches: {data['branches']} | Status: {data['target_move']}"
        worksheet.merge_range(row, 0, row, 7, filter_text, formats['filter_bar'])
        row += 1

        # Row 6: Opening Balance
        worksheet.write(row, 0, 'Opening Balance:', formats['subtotal_label'])
        # Apply value-based formatting for opening balance
        opening_val = data['opening_balance']
        if opening_val > 0:
            opening_fmt = formats['number']
        elif opening_val < 0:
            opening_fmt = formats['number_negative']
        else:
            opening_fmt = formats['number_zero']
        worksheet.write(row, 1, opening_val, opening_fmt)
        row += 1

        # Table headers row
        headers = ['Date', 'Reference', 'Partner', 'Account', 'Description', 'Debit', 'Credit', 'Balance']
        for col in range(5):
            worksheet.write(row, col, headers[col], formats['table_header'])
        for col in range(5, 8):
            worksheet.write(row, col, headers[col], formats['table_header_num'])

        # Freeze panes below header row
        worksheet.freeze_panes(row + 1, 0)
        row += 1

        # Data rows with alternating format
        for idx, line in enumerate(data['lines']):
            is_alt = (idx % 2 == 1)
            text_fmt = formats['text_alt'] if is_alt else formats['text']

            # Date
            worksheet.write(row, 0, str(line['date']), text_fmt)
            # Reference
            worksheet.write(row, 1, line['ref'], text_fmt)
            # Partner
            worksheet.write(row, 2, line['partner'], text_fmt)
            # Account
            worksheet.write(row, 3, line['account'], text_fmt)
            # Description
            worksheet.write(row, 4, line['label'], text_fmt)

            # Debit - value-based formatting
            debit_val = line['debit']
            if debit_val > 0:
                debit_fmt = formats['number_alt'] if is_alt else formats['number']
            elif debit_val < 0:
                debit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                debit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            worksheet.write(row, 5, debit_val, debit_fmt)

            # Credit - value-based formatting
            credit_val = line['credit']
            if credit_val > 0:
                credit_fmt = formats['number_alt'] if is_alt else formats['number']
            elif credit_val < 0:
                credit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                credit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            worksheet.write(row, 6, credit_val, credit_fmt)

            # Balance - value-based formatting
            balance_val = line['balance']
            if balance_val > 0:
                balance_fmt = formats['number_alt'] if is_alt else formats['number']
            elif balance_val < 0:
                balance_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                balance_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            worksheet.write(row, 7, balance_val, balance_fmt)

            row += 1

        # Total row
        worksheet.write(row, 0, 'TOTALS', formats['total_label'])
        worksheet.write(row, 1, '', formats['total_label'])
        worksheet.write(row, 2, '', formats['total_label'])
        worksheet.write(row, 3, '', formats['total_label'])
        worksheet.write(row, 4, '', formats['total_label'])
        worksheet.write(row, 5, data['total_debit'], formats['total_number'])
        worksheet.write(row, 6, data['total_credit'], formats['total_number'])
        worksheet.write(row, 7, data['closing_balance'], formats['total_number'])

        # Set column widths
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:H', 15)

        # Page setup: Landscape, A4, fit to 1 page wide
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.fit_to_pages(1, 0)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f'Cash_Book_{self.date_from}_{self.date_to}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """Return XML ID of the cash book report template."""
        return 'ops_matrix_accounting.report_cash_book_corporate'


class OpsDayBookWizard(models.TransientModel):
    """Day Book Report Wizard - All transactions for a day."""
    _name = 'ops.day.book.wizard'
    _inherit = 'ops.intelligence.security.mixin'
    _description = 'Day Book Report'

    def _get_engine_name(self):
        """Return engine name for security checks."""
        return 'financial'

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today
    )

    ops_branch_ids = fields.Many2many(
        'ops.branch',
        'ops_day_book_branch_rel',
        'wizard_id', 'branch_id',
        string='Branches',
        help='Leave empty for all branches'
    )

    journal_ids = fields.Many2many(
        'account.journal',
        'ops_day_book_journal_rel',
        'wizard_id', 'journal_id',
        string='Journals',
        help='Leave empty for all journals'
    )

    target_move = fields.Selection([
        ('posted', 'Posted Entries'),
        ('all', 'All Entries'),
    ], string='Target Moves', default='posted', required=True)

    def _get_report_data(self):
        """Get day book report data."""
        self.ensure_one()

        domain = [
            ('date', '=', self.date),
            ('company_id', '=', self.company_id.id),
        ]

        if self.target_move == 'posted':
            domain.append(('state', '=', 'posted'))

        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))

        if self.ops_branch_ids:
            domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))

        moves = self.env['account.move'].search(domain, order='journal_id, name asc')

        data_by_journal = {}
        grand_total_debit = 0
        grand_total_credit = 0

        for move in moves:
            journal_name = move.journal_id.name
            if journal_name not in data_by_journal:
                data_by_journal[journal_name] = {
                    'journal': journal_name,
                    'journal_code': move.journal_id.code,
                    'moves': [],
                    'total_debit': 0,
                    'total_credit': 0,
                }

            move_data = {
                'name': move.name,
                'ref': move.ref or '',
                'partner': move.partner_id.name or '',
                'branch': move.ops_branch_id.name if hasattr(move, 'ops_branch_id') and move.ops_branch_id else '',
                'lines': [],
                'move_debit': 0,
                'move_credit': 0,
            }

            for line in move.line_ids:
                move_data['lines'].append({
                    'account': line.account_id.display_name,
                    'label': line.name or '',
                    'debit': line.debit,
                    'credit': line.credit,
                })
                move_data['move_debit'] += line.debit
                move_data['move_credit'] += line.credit
                data_by_journal[journal_name]['total_debit'] += line.debit
                data_by_journal[journal_name]['total_credit'] += line.credit

            data_by_journal[journal_name]['moves'].append(move_data)

        grand_total_debit = sum(j['total_debit'] for j in data_by_journal.values())
        grand_total_credit = sum(j['total_credit'] for j in data_by_journal.values())

        return {
            'company': self.company_id.name,
            'date': self.date,
            'branches': ', '.join(self.ops_branch_ids.mapped('name')) or 'All',
            'journals_filter': ', '.join(self.journal_ids.mapped('name')) or 'All',
            'target_move': dict(self._fields['target_move'].selection).get(self.target_move),
            'journals_data': list(data_by_journal.values()),
            'grand_total_debit': grand_total_debit,
            'grand_total_credit': grand_total_credit,
            'currency': self.company_id.currency_id,
        }

    def action_view_report(self):
        """Open report in UI View mode (browser preview with toolbar)."""
        self.ensure_one()

        # Get report template name
        template_name = self._get_report_template_xmlid()

        # Return action to open in new tab with controller
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f'{base_url}/ops/report/html/{template_name}?wizard_id={self.id}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_generate_report(self):
        """Alias for action_print_pdf for UI consistency."""
        return self.action_print_pdf()

    def action_print_pdf(self):
        """Generate PDF report with security checks."""
        self.ensure_one()
        # Security: IT Admin Blindness & Persona Access
        self._check_intelligence_access('financial')
        data = {'wizard_id': self.id, 'report_data': self._get_report_data()}
        return self.env.ref('ops_matrix_accounting.action_report_day_book').report_action(self, data=data)

    def action_export_excel(self):
        """Export to Excel using Phase 5 corporate design."""
        if not XLSXWRITER_AVAILABLE:
            raise UserError(_('xlsxwriter library is required for Excel export. Please install it.'))

        from ..report.excel_styles import get_corporate_excel_formats

        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Day Book')

        # Get corporate formats
        formats = get_corporate_excel_formats(workbook, self.company_id)

        # Phase 5 Corporate Header Structure
        row = 0
        # Row 0: Company name
        worksheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        worksheet.write(row, 0, 'Day Book', formats['report_title'])
        row += 1

        # Row 2: Report date
        worksheet.write(row, 0, f"Date: {data['date']}", formats['metadata'])
        row += 1

        # Row 3: Generated timestamp and user
        generated = fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
        worksheet.write(row, 0, f"Generated: {generated} by {self.env.user.name}", formats['metadata'])
        row += 2

        # Row 5: Filter bar with journal and currency info
        filter_text = f"Journal: {data['journals_filter']} | Currency: {self.company_id.currency_id.name} | Branches: {data['branches']} | Status: {data['target_move']}"
        worksheet.merge_range(row, 0, row, 3, filter_text, formats['filter_bar'])
        row += 2

        # Table headers row
        headers = ['Account', 'Description', 'Debit', 'Credit']
        worksheet.write(row, 0, headers[0], formats['table_header'])
        worksheet.write(row, 1, headers[1], formats['table_header'])
        worksheet.write(row, 2, headers[2], formats['table_header_num'])
        worksheet.write(row, 3, headers[3], formats['table_header_num'])

        # Freeze panes below header row
        worksheet.freeze_panes(row + 1, 0)
        row += 1

        # Data rows grouped by journal
        line_count = 0

        for journal_data in data['journals_data']:
            # Journal header (subtotal style)
            worksheet.merge_range(row, 0, row, 3, f"Journal: {journal_data['journal']}", formats['subtotal_label'])
            row += 1

            for move in journal_data['moves']:
                # Move header
                move_header = f"{move['name']} - {move['partner']}"
                if move['ref']:
                    move_header += f" - {move['ref']}"
                worksheet.merge_range(row, 0, row, 3, move_header, formats['subtotal_label'])
                row += 1

                # Lines with alternating row format
                for line in move['lines']:
                    is_alt = (line_count % 2 == 1)
                    text_fmt = formats['text_alt'] if is_alt else formats['text']

                    # Account
                    worksheet.write(row, 0, line['account'], text_fmt)
                    # Description
                    worksheet.write(row, 1, line['label'], text_fmt)

                    # Debit - value-based formatting
                    debit_val = line['debit']
                    if debit_val > 0:
                        debit_fmt = formats['number_alt'] if is_alt else formats['number']
                    elif debit_val < 0:
                        debit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
                    else:
                        debit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
                    worksheet.write(row, 2, debit_val, debit_fmt)

                    # Credit - value-based formatting
                    credit_val = line['credit']
                    if credit_val > 0:
                        credit_fmt = formats['number_alt'] if is_alt else formats['number']
                    elif credit_val < 0:
                        credit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
                    else:
                        credit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
                    worksheet.write(row, 3, credit_val, credit_fmt)

                    row += 1
                    line_count += 1

            # Journal subtotal
            worksheet.write(row, 0, '', formats['subtotal_label'])
            worksheet.write(row, 1, f"Journal Total: {journal_data['journal']}", formats['subtotal_label'])
            worksheet.write(row, 2, journal_data['total_debit'], formats['subtotal_number'])
            worksheet.write(row, 3, journal_data['total_credit'], formats['subtotal_number'])
            row += 1

        # Grand total row
        worksheet.write(row, 0, '', formats['total_label'])
        worksheet.write(row, 1, 'GRAND TOTAL', formats['total_label'])
        worksheet.write(row, 2, data['grand_total_debit'], formats['total_number'])
        worksheet.write(row, 3, data['grand_total_credit'], formats['total_number'])

        # Set column widths
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:D', 15)

        # Page setup: Landscape, A4, fit to 1 page wide
        worksheet.set_landscape()
        worksheet.set_paper(9)  # A4
        worksheet.fit_to_pages(1, 0)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f'Day_Book_{self.date}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """Return XML ID of the day book report template."""
        return 'ops_matrix_accounting.report_day_book_corporate'


class OpsBankBookWizard(models.TransientModel):
    """Bank Book Report Wizard."""
    _name = 'ops.bank.book.wizard'
    _inherit = 'ops.intelligence.security.mixin'
    _description = 'Bank Book Report'

    def _get_engine_name(self):
        """Return engine name for security checks."""
        return 'financial'

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )

    ops_branch_ids = fields.Many2many(
        'ops.branch',
        'ops_bank_book_branch_rel',
        'wizard_id', 'branch_id',
        string='Branches',
        help='Leave empty for all branches'
    )

    journal_ids = fields.Many2many(
        'account.journal',
        'ops_bank_book_journal_rel',
        'wizard_id', 'journal_id',
        string='Bank Journals',
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        default=lambda self: self.env['account.journal'].search([
            ('type', '=', 'bank'),
            ('company_id', '=', self.env.company.id)
        ])
    )

    target_move = fields.Selection([
        ('posted', 'Posted Entries'),
        ('all', 'All Entries'),
    ], string='Target Moves', default='posted', required=True)

    group_by_journal = fields.Boolean(
        string='Group by Bank Account',
        default=True,
        help='Show separate sections for each bank account'
    )

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Update journal selection when company changes."""
        if self.company_id:
            bank_journals = self.env['account.journal'].search([
                ('type', '=', 'bank'),
                ('company_id', '=', self.company_id.id)
            ])
            self.journal_ids = bank_journals.ids
        else:
            self.journal_ids = []

    def _get_report_data(self):
        """Get bank book report data - similar to cash book but grouped by bank."""
        self.ensure_one()

        data_by_journal = {}
        grand_opening = 0
        grand_closing = 0
        grand_debit = 0
        grand_credit = 0

        for journal in self.journal_ids:
            domain = [
                ('journal_id', '=', journal.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
                ('company_id', '=', self.company_id.id),
            ]

            if self.target_move == 'posted':
                domain.append(('parent_state', '=', 'posted'))

            if self.ops_branch_ids:
                domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))

            # Get opening balance for this journal
            opening_domain = [
                ('journal_id', '=', journal.id),
                ('date', '<', self.date_from),
                ('company_id', '=', self.company_id.id),
                ('parent_state', '=', 'posted'),
            ]
            if self.ops_branch_ids:
                opening_domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))

            opening_result = self.env['account.move.line'].read_group(
                opening_domain, ['balance:sum'], []
            )
            journal_opening = opening_result[0]['balance'] if opening_result else 0.0

            # Get transactions
            move_lines = self.env['account.move.line'].search(domain, order='date asc, id asc')

            lines = []
            running_balance = journal_opening

            for ml in move_lines:
                running_balance += ml.balance
                lines.append({
                    'date': ml.date,
                    'ref': ml.move_id.name,
                    'partner': ml.partner_id.name or '',
                    'account': ml.account_id.display_name,
                    'label': ml.name or '',
                    'debit': ml.debit,
                    'credit': ml.credit,
                    'balance': running_balance,
                    'branch': ml.ops_branch_id.name if hasattr(ml, 'ops_branch_id') and ml.ops_branch_id else '',
                })

            total_debit = sum(l['debit'] for l in lines)
            total_credit = sum(l['credit'] for l in lines)

            data_by_journal[journal.name] = {
                'journal': journal.name,
                'journal_code': journal.code,
                'account': journal.default_account_id.display_name if journal.default_account_id else '',
                'opening_balance': journal_opening,
                'lines': lines,
                'closing_balance': running_balance,
                'total_debit': total_debit,
                'total_credit': total_credit,
            }

            grand_opening += journal_opening
            grand_closing += running_balance
            grand_debit += total_debit
            grand_credit += total_credit

        return {
            'company': self.company_id.name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branches': ', '.join(self.ops_branch_ids.mapped('name')) or 'All',
            'target_move': dict(self._fields['target_move'].selection).get(self.target_move),
            'banks_data': list(data_by_journal.values()),
            'grand_opening': grand_opening,
            'grand_closing': grand_closing,
            'grand_debit': grand_debit,
            'grand_credit': grand_credit,
            'currency': self.company_id.currency_id,
        }

    def action_view_report(self):
        """Open report in UI View mode (browser preview with toolbar)."""
        self.ensure_one()

        # Get report template name
        template_name = self._get_report_template_xmlid()

        # Return action to open in new tab with controller
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f'{base_url}/ops/report/html/{template_name}?wizard_id={self.id}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_generate_report(self):
        """Alias for action_print_pdf for UI consistency."""
        return self.action_print_pdf()

    def action_print_pdf(self):
        """Generate PDF report with security checks."""
        self.ensure_one()
        # Security: IT Admin Blindness & Persona Access
        self._check_intelligence_access('financial')
        data = {'wizard_id': self.id, 'report_data': self._get_report_data()}
        return self.env.ref('ops_matrix_accounting.action_report_bank_book').report_action(self, data=data)

    def action_export_excel(self):
        """Export to Excel using Phase 5 corporate design."""
        if not XLSXWRITER_AVAILABLE:
            raise UserError(_('xlsxwriter library is required for Excel export. Please install it.'))

        from ..report.excel_styles import get_corporate_excel_formats

        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Get corporate formats
        formats = get_corporate_excel_formats(workbook, self.company_id)

        # Create worksheets for each bank
        for bank_data in data['banks_data']:
            # Create worksheet for each bank
            ws_name = bank_data['journal_code'][:31] if len(bank_data['journal_code']) > 31 else bank_data['journal_code']
            worksheet = workbook.add_worksheet(ws_name)

            # Phase 5 Corporate Header Structure
            row = 0
            # Row 0: Company name
            worksheet.write(row, 0, self.company_id.name, formats['company_name'])
            row += 1

            # Row 1: Report title
            worksheet.write(row, 0, f"Bank Book - {bank_data['journal']}", formats['report_title'])
            row += 1

            # Row 2: Report period
            worksheet.write(row, 0, f"Period: {data['date_from']} to {data['date_to']}", formats['metadata'])
            row += 1

            # Row 3: Generated timestamp and user
            generated = fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
            worksheet.write(row, 0, f"Generated: {generated} by {self.env.user.name}", formats['metadata'])
            row += 2

            # Row 5: Filter bar with journal and currency info
            filter_text = f"Journal: {bank_data['journal']} | Currency: {self.company_id.currency_id.name} | Branches: {data['branches']} | Status: {data['target_move']}"
            worksheet.merge_range(row, 0, row, 7, filter_text, formats['filter_bar'])
            row += 1

            # Row 6: Opening Balance
            worksheet.write(row, 0, 'Opening Balance:', formats['subtotal_label'])
            # Apply value-based formatting for opening balance
            opening_val = bank_data['opening_balance']
            if opening_val > 0:
                opening_fmt = formats['number']
            elif opening_val < 0:
                opening_fmt = formats['number_negative']
            else:
                opening_fmt = formats['number_zero']
            worksheet.write(row, 1, opening_val, opening_fmt)
            row += 1

            # Table headers row
            headers = ['Date', 'Reference', 'Partner', 'Account', 'Description', 'Debit', 'Credit', 'Balance']
            for col in range(5):
                worksheet.write(row, col, headers[col], formats['table_header'])
            for col in range(5, 8):
                worksheet.write(row, col, headers[col], formats['table_header_num'])

            # Freeze panes below header row
            worksheet.freeze_panes(row + 1, 0)
            row += 1

            # Data rows with alternating format
            for idx, line in enumerate(bank_data['lines']):
                is_alt = (idx % 2 == 1)
                text_fmt = formats['text_alt'] if is_alt else formats['text']

                # Date
                worksheet.write(row, 0, str(line['date']), text_fmt)
                # Reference
                worksheet.write(row, 1, line['ref'], text_fmt)
                # Partner
                worksheet.write(row, 2, line['partner'], text_fmt)
                # Account
                worksheet.write(row, 3, line['account'], text_fmt)
                # Description
                worksheet.write(row, 4, line['label'], text_fmt)

                # Debit - value-based formatting
                debit_val = line['debit']
                if debit_val > 0:
                    debit_fmt = formats['number_alt'] if is_alt else formats['number']
                elif debit_val < 0:
                    debit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
                else:
                    debit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
                worksheet.write(row, 5, debit_val, debit_fmt)

                # Credit - value-based formatting
                credit_val = line['credit']
                if credit_val > 0:
                    credit_fmt = formats['number_alt'] if is_alt else formats['number']
                elif credit_val < 0:
                    credit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
                else:
                    credit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
                worksheet.write(row, 6, credit_val, credit_fmt)

                # Balance - value-based formatting
                balance_val = line['balance']
                if balance_val > 0:
                    balance_fmt = formats['number_alt'] if is_alt else formats['number']
                elif balance_val < 0:
                    balance_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
                else:
                    balance_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
                worksheet.write(row, 7, balance_val, balance_fmt)

                row += 1

            # Total row
            worksheet.write(row, 0, 'TOTALS', formats['total_label'])
            worksheet.write(row, 1, '', formats['total_label'])
            worksheet.write(row, 2, '', formats['total_label'])
            worksheet.write(row, 3, '', formats['total_label'])
            worksheet.write(row, 4, '', formats['total_label'])
            worksheet.write(row, 5, bank_data['total_debit'], formats['total_number'])
            worksheet.write(row, 6, bank_data['total_credit'], formats['total_number'])
            worksheet.write(row, 7, bank_data['closing_balance'], formats['total_number'])

            # Set column widths
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:H', 15)

            # Page setup: Landscape, A4, fit to 1 page wide
            worksheet.set_landscape()
            worksheet.set_paper(9)  # A4
            worksheet.fit_to_pages(1, 0)

        # Summary worksheet
        summary = workbook.add_worksheet('Summary')

        # Phase 5 Corporate Header Structure for Summary
        row = 0
        # Row 0: Company name
        summary.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        summary.write(row, 0, 'Bank Book Summary', formats['report_title'])
        row += 1

        # Row 2: Report period
        summary.write(row, 0, f"Period: {data['date_from']} to {data['date_to']}", formats['metadata'])
        row += 1

        # Row 3: Generated timestamp and user
        generated = fields.Datetime.now().strftime('%Y-%m-%d %H:%M')
        summary.write(row, 0, f"Generated: {generated} by {self.env.user.name}", formats['metadata'])
        row += 2

        # Row 5: Filter bar with currency info
        filter_text = f"Journal: All Banks | Currency: {self.company_id.currency_id.name} | Branches: {data['branches']} | Status: {data['target_move']}"
        summary.merge_range(row, 0, row, 4, filter_text, formats['filter_bar'])
        row += 2

        # Summary headers row
        summary.write(row, 0, 'Bank Account', formats['table_header'])
        summary.write(row, 1, 'Opening', formats['table_header_num'])
        summary.write(row, 2, 'Debit', formats['table_header_num'])
        summary.write(row, 3, 'Credit', formats['table_header_num'])
        summary.write(row, 4, 'Closing', formats['table_header_num'])

        # Freeze panes below header row
        summary.freeze_panes(row + 1, 0)
        row += 1

        # Data rows
        for idx, bank_data in enumerate(data['banks_data']):
            is_alt = (idx % 2 == 1)
            text_fmt = formats['text_alt'] if is_alt else formats['text']

            # Bank name
            summary.write(row, 0, bank_data['journal'], text_fmt)

            # Opening - value-based formatting
            opening_val = bank_data['opening_balance']
            if opening_val > 0:
                opening_fmt = formats['number_alt'] if is_alt else formats['number']
            elif opening_val < 0:
                opening_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                opening_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            summary.write(row, 1, opening_val, opening_fmt)

            # Debit - value-based formatting
            debit_val = bank_data['total_debit']
            if debit_val > 0:
                debit_fmt = formats['number_alt'] if is_alt else formats['number']
            elif debit_val < 0:
                debit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                debit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            summary.write(row, 2, debit_val, debit_fmt)

            # Credit - value-based formatting
            credit_val = bank_data['total_credit']
            if credit_val > 0:
                credit_fmt = formats['number_alt'] if is_alt else formats['number']
            elif credit_val < 0:
                credit_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                credit_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            summary.write(row, 3, credit_val, credit_fmt)

            # Closing - value-based formatting
            closing_val = bank_data['closing_balance']
            if closing_val > 0:
                closing_fmt = formats['number_alt'] if is_alt else formats['number']
            elif closing_val < 0:
                closing_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                closing_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            summary.write(row, 4, closing_val, closing_fmt)

            row += 1

        # Grand total row
        summary.write(row, 0, 'GRAND TOTAL', formats['total_label'])
        summary.write(row, 1, data['grand_opening'], formats['total_number'])
        summary.write(row, 2, data['grand_debit'], formats['total_number'])
        summary.write(row, 3, data['grand_credit'], formats['total_number'])
        summary.write(row, 4, data['grand_closing'], formats['total_number'])

        # Set column widths
        summary.set_column('A:A', 30)
        summary.set_column('B:E', 15)

        # Page setup: Landscape, A4, fit to 1 page wide
        summary.set_landscape()
        summary.set_paper(9)  # A4
        summary.fit_to_pages(1, 0)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f'Bank_Book_{self.date_from}_{self.date_to}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """Return XML ID of the bank book report template."""
        return 'ops_matrix_accounting.report_bank_book_corporate'
