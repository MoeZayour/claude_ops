# -*- coding: utf-8 -*-
"""
OPS Matrix Asset Intelligence Engine (v2 Data Contracts)
========================================================

Fixed Asset reporting wizard refactored to use Shape C (matrix) data contracts.
Reports: Asset Register, Depreciation Forecast, Disposal Analysis, Asset Movement.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round
from dataclasses import asdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeCReport, ColumnDef, MatrixRow,
)

_logger = logging.getLogger(__name__)


class OpsAssetReportWizard(models.TransientModel):
    """Asset Intelligence - CAPEX & Depreciation Engine"""
    _name = 'ops.asset.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Asset Intelligence - Fixed Asset Report Wizard'

    report_template_id = fields.Many2one(
        domain="[('engine', '=', 'asset'), '|', ('is_global', '=', True), ('user_id', '=', uid)]"
    )

    # ============================================
    # 1. REPORT TYPE SELECTOR
    # ============================================
    report_type = fields.Selection([
        ('register', 'Asset Register'),
        ('forecast', 'Depreciation Forecast'),
        ('disposal', 'Disposal Analysis'),
        ('movement', 'Asset Movement'),
    ], string='Report Type', required=True, default='register',
       help='Select the type of asset report to generate')

    # ============================================
    # 2. DATE FILTERS
    # ============================================
    date_from = fields.Date(string='From Date', help='Filter assets/depreciation from this date')
    date_to = fields.Date(
        string='To Date',
        default=lambda self: fields.Date.context_today(self),
        help='Calculate NBV as of this date / Filter depreciation to this date'
    )
    as_of_date = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        help='Reference date for asset register'
    )

    # ============================================
    # 3. DIMENSION FILTERS
    # ============================================
    branch_ids = fields.Many2many(
        'ops.branch', 'asset_wizard_branch_rel', 'wizard_id', 'branch_id',
        string='Branches', help='Filter by specific branches. Leave empty for all.'
    )
    business_unit_ids = fields.Many2many(
        'ops.business.unit', 'asset_wizard_bu_rel', 'wizard_id', 'bu_id',
        string='Business Units', help='Filter by specific business units. Leave empty for all.'
    )

    # ============================================
    # 4. ASSET FILTERS
    # ============================================
    asset_category_ids = fields.Many2many(
        'ops.asset.category', 'asset_wizard_category_rel', 'wizard_id', 'category_id',
        string='Asset Categories', help='Filter by asset categories. Leave empty for all.'
    )
    asset_state = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('open', 'Running'),
        ('close', 'Close'),
    ], string='Asset Status', default='all', help='Filter by asset status')

    # ============================================
    # 5. FORECAST OPTIONS
    # ============================================
    forecast_months = fields.Integer(
        string='Forecast Months', default=12,
        help='Number of months to forecast depreciation'
    )

    # ============================================
    # 6. DISPLAY OPTIONS
    # ============================================
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('category', 'By Category'),
        ('branch', 'By Branch'),
        ('status', 'By Status'),
    ], string='Group By', default='none')

    # ============================================
    # 7. COMPUTED / PREVIEW
    # ============================================
    total_cost = fields.Monetary(compute='_compute_asset_totals', string='Total Cost',
                                  currency_field='currency_id')
    total_nbv = fields.Monetary(compute='_compute_asset_totals', string='Total NBV',
                                 currency_field='currency_id')

    # ============================================
    # BASE CLASS HOOKS
    # ============================================

    def _get_engine_name(self):
        return 'asset'

    def _get_report_shape(self):
        return 'matrix'

    def _get_report_titles(self):
        return {
            'register': 'Fixed Asset Register',
            'forecast': 'Depreciation Forecast',
            'disposal': 'Disposal Analysis',
            'movement': 'Asset Movement Report',
        }

    def _get_scalar_fields_for_template(self):
        return ['report_type', 'asset_state', 'forecast_months', 'group_by']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'business_unit_ids', 'asset_category_ids']

    def _get_report_template_xmlid(self):
        self.ensure_one()
        mapping = {
            'register': 'ops_matrix_accounting.report_asset_register_corporate',
            'forecast': 'ops_matrix_accounting.report_asset_forecast_corporate',
            'disposal': 'ops_matrix_accounting.report_asset_disposal_corporate',
            'movement': 'ops_matrix_accounting.report_asset_movement_corporate',
        }
        return mapping.get(self.report_type, mapping['register'])

    def _add_filter_summary_parts(self, parts):
        if self.branch_ids:
            parts.append(f"Branches: {len(self.branch_ids)} selected")
        if self.business_unit_ids:
            parts.append(f"BUs: {len(self.business_unit_ids)} selected")
        if self.asset_category_ids:
            parts.append(f"Categories: {len(self.asset_category_ids)} selected")
        if self.asset_state != 'all':
            parts.append(f"Status: {dict(self._fields['asset_state'].selection).get(self.asset_state)}")

    def _estimate_record_count(self):
        return self.env['ops.asset'].search_count(self._build_asset_domain())

    # ============================================
    # COMPUTED FIELDS
    # ============================================

    @api.depends('branch_ids', 'business_unit_ids', 'asset_category_ids', 'asset_state')
    def _compute_asset_totals(self):
        for wizard in self:
            try:
                assets = self.env['ops.asset'].search(wizard._build_asset_domain())
                wizard.total_cost = sum(assets.mapped('original_value'))
                wizard.total_nbv = sum(assets.mapped('book_value'))
            except Exception as e:
                _logger.error(f"Error computing asset totals: {e}")
                wizard.total_cost = 0.0
                wizard.total_nbv = 0.0

    # ============================================
    # DOMAIN BUILDING
    # ============================================

    def _build_asset_domain(self):
        """Build domain for asset queries."""
        self.ensure_one()
        domain = [('company_id', '=', self.company_id.id)]
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))
        if self.asset_category_ids:
            domain.append(('category_id', 'in', self.asset_category_ids.ids))
        if self.asset_state and self.asset_state != 'all':
            domain.append(('state', '=', self.asset_state))

        return domain

    def _build_depreciation_domain(self):
        """Build domain for depreciation line queries."""
        self.ensure_one()
        domain = [('asset_id.company_id', '=', self.company_id.id)]
        # Branch isolation via asset relationship
        domain += self._get_branch_filter_domain(branch_field='asset_id.ops_branch_id')

        if self.branch_ids:
            domain.append(('asset_id.ops_branch_id', 'in', self.branch_ids.ids))
        if self.asset_category_ids:
            domain.append(('asset_id.category_id', 'in', self.asset_category_ids.ids))
        if self.date_from:
            domain.append(('depreciation_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('depreciation_date', '<=', self.date_to))

        return domain

    # ============================================
    # REPORT DATA (v2 contracts)
    # ============================================

    def _get_report_data(self):
        """Dispatch to the correct report data method."""
        self.ensure_one()
        self._check_intelligence_access(self._get_pillar_name())

        dispatch = {
            'register': self._get_register_data,
            'forecast': self._get_forecast_data,
            'disposal': self._get_disposal_data,
            'movement': self._get_movement_data,
        }
        return dispatch.get(self.report_type, self._get_register_data)()

    def _can_see_cost(self):
        """Check if current user can see cost/NBV columns."""
        return self.env.user.has_group('ops_matrix_core.group_ops_see_cost')

    def _get_register_data(self):
        """Asset Register -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'register', 'Fixed Asset Register', 'matrix')
        colors = build_report_colors(self.company_id)
        show_cost = self._can_see_cost()

        columns = [
            ColumnDef(key='name', label='Asset Name', col_type='string'),
            ColumnDef(key='code', label='Code', col_type='string', width=8),
            ColumnDef(key='category', label='Category', col_type='string'),
            ColumnDef(key='purchase_date', label='Purchase Date', col_type='date'),
            ColumnDef(key='branch', label='Branch', col_type='string'),
            ColumnDef(key='status', label='Status', col_type='string', width=8),
        ]
        if show_cost:
            columns.extend([
                ColumnDef(key='cost', label='Cost', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='accum_dep', label='Accum. Depreciation', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='nbv', label='NBV', col_type='currency', align='right', subtotal=True),
            ])

        assets = self.env['ops.asset'].search(self._build_asset_domain(), order='category_id, name')
        rows = []
        total_cost = 0.0
        total_accum = 0.0
        total_nbv = 0.0

        for asset in assets:
            cost = asset.original_value
            nbv = asset.book_value
            accum = cost - nbv
            total_cost += cost
            total_accum += accum
            total_nbv += nbv

            vals = {
                'name': asset.name or '',
                'code': asset.code if hasattr(asset, 'code') else '',
                'category': asset.category_id.name if asset.category_id else '',
                'purchase_date': str(asset.acquisition_date) if asset.acquisition_date else '',
                'branch': asset.ops_branch_id.name if asset.ops_branch_id else '',
                'status': dict(asset._fields['state'].selection).get(asset.state, ''),
            }
            if show_cost:
                vals.update({'cost': cost, 'accum_dep': accum, 'nbv': nbv})
            rows.append(MatrixRow(values=vals))

        totals = {'count': len(rows)}
        if show_cost:
            totals.update({'cost': total_cost, 'accum_dep': total_accum, 'nbv': total_nbv})

        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_forecast_data(self):
        """Depreciation Forecast -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'forecast', 'Depreciation Forecast', 'matrix')
        colors = build_report_colors(self.company_id)
        show_cost = self._can_see_cost()

        # Build month columns
        today = self.date_to or fields.Date.today()
        columns = [
            ColumnDef(key='name', label='Asset', col_type='string'),
            ColumnDef(key='category', label='Category', col_type='string'),
        ]
        if show_cost:
            columns.append(ColumnDef(key='nbv_start', label='Current NBV', col_type='currency', align='right'))

        month_keys = []
        for i in range(self.forecast_months):
            dt = today + relativedelta(months=i)
            key = f'm_{dt.year}_{dt.month:02d}'
            label = dt.strftime('%b %Y')
            month_keys.append(key)
            if show_cost:
                columns.append(ColumnDef(key=key, label=label, col_type='currency', align='right', subtotal=True))

        domain = self._build_asset_domain()
        domain.append(('state', '=', 'open'))
        assets = self.env['ops.asset'].search(domain, order='category_id, name')

        rows = []
        for asset in assets:
            vals = {
                'name': asset.name or '',
                'category': asset.category_id.name if asset.category_id else '',
            }
            if show_cost:
                vals['nbv_start'] = asset.book_value
                # Estimate monthly depreciation
                if hasattr(asset, 'method_number') and asset.method_number > 0:
                    monthly_dep = asset.original_value / asset.method_number
                else:
                    monthly_dep = 0.0
                for key in month_keys:
                    vals[key] = float_round(monthly_dep, precision_digits=2)
            rows.append(MatrixRow(values=vals))

        totals = {'count': len(rows)}
        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_disposal_data(self):
        """Disposal Analysis -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'disposal', 'Disposal Analysis', 'matrix')
        colors = build_report_colors(self.company_id)
        show_cost = self._can_see_cost()

        columns = [
            ColumnDef(key='name', label='Asset', col_type='string'),
            ColumnDef(key='category', label='Category', col_type='string'),
            ColumnDef(key='disposal_date', label='Disposal Date', col_type='date'),
        ]
        if show_cost:
            columns.extend([
                ColumnDef(key='cost', label='Original Cost', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='accum_dep', label='Accum. Depreciation', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='nbv_at_disposal', label='NBV at Disposal', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='sale_price', label='Sale Price', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='gain_loss', label='Gain/Loss', col_type='currency', align='right', subtotal=True),
            ])
        columns.append(ColumnDef(key='branch', label='Branch', col_type='string'))

        domain = self._build_asset_domain()
        domain.append(('state', '=', 'close'))
        if self.date_from:
            domain.append(('disposal_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('disposal_date', '<=', self.date_to))

        assets = self.env['ops.asset'].search(domain, order='disposal_date, name')
        rows = []
        for asset in assets:
            cost = asset.original_value
            nbv = asset.book_value
            accum = cost - nbv
            sale_price = asset.salvage_value if hasattr(asset, 'salvage_value') else 0.0
            gain_loss = sale_price - nbv

            vals = {
                'name': asset.name or '',
                'category': asset.category_id.name if asset.category_id else '',
                'disposal_date': str(asset.disposal_date) if hasattr(asset, 'disposal_date') and asset.disposal_date else '',
                'branch': asset.ops_branch_id.name if asset.ops_branch_id else '',
            }
            if show_cost:
                vals.update({
                    'cost': cost, 'accum_dep': accum, 'nbv_at_disposal': nbv,
                    'sale_price': sale_price, 'gain_loss': gain_loss,
                })
            rows.append(MatrixRow(values=vals))

        totals = {'count': len(rows)}
        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_movement_data(self):
        """Asset Movement -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'movement', 'Asset Movement Report', 'matrix')
        colors = build_report_colors(self.company_id)
        show_cost = self._can_see_cost()

        columns = [
            ColumnDef(key='category', label='Category', col_type='string'),
        ]
        if show_cost:
            columns.extend([
                ColumnDef(key='opening_nbv', label='Opening NBV', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='additions', label='Additions', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='disposals', label='Disposals', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='depreciation', label='Depreciation', col_type='currency', align='right', subtotal=True),
                ColumnDef(key='closing_nbv', label='Closing NBV', col_type='currency', align='right', subtotal=True),
            ])
        columns.append(ColumnDef(key='asset_count', label='Count', col_type='number', align='right', subtotal=True))

        categories = self.env['ops.asset.category'].search([('company_id', '=', self.company_id.id)])
        rows = []
        grand = {'opening_nbv': 0, 'additions': 0, 'disposals': 0, 'depreciation': 0, 'closing_nbv': 0, 'asset_count': 0}

        for cat in categories:
            cat_domain = self._build_asset_domain()
            cat_domain.append(('category_id', '=', cat.id))
            assets = self.env['ops.asset'].search(cat_domain)
            if not assets:
                continue

            opening = sum(a.original_value for a in assets)
            closing = sum(a.book_value for a in assets)
            dep = opening - closing
            additions = sum(a.original_value for a in assets
                          if a.acquisition_date and self.date_from and a.acquisition_date >= self.date_from)
            disposals = sum(a.original_value for a in assets if a.state == 'close')
            count = len(assets)

            vals = {'category': cat.name or ''}
            if show_cost:
                vals.update({
                    'opening_nbv': opening, 'additions': additions, 'disposals': disposals,
                    'depreciation': dep, 'closing_nbv': closing,
                })
            vals['asset_count'] = count
            rows.append(MatrixRow(values=vals))

            for k in grand:
                grand[k] += vals.get(k, 0)

        grand_vals = {'category': 'Total', 'asset_count': grand['asset_count']}
        if show_cost:
            for k in ['opening_nbv', 'additions', 'disposals', 'depreciation', 'closing_nbv']:
                grand_vals[k] = grand[k]
        rows.append(MatrixRow(style='grand_total', values=grand_vals))

        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=grand))

    # ============================================
    # REPORT ACTION
    # ============================================

    def _return_report_action(self, data):
        """Return report action for PDF generation."""
        report_refs = {
            'register': 'ops_matrix_accounting.action_report_asset_register',
            'forecast': 'ops_matrix_accounting.action_report_asset_forecast',
            'disposal': 'ops_matrix_accounting.action_report_asset_disposal',
            'movement': 'ops_matrix_accounting.action_report_asset_movement',
        }
        return self.env.ref(report_refs.get(self.report_type, report_refs['register'])).report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_assets(self):
        """Open filtered assets in list view."""
        self.ensure_one()
        return {
            'name': _('Fixed Assets'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.asset',
            'view_mode': 'list,form',
            'domain': self._build_asset_domain(),
            'context': {'search_default_group_category': 1},
        }

    # ============================================
    # ONCHANGE
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type == 'disposal':
            self.asset_state = 'close'
        elif self.report_type == 'forecast':
            self.asset_state = 'open'
        else:
            self.asset_state = 'all'
