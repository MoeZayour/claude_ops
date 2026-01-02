# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """
        Override PDF rendering to enforce governance rules.
        
        This prevents users from printing/downloading PDFs of documents
        that violate active governance rules or require pending approvals.
        
        Blocks print for: sale.order, purchase.order, account.move
        """
        # ADMIN BYPASS: Allow administrators to print anything
        if self.env.su or self.env.user.has_group('base.group_system'):
            return super()._render_qweb_pdf(report_ref, res_ids, data)
        
        # Determine the model being reported
        report_sudo = self._get_report(report_ref)
        target_model = report_sudo.model
        
        # Only enforce for governance-enabled models
        governed_models = ['sale.order', 'purchase.order', 'account.move']
        
        if target_model in governed_models and res_ids:
            # Get the records being printed
            records = self.env[target_model].browse(res_ids)
            
            for record in records:
                # Check if model has governance mixin
                if hasattr(record, '_enforce_governance_rules'):
                    try:
                        # Check for pending approvals
                        if hasattr(record, 'approval_request_ids'):
                            pending_approvals = record.approval_request_ids.filtered(
                                lambda a: a.state == 'pending'
                            )
                            
                            if pending_approvals:
                                rule_names = ', '.join(pending_approvals.mapped('rule_id.name'))
                                raise UserError(_(
                                    "🚫 COMMITMENT BLOCKED: You cannot Print or Download PDF for "
                                    "document '%s' until it satisfies company Governance Rules.\n\n"
                                    "⏳ Pending Approval: %s\n\n"
                                    "This document is locked for external commitment (email or print) "
                                    "until the required approvals are granted."
                                ) % (record.display_name, rule_names))
                        
                        # Enforce governance rules (will raise UserError if blocked)
                        # Use 'on_write' trigger as it's the most comprehensive
                        record._enforce_governance_rules(record, trigger_type='on_write')
                        
                        _logger.info(
                            "OPS Governance: PDF generation allowed for %s %s after rules check",
                            target_model, record.id
                        )
                        
                    except UserError as e:
                        # Re-raise with enhanced message for print context
                        error_message = str(e)
                        if 'requires approval' in error_message.lower():
                            # This is an approval requirement - enhance the message
                            raise UserError(_(
                                "🚫 COMMITMENT BLOCKED: You cannot Print or Email document '%s'.\n\n"
                                "%s\n\n"
                                "External commitment (print/email) is blocked until approval is granted."
                            ) % (record.display_name, error_message))
                        else:
                            # Re-raise the original error with print context
                            raise UserError(_(
                                "🚫 COMMITMENT BLOCKED: You cannot Print document '%s'.\n\n%s"
                            ) % (record.display_name, error_message))
        
        # If all checks pass, proceed with PDF generation
        return super()._render_qweb_pdf(report_ref, res_ids, data)
