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
    # DYNAMIC CSS VARIABLES — :root declarations only
    # =========================================================================

    @http.route('/ops_theme/variables.css', type='http', auth='public')
    def theme_variables(self, **kwargs):
        """
        Generate CSS custom properties from company settings.
        Only :root variable declarations — no component rules.
        """
        company_id = request.env.company.id if request.env.company else 1
        company = request.env['res.company'].sudo().browse(company_id)

        # Colors with defaults
        primary = company.ops_primary_color or '#1e293b'
        secondary = company.ops_secondary_color or '#3b82f6'
        success = company.ops_success_color or '#10b981'
        warning = company.ops_warning_color or '#f59e0b'
        danger = company.ops_danger_color or '#ef4444'
        bg = company.ops_bg_color or '#f1f5f9'
        surface = company.ops_surface_color or '#ffffff'
        text = company.ops_text_color or '#1e293b'
        border = company.ops_border_color or '#e2e8f0'
        accent2 = company.ops_accent2_color or '#60a5fa'
        btn = company.ops_btn_color or secondary

        # Layout settings
        navbar_style = company.ops_navbar_style or 'dark'
        card_shadow = company.ops_card_shadow or 'medium'
        border_radius = company.ops_border_radius or 'rounded'

        # Helpers
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                return '0, 0, 0'
            return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

        # Navbar bg based on style
        navbar_bg = primary if navbar_style != 'light' else '#f8fafc'
        navbar_text = '#ffffff' if navbar_style != 'light' else '#1e293b'

        # Hover states
        secondary_hover = self._darken_color(secondary)
        btn_hover = self._darken_color(btn)

        # Shadow/radius maps
        shadow_map = {
            'none': 'none',
            'light': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'heavy': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        }
        radius_map = {'sharp': '0px', 'rounded': '8px', 'pill': '16px'}

        css = f"""/* OPS Theme — Dynamic CSS Variables */
:root {{
    --ops-primary: {primary};
    --ops-primary-rgb: {hex_to_rgb(primary)};
    --ops-primary-hover: {self._darken_color(primary)};
    --ops-secondary: {secondary};
    --ops-secondary-rgb: {hex_to_rgb(secondary)};
    --ops-secondary-hover: {secondary_hover};
    --ops-success: {success};
    --ops-success-rgb: {hex_to_rgb(success)};
    --ops-warning: {warning};
    --ops-warning-rgb: {hex_to_rgb(warning)};
    --ops-danger: {danger};
    --ops-danger-rgb: {hex_to_rgb(danger)};
    --ops-bg: {bg};
    --ops-bg-rgb: {hex_to_rgb(bg)};
    --ops-surface: {surface};
    --ops-bg-card: {surface};
    --ops-text: {text};
    --ops-text-primary: {text};
    --ops-border: {border};
    --ops-border-rgb: {hex_to_rgb(border)};
    --ops-accent2: {accent2};
    --ops-btn: {btn};
    --ops-btn-rgb: {hex_to_rgb(btn)};
    --ops-btn-hover: {btn_hover};
    --ops-navbar-bg: {navbar_bg};
    --ops-navbar-text: {navbar_text};
    --ops-card-shadow: {shadow_map.get(card_shadow, shadow_map['medium'])};
    --ops-border-radius: {radius_map.get(border_radius, radius_map['rounded'])};
    --ops-radius-md: {radius_map.get(border_radius, radius_map['rounded'])};
    --ops-report-header-bg: {primary};
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
