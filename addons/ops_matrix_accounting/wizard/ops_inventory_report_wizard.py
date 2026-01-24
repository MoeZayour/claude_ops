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


class OpsInventoryReportWizard(models.TransientModel):
    """Inventory Intelligence - Stock Analysis Engine"""
    _name = 'ops.inventory.report.wizard'
    _description = 'Inventory Intelligence Report Wizard'

    # ============================================
    # SMART TEMPLATE SELECTOR
    # ============================================
    report_template_id = fields.Many2one(
        'ops.report.template',
        string='Load Template',
        domain="[('engine', '=', 'inventory'), '|', ('is_global', '=', True), ('user_id', '=', uid)]",
        help='Select a saved report template to load its configuration'
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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

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
    report_title = fields.Char(
        compute='_compute_report_title',
        string='Report Title'
    )

    filter_summary = fields.Char(
        compute='_compute_filter_summary',
        string='Filter Summary'
    )

    record_count = fields.Integer(
        compute='_compute_record_count',
        string='Estimated Items'
    )

    total_value = fields.Monetary(
        compute='_compute_totals',
        string='Total Value',
        currency_field='currency_id'
    )

    total_quantity = fields.Float(
        compute='_compute_totals',
        string='Total Quantity'
    )

    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency'
    )

    # ============================================
    # COMPUTED METHODS
    # ============================================

    @api.depends('report_type')
    def _compute_report_title(self):
        """Generate report title based on selections."""
        report_titles = {
            'valuation': 'Stock Valuation Report',
            'aging': 'Inventory Aging Analysis',
            'negative': 'Negative Stock Alert',
            'movement': 'Fast vs Slow Moving Analysis',
        }
        for wizard in self:
            wizard.report_title = report_titles.get(wizard.report_type, 'Inventory Report')

    @api.depends('date_to', 'ops_branch_ids', 'location_ids', 'product_category_ids', 'report_type')
    def _compute_filter_summary(self):
        """Generate human-readable filter summary."""
        for wizard in self:
            parts = [wizard.report_title or 'Inventory Report']
            parts.append(f"As of: {wizard.date_to}")

            if wizard.ops_branch_ids:
                parts.append(f"Branches: {len(wizard.ops_branch_ids)} selected")

            if wizard.location_ids:
                parts.append(f"Locations: {len(wizard.location_ids)} selected")

            if wizard.product_category_ids:
                parts.append(f"Categories: {len(wizard.product_category_ids)} selected")

            wizard.filter_summary = " | ".join(parts)

    @api.depends('ops_branch_ids', 'location_ids', 'product_category_ids', 'include_zero_qty')
    def _compute_record_count(self):
        """Estimate number of quants matching filters."""
        for wizard in self:
            try:
                domain = wizard._build_quant_domain()
                count = self.env['stock.quant'].search_count(domain)
                wizard.record_count = count
            except Exception as e:
                _logger.error(f"Error counting quants: {e}")
                wizard.record_count = 0

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

    def _validate_filters(self):
        """Validate wizard filters."""
        self.ensure_one()

        if self.report_type == 'movement' and not self.date_from:
            self.date_from = self.date_to - timedelta(days=self.movement_period)

        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_("From date cannot be after To date."))

        return True

    # ============================================
    # REPORT GENERATION
    # ============================================

    def action_generate_report(self):
        """Main action: Generate inventory report."""
        self.ensure_one()
        self._validate_filters()

        # Dispatch to appropriate handler
        report_data = self._get_report_data()

        # Return report action
        return self._return_report_action(report_data)

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
        """Get Fast vs Slow Moving analysis report data."""
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

        # Analyze movements for each product
        data = []
        for product in products:
            # Count stock moves in the period
            move_domain = [
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
            ]
            moves = self.env['stock.move'].search(move_domain)
            move_count = len(moves)
            total_qty_moved = sum(moves.mapped('quantity'))

            # Get current stock
            product_quants = quants.filtered(lambda q: q.product_id.id == product.id)
            current_qty = sum(product_quants.mapped('quantity'))
            current_value = sum(product_quants.mapped('value'))

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
        """Return appropriate report action."""
        # For now, return a tree view of stock.quant with filters
        # In future, this can be extended to PDF/Excel reports

        domain = self._build_quant_domain()
        if self.ops_branch_ids:
            branch_locations = self._get_branch_locations()
            if branch_locations:
                domain.append(('location_id', 'in', branch_locations))

        return {
            'name': self.report_title,
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'list,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_internal_loc': 1,
                'report_data': data,
            },
        }

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
        """Export report to Excel (placeholder for future implementation)."""
        self.ensure_one()

        report_data = self._get_report_data()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Export'),
                'message': _('Excel export will be available in a future update.'),
                'type': 'info',
                'sticky': False,
            }
        }

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

    @api.onchange('report_template_id')
    def _onchange_report_template_id(self):
        """Load configuration from selected template."""
        if not self.report_template_id:
            return

        template = self.report_template_id
        config = template.get_config_dict()

        if not config:
            return

        # Apply scalar fields
        scalar_fields = [
            'report_type', 'group_by', 'include_zero_qty',
            'aging_period_1', 'aging_period_2', 'aging_period_3', 'aging_period_4',
            'min_age_days', 'movement_period', 'slow_threshold',
        ]
        for field in scalar_fields:
            if field in config:
                setattr(self, field, config[field])

        # Apply Many2many fields
        if config.get('ops_branch_ids'):
            self.ops_branch_ids = [(6, 0, config['ops_branch_ids'])]
        if config.get('location_ids'):
            self.location_ids = [(6, 0, config['location_ids'])]
        if config.get('product_category_ids'):
            self.product_category_ids = [(6, 0, config['product_category_ids'])]

        # Increment template usage
        template.increment_usage()

        _logger.info(f"Loaded inventory report template: {template.name}")

    def _get_template_config(self):
        """Get current wizard configuration for template saving."""
        self.ensure_one()
        return {
            'report_type': self.report_type,
            'group_by': self.group_by,
            'include_zero_qty': self.include_zero_qty,
            'aging_period_1': self.aging_period_1,
            'aging_period_2': self.aging_period_2,
            'aging_period_3': self.aging_period_3,
            'aging_period_4': self.aging_period_4,
            'min_age_days': self.min_age_days,
            'movement_period': self.movement_period,
            'slow_threshold': self.slow_threshold,
            # Many2many as ID lists
            'ops_branch_ids': self.ops_branch_ids.ids,
            'location_ids': self.location_ids.ids,
            'product_category_ids': self.product_category_ids.ids,
        }

    def action_save_template(self):
        """Open wizard to save current settings as a template."""
        self.ensure_one()
        return {
            'name': _('Save as Report Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.report.template.save.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_wizard_model': self._name,
                'default_source_wizard_id': self.id,
            },
        }
