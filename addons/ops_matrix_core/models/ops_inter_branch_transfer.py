# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class OpsInterBranchTransfer(models.Model):
    _name = 'ops.inter.branch.transfer'
    _description = 'Inter-Branch Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'
    _rec_name = 'reference'

    # =========================================================================
    # Fields
    # =========================================================================
    
    reference = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    source_branch_id = fields.Many2one(
        'ops.branch',
        string='Source Branch',
        required=True,
        tracking=True,
        help="Branch sending the items"
    )
    
    dest_branch_id = fields.Many2one(
        'ops.branch',
        string='Destination Branch',
        required=True,
        tracking=True,
        help="Branch receiving the items"
    )
    
    source_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Source Warehouse',
        required=True,
        tracking=True,
        domain="[('ops_branch_id', '=', source_branch_id)]",
        help="Warehouse in source branch where items will be picked"
    )
    
    dest_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Destination Warehouse',
        required=True,
        tracking=True,
        domain="[('ops_branch_id', '=', dest_branch_id)]",
        help="Warehouse in destination branch where items will be received"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='source_branch_id.company_id',
        store=True,
        readonly=True,
        help='Company of the source branch'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True, copy=False)
    
    transfer_date = fields.Date(
        string='Transfer Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    expected_arrival_date = fields.Date(
        string='Expected Arrival',
        tracking=True
    )
    
    actual_arrival_date = fields.Date(
        string='Actual Arrival',
        readonly=True,
        tracking=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    active = fields.Boolean(
        default=True
    )
    
    # Computed fields for UI
    can_confirm = fields.Boolean(
        compute='_compute_can_actions',
        string='Can Confirm'
    )
    
    can_receive = fields.Boolean(
        compute='_compute_can_actions',
        string='Can Receive'
    )
    
    can_cancel = fields.Boolean(
        compute='_compute_can_actions',
        string='Can Cancel'
    )

    # =========================================================================
    # Computed Methods
    # =========================================================================
    
    @api.depends('state', 'source_branch_id', 'dest_branch_id')
    def _compute_can_actions(self):
        """Compute what actions the current user can perform."""
        for record in self:
            user = self.env.user
            
            # Get user's allowed branches
            user_branches = self.env['ops.branch']
            if hasattr(user, 'ops_allowed_branch_ids'):
                user_branches = user.ops_allowed_branch_ids
            elif hasattr(user, 'get_effective_matrix_access'):
                access = user.get_effective_matrix_access()
                user_branches = access.get('branches', self.env['ops.branch'])
            
            # Admin bypass
            is_admin = user.has_group('base.group_system')
            
            # Can confirm if draft and user has access to source branch
            record.can_confirm = (
                record.state == 'draft' and
                (is_admin or record.source_branch_id in user_branches)
            )
            
            # Can receive if in_transit and user has access to destination branch
            record.can_receive = (
                record.state == 'in_transit' and
                (is_admin or record.dest_branch_id in user_branches)
            )
            
            # Can cancel if not yet received or already cancelled
            record.can_cancel = record.state not in ('received', 'cancelled')

    # =========================================================================
    # Constraints
    # =========================================================================
    
    @api.constrains('source_branch_id', 'dest_branch_id')
    def _check_different_branches(self):
        """Ensure source and destination are different."""
        for record in self:
            if record.source_branch_id == record.dest_branch_id:
                raise ValidationError(_(
                    "Source and destination branches must be different."
                ))
    
    @api.constrains('transfer_date', 'expected_arrival_date')
    def _check_dates(self):
        """Validate date logic."""
        for record in self:
            if record.expected_arrival_date and record.transfer_date:
                if record.expected_arrival_date < record.transfer_date:
                    raise ValidationError(_(
                        "Expected arrival date cannot be before transfer date."
                    ))
    
    @api.constrains('source_warehouse_id', 'source_branch_id')
    def _check_source_warehouse_branch(self):
        """Ensure source warehouse belongs to source branch."""
        for record in self:
            if record.source_warehouse_id and record.source_branch_id:
                # Check if warehouse has ops_branch_id field
                if hasattr(record.source_warehouse_id, 'ops_branch_id'):
                    if record.source_warehouse_id.ops_branch_id != record.source_branch_id:
                        raise ValidationError(_(
                            "Source warehouse '%s' does not belong to source branch '%s'."
                        ) % (
                            record.source_warehouse_id.name,
                            record.source_branch_id.name
                        ))
    
    @api.constrains('dest_warehouse_id', 'dest_branch_id')
    def _check_dest_warehouse_branch(self):
        """Ensure destination warehouse belongs to destination branch."""
        for record in self:
            if record.dest_warehouse_id and record.dest_branch_id:
                # Check if warehouse has ops_branch_id field
                if hasattr(record.dest_warehouse_id, 'ops_branch_id'):
                    if record.dest_warehouse_id.ops_branch_id != record.dest_branch_id:
                        raise ValidationError(_(
                            "Destination warehouse '%s' does not belong to destination branch '%s'."
                        ) % (
                            record.dest_warehouse_id.name,
                            record.dest_branch_id.name
                        ))

    # =========================================================================
    # CRUD Methods
    # =========================================================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence for reference on create."""
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'ops.inter.branch.transfer'
                ) or _('New')
        
        records = super().create(vals_list)
        
        # Log creation
        for record in records:
            record.message_post(
                body=_('Inter-branch transfer created from %s to %s') % (
                    record.source_branch_id.name,
                    record.dest_branch_id.name
                )
            )
        
        return records
    
    def write(self, vals):
        """Track state changes."""
        # Track state changes
        if 'state' in vals:
            for record in self:
                old_state = record.state
                new_state = vals['state']
                if old_state != new_state:
                    record.message_post(
                        body=_('Status changed from %s to %s') % (
                            dict(self._fields['state'].selection).get(old_state),
                            dict(self._fields['state'].selection).get(new_state)
                        )
                    )
        
        return super().write(vals)

    # =========================================================================
    # Action Methods
    # =========================================================================
    
    def action_confirm(self):
        """Confirm the transfer - moves to 'confirmed' state."""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_("Only draft transfers can be confirmed."))
        
        # Check user has access to source branch
        user = self.env.user
        if not user.has_group('base.group_system'):
            # Get user's allowed branches
            user_branches = self.env['ops.branch']
            if hasattr(user, 'ops_allowed_branch_ids'):
                user_branches = user.ops_allowed_branch_ids
            elif hasattr(user, 'get_effective_matrix_access'):
                access = user.get_effective_matrix_access()
                user_branches = access.get('branches', self.env['ops.branch'])
            
            if self.source_branch_id not in user_branches:
                raise UserError(_(
                    "You don't have permission to confirm transfers from %s"
                ) % self.source_branch_id.name)
        
        self.write({'state': 'confirmed'})
        
        self.message_post(
            body=_('Transfer confirmed by %s') % user.name,
            subject=_('Transfer Confirmed')
        )
        
        return True
    
    def action_send(self):
        """Mark as in transit."""
        self.ensure_one()
        
        if self.state not in ('draft', 'confirmed'):
            raise UserError(_("Only draft or confirmed transfers can be sent."))
        
        self.write({'state': 'in_transit'})
        
        self.message_post(
            body=_('Transfer marked as in transit'),
            subject=_('In Transit')
        )
        
        return True
    
    def action_receive(self):
        """Receive the transfer at destination."""
        self.ensure_one()
        
        if self.state != 'in_transit':
            raise UserError(_("Only in-transit transfers can be received."))
        
        # Check user has access to destination branch
        user = self.env.user
        if not user.has_group('base.group_system'):
            # Get user's allowed branches
            user_branches = self.env['ops.branch']
            if hasattr(user, 'ops_allowed_branch_ids'):
                user_branches = user.ops_allowed_branch_ids
            elif hasattr(user, 'get_effective_matrix_access'):
                access = user.get_effective_matrix_access()
                user_branches = access.get('branches', self.env['ops.branch'])
            
            if self.dest_branch_id not in user_branches:
                raise UserError(_(
                    "You don't have permission to receive transfers at %s"
                ) % self.dest_branch_id.name)
        
        self.write({
            'state': 'received',
            'actual_arrival_date': fields.Date.context_today(self)
        })
        
        self.message_post(
            body=_('Transfer received by %s') % user.name,
            subject=_('Transfer Received')
        )
        
        return True
    
    def action_cancel(self):
        """Cancel the transfer."""
        self.ensure_one()
        
        if self.state == 'received':
            raise UserError(_("Cannot cancel a received transfer."))
        
        if self.state == 'cancelled':
            raise UserError(_("Transfer is already cancelled."))
        
        self.write({'state': 'cancelled'})
        
        self.message_post(
            body=_('Transfer cancelled'),
            subject=_('Transfer Cancelled')
        )
        
        return True
    
    def action_set_to_draft(self):
        """Reset to draft (for corrections)."""
        self.ensure_one()
        
        if self.state == 'received':
            raise UserError(_("Cannot reset a received transfer to draft."))
        
        self.write({'state': 'draft'})
        
        self.message_post(
            body=_('Transfer reset to draft'),
            subject=_('Reset to Draft')
        )
        
        return True

    # =========================================================================
    # Business Methods
    # =========================================================================

    @api.depends('reference', 'source_branch_id.name', 'dest_branch_id.name')
    def _compute_display_name(self):
        """Custom display name."""
        for record in self:
            record.display_name = '%s: %s → %s' % (
                record.reference or '',
                record.source_branch_id.name or '',
                record.dest_branch_id.name or ''
            )
    
    @api.model
    def get_transfers_for_branch(self, branch_id, direction='both'):
        """
        Get all transfers for a specific branch.
        
        :param branch_id: ID of the branch
        :param direction: 'outgoing', 'incoming', or 'both'
        :return: recordset of transfers
        """
        domain = []
        
        if direction == 'outgoing':
            domain = [('source_branch_id', '=', branch_id)]
        elif direction == 'incoming':
            domain = [('dest_branch_id', '=', branch_id)]
        else:  # both
            domain = ['|',
                     ('source_branch_id', '=', branch_id),
                     ('dest_branch_id', '=', branch_id)]
        
        return self.search(domain)
