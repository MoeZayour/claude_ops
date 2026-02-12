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
    # THEME DATA ENDPOINT
    # =========================================================================

    @http.route('/ops_theme/data', type='jsonrpc', auth='public')
    def theme_data(self, **kwargs):
        """Return theme settings as JSON."""
        company_id = request.env.company.id if request.env.company else 1
        company = request.env['res.company'].sudo().browse(company_id)
        return {
            'primary_color': company.ops_primary_color or '#1e293b',
            'secondary_color': company.ops_secondary_color or '#3b82f6',
            'success_color': company.ops_success_color or '#10b981',
            'warning_color': company.ops_warning_color or '#f59e0b',
            'danger_color': company.ops_danger_color or '#ef4444',
            'info_color': company.ops_info_color or '#06b6d4',
            'bg_color': company.ops_bg_color or '#f1f5f9',
            'surface_color': company.ops_surface_color or '#ffffff',
            'text_color': company.ops_text_color or '#1e293b',
            'border_color': company.ops_border_color or '#e2e8f0',
            'navbar_style': company.ops_navbar_style or 'dark',
            'card_shadow': company.ops_card_shadow or 'medium',
            'border_radius': company.ops_border_radius or 'rounded',
        }

    # =========================================================================
    # USER PREFERENCE TOGGLES
    # =========================================================================

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

    @http.route('/ops_theme/set_sidebar_type', type='jsonrpc', auth='user')
    def set_sidebar_type(self, type=None):
        """Save user sidebar type preference."""
        user = request.env.user
        if type not in ('invisible', 'small', 'large'):
            type = 'large'
        user.sudo().write({'ops_sidebar_type': type})
        return {'success': True, 'type': type}

    @http.route('/ops_theme/get_preferences', type='jsonrpc', auth='user')
    def get_preferences(self):
        """Get current user's theme preferences."""
        user = request.env.user
        return {
            'chatter_position': user.ops_chatter_position or 'bottom',
            'chatter_is_bottom': (user.ops_chatter_position or 'bottom') == 'bottom',
            'sidebar_type': user.ops_sidebar_type or 'large',
        }
