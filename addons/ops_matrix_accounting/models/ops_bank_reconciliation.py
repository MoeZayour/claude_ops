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
                                  domain="[('type', '=', 'bank')]", tracking=True)
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

    def action_reset_draft(self):
        """Reset to draft state."""
        self.write({'state': 'draft'})


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

    def action_manual_match(self):
        """Open wizard for manual matching."""
        self.ensure_one()
        return {
            'name': _('Manual Match'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'target': 'new',
            'domain': [
                ('journal_id', '=', self.reconciliation_id.journal_id.id),
                ('parent_state', '=', 'posted'),
                ('reconciled', '=', False),
            ],
            'context': {
                'default_reconciliation_line_id': self.id,
            },
        }


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
    col_debit = fields.Integer(string='Debit Column', default=-1,
                                help="Use -1 if using single amount column")
    col_credit = fields.Integer(string='Credit Column', default=-1,
                                 help="Use -1 if using single amount column")

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
