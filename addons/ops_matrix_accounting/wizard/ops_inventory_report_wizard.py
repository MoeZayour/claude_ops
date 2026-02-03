# -*- coding: utf-8 -*-
"""
OPS Matrix Inventory Intelligence Engine
========================================

Comprehensive inventory analysis and reporting wizard.
Provides stock valuation, aging analysis, negative stock alerts,
and fast/slow moving item identification.

Reports Supported:
- Stock Valuation: Inventory value by branch and location
- Inventory Aging: Dead stock analysis with age buckets
- Negative Stock: Alerts for stock discrepancies
- Movement Analysis: Fast vs slow moving items

Author: OPS Matrix Framework
Version: 1.0 (Phase 10 - Inventory Intelligence)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

# Corporate Excel formatting (Phase 5)
from ..report.excel_styles import get_corporate_excel_formats


class OpsInventoryReportWizard(models.TransientModel):
    """Inventory Intelligence - Stock Analysis Engine"""
    _name = 'ops.inventory.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Inventory Intelligence Report Wizard'

    # Template domain override
    report_template_id = fields.Many2one(
        domain="[('engine', '=', 'inventory'), '|', ('is_global', '=', True), ('user_id', '=', uid)]"
    )

    # ============================================
    # 1. REPORT TYPE SELECTOR
    # ============================================
    report_type = fields.Selection([
        ('valuation', 'Stock Valuation by Branch'),
        ('aging', 'Inventory Aging (Dead Stock)'),
        ('negative', 'Negative Stock Alert'),
        ('movement', 'Fast vs Slow Moving'),
    ], string='Report Type', required=True, default='valuation',
       help='Select the type of inventory report to generate')

    # ============================================
    # 2. DATE FILTERS
    # ============================================
    date_to = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        help='Reference date for inventory analysis'
    )

    date_from = fields.Date(
        string='From Date',
        help='Start date for movement analysis'
    )

    # ============================================
    # 3. DIMENSION FILTERS
    # ============================================
    # company_id inherited from ops.base.report.wizard

    ops_branch_ids = fields.Many2many(
        'ops.branch',
        'inventory_wizard_branch_rel',
        'wizard_id',
        'branch_id',
        string='Branches',
        help='Filter by specific branches. Leave empty for all.'
    )

    location_ids = fields.Many2many(
        'stock.location',
        'inventory_wizard_location_rel',
        'wizard_id',
        'location_id',
        string='Locations',
        domain="[('usage', '=', 'internal')]",
        help='Filter by specific stock locations. Leave empty for all internal locations.'
    )

    product_category_ids = fields.Many2many(
        'product.category',
        'inventory_wizard_category_rel',
        'wizard_id',
        'category_id',
        string='Product Categories',
        help='Filter by product categories. Leave empty for all.'
    )

    product_ids = fields.Many2many(
        'product.product',
        'inventory_wizard_product_rel',
        'wizard_id',
        'product_id',
        string='Products',
        domain="[('type', '=', 'product')]",
        help='Filter by specific products. Leave empty for all storable products.'
    )

    # ============================================
    # 4. AGING ANALYSIS OPTIONS
    # ============================================
    aging_period_1 = fields.Integer(
        string='Period 1 (days)',
        default=30,
        help='First aging period threshold in days'
    )

    aging_period_2 = fields.Integer(
        string='Period 2 (days)',
        default=60,
        help='Second aging period threshold in days'
    )

    aging_period_3 = fields.Integer(
        string='Period 3 (days)',
        default=90,
        help='Third aging period threshold in days'
    )

    aging_period_4 = fields.Integer(
        string='Period 4 (days)',
        default=180,
        help='Fourth aging period threshold in days (older = dead stock)'
    )

    min_age_days = fields.Integer(
        string='Minimum Age (days)',
        default=0,
        help='Only show items older than this many days'
    )

    # ============================================
    # 5. MOVEMENT ANALYSIS OPTIONS
    # ============================================
    movement_period = fields.Integer(
        string='Movement Period (days)',
        default=90,
        help='Number of days to analyze for movement classification'
    )

    slow_threshold = fields.Integer(
        string='Slow Moving Threshold',
        default=5,
        help='Items with fewer moves than this are considered slow moving'
    )

    # ============================================
    # 6. OUTPUT OPTIONS
    # ============================================
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('branch', 'By Branch'),
        ('location', 'By Location'),
        ('category', 'By Category'),
        ('product', 'By Product'),
    ], string='Group By', default='branch')

    include_zero_qty = fields.Boolean(
        string='Include Zero Quantity',
        default=False,
        help='Include items with zero stock'
    )

    # ============================================
    # 7. COMPUTED FIELDS
    # ============================================
    # report_title, filter_summary, record_count, currency_id inherited from base

    total_value = fields.Monetary(
        compute='_compute_totals',
        string='Total Value',
        currency_field='currency_id'
    )

    total_quantity = fields.Float(
        compute='_compute_totals',
        string='Total Quantity'
    )

    # ============================================
    # BASE CLASS HOOK IMPLEMENTATIONS
    # ============================================

    def _get_engine_name(self):
        """Return engine name for template filtering."""
        return 'inventory'

    def _get_report_titles(self):
        """Return mapping of report_type to human-readable title."""
        return {
            'valuation': 'Stock Valuation Report',
            'aging': 'Inventory Aging Analysis',
            'negative': 'Negative Stock Alert',
            'movement': 'Fast vs Slow Moving Analysis',
        }

    def _get_scalar_fields_for_template(self):
        """Return scalar fields for template save/load."""
        return [
            'report_type', 'group_by', 'include_zero_qty',
            'aging_period_1', 'aging_period_2', 'aging_period_3', 'aging_period_4',
            'min_age_days', 'movement_period', 'slow_threshold',
        ]

    def _get_m2m_fields_for_template(self):
        """Return Many2many fields for template save/load."""
        return ['ops_branch_ids', 'location_ids', 'product_category_ids']

    def _get_report_template_xmlid(self):
        """Return XML ID of report template based on report_type."""
        self.ensure_one()

        template_mapping = {
            'valuation': 'ops_matrix_accounting.report_stock_valuation',
            'aging': 'ops_matrix_accounting.report_inventory_aging',
            'movement': 'ops_matrix_accounting.report_inventory_movement',
            'negative': 'ops_matrix_accounting.report_negative_stock',
        }

        return template_mapping.get(self.report_type, 'ops_matrix_accounting.report_stock_valuation')

    def _add_filter_summary_parts(self, parts):
        """Add inventory-specific filter descriptions."""
        # Replace generic date with as_of for inventory
        parts[:] = [p for p in parts if not p.startswith('Period:')]
        parts.append(f"As of: {self.date_to}")

        if self.ops_branch_ids:
            parts.append(f"Branches: {len(self.ops_branch_ids)} selected")

        if self.location_ids:
            parts.append(f"Locations: {len(self.location_ids)} selected")

        if self.product_category_ids:
            parts.append(f"Categories: {len(self.product_category_ids)} selected")

    def _estimate_record_count(self):
        """Estimate number of quants matching filters."""
        domain = self._build_quant_domain()
        return self.env['stock.quant'].search_count(domain)

    @api.depends('ops_branch_ids', 'location_ids', 'product_category_ids', 'include_zero_qty')
    def _compute_totals(self):
        """Calculate total quantity and value of matching stock."""
        for wizard in self:
            try:
                domain = wizard._build_quant_domain()
                quants = self.env['stock.quant'].search(domain)
                wizard.total_quantity = sum(quants.mapped('quantity'))
                wizard.total_value = sum(quants.mapped('value'))
            except Exception as e:
                _logger.error(f"Error calculating totals: {e}")
                wizard.total_quantity = 0.0
                wizard.total_value = 0.0

    # ============================================
    # DOMAIN BUILDING
    # ============================================

    def _build_quant_domain(self):
        """Build domain for stock.quant query."""
        self.ensure_one()
        domain = [('location_id.usage', '=', 'internal')]

        # Company filter
        domain.append(('company_id', '=', self.company_id.id))

        # Location filter
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))

        # Product category filter
        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))

        # Product filter
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))

        # Zero quantity filter
        if not self.include_zero_qty:
            domain.append(('quantity', '!=', 0))

        # For negative stock report
        if self.report_type == 'negative':
            domain.append(('quantity', '<', 0))

        return domain

    def _get_branch_locations(self):
        """Get location IDs associated with selected branches."""
        self.ensure_one()
        if not self.ops_branch_ids:
            return []

        # Get warehouses linked to branches via branch.warehouse_id
        warehouse_ids = self.ops_branch_ids.mapped('warehouse_id').ids

        if not warehouse_ids:
            return []

        warehouses = self.env['stock.warehouse'].browse(warehouse_ids)

        # Get all internal locations under these warehouses
        location_ids = []
        for wh in warehouses:
            if wh.lot_stock_id:
                locations = self.env['stock.location'].search([
                    ('id', 'child_of', wh.lot_stock_id.id),
                    ('usage', '=', 'internal')
                ])
                location_ids.extend(locations.ids)

        return location_ids

    # ============================================
    # VALIDATION
    # ============================================

    def _validate_filters_extra(self):
        """Perform inventory-specific validation."""
        if self.report_type == 'movement' and not self.date_from:
            self.date_from = self.date_to - timedelta(days=self.movement_period)
        return True

    # ============================================
    # REPORT GENERATION
    # ============================================
    # action_generate_report inherited from base

    def _get_report_data(self):
        """Get report data based on report_type."""
        self.ensure_one()

        dispatch = {
            'valuation': self._get_valuation_data,
            'aging': self._get_aging_data,
            'negative': self._get_negative_data,
            'movement': self._get_movement_data,
        }

        handler = dispatch.get(self.report_type, self._get_valuation_data)
        return handler()

    # ============================================
    # STOCK VALUATION DATA
    # ============================================

    def _get_valuation_data(self):
        """Get Stock Valuation report data."""
        self.ensure_one()

        domain = self._build_quant_domain()

        # Handle branch filter through locations
        if self.ops_branch_ids:
            branch_locations = self._get_branch_locations()
            if branch_locations:
                domain.append(('location_id', 'in', branch_locations))

        quants = self.env['stock.quant'].search(domain)

        # Process and group data
        data = self._process_quants(quants)
        grouped_data = self._group_data(data, self.group_by)

        # Calculate totals
        total_qty = sum(d['quantity'] for d in data)
        total_value = sum(d['value'] for d in data)

        return {
            'report_type': 'valuation',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_to': str(self.date_to),
            'filters': self._get_filter_dict(),
            'data': data,
            'grouped_data': grouped_data,
            'totals': {
                'total_quantity': total_qty,
                'total_value': total_value,
                'item_count': len(data),
            },
        }

    def _process_quants(self, quants):
        """Process quants into report format."""
        data = []
        for quant in quants:
            # Get branch info - check warehouse relationship
            branch_name = ''
            branch_id = 0
            if quant.location_id.warehouse_id:
                # Check if branch is linked via ops.branch.warehouse_id (reverse lookup)
                branch = self.env['ops.branch'].search([
                    ('warehouse_id', '=', quant.location_id.warehouse_id.id)
                ], limit=1)
                if branch:
                    branch_name = branch.name
                    branch_id = branch.id

            data.append({
                'id': quant.id,
                'product_id': quant.product_id.id,
                'product_name': quant.product_id.display_name,
                'product_code': quant.product_id.default_code or '',
                'category_name': quant.product_id.categ_id.name,
                'category_id': quant.product_id.categ_id.id,
                'location_id': quant.location_id.id,
                'location_name': quant.location_id.complete_name,
                'branch_name': branch_name,
                'branch_id': branch_id,
                'quantity': quant.quantity,
                'reserved_quantity': quant.reserved_quantity,
                'available_quantity': quant.quantity - quant.reserved_quantity,
                'uom': quant.product_uom_id.name,
                'value': quant.value,
                'unit_cost': quant.value / quant.quantity if quant.quantity else 0,
                'in_date': str(quant.in_date) if quant.in_date else '',
                'lot_name': quant.lot_id.name if quant.lot_id else '',
            })
        return data

    def _build_empty_movement_result(self, date_from, date_to):
        """Return empty movement result structure."""
        return {
            'report_type': 'movement',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(date_from),
            'date_to': str(date_to),
            'movement_period': self.movement_period,
            'slow_threshold': self.slow_threshold,
            'filters': self._get_filter_dict(),
            'data': [],
            'movement_summary': [
                {'label': 'No Movement', 'count': 0, 'qty': 0, 'value': 0},
                {'label': 'Slow Moving', 'count': 0, 'qty': 0, 'value': 0},
                {'label': 'Fast Moving', 'count': 0, 'qty': 0, 'value': 0},
            ],
            'totals': {
                'total_products': 0,
                'total_qty': 0,
                'total_value': 0,
                'dead_count': 0,
                'slow_count': 0,
                'fast_count': 0,
            },
        }

    def _group_data(self, data, group_by):
        """Group data by specified field."""
        if group_by == 'none':
            return {'All': {'items': data, 'total_qty': sum(d['quantity'] for d in data), 'total_value': sum(d['value'] for d in data)}}

        field_map = {
            'branch': ('branch_name', 'branch_id'),
            'location': ('location_name', 'location_id'),
            'category': ('category_name', 'category_id'),
            'product': ('product_name', 'product_id'),
        }

        name_field, id_field = field_map.get(group_by, ('branch_name', 'branch_id'))

        grouped = {}
        for item in data:
            key = item.get(name_field) or 'Unassigned'
            if key not in grouped:
                grouped[key] = {
                    'name': key,
                    'id': item.get(id_field),
                    'items': [],
                    'total_qty': 0,
                    'total_value': 0,
                }
            grouped[key]['items'].append(item)
            grouped[key]['total_qty'] += item['quantity']
            grouped[key]['total_value'] += item['value']

        return grouped

    # ============================================
    # INVENTORY AGING DATA
    # ============================================

    def _get_aging_data(self):
        """Get Inventory Aging (Dead Stock) report data."""
        self.ensure_one()

        today = self.date_to
        domain = self._build_quant_domain()

        # Handle branch filter
        if self.ops_branch_ids:
            branch_locations = self._get_branch_locations()
            if branch_locations:
                domain.append(('location_id', 'in', branch_locations))

        # Only include items with in_date
        domain.append(('in_date', '!=', False))

        # Apply minimum age filter
        if self.min_age_days > 0:
            max_date = today - timedelta(days=self.min_age_days)
            domain.append(('in_date', '<=', max_date))

        quants = self.env['stock.quant'].search(domain)

        # Initialize aging buckets
        p1, p2, p3, p4 = self.aging_period_1, self.aging_period_2, self.aging_period_3, self.aging_period_4
        aging_buckets = {
            f'0-{p1}': {'label': f'Fresh (0-{p1} days)', 'items': [], 'total_qty': 0, 'total_value': 0},
            f'{p1+1}-{p2}': {'label': f'Normal ({p1+1}-{p2} days)', 'items': [], 'total_qty': 0, 'total_value': 0},
            f'{p2+1}-{p3}': {'label': f'Aging ({p2+1}-{p3} days)', 'items': [], 'total_qty': 0, 'total_value': 0},
            f'{p3+1}-{p4}': {'label': f'Old ({p3+1}-{p4} days)', 'items': [], 'total_qty': 0, 'total_value': 0},
            f'>{p4}': {'label': f'Dead Stock (>{p4} days)', 'items': [], 'total_qty': 0, 'total_value': 0},
        }

        # Classify each quant
        all_items = []
        for quant in quants:
            if not quant.in_date:
                continue

            # Calculate age in days
            in_date = quant.in_date.date() if hasattr(quant.in_date, 'date') else quant.in_date
            age_days = (today - in_date).days

            # Get branch info
            branch_name = ''
            if quant.location_id.warehouse_id:
                branch = self.env['ops.branch'].search([
                    ('warehouse_id', '=', quant.location_id.warehouse_id.id)
                ], limit=1)
                if branch:
                    branch_name = branch.name

            item = {
                'id': quant.id,
                'product_id': quant.product_id.id,
                'product_name': quant.product_id.display_name,
                'product_code': quant.product_id.default_code or '',
                'category_name': quant.product_id.categ_id.name,
                'location_name': quant.location_id.complete_name,
                'branch_name': branch_name,
                'quantity': quant.quantity,
                'value': quant.value,
                'in_date': str(quant.in_date),
                'age_days': age_days,
                'lot_name': quant.lot_id.name if quant.lot_id else '',
            }

            all_items.append(item)

            # Classify into bucket
            if age_days <= p1:
                bucket_key = f'0-{p1}'
            elif age_days <= p2:
                bucket_key = f'{p1+1}-{p2}'
            elif age_days <= p3:
                bucket_key = f'{p2+1}-{p3}'
            elif age_days <= p4:
                bucket_key = f'{p3+1}-{p4}'
            else:
                bucket_key = f'>{p4}'

            aging_buckets[bucket_key]['items'].append(item)
            aging_buckets[bucket_key]['total_qty'] += quant.quantity
            aging_buckets[bucket_key]['total_value'] += quant.value

        return {
            'report_type': 'aging',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_to': str(self.date_to),
            'filters': self._get_filter_dict(),
            'aging_periods': {
                'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4
            },
            'aging_buckets': list(aging_buckets.values()),
            'all_items': all_items,
            'totals': {
                'total_quantity': sum(i['quantity'] for i in all_items),
                'total_value': sum(i['value'] for i in all_items),
                'item_count': len(all_items),
                'dead_stock_qty': aging_buckets[f'>{p4}']['total_qty'],
                'dead_stock_value': aging_buckets[f'>{p4}']['total_value'],
            },
        }

    # ============================================
    # NEGATIVE STOCK DATA
    # ============================================

    def _get_negative_data(self):
        """Get Negative Stock Alert report data."""
        self.ensure_one()

        domain = self._build_quant_domain()  # Already includes quantity < 0 for negative report

        # Handle branch filter
        if self.ops_branch_ids:
            branch_locations = self._get_branch_locations()
            if branch_locations:
                domain.append(('location_id', 'in', branch_locations))

        quants = self.env['stock.quant'].search(domain)

        data = []
        for quant in quants:
            # Get branch info
            branch_name = ''
            if quant.location_id.warehouse_id:
                branch = self.env['ops.branch'].search([
                    ('warehouse_id', '=', quant.location_id.warehouse_id.id)
                ], limit=1)
                if branch:
                    branch_name = branch.name

            data.append({
                'id': quant.id,
                'product_id': quant.product_id.id,
                'product_name': quant.product_id.display_name,
                'product_code': quant.product_id.default_code or '',
                'category_name': quant.product_id.categ_id.name,
                'location_id': quant.location_id.id,
                'location_name': quant.location_id.complete_name,
                'branch_name': branch_name,
                'quantity': quant.quantity,
                'reserved_quantity': quant.reserved_quantity,
                'value': quant.value,
                'severity': 'critical' if quant.quantity < -10 else 'warning',
            })

        # Sort by severity (most negative first)
        data.sort(key=lambda x: x['quantity'])

        grouped_data = self._group_data(data, self.group_by)

        return {
            'report_type': 'negative',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_to': str(self.date_to),
            'filters': self._get_filter_dict(),
            'data': data,
            'grouped_data': grouped_data,
            'totals': {
                'total_negative_qty': sum(d['quantity'] for d in data),
                'total_negative_value': sum(d['value'] for d in data),
                'alert_count': len(data),
                'critical_count': len([d for d in data if d['severity'] == 'critical']),
            },
        }

    # ============================================
    # MOVEMENT ANALYSIS DATA
    # ============================================

    def _get_movement_data(self):
        """Get Fast vs Slow Moving analysis report data.

        OPTIMIZED: Uses _read_group for O(1) queries instead of N+1 pattern.
        """
        self.ensure_one()

        # Set date range
        date_to = self.date_to
        date_from = self.date_from or (date_to - timedelta(days=self.movement_period))

        domain = self._build_quant_domain()

        # Handle branch filter
        if self.ops_branch_ids:
            branch_locations = self._get_branch_locations()
            if branch_locations:
                domain.append(('location_id', 'in', branch_locations))

        quants = self.env['stock.quant'].search(domain)

        # Get unique products
        products = quants.mapped('product_id')
        product_ids = products.ids

        if not product_ids:
            return self._build_empty_movement_result(date_from, date_to)

        # =================================================================
        # OPTIMIZED: Single grouped query for ALL product movements
        # Instead of N queries (one per product), we do 1 aggregated query
        # =================================================================
        move_data = self.env['stock.move']._read_group(
            domain=[
                ('product_id', 'in', product_ids),
                ('state', '=', 'done'),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ],
            groupby=['product_id'],
            aggregates=['id:count', 'quantity:sum']
        )

        # Build O(1) lookup dictionary: {product_id: {'count': N, 'qty': X}}
        movement_map = {}
        for product, count, qty_sum in move_data:
            if product:
                movement_map[product.id] = {
                    'count': count or 0,
                    'qty': qty_sum or 0.0
                }

        # =================================================================
        # OPTIMIZED: Single pass aggregation for quants by product
        # =================================================================
        quant_map = {}
        for quant in quants:
            pid = quant.product_id.id
            if pid not in quant_map:
                quant_map[pid] = {'qty': 0.0, 'value': 0.0}
            quant_map[pid]['qty'] += quant.quantity
            quant_map[pid]['value'] += quant.value

        # Build result data using lookup maps (no additional queries)
        data = []
        for product in products:
            # Get movement info from pre-computed map
            move_info = movement_map.get(product.id, {'count': 0, 'qty': 0.0})
            move_count = move_info['count']
            total_qty_moved = move_info['qty']

            # Get current stock from pre-computed map
            stock_info = quant_map.get(product.id, {'qty': 0.0, 'value': 0.0})
            current_qty = stock_info['qty']
            current_value = stock_info['value']

            # Classify movement
            if move_count == 0:
                movement_class = 'dead'
                movement_label = 'No Movement'
            elif move_count < self.slow_threshold:
                movement_class = 'slow'
                movement_label = 'Slow Moving'
            else:
                movement_class = 'fast'
                movement_label = 'Fast Moving'

            data.append({
                'product_id': product.id,
                'product_name': product.display_name,
                'product_code': product.default_code or '',
                'category_name': product.categ_id.name,
                'current_qty': current_qty,
                'current_value': current_value,
                'move_count': move_count,
                'qty_moved': total_qty_moved,
                'movement_class': movement_class,
                'movement_label': movement_label,
                'turnover_ratio': total_qty_moved / current_qty if current_qty > 0 else 0,
            })

        # Sort by movement class (dead first, then slow, then fast)
        movement_order = {'dead': 0, 'slow': 1, 'fast': 2}
        data.sort(key=lambda x: (movement_order.get(x['movement_class'], 3), -x['current_value']))

        # Group by movement class
        movement_summary = {
            'dead': {'label': 'No Movement', 'count': 0, 'qty': 0, 'value': 0},
            'slow': {'label': 'Slow Moving', 'count': 0, 'qty': 0, 'value': 0},
            'fast': {'label': 'Fast Moving', 'count': 0, 'qty': 0, 'value': 0},
        }
        for item in data:
            cls = item['movement_class']
            movement_summary[cls]['count'] += 1
            movement_summary[cls]['qty'] += item['current_qty']
            movement_summary[cls]['value'] += item['current_value']

        return {
            'report_type': 'movement',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(date_from),
            'date_to': str(date_to),
            'movement_period': self.movement_period,
            'slow_threshold': self.slow_threshold,
            'filters': self._get_filter_dict(),
            'data': data,
            'movement_summary': list(movement_summary.values()),
            'totals': {
                'total_products': len(data),
                'total_qty': sum(d['current_qty'] for d in data),
                'total_value': sum(d['current_value'] for d in data),
                'dead_count': movement_summary['dead']['count'],
                'slow_count': movement_summary['slow']['count'],
                'fast_count': movement_summary['fast']['count'],
            },
        }

    # ============================================
    # HELPER METHODS
    # ============================================

    def _get_filter_dict(self):
        """Get filter summary as dictionary."""
        return {
            'report_type': self.report_type,
            'date_to': str(self.date_to),
            'date_from': str(self.date_from) if self.date_from else None,
            'branch_count': len(self.ops_branch_ids),
            'branch_names': self.ops_branch_ids.mapped('name') if self.ops_branch_ids else [],
            'location_count': len(self.location_ids),
            'category_count': len(self.product_category_ids),
            'include_zero_qty': self.include_zero_qty,
            'group_by': self.group_by,
        }

    def _return_report_action(self, data):
        """Return appropriate report action for PDF generation."""
        report_names = {
            'valuation': 'ops_matrix_accounting.report_inventory_valuation_pdf',
            'aging': 'ops_matrix_accounting.report_inventory_aging_pdf',
            'negative': 'ops_matrix_accounting.report_inventory_negative_pdf',
            'movement': 'ops_matrix_accounting.report_inventory_movement_pdf',
        }

        report_name = report_names.get(self.report_type, report_names['valuation'])

        return self.env.ref(report_name).report_action(self)

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_quants(self):
        """Open filtered stock quants in list view."""
        self.ensure_one()

        domain = self._build_quant_domain()
        if self.ops_branch_ids:
            branch_locations = self._get_branch_locations()
            if branch_locations:
                domain.append(('location_id', 'in', branch_locations))

        return {
            'name': _('Stock Quants'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'search_default_internal_loc': 1},
        }

    def action_export_excel(self):
        """Export report to Excel with professional OPS formatting."""
        self.ensure_one()

        # Security check
        self._check_intelligence_access('Inventory')

        # Validate branch access
        if self.ops_branch_ids:
            self._validate_branch_access(self.ops_branch_ids)

        # Get report data
        report_data = self._get_report_data()

        # Generate Excel file
        try:
            import xlsxwriter
            from io import BytesIO
            import base64

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})

            # Create formats - OPS Corporate Style (Phase 5)
            formats = get_corporate_excel_formats(workbook, self.company_id)

            # Dispatch to appropriate Excel writer
            if self.report_type == 'valuation':
                self._write_valuation_excel(workbook, formats, report_data)
            elif self.report_type == 'aging':
                self._write_aging_excel(workbook, formats, report_data)
            elif self.report_type == 'negative':
                self._write_negative_excel(workbook, formats, report_data)
            elif self.report_type == 'movement':
                self._write_movement_excel(workbook, formats, report_data)

            workbook.close()
            output.seek(0)

            # Create attachment and return download action
            date_str = self.date_to.strftime('%Y%m%d') if self.date_to else fields.Date.today().strftime('%Y%m%d')
            filename = f"Inventory_{self.report_type}_{date_str}.xlsx"

            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(output.read()),
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            })

            # Log export
            self._log_intelligence_report('Inventory', self.report_type, {
                'record_count': len(report_data.get('data', [])),
                'date_to': str(self.date_to),
            }, 'excel')

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        except ImportError:
            raise UserError(_('xlsxwriter library is not installed. Please install it to export to Excel.'))

    def _write_valuation_excel(self, workbook, formats, data):
        """Write Stock Valuation report to Excel."""
        sheet = workbook.add_worksheet('Stock Valuation')

        # Column widths
        sheet.set_column(0, 0, 40)  # Product
        sheet.set_column(1, 1, 35)  # Location
        sheet.set_column(2, 2, 20)  # Category
        sheet.set_column(3, 3, 12)  # Quantity
        sheet.set_column(4, 4, 12)  # Unit Cost
        sheet.set_column(5, 5, 15)  # Value

        row = 0

        # Row 0: Company name
        sheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        sheet.write(row, 0, 'Stock Valuation Report', formats['report_title'])
        row += 1

        # Row 2: Period
        sheet.write(row, 0, f"As of: {data.get('date_to', '')}", formats['metadata'])
        row += 1

        # Row 3: Generated info
        from odoo.fields import Datetime
        sheet.write(row, 0, f"Generated: {Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        # Row 5: Filter bar (merged)
        filter_text = f"Currency: {data.get('company_currency', 'USD')}"
        if self.ops_branch_ids:
            filter_text += f" | Branches: {', '.join(self.ops_branch_ids.mapped('name'))}"
        sheet.merge_range(row, 0, row, 5, filter_text, formats['filter_bar'])
        row += 1
        row += 1

        # Row 7: Column headers
        headers = ['Product', 'Location', 'Category', 'Quantity', 'Unit Cost', 'Value']
        for col, header in enumerate(headers):
            fmt = formats['table_header_num'] if col >= 3 else formats['table_header']
            sheet.write(row, col, header, fmt)
        row += 1

        # Row 8+: Data (freeze here)
        sheet.freeze_panes(row, 0)

        # Data rows with alternating styles
        for idx, item in enumerate(data.get('data', [])):
            is_alt = idx % 2 == 1
            text_fmt = formats['text_alt'] if is_alt else formats['text']

            sheet.write(row, 0, item.get('product_name', ''), text_fmt)
            sheet.write(row, 1, item.get('location_name', ''), text_fmt)
            sheet.write(row, 2, item.get('category_name', ''), text_fmt)
            sheet.write(row, 3, item.get('quantity', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 4, item.get('unit_cost', 0), formats['number_alt'] if is_alt else formats['number'])

            value = item.get('value', 0)
            if value > 0:
                fmt = formats['number_alt'] if is_alt else formats['number']
            elif value < 0:
                fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']
            sheet.write(row, 5, value, fmt)
            row += 1

        # Grand total
        totals = data.get('totals', {})
        sheet.write(row, 2, 'TOTAL', formats['total_label'])
        sheet.write(row, 3, totals.get('total_quantity', 0), formats['total_number'])
        sheet.write(row, 5, totals.get('total_value', 0), formats['total_number'])

    def _write_aging_excel(self, workbook, formats, data):
        """Write Inventory Aging report to Excel."""
        sheet = workbook.add_worksheet('Inventory Aging')

        sheet.set_column(0, 0, 40)  # Product
        sheet.set_column(1, 1, 30)  # Location
        sheet.set_column(2, 2, 12)  # Age Days
        sheet.set_column(3, 3, 12)  # Quantity
        sheet.set_column(4, 4, 15)  # Value
        sheet.set_column(5, 5, 12)  # Status

        row = 0

        # Row 0: Company name
        sheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        sheet.write(row, 0, 'Inventory Aging Analysis', formats['report_title'])
        row += 1

        # Row 2: Period
        sheet.write(row, 0, f"As of: {data.get('date_to', '')}", formats['metadata'])
        row += 1

        # Row 3: Generated info
        from odoo.fields import Datetime
        sheet.write(row, 0, f"Generated: {Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        # Row 5: Filter bar (merged) with aging periods
        filter_text = f"Aging Periods: {self.aging_period_1}/{self.aging_period_2}/{self.aging_period_3}/{self.aging_period_4} days"
        if self.ops_branch_ids:
            filter_text += f" | Branches: {', '.join(self.ops_branch_ids.mapped('name'))}"
        sheet.merge_range(row, 0, row, 5, filter_text, formats['filter_bar'])
        row += 1
        row += 1

        # Row 7: Column headers
        headers = ['Product', 'Location', 'Age (Days)', 'Quantity', 'Value', 'Status']
        for col, header in enumerate(headers):
            fmt = formats['table_header_num'] if col in [2, 3, 4] else formats['table_header']
            sheet.write(row, col, header, fmt)
        row += 1

        # Row 8+: Data (freeze here)
        sheet.freeze_panes(row, 0)

        # Detail rows with alternating styles
        p4 = data.get('aging_periods', {}).get('p4', 180)
        for idx, item in enumerate(data.get('all_items', [])):
            is_alt = idx % 2 == 1
            text_fmt = formats['text_alt'] if is_alt else formats['text']
            age_days = item.get('age_days', 0)

            sheet.write(row, 0, item.get('product_name', ''), text_fmt)
            sheet.write(row, 1, item.get('location_name', ''), text_fmt)
            sheet.write(row, 2, age_days, formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 3, item.get('quantity', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 4, item.get('value', 0), formats['number_alt'] if is_alt else formats['number'])

            # Status based on age - Note: using text_fmt since badges don't exist in new formats
            if age_days > p4:
                sheet.write(row, 5, 'DEAD STOCK', text_fmt)
            elif age_days > 90:
                sheet.write(row, 5, 'OLD', text_fmt)
            else:
                sheet.write(row, 5, 'NORMAL', text_fmt)
            row += 1

        # Total
        totals = data.get('totals', {})
        sheet.write(row, 2, 'TOTAL', formats['total_label'])
        sheet.write(row, 3, totals.get('total_quantity', 0), formats['total_number'])
        sheet.write(row, 4, totals.get('total_value', 0), formats['total_number'])

    def _write_negative_excel(self, workbook, formats, data):
        """Write Negative Stock Alert report to Excel."""
        sheet = workbook.add_worksheet('Negative Stock')

        sheet.set_column(0, 0, 40)  # Product
        sheet.set_column(1, 1, 30)  # Location
        sheet.set_column(2, 2, 12)  # Quantity
        sheet.set_column(3, 3, 12)  # Reserved
        sheet.set_column(4, 4, 15)  # Value
        sheet.set_column(5, 5, 12)  # Severity

        row = 0

        # Row 0: Company name
        sheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        sheet.write(row, 0, 'NEGATIVE STOCK ALERT', formats['report_title'])
        row += 1

        # Row 2: Period
        sheet.write(row, 0, f"As of: {data.get('date_to', '')}", formats['metadata'])
        row += 1

        # Row 3: Generated info
        from odoo.fields import Datetime
        sheet.write(row, 0, f"Generated: {Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        # Row 5: Filter bar (merged) with alert summary
        totals = data.get('totals', {})
        alert_count = totals.get('alert_count', 0)
        critical_count = totals.get('critical_count', 0)
        if alert_count > 0:
            filter_text = f"⚠ ALERT: {alert_count} items with negative stock ({critical_count} CRITICAL)"
        else:
            filter_text = "✓ All Clear - No negative stock found"
        if self.ops_branch_ids:
            filter_text += f" | Branches: {', '.join(self.ops_branch_ids.mapped('name'))}"
        sheet.merge_range(row, 0, row, 5, filter_text, formats['filter_bar'])
        row += 1
        row += 1

        # Row 7: Column headers
        headers = ['Product', 'Location', 'Quantity', 'Reserved', 'Value', 'Severity']
        for col, header in enumerate(headers):
            fmt = formats['table_header_num'] if col in [2, 3, 4] else formats['table_header']
            sheet.write(row, col, header, fmt)
        row += 1

        # Row 8+: Data (freeze here)
        sheet.freeze_panes(row, 0)

        # Data rows with alternating styles
        for idx, item in enumerate(data.get('data', [])):
            is_alt = idx % 2 == 1
            text_fmt = formats['text_alt'] if is_alt else formats['text']

            sheet.write(row, 0, item.get('product_name', ''), text_fmt)
            sheet.write(row, 1, item.get('location_name', ''), text_fmt)
            sheet.write(row, 2, item.get('quantity', 0), formats['number_negative_alt'] if is_alt else formats['number_negative'])
            sheet.write(row, 3, item.get('reserved_quantity', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 4, item.get('value', 0), formats['number_negative_alt'] if is_alt else formats['number_negative'])
            severity = item.get('severity', 'warning')
            sheet.write(row, 5, severity.upper(), text_fmt)
            row += 1

        # Total
        if data.get('data'):
            sheet.write(row, 1, 'TOTAL', formats['total_label'])
            sheet.write(row, 2, totals.get('total_negative_qty', 0), formats['total_number'])
            sheet.write(row, 4, totals.get('total_negative_value', 0), formats['total_number'])

    def _write_movement_excel(self, workbook, formats, data):
        """Write Fast/Slow Moving report to Excel."""
        sheet = workbook.add_worksheet('Movement Analysis')

        sheet.set_column(0, 0, 40)  # Product
        sheet.set_column(1, 1, 12)  # Current Qty
        sheet.set_column(2, 2, 15)  # Current Value
        sheet.set_column(3, 3, 10)  # Moves
        sheet.set_column(4, 4, 12)  # Qty Moved
        sheet.set_column(5, 5, 10)  # Turnover
        sheet.set_column(6, 6, 12)  # Class

        row = 0

        # Row 0: Company name
        sheet.write(row, 0, self.company_id.name, formats['company_name'])
        row += 1

        # Row 1: Report title
        sheet.write(row, 0, 'Fast vs Slow Moving Analysis', formats['report_title'])
        row += 1

        # Row 2: Period
        sheet.write(row, 0, f"Period: {data.get('date_from', '')} to {data.get('date_to', '')}", formats['metadata'])
        row += 1

        # Row 3: Generated info
        from odoo.fields import Datetime
        sheet.write(row, 0, f"Generated: {Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.env.user.name}", formats['metadata'])
        row += 1
        row += 1

        # Row 5: Filter bar (merged) with movement criteria
        filter_text = f"Slow Moving Threshold: < {self.slow_threshold} moves"
        if self.ops_branch_ids:
            filter_text += f" | Branches: {', '.join(self.ops_branch_ids.mapped('name'))}"
        sheet.merge_range(row, 0, row, 6, filter_text, formats['filter_bar'])
        row += 1
        row += 1

        # Row 7: Column headers
        headers = ['Product', 'Current Qty', 'Current Value', 'Moves', 'Qty Moved', 'Turnover', 'Class']
        for col, header in enumerate(headers):
            fmt = formats['table_header_num'] if col >= 1 else formats['table_header']
            sheet.write(row, col, header, fmt)
        row += 1

        # Row 8+: Data (freeze here)
        sheet.freeze_panes(row, 0)

        # Data rows with alternating styles
        for idx, item in enumerate(data.get('data', [])):
            is_alt = idx % 2 == 1
            text_fmt = formats['text_alt'] if is_alt else formats['text']

            sheet.write(row, 0, item.get('product_name', ''), text_fmt)
            sheet.write(row, 1, item.get('current_qty', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 2, item.get('current_value', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 3, item.get('move_count', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 4, item.get('qty_moved', 0), formats['number_alt'] if is_alt else formats['number'])
            sheet.write(row, 5, item.get('turnover_ratio', 0), formats['percentage'])

            mv_class = item.get('movement_class', 'dead')
            sheet.write(row, 6, item.get('movement_label', 'Unknown'), text_fmt)
            row += 1

        # Total
        totals = data.get('totals', {})
        sheet.write(row, 0, 'TOTAL', formats['total_label'])
        sheet.write(row, 1, totals.get('total_qty', 0), formats['total_number'])
        sheet.write(row, 2, totals.get('total_value', 0), formats['total_number'])

    # ============================================
    # ONCHANGE METHODS
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Adjust options based on report type."""
        if self.report_type == 'aging':
            self.include_zero_qty = False
        elif self.report_type == 'negative':
            self.include_zero_qty = False
        elif self.report_type == 'movement':
            if not self.date_from:
                self.date_from = self.date_to - timedelta(days=self.movement_period)

    @api.onchange('movement_period')
    def _onchange_movement_period(self):
        """Update date_from when movement period changes."""
        if self.report_type == 'movement':
            self.date_from = self.date_to - timedelta(days=self.movement_period)

    # ============================================
    # SMART TEMPLATE METHODS
    # ============================================
    # _onchange_report_template_id, _get_template_config, action_save_template
    # are inherited from ops.base.report.wizard
