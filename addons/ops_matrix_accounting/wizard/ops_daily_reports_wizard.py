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

_logger = logging.getLogger(__name__)


class OpsCashBookWizard(models.TransientModel):
    """Cash Book Report Wizard."""
    _name = 'ops.cash.book.wizard'
    _description = 'Cash Book Report'

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

    def action_print_pdf(self):
        """Generate PDF report."""
        data = {'wizard_id': self.id, 'report_data': self._get_report_data()}
        return self.env.ref('ops_matrix_accounting.action_report_cash_book').report_action(self, data=data)

    def action_export_excel(self):
        """Export to Excel."""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('xlsxwriter library is required for Excel export. Please install it.'))

        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Cash Book')

        # Formats
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 14, 'bg_color': '#4472C4', 'font_color': 'white'
        })
        subheader_format = workbook.add_format({
            'bold': True, 'align': 'left', 'font_size': 11
        })
        col_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'bg_color': '#D9E1F2',
            'border': 1
        })
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'bg_color': '#E2EFDA', 'border': 1
        })

        # Title
        worksheet.merge_range('A1:H1', f"Cash Book - {data['company']}", header_format)
        worksheet.write('A2', f"Period: {data['date_from']} to {data['date_to']}", subheader_format)
        worksheet.write('A3', f"Journals: {data['journals']}", subheader_format)
        worksheet.write('A4', f"Branches: {data['branches']}", subheader_format)

        # Opening Balance
        worksheet.write('A6', 'Opening Balance:', subheader_format)
        worksheet.write('B6', data['opening_balance'], money_format)

        # Column Headers
        headers = ['Date', 'Reference', 'Partner', 'Account', 'Description', 'Debit', 'Credit', 'Balance']
        for col, header in enumerate(headers):
            worksheet.write(7, col, header, col_header_format)

        # Data rows
        row = 8
        for line in data['lines']:
            worksheet.write(row, 0, str(line['date']), date_format)
            worksheet.write(row, 1, line['ref'], text_format)
            worksheet.write(row, 2, line['partner'], text_format)
            worksheet.write(row, 3, line['account'], text_format)
            worksheet.write(row, 4, line['label'], text_format)
            worksheet.write(row, 5, line['debit'], money_format)
            worksheet.write(row, 6, line['credit'], money_format)
            worksheet.write(row, 7, line['balance'], money_format)
            row += 1

        # Totals
        worksheet.write(row, 4, 'TOTALS', col_header_format)
        worksheet.write(row, 5, data['total_debit'], total_format)
        worksheet.write(row, 6, data['total_credit'], total_format)
        worksheet.write(row, 7, data['closing_balance'], total_format)

        # Set column widths
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:H', 15)

        workbook.close()
        output.seek(0)

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Cash_Book_{self.date_from}_{self.date_to}.xlsx',
            'type': 'binary',
            'datas': output.read().encode('base64') if hasattr(output.read(), 'encode') else __import__('base64').b64encode(output.getvalue()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """Return XML ID of the cash book report template."""
        return 'ops_matrix_accounting.report_cash_book'


class OpsDayBookWizard(models.TransientModel):
    """Day Book Report Wizard - All transactions for a day."""
    _name = 'ops.day.book.wizard'
    _description = 'Day Book Report'

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

    def action_print_pdf(self):
        """Generate PDF report."""
        data = {'wizard_id': self.id, 'report_data': self._get_report_data()}
        return self.env.ref('ops_matrix_accounting.action_report_day_book').report_action(self, data=data)

    def action_export_excel(self):
        """Export to Excel."""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('xlsxwriter library is required for Excel export. Please install it.'))

        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Day Book')

        # Formats
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 14, 'bg_color': '#4472C4', 'font_color': 'white'
        })
        journal_format = workbook.add_format({
            'bold': True, 'align': 'left', 'font_size': 12,
            'bg_color': '#D9E1F2', 'border': 1
        })
        move_format = workbook.add_format({
            'bold': True, 'align': 'left', 'bg_color': '#FCE4D6', 'border': 1
        })
        col_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'bg_color': '#E2EFDA', 'border': 1
        })
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'bg_color': '#E2EFDA', 'border': 1
        })

        # Title
        worksheet.merge_range('A1:F1', f"Day Book - {data['company']}", header_format)
        worksheet.write('A2', f"Date: {data['date']}")
        worksheet.write('A3', f"Branches: {data['branches']}")

        row = 5
        for journal_data in data['journals_data']:
            # Journal header
            worksheet.merge_range(row, 0, row, 5, f"Journal: {journal_data['journal']}", journal_format)
            row += 1

            for move in journal_data['moves']:
                # Move header
                worksheet.merge_range(row, 0, row, 5,
                    f"{move['name']} - {move['partner']} - {move['ref']}", move_format)
                row += 1

                # Column headers
                worksheet.write(row, 0, 'Account', col_header_format)
                worksheet.write(row, 1, 'Description', col_header_format)
                worksheet.write(row, 2, 'Debit', col_header_format)
                worksheet.write(row, 3, 'Credit', col_header_format)
                row += 1

                # Lines
                for line in move['lines']:
                    worksheet.write(row, 0, line['account'], text_format)
                    worksheet.write(row, 1, line['label'], text_format)
                    worksheet.write(row, 2, line['debit'], money_format)
                    worksheet.write(row, 3, line['credit'], money_format)
                    row += 1

                row += 1  # Space between moves

            # Journal total
            worksheet.write(row, 1, f"Journal Total: {journal_data['journal']}", col_header_format)
            worksheet.write(row, 2, journal_data['total_debit'], total_format)
            worksheet.write(row, 3, journal_data['total_credit'], total_format)
            row += 2

        # Grand totals
        worksheet.write(row, 1, 'GRAND TOTAL', col_header_format)
        worksheet.write(row, 2, data['grand_total_debit'], total_format)
        worksheet.write(row, 3, data['grand_total_credit'], total_format)

        # Set column widths
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:D', 15)

        workbook.close()
        output.seek(0)

        import base64
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
        return 'ops_matrix_accounting.report_day_book'


