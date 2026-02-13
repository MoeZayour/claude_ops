# -*- coding: utf-8 -*-
"""
OPS Daily Financial Reports (v2 Data Contracts)
================================================

Cash Book, Day Book, Bank Book - refactored to use Shape A data contracts.
All three are line-based reports with running balances.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dataclasses import asdict
import logging

from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeAReport, LineGroup, LineEntry,
)

_logger = logging.getLogger(__name__)


class OpsCashBookWizard(models.TransientModel):
    """Cash Book Report Wizard."""
    _name = 'ops.cash.book.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Cash Book Report'

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

    date_from = fields.Date(
        string='From Date', required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='To Date', required=True, default=fields.Date.today
    )

    sort_by = fields.Selection([
        ('date', 'Date'),
        ('name', 'Reference'),
    ], string='Sort By', default='date')

    display_account = fields.Selection([
        ('all', 'All'),
        ('movement', 'With Movements'),
    ], string='Display Accounts', default='movement')

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'lines'

    def _get_report_titles(self):
        return {'cash_book': 'Cash Book'}

    def _get_scalar_fields_for_template(self):
        return ['sort_by', 'display_account', 'target_move']

    def _get_m2m_fields_for_template(self):
        return ['journal_ids', 'branch_ids']

    def _get_report_template_xmlid(self):
        return 'ops_matrix_accounting.report_cash_book_corporate'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.journal_ids = self.env['account.journal'].search([
                ('type', '=', 'cash'), ('company_id', '=', self.company_id.id)
            ]).ids
        else:
            self.journal_ids = []

    def _get_report_data(self):
        """Return ShapeAReport dict for cash book."""
        self.ensure_one()
        self._check_intelligence_access(self._get_engine_name())

        meta = build_report_meta(self, 'cash_book', 'Cash Book', 'lines')
        colors = build_report_colors(self.company_id)

        domain = [
            ('journal_id', 'in', self.journal_ids.ids),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))

        # Opening balance
        opening_domain = [
            ('journal_id', 'in', self.journal_ids.ids),
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('parent_state', '=', 'posted'),
        ]
        # Branch isolation
        opening_domain += self._get_branch_filter_domain()
        if self.branch_ids:
            opening_domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        opening_result = self.env['account.move.line'].read_group(
            opening_domain, ['balance:sum'], []
        )
        opening_balance = opening_result[0]['balance'] if opening_result else 0.0

        order = 'date asc, id asc' if self.sort_by == 'date' else 'move_name asc, id asc'
        move_lines = self.env['account.move.line'].search(domain, order=order)

        lines = []
        running_balance = opening_balance
        total_debit = 0.0
        total_credit = 0.0

        for ml in move_lines:
            running_balance += ml.balance
            total_debit += ml.debit
            total_credit += ml.credit
            lines.append(LineEntry(
                date=str(ml.date), entry=ml.move_id.name or '',
                journal=ml.journal_id.code or '',
                account_code=ml.account_id.code or '',
                account_name=ml.account_id.name or '',
                label=ml.name or '', partner=ml.partner_id.name or '',
                branch=ml.ops_branch_id.name if ml.ops_branch_id else '',
                debit=ml.debit, credit=ml.credit, balance=running_balance,
            ))

        group = LineGroup(
            group_key='cash',
            group_name='Cash Journals: ' + ', '.join(self.journal_ids.mapped('name')),
            opening_balance=opening_balance, lines=lines,
            total_debit=total_debit, total_credit=total_credit,
            closing_balance=running_balance,
        )

        return asdict(ShapeAReport(
            meta=meta, colors=colors, groups=[group],
            grand_totals={
                'opening_balance': opening_balance,
                'total_debit': total_debit, 'total_credit': total_credit,
                'closing_balance': running_balance,
            },
        ))

    def _return_report_action(self, data):
        return self.env.ref('ops_matrix_accounting.action_report_cash_book').report_action(self, data=data)

    def action_export_to_excel(self):
        """Delegate to base class Phase 5 Excel export."""
        return super().action_export_to_excel()


class OpsDayBookWizard(models.TransientModel):
    """Day Book Report Wizard."""
    _name = 'ops.day.book.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Day Book Report'

    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    journal_ids = fields.Many2many(
        'account.journal', 'ops_day_book_journal_rel',
        'wizard_id', 'journal_id', string='Journals',
    )

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'lines'

    def _get_report_titles(self):
        return {'day_book': 'Day Book'}

    def _get_scalar_fields_for_template(self):
        return ['target_move']

    def _get_m2m_fields_for_template(self):
        return ['journal_ids', 'branch_ids']

    def _get_report_template_xmlid(self):
        return 'ops_matrix_accounting.report_day_book_corporate'

    def _get_report_data(self):
        """Return ShapeAReport dict for day book, grouped by journal."""
        self.ensure_one()
        self._check_intelligence_access(self._get_engine_name())

        meta = build_report_meta(self, 'day_book', 'Day Book', 'lines')
        meta.date_from = str(self.date)
        meta.date_to = str(self.date)
        colors = build_report_colors(self.company_id)

        domain = [('date', '=', self.date), ('company_id', '=', self.company_id.id)]
        if self.target_move == 'posted':
            domain.append(('state', '=', 'posted'))
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))

        moves = self.env['account.move'].search(domain, order='journal_id, name asc')

        groups = []
        grand_debit = 0.0
        grand_credit = 0.0
        journals_seen = {}

        for move in moves:
            jname = move.journal_id.name
            jcode = move.journal_id.code
            if jname not in journals_seen:
                journals_seen[jname] = {'code': jcode, 'lines': [], 'total_debit': 0.0, 'total_credit': 0.0}
            for line in move.line_ids:
                journals_seen[jname]['lines'].append(LineEntry(
                    date=str(move.date), entry=move.name or '', journal=jcode,
                    account_code=line.account_id.code or '',
                    account_name=line.account_id.name or '',
                    label=line.name or '', ref=move.ref or '',
                    partner=move.partner_id.name or '',
                    branch=move.ops_branch_id.name if hasattr(move, 'ops_branch_id') and move.ops_branch_id else '',
                    debit=line.debit, credit=line.credit,
                ))
                journals_seen[jname]['total_debit'] += line.debit
                journals_seen[jname]['total_credit'] += line.credit

        for jname, jdata in journals_seen.items():
            grand_debit += jdata['total_debit']
            grand_credit += jdata['total_credit']
            groups.append(LineGroup(
                group_key=jdata['code'], group_name=jname,
                lines=jdata['lines'],
                total_debit=jdata['total_debit'], total_credit=jdata['total_credit'],
            ))

        return asdict(ShapeAReport(
            meta=meta, colors=colors, groups=groups,
            grand_totals={'total_debit': grand_debit, 'total_credit': grand_credit},
        ))

    def _return_report_action(self, data):
        return self.env.ref('ops_matrix_accounting.action_report_day_book').report_action(self, data=data)

    def action_export_to_excel(self):
        return super().action_export_to_excel()


class OpsBankBookWizard(models.TransientModel):
    """Bank Book Report Wizard."""
    _name = 'ops.bank.book.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Bank Book Report'

    journal_ids = fields.Many2many(
        'account.journal', 'ops_bank_book_journal_rel',
        'wizard_id', 'journal_id', string='Bank Journals', required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        default=lambda self: self.env['account.journal'].search([
            ('type', '=', 'bank'), ('company_id', '=', self.env.company.id)
        ])
    )
    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.today)
    group_by_journal = fields.Boolean(string='Group by Bank Account', default=True)

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'lines'

    def _get_report_titles(self):
        return {'bank_book': 'Bank Book'}

    def _get_scalar_fields_for_template(self):
        return ['target_move', 'group_by_journal']

    def _get_m2m_fields_for_template(self):
        return ['journal_ids', 'branch_ids']

    def _get_report_template_xmlid(self):
        return 'ops_matrix_accounting.report_bank_book_corporate'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.journal_ids = self.env['account.journal'].search([
                ('type', '=', 'bank'), ('company_id', '=', self.company_id.id)
            ]).ids
        else:
            self.journal_ids = []

    def _get_report_data(self):
        """Return ShapeAReport dict for bank book, one group per bank journal."""
        self.ensure_one()
        self._check_intelligence_access(self._get_engine_name())

        meta = build_report_meta(self, 'bank_book', 'Bank Book', 'lines')
        colors = build_report_colors(self.company_id)

        groups = []
        grand_opening = grand_closing = grand_debit = grand_credit = 0.0

        for journal in self.journal_ids:
            domain = [
                ('journal_id', '=', journal.id),
                ('date', '>=', self.date_from), ('date', '<=', self.date_to),
                ('company_id', '=', self.company_id.id),
            ]
            if self.target_move == 'posted':
                domain.append(('parent_state', '=', 'posted'))
            # Branch isolation -- ALWAYS included
            domain += self._get_branch_filter_domain()
            if self.branch_ids:
                domain.append(('ops_branch_id', 'in', self.branch_ids.ids))

            opening_domain = [
                ('journal_id', '=', journal.id),
                ('date', '<', self.date_from),
                ('company_id', '=', self.company_id.id),
                ('parent_state', '=', 'posted'),
            ]
            # Branch isolation
            opening_domain += self._get_branch_filter_domain()
            if self.branch_ids:
                opening_domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
            opening_result = self.env['account.move.line'].read_group(
                opening_domain, ['balance:sum'], []
            )
            journal_opening = opening_result[0]['balance'] if opening_result else 0.0

            move_lines = self.env['account.move.line'].search(domain, order='date asc, id asc')
            lines = []
            running_balance = journal_opening
            j_debit = j_credit = 0.0

            for ml in move_lines:
                running_balance += ml.balance
                j_debit += ml.debit
                j_credit += ml.credit
                lines.append(LineEntry(
                    date=str(ml.date), entry=ml.move_id.name or '',
                    journal=journal.code or '',
                    account_code=ml.account_id.code or '',
                    account_name=ml.account_id.name or '',
                    label=ml.name or '', partner=ml.partner_id.name or '',
                    branch=ml.ops_branch_id.name if ml.ops_branch_id else '',
                    debit=ml.debit, credit=ml.credit, balance=running_balance,
                ))

            groups.append(LineGroup(
                group_key=journal.code, group_name=journal.name,
                group_meta={'account': journal.default_account_id.display_name if journal.default_account_id else ''},
                opening_balance=journal_opening, lines=lines,
                total_debit=j_debit, total_credit=j_credit,
                closing_balance=running_balance,
            ))
            grand_opening += journal_opening
            grand_closing += running_balance
            grand_debit += j_debit
            grand_credit += j_credit

        return asdict(ShapeAReport(
            meta=meta, colors=colors, groups=groups,
            grand_totals={
                'opening_balance': grand_opening, 'total_debit': grand_debit,
                'total_credit': grand_credit, 'closing_balance': grand_closing,
            },
        ))

    def _return_report_action(self, data):
        return self.env.ref('ops_matrix_accounting.action_report_bank_book').report_action(self, data=data)

    def action_export_to_excel(self):
        return super().action_export_to_excel()
