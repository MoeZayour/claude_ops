from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ThreeWayMatchOverrideWizard(models.TransientModel):
    _name = 'three.way.match.override.wizard'
    _description = 'Three-Way Match Override Wizard'

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True, required=True)
    match_issues = fields.Text(string="Match Issues", readonly=True, required=True)
    override_reason = fields.Text(string="Override Reason", required=True)
    approver_id = fields.Many2one(
        'res.users',
        string="Approver",
        required=True,
        domain="[('active', '=', True)]"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'account.move' and self.env.context.get('active_id'):
            invoice = self.env['account.move'].browse(self.env.context.get('active_id'))
            if 'invoice_id' in fields_list:
                res['invoice_id'] = invoice.id
            if 'match_issues' in fields_list:
                res['match_issues'] = invoice.three_way_match_issues
        return res

    def action_request_override(self):
        self.ensure_one()
        if len(self.override_reason) < 20:
            raise UserError(_('Override reason must be at least 20 characters.'))

        approval_request = self.env['ops.approval.request'].create({
            'document_model': 'account.move',
            'document_id': self.invoice_id.id,
            'document_ref': self.invoice_id.name,
            'reason': f'Three-Way Match Override Request:\n{self.override_reason}',
            'details': self.match_issues,
            'approver_id': self.approver_id.id,
            'request_type': 'three_way_match_override',
            'rule_id': self.env.ref('ops_matrix_core.rule_three_way_match_override', raise_if_not_found=False).id,
        })
        
        self.invoice_id.message_post(
            body=_(
                "Three-way match override requested by %(user_name)s. Reason: %(reason)s. Sent to %(approver_name)s for approval.",
                user_name=self.env.user.name,
                reason=self.override_reason,
                approver_name=self.approver_id.name
            ),
            subject=_("Three-Way Match Override Request")
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Override Requested'),
                'message': _('An override request has been sent to %s.') % self.approver_id.name,
                'type': 'success',
                'sticky': False,
            }
        }
