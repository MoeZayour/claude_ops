# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompanyBranding(models.Model):
    _inherit = 'res.company'

    ops_primary_color = fields.Char(
        string='Primary Brand Color',
        default='#1e293b',
        help='Hex color code for report headers and accents (e.g., #1e293b)',
    )
    ops_show_external_badge = fields.Boolean(
        string='Show OPS Badge on Reports',
        default=True,
        help='Display "Powered by OPS Framework" badge on external documents',
    )
