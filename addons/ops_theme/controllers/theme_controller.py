# -*- coding: utf-8 -*-
"""
OPS Theme Controller
====================
Handles:
1. Favicon serving for white-label branding
2. Theme toggle endpoints (color mode, chatter position) with sudo()
"""

import base64
from odoo import http
from odoo.http import request


class OPSThemeController(http.Controller):
    """Controller for OPS Theme."""

    # =========================================================================
    # FAVICON ROUTES
    # =========================================================================

    @http.route('/ops_theme/favicon', type='http', auth='public', cors='*')
    def favicon(self, **kwargs):
        """
        Serve company favicon or redirect to default.

        Returns the company's custom favicon if one is uploaded,
        otherwise redirects to Odoo's default favicon.
        """
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
    def theme_variables(self, **kwargs):
        """Generate dynamic CSS variables from company settings."""
        company_id = request.env.company.id if request.env.company else 1
        company = request.env['res.company'].sudo().browse(company_id)

        # Brand colors
        primary = company.ops_primary_color or '#1e293b'
        secondary = company.ops_secondary_color or '#3b82f6'
        success = company.ops_success_color or '#10b981'
        warning = company.ops_warning_color or '#f59e0b'
        danger = company.ops_danger_color or '#ef4444'

        # Layout settings
        card_shadow = company.ops_card_shadow or 'medium'
        border_radius = company.ops_border_radius or 'rounded'

        shadow_map = {
            'none': 'none',
            'light': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'heavy': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        }
        radius_map = {
            'sharp': '0px',
            'rounded': '8px',
            'pill': '16px',
        }

        css = f""":root {{
    --ops-primary: {primary};
    --ops-secondary: {secondary};
    --ops-success: {success};
    --ops-warning: {warning};
    --ops-danger: {danger};
    --ops-card-shadow: {shadow_map.get(card_shadow, shadow_map['medium'])};
    --ops-border-radius: {radius_map.get(border_radius, radius_map['rounded'])};
    --ops-btn-radius: {radius_map.get(border_radius, radius_map['rounded'])};
}}
"""
        return request.make_response(
            css,
            headers=[
                ('Content-Type', 'text/css'),
                ('Cache-Control', 'public, max-age=3600'),
            ]
        )

    # =========================================================================
    # THEME TOGGLE ROUTES (with sudo() to bypass permission issues)
    # =========================================================================

    @http.route('/ops_theme/toggle_color_mode', type='jsonrpc', auth='user')
    def toggle_color_mode(self, mode=None):
        """
        Toggle color mode between light and dark.

        Uses sudo() to bypass SELF_WRITEABLE_FIELDS restrictions which
        don't work reliably with ORM.write from the frontend.

        Args:
            mode: Optional explicit mode ('light' or 'dark').
                  If not provided, toggles current mode.

        Returns:
            dict with success status and new mode value.
        """
        user = request.env.user

        if mode is None:
            # Toggle: if current is dark, switch to light, and vice versa
            current = user.ops_color_mode or 'light'
            mode = 'dark' if current == 'light' else 'light'

        # Validate mode
        if mode not in ('light', 'dark'):
            mode = 'light'

        # Write to database using sudo to bypass permission issues
        user.sudo().write({'ops_color_mode': mode})

        return {
            'success': True,
            'mode': mode,
        }

    @http.route('/ops_theme/toggle_chatter', type='jsonrpc', auth='user')
    def toggle_chatter(self, position=None):
        """
        Toggle chatter position between bottom and side.

        Uses sudo() to bypass permission restrictions.

        Args:
            position: Optional explicit position ('bottom' or 'side').
                      If not provided, toggles current position.

        Returns:
            dict with success status and new position value.
        """
        user = request.env.user

        # Get current position
        current = user.ops_chatter_position or 'bottom'

        if position is None:
            # Toggle
            position = 'side' if current == 'bottom' else 'bottom'

        # Validate position
        if position not in ('bottom', 'side'):
            position = 'bottom'

        # Write using sudo
        user.sudo().write({'ops_chatter_position': position})

        return {
            'success': True,
            'position': position,
        }

    @http.route('/ops_theme/get_preferences', type='jsonrpc', auth='user')
    def get_preferences(self):
        """
        Get current user's theme preferences.

        Returns:
            dict with color_mode and chatter_position.
        """
        user = request.env.user

        return {
            'color_mode': user.ops_color_mode or 'light',
            'is_dark': (user.ops_color_mode == 'dark'),
            'chatter_position': user.ops_chatter_position or 'bottom',
            'chatter_is_bottom': (user.ops_chatter_position or 'bottom') == 'bottom',
        }
