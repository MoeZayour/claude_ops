# Claude Code Prompt - Phase 5: Advanced Features (Full Phase)

```
/ops-accounting phase5

Start Session 5: Advanced Features - All Tasks

Context:
- Repository: /opt/gemini_odoo19/addons/ops_matrix_accounting/
- Reference: claude_files/OPS_ACCOUNTING_TODO.md
- Phase 1 ✅ COMPLETE (Critical Fixes)
- Phase 2 ✅ COMPLETE (Core Accounting)
- Phase 3 ✅ COMPLETE (Recurring & Automation)
- Phase 4 ✅ COMPLETE (Financial Reports)

Phase 5 Scope (LOW Priority - Future Enhancements):
- Task 5.1: Inter-Branch Transfer Accounting
- Task 5.2: Bank Reconciliation Module
- Task 5.3: IFRS 16 Lease Accounting
- Task 5.4: Asset Impairment
- Task 5.5: FX Revaluation

================================================================================
TASK 5.1: INTER-BRANCH TRANSFER ACCOUNTING
================================================================================

Purpose:
- Track inventory/asset transfers between branches
- Auto-create mirror journal entries in receiving branch
- Use transit accounts for in-flight transfers
- Reconciliation workflow

1. Create models/ops_interbranch_transfer.py:

```python
# -*- coding: utf-8 -*-
"""
OPS Inter-Branch Transfer Accounting
Handles transfers of inventory, assets, or funds between branches
with automatic mirror journal entry creation.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsInterbranchTransfer(models.Model):
    """Inter-Branch Transfer Document."""
    _name = 'ops.interbranch.transfer'
    _description = 'Inter-Branch Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.company
    )
    
    transfer_type = fields.Selection([
        ('inventory', 'Inventory Transfer'),
        ('asset', 'Asset Transfer'),
        ('funds', 'Funds Transfer'),
        ('expense', 'Expense Allocation'),
    ], string='Transfer Type', required=True, default='inventory', tracking=True)
    
    date = fields.Date(
        string='Transfer Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    source_branch_id = fields.Many2one(
        'ops.branch', string='Source Branch',
        required=True, tracking=True,
        domain="[('company_id', '=', company_id)]"
    )
    
    dest_branch_id = fields.Many2one(
        'ops.branch', string='Destination Branch',
        required=True, tracking=True,
        domain="[('company_id', '=', company_id), ('id', '!=', source_branch_id)]"
    )
    
    currency_id = fields.Many2one(related='company_id.currency_id')
    amount = fields.Monetary(string='Transfer Amount', required=True, tracking=True)
    
    transit_account_id = fields.Many2one(
        'account.account', string='Transit Account', required=True,
        domain="[('company_id', '=', company_id)]"
    )
    
    source_account_id = fields.Many2one(
        'account.account', string='Source Account', required=True,
        domain="[('company_id', '=', company_id)]"
    )
    
    dest_account_id = fields.Many2one(
        'account.account', string='Destination Account', required=True,
        domain="[('company_id', '=', company_id)]"
    )
    
    journal_id = fields.Many2one(
        'account.journal', string='Journal', required=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]"
    )
    
    inventory_transfer_id = fields.Many2one('stock.picking', string='Inventory Transfer')
    asset_id = fields.Many2one('ops.asset', string='Asset')
    
    source_move_id = fields.Many2one('account.move', string='Source Entry', readonly=True, copy=False)
    dest_move_id = fields.Many2one('account.move', string='Destination Entry', readonly=True, copy=False)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Receipt'),
        ('received', 'Received'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)
    
    sent_by = fields.Many2one('res.users', string='Sent By', readonly=True)
    sent_date = fields.Datetime(string='Sent Date', readonly=True)
    received_by = fields.Many2one('res.users', string='Received By', readonly=True)
    received_date = fields.Datetime(string='Received Date', readonly=True)
    description = fields.Text(string='Description')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.interbranch.transfer') or _('New')
        return super().create(vals_list)
    
    @api.constrains('source_branch_id', 'dest_branch_id')
    def _check_branches(self):
        for transfer in self:
            if transfer.source_branch_id == transfer.dest_branch_id:
                raise ValidationError(_('Source and destination branches must be different.'))
    
    @api.constrains('amount')
    def _check_amount(self):
        for transfer in self:
            if transfer.amount <= 0:
                raise ValidationError(_('Transfer amount must be positive.'))
    
    def action_send(self):
        """Send the transfer - creates source branch journal entry."""
        for transfer in self:
            if transfer.state != 'draft':
                raise UserError(_('Can only send draft transfers.'))
            
            move_vals = {
                'date': transfer.date,
                'journal_id': transfer.journal_id.id,
                'ref': f'IBT Send: {transfer.name}',
                'ops_branch_id': transfer.source_branch_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': transfer.transit_account_id.id,
                        'name': f'Inter-branch transfer to {transfer.dest_branch_id.name}',
                        'debit': transfer.amount,
                        'credit': 0,
                        'ops_branch_id': transfer.source_branch_id.id,
                    }),
                    (0, 0, {
                        'account_id': transfer.source_account_id.id,
                        'name': f'Inter-branch transfer to {transfer.dest_branch_id.name}',
                        'debit': 0,
                        'credit': transfer.amount,
                        'ops_branch_id': transfer.source_branch_id.id,
                    }),
                ],
            }
            
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            transfer.write({
                'source_move_id': move.id,
                'state': 'pending',
                'sent_by': self.env.uid,
                'sent_date': fields.Datetime.now(),
            })
            
            transfer.message_post(body=_(
                'Transfer sent to %s. Amount: %s'
            ) % (transfer.dest_branch_id.name, transfer.amount))
    
    def action_receive(self):
        """Receive the transfer - creates destination branch journal entry."""
        for transfer in self:
            if transfer.state != 'pending':
                raise UserError(_('Can only receive pending transfers.'))
            
            move_vals = {
                'date': fields.Date.today(),
                'journal_id': transfer.journal_id.id,
                'ref': f'IBT Receive: {transfer.name}',
                'ops_branch_id': transfer.dest_branch_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': transfer.dest_account_id.id,
                        'name': f'Inter-branch transfer from {transfer.source_branch_id.name}',
                        'debit': transfer.amount,
                        'credit': 0,
                        'ops_branch_id': transfer.dest_branch_id.id,
                    }),
                    (0, 0, {
                        'account_id': transfer.transit_account_id.id,
                        'name': f'Inter-branch transfer from {transfer.source_branch_id.name}',
                        'debit': 0,
                        'credit': transfer.amount,
                        'ops_branch_id': transfer.dest_branch_id.id,
                    }),
                ],
            }
            
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            transfer.write({
                'dest_move_id': move.id,
                'state': 'received',
                'received_by': self.env.uid,
                'received_date': fields.Datetime.now(),
            })
            
            transfer.message_post(body=_(
                'Transfer received from %s. Amount: %s'
            ) % (transfer.source_branch_id.name, transfer.amount))
    
    def action_reconcile(self):
        """Mark transfer as reconciled after verification."""
        for transfer in self:
            if transfer.state != 'received':
                raise UserError(_('Can only reconcile received transfers.'))
            
            if not transfer.source_move_id or not transfer.dest_move_id:
                raise UserError(_('Both journal entries must exist.'))
            
            if transfer.source_move_id.state != 'posted' or transfer.dest_move_id.state != 'posted':
                raise UserError(_('Both journal entries must be posted.'))
            
            transfer.write({'state': 'reconciled'})
            transfer.message_post(body=_('Transfer reconciled.'))
    
    def action_cancel(self):
        """Cancel the transfer and reverse entries if needed."""
        for transfer in self:
            if transfer.state == 'reconciled':
                raise UserError(_('Cannot cancel reconciled transfers.'))
            
            if transfer.dest_move_id and transfer.dest_move_id.state == 'posted':
                transfer.dest_move_id.button_draft()
                transfer.dest_move_id.button_cancel()
            
            if transfer.source_move_id and transfer.source_move_id.state == 'posted':
                transfer.source_move_id.button_draft()
                transfer.source_move_id.button_cancel()
            
            transfer.write({'state': 'cancelled'})
            transfer.message_post(body=_('Transfer cancelled.'))
    
    def action_view_journal_entries(self):
        """View related journal entries."""
        self.ensure_one()
        move_ids = []
        if self.source_move_id:
            move_ids.append(self.source_move_id.id)
        if self.dest_move_id:
            move_ids.append(self.dest_move_id.id)
        
        return {
            'name': _('Journal Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', move_ids)],
        }


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    interbranch_transit_account_id = fields.Many2one(
        'account.account', string='Inter-Branch Transit Account',
        domain="[('company_id', '=', id)]"
    )
    
    interbranch_journal_id = fields.Many2one(
        'account.journal', string='Inter-Branch Journal',
        domain="[('company_id', '=', id), ('type', '=', 'general')]"
    )
```

================================================================================
TASK 5.2: BANK RECONCILIATION MODULE
================================================================================

2. Create models/ops_bank_reconciliation.py:

```python
# -*- coding: utf-8 -*-
"""
OPS Bank Reconciliation Module
Basic bank statement import and reconciliation with branch support.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import csv
import io
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsBankReconciliation(models.Model):
    """Bank Reconciliation Session."""
    _name = 'ops.bank.reconciliation'
    _description = 'Bank Reconciliation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                       default=lambda self: _('New'), readonly=True)
    company_id = fields.Many2one('res.company', string='Company',
                                  required=True, default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Bank Journal', required=True,
                                  domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]", tracking=True)
    ops_branch_id = fields.Many2one('ops.branch', string='Branch', tracking=True, index=True)
    date = fields.Date(string='Statement Date', required=True, default=fields.Date.today, tracking=True)
    date_from = fields.Date(string='Period From')
    date_to = fields.Date(string='Period To')
    
    currency_id = fields.Many2one(related='company_id.currency_id')
    balance_start = fields.Monetary(string='Starting Balance', required=True, tracking=True)
    balance_end_statement = fields.Monetary(string='Ending Balance (Statement)', required=True, tracking=True)
    balance_end_computed = fields.Monetary(string='Ending Balance (Computed)', compute='_compute_balance_end')
    balance_difference = fields.Monetary(string='Difference', compute='_compute_balance_end')
    
    line_ids = fields.One2many('ops.bank.reconciliation.line', 'reconciliation_id', string='Statement Lines')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)
    
    total_lines = fields.Integer(compute='_compute_statistics')
    matched_lines = fields.Integer(compute='_compute_statistics')
    unmatched_lines = fields.Integer(compute='_compute_statistics')
    match_percentage = fields.Float(compute='_compute_statistics')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.bank.reconciliation') or _('New')
        return super().create(vals_list)
    
    @api.depends('balance_start', 'line_ids.amount')
    def _compute_balance_end(self):
        for rec in self:
            total = sum(rec.line_ids.mapped('amount'))
            rec.balance_end_computed = rec.balance_start + total
            rec.balance_difference = rec.balance_end_statement - rec.balance_end_computed
    
    @api.depends('line_ids', 'line_ids.match_status')
    def _compute_statistics(self):
        for rec in self:
            total = len(rec.line_ids)
            matched = len(rec.line_ids.filtered(lambda l: l.match_status == 'matched'))
            rec.total_lines = total
            rec.matched_lines = matched
            rec.unmatched_lines = total - matched
            rec.match_percentage = (matched / total * 100) if total else 0
    
    def action_import_statement(self):
        """Open import wizard."""
        self.ensure_one()
        return {
            'name': _('Import Bank Statement'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.bank.statement.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_reconciliation_id': self.id},
        }
    
    def action_auto_match(self):
        """Auto-match statement lines with journal entries."""
        self.ensure_one()
        if self.state not in ('draft', 'processing'):
            raise UserError(_('Can only match draft or processing reconciliations.'))
        
        self.write({'state': 'processing'})
        matched_count = 0
        
        for line in self.line_ids.filtered(lambda l: l.match_status == 'unmatched'):
            match = self._find_match(line)
            if match:
                line.write({'matched_move_line_id': match.id, 'match_status': 'matched'})
                matched_count += 1
        
        self.message_post(body=_('Auto-matching completed. %d lines matched.') % matched_count)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Auto-Match Complete'),
                'message': _('%d of %d lines matched') % (matched_count, len(self.line_ids)),
                'type': 'success',
            }
        }
    
    def _find_match(self, line):
        """Find matching journal entry line for a statement line."""
        domain = [
            ('journal_id', '=', self.journal_id.id),
            ('parent_state', '=', 'posted'),
            ('reconciled', '=', False),
            ('company_id', '=', self.company_id.id),
        ]
        if self.ops_branch_id:
            domain.append(('ops_branch_id', '=', self.ops_branch_id.id))
        
        # Try exact amount and reference
        if line.ref:
            matches = self.env['account.move.line'].search(
                domain + [('balance', '=', line.amount), '|',
                          ('name', 'ilike', line.ref), ('move_id.ref', 'ilike', line.ref)], limit=1)
            if matches:
                return matches
        
        # Try exact amount within date range
        date_domain = domain + [
            ('balance', '=', line.amount),
            ('date', '>=', line.date - timedelta(days=5)),
            ('date', '<=', line.date + timedelta(days=5)),
        ]
        matches = self.env['account.move.line'].search(date_domain, limit=1)
        if matches:
            return matches
        
        # Try with partner
        if line.partner_id:
            partner_domain = domain + [('balance', '=', line.amount), ('partner_id', '=', line.partner_id.id)]
            matches = self.env['account.move.line'].search(partner_domain, limit=1)
            if matches:
                return matches
        
        return False
    
    def action_validate(self):
        """Validate and close the reconciliation."""
        self.ensure_one()
        if abs(self.balance_difference) > 0.01:
            raise UserError(_('Cannot validate - difference of %s exists.') % self.balance_difference)
        
        unmatched = self.line_ids.filtered(lambda l: l.match_status == 'unmatched')
        if unmatched:
            raise UserError(_('Cannot validate - %d lines are still unmatched.') % len(unmatched))
        
        self.write({'state': 'reconciled'})
        self.message_post(body=_('Reconciliation validated.'))
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})


