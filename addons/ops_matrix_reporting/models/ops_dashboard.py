# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json


class OpsDashboard(models.Model):
    """OPS Dashboard model for organizing widgets into cohesive dashboards."""
    _name = 'ops.dashboard'
    _description = 'OPS Dashboard'
    _order = 'sequence, id'

    name = fields.Char(string='Dashboard Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
    widget_ids = fields.One2many('ops.dashboard.widget', 'dashboard_id', string='Widgets')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def get_dashboard_data(self, dashboard_id=None):
        """
        Get dashboard data for the JS client.
        Can be called either on a recordset (self) or with dashboard_id parameter.
        """
        if dashboard_id:
            dashboard = self.browse(dashboard_id)
        elif self:
            dashboard = self[0]
        else:
            return {'name': 'No Dashboard', 'widgets': []}

        if not dashboard.exists():
            return {'name': 'Dashboard Not Found', 'widgets': []}

        widgets_data = []
        for widget in dashboard.widget_ids:
            widgets_data.append(widget.get_dashboard_widget_data())
        return {
            'id': dashboard.id,
            'name': dashboard.name,
            'widgets': widgets_data,
        }


class OpsDashboardWidgetExtension(models.Model):
    """
    Extends ops.dashboard.widget from ops_matrix_core to add dashboard integration.
    The base model is defined in ops_matrix_core with standalone widget capabilities.
    This extension adds dashboard_id linking and dashboard-specific rendering.
    """
    _inherit = 'ops.dashboard.widget'

    # Dashboard Integration Fields
    dashboard_id = fields.Many2one('ops.dashboard', string='Dashboard', ondelete='cascade')

    # Extended widget types for dashboard rendering
    widget_type = fields.Selection(
        selection_add=[
            ('chart_bar', 'Bar Chart'),
            ('chart_line', 'Line Chart'),
            ('chart_pie', 'Pie Chart'),
            ('list', 'Data List'),
        ],
        ondelete={
            'chart_bar': 'set kpi',
            'chart_line': 'set kpi',
            'chart_pie': 'set kpi',
            'list': 'set kpi',
        }
    )

    # Dashboard-specific source configuration
    data_source_model = fields.Char(string='Source Model')
    data_source_method = fields.Char(string='Source Method', help="Method to call on the model to get data")
    context = fields.Text(string='Context', default='{}')
    config = fields.Text(string='Configuration (JSON)', default='{}')

    # Layout for dashboard grid
    col_span = fields.Integer(string='Column Span', default=3, help="Width in grid columns (1-12)")
    row_span = fields.Integer(string='Row Span', default=1)

    def get_dashboard_widget_data(self):
        """Get data for dashboard widget rendering."""
        self.ensure_one()

        data = {
            'id': self.id,
            'name': self.name,
            'type': self.widget_type,
            'col_span': self.col_span,
            'row_span': self.row_span,
            'config': json.loads(self.config or '{}'),
        }
        if 'icon' not in data['config']:
            data['config']['icon'] = self.icon or 'fa-dashboard'

        # Fetch actual data using data_source_model if specified
        try:
            source_model = self.data_source_model or self.model_name
            if source_model:
                model = self.env[source_model]
                if self.data_source_method and hasattr(model, self.data_source_method):
                    method = getattr(model, self.data_source_method)
                    data['value'] = method()
                else:
                    # Default behavior: count - use safe_eval to prevent code injection
                    domain_str = self.domain if self.domain else '[]'
                    domain = safe_eval(domain_str)
                    data['value'] = model.search_count(domain)
            else:
                data['value'] = 0
        except Exception as e:
            data['error'] = str(e)
            data['value'] = 0

        return data
