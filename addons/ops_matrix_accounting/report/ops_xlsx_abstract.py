# -*- coding: utf-8 -*-
"""
OPS Matrix - XLSX Report Abstract Base
=======================================

Custom abstract base class for XLSX reports without dependency on report_xlsx module.
Uses xlsxwriter directly for Excel generation.

This replaces the dependency on OCA's report_xlsx module which is not available.

Phase 5: Corporate Excel Design System
v19.0.5.0

Author: OPS Matrix Framework
"""

from odoo import models
from odoo.exceptions import UserError
from odoo.http import request
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("xlsxwriter not installed. XLSX reports will not work.")
    xlsxwriter = None


class OPSXlsxAbstract(models.AbstractModel):
    """
    Abstract model for XLSX report generation.

    Provides base functionality for generating Excel reports using xlsxwriter.
    Child classes must implement generate_xlsx_report() method.

    Usage:
        class MyXlsxReport(models.AbstractModel):
            _name = 'report.my_module.my_report_xlsx'
            _inherit = 'ops.xlsx.abstract'
            _description = 'My XLSX Report'

            def generate_xlsx_report(self, workbook, data, objects):
                sheet = workbook.add_worksheet('My Report')
                # ... generate report content
    """
    _name = 'ops.xlsx.abstract'
    _description = 'Abstract XLSX Report Base'

    def _get_objs_for_report(self, docids, data):
        """
        Get objects for report generation.

        Override this method in child classes to provide custom object retrieval.

        Args:
            docids: List of record IDs
            data: Report data dictionary

        Returns:
            recordset: Objects to pass to generate_xlsx_report()
        """
        if not docids:
            return self.env[self._report_model].browse()
        return self.env[self._report_model].browse(docids)

    def generate_xlsx_report(self, workbook, data, objects):
        """
        Generate XLSX report content.

        MUST be implemented by child classes.

        Args:
            workbook: xlsxwriter.Workbook instance
            data: Report data dictionary from wizard/action
            objects: Recordset of objects to report on
        """
        raise NotImplementedError("Subclass must implement generate_xlsx_report()")

    def _generate_xlsx_report(self, docids, data):
        """
        Internal method to generate XLSX file.

        This is called by Odoo's report system.

        Args:
            docids: List of record IDs
            data: Report data dictionary

        Returns:
            tuple: (file_content, 'xlsx')
        """
        if xlsxwriter is None:
            raise UserError("xlsxwriter Python library is not installed. Cannot generate Excel reports.")

        # Get objects for report
        objects = self._get_objs_for_report(docids, data)

        # Create in-memory file
        output = io.BytesIO()

        # Create workbook
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        try:
            # Call subclass implementation
            self.generate_xlsx_report(workbook, data, objects)
        except Exception as e:
            _logger.error(f"Error generating XLSX report {self._name}: {str(e)}", exc_info=True)
            raise UserError(f"Error generating Excel report: {str(e)}")
        finally:
            # Close workbook
            workbook.close()

        # Get file content
        output.seek(0)
        file_content = output.read()
        output.close()

        return file_content, 'xlsx'

    def _render_xlsx(self, docids, data=None):
        """
        Render XLSX report.

        Called by Odoo report system for report_type='xlsx'.

        Args:
            docids: List of record IDs
            data: Optional data dictionary

        Returns:
            tuple: (file_content, 'xlsx')
        """
        if data is None:
            data = {}

        return self._generate_xlsx_report(docids, data)

    @property
    def _report_model(self):
        """
        Get the model name for this report.

        Extracts model name from report name (report.module.report_name_xlsx).
        Override if needed.

        Returns:
            str: Model name
        """
        # Default: extract from _name (e.g., 'report.ops_matrix_accounting.report_asset_xlsx' -> 'ops.asset.report.wizard')
        # This is a fallback; child classes should define explicitly if needed
        parts = self._name.split('.')
        if len(parts) >= 3:
            # Try to infer model from report name
            # This may not always work; override in child class if needed
            return 'unknown.model'
        return 'unknown.model'
