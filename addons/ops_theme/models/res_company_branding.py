# -*- coding: utf-8 -*-
"""
OPS Theme - Company Branding Extension
========================================
Extends res.company with theme customization fields for white-label branding.
"""

from odoo import fields, models


class ResCompanyBranding(models.Model):
    """Extend res.company with OPS Theme branding fields."""

    _inherit = 'res.company'

    # Theme Colors
    ops_primary_color = fields.Char(
        string='Primary Brand Color',
        default='#1e293b',
        help='Primary color for login screen gradient and theme accents (hex format).',
    )

    # Login Customization
    ops_login_tagline = fields.Char(
        string='Login Tagline',
        help='Custom tagline displayed on the login screen. Defaults to company name if not set.',
    )

    # Favicon Branding
    ops_favicon = fields.Binary(
        string='Custom Favicon',
        help='Upload a custom favicon for white-label branding (.ico, .png, or .svg).',
        attachment=True,
    )

    ops_favicon_mimetype = fields.Char(
        string='Favicon MIME Type',
        default='image/x-icon',
        help='MIME type of the favicon (auto-detected on upload).',
    )

    # External Document Settings
    ops_amount_words_lang = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('both', 'English & Arabic'),
    ], string='Amount in Words Language', default='en',
       help='Language for amount in words on external documents.')

    ops_show_external_badge = fields.Boolean(
        string='Show OPS Framework Badge',
        default=True,
        help='Display "Powered by OPS Framework" on external documents.')
