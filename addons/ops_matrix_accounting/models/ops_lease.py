# -*- coding: utf-8 -*-
"""OPS IFRS 16 Lease Accounting - Right-of-Use Assets and Lease Liabilities."""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsLease(models.Model):
    """IFRS 16 Lease Agreement."""
    _name = 'ops.lease'
    _description = 'Lease Agreement (IFRS 16)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'commencement_date desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False, default=lambda self: _('New'), readonly=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    ops_branch_id = fields.Many2one('ops.branch', string='Branch', required=True, tracking=True, index=True)
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit', tracking=True)
    description = fields.Text(string='Description')
    lessor_id = fields.Many2one('res.partner', string='Lessor', required=True, tracking=True)

    lease_type = fields.Selection([
        ('property', 'Property/Building'), ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'), ('other', 'Other'),
    ], string='Lease Type', required=True, default='property')

    commencement_date = fields.Date(string='Commencement Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    lease_term_months = fields.Integer(string='Lease Term (Months)', compute='_compute_lease_term', store=True)

    currency_id = fields.Many2one(related='company_id.currency_id')
    payment_amount = fields.Monetary(string='Periodic Payment', required=True, tracking=True)

    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('annually', 'Annually'),
    ], string='Payment Frequency', default='monthly', required=True)

    payment_timing = fields.Selection([
        ('beginning', 'Beginning of Period'), ('end', 'End of Period'),
    ], string='Payment Timing', default='end', required=True)

    discount_rate = fields.Float(string='Incremental Borrowing Rate (%)', required=True, default=5.0)
    initial_direct_costs = fields.Monetary(string='Initial Direct Costs', default=0.0)

    rou_asset_value = fields.Monetary(string='ROU Asset Value', compute='_compute_lease_values', store=True)
    lease_liability = fields.Monetary(string='Lease Liability', compute='_compute_lease_values', store=True)
    current_liability = fields.Monetary(string='Current Portion', compute='_compute_current_liability')
    non_current_liability = fields.Monetary(string='Non-Current Portion', compute='_compute_current_liability')

    payment_schedule_ids = fields.One2many('ops.lease.payment.schedule', 'lease_id', string='Payment Schedule')
    depreciation_schedule_ids = fields.One2many('ops.lease.depreciation', 'lease_id', string='Depreciation Schedule')
    initial_recognition_move_id = fields.Many2one('account.move', string='Initial Recognition Entry', readonly=True)

    rou_asset_account_id = fields.Many2one('account.account', string='ROU Asset Account', required=True)
    lease_liability_account_id = fields.Many2one('account.account', string='Lease Liability Account', required=True)
    depreciation_expense_account_id = fields.Many2one('account.account', string='Depreciation Expense Account', required=True)
    interest_expense_account_id = fields.Many2one('account.account', string='Interest Expense Account', required=True)
    accumulated_depreciation_account_id = fields.Many2one('account.account', string='Accumulated Depreciation Account', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                  domain="[('type', '=', 'general')]")

    state = fields.Selection([
        ('draft', 'Draft'), ('active', 'Active'), ('terminated', 'Terminated'), ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)

    # Computed fields for dashboard
    total_payments_made = fields.Monetary(compute='_compute_payment_stats')
    payments_remaining = fields.Integer(compute='_compute_payment_stats')
    next_payment_date = fields.Date(compute='_compute_payment_stats')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.lease') or _('New')
        return super().create(vals_list)

    @api.depends('commencement_date', 'end_date')
    def _compute_lease_term(self):
        for lease in self:
            if lease.commencement_date and lease.end_date:
                delta = relativedelta(lease.end_date, lease.commencement_date)
                lease.lease_term_months = delta.years * 12 + delta.months
            else:
                lease.lease_term_months = 0

    @api.depends('payment_amount', 'payment_frequency', 'lease_term_months', 'discount_rate', 'initial_direct_costs', 'payment_timing')
    def _compute_lease_values(self):
        """Calculate ROU Asset and Lease Liability using present value."""
        for lease in self:
            if not lease.payment_amount or not lease.lease_term_months or not lease.discount_rate:
                lease.rou_asset_value = lease.lease_liability = 0
                continue

            if lease.payment_frequency == 'monthly':
                n_payments, rate = lease.lease_term_months, lease.discount_rate / 100 / 12
            elif lease.payment_frequency == 'quarterly':
                n_payments, rate = lease.lease_term_months / 3, lease.discount_rate / 100 / 4
            else:
                n_payments, rate = lease.lease_term_months / 12, lease.discount_rate / 100

            if rate <= 0 or n_payments <= 0:
                lease.rou_asset_value = lease.lease_liability = 0
                continue

            pv_factor = (1 - (1 + rate) ** -n_payments) / rate
            if lease.payment_timing == 'beginning':
                pv_factor *= (1 + rate)

            pv = lease.payment_amount * pv_factor
            lease.lease_liability = round(pv, 2)
            lease.rou_asset_value = round(pv + lease.initial_direct_costs, 2)

    @api.depends('lease_liability', 'payment_schedule_ids')
    def _compute_current_liability(self):
        today = fields.Date.today()
        one_year = today + relativedelta(years=1)
        for lease in self:
            if not lease.payment_schedule_ids:
                lease.current_liability = 0
                lease.non_current_liability = lease.lease_liability
                continue
            current_payments = lease.payment_schedule_ids.filtered(lambda p: p.payment_date <= one_year and p.state != 'paid')
            lease.current_liability = sum(current_payments.mapped('principal_amount'))
            lease.non_current_liability = lease.lease_liability - lease.current_liability

    @api.depends('payment_schedule_ids', 'payment_schedule_ids.state')
    def _compute_payment_stats(self):
        for lease in self:
            paid = lease.payment_schedule_ids.filtered(lambda p: p.state == 'paid')
            pending = lease.payment_schedule_ids.filtered(lambda p: p.state == 'pending')
            lease.total_payments_made = sum(paid.mapped('payment_amount'))
            lease.payments_remaining = len(pending)
            if pending:
                lease.next_payment_date = min(pending.mapped('payment_date'))
            else:
                lease.next_payment_date = False

    def action_generate_schedules(self):
        """Generate payment and depreciation schedules."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Can only generate schedules for draft leases.'))

        self.payment_schedule_ids.unlink()
        self.depreciation_schedule_ids.unlink()
        self._generate_payment_schedule()
        self._generate_depreciation_schedule()
        self.message_post(body=_('Payment and depreciation schedules generated.'))

    def _generate_payment_schedule(self):
        """Generate lease payment schedule with interest/principal split."""
        self.ensure_one()
        if self.payment_frequency == 'monthly':
            period_delta, rate = relativedelta(months=1), self.discount_rate / 100 / 12
        elif self.payment_frequency == 'quarterly':
            period_delta, rate = relativedelta(months=3), self.discount_rate / 100 / 4
        else:
            period_delta, rate = relativedelta(years=1), self.discount_rate / 100

        current_date = self.commencement_date if self.payment_timing == 'beginning' else self.commencement_date + period_delta
        balance, sequence = self.lease_liability, 1

        while current_date <= self.end_date and balance > 0.01:
            interest = balance * rate
            principal = min(self.payment_amount - interest, balance)

            self.env['ops.lease.payment.schedule'].create({
                'lease_id': self.id, 'sequence': sequence, 'payment_date': current_date,
                'payment_amount': self.payment_amount, 'interest_amount': round(interest, 2),
                'principal_amount': round(principal, 2), 'balance_after': round(balance - principal, 2),
            })
            balance -= principal
            current_date += period_delta
            sequence += 1

    def _generate_depreciation_schedule(self):
        """Generate straight-line depreciation schedule for ROU asset."""
        self.ensure_one()
        if not self.lease_term_months:
            return
        monthly_depr = self.rou_asset_value / self.lease_term_months
        current_date = self.commencement_date + relativedelta(months=1)
        sequence, accumulated = 1, 0

        while current_date <= self.end_date:
            amount = round(monthly_depr, 2)
            accumulated += amount
            if current_date + relativedelta(months=1) > self.end_date:
                amount = self.rou_asset_value - (accumulated - amount)

            self.env['ops.lease.depreciation'].create({
                'lease_id': self.id, 'sequence': sequence, 'depreciation_date': current_date, 'amount': amount,
            })
            current_date += relativedelta(months=1)
            sequence += 1

    def action_activate(self):
        """Activate lease and create initial recognition entry."""
        for lease in self:
            if lease.state != 'draft':
                raise UserError(_('Can only activate draft leases.'))
            if not lease.payment_schedule_ids:
                raise UserError(_('Please generate schedules first.'))

            move_vals = {
                'date': lease.commencement_date, 'journal_id': lease.journal_id.id,
                'ref': f'Lease Recognition: {lease.name}', 'ops_branch_id': lease.ops_branch_id.id,
                'line_ids': [
                    (0, 0, {'account_id': lease.rou_asset_account_id.id, 'name': f'ROU Asset: {lease.name}',
                            'debit': lease.rou_asset_value, 'credit': 0}),
                    (0, 0, {'account_id': lease.lease_liability_account_id.id, 'name': f'Lease Liability: {lease.name}',
                            'debit': 0, 'credit': lease.lease_liability}),
                ],
            }

            if lease.initial_direct_costs:
                # Initial direct costs: Dr ROU Asset (already included), Cr Cash/Payable
                move_vals['line_ids'].append((0, 0, {
                    'account_id': lease.company_id.account_default_pos_receivable_account_id.id or lease.rou_asset_account_id.id,
                    'name': f'Initial Direct Costs: {lease.name}', 'debit': 0, 'credit': lease.initial_direct_costs,
                }))

            move = lease.env['account.move'].create(move_vals)
            move.action_post()
            lease.write({'initial_recognition_move_id': move.id, 'state': 'active'})
            lease.message_post(body=_('Lease activated. Initial recognition entry: %s') % move.name)

    def action_terminate(self):
        """Terminate the lease early."""
        self.write({'state': 'terminated'})

    def action_cancel(self):
        """Cancel the lease."""
        for lease in self:
            if lease.state == 'active':
                raise UserError(_('Cannot cancel an active lease. Terminate it instead.'))
        self.write({'state': 'cancelled'})

    def action_view_journal_entries(self):
        """View all related journal entries."""
        self.ensure_one()
        move_ids = []
        if self.initial_recognition_move_id:
            move_ids.append(self.initial_recognition_move_id.id)
        move_ids.extend(self.payment_schedule_ids.filtered(lambda p: p.move_id).mapped('move_id').ids)
        move_ids.extend(self.depreciation_schedule_ids.filtered(lambda d: d.move_id).mapped('move_id').ids)

        return {
            'name': _('Journal Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', move_ids)],
        }


class OpsLeasePaymentSchedule(models.Model):
    """Lease Payment Schedule Line."""
    _name = 'ops.lease.payment.schedule'
    _description = 'Lease Payment Schedule'
    _order = 'sequence, payment_date'

    lease_id = fields.Many2one('ops.lease', required=True, ondelete='cascade')
    sequence = fields.Integer(string='#')
    payment_date = fields.Date(string='Payment Date', required=True)
    currency_id = fields.Many2one(related='lease_id.currency_id')
    payment_amount = fields.Monetary(string='Payment')
    interest_amount = fields.Monetary(string='Interest')
    principal_amount = fields.Monetary(string='Principal')
    balance_after = fields.Monetary(string='Balance After')
    state = fields.Selection([('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)

    def action_record_payment(self):
        """Record the lease payment."""
        for line in self:
            if line.state == 'paid':
                raise UserError(_('Payment already recorded.'))

            lease = line.lease_id
            if lease.state != 'active':
                raise UserError(_('Cannot record payment for inactive lease.'))

            # Get the lessor's payable account
            payable_account = lease.lessor_id.property_account_payable_id
            if not payable_account:
                raise UserError(_('Please configure payable account for lessor %s.') % lease.lessor_id.name)

            move_vals = {
                'date': line.payment_date, 'journal_id': lease.journal_id.id,
                'ref': f'Lease Payment: {lease.name} #{line.sequence}',
                'ops_branch_id': lease.ops_branch_id.id, 'partner_id': lease.lessor_id.id,
                'line_ids': [
                    (0, 0, {'account_id': lease.lease_liability_account_id.id, 'name': f'Lease Principal: {lease.name}',
                            'debit': line.principal_amount, 'credit': 0, 'partner_id': lease.lessor_id.id}),
                    (0, 0, {'account_id': lease.interest_expense_account_id.id, 'name': f'Lease Interest: {lease.name}',
                            'debit': line.interest_amount, 'credit': 0}),
                    (0, 0, {'account_id': payable_account.id, 'name': f'Lease Payment: {lease.name}',
                            'debit': 0, 'credit': line.payment_amount, 'partner_id': lease.lessor_id.id}),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            line.write({'state': 'paid', 'move_id': move.id})


class OpsLeaseDepreciation(models.Model):
    """Lease ROU Asset Depreciation Schedule."""
    _name = 'ops.lease.depreciation'
    _description = 'Lease Depreciation'
    _order = 'sequence, depreciation_date'

    lease_id = fields.Many2one('ops.lease', required=True, ondelete='cascade')
    sequence = fields.Integer(string='#')
    depreciation_date = fields.Date(string='Date', required=True)
    currency_id = fields.Many2one(related='lease_id.currency_id')
    amount = fields.Monetary(string='Depreciation Amount')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)

    def action_post(self):
        """Post depreciation entry."""
        for line in self:
            if line.state == 'posted':
                continue
            lease = line.lease_id
            if lease.state != 'active':
                raise UserError(_('Cannot post depreciation for inactive lease.'))

            move_vals = {
                'date': line.depreciation_date, 'journal_id': lease.journal_id.id,
                'ref': f'ROU Depreciation: {lease.name} #{line.sequence}', 'ops_branch_id': lease.ops_branch_id.id,
                'line_ids': [
                    (0, 0, {'account_id': lease.depreciation_expense_account_id.id, 'name': f'ROU Depreciation: {lease.name}',
                            'debit': line.amount, 'credit': 0}),
                    (0, 0, {'account_id': lease.accumulated_depreciation_account_id.id, 'name': f'Accumulated Depreciation: {lease.name}',
                            'debit': 0, 'credit': line.amount}),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            line.write({'state': 'posted', 'move_id': move.id})
