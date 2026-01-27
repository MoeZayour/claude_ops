# -*- coding: utf-8 -*-
"""
OPS Matrix Modern PDF Mixin
===========================

Mixin to add WeasyPrint-based PDF generation to report wizards.
Provides action_print_modern_pdf() method for wizards.

Author: Antigravity AI
Version: 1.0 (Phase 21)
"""

import logging
from datetime import datetime

from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpsPdfMixin(models.AbstractModel):
    """
    Mixin for Modern PDF Generation Support.

    Add this mixin to any wizard or model to enable WeasyPrint PDF generation.

    Usage:
        class MyWizard(models.TransientModel):
            _name = 'my.wizard'
            _inherit = ['ops.pdf.mixin']

            def action_print_modern_pdf(self):
                return super().action_print_modern_pdf()
    """
    _name = 'ops.pdf.mixin'
    _description = 'Modern PDF Generation Mixin'

    def action_print_modern_pdf(self):
        """
        Generate PDF using WeasyPrint modern engine.

        This method can be overridden in child classes to customize
        the template and data passed to the PDF engine.

        Returns:
            dict: ir.actions.act_url action for PDF download
        """
        self.ensure_one()

        # Get the PDF engine
        engine = self.env['ops.pdf.engine']

        # Check if WeasyPrint is available
        status = engine.check_weasyprint()
        if not status.get('available'):
            raise UserError(_(
                "WeasyPrint is not available. Please install it to use modern PDF generation.\n"
                "Install with: pip install weasyprint"
            ))

        # Get report data - child classes should implement _get_modern_pdf_data()
        if hasattr(self, '_get_modern_pdf_data'):
            data = self._get_modern_pdf_data()
        elif hasattr(self, '_get_report_data'):
            data = self._get_report_data()
        else:
            data = self._get_default_pdf_data()

        # Get template - child classes should implement _get_modern_pdf_template()
        if hasattr(self, '_get_modern_pdf_template'):
            template_xmlid = self._get_modern_pdf_template()
        else:
            template_xmlid = 'ops_matrix_pdf_engine.default_modern_report_template'

        # Generate filename
        if hasattr(self, '_get_modern_pdf_filename'):
            filename = self._get_modern_pdf_filename()
        else:
            report_title = data.get('report_title', 'Report')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{report_title}_{timestamp}.pdf"

        # Generate the PDF
        return engine.generate_pdf_action(
            template_xmlid=template_xmlid,
            data=data,
            filename=filename,
        )

    def _get_default_pdf_data(self):
        """
        Get default data for PDF generation.

        Override this in child classes to provide custom data.

        Returns:
            dict: Data context for the PDF template
        """
        return {
            'report_title': 'Report',
            'company': self.env.company,
            'user': self.env.user,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'wizard': self,
        }


class OpsBaseReportWizardModernPdf(models.AbstractModel):
    """
    Extension of ops.base.report.wizard to add modern PDF support.

    This is automatically inherited by all report wizards that extend the base.
    """
    _inherit = 'ops.base.report.wizard'

    def action_print_modern_pdf(self):
        """
        Generate PDF using WeasyPrint modern engine.

        Uses the wizard's _get_report_data() method for data
        and provides appropriate template based on report type.

        Returns:
            dict: ir.actions.act_url action for PDF download
        """
        self.ensure_one()

        # Get the PDF engine
        engine = self.env['ops.pdf.engine']

        # Check if WeasyPrint is available
        status = engine.check_weasyprint()
        if not status.get('available'):
            raise UserError(_(
                "WeasyPrint is not available. Please install it to use modern PDF generation.\n"
                "Install with: pip install weasyprint"
            ))

        # Get report data from the wizard
        report_data = self._get_report_data()

        # Enhance data with common context
        data = self._enhance_pdf_data(report_data)

        # Get template based on report type
        template_xmlid = self._get_modern_pdf_template()

        # Generate filename
        filename = self._generate_modern_pdf_filename(report_data)

        # Generate the PDF
        return engine.generate_pdf_action(
            template_xmlid=template_xmlid,
            data=data,
            filename=filename,
        )

    def _enhance_pdf_data(self, report_data):
        """
        Enhance report data with common context for PDF generation.

        Args:
            report_data: Raw report data from _get_report_data()

        Returns:
            dict: Enhanced data with company info, colors, etc.
        """
        company = self.env.company

        # Get company colors for theming
        primary_color = company.primary_color or '#0a1628'
        secondary_color = company.secondary_color or '#3b82f6'

        enhanced_data = dict(report_data)
        enhanced_data.update({
            'company': company,
            'company_name': company.name,
            'company_logo': company.logo,
            'currency': company.currency_id,
            'currency_symbol': company.currency_id.symbol,
            'user': self.env.user,
            'user_name': self.env.user.name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'wizard': self,

            # Theme colors
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'success_color': '#059669',
            'danger_color': '#dc2626',
            'warning_color': '#d97706',

            # PDF engine flag
            'modern_pdf': True,
            'engine': 'weasyprint',
        })

        return enhanced_data

    def _get_modern_pdf_template(self):
        """
        Get the QWeb template for modern PDF generation.

        Override in child classes to provide specific templates.

        Returns:
            str: Template external ID
        """
        # Default to a generic modern report template
        # Child classes should override this based on report_type
        report_type = getattr(self, 'report_type', 'generic')

        template_map = {
            'pl': 'ops_matrix_pdf_engine.modern_profit_loss_template',
            'bs': 'ops_matrix_pdf_engine.modern_balance_sheet_template',
            'tb': 'ops_matrix_pdf_engine.modern_trial_balance_template',
            'gl': 'ops_matrix_pdf_engine.modern_general_ledger_template',
            'cf': 'ops_matrix_pdf_engine.modern_cash_flow_template',
            'aged': 'ops_matrix_pdf_engine.modern_aged_balance_template',
            'partner': 'ops_matrix_pdf_engine.modern_partner_ledger_template',
            'soa': 'ops_matrix_pdf_engine.modern_soa_template',
        }

        # Return mapped template or default
        return template_map.get(report_type, 'ops_matrix_pdf_engine.modern_generic_report_template')

    def _generate_modern_pdf_filename(self, report_data):
        """
        Generate filename for the PDF.

        Args:
            report_data: Report data dictionary

        Returns:
            str: Filename for the PDF
        """
        report_title = report_data.get('report_title', 'Report')
        company_name = self.env.company.name
        date_from = report_data.get('date_from', '')
        date_to = report_data.get('date_to', '')

        # Clean filename
        safe_title = "".join(c if c.isalnum() or c in ' -_' else '_' for c in report_title)
        safe_company = "".join(c if c.isalnum() or c in ' -_' else '_' for c in company_name)

        if date_from and date_to:
            return f"{safe_title}_{safe_company}_{date_from}_to_{date_to}.pdf"
        else:
            timestamp = datetime.now().strftime('%Y%m%d')
            return f"{safe_title}_{safe_company}_{timestamp}.pdf"
