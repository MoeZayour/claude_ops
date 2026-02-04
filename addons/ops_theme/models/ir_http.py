# -*- coding: utf-8 -*-
"""
OPS Theme - ir.http Extension (v8.1.0)
======================================
Integrates theme preferences with Odoo 19's native systems.

ROOT CAUSE FIX:
- Odoo 19 CE's color_scheme() just returns 'light' (stub)
- webclient_rendering_context() returns {'color_scheme': ..., 'session_info': ...}
- web.layout template uses: <html t-att="html_data or {}">
- BUT html_data is NEVER set with data-color-mode attribute!

SOLUTION:
- Override webclient_rendering_context() to include html_data with data-color-mode
- This makes the CSS selector [data-color-mode="dark"] work
"""

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Extend ir.http to integrate OPS theme with Odoo 19's native systems."""

    _inherit = 'ir.http'

    def color_scheme(self):
        """
        Override Odoo 19's color_scheme method.
        
        Odoo 19 uses this in webclient_rendering_context() to provide the
        color_scheme value. The webclient_bootstrap template uses this to
        conditionally load web.assets_web_dark CSS.
        """
        if request and request.session and request.session.uid:
            try:
                user = self.env['res.users'].sudo().browse(request.session.uid)
                if user.ops_color_mode == 'dark':
                    return 'dark'
            except Exception:
                pass
        return 'light'  # Default

    def webclient_rendering_context(self):
        """
        Override to add html_data with data-color-mode attribute.
        
        This is THE KEY FIX:
        - web.layout template uses: <html t-att="html_data or {}">
        - By setting html_data = {'data-color-mode': 'dark'}, we make
          the CSS selector [data-color-mode="dark"] work!
        """
        # Get the base context from parent
        result = super().webclient_rendering_context()
        
        # Get color_scheme (which calls our override)
        color_scheme = result.get('color_scheme', 'light')
        
        # THE FIX: Set html_data with data-color-mode attribute
        # This makes <html t-att="html_data or {}"> render as <html data-color-mode="dark">
        result['html_data'] = {
            'data-color-mode': color_scheme,
        }
        
        return result

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
