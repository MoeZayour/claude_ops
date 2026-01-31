# -*- coding: utf-8 -*-

import base64
from odoo import http
from odoo.http import request


class OPSThemeController(http.Controller):
    """Controller for OPS Theme: favicon serving and dynamic CSS variables."""

    # =========================================================================
    # FAVICON ENDPOINTS
    # =========================================================================

    @http.route('/ops_theme/favicon', type='http', auth='public', cors='*')
    def favicon(self, **kwargs):
        """
        Serve company favicon or redirect to default.

        Returns the company's custom favicon if one is uploaded,
        otherwise redirects to Odoo's default favicon.
        """
        # Get company - use session company or default to company ID 1
        company_id = request.env.company.id if request.env.company else 1
        company = request.env['res.company'].sudo().browse(company_id)

        if company.ops_favicon:
            try:
                favicon_data = base64.b64decode(company.ops_favicon)
                mimetype = company.ops_favicon_mimetype or 'image/x-icon'
                return request.make_response(
                    favicon_data,
                    headers=[
                        ('Content-Type', mimetype),
                        ('Cache-Control', 'public, max-age=86400'),
                    ]
                )
            except Exception:
                pass

        # Fallback to default Odoo favicon
        return request.redirect('/web/static/img/favicon.ico', code=302)

    @http.route('/favicon.ico', type='http', auth='public')
    def favicon_redirect(self, **kwargs):
        """
        Override default favicon.ico route.

        This intercepts requests to /favicon.ico and serves the
        company's custom favicon if available.
        """
        return self.favicon(**kwargs)

    # =========================================================================
    # CSS VARIABLES ENDPOINT
    # =========================================================================

    @http.route('/ops_theme/variables.css', type='http', auth='public', cors='*')
    def theme_variables_css(self, **kwargs):
        """
        Generate CSS custom properties from company theme settings.

        Returns a CSS file with --ops-* variables that can be used
        throughout the application for consistent theming.
        """
        # Get company from session or default
        company = request.env.company

        # Get theme settings with defaults
        primary_color = company.ops_primary_color or '#1e293b'
        secondary_color = company.ops_secondary_color or '#3b82f6'
        success_color = company.ops_success_color or '#10b981'
        warning_color = company.ops_warning_color or '#f59e0b'
        danger_color = company.ops_danger_color or '#ef4444'

        navbar_style = company.ops_navbar_style or 'dark'
        card_shadow = company.ops_card_shadow or 'medium'
        border_radius = company.ops_border_radius or 'rounded'

        report_header_bg = company.ops_report_header_bg or '#1e293b'

        # Map shadow levels to CSS values
        shadow_map = {
            'none': 'none',
            'light': '0 1px 3px rgba(0, 0, 0, 0.1)',
            'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'heavy': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        }

        # Map border radius options to CSS values
        radius_map = {
            'sharp': '0px',
            'rounded': '8px',
            'pill': '16px',
        }

        # Navbar style colors
        navbar_colors = {
            'dark': {'bg': '#1f2937', 'text': '#ffffff'},
            'light': {'bg': '#f8fafc', 'text': '#1f2937'},
            'primary': {'bg': primary_color, 'text': '#ffffff'},
        }

        navbar_config = navbar_colors.get(navbar_style, navbar_colors['dark'])

        # Generate CSS
        css_content = f""":root {{
    /* OPS Theme - Brand Colors */
    --ops-primary: {primary_color};
    --ops-secondary: {secondary_color};
    --ops-success: {success_color};
    --ops-warning: {warning_color};
    --ops-danger: {danger_color};

    /* OPS Theme - Navbar */
    --ops-navbar-bg: {navbar_config['bg']};
    --ops-navbar-text: {navbar_config['text']};

    /* OPS Theme - UI Elements */
    --ops-card-shadow: {shadow_map.get(card_shadow, shadow_map['medium'])};
    --ops-border-radius: {radius_map.get(border_radius, radius_map['rounded'])};
    --ops-border-radius-sm: calc({radius_map.get(border_radius, radius_map['rounded'])} / 2);
    --ops-border-radius-lg: calc({radius_map.get(border_radius, radius_map['rounded'])} * 1.5);

    /* OPS Theme - Report Styles */
    --ops-report-header-bg: {report_header_bg};

    /* OPS Theme - Derived Colors */
    --ops-primary-hover: color-mix(in srgb, {primary_color} 85%, black);
    --ops-secondary-hover: color-mix(in srgb, {secondary_color} 85%, black);
    --ops-primary-light: color-mix(in srgb, {primary_color} 10%, white);
    --ops-secondary-light: color-mix(in srgb, {secondary_color} 10%, white);
}}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {{
    :root {{
        --ops-primary-light: color-mix(in srgb, {primary_color} 20%, black);
        --ops-secondary-light: color-mix(in srgb, {secondary_color} 20%, black);
    }}
}}

/* Force dark mode class */
.ops-dark-mode {{
    --ops-primary-light: color-mix(in srgb, {primary_color} 20%, black);
    --ops-secondary-light: color-mix(in srgb, {secondary_color} 20%, black);
}}

/* Force light mode class */
.ops-light-mode {{
    --ops-primary-light: color-mix(in srgb, {primary_color} 10%, white);
    --ops-secondary-light: color-mix(in srgb, {secondary_color} 10%, white);
}}
"""

        return request.make_response(
            css_content,
            headers=[
                ('Content-Type', 'text/css; charset=utf-8'),
                ('Cache-Control', 'public, max-age=300'),  # Cache for 5 minutes
            ]
        )
