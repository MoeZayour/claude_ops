# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class OpsPDCReceivable(models.Model):
    _name = 'ops.pdc.receivable'
    _description = 'Post-Dated Check Receivable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'maturity_date desc, id desc'

    # ==================================================================
    # BASIC FIELDS
    # ==================================================================
    name = fields.Char(
        'Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Customer',
        required=True,
        tracking=True,
        index=True
    )
    amount = fields.Monetary('Amount', required=True, tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        default=lambda self: self.env.company.currency_id
    )

    check_number = fields.Char('Check Number', required=True, tracking=True)
    check_date = fields.Date('Check Date', default=fields.Date.today)
    maturity_date = fields.Date('Maturity Date', required=True, tracking=True, index=True)

    bank_id = fields.Many2one('res.bank', 'Customer Bank')
    ops_branch_id = fields.Many2one(
        'ops.branch',
        'Branch',
        tracking=True,
        index=True,
        help="Operational branch for this PDC"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        'Business Unit',
        tracking=True,
        index=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('deposited', 'Deposited'),
        ('cleared', 'Cleared'),
        ('bounced', 'Bounced'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status', index=True)

    deposit_date = fields.Date('Deposit Date')
    clearance_date = fields.Date('Clearance Date')
    bounce_date = fields.Date('Bounce Date')

    notes = fields.Text('Notes')

    # ==================================================================
    # JOURNAL ENTRY FIELDS
    # ==================================================================
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain="[('type', '=', 'general')]",
        check_company=True,
        tracking=True,
        help="Journal for PDC transactions. Defaults to company PDC journal."
    )
    pdc_account_id = fields.Many2one(
        'account.account',
        string='PDC Clearing Account',
        check_company=True,
        tracking=True,
        help="PDC clearing account. Defaults to company PDC receivable account."
    )
    deposit_bank_journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        domain="[('type', '=', 'bank')]",
        check_company=True,
        tracking=True,
        help="Bank journal for clearance entry."
    )
    deposit_move_id = fields.Many2one(
        'account.move',
        string='Deposit Entry',
        readonly=True,
        copy=False,
        help="Journal entry created on deposit."
    )
    clearance_move_id = fields.Many2one(
        'account.move',
        string='Clearance Entry',
        readonly=True,
        copy=False,
        help="Journal entry created on clearance."
    )
    bounce_move_id = fields.Many2one(
        'account.move',
        string='Bounce Entry',
        readonly=True,
        copy=False,
        help="Reversal entry created on bounce."
    )

    # ==================================================================
    # COMPUTED FIELDS
    # ==================================================================
    receivable_account_id = fields.Many2one(
        'account.account',
        string='Receivable Account',
        compute='_compute_receivable_account',
        store=False,
        help="Customer's receivable account from partner."
    )

    @api.depends('partner_id', 'company_id')
    def _compute_receivable_account(self):
        for rec in self:
            if rec.partner_id:
                rec.receivable_account_id = rec.partner_id.property_account_receivable_id
            else:
                rec.receivable_account_id = False

    # ==================================================================
    # ONCHANGE
    # ==================================================================
    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Set default PDC account and journal from company settings."""
        if self.company_id:
            if not self.journal_id:
                self.journal_id = self.company_id.pdc_journal_id
            if not self.pdc_account_id:
                self.pdc_account_id = self.company_id.pdc_receivable_account_id

    # ==================================================================
    # CRUD
    # ==================================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.pdc.receivable') or _('New')
            # Set defaults from company
            if 'company_id' in vals:
                company = self.env['res.company'].browse(vals['company_id'])
            else:
                company = self.env.company
            if not vals.get('journal_id'):
                vals['journal_id'] = company.pdc_journal_id.id if company.pdc_journal_id else False
            if not vals.get('pdc_account_id'):
                vals['pdc_account_id'] = company.pdc_receivable_account_id.id if company.pdc_receivable_account_id else False
        return super(OpsPDCReceivable, self).create(vals_list)

    # ==================================================================
    # CONSTRAINTS
    # ==================================================================
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Amount must be positive'))

    @api.constrains('maturity_date', 'check_date')
    def _check_dates(self):
        for record in self:
            if record.maturity_date and record.check_date and record.maturity_date < record.check_date:
                raise ValidationError(_('Maturity date must be after check date'))

    # ==================================================================
    # HELPER: CREATE JOURNAL ENTRY
    # ==================================================================
    def _create_pdc_journal_entry(self, journal, date, lines, ref=None, auto_post=True):
        """
        Create a journal entry for PDC operations.

        Args:
            journal: account.journal record
            date: Entry date
            lines: List of dicts with keys: account_id, debit, credit, partner_id, name
            ref: Reference string
            auto_post: Whether to post immediately

        Returns:
            account.move record
        """
        self.ensure_one()

        move_vals = {
            'date': date,
            'journal_id': journal.id,
            'ref': ref or f"{self.name} - {self.check_number}",
            'company_id': self.company_id.id,
            'line_ids': [(0, 0, line) for line in lines],
        }

        # Add OPS dimensions if available
        if self.ops_branch_id:
            move_vals['ops_branch_id'] = self.ops_branch_id.id
        if self.ops_business_unit_id:
            move_vals['ops_business_unit_id'] = self.ops_business_unit_id.id

        move = self.env['account.move'].create(move_vals)

        if auto_post:
            move.action_post()

        return move

    def _validate_pdc_config(self):
        """Validate that PDC configuration is complete."""
        self.ensure_one()
        errors = []

        if not self.journal_id and not self.company_id.pdc_journal_id:
            errors.append(_("PDC Journal is not configured."))

        if not self.pdc_account_id and not self.company_id.pdc_receivable_account_id:
            errors.append(_("PDC Receivable Account is not configured."))

        if not self.partner_id.property_account_receivable_id:
            errors.append(_("Customer has no receivable account configured."))

        if errors:
            raise UserError(_("PDC Configuration Error:\n%s\n\nPlease configure in Settings > Accounting > PDC Settings.") % '\n'.join(errors))

    # ==================================================================
    # ACTION METHODS
    # ==================================================================
    def action_deposit(self):
        """
        Deposit the PDC - Create journal entry:
        Dr: PDC Clearing Account
        Cr: Accounts Receivable
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft PDCs can be deposited."))

            rec._validate_pdc_config()

            # Get accounts
            journal = rec.journal_id or rec.company_id.pdc_journal_id
            pdc_account = rec.pdc_account_id or rec.company_id.pdc_receivable_account_id
            receivable_account = rec.partner_id.property_account_receivable_id

            deposit_date = fields.Date.today()

            # Create journal entry lines
            lines = [
                {
                    'account_id': pdc_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Deposit: %s") % rec.check_number,
                    'debit': rec.amount,
                    'credit': 0.0,
                },
                {
                    'account_id': receivable_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Deposit: %s") % rec.check_number,
                    'debit': 0.0,
                    'credit': rec.amount,
                },
            ]

            # Create and post the journal entry
            move = rec._create_pdc_journal_entry(
                journal=journal,
                date=deposit_date,
                lines=lines,
                ref=_("PDC Deposit: %s - %s") % (rec.name, rec.check_number),
            )

            # Update PDC record
            rec.write({
                'state': 'deposited',
                'deposit_date': deposit_date,
                'deposit_move_id': move.id,
            })

            # Post message to chatter
            rec.message_post(
                body=_("PDC deposited. Journal Entry: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>") % (move.id, move.name),
                subject=_("PDC Deposited"),
            )

            _logger.info("PDC %s deposited with JE %s", rec.name, move.name)

    def action_clear(self):
        """
        Clear the PDC - Create journal entry:
        Dr: Bank Account
        Cr: PDC Clearing Account
        """
        for rec in self:
            if rec.state != 'deposited':
                raise UserError(_("Only deposited PDCs can be cleared."))

            if not rec.deposit_bank_journal_id:
                raise UserError(_("Please select a Bank Journal for clearance."))

            # Get accounts
            bank_journal = rec.deposit_bank_journal_id
            bank_account = bank_journal.default_account_id
            if not bank_account:
                raise UserError(_("Bank journal '%s' has no default account configured.") % bank_journal.name)

            pdc_account = rec.pdc_account_id or rec.company_id.pdc_receivable_account_id
            journal = rec.journal_id or rec.company_id.pdc_journal_id

            clearance_date = fields.Date.today()

            # Create journal entry lines
            lines = [
                {
                    'account_id': bank_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Clearance: %s") % rec.check_number,
                    'debit': rec.amount,
                    'credit': 0.0,
                },
                {
                    'account_id': pdc_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Clearance: %s") % rec.check_number,
                    'debit': 0.0,
                    'credit': rec.amount,
                },
            ]

            # Create and post the journal entry
            move = rec._create_pdc_journal_entry(
                journal=journal,
                date=clearance_date,
                lines=lines,
                ref=_("PDC Clearance: %s - %s") % (rec.name, rec.check_number),
            )

            # Update PDC record
            rec.write({
                'state': 'cleared',
                'clearance_date': clearance_date,
                'clearance_move_id': move.id,
            })

            # Post message to chatter
            rec.message_post(
                body=_("PDC cleared. Journal Entry: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>") % (move.id, move.name),
                subject=_("PDC Cleared"),
            )

            _logger.info("PDC %s cleared with JE %s", rec.name, move.name)

    def action_bounce(self):
        """
        Bounce the PDC - Reverse the deposit entry:
        Dr: Accounts Receivable
        Cr: PDC Clearing Account
        """
        for rec in self:
            if rec.state != 'deposited':
                raise UserError(_("Only deposited PDCs can be bounced."))

            if not rec.deposit_move_id:
                raise UserError(_("No deposit entry found to reverse."))

            # Get accounts (reverse of deposit)
            journal = rec.journal_id or rec.company_id.pdc_journal_id
            pdc_account = rec.pdc_account_id or rec.company_id.pdc_receivable_account_id
            receivable_account = rec.partner_id.property_account_receivable_id

            bounce_date = fields.Date.today()

            # Create reversal lines (opposite of deposit)
            lines = [
                {
                    'account_id': receivable_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Bounce Reversal: %s") % rec.check_number,
                    'debit': rec.amount,
                    'credit': 0.0,
                },
                {
                    'account_id': pdc_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Bounce Reversal: %s") % rec.check_number,
                    'debit': 0.0,
                    'credit': rec.amount,
                },
            ]

            # Create and post the reversal entry
            move = rec._create_pdc_journal_entry(
                journal=journal,
                date=bounce_date,
                lines=lines,
                ref=_("PDC Bounce (Reversal): %s - %s") % (rec.name, rec.check_number),
            )

            # Update PDC record
            rec.write({
                'state': 'bounced',
                'bounce_date': bounce_date,
                'bounce_move_id': move.id,
            })

            # Post message to chatter
            rec.message_post(
                body=_("PDC bounced! Reversal Entry: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>") % (move.id, move.name),
                subject=_("PDC Bounced"),
                message_type='notification',
            )

            _logger.warning("PDC %s bounced with reversal JE %s", rec.name, move.name)

    def action_cancel(self):
        """Cancel a PDC - only allowed for draft state."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft PDCs can be cancelled. For deposited PDCs, use the Bounce action."))
            rec.write({'state': 'cancelled'})
            rec.message_post(body=_("PDC cancelled."), subject=_("PDC Cancelled"))

    def action_reset_to_draft(self):
        """Reset cancelled PDC to draft."""
        for rec in self:
            if rec.state != 'cancelled':
                raise UserError(_("Only cancelled PDCs can be reset to draft."))
            rec.write({'state': 'draft'})
            rec.message_post(body=_("PDC reset to draft."), subject=_("PDC Reset"))


class OpsPDCPayable(models.Model):
    _name = 'ops.pdc.payable'
    _description = 'Post-Dated Check Payable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'maturity_date desc, id desc'

    # ==================================================================
    # BASIC FIELDS
    # ==================================================================
    name = fields.Char(
        'Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Vendor',
        required=True,
        tracking=True,
        index=True
    )
    amount = fields.Monetary('Amount', required=True, tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        default=lambda self: self.env.company.currency_id
    )

    check_number = fields.Char('Check Number', required=True, tracking=True)
    check_date = fields.Date('Check Date', default=fields.Date.today)
    maturity_date = fields.Date('Maturity Date', required=True, tracking=True, index=True)

    bank_id = fields.Many2one('res.bank', 'Our Bank')
    bank_journal_id = fields.Many2one(
        'account.journal',
        string='Bank Account',
        domain="[('type', '=', 'bank')]",
        check_company=True,
        tracking=True,
        help="Bank account from which the check is drawn."
    )
    ops_branch_id = fields.Many2one(
        'ops.branch',
        'Branch',
        tracking=True,
        index=True,
        help="Operational branch for this PDC"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        'Business Unit',
        tracking=True,
        index=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('presented', 'Presented'),
        ('cleared', 'Cleared'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status', index=True)

    issue_date = fields.Date('Issue Date')
    present_date = fields.Date('Present Date')
    clearance_date = fields.Date('Clearance Date')

    notes = fields.Text('Notes')

    # ==================================================================
    # JOURNAL ENTRY FIELDS
    # ==================================================================
    journal_id = fields.Many2one(
        'account.journal',
        string='PDC Journal',
        domain="[('type', '=', 'general')]",
        check_company=True,
        tracking=True,
        help="Journal for PDC transactions. Defaults to company PDC journal."
    )
    pdc_account_id = fields.Many2one(
        'account.account',
        string='PDC Clearing Account',
        check_company=True,
        tracking=True,
        help="PDC clearing account. Defaults to company PDC payable account."
    )
    issue_move_id = fields.Many2one(
        'account.move',
        string='Issue Entry',
        readonly=True,
        copy=False,
        help="Journal entry created on issue."
    )
    clearance_move_id = fields.Many2one(
        'account.move',
        string='Clearance Entry',
        readonly=True,
        copy=False,
        help="Journal entry created on clearance."
    )
    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancellation Entry',
        readonly=True,
        copy=False,
        help="Reversal entry created on cancellation."
    )

    # ==================================================================
    # COMPUTED FIELDS
    # ==================================================================
    payable_account_id = fields.Many2one(
        'account.account',
        string='Payable Account',
        compute='_compute_payable_account',
        store=False,
        help="Vendor's payable account from partner."
    )

    @api.depends('partner_id', 'company_id')
    def _compute_payable_account(self):
        for rec in self:
            if rec.partner_id:
                rec.payable_account_id = rec.partner_id.property_account_payable_id
            else:
                rec.payable_account_id = False

    # ==================================================================
    # ONCHANGE
    # ==================================================================
    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Set default PDC account and journal from company settings."""
        if self.company_id:
            if not self.journal_id:
                self.journal_id = self.company_id.pdc_journal_id
            if not self.pdc_account_id:
                self.pdc_account_id = self.company_id.pdc_payable_account_id

    # ==================================================================
    # CRUD
    # ==================================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.pdc.payable') or _('New')
            # Set defaults from company
            if 'company_id' in vals:
                company = self.env['res.company'].browse(vals['company_id'])
            else:
                company = self.env.company
            if not vals.get('journal_id'):
                vals['journal_id'] = company.pdc_journal_id.id if company.pdc_journal_id else False
            if not vals.get('pdc_account_id'):
                vals['pdc_account_id'] = company.pdc_payable_account_id.id if company.pdc_payable_account_id else False
        return super(OpsPDCPayable, self).create(vals_list)

    # ==================================================================
    # CONSTRAINTS
    # ==================================================================
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Amount must be positive'))

    # ==================================================================
    # HELPER: CREATE JOURNAL ENTRY
    # ==================================================================
    def _create_pdc_journal_entry(self, journal, date, lines, ref=None, auto_post=True):
        """
        Create a journal entry for PDC operations.

        Args:
            journal: account.journal record
            date: Entry date
            lines: List of dicts with keys: account_id, debit, credit, partner_id, name
            ref: Reference string
            auto_post: Whether to post immediately

        Returns:
            account.move record
        """
        self.ensure_one()

        move_vals = {
            'date': date,
            'journal_id': journal.id,
            'ref': ref or f"{self.name} - {self.check_number}",
            'company_id': self.company_id.id,
            'line_ids': [(0, 0, line) for line in lines],
        }

        # Add OPS dimensions if available
        if self.ops_branch_id:
            move_vals['ops_branch_id'] = self.ops_branch_id.id
        if self.ops_business_unit_id:
            move_vals['ops_business_unit_id'] = self.ops_business_unit_id.id

        move = self.env['account.move'].create(move_vals)

        if auto_post:
            move.action_post()

        return move

    def _validate_pdc_config(self):
        """Validate that PDC configuration is complete."""
        self.ensure_one()
        errors = []

        if not self.journal_id and not self.company_id.pdc_journal_id:
            errors.append(_("PDC Journal is not configured."))

        if not self.pdc_account_id and not self.company_id.pdc_payable_account_id:
            errors.append(_("PDC Payable Account is not configured."))

        if not self.partner_id.property_account_payable_id:
            errors.append(_("Vendor has no payable account configured."))

        if errors:
            raise UserError(_("PDC Configuration Error:\n%s\n\nPlease configure in Settings > Accounting > PDC Settings.") % '\n'.join(errors))

    # ==================================================================
    # ACTION METHODS
    # ==================================================================
    def action_issue(self):
        """
        Issue the PDC - Create journal entry:
        Dr: Accounts Payable
        Cr: PDC Clearing Account
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft PDCs can be issued."))

            rec._validate_pdc_config()

            # Get accounts
            journal = rec.journal_id or rec.company_id.pdc_journal_id
            pdc_account = rec.pdc_account_id or rec.company_id.pdc_payable_account_id
            payable_account = rec.partner_id.property_account_payable_id

            issue_date = fields.Date.today()

            # Create journal entry lines
            lines = [
                {
                    'account_id': payable_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Issue: %s") % rec.check_number,
                    'debit': rec.amount,
                    'credit': 0.0,
                },
                {
                    'account_id': pdc_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Issue: %s") % rec.check_number,
                    'debit': 0.0,
                    'credit': rec.amount,
                },
            ]

            # Create and post the journal entry
            move = rec._create_pdc_journal_entry(
                journal=journal,
                date=issue_date,
                lines=lines,
                ref=_("PDC Issue: %s - %s") % (rec.name, rec.check_number),
            )

            # Update PDC record
            rec.write({
                'state': 'issued',
                'issue_date': issue_date,
                'issue_move_id': move.id,
            })

            # Post message to chatter
            rec.message_post(
                body=_("PDC issued. Journal Entry: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>") % (move.id, move.name),
                subject=_("PDC Issued"),
            )

            _logger.info("PDC Payable %s issued with JE %s", rec.name, move.name)

    def action_present(self):
        """Mark PDC as presented to bank (status only, no JE)."""
        for rec in self:
            if rec.state != 'issued':
                raise UserError(_("Only issued PDCs can be presented."))
            rec.write({
                'state': 'presented',
                'present_date': fields.Date.today(),
            })
            rec.message_post(body=_("PDC presented to bank."), subject=_("PDC Presented"))

    def action_clear(self):
        """
        Clear the PDC - Create journal entry:
        Dr: PDC Clearing Account
        Cr: Bank Account
        """
        for rec in self:
            if rec.state not in ('issued', 'presented'):
                raise UserError(_("Only issued or presented PDCs can be cleared."))

            if not rec.bank_journal_id:
                raise UserError(_("Please select a Bank Account for clearance."))

            # Get accounts
            bank_journal = rec.bank_journal_id
            bank_account = bank_journal.default_account_id
            if not bank_account:
                raise UserError(_("Bank journal '%s' has no default account configured.") % bank_journal.name)

            pdc_account = rec.pdc_account_id or rec.company_id.pdc_payable_account_id
            journal = rec.journal_id or rec.company_id.pdc_journal_id

            clearance_date = fields.Date.today()

            # Create journal entry lines
            lines = [
                {
                    'account_id': pdc_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Clearance: %s") % rec.check_number,
                    'debit': rec.amount,
                    'credit': 0.0,
                },
                {
                    'account_id': bank_account.id,
                    'partner_id': rec.partner_id.id,
                    'name': _("PDC Clearance: %s") % rec.check_number,
                    'debit': 0.0,
                    'credit': rec.amount,
                },
            ]

            # Create and post the journal entry
            move = rec._create_pdc_journal_entry(
                journal=journal,
                date=clearance_date,
                lines=lines,
                ref=_("PDC Clearance: %s - %s") % (rec.name, rec.check_number),
            )

            # Update PDC record
            rec.write({
                'state': 'cleared',
                'clearance_date': clearance_date,
                'clearance_move_id': move.id,
            })

            # Post message to chatter
            rec.message_post(
                body=_("PDC cleared. Journal Entry: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>") % (move.id, move.name),
                subject=_("PDC Cleared"),
            )

            _logger.info("PDC Payable %s cleared with JE %s", rec.name, move.name)

    def action_cancel(self):
        """
        Cancel the PDC - Reverse the issue entry if issued.
        """
        for rec in self:
            if rec.state == 'cleared':
                raise UserError(_("Cleared PDCs cannot be cancelled."))

            cancel_date = fields.Date.today()

            # If issued, create reversal entry
            if rec.state in ('issued', 'presented') and rec.issue_move_id:
                # Get accounts (reverse of issue)
                journal = rec.journal_id or rec.company_id.pdc_journal_id
                pdc_account = rec.pdc_account_id or rec.company_id.pdc_payable_account_id
                payable_account = rec.partner_id.property_account_payable_id

                # Create reversal lines (opposite of issue)
                lines = [
                    {
                        'account_id': pdc_account.id,
                        'partner_id': rec.partner_id.id,
                        'name': _("PDC Cancel Reversal: %s") % rec.check_number,
                        'debit': rec.amount,
                        'credit': 0.0,
                    },
                    {
                        'account_id': payable_account.id,
                        'partner_id': rec.partner_id.id,
                        'name': _("PDC Cancel Reversal: %s") % rec.check_number,
                        'debit': 0.0,
                        'credit': rec.amount,
                    },
                ]

                # Create and post the reversal entry
                move = rec._create_pdc_journal_entry(
                    journal=journal,
                    date=cancel_date,
                    lines=lines,
                    ref=_("PDC Cancel (Reversal): %s - %s") % (rec.name, rec.check_number),
                )

                rec.write({
                    'state': 'cancelled',
                    'cancel_move_id': move.id,
                })

                rec.message_post(
                    body=_("PDC cancelled. Reversal Entry: <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a>") % (move.id, move.name),
                    subject=_("PDC Cancelled"),
                )

                _logger.info("PDC Payable %s cancelled with reversal JE %s", rec.name, move.name)
            else:
                # Draft PDC - just cancel
                rec.write({'state': 'cancelled'})
                rec.message_post(body=_("PDC cancelled."), subject=_("PDC Cancelled"))

    def action_reset_to_draft(self):
        """Reset cancelled PDC to draft."""
        for rec in self:
            if rec.state != 'cancelled':
                raise UserError(_("Only cancelled PDCs can be reset to draft."))
            rec.write({'state': 'draft'})
            rec.message_post(body=_("PDC reset to draft."), subject=_("PDC Reset"))
