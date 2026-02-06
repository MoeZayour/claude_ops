# -*- coding: utf-8 -*-
"""
OPS Theme - ir.http Extension
==============================
Integrates theme preferences with Odoo 19's native systems.

Key overrides:
- session_info(): Adds ops_color_mode and ops_chatter_position
"""

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    """Extend ir.http to integrate OPS theme."""

    _inherit = 'ir.http'

    def session_info(self):
        """Override to include OPS theme preferences in session."""
        result = super().session_info()

        if request and request.session and request.session.uid:
            try:
                user = self.env['res.users'].sudo().browse(request.session.uid)
                if user.exists() and user._is_internal():
                    result['ops_color_mode'] = user.ops_color_mode or 'light'
                    result['ops_chatter_position'] = user.ops_chatter_position or 'bottom'
            except Exception:
                result['ops_color_mode'] = 'light'
                result['ops_chatter_position'] = 'bottom'

        return result
