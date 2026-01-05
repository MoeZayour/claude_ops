from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'ops.approval.mixin', 'ops.segregation.of.duties.mixin']
    
    def action_post(self):
        """
        Override action_post to enforce segregation of duties rules before posting.
        
        This ensures that SoD rules prevent same user from creating and posting payments.
        """
        for payment in self:
            _logger.info("SoD Check: Processing payment %s for posting", payment.name)
            
            # ADMIN BYPASS: Skip SoD checks for administrators
            if self.env.su or self.env.user.has_group('base.group_system'):
                _logger.info("SoD Check: Admin bypass for payment %s", payment.name)
                continue
            
            # Check Segregation of Duties (SoD) rules BEFORE posting
            payment._check_sod_violation('post')
        
        # If all checks pass, proceed with posting
        return super().action_post()
