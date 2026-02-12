# -*- coding: utf-8 -*-
"""
OPS Theme - Configuration Settings
===================================
Full settings UI for theme customization. Light-only skin system.
"""

from odoo import api, fields, models

# Default layout colors (Corporate Blue)
LIGHT_LAYOUT_DEFAULTS = {
    'bg': '#f1f5f9',
    'surface': '#ffffff',
    'text': '#1e293b',
    'border': '#e2e8f0',
}


class ResConfigSettings(models.TransientModel):
    """OPS Theme settings in General Settings."""

    _inherit = 'res.config.settings'

    # =========================================================================
    # THEME PRESET
    # =========================================================================
    ops_theme_skin_id = fields.Many2one(
        related='company_id.ops_theme_skin_id',
        readonly=False,
    )
    # Deprecated — kept for backwards compat
    ops_theme_preset = fields.Selection(
        related='company_id.ops_theme_preset',
        readonly=False,
    )

    # =========================================================================
    # BRAND COLORS (10 skin colors)
    # =========================================================================
    ops_primary_color = fields.Char(
        related='company_id.ops_primary_color',
        readonly=False,
    )
    ops_secondary_color = fields.Char(
        related='company_id.ops_secondary_color',
        readonly=False,
    )
    ops_success_color = fields.Char(
        related='company_id.ops_success_color',
        readonly=False,
    )
    ops_warning_color = fields.Char(
        related='company_id.ops_warning_color',
        readonly=False,
    )
    ops_danger_color = fields.Char(
        related='company_id.ops_danger_color',
        readonly=False,
    )
    ops_info_color = fields.Char(
        related='company_id.ops_info_color',
        readonly=False,
    )

    # =========================================================================
    # CANVAS COLORS
    # =========================================================================
    ops_bg_color = fields.Char(
        related='company_id.ops_bg_color',
        readonly=False,
    )
    ops_surface_color = fields.Char(
        related='company_id.ops_surface_color',
        readonly=False,
    )
    ops_text_color = fields.Char(
        related='company_id.ops_text_color',
        readonly=False,
    )
    ops_border_color = fields.Char(
        related='company_id.ops_border_color',
        readonly=False,
    )

    # =========================================================================
    # FAVICON
    # =========================================================================
    ops_favicon = fields.Binary(
        related='company_id.ops_favicon',
        readonly=False,
    )

    # =========================================================================
    # LOGIN PAGE
    # =========================================================================
    ops_login_background = fields.Binary(
        related='company_id.ops_login_background',
        readonly=False,
    )
    ops_login_tagline = fields.Char(
        related='company_id.ops_login_tagline',
        readonly=False,
    )
    ops_login_show_logo = fields.Boolean(
        related='company_id.ops_login_show_logo',
        readonly=False,
    )

    # =========================================================================
    # LAYOUT OPTIONS
    # =========================================================================
    ops_navbar_style = fields.Selection(
        related='company_id.ops_navbar_style',
        readonly=False,
    )
    ops_card_shadow = fields.Selection(
        related='company_id.ops_card_shadow',
        readonly=False,
    )
    ops_border_radius = fields.Selection(
        related='company_id.ops_border_radius',
        readonly=False,
    )

    # =========================================================================
    # REPORT COLORS
    # =========================================================================
    ops_report_primary_color = fields.Char(
        related='company_id.ops_report_primary_color',
        readonly=False,
    )
    ops_report_text_on_primary = fields.Char(
        related='company_id.ops_report_text_on_primary',
        readonly=False,
    )
    ops_report_body_text_color = fields.Char(
        related='company_id.ops_report_body_text_color',
        readonly=False,
    )

    # =========================================================================
    # REPORT SETTINGS
    # =========================================================================
    ops_report_logo_position = fields.Selection(
        related='company_id.ops_report_logo_position',
        readonly=False,
    )
    ops_amount_words_lang = fields.Selection(
        related='company_id.ops_amount_words_lang',
        readonly=False,
    )
    ops_show_external_badge = fields.Boolean(
        related='company_id.ops_show_external_badge',
        readonly=False,
    )
    ops_show_bank_details = fields.Boolean(
        related='company_id.ops_show_bank_details',
        readonly=False,
    )
    ops_show_signature_block = fields.Boolean(
        related='company_id.ops_show_signature_block',
        readonly=False,
    )
    ops_signature_label_1 = fields.Char(
        related='company_id.ops_signature_label_1',
        readonly=False,
    )
    ops_signature_label_2 = fields.Char(
        related='company_id.ops_signature_label_2',
        readonly=False,
    )
    ops_signature_label_3 = fields.Char(
        related='company_id.ops_signature_label_3',
        readonly=False,
    )
    ops_show_amount_words = fields.Boolean(
        related='company_id.ops_show_amount_words',
        readonly=False,
    )
    ops_report_terms = fields.Html(
        related='company_id.ops_report_terms',
        readonly=False,
    )
    ops_logo_max_size = fields.Integer(
        related='company_id.ops_logo_max_size',
        readonly=False,
    )
    ops_show_product_code = fields.Boolean(
        related='company_id.ops_show_product_code',
        readonly=False,
    )

    # =========================================================================
    # UI ENHANCEMENT TOGGLES
    # =========================================================================
    ops_sidebar_enabled = fields.Boolean(
        related='company_id.ops_sidebar_enabled',
        readonly=False,
    )
    ops_sidebar_logo = fields.Binary(
        related='company_id.ops_sidebar_logo',
        readonly=False,
    )
    ops_home_menu_enhanced = fields.Boolean(
        related='company_id.ops_home_menu_enhanced',
        readonly=False,
    )
    ops_dialog_enhancements = fields.Boolean(
        related='company_id.ops_dialog_enhancements',
        readonly=False,
    )
    ops_chatter_enhanced = fields.Boolean(
        related='company_id.ops_chatter_enhanced',
        readonly=False,
    )
    ops_group_controls_enabled = fields.Boolean(
        related='company_id.ops_group_controls_enabled',
        readonly=False,
    )
    ops_auto_refresh_enabled = fields.Boolean(
        related='company_id.ops_auto_refresh_enabled',
        readonly=False,
    )
    ops_auto_refresh_interval = fields.Integer(
        related='company_id.ops_auto_refresh_interval',
        readonly=False,
    )

    # =========================================================================
    # USER DEFAULTS
    # =========================================================================
    ops_default_chatter_position = fields.Selection(
        related='company_id.ops_default_chatter_position',
        readonly=False,
    )

    # =========================================================================
    # ONCHANGE — Preset applies colors on the settings form
    # =========================================================================
    @api.onchange('ops_theme_skin_id')
    def _onchange_ops_theme_skin_id(self):
        """Apply preset colors when theme skin changes."""
        if self.ops_theme_skin_id:
            skin = self.ops_theme_skin_id

            # Main palette colors (10 fields)
            self.ops_primary_color = skin.primary_color
            self.ops_secondary_color = skin.secondary_color
            self.ops_success_color = skin.success_color
            self.ops_warning_color = skin.warning_color
            self.ops_danger_color = skin.danger_color
            self.ops_info_color = skin.info_color

            self.ops_bg_color = skin.bg_color
            self.ops_surface_color = skin.surface_color
            self.ops_text_color = skin.text_color
            self.ops_border_color = skin.border_color

            self.ops_navbar_style = skin.navbar_style

    # =========================================================================
    # SET VALUES — Write colors to compile-time SCSS via color_assets
    # =========================================================================
    def set_values(self):
        """Override to write color changes to SCSS via ir.asset."""
        res = super().set_values()

        color_editor = self.env['ops_theme.color_assets']

        # Light SCSS only
        light_colors = {
            'brand': self.ops_primary_color or '#1e293b',
            'primary': self.ops_secondary_color or '#3b82f6',
            'success': self.ops_success_color or '#10b981',
            'info': self.ops_info_color or '#06b6d4',
            'warning': self.ops_warning_color or '#f59e0b',
            'danger': self.ops_danger_color or '#ef4444',
            'bg': self.ops_bg_color or LIGHT_LAYOUT_DEFAULTS['bg'],
            'surface': self.ops_surface_color or LIGHT_LAYOUT_DEFAULTS['surface'],
            'text': self.ops_text_color or LIGHT_LAYOUT_DEFAULTS['text'],
            'border': self.ops_border_color or LIGHT_LAYOUT_DEFAULTS['border'],
        }

        color_editor.set_light_colors(light_colors)

        return res

    # =========================================================================
    # ACTIONS
    # =========================================================================
    def action_reset_theme_defaults(self):
        """Reset all theme settings to Corporate Blue defaults."""
        self.ensure_one()

        # Reset SCSS color assets to module defaults
        self.env['ops_theme.color_assets'].reset_all()

        skin = self.env.ref('ops_theme.skin_corporate_blue', raise_if_not_found=False)
        self.company_id.write({
            'ops_theme_skin_id': skin.id if skin else False,
            'ops_theme_preset': 'corporate_blue',

            # Light palette (10 colors)
            'ops_primary_color': '#1e293b',
            'ops_secondary_color': '#3b82f6',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_info_color': '#06b6d4',
            'ops_bg_color': '#f1f5f9',
            'ops_surface_color': '#ffffff',
            'ops_text_color': '#1e293b',
            'ops_border_color': '#e2e8f0',

            # UI defaults
            'ops_favicon': False,
            'ops_login_background': False,
            'ops_login_tagline': 'Enterprise Resource Planning',
            'ops_login_show_logo': True,
            'ops_navbar_style': 'dark',
            'ops_card_shadow': 'medium',
            'ops_border_radius': 'rounded',
            'ops_report_logo_position': 'left',
            'ops_amount_words_lang': 'en',
            'ops_show_external_badge': True,
            'ops_default_chatter_position': 'bottom',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_preview_theme(self):
        """Open new tab to preview theme."""
        return {
            'type': 'ir.actions.act_url',
            'url': '/web',
            'target': 'new',
        }
