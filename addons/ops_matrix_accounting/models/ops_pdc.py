# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpsPDCReceivable(models.Model):
    _name = 'ops.pdc.receivable'
    _description = 'Post-Dated Check Receivable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'maturity_date desc, id desc'
    
    name = fields.Char('Reference', required=True, copy=False, 
                       default=lambda self: _('New'), readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', 
                                  required=True, tracking=True)
    amount = fields.Monetary('Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                   default=lambda self: self.env.company.currency_id)
    
    check_number = fields.Char('Check Number', required=True, tracking=True)
    check_date = fields.Date('Check Date', default=fields.Date.today)
    maturity_date = fields.Date('Maturity Date', required=True, tracking=True)
    
    bank_id = fields.Many2one('res.bank', 'Bank')
    branch_id = fields.Many2one('ops.branch', 'Branch')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('deposited', 'Deposited'),
        ('cleared', 'Cleared'),
        ('bounced', 'Bounced'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')
    
    deposit_date = fields.Date('Deposit Date')
    clearance_date = fields.Date('Clearance Date')
    
    notes = fields.Text('Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.pdc.receivable') or _('New')
        return super(OpsPDCReceivable, self).create(vals_list)
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Amount must be positive'))
    
    @api.constrains('maturity_date', 'check_date')
    def _check_dates(self):
        for record in self:
            if record.maturity_date < record.check_date:
                raise ValidationError(_('Maturity date must be after check date'))
    
    def action_deposit(self):
        self.write({
            'state': 'deposited',
            'deposit_date': fields.Date.today(),
        })
    
    def action_clear(self):
        self.write({
            'state': 'cleared',
            'clearance_date': fields.Date.today(),
        })
    
    def action_bounce(self):
        self.write({'state': 'bounced'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})


class OpsPDCPayable(models.Model):
    _name = 'ops.pdc.payable'
    _description = 'Post-Dated Check Payable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'maturity_date desc, id desc'
    
    name = fields.Char('Reference', required=True, copy=False,
                       default=lambda self: _('New'), readonly=True)
    partner_id = fields.Many2one('res.partner', 'Vendor',
                                  required=True, tracking=True)
    amount = fields.Monetary('Amount', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                   default=lambda self: self.env.company.currency_id)
    
    check_number = fields.Char('Check Number', required=True, tracking=True)
    check_date = fields.Date('Check Date', default=fields.Date.today)
    maturity_date = fields.Date('Maturity Date', required=True, tracking=True)
    
    bank_id = fields.Many2one('res.bank', 'Bank')
    branch_id = fields.Many2one('ops.branch', 'Branch')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('presented', 'Presented'),
        ('cleared', 'Cleared'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')
    
    issue_date = fields.Date('Issue Date')
    clearance_date = fields.Date('Clearance Date')
    
    notes = fields.Text('Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.pdc.payable') or _('New')
        return super(OpsPDCPayable, self).create(vals_list)
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Amount must be positive'))
    
    def action_issue(self):
        self.write({
            'state': 'issued',
            'issue_date': fields.Date.today(),
        })
    
    def action_present(self):
        self.write({'state': 'presented'})
    
    def action_clear(self):
        self.write({
            'state': 'cleared',
            'clearance_date': fields.Date.today(),
        })
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
