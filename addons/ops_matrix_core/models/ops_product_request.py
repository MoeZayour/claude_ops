from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from typing import List, Dict, Any

class OpsProductRequest(models.Model):
    _name = 'ops.product.request'
    _description = 'Product Request - Request Products for Procurement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id DESC'
    _check_company_auto = True
    
    # Basic Fields
    name = fields.Char(
        string='Request Number',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    code = fields.Char(
        string='Request Code',
        copy=False
    )
    description = fields.Text(
        string='Description',
        help='Additional details about the product request'
    )
    
    # Request Metadata
    request_date = fields.Datetime(
        string='Request Date',
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    requester_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )
    
    # Product Information
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        help='The product being requested',
        tracking=True
    )
    part_number = fields.Char(
        string='Part Number',
        related='product_id.default_code',
        readonly=True,
        store=True
    )
    quantity = fields.Float(
        string='Quantity Requested',
        required=True,
        default=1.0,
        tracking=True
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True,
        store=False
    )
    
    # Scheduling
    required_date = fields.Date(
        string='Required By Date',
        required=True,
        help='Date when the product is needed'
    )
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='normal', tracking=True)
    
    # Organization & Access Control
    branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        required=True,
        help='Branch requesting the product'
    )
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        help='Business Unit for the request'
    )
    
    # Status & Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, index=True)
    
    # Approval Chain
    approver_ids = fields.Many2many(
        'res.users',
        'product_request_approver_rel',
        'request_id',
        'user_id',
        string='Approvers'
    )
    approval_notes = fields.Text(
        string='Approval Notes',
        help='Notes from the approval process'
    )
    
    # Linked Records
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        readonly=True,
        help='Linked purchase order line if created'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )
    
    # Constraints
    @api.constrains('quantity', 'required_date')
    def _check_request_validity(self) -> None:
        """Validate quantity and required date"""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than 0'))
            
            if record.required_date < fields.Date.today():
                raise ValidationError(_('Required date cannot be in the past'))
    
    # CRUD Methods
    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'OpsProductRequest':
        """Generate request number on creation"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.product.request') or 'REQ0001'
        
        return super().create(vals_list)
     
    # Workflow State Transitions
    def action_submit(self) -> bool:
        """Submit the product request for approval"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft requests can be submitted'))
            record.write({'state': 'submitted'})
            record.message_post(body='Product request submitted for approval')
        return True
    
    def action_approve(self) -> bool:
        """Approve the product request"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted requests can be approved'))
            record.write({'state': 'approved'})
            record.message_post(body='Product request approved')
        return True
    
    def action_start(self) -> bool:
        """Mark request as in progress"""
        for record in self:
            if record.state not in ['approved', 'submitted']:
                raise UserError(_('Request must be approved before starting'))
            record.write({'state': 'in_progress'})
            record.message_post(body='Product request marked as in progress')
        return True
    
    def action_receive(self) -> bool:
        """Mark request as received"""
        for record in self:
            if record.state != 'in_progress':
                raise UserError(_('Request must be in progress before marking as received'))
            record.write({'state': 'received'})
            record.message_post(body='Product received')
        return True
    
    def action_cancel(self) -> bool:
        """Cancel the product request"""
        for record in self:
            if record.state == 'received':
                raise UserError(_('Cannot cancel a received request'))
            record.write({'state': 'cancelled'})
            record.message_post(body='Product request cancelled')
        return True
    
    def action_reset_to_draft(self) -> bool:
        """Reset request back to draft state"""
        for record in self:
            if record.state == 'received':
                raise UserError(_('Cannot reset a received request'))
            record.write({'state': 'draft'})
            record.message_post(body='Product request reset to draft')
        return True
    
    # Helper Methods
    def _assign_default_approvers(self) -> None:
        """Assign approvers based on branch manager or business unit lead"""
        for record in self:
            approvers = set()
            
            # Add branch manager if assigned
            if record.branch_id.manager_id:
                approvers.add(record.branch_id.manager_id.id)
            
            # Add business unit lead if assigned
            if record.business_unit_id:
                # Try to find business unit lead (would need to be added to ops.business_unit)
                pass
            
            if approvers:
                record.write({'approver_ids': [(6, 0, list(approvers))]})
     
    @api.onchange('branch_id')
    def _onchange_branch_id(self) -> None:
        """Set business unit based on branch if applicable"""
        # Could auto-set business unit if branch has a primary unit
        pass
     
    @api.onchange('product_id')
    def _onchange_product_id(self) -> None:
        """Update product details when product changes"""
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            # Auto-set business unit from product if product has silo assignment
            if self.product_id.business_unit_id:
                self.business_unit_id = self.product_id.business_unit_id.id