class OpsBankBookWizard(models.TransientModel):
    """Bank Book Report Wizard."""
    _name = 'ops.bank.book.wizard'
    _description = 'Bank Book Report'

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

    def action_print_pdf(self):
        """Generate PDF report."""
        data = {'wizard_id': self.id, 'report_data': self._get_report_data()}
        return self.env.ref('ops_matrix_accounting.action_report_bank_book').report_action(self, data=data)

    def action_export_excel(self):
        """Export to Excel."""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_('xlsxwriter library is required for Excel export. Please install it.'))

        data = self._get_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Formats
        header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 14, 'bg_color': '#4472C4', 'font_color': 'white'
        })
        bank_format = workbook.add_format({
            'bold': True, 'align': 'left', 'font_size': 12,
            'bg_color': '#D9E1F2', 'border': 1
        })
        subheader_format = workbook.add_format({
            'bold': True, 'align': 'left', 'font_size': 11
        })
        col_header_format = workbook.add_format({
            'bold': True, 'align': 'center', 'bg_color': '#E2EFDA', 'border': 1
        })
        money_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00', 'bg_color': '#E2EFDA', 'border': 1
        })

        for bank_data in data['banks_data']:
            # Create worksheet for each bank
            ws_name = bank_data['journal_code'][:31] if len(bank_data['journal_code']) > 31 else bank_data['journal_code']
            worksheet = workbook.add_worksheet(ws_name)

            # Title
            worksheet.merge_range('A1:H1', f"Bank Book - {data['company']}", header_format)
            worksheet.merge_range('A2:H2', f"Bank: {bank_data['journal']} ({bank_data['account']})", bank_format)
            worksheet.write('A3', f"Period: {data['date_from']} to {data['date_to']}", subheader_format)
            worksheet.write('A4', f"Branches: {data['branches']}", subheader_format)

            # Opening Balance
            worksheet.write('A6', 'Opening Balance:', subheader_format)
            worksheet.write('B6', bank_data['opening_balance'], money_format)

            # Column Headers
            headers = ['Date', 'Reference', 'Partner', 'Account', 'Description', 'Debit', 'Credit', 'Balance']
            for col, hdr in enumerate(headers):
                worksheet.write(7, col, hdr, col_header_format)

            # Data rows
            row = 8
            for line in bank_data['lines']:
                worksheet.write(row, 0, str(line['date']), date_format)
                worksheet.write(row, 1, line['ref'], text_format)
                worksheet.write(row, 2, line['partner'], text_format)
                worksheet.write(row, 3, line['account'], text_format)
                worksheet.write(row, 4, line['label'], text_format)
                worksheet.write(row, 5, line['debit'], money_format)
                worksheet.write(row, 6, line['credit'], money_format)
                worksheet.write(row, 7, line['balance'], money_format)
                row += 1

            # Totals
            worksheet.write(row, 4, 'TOTALS', col_header_format)
            worksheet.write(row, 5, bank_data['total_debit'], total_format)
            worksheet.write(row, 6, bank_data['total_credit'], total_format)
            worksheet.write(row, 7, bank_data['closing_balance'], total_format)

            # Set column widths
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:H', 15)

        # Summary worksheet
        summary = workbook.add_worksheet('Summary')
        summary.merge_range('A1:E1', f"Bank Book Summary - {data['company']}", header_format)
        summary.write('A2', f"Period: {data['date_from']} to {data['date_to']}", subheader_format)

        # Summary headers
        summary.write(4, 0, 'Bank Account', col_header_format)
        summary.write(4, 1, 'Opening', col_header_format)
        summary.write(4, 2, 'Debit', col_header_format)
        summary.write(4, 3, 'Credit', col_header_format)
        summary.write(4, 4, 'Closing', col_header_format)

        row = 5
        for bank_data in data['banks_data']:
            summary.write(row, 0, bank_data['journal'], text_format)
            summary.write(row, 1, bank_data['opening_balance'], money_format)
            summary.write(row, 2, bank_data['total_debit'], money_format)
            summary.write(row, 3, bank_data['total_credit'], money_format)
            summary.write(row, 4, bank_data['closing_balance'], money_format)
            row += 1

        # Grand totals
        summary.write(row, 0, 'GRAND TOTAL', col_header_format)
        summary.write(row, 1, data['grand_opening'], total_format)
        summary.write(row, 2, data['grand_debit'], total_format)
        summary.write(row, 3, data['grand_credit'], total_format)
        summary.write(row, 4, data['grand_closing'], total_format)

        summary.set_column('A:A', 30)
        summary.set_column('B:E', 15)

        workbook.close()
        output.seek(0)

        import base64
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
        return 'ops_matrix_accounting.report_bank_book'
