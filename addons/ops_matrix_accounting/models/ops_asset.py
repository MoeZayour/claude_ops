# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
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

    def generate_depreciation_schedule(self):
        self.ensure_one()
        _logger.info(f"Generating depreciation schedule for asset {self.name} ({self.id})")
        
        self.depreciation_ids.filtered(lambda l: l.state == 'draft').unlink()

        if self.depreciable_value < 0:
            raise UserError(_("Depreciable value cannot be negative."))
        if self.depreciable_value == 0:
            _logger.warning(f"Depreciable value is zero for asset {self.name}. No schedule generated.")
            return

        duration_years = self.category_id.depreciation_duration
        if not duration_years > 0:
            raise UserError(_("Depreciation duration must be greater than 0 years."))

        depreciation_date = self.purchase_date
        total_periods = duration_years * 12
        
        lines_to_create = []
        for i in range(total_periods):
            depreciation_date += relativedelta(months=1)
            
            lines_to_create.append({
                'asset_id': self.id,
                'depreciation_date': depreciation_date,
                'state': 'draft',
            })
        
        if not lines_to_create:
            return
            
        dep_lines = self.env['ops.asset.depreciation'].create(lines_to_create)
        dep_lines._compute_amount()
        _logger.info(f"Successfully created {len(dep_lines)} depreciation lines for asset {self.name}.")
    
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
