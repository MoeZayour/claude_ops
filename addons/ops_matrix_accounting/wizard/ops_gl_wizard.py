# -*- coding: utf-8 -*-
"""
OPS General Ledger Report Wizard (v2)
=====================================

Shape A report. Groups journal entry lines by account with
opening balances and per-account running balances.

Author: OPS Matrix Framework
Version: 2.0 (Report Engine v2 - Phase 3)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import date_utils
from dataclasses import asdict
from datetime import datetime
from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeAReport, LineGroup, LineEntry,
)
import logging

_logger = logging.getLogger(__name__)


class OpsGLReportWizard(models.TransientModel):
    _name = 'ops.gl.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'General Ledger Report'

    # =========================================================================
    # Fields
    # =========================================================================
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: date_utils.start_of(datetime.now(), 'year'),
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: date_utils.end_of(datetime.now(), 'month'),
    )

    account_ids = fields.Many2many(
        'account.account',
        'ops_gl_wiz_account_rel',
        'wizard_id', 'account_id',
        string='Accounts',
        help='Leave empty for all accounts.',
    )
    journal_ids = fields.Many2many(
        'account.journal',
        'ops_gl_wiz_journal_rel',
        'wizard_id', 'journal_id',
        string='Journals',
        help='Leave empty for all journals.',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'ops_gl_wiz_partner_rel',
        'wizard_id', 'partner_id',
        string='Partners',
        help='Leave empty for all partners.',
    )

    include_initial_balance = fields.Boolean(
        string='Include Initial Balance',
        default=True,
        help='Show opening balance before the selected period.',
    )
    display_account = fields.Selection([
        ('all', 'All Accounts'),
        ('movement', 'With Movements'),
        ('balance', 'With Balance Not Zero'),
    ], string='Display Accounts', default='movement', required=True)

    sort_by = fields.Selection([
        ('date', 'Date'),
        ('account', 'Account'),
        ('partner', 'Partner'),
    ], string='Sort By', default='date', required=True)

    report_format = fields.Selection([
        ('detailed', 'Detailed Lines'),
        ('summary', 'Summary Only'),
    ], string='Report Format', default='detailed', required=True)

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'lines'

    def _get_report_titles(self):
        return {'gl': 'General Ledger'}

    def _get_scalar_fields_for_template(self):
        return [
            'target_move', 'display_account', 'sort_by',
            'report_format', 'include_initial_balance',
        ]

    def _get_m2m_fields_for_template(self):
        return [
            'account_ids', 'journal_ids', 'partner_ids',
            'branch_ids', 'business_unit_ids',
        ]

    # =========================================================================
    # Domain builders
    # =========================================================================

    def _build_base_domain(self):
        """Build the base domain for move lines within the period."""
        self.ensure_one()
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
        ]
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()

        # Wizard-selected branch/BU filters
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))

        return domain

    def _build_initial_balance_domain(self):
        """Build domain for opening-balance query (all POSTED moves before date_from)."""
        self.ensure_one()
        domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
        ]
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        # Branch isolation
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))

        return domain

    # =========================================================================
    # Sort helper
    # =========================================================================

    def _get_sort_order(self):
        sort_map = {
            'date': 'account_id, date, id',
            'account': 'account_id, date, id',
            'partner': 'account_id, partner_id, date, id',
        }
        return sort_map.get(self.sort_by, 'account_id, date, id')

    # =========================================================================
    # Report data generation
    # =========================================================================

    def _get_report_data(self):
        """Build Shape A data for the General Ledger."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        MoveLine = self.env['account.move.line']

        # --- Initial balances per account ---
        initial_map = {}  # account_id -> balance float
        if self.include_initial_balance:
            init_domain = self._build_initial_balance_domain()
            init_data = MoveLine._read_group(
                domain=init_domain,
                groupby=['account_id'],
                aggregates=['debit:sum', 'credit:sum', 'balance:sum'],
            )
            for account, total_debit, total_credit, total_balance in init_data:
                if account:
                    initial_map[account.id] = total_balance or 0.0

        # --- Period move lines ---
        period_domain = self._build_base_domain()
        order = self._get_sort_order()
        lines = MoveLine.search(period_domain, order=order)

        # --- Group by account ---
        account_groups = {}  # account_id -> list of move.lines
        for line in lines:
            acc_id = line.account_id.id
            if acc_id not in account_groups:
                account_groups[acc_id] = {
                    'account': line.account_id,
                    'lines': [],
                }
            account_groups[acc_id]['lines'].append(line)

        # If display_account == 'all', we also need accounts with initial
        # balances but no period movements
        if self.display_account == 'all':
            for acc_id, balance in initial_map.items():
                if acc_id not in account_groups:
                    account = self.env['account.account'].browse(acc_id)
                    if account.exists():
                        account_groups[acc_id] = {
                            'account': account,
                            'lines': [],
                        }

        # --- Build LineGroup list with running balance per group ---
        groups = []
        grand_total_debit = 0.0
        grand_total_credit = 0.0

        # Sort groups by account code
        sorted_acc_ids = sorted(
            account_groups.keys(),
            key=lambda aid: account_groups[aid]['account'].code or '',
        )

        for acc_id in sorted_acc_ids:
            group_data = account_groups[acc_id]
            account = group_data['account']
            acc_lines = group_data['lines']

            opening = initial_map.get(acc_id, 0.0)

            # Apply display_account filter
            has_movement = len(acc_lines) > 0
            period_balance = sum(l.debit - l.credit for l in acc_lines)
            closing = opening + period_balance

            if self.display_account == 'movement' and not has_movement:
                continue
            if self.display_account == 'balance' and abs(closing) < 0.005:
                continue

            # Build line entries with per-group running balance
            running = opening
            entries = []
            group_debit = 0.0
            group_credit = 0.0

            for line in acc_lines:
                running += (line.debit - line.credit)
                group_debit += line.debit
                group_credit += line.credit

                entries.append(LineEntry(
                    date=str(line.date),
                    entry=line.move_id.name or '',
                    journal=line.journal_id.code or '',
                    account_code=account.code or '',
                    account_name=account.name or '',
                    label=line.name or '',
                    ref=line.ref or '',
                    partner=line.partner_id.name if line.partner_id else '',
                    branch=line.ops_branch_id.name if line.ops_branch_id else '',
                    bu=line.ops_business_unit_id.name if line.ops_business_unit_id else '',
                    debit=line.debit,
                    credit=line.credit,
                    balance=running,
                    currency=line.currency_id.name if line.currency_id else '',
                    amount_currency=line.amount_currency or 0.0,
                    reconciled=line.reconciled if hasattr(line, 'reconciled') else False,
                ))

            group = LineGroup(
                group_key=account.code or str(acc_id),
                group_name='{} {}'.format(account.code or '', account.name or ''),
                group_meta={'account_id': acc_id, 'account_type': account.account_type},
                opening_balance=opening,
                lines=entries,
                total_debit=group_debit,
                total_credit=group_credit,
                closing_balance=running,
            )
            groups.append(group)
            grand_total_debit += group_debit
            grand_total_credit += group_credit

        # --- Assemble Shape A report ---
        meta = build_report_meta(self, 'gl', 'General Ledger', 'lines')
        colors = build_report_colors(self.company_id)

        report = ShapeAReport(
            meta=meta,
            colors=colors,
            groups=groups,
            grand_totals={
                'total_debit': grand_total_debit,
                'total_credit': grand_total_credit,
                'total_balance': grand_total_debit - grand_total_credit,
            },
            visible_columns=[
                'date', 'entry', 'journal', 'label', 'ref', 'partner',
                'branch', 'bu', 'debit', 'credit', 'balance',
            ],
        )

        return asdict(report)

    # =========================================================================
    # Report action
    # =========================================================================

    def _return_report_action(self, data):
        """Return PDF report action for the General Ledger."""
        report = self.env.ref('ops_matrix_accounting.action_report_gl')
        return report.report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_filters_extra(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both From Date and To Date."))
        return True
