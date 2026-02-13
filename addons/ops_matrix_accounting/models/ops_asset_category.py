# -*- coding: utf-8 -*-
"""
OPS Asset Category with Enhanced Depreciation Methods

Task 2.4: Degressive Depreciation Fix

Features:
- Straight Line (Linear): Equal amounts each period
- Declining Balance (Degressive): Percentage of remaining book value
- Degressive then Linear: Switch when linear gives higher amount
- Prorata Temporis: Partial first period calculation
- Configurable period length (monthly/yearly)

Reference: om_account_asset depreciation patterns
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class OpsAssetCategory(models.Model):
    _name = 'ops.asset.category'
    _description = 'Fixed Asset Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _parent_store = True
    _parent_name = 'parent_id'

    parent_id = fields.Many2one(
        'ops.asset.category',
        string='Parent Category',
        index=True,
        ondelete='restrict',
    )

    parent_path = fields.Char(index=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    name = fields.Char(string='Category Name', required=True, tracking=True)
    active = fields.Boolean(default=True, help="Set active to false to hide the category without removing it.")

    # ============================================
    # Accounting Configuration
    # ============================================
    journal_id = fields.Many2one(
        'account.journal', string='Journal', required=False,
        ondelete='set null',
        domain="[('type', '=', 'general')]",
        help="Journal for posting depreciation entries. Optional until accounting is configured."
    )

    asset_account_id = fields.Many2one(
        'account.account', string='Asset Account',
        required=False, ondelete='set null',
        help="Account to book the value of new assets."
    )

    depreciation_account_id = fields.Many2one(
        'account.account', string='Accumulated Depreciation Account',
        required=False, ondelete='set null',
        help="Account for accumulated depreciation (contra-asset)."
    )

    expense_account_id = fields.Many2one(
        'account.account', string='Depreciation Expense Account',
        required=False, ondelete='set null',
        help="Account for the periodic depreciation expense."
    )

    # ============================================
    # Depreciation Method Configuration (Task 2.4)
    # ============================================
    depreciation_method = fields.Selection([
        ('straight_line', 'Straight Line (Linear)'),
        ('declining_balance', 'Declining Balance (Degressive)'),
        ('degressive_then_linear', 'Degressive then Linear'),
    ], string='Depreciation Method', default='straight_line', required=True, tracking=True,
       help="""
       • Straight Line: Equal amounts each period (Cost - Salvage) / Life
       • Declining Balance: Fixed percentage of remaining book value
       • Degressive then Linear: Declining until linear gives higher amount
       """)

    method_number = fields.Integer(
        string='Number of Depreciations',
        default=60,
        required=True,
        help='Total number of depreciation entries to generate (e.g., 60 for 5 years monthly)'
    )

    method_period = fields.Integer(
        string='Period Length (Months)',
        default=1,
        required=True,
        help='Time between two depreciations in months (1 = monthly, 12 = yearly)'
    )

    # Backward compatibility field - computed from method_number and method_period
    depreciation_duration = fields.Integer(
        string='Depreciation Duration (Years)',
        compute='_compute_depreciation_duration',
        inverse='_inverse_depreciation_duration',
        store=True,
        help="Duration over which the asset is depreciated (computed from periods)."
    )

    # ============================================
    # Degressive-specific Fields (Adopted from OM)
    # ============================================
    method_progress_factor = fields.Float(
        string='Degressive Factor',
        default=0.3,
        help="""
        Declining balance factor (depreciation rate per year).
        Example: 0.3 = 30% of book value depreciated per year.
        Common values: 0.2 (20%), 0.25 (25%), 0.3 (30%), 0.4 (40%)
        """
    )

    # ============================================
    # Prorata Temporis Configuration (Adopted from OM)
    # ============================================
    prorata = fields.Boolean(
        string='Prorata Temporis',
        default=True,
        help="""
        If checked, first depreciation is calculated proportionally from purchase date.
        If unchecked, first depreciation is a full period amount.
        """
    )

    date_first_depreciation = fields.Selection([
        ('last_day_period', 'Last Day of Purchase Period'),
        ('manual', 'Based on Purchase Date'),
    ], string='First Depreciation Date', default='manual', required=True,
       help="""
       • Last Day of Purchase Period: First depreciation on last day of purchase month/year
       • Based on Purchase Date: First depreciation exactly one period after purchase
       """)

    # Computed field for display
    depreciation_duration_display = fields.Float(
        string='Duration (Years)',
        compute='_compute_duration_display',
        help='Total depreciation duration in years'
    )

    # ============================================
    # Auto-Post Depreciation Settings (Task 2.3)
    # ============================================
    auto_post_depreciation = fields.Boolean(
        string='Auto-Post Depreciation',
        default=False,
        help='Automatically post depreciation entries when due via daily cron job. '
             'Only applies to assets in "Running" state.'
    )
    auto_post_day = fields.Integer(
        string='Auto-Post Day',
        default=0,
        help='Day of month to auto-post (0 = on due date, 1-28 = specific day). '
             'Leave at 0 to post on the exact depreciation date.'
    )

    # ============================================
    # OPS Matrix Dimensions
    # ============================================
    branch_id = fields.Many2one('ops.branch', string='Default Branch')
    business_unit_id = fields.Many2one('ops.business.unit', string='Default Business Unit')

    asset_ids = fields.One2many('ops.asset', 'category_id', string='Assets')
    asset_count = fields.Integer(compute='_compute_asset_count', string='Asset Count')

    # ============================================
    # COMPUTED FIELDS
    # ============================================

    @api.depends('method_number', 'method_period')
    def _compute_depreciation_duration(self):
        """Compute depreciation duration in years from periods."""
        for cat in self:
            if cat.method_period and cat.method_number:
                cat.depreciation_duration = int((cat.method_number * cat.method_period) / 12)
            else:
                cat.depreciation_duration = 0

    def _inverse_depreciation_duration(self):
        """Allow setting duration in years and compute periods."""
        for cat in self:
            if cat.depreciation_duration and cat.method_period:
                cat.method_number = int((cat.depreciation_duration * 12) / cat.method_period)

    @api.depends('method_number', 'method_period')
    def _compute_duration_display(self):
        """Compute depreciation duration for display (with decimals)."""
        for cat in self:
            if cat.method_period:
                cat.depreciation_duration_display = (cat.method_number * cat.method_period) / 12
            else:
                cat.depreciation_duration_display = 0

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for category in self:
            category.asset_count = len(category.asset_ids)

    # ============================================
    # ORM CONSTRAINTS
    # ============================================

    @api.constrains('name')
    def _check_unique_name(self):
        """Ensure asset category names are unique (case-insensitive)."""
        for record in self:
            existing = self.search([
                ('id', '!=', record.id),
                ('name', '=ilike', record.name)
            ], limit=1)
            if existing:
                raise ValidationError(_(
                    "Asset category name '%(name)s' already exists."
                ) % {'name': record.name})

    @api.constrains('method_progress_factor')
    def _check_degressive_factor(self):
        """Validate degressive factor is in reasonable range."""
        for cat in self:
            if cat.depreciation_method in ('declining_balance', 'degressive_then_linear'):
                if cat.method_progress_factor <= 0:
                    raise ValidationError(_(
                        'Degressive factor must be greater than 0 for declining balance method.'
                    ))
                if cat.method_progress_factor > 1:
                    raise ValidationError(_(
                        'Degressive factor should be between 0.01 and 1.0 (1%% to 100%%).\n'
                        'Current value: %(value)s'
                    ) % {'value': cat.method_progress_factor})

    @api.constrains('method_number', 'method_period')
    def _check_depreciation_params(self):
        """Validate depreciation parameters."""
        for cat in self:
            if cat.method_number <= 0:
                raise ValidationError(_('Number of depreciations must be positive.'))
            if cat.method_period <= 0:
                raise ValidationError(_('Period length must be positive.'))
            if cat.method_period > 12:
                raise ValidationError(_('Period length cannot exceed 12 months (1 year).'))

    # ============================================
    # ONCHANGE HANDLERS
    # ============================================

    @api.onchange('depreciation_method')
    def _onchange_depreciation_method(self):
        """Set sensible defaults when method changes."""
        if self.depreciation_method == 'straight_line':
            self.method_progress_factor = 0.0
        elif self.depreciation_method in ('declining_balance', 'degressive_then_linear'):
            if not self.method_progress_factor or self.method_progress_factor <= 0:
                self.method_progress_factor = 0.3

    @api.onchange('depreciation_duration')
    def _onchange_depreciation_duration(self):
        """Update method_number when duration changes (backward compat)."""
        if self.depreciation_duration and self.method_period:
            self.method_number = int((self.depreciation_duration * 12) / self.method_period)

    # ============================================
    # ACTIONS
    # ============================================

    def open_assets(self):
        self.ensure_one()
        return {
            'name': _('Assets'),
            'view_mode': 'list,form',
            'res_model': 'ops.asset',
            'type': 'ir.actions.act_window',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id}
        }

    def unlink(self):
        for category in self:
            if category.asset_ids:
                raise UserError(_('You cannot delete a category that is being used by an asset.'))
        return super(OpsAssetCategory, self).unlink()
