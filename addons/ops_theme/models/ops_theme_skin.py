# -*- coding: utf-8 -*-
"""
OPS Theme Skin Model
====================
Database-driven theme presets following OPS Design Guide v1.0.
10 colors + 1 navbar style per skin.
"""

from odoo import fields, models


class OpsThemeSkin(models.Model):
    """Theme skin preset for OPS Theme."""

    _name = 'ops.theme.skin'
    _description = 'OPS Theme Skin'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    tag = fields.Char(help="Short tag/category displayed in the selector (e.g. 'Corporate', 'Minimal').")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Identity Colors (Group 1)
    brand_color = fields.Char(string="Brand Color", required=True, default="#1e293b",
                              help="Navbar background, sidebar, headings accent.")
    action_color = fields.Char(string="Action Color", required=True, default="#3b82f6",
                               help="Buttons, links, focus rings, selected items.")

    # Semantic Colors (Group 2)
    success_color = fields.Char(default="#10b981")
    warning_color = fields.Char(default="#f59e0b")
    danger_color = fields.Char(default="#ef4444")
    info_color = fields.Char(default="#06b6d4")

    # Canvas Colors (Group 3)
    bg_color = fields.Char(string="Background", required=True, default="#f1f5f9")
    surface_color = fields.Char(string="Surface", required=True, default="#ffffff")
    text_color = fields.Char(string="Text", required=True, default="#1e293b")
    border_color = fields.Char(string="Border", required=True, default="#e2e8f0")

    # Structural
    navbar_style = fields.Selection([
        ('dark', 'Dark'),
        ('light', 'Light'),
        ('primary', 'Primary Color'),
    ], string="Navbar Style", default='dark', required=True)
