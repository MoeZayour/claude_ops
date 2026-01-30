# -*- coding: utf-8 -*-
"""
OPS Recurring Journal Framework
Adopted from OM recurring_payments, enhanced with:
- Full journal entry support (not just payments)
- Branch/BU assignment
- Approval workflow
- Auto-reversal capability
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsRecurringTemplate(models.Model):
    """
    Recurring Journal Entry Template.
    Defines the pattern for entries that repeat on a schedule.
    """
    _name = 'ops.recurring.template'
    _description = 'Recurring Journal Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Template Name', required=True, tracking=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    # Journal Configuration
    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        required=True, tracking=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]"
    )

    # OPS Matrix Dimensions
    ops_branch_id = fields.Many2one(
        'ops.branch', string='Branch',
        tracking=True, index=True
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit', string='Business Unit',
        tracking=True
    )

    # Schedule Configuration (Adopted from OM)
    recurring_period = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], string='Period Type', required=True, default='months', tracking=True)

    recurring_interval = fields.Integer(
        string='Repeat Every',
        required=True, default=1,
        help='Repeat every X periods'
    )

    # Date Range
    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    date_end = fields.Date(
        string='End Date',
        tracking=True,
        help='Leave empty for indefinite recurrence'
    )
    next_execution_date = fields.Date(
        string='Next Execution',
        compute='_compute_next_execution',
        store=True
    )

    # Entry Configuration
    journal_state = fields.Selection([
        ('draft', 'Create as Draft'),
        ('posted', 'Auto-Post'),
    ], string='Entry Status', required=True, default='draft',
       help='Status of generated journal entries')

    # Auto-Reversal (OPS Enhancement)
    auto_reverse = fields.Boolean(
        string='Auto-Reverse',
        default=False,
        help='Automatically create reversal entry'
    )
    reversal_date_offset = fields.Integer(
        string='Reversal After (Days)',
        default=1,
        help='Days after entry date to create reversal'
    )

    # Approval (OPS Enhancement)
    require_approval = fields.Boolean(
        string='Require Approval',
        default=False,
        help='Require manager approval before posting'
    )

    # Template Lines
    line_ids = fields.One2many(
        'ops.recurring.template.line', 'template_id',
        string='Entry Lines', copy=True
    )

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('done', 'Completed'),
    ], string='Status', default='draft', tracking=True, index=True)

    # Statistics
    entry_count = fields.Integer(
        string='Entries Created',
        compute='_compute_entry_count'
    )
    entry_ids = fields.One2many(
        'ops.recurring.entry', 'template_id',
        string='Generated Entries'
    )

    description = fields.Text(string='Description')

    @api.depends('date_start', 'recurring_period', 'recurring_interval', 'entry_ids.entry_date', 'state')
    def _compute_next_execution(self):
        for template in self:
            if template.state != 'active':
                template.next_execution_date = False
                continue

            # Find last execution
            last_entry = template.entry_ids.sorted('entry_date', reverse=True)[:1]
            if last_entry:
                base_date = last_entry.entry_date
            else:
                base_date = template.date_start - template._get_relativedelta()

            next_date = base_date + template._get_relativedelta()

            # Check end date
            if template.date_end and next_date > template.date_end:
                template.next_execution_date = False
            else:
                template.next_execution_date = next_date

    def _get_relativedelta(self):
        """Get relativedelta based on period type."""
        self.ensure_one()
        interval = self.recurring_interval
        period = self.recurring_period

        if period == 'days':
            return relativedelta(days=interval)
        elif period == 'weeks':
            return relativedelta(weeks=interval)
        elif period == 'months':
            return relativedelta(months=interval)
        elif period == 'years':
            return relativedelta(years=interval)
        return relativedelta(months=1)

    def _compute_entry_count(self):
        for template in self:
            template.entry_count = len(template.entry_ids)

    @api.constrains('line_ids')
    def _check_balanced_lines(self):
        for template in self:
            if template.line_ids:
                total_debit = sum(template.line_ids.mapped('debit'))
                total_credit = sum(template.line_ids.mapped('credit'))
                if abs(total_debit - total_credit) > 0.01:
                    raise ValidationError(_(
                        'Template lines must be balanced. '
                        'Debit: %(debit).2f, Credit: %(credit).2f'
                    ) % {'debit': total_debit, 'credit': total_credit})

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for template in self:
            if template.date_end and template.date_end < template.date_start:
                raise ValidationError(_('End date must be after start date.'))

    def action_activate(self):
        """Activate the recurring template."""
        for template in self:
            if not template.line_ids:
                raise UserError(_('Please add at least one line before activating.'))
        self.write({'state': 'active'})
        self._compute_next_execution()

    def action_pause(self):
        """Pause the recurring template."""
        self.write({'state': 'paused'})

    def action_resume(self):
        """Resume a paused template."""
        self.write({'state': 'active'})
        self._compute_next_execution()

    def action_complete(self):
        """Mark template as completed."""
        self.write({'state': 'done'})

    def action_reset_to_draft(self):
        """Reset to draft state."""
        self.write({'state': 'draft'})

    def action_view_entries(self):
        """View generated entries."""
        self.ensure_one()
        return {
            'name': _('Recurring Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.recurring.entry',
            'view_mode': 'tree,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }

    def action_generate_entry_now(self):
        """Manually generate entry for current date."""
        self.ensure_one()
        if self.state != 'active':
            raise UserError(_('Template must be active to generate entries.'))

        return self._generate_entry(fields.Date.today())

    def _generate_entry(self, entry_date):
        """
        Generate a recurring entry for the given date.

        Returns:
            ops.recurring.entry record
        """
        self.ensure_one()

        entry_vals = {
            'template_id': self.id,
            'entry_date': entry_date,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'ops_branch_id': self.ops_branch_id.id if self.ops_branch_id else False,
            'ops_business_unit_id': self.ops_business_unit_id.id if self.ops_business_unit_id else False,
            'state': 'draft',
            'auto_reverse': self.auto_reverse,
            'reversal_date': entry_date + relativedelta(days=self.reversal_date_offset) if self.auto_reverse else False,
        }

        # Generate lines from template
        line_vals = []
        for tpl_line in self.line_ids:
            line_vals.append((0, 0, {
                'account_id': tpl_line.account_id.id,
                'name': tpl_line.name or self.name,
                'debit': tpl_line.debit,
                'credit': tpl_line.credit,
                'partner_id': tpl_line.partner_id.id if tpl_line.partner_id else False,
                'analytic_distribution': tpl_line.analytic_distribution,
            }))

        entry_vals['line_ids'] = line_vals

        entry = self.env['ops.recurring.entry'].create(entry_vals)

        _logger.info("Generated recurring entry %s from template %s", entry.name, self.name)

        # Auto-post if configured
        if self.journal_state == 'posted' and not self.require_approval:
            entry.action_create_move()
            entry.action_post_move()

        return entry

    @api.model
    def cron_generate_recurring_entries(self):
        """
        Cron job to generate recurring entries.
        Runs daily, creates entries for all active templates due today.
        """
        _logger.info("=" * 60)
        _logger.info("OPS Recurring Entry Generation Cron Started")
        _logger.info("=" * 60)

        today = fields.Date.today()

        # Find active templates with due entries
        templates = self.search([
            ('state', '=', 'active'),
            ('next_execution_date', '<=', today),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', today),
        ])

        _logger.info("Found %d templates due for execution", len(templates))

        created_count = 0
        error_count = 0

        for template in templates:
            try:
                entry = template._generate_entry(template.next_execution_date)
                created_count += 1
                _logger.info("Generated entry %s from %s", entry.name, template.name)

                # Check if template is complete
                if template.date_end and template.next_execution_date >= template.date_end:
                    template.action_complete()
                    _logger.info("Template %s marked as completed", template.name)

            except Exception as e:
                error_count += 1
                _logger.error("Error generating entry for %s: %s", template.name, e)
                template.message_post(body=_(
                    'Error generating recurring entry: %s'
                ) % str(e))

        _logger.info("=" * 60)
        _logger.info("Recurring Cron Completed: Created %d, Errors %d", created_count, error_count)
        _logger.info("=" * 60)

        return {'created': created_count, 'errors': error_count}


class OpsRecurringTemplateLine(models.Model):
    """Template line defining account and amounts."""
    _name = 'ops.recurring.template.line'
    _description = 'Recurring Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'ops.recurring.template',
        string='Template',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(default=10)

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    name = fields.Char(string='Label')

    debit = fields.Monetary(string='Debit', default=0.0)
    credit = fields.Monetary(string='Credit', default=0.0)

    currency_id = fields.Many2one(
        related='template_id.company_id.currency_id'
    )

    partner_id = fields.Many2one('res.partner', string='Partner')
    analytic_distribution = fields.Json(string='Analytic Distribution')

    @api.constrains('debit', 'credit')
    def _check_debit_credit(self):
        for line in self:
            if line.debit < 0 or line.credit < 0:
                raise ValidationError(_('Debit and credit must be positive.'))
            if line.debit > 0 and line.credit > 0:
                raise ValidationError(_('A line cannot have both debit and credit.'))
            if line.debit == 0 and line.credit == 0:
                raise ValidationError(_('A line must have either debit or credit.'))


class OpsRecurringEntry(models.Model):
    """
    Generated recurring entry instance.
    Links template to actual journal entry.
    """
    _name = 'ops.recurring.entry'
    _description = 'Recurring Journal Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'entry_date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        readonly=True
    )

    template_id = fields.Many2one(
        'ops.recurring.template',
        string='Template',
        required=True,
        ondelete='restrict',
        tracking=True
    )

    entry_date = fields.Date(
        string='Entry Date',
        required=True,
        tracking=True
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    # OPS Matrix
    ops_branch_id = fields.Many2one('ops.branch', string='Branch', index=True)
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')

    # Entry Lines
    line_ids = fields.One2many(
        'ops.recurring.entry.line', 'entry_id',
        string='Entry Lines'
    )

    # Journal Entry Link
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False
    )
    move_state = fields.Selection(
        related='move_id.state',
        string='Entry Status'
    )

    # Auto-Reversal
    auto_reverse = fields.Boolean(string='Auto-Reverse', default=False)
    reversal_date = fields.Date(string='Reversal Date')
    reversal_move_id = fields.Many2one(
        'account.move',
        string='Reversal Entry',
        readonly=True,
        copy=False
    )

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('reversed', 'Reversed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)

    # Related field to check if approval is required
    require_approval = fields.Boolean(
        related='template_id.require_approval',
        string='Approval Required'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.recurring.entry') or _('New')
        return super().create(vals_list)

    def action_submit_for_approval(self):
        """Submit for manager approval."""
        self.write({'state': 'pending_approval'})

        # Create activity for approver
        for entry in self:
            manager_group = self.env.ref('account.group_account_manager', raise_if_not_found=False)
            if manager_group and manager_group.users:
                entry.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Recurring Entry Approval Required'),
                    note=_('Please review and approve recurring entry: %s') % entry.name,
                    user_id=manager_group.users[0].id,
                )

    def action_approve(self):
        """Approve the entry."""
        self.write({
            'state': 'approved',
            'approved_by': self.env.uid,
            'approved_date': fields.Datetime.now(),
        })
        self.activity_ids.action_done()

    def action_reject(self):
        """Reject and cancel the entry."""
        self.write({'state': 'cancelled'})
        self.activity_ids.action_done()

    def action_create_move(self):
        """Create the journal entry from recurring entry."""
        for entry in self:
            if entry.move_id:
                raise UserError(_('Journal entry already created.'))

            if not entry.line_ids:
                raise UserError(_('No lines to create journal entry.'))

            move_lines = []
            for line in entry.line_ids:
                move_lines.append((0, 0, {
                    'account_id': line.account_id.id,
                    'name': line.name or entry.template_id.name,
                    'debit': line.debit,
                    'credit': line.credit,
                    'partner_id': line.partner_id.id if line.partner_id else False,
                    'analytic_distribution': line.analytic_distribution,
                }))

            move_vals = {
                'date': entry.entry_date,
                'journal_id': entry.journal_id.id,
                'ref': 'Recurring: %s' % entry.template_id.name,
                'line_ids': move_lines,
            }

            # Add OPS Matrix fields if they exist on account.move
            if hasattr(self.env['account.move'], 'ops_branch_id'):
                move_vals['ops_branch_id'] = entry.ops_branch_id.id if entry.ops_branch_id else False
            if hasattr(self.env['account.move'], 'ops_business_unit_id'):
                move_vals['ops_business_unit_id'] = entry.ops_business_unit_id.id if entry.ops_business_unit_id else False

            move = self.env['account.move'].create(move_vals)
            entry.write({'move_id': move.id})

            _logger.info("Created journal entry %s from recurring entry %s", move.name, entry.name)

    def action_post_move(self):
        """Post the journal entry."""
        for entry in self:
            if not entry.move_id:
                raise UserError(_('Please create journal entry first.'))

            entry.move_id.action_post()
            entry.write({'state': 'posted'})

            # Schedule reversal if configured
            if entry.auto_reverse and entry.reversal_date:
                entry.message_post(body=_(
                    'Auto-reversal scheduled for %s'
                ) % entry.reversal_date)

    def action_reverse(self):
        """Create reversal entry."""
        for entry in self:
            if not entry.move_id or entry.move_id.state != 'posted':
                raise UserError(_('Can only reverse posted entries.'))

            if entry.reversal_move_id:
                raise UserError(_('Reversal already created.'))

            # Create reversal using Odoo's standard method
            reversal_wizard = self.env['account.move.reversal'].with_context(
                active_model='account.move',
                active_ids=entry.move_id.ids,
            ).create({
                'date': entry.reversal_date or fields.Date.today(),
                'reason': 'Auto-reversal: %s' % entry.template_id.name,
                'journal_id': entry.journal_id.id,
            })

            reversal_result = reversal_wizard.refund_moves()

            if reversal_result and reversal_result.get('res_id'):
                reversal_move = self.env['account.move'].browse(reversal_result['res_id'])
                entry.write({
                    'reversal_move_id': reversal_move.id,
                    'state': 'reversed',
                })
                _logger.info("Created reversal %s for %s", reversal_move.name, entry.name)

    def action_cancel(self):
        """Cancel the entry."""
        for entry in self:
            if entry.move_id and entry.move_id.state == 'posted':
                raise UserError(_('Cannot cancel posted entries. Reverse instead.'))
            if entry.move_id:
                entry.move_id.button_cancel()
                entry.move_id.unlink()
        self.write({'state': 'cancelled', 'move_id': False})

    @api.model
    def cron_process_auto_reversals(self):
        """
        Cron job to process auto-reversals.
        Creates reversal entries for posted entries with reversal_date <= today.
        """
        _logger.info("=" * 60)
        _logger.info("OPS Auto-Reversal Processing Cron Started")
        _logger.info("=" * 60)

        today = fields.Date.today()

        # Find entries due for reversal
        entries = self.search([
            ('state', '=', 'posted'),
            ('auto_reverse', '=', True),
            ('reversal_date', '<=', today),
            ('reversal_move_id', '=', False),
        ])

        _logger.info("Found %d entries due for auto-reversal", len(entries))

        reversed_count = 0
        error_count = 0

        for entry in entries:
            try:
                entry.action_reverse()
                reversed_count += 1
                _logger.info("Reversed entry %s", entry.name)
            except Exception as e:
                error_count += 1
                _logger.error("Error reversing %s: %s", entry.name, e)
                entry.message_post(body=_(
                    'Error processing auto-reversal: %s'
                ) % str(e))

        _logger.info("=" * 60)
        _logger.info("Auto-Reversal Cron Completed: Reversed %d, Errors %d", reversed_count, error_count)
        _logger.info("=" * 60)

        return {'reversed': reversed_count, 'errors': error_count}


class OpsRecurringEntryLine(models.Model):
    """Entry line with account and amounts."""
    _name = 'ops.recurring.entry.line'
    _description = 'Recurring Entry Line'
    _order = 'sequence, id'

    entry_id = fields.Many2one(
        'ops.recurring.entry',
        string='Entry',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(default=10)

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    name = fields.Char(string='Label')

    debit = fields.Monetary(string='Debit', default=0.0)
    credit = fields.Monetary(string='Credit', default=0.0)

    currency_id = fields.Many2one(
        related='entry_id.company_id.currency_id'
    )

    partner_id = fields.Many2one('res.partner', string='Partner')
    analytic_distribution = fields.Json(string='Analytic Distribution')
