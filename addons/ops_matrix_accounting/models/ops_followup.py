# -*- coding: utf-8 -*-
"""
OPS Customer Follow-up System
Adopted from OM om_account_followup, enhanced with:
- Branch assignment
- Approval workflow for credit release
- Activity scheduling
"""

from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsFollowup(models.Model):
    """Follow-up configuration for a company."""
    _name = 'ops.followup'
    _description = 'Customer Follow-up Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company,
        ondelete='cascade'
    )

    followup_line_ids = fields.One2many(
        'ops.followup.line', 'followup_id',
        string='Follow-up Levels', copy=True
    )

    # OPS Enhancement: Branch-level configuration
    branch_specific = fields.Boolean(
        string='Branch-Specific Follow-up',
        default=False,
        help='Allow different follow-up settings per branch'
    )

    # Default settings
    default_partner_days = fields.Integer(
        string='Default Payment Terms (Days)',
        default=30,
        help='Default number of days for payment if not specified on partner'
    )

    auto_send_email = fields.Boolean(
        string='Auto-Send Emails',
        default=False,
        help='Automatically send follow-up emails via cron'
    )

    _company_uniq = models.Constraint(
        'UNIQUE(company_id)',
        'Only one follow-up configuration per company is allowed.'
    )

    @api.model
    def get_or_create_followup(self, company_id=None):
        """Get or create follow-up configuration for company."""
        company = self.env['res.company'].browse(company_id) if company_id else self.env.company
        followup = self.search([('company_id', '=', company.id)], limit=1)
        if not followup:
            followup = self.create({
                'company_id': company.id,
            })
        return followup


class OpsFollowupLine(models.Model):
    """Follow-up escalation level."""
    _name = 'ops.followup.line'
    _description = 'Follow-up Level'
    _order = 'delay asc'

    followup_id = fields.Many2one(
        'ops.followup', string='Follow-up',
        required=True, ondelete='cascade'
    )

    name = fields.Char(string='Level Name', required=True)

    # Delay Configuration (Adopted from OM)
    delay = fields.Integer(
        string='Days Overdue',
        required=True,
        help='Number of days after due date to trigger this level'
    )

    sequence = fields.Integer(
        string='Sequence',
        compute='_compute_sequence',
        store=True,
        help='Auto-computed from delay'
    )

    # Actions
    send_email = fields.Boolean(string='Send Email', default=True)
    email_template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain="[('model', '=', 'res.partner')]"
    )

    send_letter = fields.Boolean(string='Generate Letter', default=False)

    manual_action = fields.Boolean(string='Manual Action Required', default=False)
    manual_action_note = fields.Text(string='Manual Action Instructions')

    # OPS Enhancement: Activity creation
    create_activity = fields.Boolean(string='Create Activity', default=False)
    activity_type_id = fields.Many2one(
        'mail.activity.type', string='Activity Type'
    )
    activity_user_id = fields.Many2one(
        'res.users', string='Assign To',
        help='Leave empty to assign to salesperson'
    )
    activity_days = fields.Integer(
        string='Activity Due In (Days)',
        default=3,
        help='Number of days until activity is due'
    )

    # OPS Enhancement: Credit block
    block_credit = fields.Boolean(
        string='Block Credit',
        default=False,
        help='Prevent new sales orders for this customer'
    )

    description = fields.Html(string='Follow-up Message')

    @api.depends('delay', 'followup_id', 'followup_id.followup_line_ids', 'followup_id.followup_line_ids.delay')
    def _compute_sequence(self):
        """Auto-compute sequence based on delay (Adopted from OM)."""
        for line in self:
            if line.followup_id:
                delays = sorted(line.followup_id.followup_line_ids.mapped('delay'))
                line.sequence = delays.index(line.delay) + 1 if line.delay in delays else 0
            else:
                line.sequence = 0

    @api.constrains('delay')
    def _check_delay(self):
        for line in self:
            if line.delay < 0:
                raise ValidationError(_('Days Overdue cannot be negative.'))


