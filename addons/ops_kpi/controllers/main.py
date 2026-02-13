# -*- coding: utf-8 -*-
"""
OPS KPI Center — Controllers
==============================
HTTP endpoints for KPI Center display settings.
"""

from odoo import http
from odoo.http import request


class OpsKpiController(http.Controller):
    """KPI Center controller for display settings."""

    @http.route('/ops_kpi/display_settings', type='json', auth='user')
    def get_display_settings(self):
        """Return KPI display settings for current company."""
        company = request.env.company
        return {
            'gradient_headers': company.ops_kpi_gradient_headers if hasattr(company, 'ops_kpi_gradient_headers') else True,
            'sparkline_style': company.ops_kpi_sparkline_style if hasattr(company, 'ops_kpi_sparkline_style') else 'gradient',
            'chart_fill': company.ops_kpi_chart_fill if hasattr(company, 'ops_kpi_chart_fill') else 'gradient',
            'animation': company.ops_kpi_animation if hasattr(company, 'ops_kpi_animation') else 'full',
            'card_style': company.ops_kpi_card_style if hasattr(company, 'ops_kpi_card_style') else 'accent',
            'color_scheme': company.ops_kpi_color_scheme if hasattr(company, 'ops_kpi_color_scheme') else 'default',
            'refresh_interval': company.ops_kpi_refresh_interval if hasattr(company, 'ops_kpi_refresh_interval') else 120,
        }
