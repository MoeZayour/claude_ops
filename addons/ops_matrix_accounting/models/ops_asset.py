# -*- coding: utf-8 -*-
"""
OPS Asset with Enhanced Depreciation Schedule Generation

Task 2.4: Degressive Depreciation Fix

Supports:
- Linear (Straight Line): Equal amounts each period
- Degressive (Declining Balance): Percentage of remaining value
- Degressive then Linear: Switch when linear gives higher amount
- Prorata temporis: Partial first period adjustment
- Monthly or yearly periods
- Salvage value handling

Reference: om_account_asset depreciation calculation patterns
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, float_is_zero
from dateutil.relativedelta import relativedelta
import calendar
import logging

_logger = logging.getLogger(__name__)

class OpsAsset(models.Model):
    _name = 'ops.asset'
    _description = 'Fixed Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'ops.matrix.mixin', 'ops.analytic.mixin']
    _order = 'purchase_date desc, name'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    category_id = fields.Many2one(
        'ops.asset.category', string='Category', required=True,
        tracking=True, ondelete='restrict'
    )
    code = fields.Char(string='Asset Code', size=32, readonly=True, copy=False)
    
    purchase_date = fields.Date(
        string='Purchase Date', required=True,
        default=fields.Date.context_today, tracking=True
    )
    purchase_value = fields.Float(
        string='Purchase Value', required=True, tracking=True
    )
    salvage_value = fields.Float(
        string='Salvage Value', default=0.0, tracking=True,
        help="Estimated residual value of an asset at the end of its useful life."
    )
    notes = fields.Text(string='Notes')
    depreciable_value = fields.Float(
        compute='_compute_depreciation_values', string='Depreciable Value',
        store=True, tracking=True, compute_sudo=True
    )
    book_value = fields.Float(
        compute='_compute_depreciation_values', string='Book Value',
        store=True, tracking=True, compute_sudo=True
    )
    fully_depreciated = fields.Boolean(
        compute='_compute_depreciation_values',
        string='Fully Depreciated',
        store=True,
        tracking=True,
        compute_sudo=True,
        help="Indicates the asset has no remaining depreciable value."
    )
    accumulated_depreciation = fields.Float(
        compute='_compute_depreciation_values', string='Accumulated Depreciation',
        store=True, compute_sudo=True
    )

    disposal_date = fields.Date(
        string='Disposal Date',
        tracking=True,
        help="Date when the asset was disposed."
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('sold', 'Sold'),
        ('disposed', 'Disposed')
    ], string='Status', default='draft', required=True, tracking=True, index=True)

    depreciation_ids = fields.One2many(
        'ops.asset.depreciation', 'asset_id',
        string='Depreciation Lines', readonly=True
    )
    depreciation_count = fields.Integer(
        compute='_compute_depreciation_count', string='Depreciation Count'
    )

    # Impairment Fields (IAS 36)
    impaired = fields.Boolean(string='Impaired', default=False, tracking=True)
    impairment_date = fields.Date(string='Impairment Date', tracking=True)
    original_value = fields.Float(string='Original Value',
                                   help="Original depreciable value before impairment")
    impairment_loss = fields.Float(string='Impairment Loss', compute='_compute_impairment', store=True)
    recoverable_amount = fields.Float(string='Recoverable Amount',
                                       help="Higher of fair value less costs to sell and value in use")
    impairment_move_id = fields.Many2one('account.move', string='Impairment Entry', readonly=True)
    impairment_loss_account_id = fields.Many2one(
        'account.account', string='Impairment Loss Account',
        help="Account to record impairment losses"
    )

    # Analytic Fields are inherited from ops.analytic.mixin

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.asset') or _('New')
            # Ensure analytic fields are set from category if not provided
            if 'category_id' in vals and ('ops_branch_id' not in vals or 'ops_business_unit_id' not in vals):
                category = self.env['ops.asset.category'].browse(vals['category_id'])
                if 'ops_branch_id' not in vals:
                    vals['ops_branch_id'] = category.branch_id.id
                if 'ops_business_unit_id' not in vals:
                    vals['ops_business_unit_id'] = category.business_unit_id.id
        return super(OpsAsset, self).create(vals_list)

    @api.depends('purchase_value', 'salvage_value', 'depreciation_ids.amount', 'depreciation_ids.state')
    def _compute_depreciation_values(self):
        for asset in self:
            asset.depreciable_value = asset.purchase_value - asset.salvage_value

            accumulated_depreciation = sum(
                line.amount for line in asset.depreciation_ids if line.state == 'posted'
            )
            asset.accumulated_depreciation = accumulated_depreciation
            asset.book_value = asset.purchase_value - accumulated_depreciation
            asset.fully_depreciated = asset.book_value <= asset.salvage_value

    @api.depends('depreciation_ids')
    def _compute_depreciation_count(self):
        for asset in self:
            asset.depreciation_count = len(asset.depreciation_ids)

    @api.depends('book_value', 'recoverable_amount', 'impaired')
    def _compute_impairment(self):
        for asset in self:
            if asset.impaired and asset.recoverable_amount:
                # Impairment loss is the excess of carrying amount over recoverable amount
                carrying = asset.book_value
                asset.impairment_loss = max(carrying - asset.recoverable_amount, 0)
            else:
                asset.impairment_loss = 0

    @api.constrains('purchase_value', 'salvage_value')
    def _check_salvage_value(self):
        for asset in self:
            if asset.salvage_value > asset.purchase_value:
                raise ValidationError(_("Salvage value cannot be greater than the purchase value."))
            if asset.purchase_value <= 0:
                raise ValidationError(_("Purchase value must be positive."))

    # =========================================================================
    # ZERO-TRUST SECURITY: Matrix Dimension Validation for Assets
    # =========================================================================

    @api.constrains('ops_branch_id')
    def _check_asset_branch_required(self):
        """
        Validate that all assets have a Branch assigned.
        Assets represent company property and must be tracked by location/branch.
        """
        for asset in self:
            if not asset.ops_branch_id:
                raise ValidationError(
                    _("SECURITY BLOCK: Asset '%s' requires a Branch.\n\n"
                      "Matrix Governance requires all assets to be assigned to a Branch "
                      "for proper location tracking and depreciation allocation.") % asset.name
                )

    def action_confirm(self):
        for asset in self:
            if not asset.category_id:
                raise UserError(_("Please assign an asset category before confirming."))
            if asset.state != 'draft':
                raise UserError(_("Only draft assets can be confirmed."))
            asset.generate_depreciation_schedule()
            asset.write({'state': 'running'})
        return True

    def action_pause(self):
        self.write({'state': 'paused'})

    def action_resume(self):
        self.write({'state': 'running'})

    def action_set_to_draft(self):
        for asset in self:
            if any(line.state == 'posted' for line in asset.depreciation_ids):
                raise UserError(_("Cannot set to draft an asset that has posted depreciation entries."))
            # Unlink moves and then depreciation lines
            asset.depreciation_ids.mapped('move_id').button_draft()
            asset.depreciation_ids.mapped('move_id').unlink()
            asset.depreciation_ids.unlink()
            asset.write({'state': 'draft'})

    def action_sell(self):
        self.write({'state': 'sold'})
        return {
            'warning': {
                'title': _("Action Required"),
                'message': _("Asset marked as Sold. Please create a manual journal entry to record the gain/loss on disposal."),
            }
        }

    def action_dispose(self):
        self.write({
            'state': 'disposed',
            'disposal_date': fields.Date.context_today(self),
        })
        return {
            'warning': {
                'title': _("Action Required"),
                'message': _("Asset marked as Disposed. Please create a manual journal entry to write off the remaining book value."),
            }
        }

    def action_impair_asset(self):
        """Open impairment wizard to record asset impairment per IAS 36."""
        self.ensure_one()
        if self.state != 'running':
            raise UserError(_('Can only impair running assets.'))
        if self.book_value <= self.salvage_value:
            raise UserError(_('Asset is already fully depreciated. No impairment possible.'))
        return {
            'name': _('Record Impairment'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.asset.impairment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
                'default_current_carrying_amount': self.book_value,
                'default_impairment_loss_account_id': self.impairment_loss_account_id.id if self.impairment_loss_account_id else False,
            }
        }

    def action_view_impairment_entry(self):
        """View the impairment journal entry."""
        self.ensure_one()
        if not self.impairment_move_id:
            raise UserError(_('No impairment entry exists for this asset.'))
        return {
            'name': _('Impairment Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.impairment_move_id.id,
            'view_mode': 'form',
        }

    def generate_depreciation_schedule(self):
        """
        Generate depreciation schedule based on category method.

        Supports:
        - Linear (Straight Line): Equal amounts each period
        - Degressive (Declining Balance): Percentage of remaining value
        - Degressive then Linear: Switch when linear gives higher amount

        Also handles:
        - Prorata temporis (partial first period)
        - Monthly or yearly periods
        - Salvage value
        """
        self.ensure_one()
        _logger.info(f"Generating depreciation schedule for asset: {self.name} (ID: {self.id})")

        # Clear existing draft lines
        self.depreciation_ids.filtered(lambda l: l.state == 'draft').unlink()

        # Validations
        if self.depreciable_value <= 0:
            _logger.warning(f"Asset {self.name} has no depreciable value. No schedule generated.")
            return

        category = self.category_id
        if not category:
            raise UserError(_("Please assign an asset category before generating schedule."))

        if category.method_number <= 0:
            raise UserError(_("Number of depreciations must be greater than 0."))

        # Get parameters
        method = category.depreciation_method
        total_periods = category.method_number
        period_months = category.method_period
        degressive_factor = category.method_progress_factor
        prorata = category.prorata
        depreciable_value = self.depreciable_value
        salvage_value = self.salvage_value
        purchase_date = self.purchase_date

        _logger.info(
            f"Parameters: method={method}, periods={total_periods}, "
            f"period_months={period_months}, factor={degressive_factor}, "
            f"prorata={prorata}, depreciable={depreciable_value}"
        )

        # Calculate first depreciation date
        if category.date_first_depreciation == 'last_day_period':
            if period_months >= 12:
                # Yearly: last day of fiscal year
                first_date = purchase_date.replace(month=12, day=31)
            else:
                # Monthly: last day of purchase month
                last_day = calendar.monthrange(purchase_date.year, purchase_date.month)[1]
                first_date = purchase_date.replace(day=last_day)
        else:
            # Manual: one period after purchase
            first_date = purchase_date + relativedelta(months=period_months)

        # Generate schedule based on method
        if method == 'straight_line':
            lines = self._compute_linear_depreciation(
                depreciable_value, total_periods, period_months,
                first_date, prorata, purchase_date
            )
        elif method == 'declining_balance':
            lines = self._compute_degressive_depreciation(
                depreciable_value, total_periods, period_months,
                first_date, prorata, purchase_date, degressive_factor,
                salvage_value
            )
        elif method == 'degressive_then_linear':
            lines = self._compute_degressive_then_linear(
                depreciable_value, total_periods, period_months,
                first_date, prorata, purchase_date, degressive_factor,
                salvage_value
            )
        else:
            raise UserError(_("Unknown depreciation method: %s") % method)

        # Create depreciation lines
        if lines:
            self.env['ops.asset.depreciation'].create(lines)
            _logger.info(f"Created {len(lines)} depreciation lines for asset {self.name}")

        return True

    def _compute_linear_depreciation(self, depreciable_value, total_periods, period_months,
                                      first_date, prorata, purchase_date):
        """
        Straight-line depreciation: Equal amounts each period.

        Formula: (Purchase Value - Salvage Value) / Number of Periods
        """
        lines = []

        # Base amount per period
        period_amount = depreciable_value / total_periods
        period_amount = float_round(period_amount, precision_digits=2)

        # Prorata adjustment for first period
        if prorata:
            days_in_first_period = (first_date - purchase_date).days
            if period_months >= 12:
                total_days = 365
            else:
                total_days = period_months * 30  # Approximate
            prorata_factor = min(days_in_first_period / total_days, 1.0) if total_days > 0 else 1.0
            first_amount = float_round(period_amount * prorata_factor, precision_digits=2)
        else:
            first_amount = period_amount

        # Generate lines
        current_date = first_date
        remaining = depreciable_value

        for i in range(total_periods):
            if i == 0:
                amount = first_amount
            elif i == total_periods - 1:
                # Last period: remaining balance to avoid rounding issues
                amount = float_round(remaining, precision_digits=2)
            else:
                amount = period_amount

            amount = min(amount, remaining)  # Don't exceed remaining

            if amount > 0.01:  # Skip tiny amounts
                lines.append({
                    'asset_id': self.id,
                    'sequence': i + 1,
                    'depreciation_date': current_date,
                    'amount': amount,
                    'remaining_value': float_round(remaining - amount, precision_digits=2),
                    'state': 'draft',
                })
                remaining -= amount

            # Next period date
            current_date = current_date + relativedelta(months=period_months)

        return lines

    def _compute_degressive_depreciation(self, depreciable_value, total_periods, period_months,
                                          first_date, prorata, purchase_date, factor,
                                          salvage_value):
        """
        Declining balance depreciation: Fixed percentage of book value.

        Formula: Book Value × Degressive Factor (annual) / periods per year
        Stops when book value reaches salvage value.
        """
        lines = []

        # Periods per year
        if period_months >= 12:
            periods_per_year = 1
        else:
            periods_per_year = 12 / period_months

        # Degressive rate per period
        rate_per_period = factor / periods_per_year

        current_date = first_date
        book_value = depreciable_value + salvage_value  # Start with purchase value
        remaining = depreciable_value

        for i in range(total_periods):
            if remaining <= 0.01:
                break

            # Calculate degressive amount based on remaining book value
            amount = book_value * rate_per_period

            # Prorata for first period
            if i == 0 and prorata:
                days_in_first_period = (first_date - purchase_date).days
                total_days = period_months * 30 if period_months < 12 else 365
                prorata_factor = min(days_in_first_period / total_days, 1.0) if total_days > 0 else 1.0
                amount = amount * prorata_factor

            # Round and cap
            amount = float_round(amount, precision_digits=2)
            amount = min(amount, remaining)

            # Ensure we don't go below salvage
            if amount > 0.01:
                lines.append({
                    'asset_id': self.id,
                    'sequence': i + 1,
                    'depreciation_date': current_date,
                    'amount': amount,
                    'remaining_value': float_round(remaining - amount, precision_digits=2),
                    'state': 'draft',
                })
                book_value -= amount
                remaining -= amount

            current_date = current_date + relativedelta(months=period_months)

        # If remaining value exists after all periods, add final adjustment
        if remaining > 0.01:
            lines.append({
                'asset_id': self.id,
                'sequence': len(lines) + 1,
                'depreciation_date': current_date,
                'amount': float_round(remaining, precision_digits=2),
                'remaining_value': 0.0,
                'state': 'draft',
            })

        return lines

    def _compute_degressive_then_linear(self, depreciable_value, total_periods, period_months,
                                         first_date, prorata, purchase_date, factor,
                                         salvage_value):
        """
        Declining balance switching to straight-line.

        Uses degressive until straight-line gives higher depreciation,
        then switches to straight-line for remaining periods.
        """
        lines = []

        # Periods per year
        if period_months >= 12:
            periods_per_year = 1
        else:
            periods_per_year = 12 / period_months

        rate_per_period = factor / periods_per_year

        current_date = first_date
        book_value = depreciable_value + salvage_value
        remaining = depreciable_value
        periods_remaining = total_periods

        for i in range(total_periods):
            if remaining <= 0.01:
                break

            # Calculate both methods
            degressive_amount = book_value * rate_per_period
            linear_amount = remaining / periods_remaining if periods_remaining > 0 else remaining

            # Use higher amount (switch point detection)
            amount = max(degressive_amount, linear_amount)

            # Prorata for first period
            if i == 0 and prorata:
                days_in_first_period = (first_date - purchase_date).days
                total_days = period_months * 30 if period_months < 12 else 365
                prorata_factor = min(days_in_first_period / total_days, 1.0) if total_days > 0 else 1.0
                amount = amount * prorata_factor

            # Round and cap
            amount = float_round(amount, precision_digits=2)
            amount = min(amount, remaining)

            if amount > 0.01:
                lines.append({
                    'asset_id': self.id,
                    'sequence': i + 1,
                    'depreciation_date': current_date,
                    'amount': amount,
                    'remaining_value': float_round(remaining - amount, precision_digits=2),
                    'state': 'draft',
                })
                book_value -= amount
                remaining -= amount

            periods_remaining -= 1
            current_date = current_date + relativedelta(months=period_months)

        return lines
    
    def open_depreciation_lines(self):
        self.ensure_one()
        return {
            'name': _('Depreciation Lines'),
            'view_mode': 'list,form',
            'res_model': 'ops.asset.depreciation',
            'type': 'ir.actions.act_window',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id}
        }

    def unlink(self):
        if any(asset.state != 'draft' for asset in self):
            raise UserError(_('You can only delete assets in the "Draft" state.'))
        return super(OpsAsset, self).unlink()
