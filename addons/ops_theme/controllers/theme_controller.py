# -*- coding: utf-8 -*-
"""
OPS Theme Controller
====================
Handles favicon serving for white-label branding.
"""

import base64
from odoo import http
from odoo.http import request


class OPSThemeController(http.Controller):
    """Controller for OPS Theme: favicon serving."""

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
