# -*- coding: utf-8 -*-
"""
OPS Matrix Inventory Intelligence Engine (v2 Data Contracts)
=============================================================

Inventory analysis wizard refactored to use Shape C (matrix) data contracts.
Reports: Stock Valuation, Aging Analysis, Negative Stock, Movement Analysis.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dataclasses import asdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeCReport, ColumnDef, MatrixRow,
)

_logger = logging.getLogger(__name__)


class OpsInventoryReportWizard(models.TransientModel):
    """Inventory Intelligence - Stock Analysis Engine"""
    _name = 'ops.inventory.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Inventory Intelligence Report Wizard'

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
    date_from = fields.Date(string='From Date', help='Start date for movement analysis')

    # ============================================
    # 3. DIMENSION FILTERS
    # ============================================
    location_ids = fields.Many2many(
        'stock.location', 'inventory_wizard_location_rel', 'wizard_id', 'location_id',
        string='Locations', domain="[('usage', '=', 'internal')]",
        help='Filter by specific stock locations. Leave empty for all internal locations.'
    )
    product_category_ids = fields.Many2many(
        'product.category', 'inventory_wizard_category_rel', 'wizard_id', 'category_id',
        string='Product Categories', help='Filter by product categories. Leave empty for all.'
    )
    product_ids = fields.Many2many(
        'product.product', 'inventory_wizard_product_rel', 'wizard_id', 'product_id',
        string='Products', help='Filter by specific products.'
    )

    # ============================================
    # 4. AGING OPTIONS
    # ============================================
    aging_period_1 = fields.Integer(string='Period 1 (Days)', default=30)
    aging_period_2 = fields.Integer(string='Period 2 (Days)', default=60)
    aging_period_3 = fields.Integer(string='Period 3 (Days)', default=90)
    aging_period_4 = fields.Integer(string='Period 4 (Days)', default=120)
    min_age_days = fields.Integer(string='Min Age Filter (Days)', default=0)

    # ============================================
    # 5. MOVEMENT OPTIONS
    # ============================================
    movement_period = fields.Selection([
        ('30', 'Last 30 Days'),
        ('60', 'Last 60 Days'),
        ('90', 'Last 90 Days'),
        ('180', 'Last 6 Months'),
        ('365', 'Last Year'),
    ], string='Movement Period', default='90')
    slow_threshold = fields.Integer(string='Slow Moving Threshold (days)', default=90,
                                     help='Days without movement to flag as slow-moving')

    # ============================================
    # 6. DISPLAY OPTIONS
    # ============================================
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('location', 'By Location'),
        ('category', 'By Category'),
        ('product', 'By Product'),
    ], string='Group By', default='none')
    include_zero_qty = fields.Boolean(string='Include Zero Quantity', default=False)

    # ============================================
    # 7. COMPUTED / PREVIEW
    # ============================================
    total_quantity = fields.Float(compute='_compute_inventory_totals', string='Total Quantity')
    total_value = fields.Monetary(compute='_compute_inventory_totals', string='Total Value',
                                   currency_field='currency_id')

    # ============================================
    # BASE CLASS HOOKS
    # ============================================

    def _get_engine_name(self):
        return 'inventory'

    def _get_report_shape(self):
        return 'matrix'

    def _get_report_titles(self):
        return {
            'valuation': 'Stock Valuation Report',
            'aging': 'Inventory Aging Analysis',
            'negative': 'Negative Stock Alert',
            'movement': 'Movement Analysis',
        }

    def _get_scalar_fields_for_template(self):
        return ['report_type', 'group_by', 'include_zero_qty', 'movement_period',
                'slow_threshold', 'aging_period_1', 'aging_period_2',
                'aging_period_3', 'aging_period_4', 'min_age_days']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'location_ids', 'product_category_ids', 'product_ids']

    def _get_report_template_xmlid(self):
        self.ensure_one()
        mapping = {
            'valuation': 'ops_matrix_accounting.report_inventory_valuation_corporate',
            'aging': 'ops_matrix_accounting.report_inventory_aging_corporate',
            'negative': 'ops_matrix_accounting.report_inventory_negative_corporate',
            'movement': 'ops_matrix_accounting.report_inventory_movement_corporate',
        }
        return mapping.get(self.report_type, mapping['valuation'])

    def _add_filter_summary_parts(self, parts):
        if self.branch_ids:
            parts.append(f"Branches: {len(self.branch_ids)} selected")
        if self.location_ids:
            parts.append(f"Locations: {len(self.location_ids)} selected")
        if self.product_category_ids:
            parts.append(f"Categories: {len(self.product_category_ids)} selected")
        if self.product_ids:
            parts.append(f"Products: {len(self.product_ids)} selected")

    def _estimate_record_count(self):
        domain = self._build_quant_domain()
        return self.env['stock.quant'].search_count(domain)

    # ============================================
    # COMPUTED FIELDS
    # ============================================

    @api.depends('branch_ids', 'location_ids', 'product_category_ids', 'product_ids',
                 'include_zero_qty', 'report_type')
    def _compute_inventory_totals(self):
        for wizard in self:
            try:
                domain = wizard._build_quant_domain()
                quants = self.env['stock.quant'].search(domain)
                wizard.total_quantity = sum(quants.mapped('quantity'))
                wizard.total_value = sum(quants.mapped('value'))
            except Exception as e:
                _logger.error(f"Error computing inventory totals: {e}")
                wizard.total_quantity = 0.0
                wizard.total_value = 0.0

    # ============================================
    # DOMAIN BUILDING
    # ============================================

    def _build_quant_domain(self):
        """Build domain for stock.quant queries with branch isolation."""
        self.ensure_one()
        domain = [
            ('location_id.usage', '=', 'internal'),
            ('company_id', '=', self.company_id.id),
        ]

        if not self.include_zero_qty and self.report_type != 'negative':
            domain.append(('quantity', '!=', 0))

        if self.report_type == 'negative':
            domain.append(('quantity', '<', 0))

        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        elif self.branch_ids:
            # Map branches to warehouses to locations
            warehouses = self.env['stock.warehouse'].search([
                ('ops_branch_id', 'in', self.branch_ids.ids),
                ('company_id', '=', self.company_id.id),
            ])
            if warehouses:
                locations = self.env['stock.location'].search([
                    ('warehouse_id', 'in', warehouses.ids),
                    ('usage', '=', 'internal'),
                ])
                domain.append(('location_id', 'in', locations.ids))

        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))

        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))

        return domain

    def _build_move_domain(self):
        """Build domain for stock.move queries."""
        self.ensure_one()
        domain = [
            ('state', '=', 'done'),
            ('company_id', '=', self.company_id.id),
        ]

        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))

        if self.branch_ids:
            warehouses = self.env['stock.warehouse'].search([
                ('ops_branch_id', 'in', self.branch_ids.ids),
                ('company_id', '=', self.company_id.id),
            ])
            if warehouses:
                locations = self.env['stock.location'].search([
                    ('warehouse_id', 'in', warehouses.ids),
                    ('usage', '=', 'internal'),
                ])
                domain.append('|')
                domain.append(('location_id', 'in', locations.ids))
                domain.append(('location_dest_id', 'in', locations.ids))

        if self.product_category_ids:
            domain.append(('product_id.categ_id', 'in', self.product_category_ids.ids))

        return domain

    # ============================================
    # REPORT DATA (v2 contracts)
    # ============================================

    def _get_report_data(self):
        """Dispatch to correct report data method."""
        self.ensure_one()
        self._check_intelligence_access(self._get_pillar_name())

        dispatch = {
            'valuation': self._get_valuation_data,
            'aging': self._get_aging_data,
            'negative': self._get_negative_data,
            'movement': self._get_movement_data,
        }
        return dispatch.get(self.report_type, self._get_valuation_data)()

    def _can_see_cost(self):
        return self.env.user.has_group('ops_matrix_core.group_ops_see_cost')

    def _can_see_valuation(self):
        return self.env.user.has_group('ops_matrix_core.group_ops_see_valuation')

    def _get_valuation_data(self):
        """Stock Valuation -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'valuation', 'Stock Valuation Report', 'matrix')
        colors = build_report_colors(self.company_id)
        show_cost = self._can_see_cost()
        show_val = self._can_see_valuation()

        columns = [
            ColumnDef(key='product', label='Product', col_type='string'),
            ColumnDef(key='category', label='Category', col_type='string'),
            ColumnDef(key='location', label='Location', col_type='string'),
            ColumnDef(key='qty', label='Qty On Hand', col_type='number', align='right', subtotal=True),
            ColumnDef(key='uom', label='UoM', col_type='string', width=6),
        ]
        if show_cost:
            columns.append(ColumnDef(key='unit_cost', label='Unit Cost', col_type='currency', align='right'))
        if show_val:
            columns.append(ColumnDef(key='total_value', label='Total Value', col_type='currency', align='right', subtotal=True))
        columns.append(ColumnDef(key='warehouse', label='Warehouse', col_type='string'))

        quants = self.env['stock.quant'].search(self._build_quant_domain(), order='product_id, location_id')
        rows = []
        total_qty = 0.0
        total_val = 0.0

        for quant in quants:
            qty = quant.quantity
            total_qty += qty
            vals = {
                'product': quant.product_id.display_name or '',
                'category': quant.product_id.categ_id.name if quant.product_id.categ_id else '',
                'location': quant.location_id.complete_name or '',
                'qty': qty,
                'uom': quant.product_uom_id.name if quant.product_uom_id else '',
                'warehouse': quant.location_id.warehouse_id.name if quant.location_id.warehouse_id else '',
            }
            if show_cost:
                vals['unit_cost'] = quant.product_id.standard_price
            if show_val:
                vals['total_value'] = quant.value
                total_val += quant.value
            rows.append(MatrixRow(values=vals))

        totals = {'qty': total_qty, 'count': len(rows)}
        if show_val:
            totals['total_value'] = total_val

        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_aging_data(self):
        """Inventory Aging -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'aging', 'Inventory Aging Analysis', 'matrix')
        colors = build_report_colors(self.company_id)
        show_val = self._can_see_valuation()

        p1, p2, p3, p4 = self.aging_period_1, self.aging_period_2, self.aging_period_3, self.aging_period_4

        columns = [
            ColumnDef(key='product', label='Product', col_type='string'),
            ColumnDef(key='category', label='Category', col_type='string'),
            ColumnDef(key='qty', label='Qty', col_type='number', align='right', subtotal=True),
        ]
        if show_val:
            columns.append(ColumnDef(key='value', label='Value', col_type='currency', align='right', subtotal=True))
        columns.extend([
            ColumnDef(key='current', label=f'0-{p1}d', col_type='number', align='right', subtotal=True),
            ColumnDef(key='bucket_2', label=f'{p1+1}-{p2}d', col_type='number', align='right', subtotal=True),
            ColumnDef(key='bucket_3', label=f'{p2+1}-{p3}d', col_type='number', align='right', subtotal=True),
            ColumnDef(key='bucket_4', label=f'{p3+1}-{p4}d', col_type='number', align='right', subtotal=True),
            ColumnDef(key='older', label=f'>{p4}d', col_type='number', align='right', subtotal=True),
        ])

        quants = self.env['stock.quant'].search(self._build_quant_domain(), order='product_id')
        today = self.date_to or fields.Date.today()
        rows = []

        # Group by product
        product_data = {}
        for quant in quants:
            pid = quant.product_id.id
            if pid not in product_data:
                product_data[pid] = {
                    'product': quant.product_id.display_name,
                    'category': quant.product_id.categ_id.name if quant.product_id.categ_id else '',
                    'qty': 0, 'value': 0,
                    'current': 0, 'bucket_2': 0, 'bucket_3': 0, 'bucket_4': 0, 'older': 0,
                }
            product_data[pid]['qty'] += quant.quantity
            product_data[pid]['value'] += quant.value

            # Determine age from last incoming move
            last_move = self.env['stock.move'].search([
                ('product_id', '=', quant.product_id.id),
                ('location_dest_id', '=', quant.location_id.id),
                ('state', '=', 'done'),
            ], order='date desc', limit=1)
            if last_move:
                age = (today - last_move.date.date()).days
            else:
                age = 999

            qty = quant.quantity
            if age <= p1:
                product_data[pid]['current'] += qty
            elif age <= p2:
                product_data[pid]['bucket_2'] += qty
            elif age <= p3:
                product_data[pid]['bucket_3'] += qty
            elif age <= p4:
                product_data[pid]['bucket_4'] += qty
            else:
                product_data[pid]['older'] += qty

        for pdata in sorted(product_data.values(), key=lambda x: x['product']):
            if self.min_age_days and pdata['older'] == 0 and pdata['bucket_4'] == 0:
                continue
            vals = {
                'product': pdata['product'],
                'category': pdata['category'],
                'qty': pdata['qty'],
                'current': pdata['current'],
                'bucket_2': pdata['bucket_2'],
                'bucket_3': pdata['bucket_3'],
                'bucket_4': pdata['bucket_4'],
                'older': pdata['older'],
            }
            if show_val:
                vals['value'] = pdata['value']
            rows.append(MatrixRow(values=vals))

        totals = {'count': len(rows), 'qty': sum(r.values.get('qty', 0) for r in rows)}
        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_negative_data(self):
        """Negative Stock Alert -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'negative', 'Negative Stock Alert', 'matrix')
        colors = build_report_colors(self.company_id)

        columns = [
            ColumnDef(key='product', label='Product', col_type='string'),
            ColumnDef(key='category', label='Category', col_type='string'),
            ColumnDef(key='location', label='Location', col_type='string'),
            ColumnDef(key='warehouse', label='Warehouse', col_type='string'),
            ColumnDef(key='qty', label='Quantity', col_type='number', align='right', subtotal=True),
            ColumnDef(key='last_move_date', label='Last Movement', col_type='date'),
        ]

        quants = self.env['stock.quant'].search(self._build_quant_domain(), order='quantity asc')
        rows = []

        for quant in quants:
            last_move = self.env['stock.move'].search([
                ('product_id', '=', quant.product_id.id),
                ('state', '=', 'done'),
            ], order='date desc', limit=1)

            rows.append(MatrixRow(values={
                'product': quant.product_id.display_name or '',
                'category': quant.product_id.categ_id.name if quant.product_id.categ_id else '',
                'location': quant.location_id.complete_name or '',
                'warehouse': quant.location_id.warehouse_id.name if quant.location_id.warehouse_id else '',
                'qty': quant.quantity,
                'last_move_date': str(last_move.date.date()) if last_move else '',
            }))

        totals = {'count': len(rows), 'qty': sum(r.values.get('qty', 0) for r in rows)}
        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_movement_data(self):
        """Movement Analysis -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'movement', 'Movement Analysis', 'matrix')
        colors = build_report_colors(self.company_id)
        show_val = self._can_see_valuation()

        columns = [
            ColumnDef(key='product', label='Product', col_type='string'),
            ColumnDef(key='category', label='Category', col_type='string'),
            ColumnDef(key='opening_qty', label='Opening Qty', col_type='number', align='right', subtotal=True),
            ColumnDef(key='qty_in', label='IN', col_type='number', align='right', subtotal=True),
            ColumnDef(key='qty_out', label='OUT', col_type='number', align='right', subtotal=True),
            ColumnDef(key='closing_qty', label='Closing Qty', col_type='number', align='right', subtotal=True),
        ]
        if show_val:
            columns.append(ColumnDef(key='value', label='Value', col_type='currency', align='right', subtotal=True))
        columns.append(ColumnDef(key='movement_flag', label='Status', col_type='string'))

        # Get moves in the period
        moves = self.env['stock.move'].search(self._build_move_domain())

        product_data = {}
        internal_locations = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('company_id', '=', self.company_id.id),
        ]).ids

        for move in moves:
            pid = move.product_id.id
            if pid not in product_data:
                product_data[pid] = {
                    'product': move.product_id.display_name,
                    'category': move.product_id.categ_id.name if move.product_id.categ_id else '',
                    'qty_in': 0, 'qty_out': 0,
                }

            if move.location_dest_id.id in internal_locations:
                product_data[pid]['qty_in'] += move.quantity
            if move.location_id.id in internal_locations:
                product_data[pid]['qty_out'] += move.quantity

        # Get current on-hand for closing qty
        quant_domain = self._build_quant_domain()
        quants = self.env['stock.quant'].search(quant_domain)
        quant_map = {}
        for q in quants:
            pid = q.product_id.id
            quant_map.setdefault(pid, {'qty': 0, 'value': 0})
            quant_map[pid]['qty'] += q.quantity
            quant_map[pid]['value'] += q.value

        rows = []
        period_days = int(self.movement_period or '90')

        for pid, pdata in sorted(product_data.items(), key=lambda x: x[1]['product']):
            closing = quant_map.get(pid, {}).get('qty', 0)
            opening = closing - pdata['qty_in'] + pdata['qty_out']

            # Determine movement flag
            if pdata['qty_in'] == 0 and pdata['qty_out'] == 0:
                flag = 'No Movement'
            elif pdata['qty_out'] > pdata['qty_in'] * 2:
                flag = 'Fast Moving'
            elif pdata['qty_out'] < pdata['qty_in'] * 0.1:
                flag = 'Slow Moving'
            else:
                flag = 'Normal'

            vals = {
                'product': pdata['product'],
                'category': pdata['category'],
                'opening_qty': opening,
                'qty_in': pdata['qty_in'],
                'qty_out': pdata['qty_out'],
                'closing_qty': closing,
                'movement_flag': flag,
            }
            if show_val:
                vals['value'] = quant_map.get(pid, {}).get('value', 0)
            rows.append(MatrixRow(values=vals))

        totals = {'count': len(rows)}
        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    # ============================================
    # REPORT ACTION
    # ============================================

    def _return_report_action(self, data):
        """Return report action for PDF generation."""
        report_refs = {
            'valuation': 'ops_matrix_accounting.action_report_stock_valuation',
            'aging': 'ops_matrix_accounting.action_report_inventory_aging',
            'negative': 'ops_matrix_accounting.action_report_negative_stock',
            'movement': 'ops_matrix_accounting.action_report_inventory_movement',
        }
        return self.env.ref(report_refs.get(self.report_type, report_refs['valuation'])).report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_quants(self):
        """Open filtered stock quants in list view."""
        self.ensure_one()
        return {
            'name': _('Stock Quants'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'list,form',
            'domain': self._build_quant_domain(),
        }

    # ============================================
    # ONCHANGE
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type == 'movement' and not self.date_from:
            self.date_from = fields.Date.today() - timedelta(days=int(self.movement_period or '90'))
