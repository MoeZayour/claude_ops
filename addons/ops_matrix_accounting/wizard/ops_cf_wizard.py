# -*- coding: utf-8 -*-
"""
OPS Cash Flow Statement Wizard (v2)
=====================================

Shape B report. Indirect method: Net Income + adjustments grouped into
Operating / Investing / Financing activities.

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
    ShapeBReport, HierarchyNode,
)
import logging

_logger = logging.getLogger(__name__)

# Account type classification for cash flow
PNL_TYPES = [
    'income', 'income_other',
    'expense', 'expense_depreciation', 'expense_direct_cost',
]
DEPRECIATION_TYPES = ['expense_depreciation']
WORKING_CAPITAL_TYPES = [
    'asset_receivable', 'asset_current', 'asset_prepayments',
    'liability_payable', 'liability_current', 'liability_credit_card',
]
INVESTING_TYPES = ['asset_non_current', 'asset_fixed']
FINANCING_LIABILITY_TYPES = ['liability_non_current']
FINANCING_EQUITY_TYPES = ['equity', 'equity_unaffected']
CASH_TYPES = ['asset_cash']


class OpsCFReportWizard(models.TransientModel):
    _name = 'ops.cf.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Cash Flow Statement'

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

    method = fields.Selection([
        ('indirect', 'Indirect Method'),
        ('direct', 'Direct Method'),
    ], string='Method', default='indirect', required=True)

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'hierarchy'

    def _get_report_titles(self):
        return {'cf': 'Cash Flow Statement'}

    def _get_scalar_fields_for_template(self):
        return ['target_move', 'method']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'business_unit_ids']

    # =========================================================================
    # Domain helpers
    # =========================================================================

    def _build_cf_domain(self, account_types):
        """Build domain for balance-sheet / P&L type queries within the period."""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('account_id.account_type', 'in', account_types),
        ]
        if self.target_move == 'posted':
            domain.append(('move_id.state', '=', 'posted'))

        # Branch isolation
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        return domain

    def _query_type_balance(self, account_types):
        """Get total balance for a set of account types within the period."""
        if not account_types:
            return 0.0
        domain = self._build_cf_domain(account_types)
        data = self.env['account.move.line']._read_group(
            domain=domain,
            groupby=[],
            aggregates=['balance:sum'],
        )
        return data[0][0] or 0.0 if data else 0.0

    def _query_type_detail(self, account_types):
        """Get per-account balance for a set of account types.

        Returns list of dicts: [{code, name, balance}, ...]
        """
        if not account_types:
            return []
        domain = self._build_cf_domain(account_types)
        data = self.env['account.move.line']._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['balance:sum'],
        )
        result = []
        for account, total_balance in data:
            if not account:
                continue
            result.append({
                'code': account.code or '',
                'name': account.name or '',
                'balance': total_balance or 0.0,
            })
        return sorted(result, key=lambda x: x['code'])

    # =========================================================================
    # Report data generation
    # =========================================================================

    def _get_report_data(self):
        """Build Shape B data for Cash Flow Statement (indirect method)."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        # =====================================================================
        # 1. Net Income from P&L accounts
        # =====================================================================
        pnl_balance = self._query_type_balance(PNL_TYPES)
        net_income = -pnl_balance  # Credit-heavy income → positive

        # =====================================================================
        # 2. OPERATING ACTIVITIES
        # =====================================================================
        # Depreciation add-back
        depr_balance = self._query_type_balance(DEPRECIATION_TYPES)
        depreciation_addback = depr_balance  # Expense (positive balance) → add back

        # Working capital changes
        wc_details = self._query_type_detail(WORKING_CAPITAL_TYPES)
        wc_children = []
        total_wc_change = 0.0
        for item in wc_details:
            # For current assets: increase (positive balance) = cash outflow (negative)
            # For current liabilities: increase (negative balance, credit-heavy) = cash inflow (positive)
            acc_type_balance = item['balance']
            wc_children.append(HierarchyNode(
                code=item['code'], name=item['name'],
                level=2, style='detail',
                values={'amount': -acc_type_balance},
            ))
            total_wc_change += -acc_type_balance

        operating_children = [
            HierarchyNode(
                name='Net Income', level=1, style='group',
                values={'amount': net_income},
            ),
            HierarchyNode(
                name='Depreciation & Amortization', level=1, style='group',
                values={'amount': depreciation_addback},
            ),
            HierarchyNode(
                name='Changes in Working Capital', level=1, style='group',
                values={'amount': total_wc_change},
                children=wc_children,
            ),
        ]
        total_operating = net_income + depreciation_addback + total_wc_change
        operating_section = HierarchyNode(
            name='Cash from Operating Activities', level=0, style='section',
            values={'amount': total_operating},
            children=operating_children,
        )

        # =====================================================================
        # 3. INVESTING ACTIVITIES
        # =====================================================================
        inv_details = self._query_type_detail(INVESTING_TYPES)
        inv_children = []
        total_investing = 0.0
        for item in inv_details:
            # Increase in fixed assets (positive balance) = cash outflow (negative)
            inv_children.append(HierarchyNode(
                code=item['code'], name=item['name'],
                level=2, style='detail',
                values={'amount': -item['balance']},
            ))
            total_investing += -item['balance']

        investing_section = HierarchyNode(
            name='Cash from Investing Activities', level=0, style='section',
            values={'amount': total_investing},
            children=inv_children,
        )

        # =====================================================================
        # 4. FINANCING ACTIVITIES
        # =====================================================================
        fin_liab_details = self._query_type_detail(FINANCING_LIABILITY_TYPES)
        fin_equity_details = self._query_type_detail(FINANCING_EQUITY_TYPES)

        fin_children = []
        total_financing = 0.0

        for item in fin_liab_details:
            # Increase in long-term debt (credit-heavy, negative balance) = cash inflow
            amount = -item['balance']
            fin_children.append(HierarchyNode(
                code=item['code'], name=item['name'],
                level=2, style='detail',
                values={'amount': amount},
            ))
            total_financing += amount

        for item in fin_equity_details:
            # Increase in equity (credit-heavy) = cash inflow
            amount = -item['balance']
            fin_children.append(HierarchyNode(
                code=item['code'], name=item['name'],
                level=2, style='detail',
                values={'amount': amount},
            ))
            total_financing += amount

        financing_section = HierarchyNode(
            name='Cash from Financing Activities', level=0, style='section',
            values={'amount': total_financing},
            children=fin_children,
        )

        # =====================================================================
        # 5. NET CHANGE IN CASH
        # =====================================================================
        net_change = total_operating + total_investing + total_financing
        net_result = HierarchyNode(
            name='Net Change in Cash & Cash Equivalents', level=0, style='grand_total',
            values={'amount': net_change},
        )

        # --- Assemble Shape B report ---
        meta = build_report_meta(self, 'cf', 'Cash Flow Statement', 'hierarchy')
        colors = build_report_colors(self.company_id)

        report = ShapeBReport(
            meta=meta,
            colors=colors,
            value_columns=[{'key': 'amount', 'label': 'Amount'}],
            sections=[operating_section, investing_section, financing_section],
            net_result=net_result,
        )

        return asdict(report)

    # =========================================================================
    # Report action
    # =========================================================================

    def _return_report_action(self, data):
        report = self.env.ref('ops_matrix_accounting.action_report_cf')
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
