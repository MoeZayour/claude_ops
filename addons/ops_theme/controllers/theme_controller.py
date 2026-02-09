# -*- coding: utf-8 -*-
"""
OPS Theme Controller
====================
Serves dynamic theme assets and toggle endpoints.
"""

import base64
from odoo import http
from odoo.http import request


class OPSThemeController(http.Controller):
    """Controller for OPS Theme."""

    # =========================================================================
    # FAVICON
    # =========================================================================

    @http.route('/ops_theme/favicon', type='http', auth='public')
    def favicon(self, **kwargs):
        """Serve company favicon or redirect to default."""
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

        return request.redirect('/web/static/img/favicon.ico', code=302)

    @http.route('/favicon.ico', type='http', auth='public')
    def favicon_redirect(self, **kwargs):
        """Override default favicon.ico route."""
        return self.favicon(**kwargs)

    # =========================================================================
    # DYNAMIC CSS VARIABLES
    # =========================================================================

    @http.route('/ops_theme/variables.css', type='http', auth='public')
    def theme_variables(self, **kwargs):
        """
        Generate dynamic CSS variables from company settings.

        These override the defaults in _variables.scss.
        Uses no-cache headers to ensure fresh values.
        """
        company_id = request.env.company.id if request.env.company else 1
        company = request.env['res.company'].sudo().browse(company_id)

        # Get settings with defaults
        primary = company.ops_primary_color or '#1e293b'
        secondary = company.ops_secondary_color or '#3b82f6'
        success = company.ops_success_color or '#10b981'
        warning = company.ops_warning_color or '#f59e0b'
        danger = company.ops_danger_color or '#ef4444'

        # Extended palette
        bg = company.ops_bg_color or '#f1f5f9'
        surface = company.ops_surface_color or '#ffffff'
        text = company.ops_text_color or '#1e293b'
        border = company.ops_border_color or '#e2e8f0'
        accent2 = company.ops_accent2_color or '#60a5fa'
        btn = company.ops_btn_color or secondary

        # Layout settings
        card_shadow = company.ops_card_shadow or 'medium'
        border_radius = company.ops_border_radius or 'rounded'
        navbar_style = company.ops_navbar_style or 'dark'

        # Report header inherits from primary color
        report_header = primary

        # Shadow values
        shadow_map = {
            'none': 'none',
            'light': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'heavy': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        }

        # Radius values
        radius_map = {
            'sharp': '0px',
            'rounded': '8px',
            'pill': '16px',
        }

        # Convert hex to RGB for rgba() usage
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                return '0, 0, 0'
            return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

        # Navbar colors based on style
        # CRITICAL: "primary" style must use PRIMARY color (dark brand color), not secondary
        navbar_colors = {
            'dark': {'bg': primary, 'text': '#ffffff', 'hover': 'rgba(255, 255, 255, 0.1)'},
            'light': {'bg': '#f8fafc', 'text': '#1e293b', 'hover': 'rgba(0, 0, 0, 0.05)'},
            'primary': {'bg': primary, 'text': '#ffffff', 'hover': 'rgba(255, 255, 255, 0.1)'},
        }
        navbar = navbar_colors.get(navbar_style, navbar_colors['dark'])

        # Darken/lighten helpers for hover states
        secondary_hover = self._darken_color(secondary)
        primary_hover = self._darken_color(primary)

        # Button hover
        btn_hover = self._darken_color(btn)

        css = f"""/* OPS Theme Dynamic Variables - Generated from Settings */

:root {{
    /* Brand Colors */
    --ops-primary: {primary};
    --ops-primary-rgb: {hex_to_rgb(primary)};
    --ops-primary-hover: {primary_hover};
    --ops-secondary: {secondary};
    --ops-secondary-rgb: {hex_to_rgb(secondary)};
    --ops-secondary-hover: {secondary_hover};
    --ops-success: {success};
    --ops-success-rgb: {hex_to_rgb(success)};
    --ops-warning: {warning};
    --ops-warning-rgb: {hex_to_rgb(warning)};
    --ops-danger: {danger};
    --ops-danger-rgb: {hex_to_rgb(danger)};

    /* Extended Palette */
    --ops-bg: {bg};
    --ops-bg-rgb: {hex_to_rgb(bg)};
    --ops-surface: {surface};
    --ops-surface-rgb: {hex_to_rgb(surface)};
    --ops-bg-card: {surface};
    --ops-text: {text};
    --ops-text-rgb: {hex_to_rgb(text)};
    --ops-text-primary: {text};
    --ops-border: {border};
    --ops-border-rgb: {hex_to_rgb(border)};
    --ops-accent2: {accent2};
    --ops-accent2-rgb: {hex_to_rgb(accent2)};
    --ops-btn: {btn};
    --ops-btn-rgb: {hex_to_rgb(btn)};
    --ops-btn-hover: {btn_hover};

    /* Navbar */
    --ops-navbar-bg: {navbar['bg']};
    --ops-navbar-text: {navbar['text']};
    --ops-navbar-hover: {navbar['hover']};
    --ops-bg-navbar: {navbar['bg']};

    /* Layout */
    --ops-card-shadow: {shadow_map.get(card_shadow, shadow_map['medium'])};
    --ops-border-radius: {radius_map.get(border_radius, radius_map['rounded'])};
    --ops-radius-md: {radius_map.get(border_radius, radius_map['rounded'])};
    --ops-btn-radius: {radius_map.get(border_radius, radius_map['rounded'])};

    /* Reports */
    --ops-report-header-bg: {report_header};

    /* Navbar entry backgrounds — keeps menu tabs in sync with navbar */
    --NavBar-entry-backgroundColor: {navbar['bg']};
    --NavBar-entry-backgroundColor--hover: {navbar['hover']};
    --NavBar-entry-backgroundColor--focus: {navbar['hover']};
    --NavBar-entry-backgroundColor--active: {navbar['hover']};
}}

/* ===================================================================
   NAVBAR — Brand-specific overrides (both light and dark modes).
   Navbar stays branded in all modes — it's the company's bar.
   =================================================================== */
nav.o_main_navbar,
.o_main_navbar,
nav.o_main_navbar.d-print-none,
header.o_navbar {{
    background: {navbar['bg']} !important;
    background-color: {navbar['bg']} !important;
}}

/* Ensure nav entries match the navbar background (prevents two-tone bar) */
.o_main_navbar .o_menu_sections .o_nav_entry,
.o_main_navbar .o_menu_sections .dropdown-toggle {{
    background: {navbar['bg']} !important;
}}

/* Override discuss-specific navbar color (mail module dark mode leak) */
.o_web_client:has(.o-mail-Discuss) .o_main_navbar,
.o_web_client:has(.o-mail-Discuss) .o_control_panel {{
    background-color: {navbar['bg']} !important;
}}

.o_main_navbar .o_menu_brand {{
    color: {secondary} !important;
    font-weight: 700 !important;
}}

.o_main_navbar .o_menu_toggle,
.o_main_navbar .o_menu_systray .dropdown-toggle,
.o_main_navbar .o_navbar_apps_menu .dropdown-toggle {{
    color: {navbar['text']} !important;
}}

.o_menu_sections > button,
.o_menu_sections > a,
.o_menu_sections .o-dropdown > button,
.o_menu_sections .dropdown-toggle {{
    color: {navbar['text']} !important;
}}

.o_menu_sections > button:hover,
.o_menu_sections > a:hover,
.o_menu_sections .o-dropdown > button:hover {{
    background: {navbar['hover']} !important;
}}
"""
        return request.make_response(
            css,
            headers=[
                ('Content-Type', 'text/css; charset=utf-8'),
                ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                ('Pragma', 'no-cache'),
                ('Expires', '0'),
            ]
        )

    def _darken_color(self, hex_color, factor=0.85):
        """Darken a hex color by a factor."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return '#000000'
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darkened)

    # =========================================================================
    # THEME DATA ENDPOINT (for JavaScript)
    # =========================================================================

    @http.route('/ops_theme/data', type='jsonrpc', auth='public')
    def theme_data(self, **kwargs):
        """Return theme settings as JSON for JavaScript consumption."""
        company_id = request.env.company.id if request.env.company else 1
        company = request.env['res.company'].sudo().browse(company_id)

        return {
            'primary_color': company.ops_primary_color or '#1e293b',
            'secondary_color': company.ops_secondary_color or '#3b82f6',
            'success_color': company.ops_success_color or '#10b981',
            'warning_color': company.ops_warning_color or '#f59e0b',
            'danger_color': company.ops_danger_color or '#ef4444',
            'bg_color': company.ops_bg_color or '#f1f5f9',
            'surface_color': company.ops_surface_color or '#ffffff',
            'text_color': company.ops_text_color or '#1e293b',
            'border_color': company.ops_border_color or '#e2e8f0',
            'accent2_color': company.ops_accent2_color or '#60a5fa',
            'btn_color': company.ops_btn_color or company.ops_secondary_color or '#3b82f6',
            'navbar_style': company.ops_navbar_style or 'dark',
            'card_shadow': company.ops_card_shadow or 'medium',
            'border_radius': company.ops_border_radius or 'rounded',
        }

    # =========================================================================
    # USER PREFERENCE TOGGLES
    # =========================================================================

    @http.route('/ops_theme/toggle_color_mode', type='jsonrpc', auth='user')
    def toggle_color_mode(self, mode=None):
        """Toggle color mode between light and dark."""
        user = request.env.user

        if mode is None:
            current = user.ops_color_mode or 'light'
            mode = 'dark' if current == 'light' else 'light'

        if mode not in ('light', 'dark'):
            mode = 'light'

        user.sudo().write({'ops_color_mode': mode})
        return {'success': True, 'mode': mode}

    @http.route('/ops_theme/toggle_chatter', type='jsonrpc', auth='user')
    def toggle_chatter(self, position=None):
        """Toggle chatter position between bottom and side."""
        user = request.env.user
        current = user.ops_chatter_position or 'bottom'

        if position is None:
            position = 'side' if current == 'bottom' else 'bottom'

        if position not in ('bottom', 'side'):
            position = 'bottom'

        user.sudo().write({'ops_chatter_position': position})
        return {'success': True, 'position': position}

    @http.route('/ops_theme/get_preferences', type='jsonrpc', auth='user')
    def get_preferences(self):
        """Get current user's theme preferences."""
        user = request.env.user
        return {
            'color_mode': user.ops_color_mode or 'light',
            'is_dark': (user.ops_color_mode == 'dark'),
            'chatter_position': user.ops_chatter_position or 'bottom',
            'chatter_is_bottom': (user.ops_chatter_position or 'bottom') == 'bottom',
        }
