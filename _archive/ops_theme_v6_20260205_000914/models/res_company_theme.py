# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models


class ResCompanyTheme(models.Model):
    """Extend res.company with OPS Theme settings."""

    _inherit = 'res.company'

    # =========================================================================
    # FAVICON
    # =========================================================================
    ops_favicon = fields.Binary(
        string='Favicon',
        attachment=True,
        help='Custom favicon for browser tabs (recommended: 32x32 or 64x64 PNG/ICO)',
    )
    ops_favicon_mimetype = fields.Char(
        string='Favicon MIME Type',
        compute='_compute_favicon_mimetype',
        store=True,
    )

    # Theme Preset
    ops_theme_preset = fields.Selection(
        selection=[
            ('corporate_blue', 'Corporate Blue'),
            ('modern_dark', 'Modern Dark'),
            ('clean_light', 'Clean Light'),
            ('enterprise_navy', 'Enterprise Navy'),
            ('custom', 'Custom'),
        ],
        string='Theme Preset',
        default='corporate_blue',
        help='Select a predefined theme or choose Custom for manual configuration.',
    )

    # Brand Colors
    ops_primary_color = fields.Char(
        string='Primary Color',
        default='#1e293b',
        help='Main brand color used for headers, buttons, and primary UI elements.',
    )
    ops_secondary_color = fields.Char(
        string='Secondary Color',
        default='#3b82f6',
        help='Accent color for links, highlights, and secondary elements.',
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

    # Login Page Settings
    ops_login_background = fields.Binary(
        string='Login Background Image',
        attachment=True,
        help='Background image for the login page split-screen.',
    )
    ops_login_tagline = fields.Char(
        string='Login Tagline',
        default='Enterprise Resource Planning',
        help='Tagline displayed on the login page.',
    )
    ops_login_show_logo = fields.Boolean(
        string='Show Logo on Login',
        default=True,
        help='Display company logo on the login page.',
    )

    # UI Style Settings
    ops_navbar_style = fields.Selection(
        selection=[
            ('dark', 'Dark'),
            ('light', 'Light'),
            ('primary', 'Primary Color'),
        ],
        string='Navbar Style',
        default='dark',
        help='Color style for the navigation bar.',
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
        help='Shadow intensity for card elements.',
    )
    ops_border_radius = fields.Selection(
        selection=[
            ('sharp', 'Sharp (0px)'),
            ('rounded', 'Rounded (8px)'),
            ('pill', 'Pill (16px)'),
        ],
        string='Border Radius',
        default='rounded',
        help='Corner rounding for buttons and cards.',
    )

    # Report Theming
    ops_report_header_bg = fields.Char(
        string='Report Header Background',
        default='#1e293b',
        help='Background color for PDF report headers.',
    )
    ops_report_logo_position = fields.Selection(
        selection=[
            ('left', 'Left'),
            ('center', 'Center'),
            ('right', 'Right'),
        ],
        string='Report Logo Position',
        default='left',
        help='Position of the company logo in PDF reports.',
    )

    # Debranding
    ops_powered_by_visible = fields.Boolean(
        string='Show Powered By',
        default=True,
        help='Show "Powered by" text in footer.',
    )

    # Preset Color Definitions
    THEME_PRESETS = {
        'corporate_blue': {
            'ops_primary_color': '#1e293b',
            'ops_secondary_color': '#3b82f6',
            'ops_success_color': '#10b981',
            'ops_warning_color': '#f59e0b',
            'ops_danger_color': '#ef4444',
            'ops_navbar_style': 'dark',
            'ops_report_header_bg': '#1e293b',
        },
        'modern_dark': {
            'ops_primary_color': '#111827',
            'ops_secondary_color': '#6366f1',
            'ops_success_color': '#22c55e',
            'ops_warning_color': '#eab308',
            'ops_danger_color': '#f43f5e',
            'ops_navbar_style': 'dark',
            'ops_report_header_bg': '#111827',
        },
        'clean_light': {
            'ops_primary_color': '#f8fafc',
            'ops_secondary_color': '#0ea5e9',
            'ops_success_color': '#14b8a6',
            'ops_warning_color': '#f97316',
            'ops_danger_color': '#dc2626',
            'ops_navbar_style': 'light',
            'ops_report_header_bg': '#64748b',
        },
        'enterprise_navy': {
            'ops_primary_color': '#0f172a',
            'ops_secondary_color': '#2563eb',
            'ops_success_color': '#059669',
            'ops_warning_color': '#d97706',
            'ops_danger_color': '#b91c1c',
            'ops_navbar_style': 'dark',
            'ops_report_header_bg': '#0f172a',
        },
    }

    @api.onchange('ops_theme_preset')
    def _onchange_theme_preset(self):
        """Apply preset colors when theme preset is changed."""
        if self.ops_theme_preset and self.ops_theme_preset != 'custom':
            preset = self.THEME_PRESETS.get(self.ops_theme_preset, {})
            for field_name, value in preset.items():
                setattr(self, field_name, value)

    @api.depends('ops_favicon')
    def _compute_favicon_mimetype(self):
        """Detect favicon MIME type from binary data header."""
        for company in self:
            if company.ops_favicon:
                try:
                    # Decode first 32 bytes to detect file type
                    data = base64.b64decode(company.ops_favicon[:64])
                    if data[:4] == b'\x00\x00\x01\x00':
                        company.ops_favicon_mimetype = 'image/x-icon'
                    elif data[:8] == b'\x89PNG\r\n\x1a\n':
                        company.ops_favicon_mimetype = 'image/png'
                    elif data[:2] == b'\xff\xd8':
                        company.ops_favicon_mimetype = 'image/jpeg'
                    elif data[:6] in (b'GIF87a', b'GIF89a'):
                        company.ops_favicon_mimetype = 'image/gif'
                    else:
                        company.ops_favicon_mimetype = 'image/x-icon'
                except Exception:
                    company.ops_favicon_mimetype = 'image/x-icon'
            else:
                company.ops_favicon_mimetype = False

    def get_favicon(self):
        """Return favicon data or False to use default."""
        self.ensure_one()
        return self.ops_favicon if self.ops_favicon else False
