# -*- coding: utf-8 -*-
"""
OPS Fiscal Period with Lock Control

This module provides fiscal period management with:
- Soft/Hard lock states (OPS Enhancement over OM)
- Branch-level locking capability
- Period close checklist workflow

Adopted from: om_fiscal_year patterns
Enhanced with: OPS multi-branch and workflow features
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsFiscalPeriod(models.Model):
    """Fiscal Period with Lock Control."""
    _name = 'ops.fiscal.period'
    _description = 'Fiscal Period with Lock Control'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    name = fields.Char(
        string='Period Name',
        required=True,
        tracking=True,
        help="Display name for this fiscal period (e.g., 'January 2026')"
    )
    code = fields.Char(
        string='Code',
        size=10,
        help="Short code for reference (e.g., '2026-01')"
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )

    date_from = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
        help="First day of this fiscal period"
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
        help="Last day of this fiscal period"
    )

    # Fiscal Year Reference
    fiscal_year = fields.Char(
        string='Fiscal Year',
        compute='_compute_fiscal_year',
        store=True,
        help="Fiscal year derived from start date"
    )

    # Lock States - OPS Enhancement over OM
    lock_state = fields.Selection([
        ('open', 'Open'),
        ('soft_lock', 'Soft Lock (Warning)'),
        ('hard_lock', 'Hard Lock (Blocked)'),
    ], string='Lock Status', default='open', tracking=True, index=True,
       help="Open: Normal posting allowed\n"
            "Soft Lock: Warning on post but allowed\n"
            "Hard Lock: No posting allowed")

    # Branch-Level Locking - OPS Enhancement
    branch_lock_ids = fields.One2many(
        'ops.fiscal.period.branch.lock',
        'period_id',
        string='Branch Lock Status',
        help="Individual lock status per branch"
    )

    # Close Checklist
    checklist_ids = fields.One2many(
        'ops.period.close.checklist',
        'period_id',
        string='Close Checklist',
        help="Period-end closing checklist items"
    )
    checklist_progress = fields.Float(
        string='Checklist Progress',
        compute='_compute_checklist_progress',
        store=True,
        help="Percentage of checklist items completed"
    )
    checklist_count = fields.Integer(
        string='Checklist Items',
        compute='_compute_checklist_progress',
        store=True
    )
    checklist_done_count = fields.Integer(
        string='Completed Items',
        compute='_compute_checklist_progress',
        store=True
    )

    # Audit Fields
    locked_by = fields.Many2one(
        'res.users',
        string='Locked By',
        readonly=True,
        help="User who last changed the lock state"
    )
    locked_date = fields.Datetime(
        string='Locked Date',
        readonly=True,
        help="Date/time when lock state was last changed"
    )

    # Activity Tracking
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    # Odoo 19 constraints syntax
    _date_check = models.Constraint(
        'CHECK(date_to >= date_from)',
        'End date must be after start date'
    )
    _unique_period = models.Constraint(
        'UNIQUE(company_id, date_from, date_to)',
        'Period dates must be unique per company'
    )

    @api.depends('date_from')
    def _compute_fiscal_year(self):
        """Compute fiscal year from start date."""
        for period in self:
            if period.date_from:
                period.fiscal_year = str(period.date_from.year)
            else:
                period.fiscal_year = False

    @api.depends('checklist_ids.is_done')
    def _compute_checklist_progress(self):
        """Compute checklist completion percentage."""
        for period in self:
            total = len(period.checklist_ids)
            done = len(period.checklist_ids.filtered('is_done'))
            period.checklist_count = total
            period.checklist_done_count = done
            period.checklist_progress = (done / total * 100) if total else 0

    @api.constrains('date_from', 'date_to', 'company_id')
    def _check_dates_overlap(self):
        """Prevent overlapping periods (adopted from OM)."""
        for period in self:
            overlapping = self.search([
                ('id', '!=', period.id),
                ('company_id', '=', period.company_id.id),
                ('date_from', '<=', period.date_to),
                ('date_to', '>=', period.date_from),
            ])
            if overlapping:
                raise ValidationError(_(
                    'Period dates overlap with: %s'
                ) % ', '.join(overlapping.mapped('name')))

    @api.model
    def get_period_for_date(self, date, company_id=None):
        """Get the fiscal period for a given date.

        Args:
            date: The date to look up
            company_id: Company ID (defaults to current company)

        Returns:
            ops.fiscal.period record or empty recordset
        """
        if not company_id:
            company_id = self.env.company.id

        return self.search([
            ('company_id', '=', company_id),
            ('date_from', '<=', date),
            ('date_to', '>=', date),
        ], limit=1)

    def action_soft_lock(self):
        """Soft lock - users get warning but can still post."""
        self.write({
            'lock_state': 'soft_lock',
            'locked_by': self.env.uid,
            'locked_date': fields.Datetime.now(),
        })
        for period in self:
            period.message_post(
                body=_('Period soft-locked by %s. Users will see a warning when posting.') % self.env.user.name,
                message_type='notification'
            )
        return True

    def action_hard_lock(self):
        """Hard lock - no posting allowed."""
        for period in self:
            if period.checklist_progress < 100 and period.checklist_ids:
                raise UserError(_(
                    'Cannot hard lock period until checklist is 100%% complete.\n'
                    'Current progress: %.0f%% (%d of %d items)'
                ) % (period.checklist_progress, period.checklist_done_count, period.checklist_count))

        self.write({
            'lock_state': 'hard_lock',
            'locked_by': self.env.uid,
            'locked_date': fields.Datetime.now(),
        })
        for period in self:
            period.message_post(
                body=_('Period hard-locked by %s. No posting is allowed.') % self.env.user.name,
                message_type='notification'
            )
        return True

    def action_unlock(self):
        """Unlock period (requires manager permissions)."""
        self.write({
            'lock_state': 'open',
            'locked_by': False,
            'locked_date': False,
        })
        for period in self:
            period.message_post(
                body=_('Period unlocked by %s.') % self.env.user.name,
                message_type='notification'
            )
        return True

    def action_generate_checklist(self):
        """Generate standard close checklist items."""
        self.ensure_one()
        if self.checklist_ids:
            raise UserError(_(
                'Checklist already exists for this period. '
                'Clear existing items first if you want to regenerate.'
            ))
        self.env['ops.period.close.checklist'].generate_for_period(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Checklist Generated'),
                'message': _('Standard period close checklist has been generated.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_clear_checklist(self):
        """Clear all checklist items."""
        self.ensure_one()
        self.checklist_ids.unlink()
        return True

    def action_open_close_wizard(self):
        """Open the period close wizard."""
        self.ensure_one()
        return {
            'name': _('Close Period: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'ops.period.close.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_period_id': self.id,
            }
        }

    def action_view_checklist(self):
        """Open checklist items for this period."""
        self.ensure_one()
        return {
            'name': _('Checklist: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'ops.period.close.checklist',
            'view_mode': 'tree',
            'domain': [('period_id', '=', self.id)],
            'context': {
                'default_period_id': self.id,
            }
        }


class OpsFiscalPeriodBranchLock(models.Model):
    """Branch-level period lock status.

    Allows locking periods at the branch level, so different branches
    can be at different stages of period close.
    """
    _name = 'ops.fiscal.period.branch.lock'
    _description = 'Period Branch Lock'
    _order = 'period_id, ops_branch_id'

    period_id = fields.Many2one(
        'ops.fiscal.period',
        string='Fiscal Period',
        required=True,
        ondelete='cascade'
    )
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=True,
        ondelete='restrict'
    )
    lock_state = fields.Selection([
        ('open', 'Open'),
        ('soft_lock', 'Soft Lock'),
        ('hard_lock', 'Hard Lock'),
    ], default='open', string='Status')
    locked_by = fields.Many2one(
        'res.users',
        string='Locked By',
        readonly=True
    )
    locked_date = fields.Datetime(
        string='Locked Date',
        readonly=True
    )
    notes = fields.Text(string='Notes')

    # Odoo 19 constraints syntax
    _unique_branch_period = models.Constraint(
        'UNIQUE(period_id, ops_branch_id)',
        'Each branch can only have one lock status per period'
    )

    def action_soft_lock(self):
        """Soft lock this branch for the period."""
        self.write({
            'lock_state': 'soft_lock',
            'locked_by': self.env.uid,
            'locked_date': fields.Datetime.now(),
        })
        return True

    def action_hard_lock(self):
        """Hard lock this branch for the period."""
        self.write({
            'lock_state': 'hard_lock',
            'locked_by': self.env.uid,
            'locked_date': fields.Datetime.now(),
        })
        return True

    def action_unlock(self):
        """Unlock this branch for the period."""
        self.write({
            'lock_state': 'open',
            'locked_by': False,
            'locked_date': False,
        })
        return True


class OpsPeriodCloseChecklist(models.Model):
    """Period close checklist items.

    Provides a structured checklist for period-end close procedures,
    ensuring all necessary tasks are completed before locking.
    """
    _name = 'ops.period.close.checklist'
    _description = 'Period Close Checklist'
    _order = 'sequence, id'

    period_id = fields.Many2one(
        'ops.fiscal.period',
        string='Fiscal Period',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(
        string='Task',
        required=True,
        help="Description of the period close task"
    )
    category = fields.Selection([
        ('cutoff', 'Cutoff Procedures'),
        ('reconciliation', 'Reconciliations'),
        ('accruals', 'Accruals & Provisions'),
        ('review', 'Review & Analysis'),
        ('reporting', 'Reporting'),
        ('approval', 'Approvals'),
    ], string='Category', required=True)

    is_done = fields.Boolean(
        string='Done',
        default=False,
        help="Mark as completed"
    )
    done_by = fields.Many2one(
        'res.users',
        string='Completed By',
        readonly=True
    )
    done_date = fields.Datetime(
        string='Completed Date',
        readonly=True
    )
    notes = fields.Text(
        string='Notes',
        help="Additional notes or comments about this task"
    )

    # Related fields for display
    period_name = fields.Char(
        related='period_id.name',
        string='Period',
        store=True
    )
    period_lock_state = fields.Selection(
        related='period_id.lock_state',
        string='Period Lock',
        store=True
    )

    def action_mark_done(self):
        """Mark checklist item as done."""
        self.write({
            'is_done': True,
            'done_by': self.env.uid,
            'done_date': fields.Datetime.now(),
        })
        return True

    def action_mark_undone(self):
        """Mark checklist item as not done."""
        self.write({
            'is_done': False,
            'done_by': False,
            'done_date': False,
        })
        return True

    @api.model
    def generate_for_period(self, period):
        """Generate standard checklist items for a period.

        Args:
            period: ops.fiscal.period record
        """
        items = [
            # Cutoff Procedures
            (10, 'cutoff', 'Verify all invoices received are entered'),
            (20, 'cutoff', 'Verify all invoices issued are posted'),
            (30, 'cutoff', 'Verify inventory receipts match POs'),
            (40, 'cutoff', 'Verify shipments are invoiced'),

            # Reconciliations
            (50, 'reconciliation', 'Bank reconciliation completed'),
            (60, 'reconciliation', 'AR subledger reconciled to GL'),
            (70, 'reconciliation', 'AP subledger reconciled to GL'),
            (80, 'reconciliation', 'Intercompany balances reconciled'),

            # Accruals & Provisions
            (90, 'accruals', 'Salary accrual posted'),
            (100, 'accruals', 'Depreciation entries posted'),
            (110, 'accruals', 'Prepaid expenses reviewed'),
            (120, 'accruals', 'Provisions reviewed'),

            # Review & Analysis
            (130, 'review', 'Trial balance reviewed'),
            (140, 'review', 'Variance analysis completed'),
            (150, 'review', 'Unusual transactions investigated'),

            # Reporting
            (160, 'reporting', 'Financial statements generated'),
            (170, 'reporting', 'Management reports distributed'),

            # Approvals
            (180, 'approval', 'Controller approval obtained'),
            (190, 'approval', 'CFO sign-off obtained'),
        ]

        checklist_items = []
        for seq, cat, name in items:
            checklist_items.append({
                'period_id': period.id,
                'sequence': seq,
                'category': cat,
                'name': name,
            })

        self.create(checklist_items)
        _logger.info('Generated %d checklist items for period %s', len(items), period.name)
