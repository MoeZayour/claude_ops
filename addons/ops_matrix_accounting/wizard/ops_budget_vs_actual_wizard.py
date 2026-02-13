# -*- coding: utf-8 -*-
"""
Budget vs Actual Report Wizard (v2 Data Contracts)
====================================================

Refactored to use Shape B (hierarchy) data contracts.
value_columns: [Budget, Actual, Committed, Available, Used %]
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dataclasses import asdict
import logging

from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeBReport, HierarchyNode,
)

_logger = logging.getLogger(__name__)


class OpsBudgetVsActualWizard(models.TransientModel):
    _name = 'ops.budget.vs.actual.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Budget vs Actual Report Wizard'

    # Override date defaults
    date_from = fields.Date(
        string='Start Date', required=True,
        default=lambda self: fields.Date.today().replace(month=1, day=1),
    )
    date_to = fields.Date(
        string='End Date', required=True,
        default=fields.Date.today,
    )

    # Consolidation filters
    budget_ids = fields.Many2many('ops.budget', string='Specific Budgets',
                                   help='Leave empty to auto-select based on date range and filters')
    include_draft = fields.Boolean(string='Include Draft Budgets', default=False,
                                    help='Include draft budgets in addition to confirmed ones')

    # -------------------------------------------------------------------------
    # BASE CLASS HOOKS
    # -------------------------------------------------------------------------

    def _get_engine_name(self):
        return 'Financial'

    def _get_report_shape(self):
        return 'hierarchy'

    def _get_report_titles(self):
        return {'budget_vs_actual': 'Budget vs Actual Report'}

    def _get_scalar_fields_for_template(self):
        return ['include_draft']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'business_unit_ids', 'budget_ids']

    def _get_report_template_xmlid(self):
        return 'ops_matrix_accounting.report_budget_vs_actual_corporate'

    def _add_filter_summary_parts(self, parts):
        if self.branch_ids:
            parts.append(f"Branches: {len(self.branch_ids)} selected")
        if self.business_unit_ids:
            parts.append(f"BUs: {len(self.business_unit_ids)} selected")
        if self.budget_ids:
            parts.append(f"Budgets: {len(self.budget_ids)} selected")
        if self.include_draft:
            parts.append("Including drafts")

    def _estimate_record_count(self):
        return 0

    # -------------------------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------------------------

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from and rec.date_to < rec.date_from:
                raise UserError('End Date must be after Start Date.')

    # -------------------------------------------------------------------------
    # REPORT DATA (v2 contracts)
    # -------------------------------------------------------------------------

    def _get_report_data(self):
        """Get budget vs actual data as Shape B (hierarchy)."""
        self.ensure_one()
        self._check_intelligence_access(self._get_pillar_name())

        meta = build_report_meta(self, 'budget_vs_actual', 'Budget vs Actual Report', 'hierarchy')
        colors = build_report_colors(self.company_id)

        value_columns = [
            {'key': 'budget', 'label': 'Budget'},
            {'key': 'actual', 'label': 'Actual'},
            {'key': 'committed', 'label': 'Committed'},
            {'key': 'available', 'label': 'Available'},
            {'key': 'used_pct', 'label': 'Used %'},
        ]

        # Build budget domain
        states = ['confirmed', 'done']
        if self.include_draft:
            states.append('draft')

        domain = [('state', 'in', states)]
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        if self.budget_ids:
            domain.append(('id', 'in', self.budget_ids.ids))
        else:
            domain.extend([
                ('date_from', '<=', self.date_to),
                ('date_to', '>=', self.date_from),
            ])

        budgets = self.env['ops.budget'].search(domain)

        if not budgets:
            return asdict(ShapeBReport(
                meta=meta, colors=colors, value_columns=value_columns,
                sections=[], net_result=None,
            ))

        # Aggregate budget lines by account
        account_data = {}
        for budget in budgets:
            for line in budget.line_ids:
                acct = line.general_account_id
                key = acct.id
                if key not in account_data:
                    account_data[key] = {
                        'code': acct.code or '',
                        'name': acct.name or '',
                        'account_type': acct.account_type or 'expense',
                        'budget': 0, 'actual': 0, 'committed': 0,
                    }
                account_data[key]['budget'] += line.planned_amount
                account_data[key]['actual'] += line.practical_amount
                account_data[key]['committed'] += line.committed_amount

        # Group by account type
        type_config = [
            ('income', 'Revenue'),
            ('income_other', 'Other Income'),
            ('expense_direct_cost', 'Cost of Revenue'),
            ('expense', 'Operating Expenses'),
            ('expense_depreciation', 'Depreciation'),
        ]
        type_labels = {k: v for k, v in type_config}
        type_order = {k: i for i, (k, _) in enumerate(type_config)}

        groups_map = {}
        for _acct_id, data in account_data.items():
            atype = data['account_type']
            label = type_labels.get(atype, atype.replace('_', ' ').title())
            sort_key = type_order.get(atype, 99)

            if label not in groups_map:
                groups_map[label] = {
                    'sort_key': sort_key,
                    'children': [],
                    'totals': {'budget': 0, 'actual': 0, 'committed': 0},
                }

            available = data['budget'] - data['actual'] - data['committed']
            used_pct = (
                (data['actual'] + data['committed']) / data['budget'] * 100
                if data['budget'] else 0
            )

            groups_map[label]['children'].append(HierarchyNode(
                code=data['code'], name=data['name'],
                level=2, style='detail',
                values={
                    'budget': data['budget'],
                    'actual': data['actual'],
                    'committed': data['committed'],
                    'available': available,
                    'used_pct': round(used_pct, 1),
                },
            ))
            groups_map[label]['totals']['budget'] += data['budget']
            groups_map[label]['totals']['actual'] += data['actual']
            groups_map[label]['totals']['committed'] += data['committed']

        # Build sections sorted by type order
        sections = []
        grand = {'budget': 0, 'actual': 0, 'committed': 0}

        for label, gdata in sorted(groups_map.items(), key=lambda x: x[1]['sort_key']):
            gdata['children'].sort(key=lambda x: x.code)
            t = gdata['totals']
            available = t['budget'] - t['actual'] - t['committed']
            used_pct = (t['actual'] + t['committed']) / t['budget'] * 100 if t['budget'] else 0

            sections.append(HierarchyNode(
                code='', name=label,
                level=0, style='section',
                values={
                    'budget': t['budget'], 'actual': t['actual'],
                    'committed': t['committed'], 'available': available,
                    'used_pct': round(used_pct, 1),
                },
                children=gdata['children'],
            ))
            grand['budget'] += t['budget']
            grand['actual'] += t['actual']
            grand['committed'] += t['committed']

        grand_available = grand['budget'] - grand['actual'] - grand['committed']
        grand_used_pct = (grand['actual'] + grand['committed']) / grand['budget'] * 100 if grand['budget'] else 0

        net_result = HierarchyNode(
            code='', name='Grand Total',
            level=0, style='grand_total',
            values={
                'budget': grand['budget'], 'actual': grand['actual'],
                'committed': grand['committed'], 'available': grand_available,
                'used_pct': round(grand_used_pct, 1),
            },
        )

        return asdict(ShapeBReport(
            meta=meta, colors=colors, value_columns=value_columns,
            sections=sections, net_result=net_result,
        ))

    # -------------------------------------------------------------------------
    # REPORT ACTION
    # -------------------------------------------------------------------------

    def _return_report_action(self, data):
        """Return report action for PDF generation."""
        return self.env.ref(
            'ops_matrix_accounting.action_report_budget_vs_actual'
        ).report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # -------------------------------------------------------------------------
    # LEGACY COMPATIBILITY
    # -------------------------------------------------------------------------
    def action_print(self):
        """Legacy entry point - delegate to base class."""
        return self.action_generate_report()
