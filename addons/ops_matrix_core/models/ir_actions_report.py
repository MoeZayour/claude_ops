# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    # External document reports — template-only, no parser needed
    _OPS_EXTERNAL_REPORTS = {
        'ops_matrix_accounting.report_ops_invoice',
        'ops_matrix_accounting.report_ops_payment',
    }

    def _get_rendering_context_model(self, report):
        """Route OPS wizard reports to bridge parser.

        External document reports (invoice, payment) are template-only
        and must NOT be routed through the bridge.
        """
        if (report.report_name
                and report.report_name.startswith('ops_matrix_accounting.report_')
                and report.report_name not in self._OPS_EXTERNAL_REPORTS):
            bridge = self.env.get('report.ops_matrix_accounting.report_document')
            if bridge is not None:
                return bridge.with_context(ops_wizard_model=report.model)
        return super()._get_rendering_context_model(report)

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """Enforce governance rules before PDF generation."""
        if self.env.su or self.env.user.has_group('base.group_system'):
            return super()._render_qweb_pdf(report_ref, res_ids, data)

        report_sudo = self._get_report(report_ref)
        target_model = report_sudo.model
        governed_models = ['sale.order', 'purchase.order', 'account.move']

        if target_model in governed_models and res_ids:
            records = self.env[target_model].browse(res_ids)
            for record in records:
                if hasattr(record, '_enforce_governance_rules'):
                    try:
                        if hasattr(record, 'approval_request_ids'):
                            pending = record.approval_request_ids.filtered(
                                lambda a: a.state == 'pending'
                            )
                            if pending:
                                rules = ', '.join(pending.mapped('rule_id.name'))
                                raise UserError(_(
                                    "Cannot Print/Download '%s' — pending approval: %s"
                                ) % (record.display_name, rules))
                        record._enforce_governance_rules(record, trigger_type='on_write')
                    except UserError:
                        raise

        return super()._render_qweb_pdf(report_ref, res_ids, data)
