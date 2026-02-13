# -*- coding: utf-8 -*-
"""
OPS Theme - Configuration Settings
===================================
Full settings UI for theme customization. Light-only skin system.
Colors are read directly from the selected skin preset — no manual
color pickers exposed to the user.
"""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

# Default colors (Corporate Blue)
CORPORATE_BLUE = {
    'brand': '#1e293b',
    'primary': '#3b82f6',
    'success': '#10b981',
    'info': '#06b6d4',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'bg': '#f1f5f9',
    'surface': '#ffffff',
    'text': '#1e293b',
    'border': '#e2e8f0',
}


class ResConfigSettings(models.TransientModel):
    """OPS Theme settings in General Settings."""

    _inherit = 'res.config.settings'

    # =========================================================================
    # THEME PRESET — the only color control exposed to users
    # =========================================================================
    ops_theme_skin_id = fields.Many2one(
        related='company_id.ops_theme_skin_id',
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
    # HELPERS — Extract colors from skin or fallback to defaults
    # =========================================================================

    def _get_skin_colors(self):
        """Return 10-color dict from the selected skin, or Corporate Blue."""
        skin = self.ops_theme_skin_id
        if not skin:
            return dict(CORPORATE_BLUE)
        return {
            'brand': skin.brand_color or CORPORATE_BLUE['brand'],
            'primary': skin.action_color or CORPORATE_BLUE['primary'],
            'success': skin.success_color or CORPORATE_BLUE['success'],
            'info': skin.info_color or CORPORATE_BLUE['info'],
            'warning': skin.warning_color or CORPORATE_BLUE['warning'],
            'danger': skin.danger_color or CORPORATE_BLUE['danger'],
            'bg': skin.bg_color or CORPORATE_BLUE['bg'],
            'surface': skin.surface_color or CORPORATE_BLUE['surface'],
            'text': skin.text_color or CORPORATE_BLUE['text'],
            'border': skin.border_color or CORPORATE_BLUE['border'],
        }

    # =========================================================================
    # SET VALUES — Read skin colors, sync to company, compile SCSS
    # =========================================================================
    def set_values(self):
        """Override to compile skin colors into SCSS and sync to company."""
        res = super().set_values()

        skin = self.ops_theme_skin_id
        colors = self._get_skin_colors()

        # Sync skin colors → company fields (used by login template + controller)
        self.company_id.write({
            'ops_brand_color': colors['brand'],
            'ops_action_color': colors['primary'],
            'ops_success_color': colors['success'],
            'ops_warning_color': colors['warning'],
            'ops_danger_color': colors['danger'],
            'ops_info_color': colors['info'],
            'ops_bg_color': colors['bg'],
            'ops_surface_color': colors['surface'],
            'ops_text_color': colors['text'],
            'ops_border_color': colors['border'],
        })

        # Sync navbar style from skin
        if skin and skin.navbar_style:
            self.company_id.write({'ops_navbar_style': skin.navbar_style})

        # Compile colors into SCSS via ir.asset
        self.env['ops_theme.color_assets'].set_light_colors(colors)

        _logger.info(
            "OPS Theme: Skin '%s' applied — SCSS compiled, reload required",
            skin.name if skin else 'Corporate Blue (default)',
        )
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
            'ops_brand_color': CORPORATE_BLUE['brand'],
            'ops_action_color': CORPORATE_BLUE['primary'],
            'ops_success_color': CORPORATE_BLUE['success'],
            'ops_warning_color': CORPORATE_BLUE['warning'],
            'ops_danger_color': CORPORATE_BLUE['danger'],
            'ops_info_color': CORPORATE_BLUE['info'],
            'ops_bg_color': CORPORATE_BLUE['bg'],
            'ops_surface_color': CORPORATE_BLUE['surface'],
            'ops_text_color': CORPORATE_BLUE['text'],
            'ops_border_color': CORPORATE_BLUE['border'],
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
