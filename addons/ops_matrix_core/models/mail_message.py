from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class MailMessage(models.Model):
    _inherit = 'mail.message'

    ops_is_audit_log = fields.Boolean(string='Is Audit Log', default=False)

    def unlink(self):
        if any(m.ops_is_audit_log for m in self):
            raise AccessError(_("Immutable Audit Log: Deletion Prohibited."))
        return super(MailMessage, self).unlink()
