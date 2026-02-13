# -*- coding: utf-8 -*-
"""
OPS KPI Center — Company-Level Display Settings
=================================================
KPI visual preferences stored per-company.
"""

from odoo import fields, models


class ResCompanyKpi(models.Model):
    """Extend res.company with KPI Center display preferences."""

    _inherit = 'res.company'

    # =========================================================================
    # KPI DISPLAY SETTINGS
    # =========================================================================
    ops_kpi_gradient_headers = fields.Boolean(
        string='Gradient Section Headers',
        default=True,
        help='Use gradient backgrounds on chart section headers in KPI Center.',
    )
    ops_kpi_sparkline_style = fields.Selection(
        selection=[
            ('gradient', 'Gradient Fill'),
            ('line', 'Line Only'),
            ('bar', 'Mini Bar'),
        ],
        string='Sparkline Style',
        default='gradient',
        help='Visual style for mini-charts inside KPI cards.',
    )
    ops_kpi_chart_fill = fields.Selection(
        selection=[
            ('gradient', 'Gradient Fill'),
            ('solid', 'Solid Fill'),
            ('none', 'No Fill (Line Only)'),
        ],
        string='Chart Area Fill',
        default='gradient',
        help='Fill style for area and trend charts.',
    )
    ops_kpi_animation = fields.Selection(
        selection=[
            ('full', 'Full Animations'),
            ('reduced', 'Reduced Motion'),
            ('none', 'No Animations'),
        ],
        string='Chart Animation',
        default='full',
        help='Animation level for chart rendering and transitions.',
    )
    ops_kpi_card_style = fields.Selection(
        selection=[
            ('accent', 'Left Accent Bar'),
            ('shadow', 'Elevated Shadow'),
            ('border', 'Subtle Border'),
        ],
        string='KPI Card Style',
        default='accent',
        help='Visual style for individual KPI cards.',
    )
    ops_kpi_color_scheme = fields.Selection(
        selection=[
            ('default', 'OPS Default'),
            ('vibrant', 'Vibrant'),
            ('muted', 'Muted / Pastel'),
            ('monochrome', 'Monochrome'),
        ],
        string='Chart Color Scheme',
        default='default',
        help='Color palette used for charts and visualizations.',
    )
    ops_kpi_refresh_interval = fields.Integer(
        string='Default Refresh Interval (seconds)',
        default=120,
        help='Auto-refresh interval for KPI dashboards. Set 0 to disable.',
    )
