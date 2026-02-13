# -*- coding: utf-8 -*-
"""
OPS Profit & Loss Report Wizard (v2)
======================================

Shape B report. Revenue/Expense hierarchy with optional comparative period.

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

# Account type to section mapping
PNL_SECTIONS = {
    'income': {'section': 'revenue', 'label': 'Revenue', 'sign': -1},
    'income_other': {'section': 'other_income', 'label': 'Other Income', 'sign': -1},
    'expense_direct_cost': {'section': 'cogs', 'label': 'Cost of Revenue', 'sign': 1},
    'expense': {'section': 'opex', 'label': 'Operating Expenses', 'sign': 1},
    'expense_depreciation': {'section': 'depreciation', 'label': 'Depreciation & Amortization', 'sign': 1},
}


class OpsPnLReportWizard(models.TransientModel):
    _name = 'ops.pnl.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Profit & Loss Report'

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

    comparative = fields.Boolean(
        string='Include Comparative Period',
        default=False,
    )
    comparative_date_from = fields.Date(string='Comparative From')
    comparative_date_to = fields.Date(string='Comparative To')

    show_percentage = fields.Boolean(
        string='Show Percentage of Revenue',
        default=True,
    )

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'hierarchy'

    def _get_report_titles(self):
        return {'pnl': 'Profit & Loss Statement'}

    def _get_scalar_fields_for_template(self):
        return [
            'target_move', 'comparative', 'show_percentage',
        ]

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'business_unit_ids']

    # =========================================================================
    # Domain builder
    # =========================================================================

    def _build_pnl_domain(self, d_from, d_to):
        """Build domain for P&L accounts within a date range."""
        domain = [
            ('date', '>=', d_from),
            ('date', '<=', d_to),
            ('company_id', '=', self.company_id.id),
            ('account_id.account_type', 'in', list(PNL_SECTIONS.keys())),
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

    def _query_pnl_data(self, d_from, d_to):
        """Query and aggregate P&L data grouped by account."""
        domain = self._build_pnl_domain(d_from, d_to)
        data = self.env['account.move.line']._read_group(
            domain=domain,
            groupby=['account_id'],
            aggregates=['debit:sum', 'credit:sum', 'balance:sum'],
        )
        # Build map: account_id -> {debit, credit, balance, account_type, code, name}
        result = {}
        for account, total_debit, total_credit, total_balance in data:
            if not account:
                continue
            result[account.id] = {
                'code': account.code or '',
                'name': account.name or '',
                'account_type': account.account_type,
                'debit': total_debit or 0.0,
                'credit': total_credit or 0.0,
                'balance': total_balance or 0.0,
            }
        return result

    def _build_hierarchy(self, account_data, value_key='amount'):
        """Build hierarchical P&L structure from account data.

        Returns (sections_list, net_result_node).
        """
        # Organise accounts into sections
        section_accounts = {
            'revenue': [], 'other_income': [],
            'cogs': [], 'opex': [], 'depreciation': [],
        }

        for acc_id, info in account_data.items():
            acc_type = info['account_type']
            section_info = PNL_SECTIONS.get(acc_type)
            if section_info:
                sign = section_info['sign']
                # balance = debit - credit; revenue has negative balance (credit-heavy)
                # We multiply by sign so positive = good (income) or cost (expense)
                amount = abs(info['balance'])
                section_accounts[section_info['section']].append({
                    'code': info['code'],
                    'name': info['name'],
                    'amount': amount,
                })

        # Revenue section
        revenue_children = [
            HierarchyNode(
                code=a['code'], name=a['name'], level=2, style='detail',
                values={value_key: a['amount']},
            )
            for a in sorted(section_accounts['revenue'], key=lambda x: x['code'])
        ]
        revenue_total = sum(a['amount'] for a in section_accounts['revenue'])
        revenue_section = HierarchyNode(
            name='Revenue', level=0, style='section',
            values={value_key: revenue_total},
            children=revenue_children,
        )

        # COGS section
        cogs_children = [
            HierarchyNode(
                code=a['code'], name=a['name'], level=2, style='detail',
                values={value_key: a['amount']},
            )
            for a in sorted(section_accounts['cogs'], key=lambda x: x['code'])
        ]
        cogs_total = sum(a['amount'] for a in section_accounts['cogs'])
        cogs_section = HierarchyNode(
            name='Cost of Revenue', level=0, style='section',
            values={value_key: cogs_total},
            children=cogs_children,
        )

        # Gross Profit
        gross_profit = revenue_total - cogs_total
        gross_profit_node = HierarchyNode(
            name='Gross Profit', level=0, style='total',
            values={value_key: gross_profit},
        )

        # Operating Expenses section
        opex_children = [
            HierarchyNode(
                code=a['code'], name=a['name'], level=2, style='detail',
                values={value_key: a['amount']},
            )
            for a in sorted(section_accounts['opex'], key=lambda x: x['code'])
        ]
        opex_total = sum(a['amount'] for a in section_accounts['opex'])
        opex_section = HierarchyNode(
            name='Operating Expenses', level=0, style='section',
            values={value_key: opex_total},
            children=opex_children,
        )

        # Depreciation section
        depr_children = [
            HierarchyNode(
                code=a['code'], name=a['name'], level=2, style='detail',
                values={value_key: a['amount']},
            )
            for a in sorted(section_accounts['depreciation'], key=lambda x: x['code'])
        ]
        depr_total = sum(a['amount'] for a in section_accounts['depreciation'])
        depr_section = HierarchyNode(
            name='Depreciation & Amortization', level=0, style='section',
            values={value_key: depr_total},
            children=depr_children,
        )

        # Operating Income
        operating_income = gross_profit - opex_total - depr_total
        operating_income_node = HierarchyNode(
            name='Operating Income', level=0, style='total',
            values={value_key: operating_income},
        )

        # Other Income section
        other_children = [
            HierarchyNode(
                code=a['code'], name=a['name'], level=2, style='detail',
                values={value_key: a['amount']},
            )
            for a in sorted(section_accounts['other_income'], key=lambda x: x['code'])
        ]
        other_total = sum(a['amount'] for a in section_accounts['other_income'])
        other_section = HierarchyNode(
            name='Other Income', level=0, style='section',
            values={value_key: other_total},
            children=other_children,
        )

        # Net Profit
        net_profit = operating_income + other_total
        net_result = HierarchyNode(
            name='Net Profit / (Loss)', level=0, style='grand_total',
            values={value_key: net_profit},
        )

        sections = [
            revenue_section, cogs_section, gross_profit_node,
            opex_section, depr_section, operating_income_node,
            other_section,
        ]

        return sections, net_result

    def _merge_comparative(self, sections_current, net_current, sections_comp, net_comp):
        """Merge comparative values into the primary hierarchy nodes."""
        # Walk both trees in parallel and add 'comparative' to values
        def merge_nodes(curr, comp):
            if comp:
                curr.values['comparative'] = comp.values.get('amount', 0.0)
                curr_amount = curr.values.get('amount', 0.0)
                comp_amount = comp.values.get('amount', 0.0)
                if comp_amount:
                    curr.values['variance'] = curr_amount - comp_amount
                    curr.values['variance_pct'] = (
                        (curr_amount - comp_amount) / abs(comp_amount)
                    ) if abs(comp_amount) > 0.005 else 0.0
                else:
                    curr.values['variance'] = curr_amount
                    curr.values['variance_pct'] = 0.0
            else:
                curr.values['comparative'] = 0.0
                curr.values['variance'] = curr.values.get('amount', 0.0)
                curr.values['variance_pct'] = 0.0

            # Merge children
            comp_children_map = {}
            if comp:
                for child in comp.children:
                    comp_children_map[child.code] = child
            for child in curr.children:
                comp_child = comp_children_map.get(child.code)
                merge_nodes(child, comp_child)

        for i, section in enumerate(sections_current):
            comp_section = sections_comp[i] if i < len(sections_comp) else None
            merge_nodes(section, comp_section)

        merge_nodes(net_current, net_comp)

    # =========================================================================
    # Report data generation
    # =========================================================================

    def _get_report_data(self):
        """Build Shape B data for Profit & Loss."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        # --- Current period ---
        current_data = self._query_pnl_data(self.date_from, self.date_to)
        sections, net_result = self._build_hierarchy(current_data, value_key='amount')

        # --- Comparative period ---
        value_columns = [
            {'key': 'amount', 'label': 'Amount'},
        ]
        if self.comparative and self.comparative_date_from and self.comparative_date_to:
            comp_data = self._query_pnl_data(
                self.comparative_date_from, self.comparative_date_to,
            )
            comp_sections, comp_net = self._build_hierarchy(comp_data, value_key='amount')
            self._merge_comparative(sections, net_result, comp_sections, comp_net)
            value_columns.append({'key': 'comparative', 'label': 'Comparative'})
            value_columns.append({'key': 'variance', 'label': 'Variance'})
            value_columns.append({'key': 'variance_pct', 'label': 'Variance %'})

        # --- Assemble Shape B report ---
        meta = build_report_meta(self, 'pnl', 'Profit & Loss Statement', 'hierarchy')
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
        report = self.env.ref('ops_matrix_accounting.action_report_pnl')
        return report.report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_filters_extra(self):
        if not self.date_from or not self.date_to:
            raise UserError(_("Please set both From Date and To Date."))
        if self.comparative:
            if not self.comparative_date_from or not self.comparative_date_to:
                raise UserError(_(
                    "Comparative period is enabled but comparative dates are not set."
                ))
            if self.comparative_date_from > self.comparative_date_to:
                raise UserError(_("Comparative From date cannot be after Comparative To date."))
        return True
