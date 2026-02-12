# -*- coding: utf-8 -*-
"""
OPS Theme - ir.http Extension
==============================
Integrates theme preferences with Odoo 19's native systems.
"""

import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    """Extend ir.http to integrate OPS theme."""

    _inherit = 'ir.http'

    def color_scheme(self):
        """Force light mode — dark mode disabled."""
        return 'light'

    def session_info(self):
        """Override to include OPS theme preferences in session."""
        result = super().session_info()

        if request and request.session and request.session.uid:
            try:
                user = self.env['res.users'].sudo().browse(request.session.uid)
                if user.exists() and user._is_internal():
                    result['ops_chatter_position'] = user.ops_chatter_position or ''
                    result['ops_sidebar_type'] = user.ops_sidebar_type or 'large'

                    company = user.company_id
                    result['ops_default_chatter_position'] = (
                        company.ops_default_chatter_position or 'bottom'
                    )
                    result['ops_sidebar_enabled'] = (
                        company.ops_sidebar_enabled
                        if company.ops_sidebar_enabled is not None
                        else True
                    )
                    # Feature toggles for JS components
                    result['ops_home_menu_enhanced'] = (
                        company.ops_home_menu_enhanced
                        if company.ops_home_menu_enhanced is not None
                        else True
                    )
                    result['ops_dialog_enhancements'] = (
                        company.ops_dialog_enhancements
                        if company.ops_dialog_enhancements is not None
                        else True
                    )
                    result['ops_chatter_enhanced'] = (
                        company.ops_chatter_enhanced
                        if company.ops_chatter_enhanced is not None
                        else True
                    )
                    result['ops_group_controls_enabled'] = (
                        company.ops_group_controls_enabled
                        if company.ops_group_controls_enabled is not None
                        else True
                    )
                    result['ops_auto_refresh_enabled'] = (
                        company.ops_auto_refresh_enabled
                        if company.ops_auto_refresh_enabled is not None
                        else False
                    )
            except Exception:
                _logger.debug(
                    'Failed to load OPS theme preferences for session_info',
                    exc_info=True,
                )
                result['ops_chatter_position'] = 'bottom'
                result['ops_sidebar_type'] = 'large'
                result['ops_default_chatter_position'] = 'bottom'
                result['ops_sidebar_enabled'] = True
                result['ops_home_menu_enhanced'] = True
                result['ops_dialog_enhancements'] = True
                result['ops_chatter_enhanced'] = True
                result['ops_group_controls_enabled'] = True
                result['ops_auto_refresh_enabled'] = False

        return result
