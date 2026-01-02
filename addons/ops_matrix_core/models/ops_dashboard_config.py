# -*- coding: utf-8 -*-
"""OPS Dashboard Configuration Model for user-specific dashboard preferences."""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsDashboardConfig(models.TransientModel):
    """Model for configuring dashboard settings."""
    
    _name = 'ops.dashboard.config'
    _description = 'OPS Dashboard Configuration'
    
    # User Preferences
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True
    )
    
    # Dashboard Layout
    dashboard_layout = fields.Selection([
        ('standard', 'Standard (3 columns)'),
        ('wide', 'Wide (2 columns)'),
        ('compact', 'Compact (4 columns)'),
    ], string='Dashboard Layout', default='standard')
    
    # Default Date Range
    default_date_range = fields.Selection([
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('quarter', 'This Quarter'),
        ('year', 'This Year'),
        ('custom', 'Custom'),
    ], string='Default Date Range', default='month')
    
    # Matrix Display Options
    show_branch_first = fields.Boolean(
        string='Show Branch Before BU',
        default=True,
        help='Display Branch then BU (vs BU then Branch)'
    )
    
    include_inactive_dimensions = fields.Boolean(
        string='Include Inactive Dimensions',
        default=False,
        help='Show data for inactive branches/BUs'
    )
    
    # Color Scheme
    color_scheme = fields.Selection([
        ('corporate', 'Corporate (Blue)'),
        ('financial', 'Financial (Green)'),
        ('sales', 'Sales (Orange)'),
        ('inventory', 'Inventory (Purple)'),
        ('custom', 'Custom Colors'),
    ], string='Color Scheme', default='corporate')
    
    # Custom Colors
    primary_color = fields.Char(string='Primary Color', default='#1f77b4')
    secondary_color = fields.Char(string='Secondary Color', default='#ff7f0e')
    success_color = fields.Char(string='Success Color', default='#2ca02c')
    warning_color = fields.Char(string='Warning Color', default='#d62728')
    
    # Widget Configuration
    enabled_widgets = fields.Many2many(
        'ops.dashboard.widget',
        string='Enabled Widgets',
        help='Widgets to display on the dashboard'
    )
    
    widget_positions = fields.Json(
        string='Widget Positions',
        help='JSON storing widget positions on dashboard'
    )
    
    # Performance Settings
    cache_duration = fields.Integer(
        string='Cache Duration (minutes)',
        default=15,
        help='How long to cache dashboard data'
    )
    
    auto_refresh = fields.Boolean(
        string='Auto Refresh',
        default=True,
        help='Automatically refresh dashboard data'
    )
    
    refresh_interval = fields.Integer(
        string='Refresh Interval (seconds)',
        default=300,
        help='Seconds between auto-refresh'
    )
    
    # Methods
    def action_save_configuration(self):
        """Save dashboard configuration for user."""
        self.ensure_one()
        
        # Store configuration in user preferences
        config_data = {
            'dashboard_layout': self.dashboard_layout,
            'default_date_range': self.default_date_range,
            'show_branch_first': self.show_branch_first,
            'include_inactive_dimensions': self.include_inactive_dimensions,
            'color_scheme': self.color_scheme,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'success_color': self.success_color,
            'warning_color': self.warning_color,
            'cache_duration': self.cache_duration,
            'auto_refresh': self.auto_refresh,
            'refresh_interval': self.refresh_interval,
        }
        
        # Save to user
        self.user_id.write({
            'ops_dashboard_config': config_data
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration Saved'),
                'message': _('Dashboard configuration saved successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_reset_to_defaults(self):
        """Reset dashboard configuration to defaults."""
        self.ensure_one()
        
        default_values = {
            'dashboard_layout': 'standard',
            'default_date_range': 'month',
            'show_branch_first': True,
            'include_inactive_dimensions': False,
            'color_scheme': 'corporate',
            'primary_color': '#1f77b4',
            'secondary_color': '#ff7f0e',
            'success_color': '#2ca02c',
            'warning_color': '#d62728',
            'cache_duration': 15,
            'auto_refresh': True,
            'refresh_interval': 300,
        }
        
        self.write(default_values)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reset to Defaults'),
                'message': _('Dashboard configuration reset to defaults.'),
                'type': 'info',
                'sticky': False,
            }
        }