class OpsBankReconciliationLine(models.Model):
    """Bank Statement Line for Reconciliation."""
    _name = 'ops.bank.reconciliation.line'
    _description = 'Bank Reconciliation Line'
    _order = 'date asc, id asc'

    reconciliation_id = fields.Many2one('ops.bank.reconciliation', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True)
    ref = fields.Char(string='Reference')
    name = fields.Char(string='Description')
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one(related='reconciliation_id.currency_id')
    amount = fields.Monetary(string='Amount', required=True)
    
    match_status = fields.Selection([
        ('unmatched', 'Unmatched'),
        ('matched', 'Matched'),
        ('manual', 'Manual'),
    ], string='Match Status', default='unmatched', index=True)
    
    matched_move_line_id = fields.Many2one('account.move.line', string='Matched Entry')
    matched_move_id = fields.Many2one(related='matched_move_line_id.move_id', string='Journal Entry')
    has_difference = fields.Boolean(compute='_compute_difference')
    difference_amount = fields.Monetary(compute='_compute_difference')
    
    @api.depends('amount', 'matched_move_line_id.balance')
    def _compute_difference(self):
        for line in self:
            if line.matched_move_line_id:
                diff = line.amount - line.matched_move_line_id.balance
                line.difference_amount = diff
                line.has_difference = abs(diff) > 0.01
            else:
                line.difference_amount = 0
                line.has_difference = False
    
    def action_unmatch(self):
        self.write({'matched_move_line_id': False, 'match_status': 'unmatched'})


