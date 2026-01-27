# -*- coding: utf-8 -*-
"""
OPS Matrix Modern PDF Engine
============================

WeasyPrint-based PDF rendering engine that supports modern CSS:
- CSS Flexbox and Grid layouts
- CSS Variables (Custom Properties)
- Modern fonts and typography
- Full CSS3 support

This bypasses the wkhtmltopdf limitations for advanced PDF generation.

Author: Antigravity AI
Version: 1.0 (Phase 21)
"""

import base64
import logging
from io import BytesIO
from datetime import datetime

from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    _logger.warning("WeasyPrint not installed. Modern PDF generation will not be available.")


class OpsPdfEngine(models.AbstractModel):
    """
    WeasyPrint-based PDF Engine for Modern CSS Support.

    This abstract model provides methods to generate PDFs using WeasyPrint,
    allowing full CSS3 support including Flexbox, Grid, and CSS Variables.

    Usage:
        pdf_content = self.env['ops.pdf.engine'].generate_pdf(
            template_xmlid='module.template_id',
            data={'key': 'value'},
            filename='report.pdf'
        )
    """
    _name = 'ops.pdf.engine'
    _description = 'OPS Modern PDF Engine (WeasyPrint)'

    # =========================================================================
    # CORE PDF GENERATION
    # =========================================================================

    @api.model
    def generate_pdf(self, template_xmlid, data, filename="Report.pdf", css_xmlid=None):
        """
        Generate a PDF from a QWeb template using WeasyPrint.

        Args:
            template_xmlid (str): External ID of QWeb template (e.g., 'module.template_id')
            data (dict): Data context to pass to the template
            filename (str): Output filename
            css_xmlid (str): Optional external ID of CSS template to inject

        Returns:
            dict: Action to download the PDF or dict with binary content
                {
                    'pdf_content': bytes,
                    'filename': str,
                    'attachment_id': int (if saved)
                }

        Raises:
            UserError: If WeasyPrint is not installed
        """
        if not WEASYPRINT_AVAILABLE:
            raise UserError(_(
                "WeasyPrint library is not installed. "
                "Please install it with: pip install weasyprint"
            ))

        # Step 1: Render HTML from QWeb template
        html_content = self._render_qweb_to_html(template_xmlid, data)

        # Step 2: Inject CSS (modern styles)
        if css_xmlid:
            css_content = self._get_css_content(css_xmlid)
            html_content = self._inject_css(html_content, css_content)
        else:
            # Use default modern CSS
            css_content = self._get_default_modern_css()
            html_content = self._inject_css(html_content, css_content)

        # Step 3: Generate PDF with WeasyPrint
        pdf_content = self._weasyprint_render(html_content)

        # Step 4: Create attachment for download
        attachment = self._create_pdf_attachment(pdf_content, filename)

        return {
            'pdf_content': pdf_content,
            'filename': filename,
            'attachment_id': attachment.id,
        }

    @api.model
    def generate_pdf_action(self, template_xmlid, data, filename="Report.pdf", css_xmlid=None):
        """
        Generate PDF and return download action.

        Same as generate_pdf() but returns an ir.actions.act_url for immediate download.

        Args:
            template_xmlid (str): External ID of QWeb template
            data (dict): Data context for template
            filename (str): Output filename
            css_xmlid (str): Optional CSS template external ID

        Returns:
            dict: ir.actions.act_url action for download
        """
        result = self.generate_pdf(template_xmlid, data, filename, css_xmlid)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{result["attachment_id"]}?download=true',
            'target': 'new',
        }

    @api.model
    def generate_pdf_from_html(self, html_content, filename="Report.pdf", inject_default_css=True):
        """
        Generate PDF directly from HTML string.

        Useful when you have pre-rendered HTML and just need PDF conversion.

        Args:
            html_content (str): Full HTML document string
            filename (str): Output filename
            inject_default_css (bool): Whether to inject default modern CSS

        Returns:
            dict: Same as generate_pdf()
        """
        if not WEASYPRINT_AVAILABLE:
            raise UserError(_(
                "WeasyPrint library is not installed. "
                "Please install it with: pip install weasyprint"
            ))

        if inject_default_css:
            css_content = self._get_default_modern_css()
            html_content = self._inject_css(html_content, css_content)

        pdf_content = self._weasyprint_render(html_content)
        attachment = self._create_pdf_attachment(pdf_content, filename)

        return {
            'pdf_content': pdf_content,
            'filename': filename,
            'attachment_id': attachment.id,
        }

    # =========================================================================
    # HTML RENDERING
    # =========================================================================

    @api.model
    def _render_qweb_to_html(self, template_xmlid, data):
        """
        Render a QWeb template to HTML string.

        Args:
            template_xmlid (str): Template external ID
            data (dict): Context data

        Returns:
            str: Rendered HTML
        """
        # Add common context
        context = dict(data)
        context.update({
            'company': self.env.company,
            'user': self.env.user,
            'datetime': datetime,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        try:
            html = self.env['ir.qweb']._render(template_xmlid, context)
            return str(html)
        except Exception as e:
            _logger.error(f"Error rendering QWeb template {template_xmlid}: {e}")
            raise UserError(_(
                "Failed to render report template: %(error)s"
            ) % {'error': str(e)})

    # =========================================================================
    # CSS HANDLING
    # =========================================================================

    @api.model
    def _get_css_content(self, css_xmlid):
        """
        Get CSS content from a QWeb template.

        Args:
            css_xmlid (str): External ID of CSS template

        Returns:
            str: CSS content
        """
        try:
            css = self.env['ir.qweb']._render(css_xmlid, {})
            return str(css)
        except Exception as e:
            _logger.warning(f"Could not load CSS template {css_xmlid}: {e}")
            return ""

    @api.model
    def _get_default_modern_css(self):
        """
        Get the default modern CSS for WeasyPrint reports.

        This CSS uses modern features not available in wkhtmltopdf:
        - CSS Variables
        - Flexbox
        - Grid

        Returns:
            str: CSS content
        """
        # Try to load from data template first
        try:
            css = self.env['ir.qweb']._render(
                'ops_matrix_pdf_engine.ops_modern_css_template',
                {'company': self.env.company}
            )
            return str(css)
        except Exception:
            # Fallback to embedded CSS
            return self._get_embedded_modern_css()

    @api.model
    def _get_embedded_modern_css(self):
        """
        Fallback embedded modern CSS.

        Returns:
            str: CSS content with modern features
        """
        company = self.env.company
        primary_color = company.primary_color or '#0a1628'
        secondary_color = company.secondary_color or '#3b82f6'

        return f"""
        /* OPS Modern CSS - WeasyPrint Engine */
        :root {{
            --ops-primary: {primary_color};
            --ops-secondary: {secondary_color};
            --ops-success: #059669;
            --ops-danger: #dc2626;
            --ops-warning: #d97706;
            --ops-info: #2563eb;
            --ops-muted: #94a3b8;
            --ops-text-dark: #1e293b;
            --ops-text-light: #64748b;
            --ops-border: #e2e8f0;
            --ops-bg-light: #f8fafc;
        }}

        @page {{
            size: A4;
            margin: 15mm;
        }}

        body {{
            font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: var(--ops-text-dark);
            background: #ffffff;
        }}

        /* Modern Flexbox Layout */
        .ops-flex {{
            display: flex;
        }}

        .ops-flex-col {{
            display: flex;
            flex-direction: column;
        }}

        .ops-flex-row {{
            display: flex;
            flex-direction: row;
        }}

        .ops-flex-wrap {{
            flex-wrap: wrap;
        }}

        .ops-justify-between {{
            justify-content: space-between;
        }}

        .ops-justify-center {{
            justify-content: center;
        }}

        .ops-align-center {{
            align-items: center;
        }}

        .ops-gap-1 {{ gap: 4px; }}
        .ops-gap-2 {{ gap: 8px; }}
        .ops-gap-3 {{ gap: 12px; }}
        .ops-gap-4 {{ gap: 16px; }}
        .ops-gap-6 {{ gap: 24px; }}

        /* Modern Grid Layout */
        .ops-grid {{
            display: grid;
        }}

        .ops-grid-cols-2 {{
            grid-template-columns: repeat(2, 1fr);
        }}

        .ops-grid-cols-3 {{
            grid-template-columns: repeat(3, 1fr);
        }}

        .ops-grid-cols-4 {{
            grid-template-columns: repeat(4, 1fr);
        }}

        /* KPI Cards with Flexbox */
        .ops-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .ops-kpi-card {{
            background: #ffffff;
            border: 1px solid var(--ops-border);
            border-left: 4px solid var(--ops-secondary);
            border-radius: 6px;
            padding: 18px;
            display: flex;
            flex-direction: column;
        }}

        .ops-kpi-card.success {{
            border-left-color: var(--ops-success);
        }}

        .ops-kpi-card.danger {{
            border-left-color: var(--ops-danger);
        }}

        .ops-kpi-card.warning {{
            border-left-color: var(--ops-warning);
        }}

        .ops-kpi-label {{
            font-size: 9px;
            font-weight: 600;
            color: var(--ops-text-light);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .ops-kpi-value {{
            font-size: 24px;
            font-weight: bold;
            font-family: 'DejaVu Sans Mono', monospace;
            margin-top: 4px;
        }}

        .ops-kpi-value.positive {{
            color: var(--ops-success);
        }}

        .ops-kpi-value.negative {{
            color: var(--ops-danger);
        }}

        /* Cover Page */
        .ops-cover {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            background: linear-gradient(135deg, var(--ops-primary) 0%, #1a2744 100%);
            color: #ffffff;
            page-break-after: always;
        }}

        .ops-cover-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 35px 45px;
        }}

        .ops-cover-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .ops-cover-logo-box {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            background: linear-gradient(135deg, #1a2744 0%, var(--ops-secondary) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Georgia, serif;
            font-size: 24px;
            font-weight: bold;
        }}

        .ops-cover-title-area {{
            padding: 50px 45px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .ops-cover-doc-type {{
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--ops-secondary);
            margin-bottom: 10px;
        }}

        .ops-cover-main-title {{
            font-family: Georgia, serif;
            font-size: 36px;
            font-weight: bold;
            line-height: 1.2;
            margin: 0;
        }}

        /* Section Headers */
        .ops-section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            border-radius: 6px 6px 0 0;
            color: #ffffff;
        }}

        .ops-section-header.success {{
            background: var(--ops-success);
        }}

        .ops-section-header.danger {{
            background: var(--ops-danger);
        }}

        .ops-section-header.neutral {{
            background: var(--ops-primary);
        }}

        /* Data Tables */
        .ops-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10pt;
        }}

        .ops-table thead th {{
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
            color: var(--ops-text-light);
            text-transform: uppercase;
            font-size: 9pt;
            letter-spacing: 0.3px;
            border-bottom: 2px solid var(--ops-text-dark);
        }}

        .ops-table tbody td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--ops-border);
        }}

        .ops-table tbody tr:hover {{
            background: var(--ops-bg-light);
        }}

        .ops-table .text-end {{
            text-align: right;
        }}

        .ops-table .mono {{
            font-family: 'DejaVu Sans Mono', monospace;
        }}

        /* Summary Box */
        .ops-summary {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            border-radius: 8px;
            margin-top: 24px;
        }}

        .ops-summary.success {{
            background: linear-gradient(135deg, #047857 0%, var(--ops-success) 100%);
            color: #ffffff;
        }}

        .ops-summary.loss {{
            background: linear-gradient(135deg, #991b1b 0%, var(--ops-danger) 100%);
            color: #ffffff;
        }}

        .ops-summary-value {{
            font-family: 'DejaVu Sans Mono', monospace;
            font-size: 28pt;
            font-weight: 700;
        }}

        /* Utilities */
        .text-success {{ color: var(--ops-success); }}
        .text-danger {{ color: var(--ops-danger); }}
        .text-warning {{ color: var(--ops-warning); }}
        .text-muted {{ color: var(--ops-muted); }}

        .font-mono {{ font-family: 'DejaVu Sans Mono', monospace; }}
        .font-serif {{ font-family: Georgia, serif; }}

        .text-end {{ text-align: right; }}
        .text-center {{ text-align: center; }}
        """

    @api.model
    def _inject_css(self, html_content, css_content):
        """
        Inject CSS into HTML document.

        Args:
            html_content (str): HTML document
            css_content (str): CSS to inject

        Returns:
            str: HTML with CSS injected into <head>
        """
        style_tag = f"<style type='text/css'>\n{css_content}\n</style>"

        # Try to inject into existing <head>
        if '</head>' in html_content:
            return html_content.replace('</head>', f'{style_tag}\n</head>')
        elif '<head>' in html_content:
            return html_content.replace('<head>', f'<head>\n{style_tag}')
        else:
            # Wrap in minimal HTML structure
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    {style_tag}
</head>
<body>
{html_content}
</body>
</html>"""

    # =========================================================================
    # WEASYPRINT RENDERING
    # =========================================================================

    @api.model
    def _weasyprint_render(self, html_content):
        """
        Render HTML to PDF using WeasyPrint.

        Args:
            html_content (str): Full HTML document

        Returns:
            bytes: PDF binary content
        """
        try:
            html_doc = weasyprint.HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf()
            return pdf_bytes
        except Exception as e:
            _logger.error(f"WeasyPrint rendering error: {e}")
            raise UserError(_(
                "PDF generation failed: %(error)s"
            ) % {'error': str(e)})

    # =========================================================================
    # ATTACHMENT HANDLING
    # =========================================================================

    @api.model
    def _create_pdf_attachment(self, pdf_content, filename):
        """
        Create an ir.attachment for the PDF.

        Args:
            pdf_content (bytes): PDF binary
            filename (str): Attachment filename

        Returns:
            ir.attachment: Created attachment record
        """
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'mimetype': 'application/pdf',
            'res_model': 'ops.pdf.engine',
        })
        return attachment

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    @api.model
    def check_weasyprint(self):
        """
        Check if WeasyPrint is available.

        Returns:
            dict: Status information
        """
        if WEASYPRINT_AVAILABLE:
            return {
                'available': True,
                'version': weasyprint.__version__,
                'message': _("WeasyPrint is installed and ready."),
            }
        else:
            return {
                'available': False,
                'version': None,
                'message': _("WeasyPrint is not installed. Install with: pip install weasyprint"),
            }
