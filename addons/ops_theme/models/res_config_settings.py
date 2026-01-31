# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Add OPS Theme configuration to General Settings."""

    _inherit = 'res.config.settings'

    # =========================================================================
    # FAVICON
    # =========================================================================

    ops_favicon = fields.Binary(
        related='company_id.ops_favicon',
        readonly=False,
        string='Favicon',
    )

    # =========================================================================
    # THEME PRESET
    # =========================================================================

    ops_theme_preset = fields.Selection(
        related='company_id.ops_theme_preset',
        readonly=False,
        string='Theme Preset',
    )

    # =========================================================================
    # BRAND COLORS
    # =========================================================================

    ops_primary_color = fields.Char(
        related='company_id.ops_primary_color',
        readonly=False,
        string='Primary Color',
    )
    ops_secondary_color = fields.Char(
        related='company_id.ops_secondary_color',
        readonly=False,
        string='Secondary Color',
    )
    ops_success_color = fields.Char(
        related='company_id.ops_success_color',
        readonly=False,
        string='Success Color',
    )
    ops_warning_color = fields.Char(
        related='company_id.ops_warning_color',
        readonly=False,
        string='Warning Color',
    )
    ops_danger_color = fields.Char(
        related='company_id.ops_danger_color',
        readonly=False,
        string='Danger Color',
    )

    # =========================================================================
    # LOGIN PAGE
    # =========================================================================

    ops_login_background = fields.Binary(
        related='company_id.ops_login_background',
        readonly=False,
        string='Login Background Image',
    )
    ops_login_tagline = fields.Char(
        related='company_id.ops_login_tagline',
        readonly=False,
        string='Login Tagline',
    )
    ops_login_show_logo = fields.Boolean(
        related='company_id.ops_login_show_logo',
        readonly=False,
        string='Show Logo on Login',
    )

    # =========================================================================
    # LAYOUT OPTIONS
    # =========================================================================

    ops_navbar_style = fields.Selection(
        related='company_id.ops_navbar_style',
        readonly=False,
        string='Navbar Style',
    )
    ops_card_shadow = fields.Selection(
        related='company_id.ops_card_shadow',
        readonly=False,
        string='Card Shadow',
    )
    ops_border_radius = fields.Selection(
        related='company_id.ops_border_radius',
        readonly=False,
        string='Border Radius',
    )

    # =========================================================================
    # REPORTS
    # =========================================================================

    ops_report_header_bg = fields.Char(
        related='company_id.ops_report_header_bg',
        readonly=False,
        string='Report Header Color',
    )
    ops_report_logo_position = fields.Selection(
        related='company_id.ops_report_logo_position',
        readonly=False,
        string='Report Logo Position',
    )

    # =========================================================================
    # ATTRIBUTION
    # =========================================================================

    ops_powered_by_visible = fields.Boolean(
        related='company_id.ops_powered_by_visible',
        readonly=False,
        string='Show "Powered by OPS Framework"',
    )

    # =========================================================================
    # ACTIONS
    # =========================================================================

    def action_reset_theme_defaults(self):
        """Reset all theme settings to defaults."""
        self.ensure_one()
        self.company_id.write({
            'ops_theme_preset': 'corporate_blue',
            'ops_primary_color': '#1e293b',
            'ops_secondary_color': '#3b82f6',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_favicon': False,
            'ops_login_background': False,
            'ops_login_tagline': 'Enterprise Resource Planning',
            'ops_login_show_logo': True,
            'ops_navbar_style': 'dark',
            'ops_card_shadow': 'medium',
            'ops_border_radius': 'rounded',
            'ops_report_header_bg': '#1e293b',
            'ops_report_logo_position': 'left',
            'ops_powered_by_visible': True,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Theme Reset',
                'message': 'Theme settings have been reset to defaults.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_preview_theme(self):
        """Open a new tab to preview theme changes."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web',
            'target': 'new',
        }