class OpsBankStatementImportWizard(models.TransientModel):
    """Wizard to import bank statement from CSV."""
    _name = 'ops.bank.statement.import.wizard'
    _description = 'Import Bank Statement'
    
    reconciliation_id = fields.Many2one('ops.bank.reconciliation', required=True)
    file_data = fields.Binary(string='Statement File', required=True)
    file_name = fields.Char(string='Filename')
    file_format = fields.Selection([('csv', 'CSV'), ('ofx', 'OFX (future)')], default='csv', required=True)
    date_format = fields.Char(string='Date Format', default='%Y-%m-%d')
    delimiter = fields.Selection([(',', 'Comma'), (';', 'Semicolon'), ('\t', 'Tab')], default=',')
    skip_header = fields.Boolean(string='Skip Header Row', default=True)
    col_date = fields.Integer(string='Date Column', default=0)
    col_ref = fields.Integer(string='Reference Column', default=1)
    col_desc = fields.Integer(string='Description Column', default=2)
    col_amount = fields.Integer(string='Amount Column', default=3)
    col_debit = fields.Integer(string='Debit Column', default=-1)
    col_credit = fields.Integer(string='Credit Column', default=-1)
    
    def action_import(self):
        self.ensure_one()
        if self.file_format != 'csv':
            raise UserError(_('Only CSV format is currently supported.'))
        
        try:
            content = base64.b64decode(self.file_data).decode('utf-8')
        except Exception as e:
            raise UserError(_('Could not read file: %s') % str(e))
        
        reader = csv.reader(io.StringIO(content), delimiter=self.delimiter)
        lines_data = []
        row_num = 0
        
        for row in reader:
            row_num += 1
            if row_num == 1 and self.skip_header:
                continue
            if not row or len(row) < max(self.col_date, self.col_amount) + 1:
                continue
            
            try:
                date_str = row[self.col_date].strip()
                date = datetime.strptime(date_str, self.date_format).date()
                
                if self.col_debit >= 0 and self.col_credit >= 0:
                    debit = float(row[self.col_debit].replace(',', '').strip() or 0)
                    credit = float(row[self.col_credit].replace(',', '').strip() or 0)
                    amount = debit - credit
                else:
                    amount = float(row[self.col_amount].replace(',', '').strip())
                
                ref = row[self.col_ref].strip() if self.col_ref >= 0 and self.col_ref < len(row) else ''
                desc = row[self.col_desc].strip() if self.col_desc >= 0 and self.col_desc < len(row) else ''
                
                lines_data.append({
                    'reconciliation_id': self.reconciliation_id.id,
                    'date': date, 'ref': ref, 'name': desc, 'amount': amount,
                })
            except Exception as e:
                _logger.warning(f"Error parsing row {row_num}: {e}")
                continue
        
        if not lines_data:
            raise UserError(_('No valid lines found in the file.'))
        
        self.env['ops.bank.reconciliation.line'].create(lines_data)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': _('Import Complete'), 'message': _('%d lines imported') % len(lines_data), 'type': 'success'}
        }
