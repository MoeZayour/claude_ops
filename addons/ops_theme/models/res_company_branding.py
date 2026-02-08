# -*- coding: utf-8 -*-
"""
OPS Theme - Company Branding Extension
========================================
Full theme customization fields for white-label branding.
"""

import base64
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResCompanyBranding(models.Model):
    """Extend res.company with OPS Theme branding fields."""

    _inherit = 'res.company'

    # =========================================================================
    # THEME PRESET
    # =========================================================================
    ops_theme_preset = fields.Selection(
        selection=[
            ('corporate_blue', 'Corporate Blue'),
            ('modern_dark', 'Modern Dark'),
            ('clean_light', 'Clean Light'),
            ('enterprise_navy', 'Enterprise Navy'),
            ('warm_professional', 'Warm Professional'),
            ('mono_minimal', 'Monochromatic Minimalism'),
            ('neon_highlights', 'Neon Highlights'),
            ('warm_tones', 'Warm Tones'),
            ('muted_pastels', 'Muted Pastels'),
            ('deep_jewel', 'Deep Jewel Tones'),
            ('contrast_vibrant', 'Contrasting Vibrancy'),
            ('custom', 'Custom'),
        ],
        string='Theme Preset',
        default='corporate_blue',
    )

    # =========================================================================
    # BRAND COLORS
    # =========================================================================
    ops_primary_color = fields.Char(
        string='Primary Brand Color',
        default='#1e293b',
        help='Main brand color for headers, navbar, and primary UI elements.',
    )
    ops_secondary_color = fields.Char(
        string='OPS Secondary Color',
        default='#3b82f6',
        help='Accent color for links, buttons, and highlights.',
    )
    ops_success_color = fields.Char(
        string='Success Color',
        default='#10b981',
        help='Color for success messages and positive indicators.',
    )
    ops_warning_color = fields.Char(
        string='Warning Color',
        default='#f59e0b',
        help='Color for warning messages and alerts.',
    )
    ops_danger_color = fields.Char(
        string='Danger Color',
        default='#ef4444',
        help='Color for error messages and destructive actions.',
    )

    # =========================================================================
    # EXTENDED PALETTE COLORS
    # =========================================================================
    ops_bg_color = fields.Char(
        string='Background Color',
        default='#f1f5f9',
        help='Page/body background color.',
    )
    ops_surface_color = fields.Char(
        string='Surface Color',
        default='#ffffff',
        help='Card, panel, and sidebar background color.',
    )
    ops_text_color = fields.Char(
        string='Text Color',
        default='#1e293b',
        help='Primary text color.',
    )
    ops_border_color = fields.Char(
        string='Border Color',
        default='#e2e8f0',
        help='Default border and divider color.',
    )
    ops_accent2_color = fields.Char(
        string='Accent 2 Color',
        default='#60a5fa',
        help='Secondary accent for badges, tags, and alternate highlights.',
    )
    ops_btn_color = fields.Char(
        string='Button Color',
        default='#3b82f6',
        help='Primary call-to-action button background color.',
    )

    # =========================================================================
    # FAVICON
    # =========================================================================
    ops_favicon = fields.Binary(
        string='Custom Favicon',
        attachment=True,
        help='Custom favicon for browser tabs (32x32 or 64x64 PNG/ICO).',
    )
    ops_favicon_mimetype = fields.Char(
        string='Favicon MIME Type',
        compute='_compute_favicon_mimetype',
        store=True,
    )

    # =========================================================================
    # LOGIN PAGE
    # =========================================================================
    ops_login_background = fields.Binary(
        string='Login Background Image',
        attachment=True,
        help='Background image for the login page (recommended: 1920x1080).',
    )
    ops_login_tagline = fields.Char(
        string='Login Tagline',
        default='Enterprise Resource Planning',
        help='Tagline displayed on the login screen.',
    )
    ops_login_show_logo = fields.Boolean(
        string='Show Logo on Login',
        default=True,
        help='Display company logo on the login page.',
    )

    # =========================================================================
    # LAYOUT OPTIONS
    # =========================================================================
    ops_navbar_style = fields.Selection(
        selection=[
            ('dark', 'Dark'),
            ('light', 'Light'),
            ('primary', 'Primary Color'),
        ],
        string='Navbar Style',
        default='dark',
    )
    ops_card_shadow = fields.Selection(
        selection=[
            ('none', 'None'),
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('heavy', 'Heavy'),
        ],
        string='Card Shadow',
        default='medium',
    )
    ops_border_radius = fields.Selection(
        selection=[
            ('sharp', 'Sharp (0px)'),
            ('rounded', 'Rounded (8px)'),
            ('pill', 'Pill (16px)'),
        ],
        string='Border Radius',
        default='rounded',
    )

    # =========================================================================
    # REPORT SETTINGS
    # =========================================================================
    ops_report_logo_position = fields.Selection(
        selection=[
            ('left', 'Left'),
            ('center', 'Center'),
            ('right', 'Right'),
        ],
        string='Report Logo Position',
        default='left',
    )
    ops_amount_words_lang = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ar', 'Arabic'),
            ('both', 'English & Arabic'),
        ],
        string='Amount in Words Language',
        default='en',
        help='Language for amount in words on external documents.',
    )
    ops_show_external_badge = fields.Boolean(
        string='Show OPS Framework Badge',
        default=True,
        help='Display "Powered by OPS Framework" badge on reports and external documents.',
    )
    ops_show_bank_details = fields.Boolean(
        string='Show Bank Details on Documents',
        default=True,
        help='Display bank account details on quotations and invoices.',
    )
    ops_show_signature_block = fields.Boolean(
        string='Show Signature Block',
        default=True,
        help='Display signature lines on printed documents.',
    )
    ops_signature_label_1 = fields.Char(
        string='Signature Label 1',
        default='Prepared By',
        help='First signature line label on printed documents.',
    )
    ops_signature_label_2 = fields.Char(
        string='Signature Label 2',
        default='Authorized Signatory',
        help='Second signature line label on printed documents.',
    )
    ops_signature_label_3 = fields.Char(
        string='Signature Label 3',
        default='Customer Acceptance',
        help='Third signature line label on printed documents.',
    )
    ops_show_amount_words = fields.Boolean(
        string='Show Amount in Words',
        default=True,
        help='Display amount in words on quotations and invoices.',
    )
    ops_report_terms = fields.Html(
        string='Default Report Terms',
        help='Default terms and conditions printed on external documents when no document-specific terms exist.',
    )

    # =========================================================================
    # USER DEFAULTS
    # =========================================================================
    ops_default_color_mode = fields.Selection(
        selection=[
            ('light', 'Light Mode'),
            ('dark', 'Dark Mode'),
        ],
        string='Default Color Mode',
        default='light',
    )
    ops_default_chatter_position = fields.Selection(
        selection=[
            ('bottom', 'Bottom'),
            ('side', 'Side'),
        ],
        string='Default Chatter Position',
        default='bottom',
    )

    # =========================================================================
    # PRESET DEFINITIONS
    # =========================================================================
    THEME_PRESETS = {
        'corporate_blue': {
            'ops_primary_color': '#1e293b',
            'ops_secondary_color': '#3b82f6',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#f1f5f9',
            'ops_surface_color': '#ffffff',
            'ops_text_color': '#1e293b',
            'ops_border_color': '#e2e8f0',
            'ops_accent2_color': '#60a5fa',
            'ops_btn_color': '#3b82f6',
            'ops_navbar_style': 'dark',
        },
        'modern_dark': {
            'ops_primary_color': '#111827',
            'ops_secondary_color': '#6366f1',
            'ops_success_color': '#22c55e',
            'ops_warning_color': '#eab308',
            'ops_danger_color': '#f43f5e',
            'ops_bg_color': '#0f172a',
            'ops_surface_color': '#1e293b',
            'ops_text_color': '#f1f5f9',
            'ops_border_color': '#334155',
            'ops_accent2_color': '#818cf8',
            'ops_btn_color': '#6366f1',
            'ops_navbar_style': 'dark',
        },
        'clean_light': {
            'ops_primary_color': '#f8fafc',
            'ops_secondary_color': '#0ea5e9',
            'ops_success_color': '#14b8a6',
            'ops_warning_color': '#f97316',
            'ops_danger_color': '#dc2626',
            'ops_bg_color': '#ffffff',
            'ops_surface_color': '#f8fafc',
            'ops_text_color': '#0f172a',
            'ops_border_color': '#e2e8f0',
            'ops_accent2_color': '#38bdf8',
            'ops_btn_color': '#0ea5e9',
            'ops_navbar_style': 'light',
        },
        'enterprise_navy': {
            'ops_primary_color': '#0f172a',
            'ops_secondary_color': '#2563eb',
            'ops_success_color': '#059669',
            'ops_warning_color': '#d97706',
            'ops_danger_color': '#b91c1c',
            'ops_bg_color': '#f8fafc',
            'ops_surface_color': '#ffffff',
            'ops_text_color': '#0f172a',
            'ops_border_color': '#e2e8f0',
            'ops_accent2_color': '#3b82f6',
            'ops_btn_color': '#2563eb',
            'ops_navbar_style': 'dark',
        },
        'warm_professional': {
            'ops_primary_color': '#292524',
            'ops_secondary_color': '#d97706',
            'ops_success_color': '#65a30d',
            'ops_warning_color': '#ea580c',
            'ops_danger_color': '#dc2626',
            'ops_bg_color': '#fafaf9',
            'ops_surface_color': '#ffffff',
            'ops_text_color': '#292524',
            'ops_border_color': '#e7e5e4',
            'ops_accent2_color': '#ea580c',
            'ops_btn_color': '#d97706',
            'ops_navbar_style': 'dark',
        },
        'mono_minimal': {
            'ops_primary_color': '#1E1E1E',
            'ops_secondary_color': '#888888',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#121212',
            'ops_surface_color': '#1E1E1E',
            'ops_text_color': '#E0E0E0',
            'ops_border_color': '#444444',
            'ops_accent2_color': '#AAAAAA',
            'ops_btn_color': '#888888',
            'ops_navbar_style': 'dark',
        },
        'neon_highlights': {
            'ops_primary_color': '#1A1A1A',
            'ops_secondary_color': '#00FF85',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#0D0D0D',
            'ops_surface_color': '#1A1A1A',
            'ops_text_color': '#FFFFFF',
            'ops_border_color': '#333333',
            'ops_accent2_color': '#1E90FF',
            'ops_btn_color': '#00FF85',
            'ops_navbar_style': 'dark',
        },
        'warm_tones': {
            'ops_primary_color': '#2A2420',
            'ops_secondary_color': '#FF6F61',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#DAA520',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#1C1C1C',
            'ops_surface_color': '#2A2420',
            'ops_text_color': '#F5E8D8',
            'ops_border_color': '#4A4038',
            'ops_accent2_color': '#DAA520',
            'ops_btn_color': '#FF6F61',
            'ops_navbar_style': 'dark',
        },
        'muted_pastels': {
            'ops_primary_color': '#363636',
            'ops_secondary_color': '#A8DADC',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#2C2C2C',
            'ops_surface_color': '#363636',
            'ops_text_color': '#E4E4E4',
            'ops_border_color': '#505050',
            'ops_accent2_color': '#FFC1CC',
            'ops_btn_color': '#B39CD0',
            'ops_navbar_style': 'dark',
        },
        'deep_jewel': {
            'ops_primary_color': '#242424',
            'ops_secondary_color': '#006B7F',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#1A1A1A',
            'ops_surface_color': '#242424',
            'ops_text_color': '#F0F0F0',
            'ops_border_color': '#404040',
            'ops_accent2_color': '#822659',
            'ops_btn_color': '#3E5641',
            'ops_navbar_style': 'dark',
        },
        'contrast_vibrant': {
            'ops_primary_color': '#222222',
            'ops_secondary_color': '#FF5722',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_bg_color': '#181818',
            'ops_surface_color': '#222222',
            'ops_text_color': '#F7F7F7',
            'ops_border_color': '#404040',
            'ops_accent2_color': '#673AB7',
            'ops_btn_color': '#FF5722',
            'ops_navbar_style': 'dark',
        },
    }

    # =========================================================================
    # THEME-AWARE WRITE — Clear assets on color/layout changes
    # =========================================================================
    _THEME_FIELDS = {
        'ops_primary_color', 'ops_secondary_color', 'ops_success_color',
        'ops_warning_color', 'ops_danger_color', 'ops_theme_preset',
        'ops_navbar_style', 'ops_card_shadow', 'ops_border_radius',
        'ops_bg_color', 'ops_surface_color', 'ops_text_color',
        'ops_border_color', 'ops_accent2_color', 'ops_btn_color',
    }

    def write(self, vals):
        """Override write to clear compiled assets when theme settings change."""
        res = super().write(vals)
        if self._THEME_FIELDS & set(vals.keys()):
            self._clear_theme_assets()
        return res

    def _clear_theme_assets(self):
        """Clear compiled asset bundles to force SCSS recompilation."""
        try:
            self.env['ir.attachment'].sudo().search([
                ('name', 'like', 'assets%'),
                ('res_model', '=', 'ir.ui.view'),
            ]).unlink()
            # Clear QWeb caches if the method exists (varies by Odoo version)
            qweb = self.env.get('ir.qweb')
            if qweb and hasattr(qweb, 'clear_caches'):
                qweb.clear_caches()
            _logger.info("OPS Theme: Cleared asset cache for theme recompilation")
        except Exception as e:
            _logger.warning("OPS Theme: Failed to clear asset cache: %s", e)

    @api.onchange('ops_theme_preset')
    def _onchange_theme_preset(self):
        """Apply preset colors when theme preset changes."""
        if self.ops_theme_preset and self.ops_theme_preset != 'custom':
            preset = self.THEME_PRESETS.get(self.ops_theme_preset, {})
            for field_name, value in preset.items():
                setattr(self, field_name, value)

    @api.depends('ops_favicon')
    def _compute_favicon_mimetype(self):
        """Detect favicon MIME type from binary data."""
        for company in self:
            if company.ops_favicon:
                try:
                    data = base64.b64decode(company.ops_favicon[:64])
                    if data[:4] == b'\x00\x00\x01\x00':
                        company.ops_favicon_mimetype = 'image/x-icon'
                    elif data[:8] == b'\x89PNG\r\n\x1a\n':
                        company.ops_favicon_mimetype = 'image/png'
                    elif data[:2] == b'\xff\xd8':
                        company.ops_favicon_mimetype = 'image/jpeg'
                    else:
                        company.ops_favicon_mimetype = 'image/x-icon'
                except Exception:
                    _logger.debug('Failed to detect favicon MIME type', exc_info=True)
                    company.ops_favicon_mimetype = 'image/x-icon'
            else:
                company.ops_favicon_mimetype = False

    def get_ops_report_settings(self):
        """Return OPS report settings as a plain dict for QWeb templates.

        Neither hasattr() nor getattr() are available in Odoo 19 QWeb sandbox.
        This method wraps all OPS-specific field access in try/except so
        templates never crash during module upgrades or with stale registries.

        Usage in QWeb:
            <t t-set="_ops" t-value="company.get_ops_report_settings()"/>
            <t t-if="_ops['show_words']">...</t>
        """
        self.ensure_one()
        defaults = {
            'show_words': False,
            'show_bank': False,
            'show_sig': False,
            'words_lang': 'en',
            'sig1': 'Prepared By',
            'sig2': 'Authorized Signatory',
            'sig3': 'Customer Acceptance',
            'report_terms': False,
        }
        try:
            return {
                'show_words': self.ops_show_amount_words,
                'show_bank': self.ops_show_bank_details,
                'show_sig': self.ops_show_signature_block,
                'words_lang': self.ops_amount_words_lang or 'en',
                'sig1': self.ops_signature_label_1 or 'Prepared By',
                'sig2': self.ops_signature_label_2 or 'Authorized Signatory',
                'sig3': self.ops_signature_label_3 or 'Customer Acceptance',
                'report_terms': self.ops_report_terms,
            }
        except (AttributeError, KeyError):
            return defaults

    def get_favicon(self):
        """Return favicon data or False."""
        self.ensure_one()
        return self.ops_favicon if self.ops_favicon else False
