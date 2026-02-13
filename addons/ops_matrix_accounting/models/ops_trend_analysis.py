# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Trend Analysis
========================================

Provides trend analysis and variance reporting using pre-computed snapshots.
Supports Month-over-Month (MoM), Quarter-over-Quarter (QoQ), and Year-over-Year (YoY) comparisons.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsTrendAnalysis(models.TransientModel):
    """
    Trend Analysis Wizard

    Compares financial performance across periods using snapshot data.
    Provides MoM, QoQ, and YoY variance analysis with growth rates.
    """
    _name = 'ops.trend.analysis'
    _description = 'Trend Analysis & Variance Reporting'

    # Filter Fields
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # Current Period
    current_period_start = fields.Date(
        string='Current Period Start',
        required=True,
        default=lambda self: date.today().replace(day=1)
    )
    current_period_end = fields.Date(
        string='Current Period End',
        required=True,
        default=lambda self: date.today()
    )

    # Comparison Type
    comparison_type = fields.Selection([
        ('mom', 'Month-over-Month (MoM)'),
        ('qoq', 'Quarter-over-Quarter (QoQ)'),
        ('yoy', 'Year-over-Year (YoY)'),
        ('custom', 'Custom Period'),
    ], string='Comparison Type', default='mom', required=True)

    # Custom comparison period (for 'custom' type)
    comparison_period_start = fields.Date(
        string='Compare Period Start',
        help='Only used if comparison type is Custom'
    )
    comparison_period_end = fields.Date(
        string='Compare Period End',
        help='Only used if comparison type is Custom'
    )

    # Computed comparison dates
    auto_comparison_start = fields.Date(
        string='Comparison Start',
        compute='_compute_comparison_dates',
        store=False
    )
    auto_comparison_end = fields.Date(
        string='Comparison End',
        compute='_compute_comparison_dates',
        store=False
    )

    # Dimension Filters
    branch_ids = fields.Many2many(
        'ops.branch',
        string='Filter Branches',
        domain="[('company_id', '=', company_id)]",
        help='Leave empty for all branches'
    )
    business_unit_ids = fields.Many2many(
        'ops.business.unit',
        string='Filter Business Units',
        help='Leave empty for all business units'
    )

    # Grouping Options
    group_by = fields.Selection([
        ('total', 'Total Only'),
        ('branch', 'By Branch'),
        ('bu', 'By Business Unit'),
        ('branch_bu', 'By Branch × Business Unit'),
    ], string='Group By', default='total', required=True)

    # Metrics Selection
    show_revenue = fields.Boolean(string='Revenue', default=True)
    show_cogs = fields.Boolean(string='COGS', default=True)
    show_gross_profit = fields.Boolean(string='Gross Profit', default=True)
    show_operating_expense = fields.Boolean(string='Operating Expense', default=True)
    show_ebitda = fields.Boolean(string='EBITDA', default=True)
    show_net_income = fields.Boolean(string='Net Income', default=True)
    show_margins = fields.Boolean(string='Margin %', default=True)

    # Report Data
    trend_data = fields.Json(
        string='Trend Analysis Data',
        compute='_compute_trend_data',
        store=False
    )

    # Data Source Indicator
    data_source = fields.Char(
        string='Data Source',
        compute='_compute_trend_data',
        store=False,
        help='Indicates whether data comes from snapshots or real-time'
    )

    @api.depends('comparison_type', 'current_period_start', 'current_period_end')
    def _compute_comparison_dates(self):
        """Auto-calculate comparison period based on type."""
        for wizard in self:
            if not wizard.current_period_start or not wizard.current_period_end:
                wizard.auto_comparison_start = False
                wizard.auto_comparison_end = False
                continue

            period_days = (wizard.current_period_end - wizard.current_period_start).days + 1

            if wizard.comparison_type == 'mom':
                # Previous month
                wizard.auto_comparison_end = wizard.current_period_start - timedelta(days=1)
                wizard.auto_comparison_start = wizard.auto_comparison_end.replace(day=1)

            elif wizard.comparison_type == 'qoq':
                # Previous quarter (3 months back)
                wizard.auto_comparison_end = wizard.current_period_start - timedelta(days=1)
                wizard.auto_comparison_start = (wizard.current_period_start - relativedelta(months=3))

            elif wizard.comparison_type == 'yoy':
                # Same period last year
                wizard.auto_comparison_start = wizard.current_period_start - relativedelta(years=1)
                wizard.auto_comparison_end = wizard.current_period_end - relativedelta(years=1)

            elif wizard.comparison_type == 'custom':
                # Use custom dates
                wizard.auto_comparison_start = wizard.comparison_period_start
                wizard.auto_comparison_end = wizard.comparison_period_end
            else:
                wizard.auto_comparison_start = False
                wizard.auto_comparison_end = False

    @api.depends(
        'company_id', 'current_period_start', 'current_period_end',
        'comparison_type', 'branch_ids', 'business_unit_ids', 'group_by',
        'show_revenue', 'show_cogs', 'show_gross_profit', 'show_operating_expense',
        'show_ebitda', 'show_net_income', 'show_margins'
    )
    def _compute_trend_data(self):
        """Compute trend analysis using snapshot data."""
        for wizard in self:
            if not wizard.current_period_start or not wizard.current_period_end:
                wizard.trend_data = {}
                wizard.data_source = 'none'
                continue

            # Get comparison period dates
            if wizard.comparison_type == 'custom':
                if not wizard.comparison_period_start or not wizard.comparison_period_end:
                    raise UserError(_('Please specify custom comparison period dates.'))
                comp_start = wizard.comparison_period_start
                comp_end = wizard.comparison_period_end
            else:
                comp_start = wizard.auto_comparison_start
                comp_end = wizard.auto_comparison_end

            if not comp_start or not comp_end:
                wizard.trend_data = {}
                wizard.data_source = 'none'
                continue

            # Try to use snapshots first
            data, source = wizard._get_trend_from_snapshots(comp_start, comp_end)

            if not data:
                # Fallback to real-time computation
                data, source = wizard._get_trend_from_realtime(comp_start, comp_end)

            wizard.trend_data = data
            wizard.data_source = source

    def _get_trend_from_snapshots(self, comp_start, comp_end):
        """
        Get trend data using pre-computed snapshots.

        Returns: (data_dict, source_string)
        """
        self.ensure_one()
        Snapshot = self.env['ops.matrix.snapshot']

        # Query snapshots for current period
        current_snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',  # We'll aggregate if needed
            date_from=self.current_period_start,
            date_to=self.current_period_end,
            company_id=self.company_id.id,
            branch_ids=self.branch_ids.ids if self.branch_ids else None,
            bu_ids=self.business_unit_ids.ids if self.business_unit_ids else None
        )

        # Query snapshots for comparison period
        comparison_snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',
            date_from=comp_start,
            date_to=comp_end,
            company_id=self.company_id.id,
            branch_ids=self.branch_ids.ids if self.branch_ids else None,
            bu_ids=self.business_unit_ids.ids if self.business_unit_ids else None
        )

        if not current_snapshots:
            _logger.warning(
                f"No snapshots found for current period {self.current_period_start} to {self.current_period_end}"
            )
            return None, 'none'

        if not comparison_snapshots:
            _logger.warning(
                f"No snapshots found for comparison period {comp_start} to {comp_end}"
            )
            return None, 'none'

        # Aggregate snapshots based on grouping
        current_data = self._aggregate_snapshots(current_snapshots, self.group_by)
        comparison_data = self._aggregate_snapshots(comparison_snapshots, self.group_by)

        # Calculate variances
        trend_data = self._calculate_variances(current_data, comparison_data)

        return trend_data, 'snapshot'

    def _get_trend_from_realtime(self, comp_start, comp_end):
        """
        Fallback: Get trend data from real-time aggregation.

        Returns: (data_dict, source_string)
        """
        self.ensure_one()
        _logger.info("⟳ Computing trend analysis from real-time data (snapshots unavailable)")

        # Get current period data
        current_data = self._aggregate_realtime(
            self.current_period_start,
            self.current_period_end
        )

        # Get comparison period data
        comparison_data = self._aggregate_realtime(comp_start, comp_end)

        # Calculate variances
        trend_data = self._calculate_variances(current_data, comparison_data)

        return trend_data, 'realtime'

    def _aggregate_snapshots(self, snapshots, group_by):
        """
        Aggregate snapshot records based on grouping option.

        Args:
            snapshots: recordset of ops.matrix.snapshot
            group_by: 'total', 'branch', 'bu', or 'branch_bu'

        Returns:
            dict with aggregated financial data
        """
        self.ensure_one()

        if group_by == 'total':
            # Aggregate everything into single total
            return {
                'total': self._sum_snapshot_metrics(snapshots)
            }

        elif group_by == 'branch':
            # Aggregate by branch
            result = {}
            for branch in snapshots.mapped('branch_id'):
                branch_snapshots = snapshots.filtered(lambda s: s.branch_id == branch)
                result[f'branch_{branch.id}'] = {
                    'dimension': 'branch',
                    'dimension_id': branch.id,
                    'dimension_code': branch.code,
                    'dimension_name': branch.name,
                    **self._sum_snapshot_metrics(branch_snapshots)
                }
            return result

        elif group_by == 'bu':
            # Aggregate by business unit
            result = {}
            for bu in snapshots.mapped('business_unit_id'):
                bu_snapshots = snapshots.filtered(lambda s: s.business_unit_id == bu)
                result[f'bu_{bu.id}'] = {
                    'dimension': 'bu',
                    'dimension_id': bu.id,
                    'dimension_code': bu.code,
                    'dimension_name': bu.name,
                    **self._sum_snapshot_metrics(bu_snapshots)
                }
            return result

        elif group_by == 'branch_bu':
            # Keep full granularity (branch × BU)
            result = {}
            for snapshot in snapshots:
                key = f'branch_{snapshot.branch_id.id}_bu_{snapshot.business_unit_id.id}'
                result[key] = {
                    'dimension': 'branch_bu',
                    'branch_id': snapshot.branch_id.id,
                    'branch_code': snapshot.branch_id.code,
                    'branch_name': snapshot.branch_id.name,
                    'bu_id': snapshot.business_unit_id.id,
                    'bu_code': snapshot.business_unit_id.code,
                    'bu_name': snapshot.business_unit_id.name,
                    **self._sum_snapshot_metrics(snapshot)
                }
            return result

        return {}

    def _sum_snapshot_metrics(self, snapshots):
        """Sum financial metrics from snapshot records."""
        if not snapshots:
            return self._empty_metrics()

        # Handle single record or recordset
        if len(snapshots) == 1:
            s = snapshots[0]
            return {
                'revenue': s.revenue,
                'cogs': s.cogs,
                'gross_profit': s.gross_profit,
                'operating_expense': s.operating_expense,
                'ebitda': s.ebitda,
                'ebit': s.ebit,
                'net_income': s.net_income,
                'gross_margin_pct': s.gross_margin_pct,
                'operating_margin_pct': s.operating_margin_pct,
                'net_margin_pct': s.net_margin_pct,
                'transaction_count': s.transaction_count,
            }

        # Sum multiple records
        revenue = sum(snapshots.mapped('revenue'))
        cogs = sum(snapshots.mapped('cogs'))
        gross_profit = sum(snapshots.mapped('gross_profit'))
        operating_expense = sum(snapshots.mapped('operating_expense'))
        ebitda = sum(snapshots.mapped('ebitda'))
        ebit = sum(snapshots.mapped('ebit'))
        net_income = sum(snapshots.mapped('net_income'))

        return {
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'operating_expense': operating_expense,
            'ebitda': ebitda,
            'ebit': ebit,
            'net_income': net_income,
            'gross_margin_pct': (gross_profit / revenue * 100) if revenue else 0,
            'operating_margin_pct': (ebit / revenue * 100) if revenue else 0,
            'net_margin_pct': (net_income / revenue * 100) if revenue else 0,
            'transaction_count': sum(snapshots.mapped('transaction_count')),
        }

    def _aggregate_realtime(self, date_from, date_to):
        """
        Aggregate financial data from real-time journal entries.

        This is a fallback when snapshots are not available.
        """
        self.ensure_one()
        MoveLine = self.env['account.move.line']

        # Build domain
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('company_id', '=', self.company_id.id),
            ('move_id.state', '=', 'posted'),
        ]

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))

        # Query based on grouping
        if self.group_by == 'total':
            return {'total': self._compute_metrics_from_lines(domain)}

        elif self.group_by == 'branch':
            result = {}
            branches = self.branch_ids if self.branch_ids else self.env['ops.branch'].search([
                ('company_id', '=', self.company_id.id)
            ])

            for branch in branches:
                branch_domain = domain + [('ops_branch_id', '=', branch.id)]
                result[f'branch_{branch.id}'] = {
                    'dimension': 'branch',
                    'dimension_id': branch.id,
                    'dimension_code': branch.code,
                    'dimension_name': branch.name,
                    **self._compute_metrics_from_lines(branch_domain)
                }
            return result

        elif self.group_by == 'bu':
            result = {}
            bus = self.business_unit_ids if self.business_unit_ids else self.env['ops.business.unit'].search([
                ('company_ids', 'in', [self.company_id.id])
            ])

            for bu in bus:
                bu_domain = domain + [('ops_business_unit_id', '=', bu.id)]
                result[f'bu_{bu.id}'] = {
                    'dimension': 'bu',
                    'dimension_id': bu.id,
                    'dimension_code': bu.code,
                    'dimension_name': bu.name,
                    **self._compute_metrics_from_lines(bu_domain)
                }
            return result

        # branch_bu not implemented for realtime (too expensive)
        return {}

    def _compute_metrics_from_lines(self, domain):
        """Compute financial metrics from account move lines."""
        MoveLine = self.env['account.move.line']

        # Aggregate by account type
        # Odoo 19 _read_group returns list of tuples: (group_value, agg1, agg2, ...)
        results = MoveLine._read_group(
            domain=domain,
            groupby=['account_id.account_type'],
            aggregates=['credit:sum', 'debit:sum', '__count']
        )

        metrics = self._empty_metrics()

        for result in results:
            # Odoo 19: result is tuple (account_type, credit_sum, debit_sum, count)
            account_type = result[0]
            credit = result[1] or 0
            debit = result[2] or 0
            count = result[3] or 0

            if account_type in ['income', 'income_other']:
                metrics['revenue'] += credit - debit
            elif account_type == 'expense_direct_cost':
                metrics['cogs'] += debit - credit
            elif account_type in ['expense', 'expense_depreciation']:
                metrics['operating_expense'] += debit - credit

            metrics['transaction_count'] += count

        # Calculate derived metrics
        metrics['gross_profit'] = metrics['revenue'] - metrics['cogs']
        metrics['ebitda'] = metrics['gross_profit'] - metrics['operating_expense']
        metrics['ebit'] = metrics['ebitda']  # Simplified (depreciation in operating_expense)
        metrics['net_income'] = metrics['ebit']  # Simplified (no interest/tax breakdown)

        # Calculate margins
        if metrics['revenue']:
            metrics['gross_margin_pct'] = metrics['gross_profit'] / metrics['revenue'] * 100
            metrics['operating_margin_pct'] = metrics['ebit'] / metrics['revenue'] * 100
            metrics['net_margin_pct'] = metrics['net_income'] / metrics['revenue'] * 100

        return metrics

    def _empty_metrics(self):
        """Return empty metrics structure."""
        return {
            'revenue': 0.0,
            'cogs': 0.0,
            'gross_profit': 0.0,
            'operating_expense': 0.0,
            'ebitda': 0.0,
            'ebit': 0.0,
            'net_income': 0.0,
            'gross_margin_pct': 0.0,
            'operating_margin_pct': 0.0,
            'net_margin_pct': 0.0,
            'transaction_count': 0,
        }

    def _calculate_variances(self, current_data, comparison_data):
        """
        Calculate variance metrics between current and comparison periods.

        Returns:
            dict with variance analysis
        """
        self.ensure_one()

        variance_data = {
            'company': self.company_id.name,
            'current_period': {
                'start': str(self.current_period_start),
                'end': str(self.current_period_end),
            },
            'comparison_period': {
                'start': str(self.auto_comparison_start or self.comparison_period_start),
                'end': str(self.auto_comparison_end or self.comparison_period_end),
            },
            'comparison_type': self.comparison_type,
            'comparison_label': dict(self._fields['comparison_type'].selection).get(self.comparison_type),
            'items': []
        }

        # Process each dimension
        for key in current_data.keys():
            current = current_data.get(key, self._empty_metrics())
            comparison = comparison_data.get(key, self._empty_metrics())

            item = {
                'key': key,
                **current.copy(),  # Include dimension info if present
                'current': self._filter_metrics(current),
                'comparison': self._filter_metrics(comparison),
                'variance': self._compute_variance(current, comparison),
            }

            variance_data['items'].append(item)

        # Sort by revenue (descending)
        variance_data['items'].sort(
            key=lambda x: x['current'].get('revenue', 0),
            reverse=True
        )

        # Add summary
        if variance_data['items']:
            variance_data['summary'] = self._compute_summary(variance_data['items'])

        return variance_data

    def _filter_metrics(self, metrics):
        """Filter metrics based on user selection."""
        filtered = {}

        if self.show_revenue:
            filtered['revenue'] = metrics.get('revenue', 0)
        if self.show_cogs:
            filtered['cogs'] = metrics.get('cogs', 0)
        if self.show_gross_profit:
            filtered['gross_profit'] = metrics.get('gross_profit', 0)
        if self.show_operating_expense:
            filtered['operating_expense'] = metrics.get('operating_expense', 0)
        if self.show_ebitda:
            filtered['ebitda'] = metrics.get('ebitda', 0)
        if self.show_net_income:
            filtered['net_income'] = metrics.get('net_income', 0)
        if self.show_margins:
            filtered['gross_margin_pct'] = metrics.get('gross_margin_pct', 0)
            filtered['net_margin_pct'] = metrics.get('net_margin_pct', 0)

        filtered['transaction_count'] = metrics.get('transaction_count', 0)

        return filtered

    def _compute_variance(self, current, comparison):
        """Compute variance metrics between two periods."""
        variance = {}

        metric_fields = [
            'revenue', 'cogs', 'gross_profit', 'operating_expense',
            'ebitda', 'ebit', 'net_income'
        ]

        for metric in metric_fields:
            curr_val = current.get(metric, 0)
            comp_val = comparison.get(metric, 0)

            # Absolute variance
            abs_variance = curr_val - comp_val

            # Percentage change
            if comp_val != 0:
                pct_change = (abs_variance / abs(comp_val)) * 100
            else:
                pct_change = 100.0 if curr_val > 0 else 0.0

            # Direction indicator
            if abs_variance > 0:
                direction = 'up'
            elif abs_variance < 0:
                direction = 'down'
            else:
                direction = 'flat'

            variance[metric] = {
                'absolute': abs_variance,
                'percentage': pct_change,
                'direction': direction,
            }

        # Margin variance (percentage points)
        for margin in ['gross_margin_pct', 'net_margin_pct']:
            curr_margin = current.get(margin, 0)
            comp_margin = comparison.get(margin, 0)
            margin_change = curr_margin - comp_margin

            variance[margin] = {
                'absolute': margin_change,  # Percentage points
                'direction': 'up' if margin_change > 0 else ('down' if margin_change < 0 else 'flat'),
            }

        return variance

    def _compute_summary(self, items):
        """Compute summary statistics across all items."""
        if not items:
            return {}

        total_current_revenue = sum(item['current'].get('revenue', 0) for item in items)
        total_comparison_revenue = sum(item['comparison'].get('revenue', 0) for item in items)

        total_current_net = sum(item['current'].get('net_income', 0) for item in items)
        total_comparison_net = sum(item['comparison'].get('net_income', 0) for item in items)

        # Overall growth rate
        revenue_growth = 0
        if total_comparison_revenue:
            revenue_growth = ((total_current_revenue - total_comparison_revenue) / abs(total_comparison_revenue)) * 100

        net_income_growth = 0
        if total_comparison_net:
            net_income_growth = ((total_current_net - total_comparison_net) / abs(total_comparison_net)) * 100

        # Best/worst performers
        items_with_growth = [
            {
                'item': item,
                'growth': item['variance'].get('revenue', {}).get('percentage', 0)
            }
            for item in items if 'variance' in item
        ]

        items_with_growth.sort(key=lambda x: x['growth'], reverse=True)

        return {
            'total_current_revenue': total_current_revenue,
            'total_comparison_revenue': total_comparison_revenue,
            'total_current_net_income': total_current_net,
            'total_comparison_net_income': total_comparison_net,
            'revenue_growth_pct': revenue_growth,
            'net_income_growth_pct': net_income_growth,
            'best_performer': items_with_growth[0]['item'] if items_with_growth else None,
            'worst_performer': items_with_growth[-1]['item'] if items_with_growth else None,
            'item_count': len(items),
        }

    # Action Methods

    def action_generate_report(self):
        """Generate trend analysis report."""
        self.ensure_one()

        if not self.trend_data:
            raise UserError(_('No trend data available. Please check your date ranges and filters.'))

        # For now, return a notification with summary
        summary = self.trend_data.get('summary', {})

        message = _(
            "Trend Analysis Results (%(comparison_type)s):\n\n"
            "Revenue Growth: %(revenue_growth).1f%%\n"
            "Net Income Growth: %(net_growth).1f%%\n"
            "Items Analyzed: %(count)d\n\n"
            "Data Source: %(source)s"
        ) % {
            'comparison_type': self.trend_data.get('comparison_label', 'N/A'),
            'revenue_growth': summary.get('revenue_growth_pct', 0),
            'net_growth': summary.get('net_income_growth_pct', 0),
            'count': summary.get('item_count', 0),
            'source': 'Pre-computed Snapshots' if self.data_source == 'snapshot' else 'Real-time Aggregation',
        }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Trend Analysis Complete'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_export_excel(self):
        """Export trend analysis to Excel with full variance breakdown."""
        self.ensure_one()
        import io
        import base64
        try:
            import xlsxwriter
        except ImportError:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Missing Library'),
                    'message': _('xlsxwriter is required for Excel export. Contact your administrator.'),
                    'type': 'warning',
                }
            }

        if not self.trend_data or not self.trend_data.get('items'):
            raise UserError(_('No trend data available. Please generate the report first.'))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Trend Analysis')

        # Formats
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#1e293b', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter',
        })
        number_fmt = workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'border': 1})
        pct_fmt = workbook.add_format({'num_format': '0.0%', 'align': 'right', 'border': 1})
        text_fmt = workbook.add_format({'border': 1, 'align': 'left'})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 14})
        subtitle_fmt = workbook.add_format({'italic': True, 'font_size': 10, 'font_color': '#666666'})
        up_fmt = workbook.add_format({
            'num_format': '#,##0.00', 'align': 'right', 'border': 1,
            'font_color': '#16a34a',
        })
        down_fmt = workbook.add_format({
            'num_format': '#,##0.00', 'align': 'right', 'border': 1,
            'font_color': '#dc2626',
        })
        up_pct_fmt = workbook.add_format({
            'num_format': '0.0%', 'align': 'right', 'border': 1,
            'font_color': '#16a34a',
        })
        down_pct_fmt = workbook.add_format({
            'num_format': '0.0%', 'align': 'right', 'border': 1,
            'font_color': '#dc2626',
        })

        data = self.trend_data

        # Title block
        comparison_label = data.get('comparison_label', self.comparison_type)
        worksheet.write(0, 0, f'Trend Analysis: {comparison_label}', title_fmt)
        worksheet.write(1, 0, f'Company: {data.get("company", self.company_id.name)}', subtitle_fmt)

        current_period = data.get('current_period', {})
        comp_period = data.get('comparison_period', {})
        worksheet.write(2, 0, f'Current Period: {current_period.get("start", "")} to {current_period.get("end", "")}', subtitle_fmt)
        worksheet.write(3, 0, f'Comparison Period: {comp_period.get("start", "")} to {comp_period.get("end", "")}', subtitle_fmt)
        worksheet.write(4, 0, f'Generated: {fields.Datetime.now().strftime("%Y-%m-%d %H:%M")}', subtitle_fmt)
        worksheet.write(5, 0, f'Data Source: {"Snapshots" if self.data_source == "snapshot" else "Real-time"}', subtitle_fmt)

        # Determine which metrics to show based on wizard flags
        metric_defs = []
        if self.show_revenue:
            metric_defs.append(('revenue', 'Revenue'))
        if self.show_cogs:
            metric_defs.append(('cogs', 'COGS'))
        if self.show_gross_profit:
            metric_defs.append(('gross_profit', 'Gross Profit'))
        if self.show_operating_expense:
            metric_defs.append(('operating_expense', 'Operating Expense'))
        if self.show_ebitda:
            metric_defs.append(('ebitda', 'EBITDA'))
        if self.show_net_income:
            metric_defs.append(('net_income', 'Net Income'))

        margin_defs = []
        if self.show_margins:
            margin_defs = [
                ('gross_margin_pct', 'Gross Margin %'),
                ('net_margin_pct', 'Net Margin %'),
            ]

        # Build headers: Dimension | Metric Current | Metric Comparison | Variance | Variance % | ...
        row = 7
        headers = ['Dimension']
        for _key, label in metric_defs:
            headers.extend([
                f'{label} (Current)',
                f'{label} (Comparison)',
                f'{label} (Variance)',
                f'{label} (Change %)',
            ])
        for _key, label in margin_defs:
            headers.extend([
                f'{label} (Current)',
                f'{label} (Comparison)',
                f'{label} (Change pp)',
            ])

        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_fmt)

        # Write data rows
        for item in data.get('items', []):
            row += 1
            # Determine dimension label
            dim_label = item.get('dimension_name', '')
            if not dim_label and item.get('branch_name'):
                dim_label = f"{item.get('branch_name', '')} / {item.get('bu_name', '')}"
            if not dim_label:
                dim_label = item.get('key', 'Total')

            col = 0
            worksheet.write(row, col, dim_label, text_fmt)
            col += 1

            current = item.get('current', {})
            comparison = item.get('comparison', {})
            variance = item.get('variance', {})

            # Monetary metrics
            for metric_key, _label in metric_defs:
                curr_val = current.get(metric_key, 0) or 0
                comp_val = comparison.get(metric_key, 0) or 0
                var_info = variance.get(metric_key, {})
                abs_var = var_info.get('absolute', 0) or 0
                pct_var = (var_info.get('percentage', 0) or 0) / 100.0  # Convert to decimal for Excel %
                direction = var_info.get('direction', 'flat')

                var_fmt = up_fmt if direction == 'up' else (down_fmt if direction == 'down' else number_fmt)
                var_pct = up_pct_fmt if direction == 'up' else (down_pct_fmt if direction == 'down' else pct_fmt)

                worksheet.write(row, col, curr_val, number_fmt)
                worksheet.write(row, col + 1, comp_val, number_fmt)
                worksheet.write(row, col + 2, abs_var, var_fmt)
                worksheet.write(row, col + 3, pct_var, var_pct)
                col += 4

            # Margin metrics (percentage points, not monetary)
            for metric_key, _label in margin_defs:
                curr_val = current.get(metric_key, 0) or 0
                comp_val = comparison.get(metric_key, 0) or 0
                var_info = variance.get(metric_key, {})
                pp_change = var_info.get('absolute', 0) or 0
                direction = var_info.get('direction', 'flat')

                pp_fmt = up_fmt if direction == 'up' else (down_fmt if direction == 'down' else number_fmt)

                worksheet.write(row, col, curr_val / 100.0, pct_fmt)
                worksheet.write(row, col + 1, comp_val / 100.0, pct_fmt)
                worksheet.write(row, col + 2, pp_change, pp_fmt)
                col += 3

        # Summary section
        summary = data.get('summary', {})
        if summary:
            row += 2
            summary_title_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'bottom': 1})
            worksheet.write(row, 0, 'Summary', summary_title_fmt)
            row += 1
            bold_fmt = workbook.add_format({'bold': True})
            worksheet.write(row, 0, 'Total Current Revenue:', bold_fmt)
            worksheet.write(row, 1, summary.get('total_current_revenue', 0), number_fmt)
            row += 1
            worksheet.write(row, 0, 'Total Comparison Revenue:', bold_fmt)
            worksheet.write(row, 1, summary.get('total_comparison_revenue', 0), number_fmt)
            row += 1
            worksheet.write(row, 0, 'Revenue Growth:', bold_fmt)
            worksheet.write(row, 1, (summary.get('revenue_growth_pct', 0) or 0) / 100.0, pct_fmt)
            row += 1
            worksheet.write(row, 0, 'Net Income Growth:', bold_fmt)
            worksheet.write(row, 1, (summary.get('net_income_growth_pct', 0) or 0) / 100.0, pct_fmt)
            row += 1
            worksheet.write(row, 0, 'Items Analyzed:', bold_fmt)
            worksheet.write(row, 1, summary.get('item_count', 0))

        # Auto-fit columns
        worksheet.set_column(0, 0, 28)
        num_cols = len(headers)
        if num_cols > 1:
            worksheet.set_column(1, num_cols - 1, 20)

        workbook.close()

        # Create attachment for download
        file_data = base64.b64encode(output.getvalue())
        safe_name = (self.company_id.name or 'report').replace(' ', '_')
        filename = f'trend_analysis_{safe_name}_{fields.Date.today()}.xlsx'

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': file_data,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
