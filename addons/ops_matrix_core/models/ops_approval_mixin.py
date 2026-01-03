from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsApprovalMixin(models.AbstractModel):
    """Mixin to add approval locking capability to any model."""
    
    _name = 'ops.approval.mixin'
    _description = 'OPS Approval Locking Mixin'
    
    approval_locked = fields.Boolean(
        string='Approval Locked',
        default=False,
        readonly=True,
        copy=False,
        tracking=True,
        help='When True, this document is locked pending approval. '
             'Locked documents cannot be edited, printed, or deleted. '
             'Only the requestor can recall (with reason) or approvers can approve/reject.'
    )
    
    approval_request_id = fields.Many2one(
        'ops.approval.request',
        string='Approval Request',
        readonly=True,
        copy=False,
        help='The active approval request for this document. '
             'Linked to track approval status and enable recall/rejection.'
    )
    
    def _check_approval_lock(self, operation='write'):
        """Check if operation is allowed on locked document.
        
        Args:
            operation: 'write', 'unlink', or 'print'
            
        Raises:
            UserError: If document is locked and user is not authorized
        """
        for record in self:
            if not record.approval_locked:
                continue
                
            # System operations allowed
            if self.env.su:
                continue
                
            # Approvers can modify approval_locked field itself (to unlock)
            if operation == 'write' and self.env.context.get('approval_unlock'):
                continue
                
            # Current user is requestor - allow recall only
            if record.approval_request_id and record.approval_request_id.requested_by == self.env.user:
                # Recall must be explicit action, not silent write
                if not self.env.context.get('approval_recall'):
                    raise UserError(_(
                        'This document is locked pending approval.\n\n'
                        'You cannot edit it directly. To make changes, you must:\n'
                        '1. Recall the approval request (with reason)\n'
                        '2. Make your changes\n'
                        '3. Re-submit for approval'
                    ))
            else:
                # Not requestor
                operation_name = {
                    'write': 'edited',
                    'unlink': 'deleted',
                    'print': 'printed'
                }.get(operation, operation)
                
                raise UserError(_(
                    'This document is locked pending approval and cannot be %s.\n\n'
                    'Approval Request: %s\n'
                    'Requested by: %s\n'
                    'Status: %s\n\n'
                    'Wait for approval or contact the requestor to recall the request.'
                ) % (
                    operation_name,
                    record.approval_request_id.name if record.approval_request_id else 'Unknown',
                    record.approval_request_id.requested_by.name if record.approval_request_id else 'Unknown',
                    record.approval_request_id.state if record.approval_request_id else 'Unknown'
                ))
    
    def write(self, vals):
        """Override write to check approval lock."""
        # Check lock before any write
        self._check_approval_lock('write')
        return super().write(vals)
    
    def unlink(self):
        """Override unlink to check approval lock."""
        self._check_approval_lock('unlink')
        return super().unlink()
    
    def action_recall_approval(self):
        """Recall the approval request (requestor only).
        
        Opens wizard to enter recall reason.
        """
        self.ensure_one()
        
        if not self.approval_locked or not self.approval_request_id:
            raise UserError(_('No active approval request to recall.'))
        
        if self.approval_request_id.requested_by != self.env.user:
            raise UserError(_('Only the requestor can recall an approval request.'))
        
        if self.approval_request_id.state != 'pending':
            raise UserError(_('Only pending approval requests can be recalled.'))
        
        # Open wizard for recall reason
        return {
            'type': 'ir.actions.act_window',
            'name': _('Recall Approval Request'),
            'res_model': 'ops.approval.recall.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_approval_request_id': self.approval_request_id.id,
                'default_document_id': self.id,
                'default_document_model': self._name,
            },
        }