class OpsPartnerFollowup(models.Model):
    """Partner follow-up status tracking."""
    _name = 'ops.partner.followup'
    _description = 'Partner Follow-up Status'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner', string='Customer',
        required=True, ondelete='cascade',
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    # OPS Enhancement
    ops_branch_id = fields.Many2one(
        'ops.branch', string='Branch',
        index=True,
        tracking=True
    )

    # Current Status
    followup_level_id = fields.Many2one(
        'ops.followup.line', string='Current Level',
        readonly=True,
        tracking=True
    )
    followup_level_sequence = fields.Integer(
        related='followup_level_id.sequence',
        string='Level #'
    )

    max_overdue_days = fields.Integer(
        string='Max Days Overdue',
        compute='_compute_overdue',
        store=True
    )

    total_overdue_amount = fields.Monetary(
        string='Total Overdue',
        compute='_compute_overdue',
        store=True
    )

    total_balance = fields.Monetary(
        string='Total Balance',
        compute='_compute_overdue',
        store=True
    )

    currency_id = fields.Many2one(
        related='company_id.currency_id'
    )

    overdue_invoice_count = fields.Integer(
        string='Overdue Invoices',
        compute='_compute_overdue',
        store=True
    )

    # Last Action
    last_followup_date = fields.Date(
        string='Last Follow-up Date',
        tracking=True
    )
    last_followup_level_id = fields.Many2one(
        'ops.followup.line', string='Last Level Sent'
    )
    next_followup_date = fields.Date(
        string='Next Follow-up Date',
        compute='_compute_next_followup',
        store=True
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active Follow-up'),
        ('resolved', 'Resolved'),
        ('blocked', 'Credit Blocked'),
    ], string='Status', default='draft', tracking=True)

    # Credit Block Status (OPS Enhancement)
    credit_blocked = fields.Boolean(
        string='Credit Blocked',
        default=False,
        tracking=True
    )
    credit_block_reason = fields.Text(string='Block Reason')
    credit_override = fields.Boolean(
        string='Credit Override',
        default=False,
        tracking=True,
        help='Override credit block (requires approval)'
    )
    credit_override_by = fields.Many2one('res.users', string='Override By', readonly=True)
    credit_override_date = fields.Datetime(string='Override Date', readonly=True)
    credit_override_reason = fields.Text(string='Override Reason')
    credit_override_expiry = fields.Date(
        string='Override Expiry',
        help='Date when override expires automatically'
    )

    # Notes
    notes = fields.Text(string='Notes')

    # History
    followup_history_ids = fields.One2many(
        'ops.partner.followup.history',
        'partner_followup_id',
        string='Follow-up History'
    )

    _partner_company_uniq = models.Constraint(
        'UNIQUE(partner_id, company_id)',
        'Only one follow-up record per partner per company.'
    )

    @api.depends('partner_id', 'partner_id.invoice_ids', 'partner_id.invoice_ids.amount_residual',
                 'partner_id.invoice_ids.invoice_date_due', 'partner_id.invoice_ids.state',
                 'partner_id.invoice_ids.payment_state')
    def _compute_overdue(self):
        """Compute overdue amount and days."""
        today = fields.Date.today()

        for record in self:
            # Get overdue invoices
            invoices = self.env['account.move'].search([
                ('partner_id', '=', record.partner_id.id),
                ('company_id', '=', record.company_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date_due', '<', today),
            ])

            # Get total balance (all unpaid invoices)
            all_invoices = self.env['account.move'].search([
                ('partner_id', '=', record.partner_id.id),
                ('company_id', '=', record.company_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
            ])

            if invoices:
                record.total_overdue_amount = sum(invoices.mapped('amount_residual'))
                record.overdue_invoice_count = len(invoices)
                oldest_due = min(invoices.mapped('invoice_date_due'))
                record.max_overdue_days = (today - oldest_due).days
            else:
                record.total_overdue_amount = 0.0
                record.overdue_invoice_count = 0
                record.max_overdue_days = 0

            record.total_balance = sum(all_invoices.mapped('amount_residual'))

    @api.depends('last_followup_date', 'followup_level_id', 'followup_level_id.followup_id.followup_line_ids')
    def _compute_next_followup(self):
        """Compute next follow-up date."""
        for record in self:
            if not record.followup_level_id:
                record.next_followup_date = False
                continue

            # Find next level
            next_level = self.env['ops.followup.line'].search([
                ('followup_id', '=', record.followup_level_id.followup_id.id),
                ('sequence', '>', record.followup_level_id.sequence),
            ], limit=1, order='sequence asc')

            if next_level and record.last_followup_date:
                days_diff = next_level.delay - record.followup_level_id.delay
                record.next_followup_date = record.last_followup_date + timedelta(days=days_diff)
            else:
                record.next_followup_date = False

    def action_send_followup(self):
        """Execute follow-up action for current level."""
        self.ensure_one()

        if not self.followup_level_id:
            raise UserError(_('No follow-up level set.'))

        level = self.followup_level_id

        # Create history record
        history_vals = {
            'partner_followup_id': self.id,
            'followup_level_id': level.id,
            'date': fields.Date.today(),
            'user_id': self.env.uid,
            'action_taken': [],
        }
        actions = []

        # Send email
        if level.send_email and level.email_template_id:
            try:
                level.email_template_id.send_mail(self.partner_id.id)
                actions.append('Email sent')
                _logger.info(f"Sent follow-up email to {self.partner_id.name}")
            except Exception as e:
                _logger.error(f"Failed to send follow-up email: {e}")
                actions.append(f'Email failed: {e}')

        # Create activity
        if level.create_activity and level.activity_type_id:
            user = level.activity_user_id or self.partner_id.user_id or self.env.user
            try:
                self.partner_id.activity_schedule(
                    activity_type_id=level.activity_type_id.id,
                    summary=f'Follow-up Level {level.sequence}: {level.name}',
                    note=level.manual_action_note or '',
                    user_id=user.id,
                    date_deadline=fields.Date.today() + timedelta(days=level.activity_days),
                )
                actions.append('Activity created')
            except Exception as e:
                _logger.error(f"Failed to create activity: {e}")
                actions.append(f'Activity failed: {e}')

        # Apply credit block
        if level.block_credit and not self.credit_override:
            self.write({
                'credit_blocked': True,
                'credit_block_reason': f'Auto-blocked at follow-up level {level.sequence}: {level.name}',
                'state': 'blocked',
            })
            actions.append('Credit blocked')

        # Update history
        history_vals['action_taken'] = ', '.join(actions) if actions else 'No action'
        self.env['ops.partner.followup.history'].create(history_vals)

        # Update status
        self.write({
            'last_followup_date': fields.Date.today(),
            'last_followup_level_id': level.id,
            'state': 'active' if not self.credit_blocked else self.state,
        })

        # Advance to next level
        next_level = self.env['ops.followup.line'].search([
            ('followup_id', '=', level.followup_id.id),
            ('sequence', '>', level.sequence),
        ], limit=1, order='sequence asc')

        if next_level:
            self.followup_level_id = next_level.id

        # Post message
        self.message_post(body=_(
            'Follow-up Level %(level)s sent. Actions: %(actions)s',
            level=level.name,
            actions=', '.join(actions) if actions else 'None'
        ))

        return True

    def action_request_credit_override(self):
        """Request credit override approval."""
        self.ensure_one()

        return {
            'name': _('Request Credit Override'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.credit.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_followup_id': self.id,
            }
        }

    def action_approve_credit_override(self):
        """Approve credit override (manager action)."""
        self.ensure_one()
        self.write({
            'credit_override': True,
            'credit_override_by': self.env.uid,
            'credit_override_date': fields.Datetime.now(),
            'state': 'active',
        })
        self.message_post(body=_(
            'Credit override approved by %(user)s',
            user=self.env.user.name
        ))

    def action_revoke_credit_override(self):
        """Revoke credit override."""
        self.write({
            'credit_override': False,
            'credit_override_by': False,
            'credit_override_date': False,
            'credit_override_reason': False,
            'credit_override_expiry': False,
        })
        # Re-apply block if at blocking level
        if self.followup_level_id and self.followup_level_id.block_credit:
            self.write({
                'credit_blocked': True,
                'state': 'blocked',
            })
        self.message_post(body=_('Credit override revoked.'))

    def action_mark_resolved(self):
        """Mark follow-up as resolved."""
        self.write({
            'state': 'resolved',
            'credit_blocked': False,
            'followup_level_id': False,
        })
        self.message_post(body=_('Follow-up marked as resolved.'))

    def action_reset_followup(self):
        """Reset follow-up to beginning."""
        followup = self.env['ops.followup'].get_or_create_followup(self.company_id.id)
        first_level = self.env['ops.followup.line'].search([
            ('followup_id', '=', followup.id),
        ], limit=1, order='sequence asc')

        self.write({
            'followup_level_id': first_level.id if first_level else False,
            'state': 'draft',
            'credit_blocked': False,
            'credit_override': False,
            'last_followup_date': False,
        })
        self.message_post(body=_('Follow-up reset to beginning.'))

    def action_view_overdue_invoices(self):
        """Open list of overdue invoices."""
        self.ensure_one()
        return {
            'name': _('Overdue Invoices - %s') % self.partner_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [
                ('partner_id', '=', self.partner_id.id),
                ('company_id', '=', self.company_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date_due', '<', fields.Date.today()),
            ],
            'context': {
                'default_partner_id': self.partner_id.id,
            }
        }

    @api.model
    def cron_process_followups(self):
        """Scheduled action to process all follow-ups."""
        today = fields.Date.today()
        _logger.info("Starting follow-up processing cron job")

        # Find all partners with overdue invoices
        overdue_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('invoice_date_due', '<', today),
        ])

        partner_ids = overdue_invoices.mapped('partner_id').ids

        for partner_id in partner_ids:
            partner = self.env['res.partner'].browse(partner_id)

            # Get or create follow-up record
            followup_status = self.search([
                ('partner_id', '=', partner_id),
                ('company_id', '=', self.env.company.id),
            ], limit=1)

            if not followup_status:
                # Create new follow-up record
                followup_config = self.env['ops.followup'].get_or_create_followup()
                first_level = self.env['ops.followup.line'].search([
                    ('followup_id', '=', followup_config.id),
                ], limit=1, order='sequence asc')

                followup_status = self.create({
                    'partner_id': partner_id,
                    'company_id': self.env.company.id,
                    'followup_level_id': first_level.id if first_level else False,
                    'state': 'draft',
                })

            # Determine appropriate follow-up level based on overdue days
            if followup_status.max_overdue_days > 0:
                followup_config = self.env['ops.followup'].get_or_create_followup()

                # Find appropriate level based on days overdue
                appropriate_level = self.env['ops.followup.line'].search([
                    ('followup_id', '=', followup_config.id),
                    ('delay', '<=', followup_status.max_overdue_days),
                ], limit=1, order='delay desc')

                if appropriate_level and appropriate_level != followup_status.followup_level_id:
                    followup_status.followup_level_id = appropriate_level.id

                # Check if auto-send is enabled and we should send
                if followup_config.auto_send_email and followup_status.followup_level_id:
                    # Only send if we haven't sent recently for this level
                    if (not followup_status.last_followup_date or
                        followup_status.last_followup_level_id != followup_status.followup_level_id):
                        try:
                            followup_status.action_send_followup()
                        except Exception as e:
                            _logger.error(f"Error processing follow-up for {partner.name}: {e}")

        # Check for expired credit overrides
        expired_overrides = self.search([
            ('credit_override', '=', True),
            ('credit_override_expiry', '!=', False),
            ('credit_override_expiry', '<', today),
        ])
        for record in expired_overrides:
            record.action_revoke_credit_override()
            _logger.info(f"Credit override expired for {record.partner_id.name}")

        _logger.info(f"Follow-up processing complete. Processed {len(partner_ids)} partners.")

        return True


class OpsPartnerFollowupHistory(models.Model):
    """Follow-up action history."""
    _name = 'ops.partner.followup.history'
    _description = 'Follow-up History'
    _order = 'date desc, id desc'

    partner_followup_id = fields.Many2one(
        'ops.partner.followup',
        string='Follow-up Record',
        required=True,
        ondelete='cascade'
    )
    partner_id = fields.Many2one(
        related='partner_followup_id.partner_id',
        store=True
    )

    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    followup_level_id = fields.Many2one(
        'ops.followup.line',
        string='Follow-up Level'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Performed By',
        default=lambda self: self.env.uid
    )

    action_taken = fields.Char(string='Actions Taken')
    notes = fields.Text(string='Notes')


class OpsCreditOverrideWizard(models.TransientModel):
    """Wizard for credit override request."""
    _name = 'ops.credit.override.wizard'
    _description = 'Credit Override Request'

    partner_followup_id = fields.Many2one(
        'ops.partner.followup', required=True
    )
    partner_id = fields.Many2one(
        related='partner_followup_id.partner_id'
    )
    total_overdue = fields.Monetary(
        related='partner_followup_id.total_overdue_amount'
    )
    currency_id = fields.Many2one(
        related='partner_followup_id.currency_id'
    )
    max_overdue_days = fields.Integer(
        related='partner_followup_id.max_overdue_days'
    )
    current_level = fields.Many2one(
        related='partner_followup_id.followup_level_id'
    )

    reason = fields.Text(
        string='Override Reason',
        required=True,
        help='Explain why credit override is needed'
    )

    override_expiry = fields.Date(
        string='Override Expiry Date',
        help='Leave empty for indefinite override'
    )

    def action_submit_request(self):
        """Submit override request."""
        self.ensure_one()

        self.partner_followup_id.write({
            'credit_override_reason': self.reason,
            'credit_override_expiry': self.override_expiry,
        })

        # Create activity for credit manager
        manager_group = self.env.ref('account.group_account_manager', raise_if_not_found=False)
        if manager_group and manager_group.users:
            self.partner_followup_id.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('Credit Override Request'),
                note=_(
                    'Credit override requested for %(partner)s.\n'
                    'Overdue Amount: %(amount)s %(currency)s\n'
                    'Days Overdue: %(days)s\n'
                    'Reason: %(reason)s',
                    partner=self.partner_id.name,
                    amount=self.total_overdue,
                    currency=self.currency_id.name,
                    days=self.max_overdue_days,
                    reason=self.reason
                ),
                user_id=manager_group.users[0].id,
            )

        self.partner_followup_id.message_post(body=_(
            'Credit override requested.\nReason: %(reason)s',
            reason=self.reason
        ))

        return {'type': 'ir.actions.act_window_close'}


