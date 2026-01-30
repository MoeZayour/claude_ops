# -*- coding: utf-8 -*-
"""OPS Foreign Currency Revaluation - Calculate and record unrealized FX gains/losses."""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsFxRevaluationWizard(models.TransientModel):
    """FX Revaluation Wizard."""
    _name = 'ops.fx.revaluation.wizard'
    _description = 'Foreign Currency Revaluation'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    revaluation_date = fields.Date(string='Revaluation Date', required=True, default=fields.Date.today)
    ops_branch_ids = fields.Many2many('ops.branch', string='Branches',
                                       help="Leave empty to include all branches")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                  domain="[('type', '=', 'general')]")
    currency_ids = fields.Many2many('res.currency', string='Currencies',
                                     help="Leave empty to include all foreign currencies")

    account_type_filter = fields.Selection([
        ('all', 'All Monetary Accounts'),
        ('receivable_payable', 'Receivables & Payables Only'),
        ('bank', 'Bank Accounts Only'),
    ], string='Account Filter', default='receivable_payable', required=True)

    revaluation_line_ids = fields.One2many('ops.fx.revaluation.line', 'wizard_id', string='Revaluation Lines')
    total_gain = fields.Monetary(string='Total Gain', compute='_compute_totals')
    total_loss = fields.Monetary(string='Total Loss', compute='_compute_totals')
    net_result = fields.Monetary(string='Net Result', compute='_compute_totals')
    currency_id = fields.Many2one(related='company_id.currency_id')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('calculated', 'Calculated'), ('posted', 'Posted')], default='draft')

    @api.depends('revaluation_line_ids.adjustment_amount')
    def _compute_totals(self):
        for wizard in self:
            gains = sum(wizard.revaluation_line_ids.filtered(lambda l: l.adjustment_amount > 0).mapped('adjustment_amount'))
            losses = sum(wizard.revaluation_line_ids.filtered(lambda l: l.adjustment_amount < 0).mapped('adjustment_amount'))
            wizard.total_gain = gains
            wizard.total_loss = abs(losses)
            wizard.net_result = gains + losses

    def action_calculate(self):
        """Calculate FX revaluation adjustments."""
        self.ensure_one()
        self.revaluation_line_ids.unlink()

        # Get currencies to evaluate (exclude company currency)
        if self.currency_ids:
            currencies = self.currency_ids.filtered(lambda c: c.id != self.company_id.currency_id.id)
        else:
            currencies = self.env['res.currency'].search([
                ('id', '!=', self.company_id.currency_id.id),
                ('active', '=', True)
            ])

        if not currencies:
            raise UserError(_('No foreign currencies found to revalue.'))

        # Build account domain based on filter
        account_domain = [
            ('company_id', '=', self.company_id.id),
            ('currency_id', 'in', currencies.ids)
        ]

        if self.account_type_filter == 'receivable_payable':
            account_domain.append(('account_type', 'in', ['asset_receivable', 'liability_payable']))
        elif self.account_type_filter == 'bank':
            account_domain.append(('account_type', '=', 'asset_cash'))

        accounts = self.env['account.account'].search(account_domain)

        if not accounts:
            raise UserError(_('No accounts with foreign currency found matching the filter.'))

        lines_to_create = []

        for account in accounts:
            move_line_domain = [
                ('account_id', '=', account.id),
                ('date', '<=', self.revaluation_date),
                ('parent_state', '=', 'posted'),
                ('reconciled', '=', False)
            ]

            if self.ops_branch_ids:
                move_line_domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))

            move_lines = self.env['account.move.line'].search(move_line_domain)
            if not move_lines:
                continue

            # Calculate balances
            foreign_balance = sum(move_lines.mapped('amount_currency'))
            book_balance = sum(move_lines.mapped('balance'))

            if abs(foreign_balance) < 0.01:
                continue

            # Get current exchange rate
            currency = account.currency_id
            rate = currency._get_conversion_rate(
                currency,
                self.company_id.currency_id,
                self.company_id,
                self.revaluation_date
            )

            fair_value = foreign_balance * rate
            adjustment = fair_value - book_balance

            if abs(adjustment) < 0.01:
                continue

            lines_to_create.append({
                'wizard_id': self.id,
                'account_id': account.id,
                'currency_id': currency.id,
                'foreign_balance': foreign_balance,
                'book_balance': book_balance,
                'exchange_rate': rate,
                'fair_value': fair_value,
                'adjustment_amount': adjustment,
            })

        if lines_to_create:
            self.env['ops.fx.revaluation.line'].create(lines_to_create)

        self.write({'state': 'calculated'})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Calculation Complete'),
                'message': _('%d accounts analyzed, net adjustment: %s') % (len(lines_to_create), self.net_result),
                'type': 'success'
            }
        }

    def action_post(self):
        """Create and post revaluation journal entry."""
        self.ensure_one()
        if self.state != 'calculated':
            raise UserError(_('Please calculate revaluation first.'))
        if not self.revaluation_line_ids:
            raise UserError(_('No revaluation adjustments to post.'))

        # Get gain/loss accounts from company settings
        gain_account = self.company_id.income_currency_exchange_account_id
        loss_account = self.company_id.expense_currency_exchange_account_id

        if not gain_account or not loss_account:
            raise UserError(_(
                'Please configure currency exchange gain/loss accounts in the company settings.\n'
                'Go to Settings > Accounting > Currencies and set the exchange rate gain/loss accounts.'
            ))

        move_lines = []

        for line in self.revaluation_line_ids:
            if abs(line.adjustment_amount) < 0.01:
                continue

            move_lines.append((0, 0, {
                'account_id': line.account_id.id,
                'name': f'FX Revaluation: {line.account_id.name}',
                'debit': line.adjustment_amount if line.adjustment_amount > 0 else 0,
                'credit': -line.adjustment_amount if line.adjustment_amount < 0 else 0,
                'currency_id': line.currency_id.id,
                'amount_currency': 0,
            }))

        # Add offsetting entry for gain or loss
        if self.net_result > 0:
            move_lines.append((0, 0, {
                'account_id': gain_account.id,
                'name': 'Unrealized FX Gain',
                'debit': 0,
                'credit': self.net_result
            }))
        elif self.net_result < 0:
            move_lines.append((0, 0, {
                'account_id': loss_account.id,
                'name': 'Unrealized FX Loss',
                'debit': -self.net_result,
                'credit': 0
            }))

        move = self.env['account.move'].create({
            'date': self.revaluation_date,
            'journal_id': self.journal_id.id,
            'ref': f'FX Revaluation {self.revaluation_date}',
            'line_ids': move_lines,
        })
        move.action_post()

        self.write({'move_id': move.id, 'state': 'posted'})

        return {
            'name': _('Revaluation Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form'
        }

    def action_reset(self):
        """Reset to draft state."""
        self.revaluation_line_ids.unlink()
        self.write({'state': 'draft', 'move_id': False})


class OpsFxRevaluationLine(models.TransientModel):
    """FX Revaluation Line."""
    _name = 'ops.fx.revaluation.line'
    _description = 'FX Revaluation Line'

    wizard_id = fields.Many2one('ops.fx.revaluation.wizard', required=True, ondelete='cascade')
    account_id = fields.Many2one('account.account', string='Account', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    company_currency_id = fields.Many2one(related='wizard_id.company_id.currency_id')
    foreign_balance = fields.Monetary(string='Foreign Balance', currency_field='currency_id')
    book_balance = fields.Monetary(string='Book Balance', currency_field='company_currency_id')
    exchange_rate = fields.Float(string='Exchange Rate', digits=(12, 6))
    fair_value = fields.Monetary(string='Fair Value', currency_field='company_currency_id')
    adjustment_amount = fields.Monetary(string='Adjustment', currency_field='company_currency_id')
    adjustment_type = fields.Selection([
        ('gain', 'Gain'),
        ('loss', 'Loss'),
    ], compute='_compute_adjustment_type', string='Type')

    @api.depends('adjustment_amount')
    def _compute_adjustment_type(self):
        for line in self:
            if line.adjustment_amount > 0:
                line.adjustment_type = 'gain'
            elif line.adjustment_amount < 0:
                line.adjustment_type = 'loss'
            else:
                line.adjustment_type = False
