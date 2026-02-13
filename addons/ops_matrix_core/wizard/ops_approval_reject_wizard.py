from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OpsApprovalRejectWizard(models.TransientModel):
    _name = 'ops.approval.reject.wizard'
    _description = 'Reject Approval Request Wizard'
    
    approval_request_id = fields.Many2one('ops.approval.request', string='Approval Request', required=True)
    
    rejection_reason = fields.Text(
        string='Reason for Rejection',
        required=True,
        help='Explain why you are rejecting this request. '
             'Provide guidance for the requestor on what needs to change. '
             'This will be visible to the requestor and recorded in approval history.'
    )
    
    def action_confirm_reject(self):
        """Execute the rejection."""
        self.ensure_one()
        
        if not self.rejection_reason or len(self.rejection_reason.strip()) < 10:
            raise UserError(_('Please provide a detailed reason (at least 10 characters).'))
        
        # Reject with reason
        self.approval_request_id.write({
            'state': 'rejected',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
            'response_notes': self.rejection_reason,
        })
        
        # Unlock document
        if self.approval_request_id.model_name and self.approval_request_id.res_id:
            try:
                record = self.env[self.approval_request_id.model_name].browse(self.approval_request_id.res_id)
                if record.exists() and hasattr(record, 'approval_locked'):
                    record.with_context(approval_unlock=True).write({
                        'approval_locked': False,
                        'approval_request_id': False,
                    })
                    
                    # Post to document
                    if hasattr(record, 'message_post'):
                        record.message_post(
                            body=_('Approval REJECTED by %s<br/>Reason: %s') % (self.env.user.name, self.rejection_reason),
                            message_type='notification',
                            subtype_xmlid='mail.mt_note'
                        )
            except Exception as e:
                _logger.error(f'Error unlocking document: {e}')
        
        # Post to approval request
        self.approval_request_id.message_post(
            body=_('Approval REJECTED by %s<br/>Reason: %s') % (self.env.user.name, self.rejection_reason),
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {'type': 'ir.actions.act_window_close'}