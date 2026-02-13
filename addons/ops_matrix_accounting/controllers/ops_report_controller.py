# -*- coding: utf-8 -*-
"""
OPS Report HTML View Controller
================================

HTTP controller that renders OPS corporate reports as HTML pages
viewable in a browser tab.  Provides a print toolbar with Print and
Close buttons that hide themselves when printing.

The controller validates the wizard model against a security whitelist,
loads the wizard, calls ``_get_report_data()``, selects the correct
shape template, and wraps the rendered body in an HTML chrome page.
"""

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)

# Security whitelist -- only these wizard models may render reports
ALLOWED_MODELS = [
    'ops.gl.report.wizard',
    'ops.tb.report.wizard',
    'ops.pnl.report.wizard',
    'ops.bs.report.wizard',
    'ops.cf.report.wizard',
    'ops.aged.report.wizard',
    'ops.partner.ledger.wizard',
    'ops.cash.book.wizard',
    'ops.day.book.wizard',
    'ops.bank.book.wizard',
    'ops.asset.report.wizard',
    'ops.inventory.report.wizard',
    'ops.treasury.report.wizard',
    'ops.budget.vs.actual.wizard',
    'ops.consolidation.intelligence.wizard',
]

SHAPE_TEMPLATES = {
    'lines': 'ops_matrix_accounting.ops_report_shape_lines',
    'hierarchy': 'ops_matrix_accounting.ops_report_shape_hierarchy',
    'matrix': 'ops_matrix_accounting.ops_report_shape_matrix',
}

# HTML chrome wrapper with print toolbar
HTML_WRAPPER = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; }}
        .ops-toolbar {{
            position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
            background: #1e293b; color: #fff; padding: 8px 16px;
            display: flex; align-items: center; gap: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .ops-toolbar button {{
            background: #3b82f6; color: #fff; border: none;
            padding: 6px 16px; border-radius: 4px; cursor: pointer;
            font-size: 13px; font-weight: 500;
        }}
        .ops-toolbar button:hover {{ background: #2563eb; }}
        .ops-toolbar button.btn-close-report {{
            background: #64748b;
        }}
        .ops-toolbar button.btn-close-report:hover {{ background: #475569; }}
        .ops-toolbar .toolbar-title {{
            font-size: 14px; font-weight: 600; flex: 1;
        }}
        .ops-report-body {{
            padding: 24px 32px; margin-top: 52px;
        }}
        @media print {{
            .ops-toolbar {{ display: none !important; }}
            .ops-report-body {{ margin-top: 0; padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="ops-toolbar">
        <span class="toolbar-title">{title}</span>
        <button onclick="window.print();">Print</button>
        <button class="btn-close-report" onclick="window.close();">Close</button>
    </div>
    <div class="ops-report-body">
        {body}
    </div>
</body>
</html>"""


class OpsReportController(http.Controller):
    """Controller for rendering OPS reports as HTML in a browser tab."""

    @http.route(
        '/ops/report/html/<string:wizard_model>/<int:wizard_id>',
        type='http',
        auth='user',
        website=False,
    )
    def report_html_view(self, wizard_model, wizard_id, **kwargs):
        """Render an OPS report as a full HTML page.

        Args:
            wizard_model (str): Dotted model name of the wizard.
            wizard_id (int): Database ID of the wizard record.

        Returns:
            HTTP response with rendered HTML.
        """
        # 1. Model whitelist check
        if wizard_model not in ALLOWED_MODELS:
            _logger.warning(
                "Blocked HTML report request for non-whitelisted model: %s",
                wizard_model,
            )
            return request.not_found(_("Invalid report type."))

        # 2. Load wizard and check existence
        try:
            wizard = request.env[wizard_model].browse(wizard_id)
        except KeyError:
            _logger.warning("Unknown model requested: %s", wizard_model)
            return request.not_found(_("Report type not found."))

        if not wizard.exists():
            return request.not_found(
                _("Report wizard record not found (ID: %s).") % wizard_id
            )

        # 3. Access check -- the wizard's own access rules apply via ORM;
        #    additionally verify the user can read the record.
        try:
            wizard.check_access_rights('read')
            wizard.check_access_rule('read')
        except AccessError:
            return request.not_found(_("You do not have access to this report."))

        # 4. Generate report data
        try:
            report_data = wizard._get_report_data()
        except UserError as e:
            return request.make_response(
                HTML_WRAPPER.format(
                    title=_('Report Error'),
                    body='<div style="color:#dc2626;padding:40px;font-size:14px;">'
                         '<strong>%s</strong></div>' % str(e),
                ),
                headers=[('Content-Type', 'text/html; charset=utf-8')],
            )
        except Exception as e:
            _logger.error(
                "HTML report generation failed for %s/%s: %s",
                wizard_model, wizard_id, e, exc_info=True,
            )
            return request.make_response(
                HTML_WRAPPER.format(
                    title=_('Report Error'),
                    body='<div style="color:#dc2626;padding:40px;font-size:14px;">'
                         '<strong>%s</strong></div>' % _("Failed to generate report."),
                ),
                headers=[('Content-Type', 'text/html; charset=utf-8')],
            )

        # 5. Select shape template
        meta = report_data.get('meta', {})
        shape = meta.get('shape', 'matrix')
        template_xmlid = SHAPE_TEMPLATES.get(shape, SHAPE_TEMPLATES['matrix'])

        # 6. Render QWeb template
        try:
            report_body = request.env['ir.qweb']._render(template_xmlid, {
                'data': report_data,
                'meta': meta,
                'colors': report_data.get('colors', {}),
                'helpers': request.env['ops.report.helpers'],
            })
        except Exception as e:
            _logger.error(
                "QWeb rendering failed for template %s: %s",
                template_xmlid, e, exc_info=True,
            )
            return request.make_response(
                HTML_WRAPPER.format(
                    title=_('Report Error'),
                    body='<div style="color:#dc2626;padding:40px;font-size:14px;">'
                         '<strong>%s</strong></div>' % _("Failed to render report template."),
                ),
                headers=[('Content-Type', 'text/html; charset=utf-8')],
            )

        # 7. Wrap in HTML chrome with toolbar
        report_title = meta.get('report_title', _('Report'))
        company_name = meta.get('company_name', '')
        page_title = '%s - %s' % (report_title, company_name) if company_name else report_title

        # Convert markup to string if needed
        body_str = str(report_body) if report_body else ''

        html_page = HTML_WRAPPER.format(
            title=page_title,
            body=body_str,
        )

        return request.make_response(
            html_page,
            headers=[('Content-Type', 'text/html; charset=utf-8')],
        )
