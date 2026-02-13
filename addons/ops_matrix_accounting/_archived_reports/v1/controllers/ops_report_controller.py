# -*- coding: utf-8 -*-
"""
OPS Framework - Report Web Controller
======================================
Handles HTML report rendering for UI View mode.
"""

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)


class OpsReportController(http.Controller):
    """Web controller for OPS corporate report HTML rendering"""

    @http.route('/ops/report/html/<string:template_xmlid>', type='http', auth='user')
    def report_html_view(self, template_xmlid, wizard_id=None, **kwargs):
        """
        Render report as HTML for UI View mode with toolbar.

        Args:
            template_xmlid (str): Full XML ID of report template
            wizard_id (int): Wizard record ID

        Returns:
            Response: HTML content with OPS corporate styling
        """
        if not wizard_id:
            return request.not_found("Missing wizard_id parameter")

        try:
            wizard_id = int(wizard_id)
        except (ValueError, TypeError):
            return request.not_found("Invalid wizard_id")

        # Get wizard model from template mapping
        wizard_model = self._get_wizard_model(template_xmlid)
        if not wizard_model:
            return request.not_found(f"Unknown template: {template_xmlid}")

        # Verify wizard exists and user has access
        try:
            wizard = request.env[wizard_model].browse(wizard_id)
            if not wizard.exists():
                return request.not_found("Wizard record not found")

            # Check access rights
            wizard.check_access_rights('read')
            wizard.check_access_rule('read')

        except AccessError as e:
            return request.render('http_routing.403', {'message': str(e)})

        # Validate wizard filters
        validation_result = wizard._validate_filters()
        if isinstance(validation_result, dict) and 'warning' in validation_result:
            return self._render_error(
                'Validation Error',
                validation_result.get('warning', {}).get('message', 'Validation failed')
            )

        # Security check (IT Admin Blindness)
        try:
            engine_name = wizard._get_engine_name()
            if engine_name:
                wizard._check_intelligence_access(engine_name)
        except AccessError as e:
            return request.render('http_routing.403', {'message': str(e)})

        # Generate report data
        try:
            report_data = wizard._get_report_data()
        except Exception as e:
            _logger.error(f"Error generating report data: {e}", exc_info=True)
            return self._render_error(
                'Report Generation Error',
                f'Failed to generate report: {str(e)}'
            )

        # Get report helpers for context
        helpers = request.env['ops.report.helpers']
        context = helpers.get_report_context(wizard, report_data)
        context['ui_view_mode'] = True
        context['wizard_id'] = wizard_id
        context['template_xmlid'] = template_xmlid

        # Render report template
        try:
            # Extract module and template name from XML ID
            if '.' in template_xmlid:
                module, template_name = template_xmlid.split('.', 1)
                full_template_id = f'{module}.{template_name}'
            else:
                full_template_id = template_xmlid

            html_content = request.env['ir.qweb']._render(full_template_id, context)
        except Exception as e:
            _logger.error(f"Error rendering template {template_xmlid}: {e}", exc_info=True)
            return self._render_error(
                'Template Rendering Error',
                f'Failed to render report template: {str(e)}'
            )

        # Wrap in UI View container with toolbar
        wrapped_html = self._wrap_ui_view(html_content, wizard, template_xmlid)

        return request.make_response(wrapped_html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])

    def _wrap_ui_view(self, html_content, wizard, template_xmlid):
        """
        Wrap report HTML in UI View container with toolbar.

        Args:
            html_content (str): Rendered report HTML
            wizard: Wizard record
            template_xmlid (str): Template XML ID

        Returns:
            str: Complete HTML page with toolbar
        """
        report_title = wizard.report_title if hasattr(wizard, 'report_title') else 'OPS Report'

        toolbar_html = f"""
        <div class="ops-report-toolbar" style="display: flex; justify-content: flex-end; gap: 12px;
             margin-bottom: 16px; padding: 12px; background: white; border-radius: 8px;
             box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <button onclick="window.print()"
                    style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;
                           background: #5B6BBB; color: white; border: none; border-radius: 6px;
                           font-size: 9pt; font-weight: 500; cursor: pointer;">
                Print PDF
            </button>
            <a href="/ops/report/excel/{template_xmlid}?wizard_id={wizard.id}"
               style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;
                      background: #16a34a; color: white; border: none; border-radius: 6px;
                      font-size: 9pt; font-weight: 500; text-decoration: none;">
                Export Excel
            </a>
            <button onclick="window.close()"
                    style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;
                           background: #6b7280; color: white; border: none; border-radius: 6px;
                           font-size: 9pt; font-weight: 500; cursor: pointer;">
                Close
            </button>
        </div>
        """

        # Use relative URL for CSS to avoid mixed content (HTTP/HTTPS mismatch)
        wrapper = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report_title} - OPS Framework</title>
            <link rel="stylesheet" href="/ops_matrix_accounting/static/src/css/ops_report.css"/>
            <style>
                body {{
                    margin: 0;
                    background: #f5f5f5;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                }}
                .ops-report-ui-view {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 24px;
                }}
                .ops-corporate-report {{
                    background: white;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    padding: 40px;
                }}
                @media print {{
                    body {{
                        background: white;
                    }}
                    .ops-report-toolbar {{
                        display: none !important;
                    }}
                    .ops-report-ui-view {{
                        padding: 0;
                        max-width: none;
                    }}
                    .ops-corporate-report {{
                        box-shadow: none;
                        border-radius: 0;
                        padding: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="ops-report-ui-view">
                {toolbar_html}
                {html_content}
            </div>
        </body>
        </html>
        """
        return wrapper

    def _get_wizard_model(self, template_xmlid):
        """
        Map report template XML ID to wizard model.

        Args:
            template_xmlid (str): Report template XML ID

        Returns:
            str: Wizard model name or None
        """
        # Extract template name from XML ID
        template_name = template_xmlid.split('.')[-1] if '.' in template_xmlid else template_xmlid

        # Mapping of report templates to wizard models
        mapping = {
            # Financial Intelligence (Enhanced GL Wizard)
            'report_general_ledger': 'ops.general.ledger.wizard.enhanced',
            'report_trial_balance': 'ops.general.ledger.wizard.enhanced',
            'report_profit_loss': 'ops.general.ledger.wizard.enhanced',
            'report_balance_sheet': 'ops.general.ledger.wizard.enhanced',
            'report_cash_flow': 'ops.general.ledger.wizard.enhanced',
            'report_aged_receivable': 'ops.general.ledger.wizard.enhanced',
            'report_aged_payable': 'ops.general.ledger.wizard.enhanced',
            'report_partner_ledger': 'ops.general.ledger.wizard.enhanced',
            'report_statement_account': 'ops.general.ledger.wizard.enhanced',

            # Corporate Financial Intelligence
            'report_general_ledger_corporate': 'ops.general.ledger.wizard.enhanced',
            'report_trial_balance_corporate': 'ops.general.ledger.wizard.enhanced',
            'report_profit_loss_corporate': 'ops.general.ledger.wizard.enhanced',
            'report_balance_sheet_corporate': 'ops.general.ledger.wizard.enhanced',
            'report_cash_flow_corporate': 'ops.general.ledger.wizard.enhanced',
            'report_aged_partner_corporate': 'ops.general.ledger.wizard.enhanced',

            # V2 Financial Intelligence
            'report_trial_balance_v2': 'ops.general.ledger.wizard.enhanced',
            'report_profit_loss_v2': 'ops.general.ledger.wizard.enhanced',
            'report_balance_sheet_v2': 'ops.general.ledger.wizard.enhanced',
            'report_cash_flow_v2': 'ops.general.ledger.wizard.enhanced',
            'report_aged_partner_v2': 'ops.general.ledger.wizard.enhanced',

            # Treasury Intelligence
            'report_pdc_registry': 'ops.treasury.report.wizard',
            'report_pdc_maturity': 'ops.treasury.report.wizard',
            'report_pdc_on_hand': 'ops.treasury.report.wizard',

            # Asset Intelligence
            'report_asset_register': 'ops.asset.report.wizard',
            'report_depreciation_schedule': 'ops.asset.report.wizard',
            'report_asset_disposal': 'ops.asset.report.wizard',

            # Inventory Intelligence
            'report_stock_valuation': 'ops.inventory.report.wizard',
            'report_inventory_aging': 'ops.inventory.report.wizard',
            'report_inventory_movement': 'ops.inventory.report.wizard',
            'report_negative_stock': 'ops.inventory.report.wizard',

            # Daily Books
            'report_cash_book': 'ops.cash.book.wizard',
            'report_day_book': 'ops.day.book.wizard',
            'report_bank_book': 'ops.bank.book.wizard',
        }

        return mapping.get(template_name)

    @http.route('/ops/report/excel/<string:template_xmlid>', type='http', auth='user')
    def report_excel_download(self, template_xmlid, wizard_id=None, **kwargs):
        """
        Generate and download Excel export for report.

        Args:
            template_xmlid (str): Report template XML ID
            wizard_id (int): Wizard record ID

        Returns:
            Response: Excel file download
        """
        if not wizard_id:
            return request.not_found("Missing wizard_id parameter")

        try:
            wizard_id = int(wizard_id)
        except (ValueError, TypeError):
            return request.not_found("Invalid wizard_id")

        wizard_model = self._get_wizard_model(template_xmlid)
        if not wizard_model:
            return request.not_found(f"Unknown template: {template_xmlid}")

        try:
            wizard = request.env[wizard_model].browse(wizard_id)
            if not wizard.exists():
                return request.not_found("Wizard record not found")

            # Check access
            wizard.check_access_rights('read')

            # Call wizard's Excel export method
            if hasattr(wizard, 'action_export_excel'):
                return wizard.action_export_excel()
            else:
                raise UserError("Excel export not available for this report")

        except Exception as e:
            _logger.error(f"Error generating Excel export: {e}", exc_info=True)
            return request.not_found(str(e))

    def _render_error(self, title, message):
        """
        Render simple error page.

        Args:
            title (str): Error title
            message (str): Error message

        Returns:
            Response: HTML error page
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title} - OPS Framework</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    background: #f5f5f5;
                }}
                .error-container {{
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 600px;
                    text-align: center;
                }}
                h1 {{
                    color: #dc2626;
                    margin: 0 0 16px;
                }}
                p {{
                    color: #6b7280;
                    line-height: 1.6;
                }}
                button {{
                    margin-top: 24px;
                    padding: 12px 24px;
                    background: #5B6BBB;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>{title}</h1>
                <p>{message}</p>
                <button onclick="window.close()">Close Window</button>
            </div>
        </body>
        </html>
        """
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])
