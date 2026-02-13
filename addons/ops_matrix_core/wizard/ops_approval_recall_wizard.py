from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OpsApprovalRecallWizard(models.TransientModel):
    _name = 'ops.approval.recall.wizard'
    _description = 'Recall Approval Request Wizard'
    
    approval_request_id = fields.Many2one('ops.approval.request', string='Approval Request', required=True)
    document_id = fields.Integer(string='Document ID', required=True)
    document_model = fields.Char(string='Document Model', required=True)
    
    recall_reason = fields.Text(
        string='Reason for Recall',
        required=True,
        help='Explain why you need to recall this approval request. '
             'This will be recorded in the approval history and visible to approvers.'
    )
    
    def action_confirm_recall(self):
        """Execute the recall."""
        self.ensure_one()
        
        if not self.recall_reason or len(self.recall_reason.strip()) < 10:
            raise UserError(_('Please provide a detailed reason (at least 10 characters).'))
        
        # Cancel approval request with reason
        self.approval_request_id.with_context(approval_recall=True).write({
            'state': 'cancelled',
            'response_notes': f'RECALLED BY REQUESTOR: {self.recall_reason}',
        })
        
        # Post to chatter
        self.approval_request_id.message_post(
            body=_('Approval request recalled by %s.<br/>Reason: %s') % (self.env.user.name, self.recall_reason),
            message_type='notification'
        )
        
        # Unlock document
        document = self.env[self.document_model].browse(self.document_id)
        if document.exists():
            document.with_context(approval_unlock=True).write({
                'approval_locked': False,
                'approval_request_id': False,
            })
            
            # Post to document chatter
            if hasattr(document, 'message_post'):
                document.message_post(
                    body=_('Approval recalled: %s') % self.recall_reason,
                    message_type='notification'
                )
        
        return {'type': 'ir.actions.act_window_close'}