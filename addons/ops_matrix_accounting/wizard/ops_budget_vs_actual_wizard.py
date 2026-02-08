# -*- coding: utf-8 -*-
"""Budget vs Actual Report Wizard."""
from odoo import models, fields, api
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class OpsBudgetVsActualWizard(models.TransientModel):
    _name = 'ops.budget.vs.actual.wizard'
    _description = 'Budget vs Actual Report Wizard'

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
    )
    date_from = fields.Date(
        string='Start Date', required=True,
        default=lambda self: fields.Date.today().replace(month=1, day=1),
    )
    date_to = fields.Date(
        string='End Date', required=True,
        default=fields.Date.today,
    )
    ops_branch_ids = fields.Many2many(
        'ops.branch', string='Branches',
        help='Leave empty for all branches',
    )
    ops_business_unit_ids = fields.Many2many(
        'ops.business.unit', string='Business Units',
        help='Leave empty for all business units',
    )
    budget_ids = fields.Many2many(
        'ops.budget', string='Specific Budgets',
        help='Leave empty to auto-select based on date range and filters',
    )
    include_draft = fields.Boolean(
        string='Include Draft Budgets', default=False,
        help='Include draft budgets in addition to confirmed ones',
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise UserError('End Date must be after Start Date.')

    def action_print(self):
        """Print Budget vs Actual report."""
        self.ensure_one()
        return self.env.ref(
            'ops_matrix_accounting.action_report_budget_vs_actual_corporate'
        ).report_action(self)

    def _get_report_data(self):
        """Get budget vs actual data grouped by account type."""
        self.ensure_one()

        # Build budget domain
        states = ['confirmed', 'done']
        if self.include_draft:
            states.append('draft')

        domain = [('state', 'in', states)]

        if self.ops_branch_ids:
            domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))
        if self.ops_business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.ops_business_unit_ids.ids))
        if self.budget_ids:
            domain.append(('id', 'in', self.budget_ids.ids))
        else:
            # Find budgets that overlap the date range
            domain.extend([
                ('date_from', '<=', self.date_to),
                ('date_to', '>=', self.date_from),
            ])

        budgets = self.env['ops.budget'].search(domain)

        if not budgets:
            return {
                'groups': [],
                'grand_budget': 0,
                'grand_actual': 0,
                'grand_committed': 0,
                'grand_available': 0,
                'grand_used_pct': 0,
                'budget_count': 0,
            }

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
                        'budget': 0,
                        'actual': 0,
                        'committed': 0,
                    }
                account_data[key]['budget'] += line.planned_amount
                account_data[key]['actual'] += line.practical_amount
                account_data[key]['committed'] += line.committed_amount

        # Account type display labels and sort order
        type_config = [
            ('income', 'Revenue'),
            ('income_other', 'Other Income'),
            ('expense_direct_cost', 'Cost of Revenue'),
            ('expense', 'Operating Expenses'),
            ('expense_depreciation', 'Depreciation'),
        ]
        type_labels = {k: v for k, v in type_config}
        type_order = {k: i for i, (k, _) in enumerate(type_config)}

        # Group by account type
        groups_map = {}
        for _acct_id, data in account_data.items():
            atype = data['account_type']
            label = type_labels.get(atype, atype.replace('_', ' ').title())
            sort_key = type_order.get(atype, 99)

            if label not in groups_map:
                groups_map[label] = {
                    'name': label,
                    'sort_key': sort_key,
                    'lines': [],
                    'total_budget': 0,
                    'total_actual': 0,
                    'total_committed': 0,
                }

            available = data['budget'] - data['actual'] - data['committed']
            used_pct = (
                (data['actual'] + data['committed']) / data['budget'] * 100
                if data['budget'] else 0
            )

            groups_map[label]['lines'].append({
                'code': data['code'],
                'name': data['name'],
                'budget': data['budget'],
                'actual': data['actual'],
                'committed': data['committed'],
                'available': available,
                'used_pct': round(used_pct, 1),
            })
            groups_map[label]['total_budget'] += data['budget']
            groups_map[label]['total_actual'] += data['actual']
            groups_map[label]['total_committed'] += data['committed']

        # Sort groups and compute group totals
        groups = []
        for label, gdata in sorted(groups_map.items(), key=lambda x: x[1]['sort_key']):
            gdata['lines'].sort(key=lambda x: x['code'])
            gdata['total_available'] = (
                gdata['total_budget'] - gdata['total_actual'] - gdata['total_committed']
            )
            gdata['total_used_pct'] = round(
                (gdata['total_actual'] + gdata['total_committed']) / gdata['total_budget'] * 100
                if gdata['total_budget'] else 0, 1
            )
            groups.append(gdata)

        grand_budget = sum(g['total_budget'] for g in groups)
        grand_actual = sum(g['total_actual'] for g in groups)
        grand_committed = sum(g['total_committed'] for g in groups)
        grand_available = grand_budget - grand_actual - grand_committed
        grand_used_pct = round(
            (grand_actual + grand_committed) / grand_budget * 100
            if grand_budget else 0, 1
        )

        return {
            'groups': groups,
            'grand_budget': grand_budget,
            'grand_actual': grand_actual,
            'grand_committed': grand_committed,
            'grand_available': grand_available,
            'grand_used_pct': grand_used_pct,
            'budget_count': len(budgets),
        }
