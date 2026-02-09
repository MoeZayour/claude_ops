# -*- coding: utf-8 -*-
"""
OPS Theme - ir.http Extension
==============================
Integrates theme preferences with Odoo 19's native systems.

Key overrides:
- color_scheme(): Reads cookie to select dark/light CSS bundle
- session_info(): Adds user prefs + company defaults for JS consumption
"""

import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    """Extend ir.http to integrate OPS theme."""

    _inherit = 'ir.http'

    def color_scheme(self):
        """Override to respect user color preference for CSS bundle selection.

        Resolution order:
        1. color_scheme cookie (set by toggle JS, fastest)
        2. User DB preference (ops_color_mode on res.users)
        3. Company default (ops_default_color_mode on res.company)
        4. Odoo default ('light')
        """
        if request and hasattr(request, 'httprequest'):
            # 1. Cookie — already set by toggle, honor it
            scheme = request.httprequest.cookies.get('color_scheme')
            if scheme in ('dark', 'light'):
                return scheme

            # 2. User DB preference (no cookie yet — fresh session)
            if request.session and request.session.uid:
                try:
                    user = self.env['res.users'].sudo().browse(request.session.uid)
                    if user.exists() and user.ops_color_mode in ('dark', 'light'):
                        return user.ops_color_mode
                    # 3. Company default
                    company = user.company_id
                    if company.ops_default_color_mode in ('dark', 'light'):
                        return company.ops_default_color_mode
                except Exception:
                    _logger.debug('Failed to resolve color scheme from user/company preferences', exc_info=True)

        return super().color_scheme()

    def session_info(self):
        """Override to include OPS theme preferences in session."""
        result = super().session_info()

        if request and request.session and request.session.uid:
            try:
                user = self.env['res.users'].sudo().browse(request.session.uid)
                if user.exists() and user._is_internal():
                    # User-level preferences (empty string if not set)
                    result['ops_color_mode'] = user.ops_color_mode or ''
                    result['ops_chatter_position'] = user.ops_chatter_position or ''

                    # Company-level defaults (for new users with no preference)
                    company = user.company_id
                    result['ops_default_color_mode'] = company.ops_default_color_mode or 'light'
                    result['ops_default_chatter_position'] = company.ops_default_chatter_position or 'bottom'
            except Exception:
                _logger.debug('Failed to load OPS theme preferences for session_info', exc_info=True)
                result['ops_color_mode'] = 'light'
                result['ops_chatter_position'] = 'bottom'
                result['ops_default_color_mode'] = 'light'
                result['ops_default_chatter_position'] = 'bottom'

        return result
