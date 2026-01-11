# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
import logging

_logger = logging.getLogger(__name__)

class OpsAssetDepreciation(models.Model):
    _name = 'ops.asset.depreciation'
    _description = 'Fixed Asset Depreciation Line'
    _order = 'depreciation_date asc, asset_id asc'

    company_id = fields.Many2one(related='asset_id.company_id', store=True, readonly=True)

    asset_id = fields.Many2one('ops.asset', string='Asset', required=True, ondelete='cascade', index=True)
    category_id = fields.Many2one(related='asset_id.category_id', store=True)
    depreciation_date = fields.Date(string='Depreciation Date', required=True)
    amount = fields.Float(string='Depreciation Amount', readonly=True, compute='_compute_amount', store=True)
    
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('failed', 'Failed')
    ], string='Status', default='draft', required=True, tracking=True, index=True)

    # Analytic fields for reporting and grouping, inherited from asset
    branch_id = fields.Many2one(related='asset_id.ops_branch_id', store=True, readonly=True)
    business_unit_id = fields.Many2one(related='asset_id.ops_business_unit_id', store=True, readonly=True)

    @api.depends('asset_id', 'depreciation_date')
    def _compute_amount(self):
        for line in self:
            asset = line.asset_id
            if not asset or not asset.category_id or asset.depreciable_value <= 0:
                line.amount = 0.0
                continue
            
            category = asset.category_id
            total_periods = category.depreciation_duration * 12
            if total_periods == 0:
                line.amount = 0.0
                continue

            # Distribute rounding on the last period
            # Get all lines in order, to see if this is the last one
            all_lines = self.search([('asset_id', '=', asset.id)], order='depreciation_date asc, id asc')
            is_last_line = all_lines and all_lines[-1].id == line.id

            if is_last_line:
                posted_amount = sum(self.search([
                    ('asset_id', '=', asset.id),
                    ('state', '=', 'posted'),
                    ('id', '!=', line.id) # Exclude self
                ]).mapped('amount'))
                line.amount = asset.depreciable_value - posted_amount
            else:
                if category.depreciation_method == 'straight_line':
                    line.amount = asset.depreciable_value / total_periods
                elif category.depreciation_method == 'declining_balance':
                    # This is a simplified version. A real implementation might need a declining factor.
                    # For now, we use a double-declining method as an example.
                    book_value_at_start_of_period = asset.book_value
                    line.amount = (book_value_at_start_of_period * (2 / total_periods))
                else:
                    line.amount = 0.0
    
    def action_post(self):
        if not self:
            return True
            
        created_moves = self.env['account.move']
        for line in self.filtered(lambda l: l.state == 'draft' and not float_is_zero(l.amount, precision_digits=2)):
            try:
                move = line._create_journal_entry()
                move.action_post()
                line.write({
                    'state': 'posted',
                    'move_id': move.id
                })
                created_moves |= move
                _logger.info(f"Posted depreciation for asset {line.asset_id.name} on {line.depreciation_date}")
            except UserError as e:
                _logger.error(f"Failed to post depreciation for asset {line.asset_id.name}: {e}")
                line.state = 'failed'
                self.env.cr.commit() # Commit the failure state

        return {
            'name': _('Created Journal Entries'),
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', created_moves.ids)],
        }

    def _create_journal_entry(self):
        self.ensure_one()
        asset = self.asset_id
        category = asset.category_id
        
        if not all([category.journal_id, category.expense_account_id, category.depreciation_account_id]):
            raise UserError(_('The asset category is missing some accounting configuration (Journal, Expense Account, or Depreciation Account).'))

        move_lines = [
            # Debit: Depreciation Expense
            (0, 0, {
                'account_id': category.expense_account_id.id,
                'debit': self.amount,
                'credit': 0.0,
                'name': _('Depreciation of %s') % asset.name,
                'partner_id': asset.partner_id.id if hasattr(asset, 'partner_id') else None,
                'analytic_account_id': asset.analytic_account_id.id if hasattr(asset, 'analytic_account_id') else None,
            }),
            # Credit: Accumulated Depreciation
            (0, 0, {
                'account_id': category.depreciation_account_id.id,
                'debit': 0.0,
                'credit': self.amount,
                'name': _('Depreciation of %s') % asset.name,
                'partner_id': asset.partner_id.id if hasattr(asset, 'partner_id') else None,
                'analytic_account_id': asset.analytic_account_id.id if hasattr(asset, 'analytic_account_id') else None,
            }),
        ]

        move_vals = {
            'journal_id': category.journal_id.id,
            'date': self.depreciation_date,
            'ref': asset.code,
            'line_ids': move_lines,
            'asset_id': asset.id, # Link back to the asset
            'branch_id': asset.branch_id.id,
            'business_unit_id': asset.business_unit_id.id,
        }

        return self.env['account.move'].create(move_vals)

    def action_view_move(self):
        self.ensure_one()
        if not self.move_id:
            raise UserError(_("No journal entry associated with this depreciation line."))
        return {
            'name': _('Journal Entry'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'res_id': self.move_id.id,
        }

    def unlink(self):
        if any(line.state == 'posted' for line in self):
            raise UserError(_("You cannot delete a depreciation line that has already been posted."))
        return super(OpsAssetDepreciation, self).unlink()
