from odoo import models

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'ops.approval.mixin']
