# -*- coding: utf-8 -*-
"""
OPS Theme - Company Branding Extension
========================================
Full theme customization fields for white-label branding.
Light-only skin system with 10 colors + 1 navbar style.
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
    ops_theme_skin_id = fields.Many2one(
        'ops.theme.skin',
        string='Theme Preset',
        default=lambda self: self.env.ref('ops_theme.skin_corporate_blue', raise_if_not_found=False)
    )

    # =========================================================================
    # BRAND COLORS (10 skin colors — OPS Design Guide v1.0 naming)
    # =========================================================================
    ops_brand_color = fields.Char(
        string='Brand Color',
        default='#1e293b',
        help='Main brand color for navbar, sidebar, and headings accent.',
    )
    ops_action_color = fields.Char(
        string='Action Color',
        default='#3b82f6',
        help='Interactive elements: buttons, links, focus rings, selected items.',
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
    ops_info_color = fields.Char(
        string='Info Color',
        default='#06b6d4',
        help='Color for informational messages, badges, and highlights.',
    )

    # =========================================================================
    # CANVAS COLORS
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
        default=False,
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
    # REPORT COLORS (external PDF documents)
    # =========================================================================
    ops_report_primary_color = fields.Char(string='Report Primary Color', default='#5B6BBB')
    ops_report_text_on_primary = fields.Char(string='Report Text on Primary', default='#FFFFFF')
    ops_report_body_text_color = fields.Char(string='Report Body Text Color', default='#1a1a1a')
    ops_logo_max_size = fields.Integer(string='Report Logo Max Size (px)', default=80)
    ops_show_product_code = fields.Boolean(string='Show Product Code on Reports', default=True)

    # =========================================================================
    # UI ENHANCEMENT TOGGLES
    # =========================================================================
    ops_sidebar_enabled = fields.Boolean(string='Enable Sidebar', default=True)
    ops_sidebar_logo = fields.Binary(string='Sidebar Logo', attachment=True)
    ops_home_menu_enhanced = fields.Boolean(string='Enhanced Home Menu', default=True)
    ops_dialog_enhancements = fields.Boolean(string='Dialog Enhancements', default=True)
    ops_chatter_enhanced = fields.Boolean(string='Chatter Enhancements', default=True)
    ops_group_controls_enabled = fields.Boolean(string='Group Controls', default=True)
    ops_auto_refresh_enabled = fields.Boolean(string='Auto Refresh Lists', default=False)
    ops_auto_refresh_interval = fields.Integer(string='Auto Refresh Interval (s)', default=30)

    # =========================================================================
    # USER DEFAULTS
    # =========================================================================
    ops_default_chatter_position = fields.Selection(
        selection=[
            ('bottom', 'Bottom'),
            ('side', 'Side'),
        ],
        string='Default Chatter Position',
        default='bottom',
    )

    # =========================================================================
    # SMART SKIN — Auto-detect dark backgrounds
    # =========================================================================
    ops_is_dark_skin = fields.Boolean(
        string='Dark Skin Detected',
        compute='_compute_ops_is_dark_skin',
        store=True,
        help='Automatically True when the background color luminance < 128.',
    )

    @api.depends('ops_bg_color')
    def _compute_ops_is_dark_skin(self):
        """Detect if the current skin is dark based on bg_color luminance."""
        for company in self:
            bg = (company.ops_bg_color or '#f1f5f9').lstrip('#')
            try:
                r = int(bg[0:2], 16)
                g = int(bg[2:4], 16)
                b = int(bg[4:6], 16)
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                company.ops_is_dark_skin = luminance < 128
            except (ValueError, IndexError):
                company.ops_is_dark_skin = False

    # =========================================================================
    # THEME-AWARE WRITE — Clear assets on color/layout changes
    # =========================================================================
    _THEME_FIELDS = {
        'ops_brand_color', 'ops_action_color', 'ops_success_color',
        'ops_warning_color', 'ops_danger_color', 'ops_info_color',
        'ops_navbar_style', 'ops_card_shadow',
        'ops_border_radius', 'ops_bg_color', 'ops_surface_color',
        'ops_text_color', 'ops_border_color',
    }

    def write(self, vals):
        """Override write to log theme changes."""
        res = super().write(vals)
        if self._THEME_FIELDS & set(vals.keys()):
            _logger.info(
                "OPS Theme: Theme fields updated — changes will appear on "
                "next page load via compiled CSS bundles"
            )
        return res

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

    # =========================================================================
    # REPORT COLOR HELPERS
    # =========================================================================
    @staticmethod
    def _hex_to_rgb(hex_str):
        try:
            h = (hex_str or '').lstrip('#')
            if len(h) == 6:
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, TypeError):
            pass
        return (91, 107, 187)

    def get_report_rgb(self):
        r, g, b = self._hex_to_rgb(self.ops_report_primary_color or '#5B6BBB')
        return '%d,%d,%d' % (r, g, b)

    def get_report_primary_light(self):
        r, g, b = self._hex_to_rgb(self.ops_report_primary_color or '#5B6BBB')
        return '#%02x%02x%02x' % (int(r+(255-r)*0.85), int(g+(255-g)*0.85), int(b+(255-b)*0.85))

    def get_report_primary_dark(self):
        r, g, b = self._hex_to_rgb(self.ops_report_primary_color or '#5B6BBB')
        return '#%02x%02x%02x' % (int(r*0.75), int(g*0.75), int(b*0.75))

    def get_ops_report_settings(self):
        """Return OPS report settings as a plain dict for QWeb templates."""
        self.ensure_one()
        defaults = {
            'primary': '#5B6BBB',
            'text_on_primary': '#FFFFFF',
            'body_text': '#1a1a1a',
            'rgb': '91,107,187',
            'primary_light': '#e2e5f3',
            'primary_dark': '#44508c',
            'show_words': True,
            'show_bank': True,
            'show_badge': True,
            'show_sig': False,
            'words_lang': 'en',
            'sig1': 'Prepared By',
            'sig2': 'Authorized Signatory',
            'sig3': 'Customer Acceptance',
            'report_terms': False,
            'logo_size': 80,
            'show_code': True,
        }
        try:
            return {
                'primary': self.ops_report_primary_color or '#5B6BBB',
                'text_on_primary': self.ops_report_text_on_primary or '#FFFFFF',
                'body_text': self.ops_report_body_text_color or '#1a1a1a',
                'rgb': self.get_report_rgb(),
                'primary_light': self.get_report_primary_light(),
                'primary_dark': self.get_report_primary_dark(),
                'show_words': self.ops_show_amount_words,
                'show_bank': self.ops_show_bank_details,
                'show_badge': self.ops_show_external_badge,
                'show_sig': self.ops_show_signature_block,
                'words_lang': self.ops_amount_words_lang or 'en',
                'sig1': self.ops_signature_label_1 or 'Prepared By',
                'sig2': self.ops_signature_label_2 or 'Authorized Signatory',
                'sig3': self.ops_signature_label_3 or 'Customer Acceptance',
                'report_terms': self.ops_report_terms,
                'logo_size': self.ops_logo_max_size or 80,
                'show_code': self.ops_show_product_code,
            }
        except (AttributeError, KeyError):
            return defaults

    def get_favicon(self):
        """Return favicon data or False."""
        self.ensure_one()
        return self.ops_favicon if self.ops_favicon else False