```

================================================================================
TASK 5.3: IFRS 16 LEASE ACCOUNTING
================================================================================

3. Create models/ops_lease.py:

```python
# -*- coding: utf-8 -*-
"""OPS IFRS 16 Lease Accounting - Right-of-Use Assets and Lease Liabilities."""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OpsLease(models.Model):
    """IFRS 16 Lease Agreement."""
    _name = 'ops.lease'
    _description = 'Lease Agreement (IFRS 16)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'commencement_date desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False, default=lambda self: _('New'), readonly=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    ops_branch_id = fields.Many2one('ops.branch', string='Branch', required=True, tracking=True, index=True)
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit', tracking=True)
    description = fields.Text(string='Description')
    lessor_id = fields.Many2one('res.partner', string='Lessor', required=True, tracking=True)
    
    lease_type = fields.Selection([
        ('property', 'Property/Building'), ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'), ('other', 'Other'),
    ], string='Lease Type', required=True, default='property')
    
    commencement_date = fields.Date(string='Commencement Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    lease_term_months = fields.Integer(string='Lease Term (Months)', compute='_compute_lease_term', store=True)
    
    currency_id = fields.Many2one(related='company_id.currency_id')
    payment_amount = fields.Monetary(string='Periodic Payment', required=True, tracking=True)
    
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('annually', 'Annually'),
    ], string='Payment Frequency', default='monthly', required=True)
    
    payment_timing = fields.Selection([
        ('beginning', 'Beginning of Period'), ('end', 'End of Period'),
    ], string='Payment Timing', default='end', required=True)
    
    discount_rate = fields.Float(string='Incremental Borrowing Rate (%)', required=True, default=5.0)
    initial_direct_costs = fields.Monetary(string='Initial Direct Costs', default=0.0)
    
    rou_asset_value = fields.Monetary(string='ROU Asset Value', compute='_compute_lease_values', store=True)
    lease_liability = fields.Monetary(string='Lease Liability', compute='_compute_lease_values', store=True)
    current_liability = fields.Monetary(string='Current Portion', compute='_compute_current_liability')
    non_current_liability = fields.Monetary(string='Non-Current Portion', compute='_compute_current_liability')
    
    payment_schedule_ids = fields.One2many('ops.lease.payment.schedule', 'lease_id', string='Payment Schedule')
    depreciation_schedule_ids = fields.One2many('ops.lease.depreciation', 'lease_id', string='Depreciation Schedule')
    initial_recognition_move_id = fields.Many2one('account.move', string='Initial Recognition Entry', readonly=True)
    
    rou_asset_account_id = fields.Many2one('account.account', string='ROU Asset Account', required=True)
    lease_liability_account_id = fields.Many2one('account.account', string='Lease Liability Account', required=True)
    depreciation_expense_account_id = fields.Many2one('account.account', string='Depreciation Expense Account', required=True)
    interest_expense_account_id = fields.Many2one('account.account', string='Interest Expense Account', required=True)
    accumulated_depreciation_account_id = fields.Many2one('account.account', string='Accumulated Depreciation Account', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                  domain="[('company_id', '=', company_id), ('type', '=', 'general')]")
    
    state = fields.Selection([
        ('draft', 'Draft'), ('active', 'Active'), ('terminated', 'Terminated'), ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.lease') or _('New')
        return super().create(vals_list)
    
    @api.depends('commencement_date', 'end_date')
    def _compute_lease_term(self):
        for lease in self:
            if lease.commencement_date and lease.end_date:
                delta = relativedelta(lease.end_date, lease.commencement_date)
                lease.lease_term_months = delta.years * 12 + delta.months
            else:
                lease.lease_term_months = 0
    
    @api.depends('payment_amount', 'payment_frequency', 'lease_term_months', 'discount_rate', 'initial_direct_costs', 'payment_timing')
    def _compute_lease_values(self):
        """Calculate ROU Asset and Lease Liability using present value."""
        for lease in self:
            if not lease.payment_amount or not lease.lease_term_months or not lease.discount_rate:
                lease.rou_asset_value = lease.lease_liability = 0
                continue
            
            if lease.payment_frequency == 'monthly':
                n_payments, rate = lease.lease_term_months, lease.discount_rate / 100 / 12
            elif lease.payment_frequency == 'quarterly':
                n_payments, rate = lease.lease_term_months / 3, lease.discount_rate / 100 / 4
            else:
                n_payments, rate = lease.lease_term_months / 12, lease.discount_rate / 100
            
            if rate <= 0 or n_payments <= 0:
                lease.rou_asset_value = lease.lease_liability = 0
                continue
            
            pv_factor = (1 - (1 + rate) ** -n_payments) / rate
            if lease.payment_timing == 'beginning':
                pv_factor *= (1 + rate)
            
            pv = lease.payment_amount * pv_factor
            lease.lease_liability = round(pv, 2)
            lease.rou_asset_value = round(pv + lease.initial_direct_costs, 2)
    
    @api.depends('lease_liability', 'payment_schedule_ids')
    def _compute_current_liability(self):
        today = fields.Date.today()
        one_year = today + relativedelta(years=1)
        for lease in self:
            if not lease.payment_schedule_ids:
                lease.current_liability = 0
                lease.non_current_liability = lease.lease_liability
                continue
            current_payments = lease.payment_schedule_ids.filtered(lambda p: p.payment_date <= one_year and p.state != 'paid')
            lease.current_liability = sum(current_payments.mapped('principal_amount'))
            lease.non_current_liability = lease.lease_liability - lease.current_liability
    
    def action_generate_schedules(self):
        """Generate payment and depreciation schedules."""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Can only generate schedules for draft leases.'))
        
        self.payment_schedule_ids.unlink()
        self.depreciation_schedule_ids.unlink()
        self._generate_payment_schedule()
        self._generate_depreciation_schedule()
        self.message_post(body=_('Payment and depreciation schedules generated.'))
    
    def _generate_payment_schedule(self):
        """Generate lease payment schedule with interest/principal split."""
        self.ensure_one()
        if self.payment_frequency == 'monthly':
            period_delta, rate = relativedelta(months=1), self.discount_rate / 100 / 12
        elif self.payment_frequency == 'quarterly':
            period_delta, rate = relativedelta(months=3), self.discount_rate / 100 / 4
        else:
            period_delta, rate = relativedelta(years=1), self.discount_rate / 100
        
        current_date = self.commencement_date if self.payment_timing == 'beginning' else self.commencement_date + period_delta
        balance, sequence = self.lease_liability, 1
        
        while current_date <= self.end_date and balance > 0.01:
            interest = balance * rate
            principal = min(self.payment_amount - interest, balance)
            
            self.env['ops.lease.payment.schedule'].create({
                'lease_id': self.id, 'sequence': sequence, 'payment_date': current_date,
                'payment_amount': self.payment_amount, 'interest_amount': round(interest, 2),
                'principal_amount': round(principal, 2), 'balance_after': round(balance - principal, 2),
            })
            balance -= principal
            current_date += period_delta
            sequence += 1
    
    def _generate_depreciation_schedule(self):
        """Generate straight-line depreciation schedule for ROU asset."""
        self.ensure_one()
        monthly_depr = self.rou_asset_value / self.lease_term_months
        current_date = self.commencement_date + relativedelta(months=1)
        sequence, accumulated = 1, 0
        
        while current_date <= self.end_date:
            amount = round(monthly_depr, 2)
            accumulated += amount
            if current_date + relativedelta(months=1) > self.end_date:
                amount = self.rou_asset_value - (accumulated - amount)
            
            self.env['ops.lease.depreciation'].create({
                'lease_id': self.id, 'sequence': sequence, 'depreciation_date': current_date, 'amount': amount,
            })
            current_date += relativedelta(months=1)
            sequence += 1
    
    def action_activate(self):
        """Activate lease and create initial recognition entry."""
        for lease in self:
            if lease.state != 'draft':
                raise UserError(_('Can only activate draft leases.'))
            if not lease.payment_schedule_ids:
                raise UserError(_('Please generate schedules first.'))
            
            move_vals = {
                'date': lease.commencement_date, 'journal_id': lease.journal_id.id,
                'ref': f'Lease Recognition: {lease.name}', 'ops_branch_id': lease.ops_branch_id.id,
                'line_ids': [
                    (0, 0, {'account_id': lease.rou_asset_account_id.id, 'name': f'ROU Asset: {lease.name}',
                            'debit': lease.rou_asset_value, 'credit': 0}),
                    (0, 0, {'account_id': lease.lease_liability_account_id.id, 'name': f'Lease Liability: {lease.name}',
                            'debit': 0, 'credit': lease.lease_liability}),
                ],
            }
            
            if lease.initial_direct_costs:
                move_vals['line_ids'].append((0, 0, {
                    'account_id': lease.company_id.account_default_pos_receivable_account_id.id or lease.rou_asset_account_id.id,
                    'name': f'Initial Direct Costs: {lease.name}', 'debit': 0, 'credit': lease.initial_direct_costs,
                }))
            
            move = lease.env['account.move'].create(move_vals)
            move.action_post()
            lease.write({'initial_recognition_move_id': move.id, 'state': 'active'})
            lease.message_post(body=_('Lease activated. Initial recognition entry: %s') % move.name)


class OpsLeasePaymentSchedule(models.Model):
    """Lease Payment Schedule Line."""
    _name = 'ops.lease.payment.schedule'
    _description = 'Lease Payment Schedule'
    _order = 'sequence, payment_date'

    lease_id = fields.Many2one('ops.lease', required=True, ondelete='cascade')
    sequence = fields.Integer(string='#')
    payment_date = fields.Date(string='Payment Date', required=True)
    currency_id = fields.Many2one(related='lease_id.currency_id')
    payment_amount = fields.Monetary(string='Payment')
    interest_amount = fields.Monetary(string='Interest')
    principal_amount = fields.Monetary(string='Principal')
    balance_after = fields.Monetary(string='Balance After')
    state = fields.Selection([('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    
    def action_record_payment(self):
        """Record the lease payment."""
        for line in self:
            if line.state == 'paid':
                raise UserError(_('Payment already recorded.'))
            
            lease = line.lease_id
            move_vals = {
                'date': line.payment_date, 'journal_id': lease.journal_id.id,
                'ref': f'Lease Payment: {lease.name} #{line.sequence}',
                'ops_branch_id': lease.ops_branch_id.id, 'partner_id': lease.lessor_id.id,
                'line_ids': [
                    (0, 0, {'account_id': lease.lease_liability_account_id.id, 'name': f'Lease Principal: {lease.name}',
                            'debit': line.principal_amount, 'credit': 0, 'partner_id': lease.lessor_id.id}),
                    (0, 0, {'account_id': lease.interest_expense_account_id.id, 'name': f'Lease Interest: {lease.name}',
                            'debit': line.interest_amount, 'credit': 0}),
                    (0, 0, {'account_id': lease.lessor_id.property_account_payable_id.id, 'name': f'Lease Payment: {lease.name}',
                            'debit': 0, 'credit': line.payment_amount, 'partner_id': lease.lessor_id.id}),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            line.write({'state': 'paid', 'move_id': move.id})


class OpsLeaseDepreciation(models.Model):
    """Lease ROU Asset Depreciation Schedule."""
    _name = 'ops.lease.depreciation'
    _description = 'Lease Depreciation'
    _order = 'sequence, depreciation_date'

    lease_id = fields.Many2one('ops.lease', required=True, ondelete='cascade')
    sequence = fields.Integer(string='#')
    depreciation_date = fields.Date(string='Date', required=True)
    currency_id = fields.Many2one(related='lease_id.currency_id')
    amount = fields.Monetary(string='Depreciation Amount')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    
    def action_post(self):
        """Post depreciation entry."""
        for line in self:
            if line.state == 'posted':
                continue
            lease = line.lease_id
            move_vals = {
                'date': line.depreciation_date, 'journal_id': lease.journal_id.id,
                'ref': f'ROU Depreciation: {lease.name} #{line.sequence}', 'ops_branch_id': lease.ops_branch_id.id,
                'line_ids': [
                    (0, 0, {'account_id': lease.depreciation_expense_account_id.id, 'name': f'ROU Depreciation: {lease.name}',
                            'debit': line.amount, 'credit': 0}),
                    (0, 0, {'account_id': lease.accumulated_depreciation_account_id.id, 'name': f'Accumulated Depreciation: {lease.name}',
                            'debit': 0, 'credit': line.amount}),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            line.write({'state': 'posted', 'move_id': move.id})
```

================================================================================
TASK 5.4: ASSET IMPAIRMENT
================================================================================

4. Add to models/ops_asset.py (extend existing):

```python
# -*- coding: utf-8 -*-
# Add to existing OpsAsset class

class OpsAsset(models.Model):
    _inherit = 'ops.asset'
    
    impaired = fields.Boolean(string='Impaired', default=False, tracking=True)
    impairment_date = fields.Date(string='Impairment Date', tracking=True)
    original_value = fields.Monetary(string='Original Value')
    impairment_loss = fields.Monetary(string='Impairment Loss', compute='_compute_impairment', store=True)
    recoverable_amount = fields.Monetary(string='Recoverable Amount')
    impairment_move_id = fields.Many2one('account.move', string='Impairment Entry', readonly=True)
    impairment_loss_account_id = fields.Many2one('account.account', string='Impairment Loss Account',
                                                   domain="[('company_id', '=', company_id)]")
    
    @api.depends('depreciable_value', 'recoverable_amount', 'impaired')
    def _compute_impairment(self):
        for asset in self:
            if asset.impaired and asset.recoverable_amount:
                carrying = asset.depreciable_value - asset.accumulated_depreciation
                asset.impairment_loss = max(carrying - asset.recoverable_amount, 0)
            else:
                asset.impairment_loss = 0
    
    def action_impair_asset(self):
        """Open impairment wizard."""
        self.ensure_one()
        if self.state != 'running':
            raise UserError(_('Can only impair running assets.'))
        return {
            'name': _('Record Impairment'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.asset.impairment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
                'default_current_carrying_amount': self.depreciable_value - self.accumulated_depreciation,
            }
        }


class OpsAssetImpairmentWizard(models.TransientModel):
    """Wizard to record asset impairment."""
    _name = 'ops.asset.impairment.wizard'
    _description = 'Asset Impairment Wizard'
    
    asset_id = fields.Many2one('ops.asset', required=True)
    impairment_date = fields.Date(string='Impairment Date', required=True, default=fields.Date.today)
    currency_id = fields.Many2one(related='asset_id.currency_id')
    current_carrying_amount = fields.Monetary(string='Current Carrying Amount', readonly=True)
    recoverable_amount = fields.Monetary(string='Recoverable Amount', required=True)
    impairment_loss = fields.Monetary(string='Impairment Loss', compute='_compute_loss')
    reason = fields.Text(string='Impairment Reason', required=True)
    regenerate_schedule = fields.Boolean(string='Regenerate Depreciation Schedule', default=True)
    
    @api.depends('current_carrying_amount', 'recoverable_amount')
    def _compute_loss(self):
        for wizard in self:
            if wizard.recoverable_amount and wizard.current_carrying_amount > wizard.recoverable_amount:
                wizard.impairment_loss = wizard.current_carrying_amount - wizard.recoverable_amount
            else:
                wizard.impairment_loss = 0
    
    def action_record_impairment(self):
        """Record the impairment."""
        self.ensure_one()
        if self.impairment_loss <= 0:
            raise UserError(_('No impairment loss to record.'))
        
        asset = self.asset_id
        if not asset.impairment_loss_account_id:
            raise UserError(_('Please configure an impairment loss account on the asset.'))
        
        move_vals = {
            'date': self.impairment_date, 'journal_id': asset.category_id.journal_id.id,
            'ref': f'Asset Impairment: {asset.name}', 'ops_branch_id': asset.ops_branch_id.id,
            'line_ids': [
                (0, 0, {'account_id': asset.impairment_loss_account_id.id, 'name': f'Impairment Loss: {asset.name}',
                        'debit': self.impairment_loss, 'credit': 0}),
                (0, 0, {'account_id': asset.category_id.account_depreciation_id.id, 'name': f'Impairment: {asset.name}',
                        'debit': 0, 'credit': self.impairment_loss}),
            ],
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        asset.write({
            'impaired': True, 'impairment_date': self.impairment_date, 'original_value': asset.depreciable_value,
            'recoverable_amount': self.recoverable_amount, 'depreciable_value': self.recoverable_amount,
            'impairment_move_id': move.id,
        })
        asset.message_post(body=_('Asset impaired. Loss: %s. Reason: %s') % (self.impairment_loss, self.reason))
        
        if self.regenerate_schedule:
            future_lines = asset.depreciation_ids.filtered(lambda l: l.state == 'draft' and l.depreciation_date > self.impairment_date)
            future_lines.unlink()
            asset.generate_depreciation_schedule()
        
        return {'type': 'ir.actions.act_window_close'}
```

================================================================================
TASK 5.5: FX REVALUATION
================================================================================

5. Create wizard/ops_fx_revaluation_wizard.py:

```python
# -*- coding: utf-8 -*-
"""OPS Foreign Currency Revaluation - Calculate and record unrealized FX gains/losses."""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class OpsFxRevaluationWizard(models.TransientModel):
    """FX Revaluation Wizard."""
    _name = 'ops.fx.revaluation.wizard'
    _description = 'Foreign Currency Revaluation'
    
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    revaluation_date = fields.Date(string='Revaluation Date', required=True, default=fields.Date.today)
    ops_branch_ids = fields.Many2many('ops.branch', string='Branches')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                  domain="[('company_id', '=', company_id), ('type', '=', 'general')]")
    currency_ids = fields.Many2many('res.currency', string='Currencies')
    
    account_type_filter = fields.Selection([
        ('all', 'All Monetary Accounts'),
        ('receivable_payable', 'Receivables & Payables Only'),
        ('bank', 'Bank Accounts Only'),
    ], string='Account Filter', default='receivable_payable', required=True)
    
    revaluation_line_ids = fields.One2many('ops.fx.revaluation.line', 'wizard_id', string='Revaluation Lines')
    total_gain = fields.Monetary(string='Total Gain', compute='_compute_totals')
    total_loss = fields.Monetary(string='Total Loss', compute='_compute_totals')
    net_result = fields.Monetary(string='Net Result', compute='_compute_totals')
    currency_id = fields.Many2one(related='company_id.currency_id')
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('calculated', 'Calculated'), ('posted', 'Posted')], default='draft')
    
    @api.depends('revaluation_line_ids.adjustment_amount')
    def _compute_totals(self):
        for wizard in self:
            gains = sum(wizard.revaluation_line_ids.filtered(lambda l: l.adjustment_amount > 0).mapped('adjustment_amount'))
            losses = sum(wizard.revaluation_line_ids.filtered(lambda l: l.adjustment_amount < 0).mapped('adjustment_amount'))
            wizard.total_gain = gains
            wizard.total_loss = abs(losses)
            wizard.net_result = gains + losses
    
    def action_calculate(self):
        """Calculate FX revaluation adjustments."""
        self.ensure_one()
        self.revaluation_line_ids.unlink()
        
        currencies = self.currency_ids or self.env['res.currency'].search([
            ('id', '!=', self.company_id.currency_id.id), ('active', '=', True)])
        
        account_domain = [('company_id', '=', self.company_id.id), ('currency_id', 'in', currencies.ids)]
        if self.account_type_filter == 'receivable_payable':
            account_domain.append(('account_type', 'in', ['asset_receivable', 'liability_payable']))
        elif self.account_type_filter == 'bank':
            account_domain.append(('account_type', '=', 'asset_cash'))
        
        accounts = self.env['account.account'].search(account_domain)
        lines_to_create = []
        
        for account in accounts:
            move_line_domain = [
                ('account_id', '=', account.id), ('date', '<=', self.revaluation_date),
                ('parent_state', '=', 'posted'), ('reconciled', '=', False)]
            if self.ops_branch_ids:
                move_line_domain.append(('ops_branch_id', 'in', self.ops_branch_ids.ids))
            
            move_lines = self.env['account.move.line'].search(move_line_domain)
            if not move_lines:
                continue
            
            foreign_balance = sum(move_lines.mapped('amount_currency'))
            book_balance = sum(move_lines.mapped('balance'))
            if abs(foreign_balance) < 0.01:
                continue
            
            currency = account.currency_id
            current_rate = currency._get_rates(self.company_id, self.revaluation_date).get(currency.id, 1.0)
            fair_value = foreign_balance / current_rate if current_rate else foreign_balance
            adjustment = fair_value - book_balance
            
            if abs(adjustment) < 0.01:
                continue
            
            lines_to_create.append({
                'wizard_id': self.id, 'account_id': account.id, 'currency_id': currency.id,
                'foreign_balance': foreign_balance, 'book_balance': book_balance,
                'exchange_rate': current_rate, 'fair_value': fair_value, 'adjustment_amount': adjustment,
            })
        
        if lines_to_create:
            self.env['ops.fx.revaluation.line'].create(lines_to_create)
        
        self.write({'state': 'calculated'})
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {'title': _('Calculation Complete'),
                       'message': _('%d accounts analyzed, net adjustment: %s') % (len(lines_to_create), self.net_result),
                       'type': 'success'}
        }
    
    def action_post(self):
        """Create and post revaluation journal entry."""
        self.ensure_one()
        if self.state != 'calculated':
            raise UserError(_('Please calculate revaluation first.'))
        if not self.revaluation_line_ids:
            raise UserError(_('No revaluation adjustments to post.'))
        
        gain_account = self.company_id.income_currency_exchange_account_id
        loss_account = self.company_id.expense_currency_exchange_account_id
        if not gain_account or not loss_account:
            raise UserError(_('Please configure currency exchange gain/loss accounts in the company settings.'))
        
        move_lines = []
        for line in self.revaluation_line_ids:
            if abs(line.adjustment_amount) < 0.01:
                continue
            move_lines.append((0, 0, {
                'account_id': line.account_id.id, 'name': f'FX Revaluation: {line.account_id.name}',
                'debit': line.adjustment_amount if line.adjustment_amount > 0 else 0,
                'credit': -line.adjustment_amount if line.adjustment_amount < 0 else 0,
                'currency_id': line.currency_id.id, 'amount_currency': 0,
            }))
        
        if self.net_result > 0:
            move_lines.append((0, 0, {'account_id': gain_account.id, 'name': 'Unrealized FX Gain', 'debit': 0, 'credit': self.net_result}))
        elif self.net_result < 0:
            move_lines.append((0, 0, {'account_id': loss_account.id, 'name': 'Unrealized FX Loss', 'debit': -self.net_result, 'credit': 0}))
        
        move = self.env['account.move'].create({
            'date': self.revaluation_date, 'journal_id': self.journal_id.id,
            'ref': f'FX Revaluation {self.revaluation_date}', 'line_ids': move_lines,
        })
        move.action_post()
        self.write({'move_id': move.id, 'state': 'posted'})
        return {'name': _('Revaluation Entry'), 'type': 'ir.actions.act_window', 'res_model': 'account.move', 'res_id': move.id, 'view_mode': 'form'}


class OpsFxRevaluationLine(models.TransientModel):
    """FX Revaluation Line."""
    _name = 'ops.fx.revaluation.line'
    _description = 'FX Revaluation Line'
    
    wizard_id = fields.Many2one('ops.fx.revaluation.wizard', required=True, ondelete='cascade')
    account_id = fields.Many2one('account.account', string='Account', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    company_currency_id = fields.Many2one(related='wizard_id.company_id.currency_id')
    foreign_balance = fields.Monetary(string='Foreign Balance', currency_field='currency_id')
    book_balance = fields.Monetary(string='Book Balance', currency_field='company_currency_id')
    exchange_rate = fields.Float(string='Exchange Rate', digits=(12, 6))
    fair_value = fields.Monetary(string='Fair Value', currency_field='company_currency_id')
    adjustment_amount = fields.Monetary(string='Adjustment', currency_field='company_currency_id')
```

================================================================================
UPDATE FILES
================================================================================

10. Update models/__init__.py:
```python
from . import ops_interbranch_transfer
from . import ops_bank_reconciliation
from . import ops_lease
# Asset impairment is in ops_asset.py extension
```

11. Update wizard/__init__.py:
```python
from . import ops_fx_revaluation_wizard
```

12. Update __manifest__.py data list:
```python
'data': [
    'data/sequences.xml',
    'views/ops_interbranch_transfer_views.xml',
    'views/ops_bank_reconciliation_views.xml',
    'views/ops_lease_views.xml',
    'views/ops_fx_revaluation_views.xml',
],
```

13. Update security/ir.model.access.csv - Add all new models (see full list in original prompt)

14. Create data/sequences.xml with sequences for interbranch transfer, bank reconciliation, and lease

================================================================================
TESTING
================================================================================

After implementation:
- /odoo-restart
- /odoo-update ops_matrix_accounting
- /odoo-logs --tail 200

Test Scenarios:
1. Inter-Branch Transfer: Create, send, receive, reconcile
2. Bank Reconciliation: Import CSV, auto-match, validate
3. IFRS 16 Lease: Generate schedules, activate, record payments
4. Asset Impairment: Impair running asset, verify JE
5. FX Revaluation: Calculate and post revaluation

Commit: [ACCT-FEAT] Add advanced features: inter-branch, bank recon, IFRS 16 leases, impairment, FX reval
```

---

## ALL PHASES COMPLETE - SUMMARY

| Phase | Description | Tasks | Status |
|-------|-------------|-------|--------|
| Phase 1 | Critical Fixes | 4 | ✅ |
| Phase 2 | Core Accounting | 4 | ✅ |
| Phase 3 | Recurring & Automation | 3 | ✅ |
| Phase 4 | Financial Reports | 3 | ✅ |
| Phase 5 | Advanced Features | 5 | ✅ |
| **TOTAL** | | **19 Tasks** | **COMPLETE** |
