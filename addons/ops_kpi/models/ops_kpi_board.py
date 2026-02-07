from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class OpsKpiBoard(models.Model):
    """
    KPI Board Definition - Container for widgets/KPIs.
    Each board targets specific personas.
    """
    _name = 'ops.kpi.board'
    _description = 'OPS KPI Board'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(string='Dashboard Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, index=True,
                       help='Unique identifier: EXEC, BRANCH, SALES')
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Dashboard Type - Extended for enterprise
    dashboard_type = fields.Selection([
        ('executive', 'Executive'),
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('purchase', 'Purchase'),
        ('inventory', 'Inventory'),
        ('receivable', 'Receivables'),
        ('payable', 'Payables'),
        ('treasury', 'Treasury'),
        ('branch', 'Branch'),
        ('bu', 'Business Unit'),
        ('system', 'System'),
        ('custom', 'Custom'),
    ], string='Type', required=True, default='custom')

    # Persona Access - Enhanced for enterprise
    persona_ids = fields.Many2many('ops.persona', string='Target Personas',
                                   help='Which personas can view this dashboard')
    persona_codes = fields.Char(
        string='Persona Codes',
        help='Comma-separated persona codes: P01,P02,P03. Alternative to persona_ids.'
    )
    group_ids = fields.Many2many('res.groups', string='Access Groups',
                                 help='Additional groups that can view this dashboard')

    # Widgets
    widget_ids = fields.One2many('ops.kpi.widget', 'board_id', string='Widgets')
    widget_count = fields.Integer(compute='_compute_widget_count')

    # Display Settings
    auto_refresh = fields.Boolean(string='Auto Refresh', default=True)
    refresh_interval = fields.Selection([
        ('30000', '30 Seconds'),
        ('60000', '1 Minute'),
        ('120000', '2 Minutes'),
        ('300000', '5 Minutes'),
        ('600000', '10 Minutes'),
        ('0', 'Manual Only'),
    ], string='Refresh Interval', default='120000')

    columns = fields.Integer(string='Grid Columns', default=4,
                            help='Number of columns in the grid layout')

    # Alert & Chart Configuration
    alert_threshold = fields.Float(
        string='Alert Threshold (%)', default=-10.0,
        help='KPI change percentage below which an alert is triggered')
    chart_kpi_codes = fields.Char(
        string='Chart KPI Codes',
        default='SALES_TOTAL,REVENUE_MTD,SALES_MTD',
        help='Comma-separated KPI codes to display in the main chart')

    # Company
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    _code_company_unique = models.Constraint(
        'unique(code, company_id)',
        'Dashboard code must be unique per company!',
    )

    @api.depends('widget_ids')
    def _compute_widget_count(self):
        for dashboard in self:
            dashboard.widget_count = len(dashboard.widget_ids)

    def _check_user_dashboard_access(self):
        """
        Check if current user can access this dashboard.
        Checks: system admin, IT admin blindness, persona codes, groups.
        """
        user = self.env.user
        self.ensure_one()

        # System admin always has access
        if user.has_group('base.group_system'):
            return True

        # IT Admin can ONLY see system dashboards
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            return self.dashboard_type == 'system'

        # Check persona_codes first (comma-separated string)
        if self.persona_codes:
            allowed_codes = [p.strip() for p in self.persona_codes.split(',') if p.strip()]
            user_personas = []
            if hasattr(user, 'ops_persona_ids'):
                user_personas = user.ops_persona_ids.mapped('code')
            if allowed_codes and any(p in allowed_codes for p in user_personas):
                return True

        # Check persona_ids (Many2many)
        if self.persona_ids:
            if hasattr(user, 'persona_id') and user.persona_id in self.persona_ids:
                return True
            if hasattr(user, 'ops_persona_ids') and (user.ops_persona_ids & self.persona_ids):
                return True

        # Check group access
        if self.group_ids:
            user_groups = user.groups_id
            if self.group_ids & user_groups:
                return True

        # Default: allow if no restrictions set
        if not self.group_ids and not self.persona_ids and not self.persona_codes:
            return True

        return False

    @api.model
    def get_user_dashboards(self):
        """Get dashboards accessible to current user."""
        user = self.env.user

        # IT Admin gets only system dashboards
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            dashboards = self.search([
                ('active', '=', True),
                ('dashboard_type', '=', 'system')
            ])
            return dashboards.read(['id', 'name', 'code', 'dashboard_type'])

        dashboards = self.search([('active', '=', True)])
        accessible = dashboards.filtered(lambda d: d._check_user_dashboard_access())
        return accessible.read(['id', 'name', 'code', 'dashboard_type'])

    @api.model
    def get_dashboard_data(self, dashboard_id, period=None):
        """
        Main RPC method to fetch dashboard data.
        Returns all widget data for the dashboard.
        """
        dashboard = self.browse(dashboard_id)

        if not dashboard.exists():
            return {'error': 'Dashboard not found'}

        if not dashboard._check_user_dashboard_access():
            return {'error': 'Access Denied'}

        # Collect widget data
        widgets_data = []
        for widget in dashboard.widget_ids.sorted('sequence'):
            widget_data = widget.get_widget_data(period=period)
            if widget_data and not widget_data.get('error'):
                widgets_data.append(widget_data)

        return {
            'dashboard_id': dashboard.id,
            'dashboard_name': dashboard.name,
            'dashboard_type': dashboard.dashboard_type,
            'refresh_interval': int(dashboard.refresh_interval or 0),
            'columns': dashboard.columns,
            'widgets': widgets_data,
        }

    @api.model
    def get_company_currency_info(self):
        """
        Get the current user's company currency information.
        Returns symbol, position, and code for frontend formatting.
        """
        company = self.env.company
        currency = company.currency_id

        if currency:
            return {
                'symbol': currency.symbol or '$',
                'position': currency.position or 'before',
                'code': currency.name or 'USD',
            }

        # Fallback defaults
        return {
            'symbol': '$',
            'position': 'before',
            'code': 'USD',
        }

    @api.model
    def get_chart_data(self, dashboard_id, period='this_month'):
        """
        Get all chart data for a dashboard including time series and breakdowns.
        This is the main RPC method for the enhanced dashboard with charts.

        Returns structured data for:
        - KPI cards with sparkline data
        - Area charts (trends)
        - Bar charts (branch comparisons)
        - Donut charts (breakdowns)
        - Alerts
        """
        dashboard = self.browse(dashboard_id)

        if not dashboard.exists():
            return {'error': 'Dashboard not found'}

        if not dashboard._check_user_dashboard_access():
            return {'error': 'Access Denied'}

        result = {
            'dashboard_id': dashboard.id,
            'dashboard_name': dashboard.name,
            'dashboard_type': dashboard.dashboard_type,
            'refresh_interval': int(dashboard.refresh_interval or 0),
            'period': period,
            'kpi_cards': [],
            'trend_charts': [],
            'breakdown_charts': [],
            'comparison_charts': [],
            'alerts': [],
            'filters': {
                'branches': [],
                'business_units': [],
            },
        }

        # Get filter options
        user = self.env.user
        if hasattr(user, 'ops_allowed_branch_ids') and user.ops_allowed_branch_ids:
            result['filters']['branches'] = user.ops_allowed_branch_ids.read(['id', 'name'])
        else:
            branches = self.env['ops.branch'].search([('active', '=', True)])
            result['filters']['branches'] = branches.read(['id', 'name'])

        # Process each widget
        for widget in dashboard.widget_ids.sorted('sequence'):
            widget_data = widget.get_widget_data(period=period)
            if widget_data and not widget_data.get('error'):
                kpi = widget.kpi_id

                # Add sparkline data for KPI cards
                if kpi:
                    sparkline = kpi.get_time_series(period=period, granularity='day')
                    widget_data['sparkline_data'] = sparkline.get('data', [])

                    # Check for comparison data
                    comparison = kpi.get_comparison(period=period)
                    if comparison and not comparison.get('error'):
                        widget_data['comparison'] = comparison

                result['kpi_cards'].append(widget_data)

        # Generate trend charts from revenue/sales KPIs
        chart_codes = [c.strip() for c in (dashboard.chart_kpi_codes or 'SALES_REVENUE_MTD,SALES_ORDERS_MTD').split(',') if c.strip()]
        trend_kpis = self.env['ops.kpi'].search([
            ('code', 'in', chart_codes),
            ('active', '=', True),
        ])

        for kpi in trend_kpis:
            if kpi._check_user_access():
                trend_data = kpi.get_time_series(period=period, granularity='day')
                if trend_data.get('data'):
                    result['trend_charts'].append({
                        'kpi_id': kpi.id,
                        'kpi_code': kpi.code,
                        'title': kpi.name,
                        'data': trend_data['data'],
                        'color': kpi.color,
                        'format_type': kpi.format_type,
                    })

        # Generate breakdown charts (branch comparison)
        breakdown_codes = chart_codes + ['AR_TOTAL']
        breakdown_kpis = self.env['ops.kpi'].search([
            ('code', 'in', breakdown_codes),
            ('active', '=', True),
        ])

        for kpi in breakdown_kpis:
            if kpi._check_user_access():
                Model = self.env.get(kpi.source_model)
                if Model is None:
                    continue

                # Try ops_branch_id first, then company_id as fallback
                if 'ops_branch_id' in Model._fields:
                    gb_field = 'ops_branch_id'
                    gb_label = 'Branch'
                elif 'company_id' in Model._fields:
                    gb_field = 'company_id'
                    gb_label = 'Company'
                else:
                    continue

                breakdown_data = kpi.get_breakdown(period=period, group_by=gb_field)
                if breakdown_data.get('data'):
                    result['breakdown_charts'].append({
                        'kpi_id': kpi.id,
                        'kpi_code': kpi.code,
                        'title': f'{kpi.name} by {gb_label}',
                        'data': breakdown_data['data'],
                        'group_by': gb_field,
                        'format_type': kpi.format_type,
                    })

        # Generate alerts from KPIs with negative trends or thresholds
        alert_threshold = dashboard.alert_threshold or -10.0
        for widget_data in result['kpi_cards']:
            trend_pct = widget_data.get('trend_percentage', 0)
            trend_is_good = widget_data.get('trend_is_good', True)

            if not trend_is_good and trend_pct != 0:
                severity = 'critical' if trend_pct < -20 else 'warning'
                result['alerts'].append({
                    'kpi_id': widget_data.get('kpi_id'),
                    'title': widget_data.get('name'),
                    'message': f'{abs(trend_pct):.1f}% {"decrease" if trend_pct < 0 else "increase"} vs previous period',
                    'severity': severity,
                    'value': widget_data.get('value'),
                    'formatted_value': widget_data.get('formatted_value'),
                    'positive': False,
                })
            elif trend_is_good and trend_pct > 15:
                result['alerts'].append({
                    'kpi_id': widget_data.get('kpi_id'),
                    'title': widget_data.get('name'),
                    'message': f'{trend_pct:.1f}% {"increase" if trend_pct > 0 else "decrease"} vs previous period',
                    'severity': 'success',
                    'value': widget_data.get('value'),
                    'formatted_value': widget_data.get('formatted_value'),
                    'positive': True,
                })

        return result

    @api.model
    def get_kpi_chart_data(self, kpi_id, chart_type, period='this_month', group_by=None):
        """
        Get specific chart data for a single KPI.
        Used for drill-down and detailed views.

        Args:
            kpi_id: ID of the KPI
            chart_type: 'time_series', 'breakdown', 'comparison'
            period: Time period
            group_by: Field to group by (for breakdown)

        Returns:
            Chart data specific to the requested type
        """
        kpi = self.env['ops.kpi'].browse(kpi_id)

        if not kpi.exists():
            return {'error': 'KPI not found'}

        if not kpi._check_user_access():
            return {'error': 'Access Denied'}

        if chart_type == 'time_series':
            return kpi.get_time_series(period=period)
        elif chart_type == 'breakdown':
            group_by = group_by or 'ops_branch_id'
            return kpi.get_breakdown(period=period, group_by=group_by)
        elif chart_type == 'comparison':
            return kpi.get_comparison(period=period)
        else:
            return {'error': f'Unknown chart type: {chart_type}'}
