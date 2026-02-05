# -*- coding: utf-8 -*-
"""
OPS Theme - Configuration Settings
===================================
Expose OPS Theme settings in General Settings.
"""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose OPS Theme settings in General Settings."""

    _inherit = 'res.config.settings'

    # OPS Theme Settings (related to company)
    ops_primary_color = fields.Char(
        related='company_id.ops_primary_color',
        readonly=False,
        string='Primary Brand Color')

    ops_amount_words_lang = fields.Selection(
        related='company_id.ops_amount_words_lang',
        readonly=False,
        string='Amount in Words Language')

    ops_show_external_badge = fields.Boolean(
        related='company_id.ops_show_external_badge',
        readonly=False,
        string='Show OPS Framework Badge')
