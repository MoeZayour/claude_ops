# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Extend ir.http to integrate OPS theme with Odoo 19's native systems."""

    _inherit = 'ir.http'

    def color_scheme(self):
        """
        Override Odoo 19's color_scheme method.
        
        Odoo 19 uses a COOKIE named 'color_scheme' for dark mode.
        This method provides the default value for that cookie.
        We read from user's ops_color_mode field for persistence.
        """
        if request and request.session and request.session.uid:
            user = self.env['res.users'].sudo().browse(request.session.uid)
            # Convert our field format to Odoo's cookie format
            if user.ops_color_mode == 'dark':
                return 'dark'
        return 'light'  # Default

    @classmethod
    def _get_frontend_session_info(cls):
        """Add OPS theme preferences to frontend session info."""
        result = super()._get_frontend_session_info()
        result.update(cls._get_ops_theme_session_info())
        return result

    @classmethod
    def _get_backend_session_info(cls):
        """Add OPS theme preferences to backend session info."""
        result = super()._get_backend_session_info()
        result.update(cls._get_ops_theme_session_info())
        return result

    @classmethod
    def _get_ops_theme_session_info(cls):
        """Get OPS theme specific session info."""
        user = request.env.user
        return {
            'ops_color_mode': user.ops_color_mode or 'light',
            'ops_chatter_position': user.ops_chatter_position or 'bottom',
        }
