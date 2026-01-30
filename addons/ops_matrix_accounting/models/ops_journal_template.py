# -*- coding: utf-8 -*-
"""
OPS Journal Entry Templates
One-click journal entry creation from predefined templates.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class OpsJournalTemplate(models.Model):
    """
    Quick-create journal entry template.
    Unlike recurring templates, these are manually triggered.
    """
    _name = 'ops.journal.template'
    _description = 'Journal Entry Template'
    _order = 'sequence, name'

    name = fields.Char(string='Template Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )

    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        required=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]"
    )

    # OPS Matrix defaults
    ops_branch_id = fields.Many2one('ops.branch', string='Default Branch')
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Default Business Unit')

    # Template Lines
    line_ids = fields.One2many(
        'ops.journal.template.line', 'template_id',
        string='Template Lines', copy=True
    )

    # Usage tracking
    use_count = fields.Integer(
        string='Times Used',
        default=0,
        readonly=True
    )
    last_used = fields.Datetime(string='Last Used', readonly=True)

    description = fields.Text(string='Description')

    # Categories for organization
    category = fields.Selection([
        ('accrual', 'Accruals'),
        ('provision', 'Provisions'),
        ('adjustment', 'Adjustments'),
        ('allocation', 'Allocations'),
        ('correction', 'Corrections'),
        ('closing', 'Period Closing'),
        ('other', 'Other'),
    ], string='Category', default='other')

    @api.constrains('line_ids')
    def _check_balanced(self):
        for template in self:
            if template.line_ids:
                # Only check fixed amount lines
                fixed_lines = template.line_ids.filtered(lambda l: l.amount_type == 'fixed')
                if fixed_lines:
                    debit = sum(fixed_lines.mapped('debit'))
                    credit = sum(fixed_lines.mapped('credit'))
                    if abs(debit - credit) > 0.01:
                        raise ValidationError(_(
                            'Template fixed amount lines must be balanced. Debit: %(debit).2f, Credit: %(credit).2f'
                        ) % {'debit': debit, 'credit': credit})

    def action_create_entry(self):
        """Create journal entry from template."""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_('Template has no lines.'))

        # Open wizard to confirm/adjust
        return {
            'name': _('Create Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.journal.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_template_id': self.id,
                'default_journal_id': self.journal_id.id,
                'default_ops_branch_id': self.ops_branch_id.id if self.ops_branch_id else False,
                'default_ops_business_unit_id': self.ops_business_unit_id.id if self.ops_business_unit_id else False,
            },
        }

    def action_duplicate_template(self):
        """Duplicate this template."""
        self.ensure_one()
        new_template = self.copy({'name': '%s (Copy)' % self.name})
        return {
            'name': _('Journal Template'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.journal.template',
            'res_id': new_template.id,
            'view_mode': 'form',
        }


class OpsJournalTemplateLine(models.Model):
    _name = 'ops.journal.template.line'
    _description = 'Journal Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'ops.journal.template',
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
    analytic_distribution = fields.Json(string='Analytic')

    # Amount can be fixed or percentage
    amount_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ], string='Amount Type', default='fixed')

    percentage = fields.Float(string='Percentage', help='Used when amount_type is percentage')

    is_debit = fields.Boolean(
        string='Is Debit',
        default=True,
        help='For percentage lines: if True, amount goes to debit; if False, to credit'
    )

    @api.constrains('debit', 'credit', 'amount_type')
    def _check_amounts(self):
        for line in self:
            if line.amount_type == 'fixed':
                if line.debit < 0 or line.credit < 0:
                    raise ValidationError(_('Debit and credit must be positive.'))
                if line.debit > 0 and line.credit > 0:
                    raise ValidationError(_('A line cannot have both debit and credit.'))

    @api.constrains('percentage')
    def _check_percentage(self):
        for line in self:
            if line.amount_type == 'percentage' and line.percentage <= 0:
                raise ValidationError(_('Percentage must be greater than zero.'))


class OpsJournalTemplateWizard(models.TransientModel):
    """Wizard to create JE from template with date selection."""
    _name = 'ops.journal.template.wizard'
    _description = 'Create Entry from Template'

    template_id = fields.Many2one('ops.journal.template', required=True)

    date = fields.Date(
        string='Entry Date',
        required=True,
        default=fields.Date.today
    )

    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    ref = fields.Char(string='Reference')

    ops_branch_id = fields.Many2one('ops.branch', string='Branch')
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')

    # Amount multiplier for percentage-based templates
    base_amount = fields.Monetary(
        string='Base Amount',
        help='Used to calculate percentage-based lines'
    )
    currency_id = fields.Many2one(
        related='template_id.company_id.currency_id'
    )

    auto_post = fields.Boolean(string='Post Immediately', default=False)

    # Show base amount field only if template has percentage lines
    has_percentage_lines = fields.Boolean(
        compute='_compute_has_percentage_lines'
    )

    @api.depends('template_id')
    def _compute_has_percentage_lines(self):
        for wizard in self:
            wizard.has_percentage_lines = bool(
                wizard.template_id and
                wizard.template_id.line_ids.filtered(lambda l: l.amount_type == 'percentage')
            )

    def action_create_entry(self):
        """Create the journal entry."""
        self.ensure_one()

        template = self.template_id

        # Check if base amount is needed
        percentage_lines = template.line_ids.filtered(lambda l: l.amount_type == 'percentage')
        if percentage_lines and not self.base_amount:
            raise UserError(_('Base amount is required for percentage-based templates.'))

        # Build lines
        move_lines = []
        for tpl_line in template.line_ids:
            if tpl_line.amount_type == 'percentage' and self.base_amount:
                amount = self.base_amount * (tpl_line.percentage / 100)
                if tpl_line.is_debit:
                    debit, credit = amount, 0
                else:
                    debit, credit = 0, amount
            else:
                debit, credit = tpl_line.debit, tpl_line.credit

            move_lines.append((0, 0, {
                'account_id': tpl_line.account_id.id,
                'name': tpl_line.name or template.name,
                'debit': debit,
                'credit': credit,
                'partner_id': tpl_line.partner_id.id if tpl_line.partner_id else False,
                'analytic_distribution': tpl_line.analytic_distribution,
            }))

        move_vals = {
            'date': self.date,
            'journal_id': self.journal_id.id,
            'ref': self.ref or 'Template: %s' % template.name,
            'line_ids': move_lines,
        }

        # Add OPS Matrix fields if they exist on account.move
        if hasattr(self.env['account.move'], 'ops_branch_id'):
            move_vals['ops_branch_id'] = self.ops_branch_id.id if self.ops_branch_id else False
        if hasattr(self.env['account.move'], 'ops_business_unit_id'):
            move_vals['ops_business_unit_id'] = self.ops_business_unit_id.id if self.ops_business_unit_id else False

        move = self.env['account.move'].create(move_vals)

        # Update template usage
        template.write({
            'use_count': template.use_count + 1,
            'last_used': fields.Datetime.now(),
        })

        if self.auto_post:
            move.action_post()

        # Open created entry
        return {
            'name': _('Journal Entry'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }
