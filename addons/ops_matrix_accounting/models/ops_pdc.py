from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OpsPostDatedCheck(models.Model):
    _name = 'ops.pdc'
    _description = 'Post-Dated Check'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'maturity_date desc, id desc'

    name = fields.Char(string='Reference', required=True, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date = fields.Date(string='Issue Date', required=True, tracking=True)
    maturity_date = fields.Date(string='Maturity Date', required=True, tracking=True)
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    
    payment_type = fields.Selection([
        ('inbound', 'Customer'),
        ('outbound', 'Vendor')
    ], string='Payment Type', required=True)
    
    bank_id = fields.Many2one('res.bank', string='Bank', required=True)
    check_number = fields.Char(string='Check Number', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('deposited', 'Deposited'),
        ('cleared', 'Cleared'),
        ('bounced', 'Bounced'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    active = fields.Boolean(default=True)

    days_to_maturity = fields.Integer(
        string='Days to Maturity',
        compute='_compute_days_to_maturity',
        store=True,
        help='Number of days until maturity (negative when past due).'
    )

    # Matrix Dimensions
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=False,
        ondelete='set null',
        index=True,
    )
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit', required=True)
    
    # Accounting Fields
    journal_id = fields.Many2one('account.journal', string='PDC Journal', required=True, domain=[('type', '=', 'bank')])
    holding_account_id = fields.Many2one('account.account', string='PDC Holding Account', required=True)
    move_id = fields.Many2one('account.move', string='Registration Entry', readonly=True)
    deposit_move_id = fields.Many2one('account.move', string='Deposit Entry', readonly=True)
    
    # Anti-Fraud Security: Button-level authority for PDC management
    can_user_manage_pdc = fields.Boolean(
        compute='_compute_can_user_manage_pdc',
        string='Can Manage PDC',
        help='Technical field: User has authority to manage PDC operations (register, deposit, clear)'
    )
    
    @api.depends_context('uid')
    def _compute_can_user_manage_pdc(self):
        """
        Check if current user has authority to manage PDC operations.
        
        ADMIN BYPASS: System administrators always have access.
        PERSONA LOGIC: Uses additive authority - if ANY persona grants the right, access is granted.
        """
        for record in self:
            # Admin bypass
            if self.env.su or self.env.user.has_group('base.group_system'):
                record.can_user_manage_pdc = True
            else:
                # Check persona authority using the helper method
                record.can_user_manage_pdc = self.env.user.has_ops_authority('can_manage_pdc')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.pdc') or 'PDC/0001'
        return super().create(vals_list)

    @api.constrains('date', 'maturity_date')
    def _check_dates(self):
        for pdc in self:
            if pdc.maturity_date < pdc.date:
                raise ValidationError('Maturity Date cannot be earlier than Issue Date.')

    def _prepare_move_line_vals(self, account_id, debit, credit, name_suffix=''):
        """Helper to prepare consistent move line values with matrix dimensions."""
        return {
            'account_id': account_id,
            'partner_id': self.partner_id.id,
            'name': f'{name_suffix} - {self.check_number}',
            'debit': debit,
            'credit': credit,
            'ops_branch_id': self.ops_branch_id.id,
            'ops_business_unit_id': self.ops_business_unit_id.id,
        }

    @api.depends('maturity_date')
    def _compute_days_to_maturity(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.maturity_date:
                record.days_to_maturity = (record.maturity_date - today).days
            else:
                record.days_to_maturity = 0

    def action_register(self):
        """Register the PDC and create initial journal entry."""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError('Only draft PDCs can be registered.')

        # Determine accounts based on payment type
        if self.payment_type == 'inbound':
            partner_account = self.partner_id.property_account_receivable_id
            debit_account = self.holding_account_id
            credit_account = partner_account
        else:  # outbound
            partner_account = self.partner_id.property_account_payable_id
            debit_account = partner_account
            credit_account = self.holding_account_id

        move_vals = {
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': f'PDC Registration - {self.name}',
            'ops_branch_id': self.ops_branch_id.id,
            'ops_business_unit_id': self.ops_business_unit_id.id,
            'line_ids': [
                (0, 0, self._prepare_move_line_vals(
                    debit_account.id, self.amount, 0.0, 'PDC Holding'
                )),
                (0, 0, self._prepare_move_line_vals(
                    credit_account.id, 0.0, self.amount, 'PDC Registration'
                ))
            ]
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        self.write({
            'state': 'registered',
            'move_id': move.id
        })

    def action_deposit(self):
        """Deposit the PDC and create bank entry."""
        self.ensure_one()
        if self.state != 'registered':
            raise ValidationError('Only registered PDCs can be deposited.')

        # Get bank account from journal
        if not self.journal_id.default_account_id:
            raise ValidationError('Bank journal must have a default account configured.')

        # Determine accounts based on payment type
        if self.payment_type == 'inbound':
            debit_account = self.journal_id.default_account_id
            credit_account = self.holding_account_id
        else:  # outbound
            debit_account = self.holding_account_id
            credit_account = self.journal_id.default_account_id

        move_vals = {
            'journal_id': self.journal_id.id,
            'date': fields.Date.today(),
            'ref': f'PDC Deposit - {self.name}',
            'ops_branch_id': self.ops_branch_id.id,
            'ops_business_unit_id': self.ops_business_unit_id.id,
            'line_ids': [
                (0, 0, self._prepare_move_line_vals(
                    debit_account.id, self.amount, 0.0, 'PDC Bank Deposit'
                )),
                (0, 0, self._prepare_move_line_vals(
                    credit_account.id, 0.0, self.amount, 'PDC Holding Clearance'
                ))
            ]
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        self.write({
            'state': 'deposited',
            'deposit_move_id': move.id
        })

    def action_cancel(self):
        """Cancel the PDC and revert to cancelled state."""
        for pdc in self:
            if pdc.state in ('cleared', 'cancelled'):
                continue
            pdc.state = 'cancelled'
