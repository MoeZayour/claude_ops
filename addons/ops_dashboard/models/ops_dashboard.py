from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class OpsDashboard(models.Model):
    """
    Dashboard Definition - Container for widgets/KPIs.
    Each dashboard targets specific personas.
    """
    _name = 'ops.dashboard'
    _description = 'OPS Dashboard'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(string='Dashboard Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, index=True,
                       help='Unique identifier: EXEC, BRANCH, SALES')
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Targeting
    dashboard_type = fields.Selection([
        ('executive', 'Executive Dashboard'),
        ('branch', 'Branch Dashboard'),
        ('bu', 'Business Unit Dashboard'),
        ('sales', 'Sales Dashboard'),
        ('purchase', 'Purchase Dashboard'),
        ('finance', 'Finance Dashboard'),
        ('inventory', 'Inventory Dashboard'),
        ('custom', 'Custom Dashboard'),
    ], string='Type', required=True, default='custom')

    # Persona Access
    persona_ids = fields.Many2many('ops.persona', string='Target Personas',
                                   help='Which personas can view this dashboard')
    group_ids = fields.Many2many('res.groups', string='Access Groups',
                                 help='Additional groups that can view this dashboard')

    # Widgets
    widget_ids = fields.One2many('ops.dashboard.widget', 'dashboard_id', string='Widgets')
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

    def _check_access(self):
        """Check if current user can access this dashboard."""
        user = self.env.user
        self.ensure_one()

        # System admin always has access
        if user.has_group('base.group_system'):
            return True

        # Check group access
        if self.group_ids:
            user_groups = user.groups_id
            if self.group_ids & user_groups:
                return True

        # Check persona access
        if self.persona_ids and hasattr(user, 'ops_persona_id'):
            if user.ops_persona_id in self.persona_ids:
                return True

        # Default: allow if no restrictions set
        if not self.group_ids and not self.persona_ids:
            return True

        return False

    @api.model
    def get_user_dashboards(self):
        """Get dashboards accessible to current user."""
        user = self.env.user

        # IT Admin gets no business dashboards
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            return []  # Return empty list for JSON serialization

        dashboards = self.search([('active', '=', True)])
        accessible = dashboards.filtered(lambda d: d._check_access())
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

        if not dashboard._check_access():
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
