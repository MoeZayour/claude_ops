# -*- coding: utf-8 -*-
"""
OPS Theme - ir.http Extension
=============================
Integrates theme preferences with Odoo 19's native systems.
"""

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Extend ir.http to integrate OPS theme with Odoo 19's native systems."""

    _inherit = 'ir.http'

    def color_scheme(self):
        """
        Override Odoo 19's color_scheme method.
        
        Odoo 19 uses this to provide the default value for the color_scheme cookie.
        The webclient_bootstrap template uses webclient_rendering_context() which
        calls this method. We read from user's ops_color_mode field for persistence.
        """
        if request and request.session and request.session.uid:
            try:
                user = self.env['res.users'].sudo().browse(request.session.uid)
                if user.ops_color_mode == 'dark':
                    return 'dark'
            except Exception:
                pass
        return 'light'  # Default

    def session_info(self):
        """
        Override session_info to include OPS theme preferences.
        
        This makes ops_chatter_position available in session.ops_chatter_position
        on the frontend JavaScript.
        """
        result = super().session_info()
        
        # Only add for authenticated internal users
        if request and request.session and request.session.uid:
            try:
                user = self.env['res.users'].sudo().browse(request.session.uid)
                if user._is_internal():
                    result['ops_color_mode'] = user.ops_color_mode or 'light'
                    result['ops_chatter_position'] = user.ops_chatter_position or 'bottom'
            except Exception:
                # Fallback defaults
                result['ops_color_mode'] = 'light'
                result['ops_chatter_position'] = 'bottom'
        
        return result
