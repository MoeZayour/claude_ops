# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Branch-Level Profit & Loss Report
==========================================================

Provides the Branch-Level P&L Report wizard with BU performance breakdown
and top product/service analysis.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class OpsBranchReport(models.TransientModel):
    """Branch-Level Profit & Loss Report"""
    _name = 'ops.branch.report'
    _description = 'Branch-Level Profit & Loss Report'

    # Filter Fields
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
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

    # BU Filtering
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        string='Filter Business Units'
    )

    # Report Data
    report_data = fields.Json(
        string='Report Data',
        compute='_compute_report_data',
        store=False
    )

    @api.depends('branch_id', 'date_from', 'date_to', 'business_unit_ids')
    def _compute_report_data(self):
        """Compute branch-level P&L report."""
        for wizard in self:
            if not wizard.branch_id or not wizard.date_from or not wizard.date_to:
                wizard.report_data = {}
                continue

            MoveLine = self.env['account.move.line']
            base_domain = [
                ('date', '>=', wizard.date_from),
                ('date', '<=', wizard.date_to),
                ('ops_branch_id', '=', wizard.branch_id.id),
                ('move_id.state', '=', 'posted'),
            ]

            # Apply BU filter if specified
            if wizard.business_unit_ids:
                base_domain.append(('ops_business_unit_id', 'in', wizard.business_unit_ids.ids))

            # Get BU performance data
            bu_performance = {}
            # Get business units that operate in this branch
            if wizard.business_unit_ids:
                bus = wizard.business_unit_ids
            else:
                bus = self.env['ops.business.unit'].search([
                    ('branch_ids', 'in', [wizard.branch_id.id])
                ])

            for bu in bus:
                bu_domain = base_domain + [('ops_business_unit_id', '=', bu.id)]

                # Income for this BU
                income_result = MoveLine._read_group(
                    domain=bu_domain + [('account_id.account_type', 'in', ['income', 'income_other'])],
                    groupby=[],
                    aggregates=['credit:sum', 'debit:sum']
                )
                bu_income = income_result[0]['credit'] - income_result[0]['debit'] if income_result else 0

                # Expense for this BU
                expense_result = MoveLine._read_group(
                    domain=bu_domain + [('account_id.account_type', 'in', ['expense', 'expense_depreciation', 'expense_direct_cost'])],
                    groupby=[],
                    aggregates=['debit:sum', 'credit:sum']
                )
                bu_expense = expense_result[0]['debit'] - expense_result[0]['credit'] if expense_result else 0

                bu_performance[bu.id] = {
                    'bu_id': bu.id,
                    'bu_code': bu.code,
                    'bu_name': bu.name,
                    'income': bu_income,
                    'expense': bu_expense,
                    'net_profit': bu_income - bu_expense,
                    'margin': ((bu_income - bu_expense) / bu_income * 100) if bu_income else 0,
                    'transaction_count': MoveLine.search_count(bu_domain),
                }

            # Get branch totals
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

            # Get top products/services (if sale/purchase modules installed)
            top_products = []
            if 'sale.order.line' in self.env:
                try:
                    sale_lines = self.env['sale.order.line'].search([
                        ('order_id.ops_branch_id', '=', wizard.branch_id.id),
                        ('order_id.date_order', '>=', wizard.date_from),
                        ('order_id.date_order', '<=', wizard.date_to),
                        ('order_id.state', 'in', ['sale', 'done']),
                    ], limit=10)

                    for line in sale_lines:
                        top_products.append({
                            'product': line.product_id.name if line.product_id else 'N/A',
                            'quantity': line.product_uom_qty,
                            'revenue': line.price_subtotal,
                        })
                except Exception as e:
                    _logger.warning(f"Could not fetch sale order lines: {e}")

            wizard.report_data = {
                'branch': wizard.branch_id.name,
                'branch_code': wizard.branch_id.code,
                'company': wizard.branch_id.company_id.name,
                'period': f"{wizard.date_from} to {wizard.date_to}",
                'bu_performance': list(bu_performance.values()),
                'totals': {
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_profit': total_income - total_expense,
                    'bu_count': len(bus),
                    'transaction_count': MoveLine.search_count(base_domain),
                },
                'top_products': top_products[:5],
            }

    def action_generate_pdf(self):
        """Generate PDF report for branch."""
        self.ensure_one()
        return self.env.ref('ops_matrix_accounting.report_branch_pl_pdf').report_action(self)
