# -*- coding: utf-8 -*-
"""
OPS Matrix Core - Sale Order Approval Workflow
=================================================

Extends sale.order with approval workflow actions: request approval,
approve, reject, recall, and product bundle PDF generation.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from typing import Dict, Any
import base64
import io
import logging

_logger = logging.getLogger(__name__)

try:
    from pypdf import PdfMerger
except ImportError:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        PdfMerger = None


class SaleOrderApproval(models.Model):
    _inherit = 'sale.order'

    # ==========================================================================
    # APPROVAL WORKFLOW ACTIONS
    # ==========================================================================

    def action_request_approval(self):
        """
        Request approval for this sale order.
        Sets state to 'waiting_approval' and creates approval request.
        """
        self.ensure_one()

        if self.state not in ['draft', 'sent']:
            raise UserError(_("Approval can only be requested for draft or sent quotations."))

        # Find applicable approval rules
        ApprovalRule = self.env['ops.approval.rule']
        rules = ApprovalRule.search([
            ('active', '=', True),
            ('model_name', '=', 'sale.order'),
            ('company_id', '=', self.company_id.id)
        ])

        # Also check governance rules that require approval
        GovernanceRule = self.env['ops.governance.rule']
        gov_rules = GovernanceRule.search([
            ('active', '=', True),
            ('model_id.model', '=', 'sale.order'),
            ('require_approval', '=', True),
            ('company_id', '=', self.company_id.id)
        ])

        approval_request = None

        # Try approval rules first
        for rule in rules:
            if rule.check_requires_approval(self):
                approval_request = rule.create_approval_request(
                    self,
                    notes=_("Approval requested for Sale Order %s") % self.name
                )
                break

        # If no approval rule matched, try governance rules
        if not approval_request and gov_rules:
            for rule in gov_rules:
                result = rule.validate_record(self, trigger_type='on_write')
                if result.get('requires_approval'):
                    approval_request = rule.action_create_approval_request(
                        self,
                        'approval_workflow',
                        '\n'.join(result.get('warnings', []))
                    )
                    break

        # If still no request, create a generic one
        if not approval_request:
            # Find default approvers using robust ORM approach
            approvers = self.env['res.users']

            try:
                manager_group = self.env.ref('ops_matrix_core.group_ops_manager', raise_if_not_found=False)
                if manager_group:
                    group_data = manager_group.read(['users'])[0] if manager_group else {}
                    user_ids = group_data.get('users', [])
                    if user_ids:
                        approvers = self.env['res.users'].browse(user_ids).filtered(
                            lambda u: u.active and self.company_id.id in u.company_ids.ids
                        )[:5]
            except Exception:
                _logger.debug('Failed to resolve approvers from OPS Manager group', exc_info=True)

            # Fallback to admin user
            if not approvers:
                admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
                if admin_user and admin_user.active:
                    approvers = admin_user

            if not approvers:
                raise UserError(_(
                    "No approvers found. Please configure approval rules or manager users."
                ))

            approval_request = self.env['ops.approval.request'].create({
                'name': _("Approval Request: %s") % self.name,
                'model_name': 'sale.order',
                'res_id': self.id,
                'notes': _("Manual approval requested for Sale Order %s") % self.name,
                'approver_ids': [(6, 0, approvers.ids)],
                'requested_by': self.env.user.id,
            })

        # Update state and lock
        self.write({
            'state': 'waiting_approval',
            'approval_locked': True,
            'approval_request_id': approval_request.id,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approval Requested'),
                'message': _('Approval request created: %s') % approval_request.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_view_approvals(self):
        """View approval requests for this sale order."""
        self.ensure_one()
        return {
            'name': _('Approval Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.approval.request',
            'view_mode': 'list,form',
            'domain': [
                ('model_name', '=', 'sale.order'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_model_name': 'sale.order',
                'default_res_id': self.id,
                'create': False,
            },
            'target': 'current',
        }

    def action_approve(self):
        """Approve the sale order (from waiting_approval state)."""
        self.ensure_one()

        if self.state != 'waiting_approval':
            raise UserError(_("Only orders in 'Waiting Approval' state can be approved."))

        # Approve the linked request
        if self.approval_request_id:
            self.approval_request_id.action_approve()

        # Unlock and change state back to sent (or draft)
        self.with_context(approval_unlock=True).write({
            'state': 'sent',
            'approval_locked': False,
        })

        return True

    def action_reject_approval(self):
        """Reject the approval and return to draft."""
        self.ensure_one()

        if self.state != 'waiting_approval':
            raise UserError(_("Only orders in 'Waiting Approval' state can be rejected."))

        # Reject the linked request
        if self.approval_request_id:
            self.approval_request_id.action_reject()

        # Unlock and change state back to draft
        self.with_context(approval_unlock=True).write({
            'state': 'draft',
            'approval_locked': False,
        })

        return True

    def action_recall_approval(self):
        """
        Recall an approval request - allows the salesperson to pull back the
        request to make edits. Only works when state is 'waiting_approval'.
        """
        self.ensure_one()

        if self.state != 'waiting_approval':
            raise UserError(_("You can only recall orders that are waiting for approval."))

        # Cancel the related approval request
        if self.approval_request_id:
            try:
                self.approval_request_id.write({'state': 'cancelled'})
            except Exception as e:
                _logger.warning("Failed to cancel approval request: %s", str(e))

        # Unlock and return to draft state
        self.with_context(approval_unlock=True).write({
            'state': 'draft',
            'approval_locked': False,
        })

        _logger.info("OPS Governance: SO %s recalled from approval by user %s",
                     self.name, self.env.user.name)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approval Recalled'),
                'message': _('Order %s has been recalled. You can now make edits.') % self.name,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_print_product_bundle(self) -> Dict[str, Any]:
        """
        Bulk Product Doc Generator (Smart Merge):
        Generate a single merged PDF of product documents for a sale order,
        removing duplicates using SHA-1 checksums.
        """
        self.ensure_one()

        if not PdfMerger:
            raise UserError(_('PyPDF library is not installed. Cannot merge PDFs.'))

        # Collect all PDF attachments from products
        pdf_attachments = []
        seen_checksums = set()

        for line in self.order_line:
            product = line.product_id

            # Find PDF attachments linked to this product
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'product.product'),
                ('res_id', '=', product.id),
                ('mimetype', '=', 'application/pdf'),
            ])

            # Also check product template attachments
            if product.product_tmpl_id:
                template_attachments = self.env['ir.attachment'].search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', product.product_tmpl_id.id),
                    ('mimetype', '=', 'application/pdf'),
                ])
                attachments |= template_attachments

            # Deduplicate by checksum
            for attachment in attachments:
                checksum = attachment.checksum
                if checksum and checksum not in seen_checksums:
                    seen_checksums.add(checksum)
                    pdf_attachments.append(attachment)

        if not pdf_attachments:
            raise UserError(_('No PDF documents found for the products in this sale order.'))

        # Merge PDFs
        merger = PdfMerger()

        try:
            for attachment in pdf_attachments:
                pdf_data = base64.b64decode(attachment.datas)
                pdf_stream = io.BytesIO(pdf_data)
                merger.append(pdf_stream)

            # Get merged PDF output
            output_stream = io.BytesIO()
            merger.write(output_stream)
            merger.close()
            output_stream.seek(0)

            # Encode to base64
            merged_pdf_data = base64.b64encode(output_stream.read()).decode('utf-8')

            # Create attachment for the merged PDF
            attachment = self.env['ir.attachment'].create({
                'name': f'Product_Bundle_{self.name}.pdf',
                'type': 'binary',
                'datas': merged_pdf_data,
                'res_model': 'sale.order',
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })

            # Return action to open the merged PDF in a new tab
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }

        except Exception as e:
            raise UserError(_('Error merging PDFs: %s') % str(e))
