# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpsProductRequest(models.Model):
    _name = 'ops.product.request'
    _description = 'Product Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char('Request Number', required=True, copy=False, 
                       default=lambda self: _('New'), readonly=True)
    
    # Request Details
    product_sku = fields.Char('Product SKU', required=True, tracking=True,
                              help='Proposed product code/SKU')
    product_name = fields.Char('Product Name', required=True, tracking=True)
    product_description = fields.Text('Description', required=True)
    
    categ_id = fields.Many2one('product.category', 'Product Category', 
                               required=True, tracking=True)
    
    # Requester Info
    requester_id = fields.Many2one('res.users', 'Requester', 
                                    required=True, readonly=True,
                                    default=lambda self: self.env.user)
    branch_id = fields.Many2one('ops.branch', 'Branch', required=True,
                                 default=lambda self: self.env.user.branch_id)
    request_date = fields.Date('Request Date', default=fields.Date.today, 
                               readonly=True)
    
    # Business Justification
    justification = fields.Text('Business Justification', required=True,
                                help='Explain why this product is needed')
    expected_price = fields.Float('Expected Price', 
                                   help='Estimated selling price')
    expected_cost = fields.Float('Expected Cost',
                                  help='Estimated purchase cost')
    supplier_info = fields.Text('Supplier Information',
                                help='Potential suppliers or vendors')
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', 
                                      'ops_product_request_attachment_rel',
                                      'request_id', 'attachment_id',
                                      'Attachments',
                                      help='Product specifications, quotes, etc.')
    
    # Approval
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('created', 'Product Created')
    ], default='draft', tracking=True, required=True)
    
    approver_id = fields.Many2one('res.users', 'Approver', readonly=True)
    approval_date = fields.Datetime('Approval Date', readonly=True)
    rejection_reason = fields.Text('Rejection Reason')
    
    # Created Product Link
    product_id = fields.Many2one('product.product', 'Created Product', 
                                  readonly=True)
    
    notes = fields.Text('Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('ops.product.request') or _('New')
        return super(OpsProductRequest, self).create(vals)
    
    def action_submit(self):
        """Submit request for approval"""
        self.write({'state': 'submitted'})
        
        # Create approval activity
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary='Product Request Approval',
            note=f'Please review product request: {self.product_name}',
            user_id=self._get_approver().id
        )
    
    def action_approve(self):
        """Approve request and create product"""
        self.write({
            'state': 'approved',
            'approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        # Auto-create product
        self._create_product()
    
    def action_reject(self):
        """Reject request"""
        self.write({
            'state': 'rejected',
            'approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
    
    def _create_product(self):
        """Create product from approved request"""
        product = self.env['product.product'].create({
            'name': self.product_name,
            'default_code': self.product_sku,
            'description': self.product_description,
            'categ_id': self.categ_id.id,
            'list_price': self.expected_price or 0,
            'standard_price': self.expected_cost or 0,
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
        })
        
        self.write({
            'product_id': product.id,
            'state': 'created'
        })
        
        # Notify requester
        self.message_post(
            body=f'Product {product.name} has been created successfully.',
            subject='Product Created'
        )
        
        return product
    
    def _get_approver(self):
        """Get approver based on company configuration"""
        # Default: Branch Manager or Product Manager
        product_manager_group = self.env.ref('ops_matrix_core.group_ops_product_manager', 
                                             raise_if_not_found=False)
        if product_manager_group:
            approvers = product_manager_group.users
            if approvers:
                return approvers[0]
        
        # Fallback to branch manager
        if hasattr(self.env.user, 'branch_id') and self.env.user.branch_id and self.env.user.branch_id.manager_id:
            return self.env.user.branch_id.manager_id
        
        # Fallback to admin
        return self.env.ref('base.user_admin')
