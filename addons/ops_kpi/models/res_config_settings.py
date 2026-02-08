# -*- coding: utf-8 -*-
"""
OPS KPI Center — Configuration Settings
=========================================
Settings UI for KPI Center visual customization.
"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """KPI Center settings in General Settings."""

    _inherit = 'res.config.settings'

    # =========================================================================
    # KPI DISPLAY SETTINGS (related to res.company)
    # =========================================================================
    ops_kpi_gradient_headers = fields.Boolean(
        related='company_id.ops_kpi_gradient_headers',
        readonly=False,
    )
    ops_kpi_sparkline_style = fields.Selection(
        related='company_id.ops_kpi_sparkline_style',
        readonly=False,
    )
    ops_kpi_chart_fill = fields.Selection(
        related='company_id.ops_kpi_chart_fill',
        readonly=False,
    )
    ops_kpi_animation = fields.Selection(
        related='company_id.ops_kpi_animation',
        readonly=False,
    )
    ops_kpi_card_style = fields.Selection(
        related='company_id.ops_kpi_card_style',
        readonly=False,
    )
    ops_kpi_color_scheme = fields.Selection(
        related='company_id.ops_kpi_color_scheme',
        readonly=False,
    )
    ops_kpi_refresh_interval = fields.Integer(
        related='company_id.ops_kpi_refresh_interval',
        readonly=False,
    )
