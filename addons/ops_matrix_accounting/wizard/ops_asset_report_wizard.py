# -*- coding: utf-8 -*-
"""
OPS Matrix Asset Intelligence Engine
====================================

Comprehensive Fixed Asset tracking and Depreciation forecasting wizard.
Provides asset register, depreciation forecast, and disposal analysis
for CAPEX management.

Reports Supported:
- Asset Register: Complete asset listing with NBV
- Depreciation Forecast: Future depreciation schedule
- Disposal Analysis: Asset movements (additions, disposals)

Author: OPS Matrix Framework
Version: 1.0 (Phase 4 - Asset Engine)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils, float_round
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsAssetReportWizard(models.TransientModel):
    """Asset Intelligence - CAPEX & Depreciation Engine"""
    _name = 'ops.asset.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Asset Intelligence - Fixed Asset Report Wizard'

    # Template domain override
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
    date_from = fields.Date(
        string='From Date',
        help='Filter assets/depreciation from this date'
    )
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
    # company_id inherited from ops.base.report.wizard

    branch_ids = fields.Many2many(
        'ops.branch',
        'asset_wizard_branch_rel',
        'wizard_id',
        'branch_id',
        string='Branches',
        help='Filter by specific branches. Leave empty for all.'
    )

    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'asset_wizard_bu_rel',
        'wizard_id',
        'bu_id',
        string='Business Units',
        help='Filter by specific business units. Leave empty for all.'
    )

    # ============================================
    # 4. ASSET FILTERS
    # ============================================
    asset_category_ids = fields.Many2many(
        'ops.asset.category',
        'asset_wizard_category_rel',
        'wizard_id',
        'category_id',
        string='Asset Categories',
        help='Filter by specific asset categories'
    )

    asset_state = fields.Selection([
        ('all', 'All Statuses'),
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('closed', 'Closed (Sold/Disposed)'),
    ], string='Asset Status', default='all',
       help='Filter by asset status')

    include_fully_depreciated = fields.Boolean(
        string='Include Fully Depreciated',
        default=True,
        help='Include assets that are fully depreciated'
    )

    # ============================================
    # 5. DEPRECIATION FILTERS
    # ============================================
    depreciation_state = fields.Selection([
        ('all', 'All'),
        ('draft', 'Pending Only'),
        ('posted', 'Posted Only'),
    ], string='Depreciation Status', default='all',
       help='Filter depreciation lines by status')

    # ============================================
    # 6. OUTPUT OPTIONS
    # ============================================
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('category', 'By Category'),
        ('branch', 'By Branch'),
        ('bu', 'By Business Unit'),
        ('state', 'By Status'),
    ], string='Group By', default='category')

    show_depreciation_details = fields.Boolean(
        string='Show Depreciation Schedule',
        default=False,
        help='Include depreciation line details in register'
    )

    # ============================================
    # 7. COMPUTED FIELDS
    # ============================================
    # report_title, filter_summary, record_count, currency_id inherited from base

    asset_count = fields.Integer(
        compute='_compute_totals',
        string='Asset Count'
    )

    total_gross_value = fields.Monetary(
        compute='_compute_totals',
        string='Total Gross Value',
        currency_field='currency_id'
    )

    total_nbv = fields.Monetary(
        compute='_compute_totals',
        string='Total Net Book Value',
        currency_field='currency_id'
    )

    # ============================================
    # BASE CLASS HOOK IMPLEMENTATIONS
    # ============================================

    def _get_engine_name(self):
        """Return engine name for template filtering."""
        return 'asset'

    def _get_report_titles(self):
        """Return mapping of report_type to human-readable title."""
        return {
            'register': 'Fixed Asset Register',
            'forecast': 'Depreciation Forecast',
            'disposal': 'Asset Disposal Analysis',
            'movement': 'Asset Movement Report',
        }

    def _get_scalar_fields_for_template(self):
        """Return scalar fields for template save/load."""
        return [
            'report_type', 'asset_state', 'depreciation_state', 'group_by',
            'include_fully_depreciated', 'show_depreciation_details',
        ]

    def _get_m2m_fields_for_template(self):
        """Return Many2many fields for template save/load."""
        return ['branch_ids', 'business_unit_ids', 'asset_category_ids']

    def _get_report_template_xmlid(self):
        """Return XML ID of report template based on report_type."""
        self.ensure_one()

        template_mapping = {
            'register': 'ops_matrix_accounting.report_asset_register',
            'depreciation': 'ops_matrix_accounting.report_depreciation_schedule',
            'disposal': 'ops_matrix_accounting.report_asset_disposal',
        }

        return template_mapping.get(self.report_type, 'ops_matrix_accounting.report_asset_register')

    def _add_filter_summary_parts(self, parts):
        """Add asset-specific filter descriptions."""
        # Handle date display based on report type
        if self.report_type == 'register' and self.date_to:
            # Replace generic date with as_of
            parts[:] = [p for p in parts if not p.startswith('Period:')]
            parts.append(f"As of: {self.date_to}")

        if self.branch_ids:
            parts.append(f"Branches: {len(self.branch_ids)} selected")

        if self.business_unit_ids:
            parts.append(f"BUs: {len(self.business_unit_ids)} selected")

        if self.asset_category_ids:
            parts.append(f"Categories: {len(self.asset_category_ids)} selected")

        if self.asset_state != 'all':
            parts.append(f"Status: {dict(self._fields['asset_state'].selection).get(self.asset_state)}")

    def _estimate_record_count(self):
        """Estimate number of assets matching filters."""
        domain = self._build_asset_domain()
        return self.env['ops.asset'].search_count(domain)

    @api.depends('branch_ids', 'business_unit_ids', 'asset_category_ids',
                 'asset_state', 'include_fully_depreciated')
    def _compute_totals(self):
        """Calculate totals for matching assets."""
        for wizard in self:
            try:
                domain = wizard._build_asset_domain()
                assets = self.env['ops.asset'].search(domain)
                wizard.asset_count = len(assets)
                wizard.total_gross_value = sum(assets.mapped('purchase_value'))
                wizard.total_nbv = sum(assets.mapped('book_value'))
            except Exception as e:
                _logger.error(f"Error calculating asset totals: {e}")
                wizard.asset_count = 0
                wizard.total_gross_value = 0.0
                wizard.total_nbv = 0.0

    # ============================================
    # DOMAIN BUILDING
    # ============================================

    def _build_asset_domain(self):
        """Build domain for asset query."""
        self.ensure_one()
        domain = [('company_id', '=', self.company_id.id)]

        # Branch filter
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))

        # Business Unit filter
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))

        # Category filter
        if self.asset_category_ids:
            domain.append(('category_id', 'in', self.asset_category_ids.ids))

        # State filter
        if self.asset_state == 'draft':
            domain.append(('state', '=', 'draft'))
        elif self.asset_state == 'running':
            domain.append(('state', '=', 'running'))
        elif self.asset_state == 'paused':
            domain.append(('state', '=', 'paused'))
        elif self.asset_state == 'closed':
            domain.append(('state', 'in', ['sold', 'disposed']))

        # Fully depreciated filter
        if not self.include_fully_depreciated:
            domain.append(('fully_depreciated', '=', False))

        # Date filter for purchase date (for register as of date)
        if self.report_type == 'register' and self.as_of_date:
            domain.append(('purchase_date', '<=', self.as_of_date))

        # Date filter for disposal analysis
        if self.report_type == 'disposal':
            if self.date_from:
                domain.append(('disposal_date', '>=', self.date_from))
            if self.date_to:
                domain.append(('disposal_date', '<=', self.date_to))

        # Movement report - assets added in period
        if self.report_type == 'movement':
            if self.date_from:
                domain.append(('purchase_date', '>=', self.date_from))
            if self.date_to:
                domain.append(('purchase_date', '<=', self.date_to))

        return domain

    def _build_depreciation_domain(self, asset_ids=None):
        """Build domain for depreciation line query."""
        self.ensure_one()
        domain = []

        if asset_ids:
            domain.append(('asset_id', 'in', asset_ids))

        # Date filter
        if self.date_from:
            domain.append(('depreciation_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('depreciation_date', '<=', self.date_to))

        # Depreciation state filter
        if self.depreciation_state == 'draft':
            domain.append(('state', '=', 'draft'))
        elif self.depreciation_state == 'posted':
            domain.append(('state', '=', 'posted'))

        return domain

    # ============================================
    # REPORT GENERATION
    # ============================================
    # _validate_filters and action_generate_report inherited from base

    def _get_report_data(self):
        """Get report data based on report_type."""
        self.ensure_one()

        dispatch = {
            'register': self._get_register_data,
            'forecast': self._get_forecast_data,
            'disposal': self._get_disposal_data,
            'movement': self._get_movement_data,
        }

        handler = dispatch.get(self.report_type, self._get_register_data)
        return handler()

    # ============================================
    # ASSET REGISTER DATA
    # ============================================

    def _get_register_data(self):
        """Get Asset Register report data."""
        self.ensure_one()

        domain = self._build_asset_domain()
        assets = self.env['ops.asset'].search(domain, order='category_id, code')

        # Process assets
        asset_data = []
        for asset in assets:
            # Calculate accumulated depreciation as of date
            accum_dep = self._get_accumulated_depreciation_as_of(asset, self.as_of_date)
            nbv = asset.purchase_value - accum_dep

            asset_record = {
                'id': asset.id,
                'code': asset.code,
                'name': asset.name,
                'category_name': asset.category_id.name,
                'category_id': asset.category_id.id,
                'purchase_date': str(asset.purchase_date),
                'purchase_value': asset.purchase_value,
                'salvage_value': asset.salvage_value,
                'depreciable_value': asset.depreciable_value,
                'accumulated_depreciation': accum_dep,
                'book_value': nbv,
                'fully_depreciated': nbv <= asset.salvage_value,
                'branch_name': asset.ops_branch_id.name if asset.ops_branch_id else '',
                'branch_code': asset.ops_branch_id.code if asset.ops_branch_id else '',
                'bu_name': asset.ops_business_unit_id.name if asset.ops_business_unit_id else '',
                'state': asset.state,
                'state_label': dict(asset._fields['state'].selection).get(asset.state),
                'depreciation_method': asset.category_id.depreciation_method,
                'useful_life_years': asset.category_id.depreciation_duration,
            }

            # Include depreciation schedule if requested
            if self.show_depreciation_details:
                dep_lines = asset.depreciation_ids.filtered(
                    lambda l: l.depreciation_date <= self.as_of_date if self.as_of_date else True
                )
                asset_record['depreciation_lines'] = [
                    {
                        'date': str(line.depreciation_date),
                        'amount': line.amount,
                        'state': line.state,
                    }
                    for line in dep_lines.sorted('depreciation_date')
                ]

            asset_data.append(asset_record)

        # Group if requested
        grouped_data = {}
        if self.group_by != 'none':
            grouped_data = self._group_assets(asset_data)

        # Calculate totals
        total_gross = sum(a['purchase_value'] for a in asset_data)
        total_accum = sum(a['accumulated_depreciation'] for a in asset_data)
        total_nbv = sum(a['book_value'] for a in asset_data)

        return {
            'report_type': 'register',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'as_of_date': str(self.as_of_date) if self.as_of_date else str(fields.Date.today()),
            'filters': self._get_filter_dict(),
            'group_by': self.group_by,
            'data': asset_data,
            'grouped': grouped_data,
            'totals': {
                'asset_count': len(asset_data),
                'total_gross_value': total_gross,
                'total_accumulated_depreciation': total_accum,
                'total_net_book_value': total_nbv,
            },
        }

    def _get_accumulated_depreciation_as_of(self, asset, as_of_date):
        """Calculate accumulated depreciation as of a specific date."""
        if not as_of_date:
            return asset.accumulated_depreciation

        posted_lines = asset.depreciation_ids.filtered(
            lambda l: l.state == 'posted' and l.depreciation_date <= as_of_date
        )
        return sum(posted_lines.mapped('amount'))

    def _group_assets(self, asset_data):
        """Group assets by selected field."""
        grouped = {}
        group_field_map = {
            'category': ('category_name', 'category_id'),
            'branch': ('branch_name', 'branch_code'),
            'bu': ('bu_name', 'bu_name'),
            'state': ('state_label', 'state'),
        }

        field_name, key_field = group_field_map.get(self.group_by, ('category_name', 'category_id'))

        for asset in asset_data:
            key = asset.get(field_name, 'Unspecified') or 'Unspecified'
            if key not in grouped:
                grouped[key] = {
                    'name': key,
                    'assets': [],
                    'total_gross': 0,
                    'total_accum': 0,
                    'total_nbv': 0,
                    'count': 0,
                }
            grouped[key]['assets'].append(asset)
            grouped[key]['total_gross'] += asset['purchase_value']
            grouped[key]['total_accum'] += asset['accumulated_depreciation']
            grouped[key]['total_nbv'] += asset['book_value']
            grouped[key]['count'] += 1

        return list(grouped.values())

    # ============================================
    # DEPRECIATION FORECAST DATA
    # ============================================

    def _get_forecast_data(self):
        """Get Depreciation Forecast report data."""
        self.ensure_one()

        # Get assets
        asset_domain = self._build_asset_domain()
        assets = self.env['ops.asset'].search(asset_domain)

        # Get depreciation lines for these assets in date range
        dep_domain = self._build_depreciation_domain(assets.ids)
        dep_lines = self.env['ops.asset.depreciation'].search(dep_domain, order='depreciation_date, asset_id')

        # Process depreciation lines
        forecast_data = []
        monthly_totals = {}

        for line in dep_lines:
            asset = line.asset_id
            month_key = line.depreciation_date.strftime('%Y-%m')

            line_data = {
                'id': line.id,
                'asset_id': asset.id,
                'asset_code': asset.code,
                'asset_name': asset.name,
                'category_name': asset.category_id.name,
                'depreciation_date': str(line.depreciation_date),
                'month_key': month_key,
                'amount': line.amount,
                'state': line.state,
                'state_label': dict(line._fields['state'].selection).get(line.state),
                'branch_name': line.branch_id.name if line.branch_id else '',
                'bu_name': line.business_unit_id.name if line.business_unit_id else '',
            }
            forecast_data.append(line_data)

            # Aggregate by month
            if month_key not in monthly_totals:
                monthly_totals[month_key] = {
                    'month': month_key,
                    'posted': 0,
                    'pending': 0,
                    'total': 0,
                    'count': 0,
                }
            monthly_totals[month_key]['total'] += line.amount
            monthly_totals[month_key]['count'] += 1
            if line.state == 'posted':
                monthly_totals[month_key]['posted'] += line.amount
            else:
                monthly_totals[month_key]['pending'] += line.amount

        # Sort monthly totals
        sorted_months = sorted(monthly_totals.values(), key=lambda x: x['month'])

        # Calculate totals
        total_posted = sum(m['posted'] for m in sorted_months)
        total_pending = sum(m['pending'] for m in sorted_months)

        return {
            'report_type': 'forecast',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from) if self.date_from else None,
            'date_to': str(self.date_to) if self.date_to else None,
            'filters': self._get_filter_dict(),
            'data': forecast_data,
            'monthly_summary': sorted_months,
            'totals': {
                'line_count': len(forecast_data),
                'total_posted': total_posted,
                'total_pending': total_pending,
                'total_depreciation': total_posted + total_pending,
            },
        }

    # ============================================
    # DISPOSAL ANALYSIS DATA
    # ============================================

    def _get_disposal_data(self):
        """Get Asset Disposal Analysis report data."""
        self.ensure_one()

        # Get disposed/sold assets
        domain = self._build_asset_domain()
        domain.append(('state', 'in', ['sold', 'disposed']))

        assets = self.env['ops.asset'].search(domain, order='disposal_date desc, name')

        disposal_data = []
        for asset in assets:
            disposal_data.append({
                'id': asset.id,
                'code': asset.code,
                'name': asset.name,
                'category_name': asset.category_id.name,
                'purchase_date': str(asset.purchase_date),
                'disposal_date': str(asset.disposal_date) if asset.disposal_date else '',
                'purchase_value': asset.purchase_value,
                'accumulated_depreciation': asset.accumulated_depreciation,
                'book_value_at_disposal': asset.book_value,
                'state': asset.state,
                'state_label': dict(asset._fields['state'].selection).get(asset.state),
                'branch_name': asset.ops_branch_id.name if asset.ops_branch_id else '',
                'bu_name': asset.ops_business_unit_id.name if asset.ops_business_unit_id else '',
                'holding_period_days': (
                    (asset.disposal_date - asset.purchase_date).days
                    if asset.disposal_date and asset.purchase_date else 0
                ),
            })

        # Group by disposal type
        sold_assets = [a for a in disposal_data if a['state'] == 'sold']
        disposed_assets = [a for a in disposal_data if a['state'] == 'disposed']

        return {
            'report_type': 'disposal',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from) if self.date_from else None,
            'date_to': str(self.date_to) if self.date_to else None,
            'filters': self._get_filter_dict(),
            'data': disposal_data,
            'sold': {
                'data': sold_assets,
                'count': len(sold_assets),
                'total_gross': sum(a['purchase_value'] for a in sold_assets),
                'total_nbv': sum(a['book_value_at_disposal'] for a in sold_assets),
            },
            'disposed': {
                'data': disposed_assets,
                'count': len(disposed_assets),
                'total_gross': sum(a['purchase_value'] for a in disposed_assets),
                'total_nbv': sum(a['book_value_at_disposal'] for a in disposed_assets),
            },
            'totals': {
                'total_count': len(disposal_data),
                'total_gross_value': sum(a['purchase_value'] for a in disposal_data),
                'total_nbv_at_disposal': sum(a['book_value_at_disposal'] for a in disposal_data),
            },
        }

    # ============================================
    # ASSET MOVEMENT DATA
    # ============================================

    def _get_movement_data(self):
        """Get Asset Movement report data (additions in period)."""
        self.ensure_one()

        # Get assets added in period
        domain = self._build_asset_domain()
        assets = self.env['ops.asset'].search(domain, order='purchase_date, name')

        movement_data = []
        for asset in assets:
            movement_data.append({
                'id': asset.id,
                'code': asset.code,
                'name': asset.name,
                'category_name': asset.category_id.name,
                'purchase_date': str(asset.purchase_date),
                'purchase_value': asset.purchase_value,
                'salvage_value': asset.salvage_value,
                'depreciable_value': asset.depreciable_value,
                'state': asset.state,
                'state_label': dict(asset._fields['state'].selection).get(asset.state),
                'branch_name': asset.ops_branch_id.name if asset.ops_branch_id else '',
                'bu_name': asset.ops_business_unit_id.name if asset.ops_business_unit_id else '',
                'useful_life_years': asset.category_id.depreciation_duration,
            })

        # Group by category for summary
        category_summary = {}
        for asset in movement_data:
            cat = asset['category_name'] or 'Uncategorized'
            if cat not in category_summary:
                category_summary[cat] = {
                    'name': cat,
                    'count': 0,
                    'total_value': 0,
                }
            category_summary[cat]['count'] += 1
            category_summary[cat]['total_value'] += asset['purchase_value']

        return {
            'report_type': 'movement',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from) if self.date_from else None,
            'date_to': str(self.date_to) if self.date_to else None,
            'filters': self._get_filter_dict(),
            'data': movement_data,
            'category_summary': list(category_summary.values()),
            'totals': {
                'additions_count': len(movement_data),
                'total_additions_value': sum(a['purchase_value'] for a in movement_data),
            },
        }

    # ============================================
    # HELPER METHODS
    # ============================================

    def _get_filter_dict(self):
        """Get filter summary as dictionary."""
        return {
            'report_type': self.report_type,
            'date_from': str(self.date_from) if self.date_from else None,
            'date_to': str(self.date_to) if self.date_to else None,
            'as_of_date': str(self.as_of_date) if self.as_of_date else None,
            'branch_count': len(self.branch_ids),
            'branch_names': self.branch_ids.mapped('name') if self.branch_ids else [],
            'bu_count': len(self.business_unit_ids),
            'bu_names': self.business_unit_ids.mapped('name') if self.business_unit_ids else [],
            'category_count': len(self.asset_category_ids),
            'category_names': self.asset_category_ids.mapped('name') if self.asset_category_ids else [],
            'asset_state': self.asset_state,
            'include_fully_depreciated': self.include_fully_depreciated,
            'depreciation_state': self.depreciation_state,
            'group_by': self.group_by,
        }

    def _return_report_action(self, data):
        """Return appropriate report action."""
        report_names = {
            'register': 'ops_matrix_accounting.report_asset_register',
            'forecast': 'ops_matrix_accounting.report_asset_forecast',
            'disposal': 'ops_matrix_accounting.report_asset_disposal',
            'movement': 'ops_matrix_accounting.report_asset_movement',
        }

        return {
            'type': 'ir.actions.report',
            'report_name': report_names.get(self.report_type, report_names['register']),
            'report_type': 'qweb-pdf',
            'data': data,
            'config': False,
        }

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_assets(self):
        """Open filtered assets in list view."""
        self.ensure_one()

        domain = self._build_asset_domain()

        return {
            'name': _('Fixed Assets'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.asset',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'search_default_group_by_category': 1},
        }

    def action_view_depreciation(self):
        """Open depreciation lines in list view."""
        self.ensure_one()

        asset_domain = self._build_asset_domain()
        assets = self.env['ops.asset'].search(asset_domain)
        dep_domain = self._build_depreciation_domain(assets.ids)

        return {
            'name': _('Depreciation Schedule'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.asset.depreciation',
            'view_mode': 'list,form',
            'domain': dep_domain,
            'context': {'search_default_group_by_month': 1},
        }

    def action_export_excel(self):
        """
        Export Asset Intelligence report to Excel.

        Uses Phase 5 corporate Excel format structure.
        Generates file directly using xlsxwriter (no report_xlsx dependency).
        """
        self.ensure_one()

        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter Python library is not installed. Cannot generate Excel reports."))

        import io
        import base64

        # Get report data
        report_data = self._get_report_data()

        # Create in-memory Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        try:
            # Generate Excel report using the XLSX report generator
            xlsx_report = self.env['report.ops_matrix_accounting.report_asset_xlsx']
            xlsx_report.generate_xlsx_report(workbook, report_data, self)
        finally:
            workbook.close()

        # Get file content
        output.seek(0)
        file_content = output.read()
        output.close()

        # Encode to base64
        file_content_b64 = base64.b64encode(file_content)

        # Generate filename
        report_type_labels = {
            'register': 'Asset_Register',
            'forecast': 'Depreciation_Forecast',
            'disposal': 'Disposal_Analysis',
            'movement': 'Asset_Movement',
        }
        report_label = report_type_labels.get(self.report_type, 'Asset_Report')
        filename = f"OPS_{report_label}_{fields.Date.today().strftime('%Y%m%d')}.xlsx"

        # Create attachment and return download action
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': file_content_b64,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    # ============================================
    # ONCHANGE METHODS
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Adjust options based on report type."""
        if self.report_type == 'disposal':
            # Disposal analysis focuses on closed assets
            self.asset_state = 'closed'
        elif self.report_type == 'forecast':
            # Forecast focuses on running assets
            self.asset_state = 'running'
            self.depreciation_state = 'draft'
        else:
            self.asset_state = 'all'

    @api.onchange('branch_ids')
    def _onchange_branch_ids(self):
        """Update BU domain when branches change."""
        if self.branch_ids:
            return {
                'domain': {
                    'business_unit_ids': [('branch_ids', 'in', self.branch_ids.ids)]
                }
            }
        return {}

    # ============================================
    # SMART TEMPLATE METHODS
    # ============================================
    # _onchange_report_template_id, _get_template_config, action_save_template
    # are inherited from ops.base.report.wizard
