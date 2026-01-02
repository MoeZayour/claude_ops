# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class OpsPersonaDelegation(models.Model):
    """Model to track persona delegation history."""
    _name = 'ops.persona.delegation'
    _description = 'OPS Persona Delegation History'
    _order = 'create_date desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # ============================================
    # BASIC INFORMATION
    # ============================================
    persona_id = fields.Many2one(
        'ops.persona',
        string='Persona',
        required=True,
        ondelete='cascade',
        tracking=True,
        help="The persona being delegated"
    )
    
    delegator_id = fields.Many2one(
        'res.users',
        string='Delegator',
        required=True,
        tracking=True,
        help='User who delegated the persona'
    )
    
    delegate_id = fields.Many2one(
        'res.users',
        string='Delegate',
        required=True,
        tracking=True,
        help='User who received the delegation'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='persona_id.company_id',
        store=True,
        readonly=True,
        help='Company from the persona'
    )
    
    # ============================================
    # DATE RANGE
    # ============================================
    start_date = fields.Datetime(
        string='Start Date',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        help="When the delegation becomes active"
    )
    
    end_date = fields.Datetime(
        string='End Date',
        required=True,
        tracking=True,
        help="When the delegation expires"
    )
    
    revoked_date = fields.Datetime(
        string='Revoked Date',
        tracking=True,
        help='When delegation was manually revoked'
    )
    
    # ============================================
    # STATUS
    # ============================================
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help="Set to False to cancel the delegation"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('cancelled', 'Cancelled'),
    ], string='Status', compute='_compute_state', store=True, tracking=True)
    
    # ============================================
    # DETAILS
    # ============================================
    reason = fields.Text(
        string='Reason for Delegation',
        tracking=True,
        help='Why this delegation was created (e.g., vacation, training)'
    )
    
    notes = fields.Text(
        string='Additional Notes',
        help='Additional notes about the delegation'
    )
    
    # ============================================
    # COMPUTED FIELDS
    # ============================================
    display_name = fields.Char(
        compute='_compute_display_name',
        string='Display Name',
        store=True
    )
    
    duration_days = fields.Integer(
        compute='_compute_duration',
        string='Duration (Days)',
        store=True,
        help='Total delegation duration in days'
    )
    
    is_current = fields.Boolean(
        string='Is Currently Active',
        compute='_compute_is_current',
        store=True,
        help="True if this delegation is currently in effect"
    )
    
    remaining_days = fields.Integer(
        compute='_compute_remaining_days',
        string='Remaining Days',
        help='Days remaining until delegation expires'
    )
    
    # ============================================
    # ADDITIONAL TRACKING FIELDS
    # ============================================
    approval_required = fields.Boolean(
        string='Approval Required',
        default=False,
        help='Whether this delegation requires approval'
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        tracking=True,
        help='User who approved the delegation'
    )
    
    approval_date = fields.Datetime(
        string='Approval Date',
        tracking=True,
        help='When the delegation was approved'
    )
    
    # Audit fields
    create_uid = fields.Many2one(
        'res.users',
        string='Created By',
        readonly=True
    )
    
    create_date = fields.Datetime(
        string='Created On',
        readonly=True
    )
    
    write_uid = fields.Many2one(
        'res.users',
        string='Last Updated By',
        readonly=True
    )
    
    write_date = fields.Datetime(
        string='Last Updated On',
        readonly=True
    )
    
    # ============================================
    # COMPUTED METHODS
    # ============================================
    
    @api.depends('delegator_id', 'delegate_id', 'start_date', 'persona_id')
    def _compute_display_name(self):
        """Compute display name for delegation record."""
        for record in self:
            if record.delegator_id and record.delegate_id:
                record.display_name = _("%(delegator)s → %(delegate)s (%(persona)s)") % {
                    'delegator': record.delegator_id.name,
                    'delegate': record.delegate_id.name,
                    'persona': record.persona_id.name if record.persona_id else _('N/A')
                }
            else:
                record.display_name = _('Delegation #%s') % record.id
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calculate delegation duration in days."""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_days = delta.days
            else:
                record.duration_days = 0
    
    @api.depends('start_date', 'end_date', 'active', 'state')
    def _compute_is_current(self):
        """Check if delegation is currently in effect."""
        now = fields.Datetime.now()
        for record in self:
            record.is_current = (
                record.active and
                record.start_date and
                record.end_date and
                record.start_date <= now <= record.end_date
            )
    
    @api.depends('end_date')
    def _compute_remaining_days(self):
        """Calculate remaining days until delegation expires."""
        now = fields.Datetime.now()
        for record in self:
            if record.end_date and record.is_current:
                delta = record.end_date - now
                record.remaining_days = max(0, delta.days)
            else:
                record.remaining_days = 0
    
    @api.depends('start_date', 'end_date', 'active', 'revoked_date')
    def _compute_state(self):
        """Compute the delegation state based on dates and active flag."""
        now = fields.Datetime.now()
        for record in self:
            if record.revoked_date:
                record.state = 'revoked'
            elif not record.active:
                record.state = 'cancelled'
            elif not record.start_date or not record.end_date:
                record.state = 'draft'
            elif record.end_date < now:
                record.state = 'expired'
            elif record.start_date <= now <= record.end_date:
                record.state = 'active'
            elif record.start_date > now:
                record.state = 'pending'
            else:
                record.state = 'draft'
    
    # ============================================
    # CONSTRAINTS & VALIDATION
    # ============================================
    
    @api.constrains('delegator_id', 'delegate_id')
    def _check_self_delegation(self):
        """Prevent delegating to yourself."""
        for record in self:
            if record.delegator_id and record.delegator_id == record.delegate_id:
                raise ValidationError(_("You cannot delegate to yourself."))
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate date range."""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError(_("End date must be after start date."))
    
    @api.constrains('persona_id', 'start_date', 'end_date', 'active')
    def _check_overlapping_delegations(self):
        """Prevent overlapping delegations for the same persona."""
        for record in self:
            if not record.active or not record.start_date or not record.end_date:
                continue
                
            overlapping = self.search([
                ('id', '!=', record.id),
                ('persona_id', '=', record.persona_id.id),
                ('active', '=', True),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date)
            ])
            
            if overlapping:
                raise ValidationError(_(
                    "This delegation overlaps with another active delegation for the same persona. "
                    "Please adjust the dates or cancel the conflicting delegation."
                ))
    
    @api.constrains('persona_id', 'delegate_id')
    def _check_delegate_capabilities(self):
        """Validate that delegate has sufficient capabilities."""
        for record in self:
            if not record.persona_id or not record.delegate_id:
                continue
            
            # Ensure delegate is an active user
            if not record.delegate_id.active:
                raise ValidationError(_(
                    "Cannot delegate to an inactive user."
                ))
            
            # Ensure the persona allows delegation
            persona = record.persona_id
            if not persona.can_be_delegated:
                raise ValidationError(_(
                    "The persona '%s' does not allow delegation."
                ) % persona.name)
    
    # ============================================
    # CRUD METHODS
    # ============================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to log delegation creation."""
        delegations = super().create(vals_list)
        
        for delegation in delegations:
            # Send notification to delegate
            delegation._notify_delegation_created()
            
            # Log creation
            delegation.message_post(
                body=_('Delegation created: %(delegator)s delegated persona %(persona)s to %(delegate)s.') % {
                    'delegator': delegation.delegator_id.name,
                    'persona': delegation.persona_id.name,
                    'delegate': delegation.delegate_id.name
                }
            )
        
        return delegations
    
    def write(self, vals):
        """Override write to track changes."""
        result = super().write(vals)
        
        # If dates changed, log it
        if 'start_date' in vals or 'end_date' in vals:
            for delegation in self:
                delegation.message_post(
                    body=_('Delegation dates updated.')
                )
        
        # If revoked, notify
        if 'active' in vals and not vals['active']:
            for delegation in self:
                delegation.write({'revoked_date': fields.Datetime.now()})
                delegation._notify_delegation_revoked()
        
        return result
    
    # ============================================
    # BUSINESS METHODS
    # ============================================
    
    def action_activate(self):
        """Manually activate a delegation."""
        self.ensure_one()
        self.write({'active': True, 'revoked_date': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Delegation Activated'),
                'message': _('Delegation has been activated.'),
                'type': 'success',
            }
        }
    
    def action_cancel(self):
        """Cancel a delegation."""
        self.ensure_one()
        self.write({'active': False, 'revoked_date': fields.Datetime.now()})
        
        # Notify both parties
        self._notify_delegation_revoked()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Delegation Cancelled'),
                'message': _('Delegation has been cancelled.'),
                'type': 'warning',
            }
        }
    
    def action_extend(self):
        """Open wizard to extend delegation end date."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Extend Delegation'),
            'res_model': 'ops.persona.delegation',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'default_end_date': self.end_date,
            }
        }
    
    def action_approve(self):
        """Approve the delegation."""
        self.ensure_one()
        self.write({
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
        })
        
        self.message_post(
            body=_('Delegation approved by %s.') % self.env.user.name
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Delegation Approved'),
                'message': _('Delegation has been approved.'),
                'type': 'success',
            }
        }
    
    def action_view_persona(self):
        """Open the associated persona."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ops.persona',
            'view_mode': 'form',
            'res_id': self.persona_id.id,
            'target': 'current',
        }
    
    def action_view_delegate(self):
        """Open the delegate user."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'form',
            'res_id': self.delegate_id.id,
            'target': 'current',
        }
    
    # ============================================
    # UTILITY METHODS
    # ============================================
    
    @api.model
    def get_active_delegation_for_persona(self, persona_id):
        """Get the currently active delegation for a persona, if any."""
        now = fields.Datetime.now()
        return self.search([
            ('persona_id', '=', persona_id),
            ('active', '=', True),
            ('start_date', '<=', now),
            ('end_date', '>=', now)
        ], limit=1)
    
    @api.model
    def get_delegations_for_user(self, user_id, only_active=True):
        """Get all delegations where the user is the delegate."""
        domain = [('delegate_id', '=', user_id)]
        if only_active:
            now = fields.Datetime.now()
            domain += [
                ('active', '=', True),
                ('start_date', '<=', now),
                ('end_date', '>=', now)
            ]
        return self.search(domain)
    
    @api.model
    def get_expiring_delegations(self, days=7):
        """Get delegations expiring within specified days."""
        now = fields.Datetime.now()
        end_date = now + timedelta(days=days)
        
        return self.search([
            ('active', '=', True),
            ('end_date', '>=', now),
            ('end_date', '<=', end_date)
        ])
    
    # ============================================
    # NOTIFICATION METHODS
    # ============================================
    
    def _notify_delegation_created(self):
        """Send notification when delegation is created."""
        self.ensure_one()
        
        # Notify delegator
        if self.delegator_id:
            self.message_post(
                body=_('Persona %(persona)s delegated to %(delegate)s from %(start)s to %(end)s.') % {
                    'persona': self.persona_id.name,
                    'delegate': self.delegate_id.name,
                    'start': self.start_date,
                    'end': self.end_date
                },
                partner_ids=[self.delegator_id.partner_id.id],
                subject=_('Persona Delegation Created')
            )
        
        # Notify delegate
        if self.delegate_id:
            self.message_post(
                body=_(
                    'You have been delegated persona %(persona)s by %(delegator)s. '
                    'Effective: %(start)s to %(end)s. Reason: %(reason)s'
                ) % {
                    'persona': self.persona_id.name,
                    'delegator': self.delegator_id.name,
                    'start': self.start_date,
                    'end': self.end_date,
                    'reason': self.reason or _('No reason provided')
                },
                partner_ids=[self.delegate_id.partner_id.id],
                subject=_('Persona Delegation Assignment')
            )
    
    def _notify_delegation_revoked(self):
        """Send notification when delegation is revoked."""
        self.ensure_one()
        
        # Notify both parties
        partner_ids = []
        if self.delegator_id:
            partner_ids.append(self.delegator_id.partner_id.id)
        if self.delegate_id:
            partner_ids.append(self.delegate_id.partner_id.id)
        
        if partner_ids:
            self.message_post(
                body=_('Delegation for persona %(persona)s has been revoked.') % {
                    'persona': self.persona_id.name
                },
                partner_ids=partner_ids,
                subject=_('Delegation Revoked')
            )
    
    def _notify_delegation_expiring(self):
        """Send notification when delegation is about to expire."""
        self.ensure_one()
        
        partner_ids = []
        if self.delegator_id:
            partner_ids.append(self.delegator_id.partner_id.id)
        if self.delegate_id:
            partner_ids.append(self.delegate_id.partner_id.id)
        
        if partner_ids:
            self.message_post(
                body=_('Delegation for persona %(persona)s expires on %(end_date)s (%(days)d days remaining).') % {
                    'persona': self.persona_id.name,
                    'end_date': self.end_date,
                    'days': self.remaining_days
                },
                partner_ids=partner_ids,
                subject=_('Delegation Expiring Soon')
            )
    
    # ============================================
    # SCHEDULED ACTIONS
    # ============================================
    
    @api.model
    def cron_check_expiring_delegations(self):
        """Notify users of delegations expiring soon."""
        expiring_delegations = self.get_expiring_delegations(days=3)
        
        for delegation in expiring_delegations:
            try:
                delegation._notify_delegation_expiring()
            except Exception as e:
                _logger.error(f"Failed to notify expiring delegation {delegation.id}: {e}")
    
    @api.model
    def cron_expire_delegations(self):
        """Deactivate expired delegations."""
        now = fields.Datetime.now()
        
        expired_delegations = self.search([
            ('active', '=', True),
            ('end_date', '!=', False),
            ('end_date', '<', now),
        ])
        
        for delegation in expired_delegations:
            try:
                delegation.write({
                    'active': False,
                    'state': 'expired'
                })
                _logger.info(f"Auto-expired delegation {delegation.id}")
            except Exception as e:
                _logger.error(f"Failed to expire delegation {delegation.id}: {e}")
