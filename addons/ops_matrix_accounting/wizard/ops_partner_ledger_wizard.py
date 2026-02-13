# -*- coding: utf-8 -*-
"""
OPS Partner Ledger & Statement of Account Wizard (v2)
======================================================

Shape A report. Per-partner grouping with opening balances and
per-partner running balances.

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


class OpsPartnerLedgerWizard(models.TransientModel):
    _name = 'ops.partner.ledger.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Partner Ledger / Statement of Account'

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

    partner_ids = fields.Many2many(
        'res.partner',
        'ops_pl_wiz_partner_rel',
        'wizard_id', 'partner_id',
        string='Partners',
        help='Leave empty for all partners.',
    )

    partner_type = fields.Selection([
        ('customer', 'Customers'),
        ('vendor', 'Vendors'),
        ('all', 'All Partners'),
    ], string='Partner Type', default='all', required=True)

    report_type = fields.Selection([
        ('partner_ledger', 'Partner Ledger'),
        ('soa', 'Statement of Account'),
    ], string='Report Type', default='partner_ledger', required=True)

    include_initial_balance = fields.Boolean(
        string='Include Initial Balance',
        default=True,
    )

    reconciled = fields.Selection([
        ('all', 'All Items'),
        ('reconciled', 'Reconciled Only'),
        ('unreconciled', 'Unreconciled Only'),
    ], string='Reconciliation Status', default='all', required=True)

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'lines'

    def _get_report_titles(self):
        return {
            'partner_ledger': 'Partner Ledger',
            'soa': 'Statement of Account',
        }

    def _get_scalar_fields_for_template(self):
        return [
            'target_move', 'partner_type', 'report_type',
            'include_initial_balance', 'reconciled',
        ]

    def _get_m2m_fields_for_template(self):
        return ['partner_ids', 'branch_ids', 'business_unit_ids']

    # =========================================================================
    # Domain builders
    # =========================================================================

    def _build_period_domain(self):
        """Build domain for move lines within the period."""
        self.ensure_one()
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
        ]
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))

        # Partner filters
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        elif self.partner_type == 'customer':
            domain.append(('partner_id.customer_rank', '>', 0))
        elif self.partner_type == 'vendor':
            domain.append(('partner_id.supplier_rank', '>', 0))

        # Reconciliation filter
        if self.reconciled == 'reconciled':
            domain.append(('reconciled', '=', True))
        elif self.reconciled == 'unreconciled':
            domain.append(('reconciled', '=', False))

        # Branch isolation
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))

        return domain

    def _build_initial_domain(self):
        """Build domain for initial balances (all posted moves before date_from)."""
        self.ensure_one()
        domain = [
            ('date', '<', self.date_from),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
        ]
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        elif self.partner_type == 'customer':
            domain.append(('partner_id.customer_rank', '>', 0))
        elif self.partner_type == 'vendor':
            domain.append(('partner_id.supplier_rank', '>', 0))

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
        """Build Shape A data for Partner Ledger / SOA."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        MoveLine = self.env['account.move.line']

        # --- Initial balances per partner ---
        initial_map = {}  # partner_id -> balance
        if self.include_initial_balance:
            init_data = MoveLine._read_group(
                domain=self._build_initial_domain(),
                groupby=['partner_id'],
                aggregates=['balance:sum'],
            )
            for partner, total_balance in init_data:
                if partner:
                    initial_map[partner.id] = total_balance or 0.0

        # --- Period move lines ---
        period_domain = self._build_period_domain()
        lines = MoveLine.search(period_domain, order='partner_id, date, id')

        # --- Group by partner ---
        partner_groups = {}  # partner_id -> {partner, lines}
        for line in lines:
            p_id = line.partner_id.id if line.partner_id else 0
            if p_id not in partner_groups:
                partner_groups[p_id] = {
                    'partner': line.partner_id,
                    'partner_name': line.partner_id.name if line.partner_id else 'No Partner',
                    'lines': [],
                }
            partner_groups[p_id]['lines'].append(line)

        # Also include partners with only initial balance
        if self.include_initial_balance:
            for p_id, balance in initial_map.items():
                if p_id not in partner_groups:
                    partner = self.env['res.partner'].browse(p_id)
                    if partner.exists():
                        partner_groups[p_id] = {
                            'partner': partner,
                            'partner_name': partner.name or 'Unknown',
                            'lines': [],
                        }

        # --- Build LineGroup list with per-partner running balance ---
        groups = []
        grand_total_debit = 0.0
        grand_total_credit = 0.0

        sorted_partner_ids = sorted(
            partner_groups.keys(),
            key=lambda pid: partner_groups[pid]['partner_name'],
        )

        for p_id in sorted_partner_ids:
            pgroup = partner_groups[p_id]
            partner_name = pgroup['partner_name']
            p_lines = pgroup['lines']

            opening = initial_map.get(p_id, 0.0)

            # Per-partner running balance
            running = opening
            entries = []
            group_debit = 0.0
            group_credit = 0.0

            for line in p_lines:
                running += (line.debit - line.credit)
                group_debit += line.debit
                group_credit += line.credit

                entries.append(LineEntry(
                    date=str(line.date),
                    entry=line.move_id.name or '',
                    journal=line.journal_id.code or '',
                    account_code=line.account_id.code or '',
                    account_name=line.account_id.name or '',
                    label=line.name or '',
                    ref=line.ref or '',
                    partner=partner_name,
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
                group_key=str(p_id),
                group_name=partner_name,
                group_meta={'partner_id': p_id},
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
        title = 'Statement of Account' if self.report_type == 'soa' else 'Partner Ledger'
        report_code = 'soa' if self.report_type == 'soa' else 'partner_ledger'
        meta = build_report_meta(self, report_code, title, 'lines')
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
                'date', 'entry', 'journal', 'account_code', 'label',
                'ref', 'debit', 'credit', 'balance',
            ],
        )

        return asdict(report)

    # =========================================================================
    # Report action
    # =========================================================================

    def _return_report_action(self, data):
        action_map = {
            'partner_ledger': 'ops_matrix_accounting.action_report_partner_ledger',
            'soa': 'ops_matrix_accounting.action_report_soa',
        }
        ref = action_map.get(self.report_type, action_map['partner_ledger'])
        report = self.env.ref(ref)
        return report.report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_filters_extra(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both From Date and To Date."))
        if self.report_type == 'soa' and not self.partner_ids:
            raise UserError(_(
                "Statement of Account requires at least one partner to be selected."
            ))
        return True
