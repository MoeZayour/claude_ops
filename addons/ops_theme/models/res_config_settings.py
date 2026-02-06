# -*- coding: utf-8 -*-
"""
OPS Theme - Configuration Settings
===================================
Full settings UI for theme customization.
"""

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """OPS Theme settings in General Settings."""

    _inherit = 'res.config.settings'

    # =========================================================================
    # THEME PRESET
    # =========================================================================
    ops_theme_preset = fields.Selection(
        related='company_id.ops_theme_preset',
        readonly=False,
    )

    # =========================================================================
    # BRAND COLORS
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

    # =========================================================================
    # USER DEFAULTS
    # =========================================================================
    ops_default_color_mode = fields.Selection(
        related='company_id.ops_default_color_mode',
        readonly=False,
    )
    ops_default_chatter_position = fields.Selection(
        related='company_id.ops_default_chatter_position',
        readonly=False,
    )

    # =========================================================================
    # ONCHANGE — Preset applies colors on the settings form
    # =========================================================================
    @api.onchange('ops_theme_preset')
    def _onchange_theme_preset(self):
        """Apply preset colors when theme preset changes.

        This must live on res.config.settings (not res.company) because
        the settings form operates on this transient model — onchange
        defined on the related model does not fire.
        """
        if self.ops_theme_preset and self.ops_theme_preset != 'custom':
            from odoo.addons.ops_theme.models.res_company_branding import ResCompanyBranding
            preset = ResCompanyBranding.THEME_PRESETS.get(self.ops_theme_preset, {})
            for field_name, value in preset.items():
                setattr(self, field_name, value)

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
            'ops_report_logo_position': 'left',
            'ops_amount_words_lang': 'en',
            'ops_show_external_badge': True,
            'ops_default_color_mode': 'light',
            'ops_default_chatter_position': 'bottom',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Theme Reset',
                'message': 'All theme settings have been reset to defaults.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_preview_theme(self):
        """Open new tab to preview theme."""
        return {
            'type': 'ir.actions.act_url',
            'url': '/web',
            'target': 'new',
        }
