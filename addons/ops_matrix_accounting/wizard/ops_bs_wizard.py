# -*- coding: utf-8 -*-
"""
OPS Balance Sheet Report Wizard (v2)
======================================

Shape B report. Uses ``as_of_date`` instead of a date range.
Builds hierarchy: Assets / Liabilities / Equity with retained-earnings
computed from P&L accounts.

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

# Account type grouping for Balance Sheet
BS_ASSET_TYPES = [
    'asset_receivable', 'asset_cash', 'asset_current',
    'asset_non_current', 'asset_prepayments', 'asset_fixed',
]
BS_LIABILITY_TYPES = [
    'liability_payable', 'liability_current',
    'liability_non_current', 'liability_credit_card',
]
BS_EQUITY_TYPES = [
    'equity', 'equity_unaffected',
]
PNL_TYPES = [
    'income', 'income_other',
    'expense', 'expense_depreciation', 'expense_direct_cost',
]

# Sub-grouping for presentation
BS_CURRENT_ASSETS = ['asset_receivable', 'asset_cash', 'asset_current', 'asset_prepayments']
BS_NON_CURRENT_ASSETS = ['asset_non_current', 'asset_fixed']
BS_CURRENT_LIABILITIES = ['liability_payable', 'liability_current', 'liability_credit_card']
BS_NON_CURRENT_LIABILITIES = ['liability_non_current']


class OpsBSReportWizard(models.TransientModel):
    _name = 'ops.bs.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Balance Sheet Report'

    # =========================================================================
    # Fields
    # =========================================================================
    as_of_date = fields.Date(
        string='As of Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help='Balance Sheet date (cumulative balances up to this date).',
    )

    comparative = fields.Boolean(
        string='Include Comparative',
        default=False,
    )
    comparative_as_of_date = fields.Date(
        string='Comparative As of Date',
    )

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'hierarchy'

    def _get_report_titles(self):
        return {'bs': 'Balance Sheet'}

    def _get_scalar_fields_for_template(self):
        return ['target_move', 'comparative']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'business_unit_ids']

    # =========================================================================
    # Domain builder
    # =========================================================================

    def _build_bs_domain(self, as_of, account_types):
        """Build cumulative domain up to as_of_date for given account types."""
        domain = [
            ('date', '<=', as_of),
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

    # =========================================================================
    # Helpers
    # =========================================================================

    def _query_bs_data(self, as_of):
        """Query account balances cumulative to as_of date.

        Returns dict: account_id -> {code, name, account_type, balance}
        """
        MoveLine = self.env['account.move.line']

        all_types = BS_ASSET_TYPES + BS_LIABILITY_TYPES + BS_EQUITY_TYPES
        domain = self._build_bs_domain(as_of, all_types)

        data = MoveLine._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['balance:sum'],
        )
        result = {}
        for account, total_balance in data:
            if not account:
                continue
            result[account.id] = {
                'code': account.code or '',
                'name': account.name or '',
                'account_type': account.account_type,
                'balance': total_balance or 0.0,
            }
        return result

    def _compute_retained_earnings(self, as_of):
        """Compute retained earnings from P&L accounts up to as_of."""
        MoveLine = self.env['account.move.line']
        domain = self._build_bs_domain(as_of, PNL_TYPES)

        data = MoveLine._read_group(
            domain=domain,
            groupby=[],
            aggregates=['balance:sum'],
        )
        # _read_group with no groupby returns [(total_balance,)]
        if data:
            return -(data[0][0] or 0.0)  # Negate: credit-heavy P&L → positive retained earnings
        return 0.0

    def _build_section(self, account_data, account_types, section_name, value_key, negate=False):
        """Build a HierarchyNode section from account data filtered by types."""
        children = []
        total = 0.0
        for acc_id, info in sorted(account_data.items(), key=lambda x: x[1]['code']):
            if info['account_type'] not in account_types:
                continue
            balance = info['balance']
            if negate:
                balance = -balance
            children.append(HierarchyNode(
                code=info['code'],
                name=info['name'],
                level=2,
                style='detail',
                values={value_key: balance},
            ))
            total += balance

        return HierarchyNode(
            name=section_name,
            level=1,
            style='group',
            values={value_key: total},
            children=children,
        ), total

    def _build_hierarchy(self, account_data, retained_earnings, value_key='amount'):
        """Build the full BS hierarchy: Assets / Liabilities / Equity."""
        # --- ASSETS ---
        current_assets_node, ca_total = self._build_section(
            account_data, BS_CURRENT_ASSETS, 'Current Assets', value_key,
        )
        non_current_assets_node, nca_total = self._build_section(
            account_data, BS_NON_CURRENT_ASSETS, 'Non-current Assets', value_key,
        )
        total_assets = ca_total + nca_total
        assets_section = HierarchyNode(
            name='Total Assets', level=0, style='section',
            values={value_key: total_assets},
            children=[current_assets_node, non_current_assets_node],
        )

        # --- LIABILITIES ---
        current_liab_node, cl_total = self._build_section(
            account_data, BS_CURRENT_LIABILITIES, 'Current Liabilities', value_key, negate=True,
        )
        non_current_liab_node, ncl_total = self._build_section(
            account_data, BS_NON_CURRENT_LIABILITIES, 'Non-current Liabilities', value_key, negate=True,
        )
        total_liabilities = cl_total + ncl_total
        liabilities_section = HierarchyNode(
            name='Total Liabilities', level=0, style='section',
            values={value_key: total_liabilities},
            children=[current_liab_node, non_current_liab_node],
        )

        # --- EQUITY ---
        equity_node, eq_total = self._build_section(
            account_data, BS_EQUITY_TYPES, 'Equity Accounts', value_key, negate=True,
        )
        # Add retained earnings as a child
        re_node = HierarchyNode(
            code='', name='Retained Earnings (Current Year)',
            level=2, style='detail',
            values={value_key: retained_earnings},
        )
        equity_node.children.append(re_node)
        total_equity = eq_total + retained_earnings
        equity_node.values[value_key] = total_equity

        equity_section = HierarchyNode(
            name='Total Equity', level=0, style='section',
            values={value_key: total_equity},
            children=[equity_node],
        )

        # --- Total Liabilities + Equity ---
        total_le = total_liabilities + total_equity
        net_result = HierarchyNode(
            name='Total Liabilities & Equity', level=0, style='grand_total',
            values={value_key: total_le},
        )

        sections = [assets_section, liabilities_section, equity_section]
        return sections, net_result

    def _merge_comparative(self, sections_current, net_current, sections_comp, net_comp):
        """Merge comparative values into the current hierarchy."""
        def merge_nodes(curr, comp):
            if comp:
                curr.values['comparative'] = comp.values.get('amount', 0.0)
            else:
                curr.values['comparative'] = 0.0

            comp_map = {}
            if comp:
                for child in comp.children:
                    key = child.code or child.name
                    comp_map[key] = child
            for child in curr.children:
                key = child.code or child.name
                merge_nodes(child, comp_map.get(key))

        for i, section in enumerate(sections_current):
            comp_section = sections_comp[i] if i < len(sections_comp) else None
            merge_nodes(section, comp_section)
        merge_nodes(net_current, net_comp)

    # =========================================================================
    # Report data generation
    # =========================================================================

    def _get_report_data(self):
        """Build Shape B data for Balance Sheet."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        # --- Current period ---
        account_data = self._query_bs_data(self.as_of_date)
        retained_earnings = self._compute_retained_earnings(self.as_of_date)
        sections, net_result = self._build_hierarchy(
            account_data, retained_earnings, value_key='amount',
        )

        value_columns = [{'key': 'amount', 'label': 'Amount'}]

        # --- Comparative ---
        if self.comparative and self.comparative_as_of_date:
            comp_data = self._query_bs_data(self.comparative_as_of_date)
            comp_re = self._compute_retained_earnings(self.comparative_as_of_date)
            comp_sections, comp_net = self._build_hierarchy(
                comp_data, comp_re, value_key='amount',
            )
            self._merge_comparative(sections, net_result, comp_sections, comp_net)
            value_columns.append({'key': 'comparative', 'label': 'Comparative'})

        # --- Assemble Shape B report ---
        meta = build_report_meta(self, 'bs', 'Balance Sheet', 'hierarchy')
        colors = build_report_colors(self.company_id)

        report = ShapeBReport(
            meta=meta,
            colors=colors,
            value_columns=value_columns,
            sections=sections,
            net_result=net_result,
        )

        return asdict(report)

    # =========================================================================
    # Report action
    # =========================================================================

    def _return_report_action(self, data):
        report = self.env.ref('ops_matrix_accounting.action_report_bs')
        return report.report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_filters_extra(self):
        if not self.as_of_date:
            raise UserError(_("Please set the As of Date."))
        if self.comparative and not self.comparative_as_of_date:
            raise UserError(_("Comparative is enabled but Comparative As of Date is not set."))
        return True
