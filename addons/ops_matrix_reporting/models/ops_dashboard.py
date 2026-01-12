# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json

class OpsDashboard(models.Model):
    _name = 'ops.dashboard'
    _description = 'OPS Dashboard'
    _order = 'sequence, id'

    name = fields.Char(string='Dashboard Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
    widget_ids = fields.One2many('ops.dashboard.widget', 'dashboard_id', string='Widgets')
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def get_dashboard_data(self):
        self.ensure_one()
        widgets_data = []
        for widget in self.widget_ids:
            widgets_data.append(widget.get_widget_data())
        return {
            'name': self.name,
            'widgets': widgets_data,
        }

class OpsDashboardWidget(models.Model):
    _name = 'ops.dashboard.widget'
    _description = 'OPS Dashboard Widget'
    _order = 'sequence, id'

    name = fields.Char(string='Widget Name', required=True, translate=True)
    dashboard_id = fields.Many2one('ops.dashboard', string='Dashboard', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    
    widget_type = fields.Selection([
        ('kpi', 'KPI Card'),
        ('chart_bar', 'Bar Chart'),
        ('chart_line', 'Line Chart'),
        ('chart_pie', 'Pie Chart'),
        ('list', 'Data List'),
    ], string='Widget Type', required=True, default='kpi')

    data_source_model = fields.Char(string='Source Model', required=True)
    data_source_method = fields.Char(string='Source Method', help="Method to call on the model to get data")
    
    domain = fields.Text(string='Domain', default='[]')
    context = fields.Text(string='Context', default='{}')
    
    config = fields.Text(string='Configuration (JSON)', default='{}')
    
    # Layout
    col_span = fields.Integer(string='Column Span', default=3, help="Width in grid columns (1-12)")
    row_span = fields.Integer(string='Row Span', default=1)
    icon = fields.Char(string='Icon', default='fa-dashboard')

    def get_widget_data(self):
        self.ensure_one()
        # This method will be called by the JS to fetch data for this specific widget
        
        data = {
            'id': self.id,
            'name': self.name,
            'type': self.widget_type,
            'col_span': self.col_span,
            'row_span': self.row_span,
            'config': json.loads(self.config or '{}'),
        }
        if 'icon' not in data['config']:
            data['config']['icon'] = self.icon
        
        # Fetch actual data
        try:
            model = self.env[self.data_source_model]
            if self.data_source_method and hasattr(model, self.data_source_method):
                method = getattr(model, self.data_source_method)
                # Call method
                data['value'] = method()
            else:
                # Default behavior: count - use safe_eval to prevent code injection
                domain = safe_eval(self.domain or '[]')
                data['value'] = model.search_count(domain)
        except Exception as e:
            data['error'] = str(e)
            data['value'] = 0
            
        return data
            
