from odoo import _, models, fields, api
from odoo.exceptions import ValidationError
from typing import TYPE_CHECKING, List, Dict, Any, Tuple

if TYPE_CHECKING:
    from odoo.api import Environment


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ==========================================================================
    # MASTER DATA GOVERNANCE: Company Registration & Verification
    # ==========================================================================
    ops_cr_number = fields.Char(
        string='CR Number',
        tracking=True,
        index=True,
        copy=False,
        help='Official Company Registration (CR) number. '
             'UNIQUE when provided (NULL allowed for leads/individuals). '
             'Used for: KYC compliance, duplicate customer detection, government reporting. '
             'Example: CR-123456, REG-2024-00123'
    )

    ops_master_verified = fields.Boolean(
        string='Master Verified',
        default=False,
        tracking=True,
        groups='ops_matrix_core.group_ops_manager,base.group_system',
        help='Indicates this customer has been verified by Master Data Management.\n\n'
             'SMART GATE LOGIC:\n'
             '• CREDIT transactions: BLOCKED if not verified\n'
             '• CASH/Immediate transactions: ALLOWED even if not verified\n\n'
             'Verification involves: CR number validation, credit assessment, KYC checks.\n'
             'Only authorized users (Finance/Manager) can toggle this flag.'
    )

    # SQL Constraint for CR Number uniqueness (NULL allowed for leads/individuals)
    # Note: PostgreSQL UNIQUE constraint allows multiple NULL values by design
    _sql_constraints = [
        ('ops_cr_number_unique',
         'UNIQUE(ops_cr_number)',
         'Company Registration Number must be unique! Another customer already has this CR Number.'),
    ]

    # Stewardship State for Partner Governance
    ops_state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('blocked', 'Blocked'),
        ('archived', 'Archived')
    ], string='Stewardship State', default='draft', help="Partner approval state for governance workflow.", tracking=True)
    
    # Partner Verification & Compliance
    ops_verification_date = fields.Date(
        string='Verification Date',
        help='Date when partner was verified/approved'
    )
    ops_verified_by_id = fields.Many2one(
        'res.users',
        string='Verified By',
        help='User who verified the partner',
        readonly=True
    )
    ops_approval_notes = fields.Text(
        string='Approval Notes',
        help='Notes about partner approval/rejection'
    )
    
    # Credit & Payment Terms
    ops_credit_limit = fields.Monetary(
        string='OPS Credit Limit',
        help='Maximum credit amount for this partner (OPS Matrix)',
        currency_field='company_currency_id'
    )
    ops_total_outstanding = fields.Monetary(
        string='Total Outstanding',
        compute='_compute_total_outstanding',
        store=False,
        compute_sudo=True,
        help='Total outstanding amount for this partner',
        currency_field='company_currency_id'
    )
    
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        related='company_id.currency_id',
        readonly=True
    )
    
    ops_confirmation_restrictions = fields.Text(
        string='Confirmation Restrictions',
        compute='_compute_confirmation_restrictions',
        store=False,
        compute_sudo=True,
        help='Displays any restrictions preventing order confirmation'
    )
    
    @api.constrains('ops_state')
    def _check_state_validity(self) -> None:
        """Ensure state transitions are valid"""
        for record in self:
            if record.ops_state == 'archived' and record.active:
                raise ValidationError(_('Archived partners should be marked as inactive'))
    
    def _compute_total_outstanding(self) -> None:
        """Calculate total outstanding amount for partner"""
        for partner in self:
            total = 0.0
            
            # Sum outstanding invoices
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '!=', 'cancel'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            
            for invoice in invoices:
                if invoice.move_type == 'out_invoice':
                    total += invoice.amount_residual
                else:  # refund
                    total -= invoice.amount_residual
            
            partner.ops_total_outstanding = total
    
    def _compute_confirmation_restrictions(self) -> None:
        """Compute any restrictions that would prevent order confirmation"""
        for partner in self:
            restrictions = []

            # Check Master Data Verification - HIGHEST PRIORITY
            if not partner.ops_master_verified:
                restrictions.append('⚠️ NOT MASTER VERIFIED - Orders CANNOT be confirmed')

            # Check stewardship state
            if partner.ops_state == 'draft':
                restrictions.append('Partner not yet approved (Draft state)')
            elif partner.ops_state == 'blocked':
                restrictions.append('Partner is blocked from transactions')
            elif partner.ops_state == 'archived':
                restrictions.append('Partner is archived')

            # Check credit limit (optional)
            if partner.ops_credit_limit > 0 and partner.ops_total_outstanding >= partner.ops_credit_limit:
                restrictions.append(f'Credit limit exceeded ({partner.ops_total_outstanding} >= {partner.ops_credit_limit})')

            # Check if partner is active
            if not partner.active:
                restrictions.append('Partner is inactive')

            partner.ops_confirmation_restrictions = '\n'.join(restrictions) if restrictions else ''
    
    def action_approve(self) -> bool:
        """Approve the partner for transactions"""
        for partner in self:
            partner.write({
                'ops_state': 'approved',
                'ops_verification_date': fields.Date.today(),
                'ops_verified_by_id': self.env.user.id
            })
            partner.message_post(body='Partner approved for transactions')
        return True
    
    def action_block(self) -> bool:
        """Block partner from further transactions"""
        for partner in self:
            partner.write({'ops_state': 'blocked'})
            partner.message_post(body='Partner blocked from transactions')
        return True
    
    def action_unblock(self) -> bool:
        """Unblock partner - return to approved state"""
        for partner in self:
            if partner.ops_state == 'blocked':
                partner.write({'ops_state': 'approved'})
                partner.message_post(body='Partner unblocked')
        return True
    
    def action_reset_to_draft(self) -> bool:
        """Reset partner back to draft state"""
        for partner in self:
            partner.write({
                'ops_state': 'draft',
                'ops_verification_date': None,
                'ops_verified_by_id': None
            })
            partner.message_post(body='Partner reset to draft')
        return True

    def action_verify_master(self) -> bool:
        """Verify customer in Master Data Management (MDM)."""
        for partner in self:
            if not partner.ops_cr_number:
                raise ValidationError(_(
                    "Cannot verify customer '%s'. Company Registration Number (CR) is required."
                ) % partner.name)

            partner.write({
                'ops_master_verified': True,
            })
            partner.message_post(
                body=_('Customer MASTER VERIFIED by %s. Sales Orders can now be confirmed.') % self.env.user.name
            )
        return True

    def action_unverify_master(self) -> bool:
        """Revoke Master Data verification."""
        for partner in self:
            partner.write({
                'ops_master_verified': False,
            })
            partner.message_post(
                body=_('Customer Master Verification REVOKED by %s. Sales Orders can no longer be confirmed.') % self.env.user.name
            )
        return True

    def can_confirm_orders(self) -> Tuple[bool, str]:
        """Check if partner can have orders confirmed"""
        self.ensure_one()

        # Check Master Data Verification - HARD BLOCK
        if not self.ops_master_verified:
            return False, 'Customer is NOT MASTER VERIFIED. Sales Orders cannot be confirmed until verification is complete.'

        if self.ops_state not in ['approved', 'approved']:
            return False, f'Partner state is {self.ops_state}'

        if not self.active:
            return False, 'Partner is inactive'

        if self.ops_credit_limit > 0 and self.ops_total_outstanding >= self.ops_credit_limit:
            return False, f'Credit limit exceeded: {self.ops_total_outstanding} >= {self.ops_credit_limit}'

        return True, 'Partner can confirm orders'
     
    @api.onchange('ops_state')
    def _onchange_ops_state(self) -> None:
        """Auto-deactivate when archived"""
        if self.ops_state == 'archived':
            self.active = False
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger approval notifications for draft customers."""
        partners = super().create(vals_list)
        
        # Trigger notification for draft customers
        for partner in partners:
            if partner.ops_state == 'draft' and partner.customer_rank > 0:
                partner._notify_draft_customer_creation()
        
        return partners
    
    def write(self, vals):
        """Override write to trigger notification if state changes to draft."""
        result = super().write(vals)
        
        # If ops_state changed to draft, notify approvers
        if 'ops_state' in vals and vals['ops_state'] == 'draft':
            for partner in self:
                if partner.customer_rank > 0:
                    partner._notify_draft_customer_creation()
        
        return result
    
    def _notify_draft_customer_creation(self):
        """Send notification/activity to approvers when customer is in draft state."""
        self.ensure_one()
        
        # Find users with approval rights
        approver_group = self.env.ref('ops_matrix_core.group_ops_matrix_approver', raise_if_not_found=False)
        manager_persona = self.env['ops.persona'].search([('name', 'ilike', 'Manager')], limit=1)
        
        approvers = self.env['res.users']
        
        # Add users from approver group
        if approver_group:
            approvers |= approver_group.users
        
        # Add users with Manager persona
        if manager_persona:
            approvers |= self.env['res.users'].search([('persona_id', '=', manager_persona.id)])
        
        # Create activity for each approver
        for approver in approvers:
            if not approver.share:  # Skip portal users
                self.activity_schedule(
                    activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                    summary=_('Customer Approval Required: %s') % self.name,
                    note=_(
                        'A new customer "%s" has been created in Draft state and requires approval.\n\n'
                        'Please review the customer details and approve or reject as needed.'
                    ) % self.name,
                    user_id=approver.id
                )
        
        # Also post a message on the partner
        self.message_post(
            body=_('Customer created in Draft state. Approval notification sent to %d approver(s).') % len(approvers),
            subject=_('Approval Required'),
            message_type='notification'
        )
