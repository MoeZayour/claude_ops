from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpsDashboardWidget(models.Model):
    """
    Dashboard Widget - Individual component on a dashboard.
    Can display KPIs, charts, lists, etc.
    """
    _name = 'ops.dashboard.widget'
    _description = 'Dashboard Widget'
    _order = 'sequence, id'

    name = fields.Char(string='Widget Name', required=True)
    dashboard_id = fields.Many2one('ops.dashboard', string='Dashboard',
                                   required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Widget Type
    widget_type = fields.Selection([
        ('kpi', 'KPI Card'),
        ('kpi_group', 'KPI Group'),
        ('bar_chart', 'Bar Chart'),
        ('line_chart', 'Line Chart'),
        ('pie_chart', 'Pie Chart'),
        ('list', 'Top N List'),
        ('metric', 'Single Metric'),
    ], string='Type', required=True, default='kpi')

    # KPI Reference
    kpi_id = fields.Many2one('ops.kpi', string='KPI',
                             help='KPI definition for this widget')
    kpi_ids = fields.Many2many('ops.kpi', string='KPIs',
                               help='Multiple KPIs for group widget')

    # Display Configuration
    title = fields.Char(string='Display Title',
                        help='Override KPI name for display')
    subtitle = fields.Char(string='Subtitle')
    icon = fields.Char(string='Icon Override',
                       help='Override KPI icon')
    color = fields.Char(string='Color Override',
                        help='Override KPI color')

    # Grid Position
    position_x = fields.Integer(string='Column', default=0)
    position_y = fields.Integer(string='Row', default=0)
    width = fields.Integer(string='Width (columns)', default=1)
    height = fields.Integer(string='Height (rows)', default=1)

    # Period Override
    period_override = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('last_30_days', 'Last 30 Days'),
        ('last_90_days', 'Last 90 Days'),
        ('all_time', 'All Time'),
    ], string='Period Override')

    # For List widgets
    list_limit = fields.Integer(string='List Limit', default=5)
    list_model = fields.Char(string='List Model')
    list_fields = fields.Char(string='Display Fields',
                              help='Comma-separated field names')
    list_domain = fields.Char(string='List Domain', default='[]')
    list_order = fields.Char(string='Sort Order', default='id desc')

    def get_widget_data(self, period=None):
        """
        Get data for this widget.
        Returns formatted data ready for frontend display.
        """
        self.ensure_one()

        # Check access through KPI
        if self.kpi_id and not self.kpi_id._check_user_access():
            return None  # Skip this widget

        # Determine period
        widget_period = period or self.period_override or (
            self.kpi_id.default_period if self.kpi_id else 'this_month'
        )

        result = {
            'widget_id': self.id,
            'widget_type': self.widget_type,
            'name': self.title or (self.kpi_id.name if self.kpi_id else self.name),
            'subtitle': self.subtitle,
            'icon': self.icon or (self.kpi_id.icon if self.kpi_id else 'fa-chart-bar'),
            'color': self.color or (self.kpi_id.color if self.kpi_id else '#3b82f6'),
            'position': {
                'x': self.position_x,
                'y': self.position_y,
                'w': self.width,
                'h': self.height,
            },
        }

        if self.widget_type == 'kpi' and self.kpi_id:
            # Single KPI
            kpi_data = self.env['ops.kpi.value'].compute_kpi_value(
                self.kpi_id, period=widget_period
            )
            result.update(kpi_data)

        elif self.widget_type == 'kpi_group' and self.kpi_ids:
            # Multiple KPIs
            kpis_data = []
            for kpi in self.kpi_ids:
                if kpi._check_user_access():
                    kpi_data = self.env['ops.kpi.value'].compute_kpi_value(
                        kpi, period=widget_period
                    )
                    if not kpi_data.get('error'):
                        kpis_data.append(kpi_data)
            result['kpis'] = kpis_data

        elif self.widget_type == 'list':
            # Top N List
            result['list_data'] = self._get_list_data()

        elif self.widget_type in ('bar_chart', 'line_chart', 'pie_chart'):
            # Chart data - placeholder for now
            result['chart_data'] = {'labels': [], 'values': []}

        return result

    def _get_list_data(self):
        """Get data for list widget."""
        if not self.list_model or self.list_model not in self.env:
            return []

        Model = self.env[self.list_model]

        from odoo.tools.safe_eval import safe_eval
        from .ops_kpi_value import _get_safe_eval_context
        eval_context = _get_safe_eval_context(self.env)
        base_domain = safe_eval(self.list_domain, eval_context) if self.list_domain else []

        # Apply branch isolation if model has ops_branch_id
        user = self.env.user
        if 'ops_branch_id' in Model._fields:
            if not user.has_group('ops_matrix_core.group_ops_manager'):
                branch_ids = user.ops_allowed_branch_ids.ids if hasattr(user, 'ops_allowed_branch_ids') else []
                if branch_ids:
                    base_domain.append(('ops_branch_id', 'in', branch_ids))

        # Company filter
        if 'company_id' in Model._fields:
            base_domain.append(('company_id', 'in', self.env.companies.ids))

        records = Model.search(
            base_domain,
            limit=self.list_limit or 5,
            order=self.list_order or 'id desc'
        )

        display_fields = (self.list_fields or 'name').split(',')
        result = []
        for rec in records:
            row = {'id': rec.id}
            for field in display_fields:
                field = field.strip()
                if hasattr(rec, field):
                    val = getattr(rec, field)
                    if hasattr(val, 'name'):
                        val = val.name
                    elif hasattr(val, 'display_name'):
                        val = val.display_name
                    row[field] = val
            result.append(row)

        return result

    @api.model
    def cron_refresh_dashboard_data(self):
        """
        Refresh data for all active widgets.
        Called by scheduled cron job to pre-compute widget data.
        """
        widgets = self.search([('active', '=', True)])
        _logger.info(f"Cron: Refreshing data for {len(widgets)} active dashboard widgets")

        success_count = 0
        error_count = 0
        for widget in widgets:
            try:
                widget.get_widget_data()
                success_count += 1
            except Exception as e:
                error_count += 1
                _logger.error(f"Error refreshing widget '{widget.name}' (ID: {widget.id}): {e}")

        _logger.info(f"Cron: Dashboard refresh complete. Success: {success_count}, Errors: {error_count}")
        return True
