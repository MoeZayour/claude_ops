# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Group-Level Balance Sheet Consolidation
================================================================

Provides the Group-Level Balance Sheet Consolidation wizard with
multi-company support and intercompany elimination calculations.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpsConsolidatedBalanceSheet(models.TransientModel):
    """Group-Level Balance Sheet Consolidation"""
    _name = 'ops.consolidated.balance.sheet'
    _description = 'Group-Level Balance Sheet Consolidation'

    # Company Selection
    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
        required=True,
        default=lambda self: self.env.company
    )

    # Date for balance sheet
    date = fields.Date(
        string='As of Date',
        required=True,
        default=fields.Date.today
    )

    # Consolidation Options
    include_intercompany = fields.Boolean(
        string='Include Intercompany Eliminations',
        default=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Reporting Currency',
        default=lambda self: self.env.company.currency_id
    )

    # Report Data
    report_data = fields.Json(
        string='Report Data',
        compute='_compute_report_data',
        store=False
    )

    @api.depends('company_ids', 'date', 'include_intercompany', 'currency_id')
    def _compute_report_data(self):
        """Compute consolidated balance sheet for multiple companies."""
        for wizard in self:
            if not wizard.company_ids or not wizard.date:
                wizard.report_data = {}
                continue

            MoveLine = self.env['account.move.line']

            # Get balance sheet data for each company
            company_data = []
            total_assets = total_liabilities = total_equity = 0

            for company in wizard.company_ids:
                domain = [
                    ('date', '<=', wizard.date),
                    ('company_id', '=', company.id),
                    ('move_id.state', '=', 'posted'),
                    ('account_id.include_initial_balance', '=', True),
                ]

                # Group by account type
                result = MoveLine._read_group(
                    domain=domain,
                    groupby=['account_id'],
                    aggregates=['balance:sum']
                )

                # Initialize totals
                assets = liabilities = equity = income = expense = 0

                for group in result:
                    if group.get('account_id'):
                        account = self.env['account.account'].browse(group['account_id'][0])
                        balance = group.get('balance', 0)

                        if account.account_type and account.account_type.startswith('asset'):
                            assets += balance
                        elif account.account_type and account.account_type.startswith('liability'):
                            liabilities += balance
                        elif account.account_type == 'equity':
                            equity += balance
                        elif account.account_type in ['income', 'income_other']:
                            income += balance
                        elif account.account_type in ['expense', 'expense_depreciation', 'expense_direct_cost']:
                            expense += balance

                # Calculate net income/loss for period
                net_income = income + expense  # Expense is negative in accounting

                company_data.append({
                    'company_id': company.id,
                    'company_name': company.name,
                    'company_code': company.ops_code if hasattr(company, 'ops_code') else company.name,
                    'assets': assets,
                    'liabilities': liabilities,
                    'equity': equity + net_income,  # Include current year profit/loss
                    'net_income': net_income,
                    'currency': company.currency_id.name,
                })

                # Accumulate totals
                total_assets += assets
                total_liabilities += liabilities
                total_equity += equity + net_income

            # Apply intercompany eliminations if requested
            eliminations = {'asset_eliminations': 0, 'liability_eliminations': 0}
            if wizard.include_intercompany and len(wizard.company_ids) > 1:
                eliminations = wizard._calculate_intercompany_eliminations(wizard.company_ids.ids, wizard.date)
                total_assets -= eliminations.get('asset_eliminations', 0)
                total_liabilities -= eliminations.get('liability_eliminations', 0)

            wizard.report_data = {
                'report_date': str(wizard.date),
                'companies': company_data,
                'consolidated': {
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'total_equity': total_equity,
                    'balance_check': total_assets - (total_liabilities + total_equity),
                },
                'eliminations': eliminations,
                'reporting_currency': wizard.currency_id.name,
                'company_count': len(wizard.company_ids),
            }

    def _calculate_intercompany_eliminations(self, company_ids, date):
        """Calculate intercompany eliminations for consolidation."""
        MoveLine = self.env['account.move.line']

        # Find intercompany accounts (accounts marked as intercompany)
        intercompany_accounts = self.env['account.account'].search([
            ('company_id', 'in', company_ids),
            ('reconcile', '=', True),  # Use reconcile flag as proxy for intercompany
        ])

        asset_eliminations = 0
        liability_eliminations = 0

        for account in intercompany_accounts:
            if 'intercompany' not in account.name.lower():
                continue

            domain = [
                ('date', '<=', date),
                ('account_id', '=', account.id),
                ('company_id', 'in', company_ids),
                ('move_id.state', '=', 'posted'),
            ]

            result = MoveLine._read_group(
                domain=domain,
                groupby=['company_id'],
                aggregates=['balance:sum']
            )

            # Sum balances across companies
            total_balance = sum(item.get('balance', 0) for item in result)

            # If total balance across companies is not zero, there's an elimination
            if abs(total_balance) > 0.01:  # Tolerance for floating point
                if account.account_type and account.account_type.startswith('asset'):
                    asset_eliminations += total_balance
                elif account.account_type and account.account_type.startswith('liability'):
                    liability_eliminations += total_balance

        return {
            'asset_eliminations': asset_eliminations,
            'liability_eliminations': liability_eliminations,
        }

    def action_generate_pdf(self):
        """Generate PDF consolidated balance sheet."""
        self.ensure_one()
        return self.env.ref('ops_matrix_accounting.report_consolidated_balance_sheet_pdf').report_action(self)
