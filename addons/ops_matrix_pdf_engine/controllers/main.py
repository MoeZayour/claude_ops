# -*- coding: utf-8 -*-
"""
OPS Matrix PDF Engine - Controllers
===================================

HTTP controllers for PDF download and generation endpoints.

Author: Antigravity AI
Version: 1.0 (Phase 21)
"""

import base64
import json
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class OpsPdfEngineController(http.Controller):
    """
    HTTP Controller for OPS Modern PDF Engine.

    Provides endpoints for:
    - Direct PDF download
    - PDF generation from templates
    - PDF preview
    """

    @http.route('/ops/pdf/download/<int:attachment_id>', type='http', auth='user')
    def download_pdf(self, attachment_id, **kwargs):
        """
        Download a PDF attachment directly.

        Args:
            attachment_id (int): ID of the ir.attachment record

        Returns:
            HTTP Response with PDF content
        """
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)

        if not attachment.exists():
            return request.not_found()

        # Security check: verify user has access
        if attachment.res_model and attachment.res_id:
            try:
                request.env[attachment.res_model].browse(attachment.res_id).check_access_rights('read')
            except Exception:
                return request.not_found()

        pdf_content = base64.b64decode(attachment.datas)
        filename = attachment.name or 'report.pdf'

        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename="{filename}"'),
            ('Content-Length', len(pdf_content)),
        ]

        return Response(pdf_content, headers=headers)

    @http.route('/ops/pdf/generate', type='jsonrpc', auth='user', methods=['POST'])
    def generate_pdf(self, template_xmlid, data, filename="Report.pdf", css_xmlid=None, **kwargs):
        """
        Generate PDF from template via JSON-RPC.

        Args:
            template_xmlid (str): QWeb template external ID
            data (dict): Template context data
            filename (str): Output filename
            css_xmlid (str): Optional CSS template external ID

        Returns:
            dict: {
                'success': bool,
                'attachment_id': int,
                'download_url': str,
                'error': str (if failed)
            }
        """
        try:
            engine = request.env['ops.pdf.engine']
            result = engine.generate_pdf(template_xmlid, data, filename, css_xmlid)

            return {
                'success': True,
                'attachment_id': result['attachment_id'],
                'download_url': f'/web/content/{result["attachment_id"]}?download=true',
                'filename': result['filename'],
            }
        except Exception as e:
            _logger.error(f"PDF generation error: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    @http.route('/ops/pdf/preview/<int:attachment_id>', type='http', auth='user')
    def preview_pdf(self, attachment_id, **kwargs):
        """
        Preview PDF inline (without download prompt).

        Args:
            attachment_id (int): ID of the ir.attachment record

        Returns:
            HTTP Response with PDF for inline display
        """
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)

        if not attachment.exists():
            return request.not_found()

        pdf_content = base64.b64decode(attachment.datas)
        filename = attachment.name or 'report.pdf'

        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'inline; filename="{filename}"'),
            ('Content-Length', len(pdf_content)),
        ]

        return Response(pdf_content, headers=headers)

    @http.route('/ops/pdf/check', type='jsonrpc', auth='user', methods=['POST'])
    def check_weasyprint(self, **kwargs):
        """
        Check WeasyPrint availability.

        Returns:
            dict: WeasyPrint status information
        """
        engine = request.env['ops.pdf.engine']
        return engine.check_weasyprint()

    @http.route('/ops/pdf/generate_from_wizard', type='jsonrpc', auth='user', methods=['POST'])
    def generate_from_wizard(self, wizard_model, wizard_id, report_type='standard', **kwargs):
        """
        Generate PDF from a report wizard.

        This endpoint allows wizards to generate PDFs using the modern engine.

        Args:
            wizard_model (str): Technical name of the wizard model
            wizard_id (int): ID of the wizard record
            report_type (str): Type of report to generate

        Returns:
            dict: Generation result with download URL
        """
        try:
            wizard = request.env[wizard_model].browse(wizard_id)
            if not wizard.exists():
                return {'success': False, 'error': 'Wizard not found'}

            # Check if wizard has modern PDF method
            if hasattr(wizard, 'action_print_modern_pdf'):
                result = wizard.action_print_modern_pdf()
                return {
                    'success': True,
                    'action': result,
                }
            else:
                return {
                    'success': False,
                    'error': 'Wizard does not support modern PDF generation',
                }

        except Exception as e:
            _logger.error(f"Wizard PDF generation error: {e}")
            return {
                'success': False,
                'error': str(e),
            }
