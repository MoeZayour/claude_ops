# -*- coding: utf-8 -*-
"""
OPS Universal Report Bridge Parser
===================================

Single bridge between ``ir.actions.report`` and every OPS report wizard.

The wizard owns the data logic via ``_get_report_data()``.  This bridge just:

1. Validates the wizard model against a security whitelist.
2. Loads the wizard record.
3. Calls ``wizard._get_report_data()`` to obtain the data contract dict.
4. Passes the dict (plus helpers and colors) to the QWeb template.

One bridge replaces the 15+ individual parsers from v1.
"""

from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# Security whitelist — only these wizard models may generate reports
ALLOWED_WIZARD_MODELS = [
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


class OpsReportBridge(models.AbstractModel):
    """Universal bridge parser for all OPS corporate reports.

    This is the ONLY parser in the report engine.  It connects
    ``ir.actions.report`` to ``wizard._get_report_data()`` via a thin bridge.

    The wizard owns the data logic.  This bridge just:

    1. Validates the wizard model and record.
    2. Calls ``wizard._get_report_data()``.
    3. Passes the data-contract dict to the QWeb template.
    """
    _name = 'report.ops_matrix_accounting.report_document'
    _description = 'OPS Universal Report Bridge'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Bridge between ir.actions.report and wizard data engine.

        Args:
            docids: List of wizard record IDs (from report action)
            data: Dict with ``wizard_model`` and optionally ``wizard_id``

        Returns:
            dict with keys: doc_ids, doc_model, docs, data, helpers, colors, meta
        """
        data = data or {}
        wizard_model = data.get('wizard_model') or self.env.context.get('ops_wizard_model') or self.env.context.get('active_model')
        wizard_id = data.get('wizard_id') or (docids[0] if docids else self.env.context.get('active_id'))

        # Security: only allow whitelisted wizard models
        if wizard_model not in ALLOWED_WIZARD_MODELS:
            _logger.warning("Blocked report request for non-whitelisted model: %s", wizard_model)
            raise UserError(_("Invalid report configuration."))

        if not wizard_id:
            raise UserError(_("No report wizard record specified."))

        wizard = self.env[wizard_model].browse(int(wizard_id))
        if not wizard.exists():
            raise UserError(_("Report wizard record not found (ID: %s).") % wizard_id)

        # Wizard generates the data contract
        try:
            report_data = wizard._get_report_data()
        except UserError:
            raise
        except Exception as e:
            _logger.error("Report data generation failed for %s: %s", wizard_model, e, exc_info=True)
            raise UserError(_("Failed to generate report: %s") % str(e))

        return {
            'doc_ids': docids or [wizard_id],
            'doc_model': wizard_model,
            'docs': wizard,
            'data': report_data,
            'helpers': self.env['ops.report.helpers'],
            'colors': report_data.get('colors', {}),
            'meta': report_data.get('meta', {}),
        }
