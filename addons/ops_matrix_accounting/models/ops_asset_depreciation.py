# -*- coding: utf-8 -*-
"""
OPS Asset Depreciation with Auto-Post Cron Job

Task 2.3: Auto-Depreciation Cron Job
Task 2.4: Degressive Depreciation Fix

Features:
- Automated daily posting of due depreciation entries
- Respects period lock state (skips hard-locked periods)
- Category-level auto_post_depreciation control
- Error tracking and notification to accounting managers
- Monthly depreciation reminder summaries
- Support for Linear, Degressive, and Degressive-then-Linear methods
- Prorata temporis support for first period

Reference: om_account_asset cron pattern
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_round
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsAssetDepreciation(models.Model):
    _name = 'ops.asset.depreciation'
    _description = 'Fixed Asset Depreciation Line'
    _order = 'asset_id asc, sequence asc, depreciation_date asc'

    company_id = fields.Many2one(related='asset_id.company_id', store=True, readonly=True)

    asset_id = fields.Many2one('ops.asset', string='Asset', required=True, ondelete='cascade', index=True)
    category_id = fields.Many2one(related='asset_id.category_id', store=True)

    # Sequence for ordering (important for degressive calculations)
    sequence = fields.Integer(
        string='Sequence',
        default=1,
        help='Order of the depreciation line in the schedule'
    )

    depreciation_date = fields.Date(string='Depreciation Date', required=True)

    # Amount is now a stored field, calculated during schedule generation
    # This is critical for degressive methods where amount depends on previous periods
    amount = fields.Float(
        string='Depreciation Amount',
        digits='Product Price',
        readonly=True,
        help='Depreciation amount for this period (calculated during schedule generation)'
    )

    # Remaining value after this depreciation
    remaining_value = fields.Float(
        string='Remaining Value',
        digits='Product Price',
        readonly=True,
        help='Depreciable value remaining after this depreciation'
    )

    # Cumulative depreciation up to and including this line
    cumulative_depreciation = fields.Float(
        string='Cumulative Depreciation',
        digits='Product Price',
        readonly=True,
        compute='_compute_cumulative',
        store=True,
        help='Total depreciation accumulated up to this period'
    )

    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('failed', 'Failed')
    ], string='Status', default='draft', required=True, index=True)

    # Analytic fields for reporting and grouping, inherited from asset
    branch_id = fields.Many2one(related='asset_id.ops_branch_id', store=True, readonly=True)
    business_unit_id = fields.Many2one(related='asset_id.ops_business_unit_id', store=True, readonly=True)

    # ============================================
    # Auto-Post Tracking Fields (Task 2.3)
    # ============================================
    auto_posted = fields.Boolean(
        string='Auto-Posted',
        default=False,
        readonly=True,
        help='Indicates this entry was posted by the automated cron job'
    )
    auto_post_date = fields.Datetime(
        string='Auto-Post Date',
        readonly=True,
        help='Date/time when this entry was auto-posted'
    )
    auto_post_error = fields.Text(
        string='Auto-Post Error',
        readonly=True,
        help='Error message if auto-posting failed'
    )

    # ============================================
    # COMPUTED FIELDS
    # ============================================

    @api.depends('asset_id', 'sequence', 'amount')
    def _compute_cumulative(self):
        """Compute cumulative depreciation for each line."""
        for line in self:
            if not line.asset_id:
                line.cumulative_depreciation = 0.0
                continue

            # Sum all amounts for this asset up to and including this sequence
            previous_lines = self.search([
                ('asset_id', '=', line.asset_id.id),
                ('sequence', '<=', line.sequence),
            ])
            line.cumulative_depreciation = sum(previous_lines.mapped('amount'))
    
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

    # ============================================
    # Auto-Depreciation Cron Methods (Task 2.3)
    # ============================================

    @api.model
    def cron_auto_post_depreciation(self):
        """
        Automated cron job to post due depreciation entries.

        Runs daily, posts all depreciation lines where:
        - State is 'draft'
        - Depreciation date is today or earlier
        - Asset is in 'running' state
        - Asset category has auto_post_depreciation enabled

        Returns:
            dict: Summary of posted/failed/skipped entries
        """
        _logger.info("=" * 60)
        _logger.info("OPS Auto-Depreciation Cron Started")
        _logger.info("=" * 60)

        today = fields.Date.today()

        # Find due depreciation lines
        domain = [
            ('state', '=', 'draft'),
            ('depreciation_date', '<=', today),
            ('asset_id.state', '=', 'running'),
            ('asset_id.category_id.auto_post_depreciation', '=', True),
        ]

        due_lines = self.search(domain, order='depreciation_date asc, id asc')

        _logger.info("Found %d depreciation lines due for auto-posting", len(due_lines))

        if not due_lines:
            _logger.info("No depreciation lines to process. Cron completed.")
            return {'posted': 0, 'failed': 0, 'skipped': 0}

        posted_count = 0
        failed_count = 0
        skipped_count = 0
        failed_details = []

        # Group by company for proper context
        for company in due_lines.mapped('asset_id.company_id'):
            company_lines = due_lines.filtered(
                lambda l: l.asset_id.company_id == company
            )

            _logger.info("Processing %d lines for company: %s", len(company_lines), company.name)

            for line in company_lines.with_company(company):
                try:
                    # Check period lock
                    if self._is_period_locked(line):
                        _logger.warning(
                            "Skipping line %d - period locked for date %s",
                            line.id, line.depreciation_date
                        )
                        line.write({
                            'auto_post_error': _('Period locked for %s') % line.depreciation_date
                        })
                        skipped_count += 1
                        continue

                    # Post the depreciation
                    line.with_context(auto_post=True).action_post()

                    # Mark as auto-posted
                    line.write({
                        'auto_posted': True,
                        'auto_post_date': fields.Datetime.now(),
                        'auto_post_error': False,
                    })

                    posted_count += 1
                    _logger.info(
                        "Posted depreciation: Asset=%s, Date=%s, Amount=%s",
                        line.asset_id.name, line.depreciation_date, line.amount
                    )

                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    failed_details.append({
                        'line_id': line.id,
                        'asset': line.asset_id.name,
                        'date': str(line.depreciation_date),
                        'error': error_msg,
                    })

                    # Store error on line
                    line.write({
                        'auto_post_error': error_msg[:500]  # Truncate if too long
                    })

                    _logger.error(
                        "Failed to post depreciation: Asset=%s, Date=%s, Error=%s",
                        line.asset_id.name, line.depreciation_date, error_msg
                    )

        # Log summary
        _logger.info("=" * 60)
        _logger.info("OPS Auto-Depreciation Cron Completed")
        _logger.info("  Posted:  %d", posted_count)
        _logger.info("  Failed:  %d", failed_count)
        _logger.info("  Skipped: %d", skipped_count)
        _logger.info("=" * 60)

        # Send notification if failures occurred
        if failed_count > 0:
            self._notify_depreciation_failures(failed_details)

        return {
            'posted': posted_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'failed_details': failed_details,
        }

    def _is_period_locked(self, line):
        """
        Check if the period is locked (hard lock) for the depreciation date.

        Args:
            line: ops.asset.depreciation record

        Returns:
            bool: True if period is hard-locked, False otherwise
        """
        Period = self.env['ops.fiscal.period']
        period = Period.search([
            ('company_id', '=', line.asset_id.company_id.id),
            ('date_from', '<=', line.depreciation_date),
            ('date_to', '>=', line.depreciation_date),
            ('lock_state', '=', 'hard_lock'),
        ], limit=1)
        return bool(period)

    def _notify_depreciation_failures(self, failed_details):
        """
        Send notification to accounting managers about failed auto-posts.

        Args:
            failed_details: list of dicts with failure information
        """
        try:
            # Find accounting managers
            manager_group = self.env.ref('account.group_account_manager', raise_if_not_found=False)
            if not manager_group:
                _logger.warning("Account manager group not found - skipping notification")
                return

            users = manager_group.users.filtered(lambda u: u.email)
            if not users:
                _logger.warning("No users with emails in manager group - skipping notification")
                return

            # Build email content
            body = """
                <h3>Asset Depreciation Auto-Post Failures</h3>
                <p>The following depreciation entries could not be automatically posted:</p>
                <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%%;">
                    <tr style="background-color: #f0f0f0;">
                        <th>Asset</th>
                        <th>Date</th>
                        <th>Error</th>
                    </tr>
            """

            for detail in failed_details[:20]:  # Limit to 20 entries
                body += """
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
                """ % (detail['asset'], detail['date'], detail['error'][:100])

            if len(failed_details) > 20:
                body += """
                    <tr>
                        <td colspan="3"><i>... and %d more failures</i></td>
                    </tr>
                """ % (len(failed_details) - 20)

            body += """
                </table>
                <p>Please review and post manually or fix the issues.</p>
            """

            # Create mail
            mail_values = {
                'subject': _('Asset Depreciation Auto-Post Failures - %s') % fields.Date.today(),
                'body_html': body,
                'email_to': ','.join(users.mapped('email')),
            }

            self.env['mail.mail'].sudo().create(mail_values).send()
            _logger.info("Depreciation failure notification sent to %d users", len(users))

        except Exception as e:
            _logger.error("Failed to send depreciation notification: %s", e)

    @api.model
    def cron_send_depreciation_reminder(self):
        """
        Monthly reminder cron - sends summary of pending depreciation.
        Runs on 1st of each month.

        Returns:
            dict: Summary of pending depreciation by company
        """
        _logger.info("OPS Depreciation Reminder Cron Started")

        today = fields.Date.today()

        # Find pending depreciation for current month
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        pending = self.search([
            ('state', '=', 'draft'),
            ('depreciation_date', '>=', month_start),
            ('depreciation_date', '<=', month_end),
            ('asset_id.state', '=', 'running'),
        ])

        if not pending:
            _logger.info("No pending depreciation for current month")
            return {'companies': {}}

        result = {'companies': {}}

        # Group by company and prepare summary
        for company in pending.mapped('asset_id.company_id'):
            company_pending = pending.filtered(lambda l: l.asset_id.company_id == company)
            total_amount = sum(company_pending.mapped('amount'))

            result['companies'][company.name] = {
                'count': len(company_pending),
                'total_amount': total_amount,
            }

            _logger.info(
                "Company %s: %d pending entries, total amount: %s",
                company.name, len(company_pending), total_amount
            )

            # Send email reminder to accounting managers
            self._send_depreciation_reminder_email(company, company_pending, month_start, month_end)

        _logger.info("OPS Depreciation Reminder Cron Completed")
        return result

    def _send_depreciation_reminder_email(self, company, pending_lines, month_start, month_end):
        """
        Send monthly depreciation reminder email to company's accounting managers.

        Args:
            company: res.company record
            pending_lines: recordset of pending depreciation lines
            month_start: First day of current month
            month_end: Last day of current month
        """
        try:
            # Find accounting managers for this company
            manager_group = self.env.ref('account.group_account_manager', raise_if_not_found=False)
            if not manager_group:
                return

            users = manager_group.users.filtered(
                lambda u: u.email and (u.company_id == company or company in u.company_ids)
            )
            if not users:
                return

            total_amount = sum(pending_lines.mapped('amount'))

            body = """
                <h3>Monthly Depreciation Reminder - %s</h3>
                <p><strong>Company:</strong> %s</p>
                <p><strong>Period:</strong> %s to %s</p>
                <p><strong>Pending Entries:</strong> %d</p>
                <p><strong>Total Depreciation Amount:</strong> %s</p>

                <h4>Summary by Asset Category:</h4>
                <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%%;">
                    <tr style="background-color: #f0f0f0;">
                        <th>Category</th>
                        <th>Count</th>
                        <th>Amount</th>
                    </tr>
            """ % (
                month_start.strftime('%B %Y'),
                company.name,
                month_start.strftime('%Y-%m-%d'),
                month_end.strftime('%Y-%m-%d'),
                len(pending_lines),
                total_amount
            )

            # Group by category
            for category in pending_lines.mapped('category_id'):
                cat_lines = pending_lines.filtered(lambda l: l.category_id == category)
                body += """
                    <tr>
                        <td>%s</td>
                        <td>%d</td>
                        <td>%s</td>
                    </tr>
                """ % (category.name, len(cat_lines), sum(cat_lines.mapped('amount')))

            body += """
                </table>
                <p style="margin-top: 20px;">
                    <a href="/web#action=ops_matrix_accounting.action_ops_asset_depreciation"
                       style="background-color: #875a7b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Review Pending Depreciation
                    </a>
                </p>
            """

            mail_values = {
                'subject': _('Monthly Depreciation Reminder - %s - %s') % (
                    company.name, month_start.strftime('%B %Y')
                ),
                'body_html': body,
                'email_to': ','.join(users.mapped('email')),
            }

            self.env['mail.mail'].sudo().create(mail_values).send()
            _logger.info(
                "Monthly depreciation reminder sent for company %s to %d users",
                company.name, len(users)
            )

        except Exception as e:
            _logger.error("Failed to send monthly reminder for company %s: %s", company.name, e)