# Extend res.partner
class ResPartnerFollowupExtension(models.Model):
    _inherit = 'res.partner'

    followup_status_id = fields.Many2one(
        'ops.partner.followup',
        string='Follow-up Status',
        compute='_compute_followup_status',
        store=False
    )

    credit_blocked = fields.Boolean(
        string='Credit Blocked',
        compute='_compute_credit_status',
        store=False
    )

    overdue_amount = fields.Monetary(
        string='Overdue Amount',
        compute='_compute_credit_status',
        store=False
    )

    def _compute_followup_status(self):
        for partner in self:
            status = self.env['ops.partner.followup'].search([
                ('partner_id', '=', partner.id),
                ('company_id', '=', self.env.company.id),
            ], limit=1)
            partner.followup_status_id = status.id if status else False

    def _compute_credit_status(self):
        for partner in self:
            if partner.followup_status_id:
                blocked = partner.followup_status_id.credit_blocked
                override = partner.followup_status_id.credit_override
                partner.credit_blocked = blocked and not override
                partner.overdue_amount = partner.followup_status_id.total_overdue_amount
            else:
                partner.credit_blocked = False
                partner.overdue_amount = 0.0

    def action_view_followup(self):
        """Open follow-up status for this partner."""
        self.ensure_one()

        followup = self.env['ops.partner.followup'].search([
            ('partner_id', '=', self.id),
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        if not followup:
            # Create one
            followup_config = self.env['ops.followup'].get_or_create_followup()
            first_level = self.env['ops.followup.line'].search([
                ('followup_id', '=', followup_config.id),
            ], limit=1, order='sequence asc')

            followup = self.env['ops.partner.followup'].create({
                'partner_id': self.id,
                'company_id': self.env.company.id,
                'followup_level_id': first_level.id if first_level else False,
            })

        return {
            'name': _('Follow-up Status'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.partner.followup',
            'view_mode': 'form',
            'res_id': followup.id,
        }
