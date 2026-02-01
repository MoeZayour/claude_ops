# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Extend ir.http to pass user theme preferences to frontend session."""

    _inherit = 'ir.http'

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
