# -*- coding: utf-8 -*-
"""
OPS Trial Balance Report Wizard (v2)
=====================================

Shape C report. Columns: Account Code, Account Name, Initial Debit,
Initial Credit, Period Debit, Period Credit, Ending Debit, Ending Credit.

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
    ShapeCReport, ColumnDef, MatrixRow,
)
import logging

_logger = logging.getLogger(__name__)


class OpsTBReportWizard(models.TransientModel):
    _name = 'ops.tb.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Trial Balance Report'

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
        'ops_tb_wiz_account_rel',
        'wizard_id', 'account_id',
        string='Accounts',
        help='Leave empty for all accounts.',
    )

    include_zero_balance = fields.Boolean(
        string='Include Zero Balances',
        default=False,
        help='Include accounts with zero ending balance.',
    )
    show_hierarchy = fields.Boolean(
        string='Show Account Groups',
        default=False,
        help='Display accounts grouped by their account group hierarchy.',
    )

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'matrix'

    def _get_report_titles(self):
        return {'tb': 'Trial Balance'}

    def _get_scalar_fields_for_template(self):
        return [
            'target_move', 'include_zero_balance', 'show_hierarchy',
        ]

    def _get_m2m_fields_for_template(self):
        return ['account_ids', 'branch_ids', 'business_unit_ids']

    # =========================================================================
    # Domain builders
    # =========================================================================

    def _build_period_domain(self):
        """Domain for period transactions."""
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

        # Branch isolation
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        return domain

    def _build_initial_domain(self):
        """Domain for initial balances (all posted moves before date_from)."""
        self.ensure_one()
        domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
        ]
        if self.account_ids:
            domain.append(('account_id', 'in', self.account_ids.ids))

        # Branch isolation
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        return domain

    # =========================================================================
    # Report data generation
    # =========================================================================

    def _get_report_data(self):
        """Build Shape C data for the Trial Balance."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        MoveLine = self.env['account.move.line']

        # --- Initial balances ---
        init_data = MoveLine._read_group(
            domain=self._build_initial_domain(),
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum'],
        )
        initial_map = {}
        for account, i_debit, i_credit, i_balance in init_data:
            if account:
                initial_map[account.id] = {
                    'debit': i_debit or 0.0,
                    'credit': i_credit or 0.0,
                    'balance': i_balance or 0.0,
                }

        # --- Period movements ---
        period_data = MoveLine._read_group(
            domain=self._build_period_domain(),
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum'],
        )
        period_map = {}
        for account, p_debit, p_credit, p_balance in period_data:
            if account:
                period_map[account.id] = {
                    'debit': p_debit or 0.0,
                    'credit': p_credit or 0.0,
                    'balance': p_balance or 0.0,
                }

        # --- Merge all account IDs ---
        all_acc_ids = set(initial_map.keys()) | set(period_map.keys())
        accounts = self.env['account.account'].browse(list(all_acc_ids))
        acc_lookup = {a.id: a for a in accounts}

        # --- Column definitions ---
        columns = [
            ColumnDef(key='account_code', label='Account Code', col_type='string', width=12, align='left'),
            ColumnDef(key='account_name', label='Account Name', col_type='string', width=30, align='left'),
            ColumnDef(key='initial_debit', label='Initial Debit', col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='initial_credit', label='Initial Credit', col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='period_debit', label='Period Debit', col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='period_credit', label='Period Credit', col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='ending_debit', label='Ending Debit', col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='ending_credit', label='Ending Credit', col_type='currency', width=15, align='right', subtotal=True),
        ]

        # --- Rows ---
        rows = []
        totals = {
            'initial_debit': 0.0, 'initial_credit': 0.0,
            'period_debit': 0.0, 'period_credit': 0.0,
            'ending_debit': 0.0, 'ending_credit': 0.0,
        }

        sorted_ids = sorted(all_acc_ids, key=lambda aid: acc_lookup.get(aid, self.env['account.account']).code or '')

        for acc_id in sorted_ids:
            account = acc_lookup.get(acc_id)
            if not account:
                continue

            init = initial_map.get(acc_id, {'debit': 0.0, 'credit': 0.0, 'balance': 0.0})
            period = period_map.get(acc_id, {'debit': 0.0, 'credit': 0.0, 'balance': 0.0})

            initial_balance = init['balance']
            period_debit = period['debit']
            period_credit = period['credit']
            ending_balance = initial_balance + (period_debit - period_credit)

            # Split initial and ending into debit/credit presentation
            initial_debit = initial_balance if initial_balance > 0 else 0.0
            initial_credit = abs(initial_balance) if initial_balance < 0 else 0.0
            ending_debit = ending_balance if ending_balance > 0 else 0.0
            ending_credit = abs(ending_balance) if ending_balance < 0 else 0.0

            # Filter zero-balance accounts if requested
            if not self.include_zero_balance:
                if (abs(ending_balance) < 0.005 and abs(period_debit) < 0.005
                        and abs(period_credit) < 0.005 and abs(initial_balance) < 0.005):
                    continue

            rows.append(MatrixRow(
                level=0,
                style='detail',
                values={
                    'account_code': account.code or '',
                    'account_name': account.name or '',
                    'initial_debit': initial_debit,
                    'initial_credit': initial_credit,
                    'period_debit': period_debit,
                    'period_credit': period_credit,
                    'ending_debit': ending_debit,
                    'ending_credit': ending_credit,
                },
            ))

            totals['initial_debit'] += initial_debit
            totals['initial_credit'] += initial_credit
            totals['period_debit'] += period_debit
            totals['period_credit'] += period_credit
            totals['ending_debit'] += ending_debit
            totals['ending_credit'] += ending_credit

        # --- Assemble Shape C report ---
        meta = build_report_meta(self, 'tb', 'Trial Balance', 'matrix')
        colors = build_report_colors(self.company_id)

        report = ShapeCReport(
            meta=meta,
            colors=colors,
            columns=columns,
            rows=rows,
            totals=totals,
        )

        return asdict(report)

    # =========================================================================
    # Report action
    # =========================================================================

    def _return_report_action(self, data):
        report = self.env.ref('ops_matrix_accounting.action_report_tb')
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
