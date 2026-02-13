# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Business Unit Profitability Report
============================================================

Provides the Business Unit Profitability Report wizard with cross-branch
analysis, contribution percentages, and monthly trend data.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsBusinessUnitReport(models.TransientModel):
    """Business Unit Profitability Report"""
    _name = 'ops.business.unit.report'
    _description = 'Business Unit Profitability Report'

    # Filter Fields
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=True
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: date_utils.start_of(datetime.now(), 'month')
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: date_utils.end_of(datetime.now(), 'month')
    )

    # Branch Filtering
    branch_ids = fields.Many2many(
        'ops.branch',
        string='Filter Branches'
    )

    business_unit_branch_ids = fields.Many2many(
        'ops.branch',
        compute='_compute_business_unit_branch_ids',
        store=False
    )

    # Include branch consolidation
    consolidate_by_branch = fields.Boolean(
        string='Show Branch Breakdown',
        default=True
    )

    # Report Data
    report_data = fields.Json(
        string='Report Data',
        compute='_compute_report_data',
        store=False
    )

    @api.depends('business_unit_id')
    def _compute_business_unit_branch_ids(self):
        """Compute available branches for the selected business unit."""
        for wizard in self:
            if wizard.business_unit_id:
                wizard.business_unit_branch_ids = wizard.business_unit_id.branch_ids
            else:
                wizard.business_unit_branch_ids = False

    @api.depends('business_unit_id', 'date_from', 'date_to', 'branch_ids', 'consolidate_by_branch')
    def _compute_report_data(self):
        """Compute BU performance across branches."""
        for wizard in self:
            if not wizard.business_unit_id or not wizard.date_from or not wizard.date_to:
                wizard.report_data = {}
                continue

            MoveLine = self.env['account.move.line']
            base_domain = [
                ('date', '>=', wizard.date_from),
                ('date', '<=', wizard.date_to),
                ('ops_business_unit_id', '=', wizard.business_unit_id.id),
                ('move_id.state', '=', 'posted'),
            ]

            # Apply branch filter if specified
            branches = wizard.branch_ids if wizard.branch_ids else wizard.business_unit_id.branch_ids
            if wizard.branch_ids:
                base_domain.append(('ops_branch_id', 'in', wizard.branch_ids.ids))

            # Branch performance breakdown
            branch_performance = {}
            if wizard.consolidate_by_branch:
                for branch in branches:
                    branch_domain = base_domain + [('ops_branch_id', '=', branch.id)]

                    # Income for this branch
                    income_result = MoveLine._read_group(
                        domain=branch_domain + [('account_id.account_type', 'in', ['income', 'income_other'])],
                        groupby=[],
                        aggregates=['credit:sum', 'debit:sum']
                    )
                    branch_income = income_result[0]['credit'] - income_result[0]['debit'] if income_result else 0

                    # Expense for this branch
                    expense_result = MoveLine._read_group(
                        domain=branch_domain + [('account_id.account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost'])],
                        groupby=[],
                        aggregates=['debit:sum', 'credit:sum']
                    )
                    branch_expense = expense_result[0]['debit'] - expense_result[0]['credit'] if expense_result else 0

                    branch_performance[branch.id] = {
                        'branch_id': branch.id,
                        'branch_code': branch.code,
                        'branch_name': branch.name,
                        'income': branch_income,
                        'expense': branch_expense,
                        'net_profit': branch_income - branch_expense,
                        'contribution_percentage': 0,  # Will calculate after totals
                        'transaction_count': MoveLine.search_count(branch_domain),
                    }

            # Get BU totals
            income_result = MoveLine._read_group(
                domain=base_domain + [('account_id.account_type', 'in', ['income', 'income_other'])],
                groupby=[],
                aggregates=['credit:sum', 'debit:sum']
            )
            total_income = income_result[0]['credit'] - income_result[0]['debit'] if income_result else 0

            expense_result = MoveLine._read_group(
                domain=base_domain + [('account_id.account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost'])],
                groupby=[],
                aggregates=['debit:sum', 'credit:sum']
            )
            total_expense = expense_result[0]['debit'] - expense_result[0]['credit'] if expense_result else 0

            total_net = total_income - total_expense

            # Calculate contribution percentages
            for branch_id, data in branch_performance.items():
                if total_income > 0:
                    data['contribution_percentage'] = (data['income'] / total_income * 100)
                else:
                    data['contribution_percentage'] = 0

            # Sort branches by contribution (descending)
            sorted_branches = sorted(
                branch_performance.values(),
                key=lambda x: x['contribution_percentage'],
                reverse=True
            )

            wizard.report_data = {
                'business_unit': wizard.business_unit_id.name,
                'business_unit_code': wizard.business_unit_id.code,
                'primary_branch': wizard.business_unit_id.primary_branch_id.name if wizard.business_unit_id.primary_branch_id else 'None',
                'period': f"{wizard.date_from} to {wizard.date_to}",
                'branch_performance': sorted_branches,
                'totals': {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_profit': total_net,
                    'profit_margin': (total_net / total_income * 100) if total_income else 0,
                    'branch_count': len(branches),
                    'active_branches': len([b for b in branch_performance.values() if b['transaction_count'] > 0]),
                    'total_transactions': MoveLine.search_count(base_domain),
                },
                'trend_data': wizard._get_trend_data(),
            }

    def _get_trend_data(self):
        """Get monthly trend data for the past 6 months."""
        MoveLine = self.env['account.move.line']
        trend_data = []

        for i in range(6, -1, -1):  # Last 6 months plus current
            month_start = date_utils.start_of(datetime.now() - timedelta(days=30*i), 'month')
            month_end = date_utils.end_of(month_start, 'month')

            domain = [
                ('date', '>=', month_start),
                ('date', '<=', month_end),
                ('ops_business_unit_id', '=', self.business_unit_id.id),
                ('move_id.state', '=', 'posted'),
            ]

            if self.branch_ids:
                domain.append(('ops_branch_id', 'in', self.branch_ids.ids))

            income_result = MoveLine._read_group(
                domain=domain + [('account_id.account_type', 'in', ['income', 'income_other'])],
                groupby=[],
                aggregates=['credit:sum', 'debit:sum']
            )
            month_income = income_result[0]['credit'] - income_result[0]['debit'] if income_result else 0

            expense_result = MoveLine._read_group(
                domain=domain + [('account_id.account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost'])],
                groupby=[],
                aggregates=['debit:sum', 'credit:sum']
            )
            month_expense = expense_result[0]['debit'] - expense_result[0]['credit'] if expense_result else 0

            trend_data.append({
                'month': month_start.strftime('%b %Y'),
                'income': month_income,
                'expense': month_expense,
                'net_profit': month_income - month_expense,
                'transaction_count': MoveLine.search_count(domain),
            })

        return trend_data

    def action_generate_pdf(self):
        """Generate PDF report for business unit."""
        self.ensure_one()
        return self.env.ref('ops_matrix_accounting.report_business_unit_pdf').report_action(self)
