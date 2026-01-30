# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    # ==================================================================
    # PDC CONFIGURATION
    # ==================================================================

    pdc_receivable_account_id = fields.Many2one(
        'account.account',
        string='PDC Receivable Account',
        domain="[('account_type', '=', 'asset_current'), ('company_id', '=', id)]",
        help="Clearing account for Post-Dated Checks Receivable. "
             "Debited when check is deposited, credited when check clears."
    )

    pdc_payable_account_id = fields.Many2one(
        'account.account',
        string='PDC Payable Account',
        domain="[('account_type', '=', 'liability_current'), ('company_id', '=', id)]",
        help="Clearing account for Post-Dated Checks Payable. "
             "Credited when check is issued, debited when check clears."
    )

    pdc_journal_id = fields.Many2one(
        'account.journal',
        string='PDC Journal',
        domain="[('type', '=', 'general'), ('company_id', '=', id)]",
        help="Default journal for PDC transactions. "
             "Should be a miscellaneous journal type."
    )

    pdc_bounce_expense_account_id = fields.Many2one(
        'account.account',
        string='PDC Bounce Expense Account',
        domain="[('account_type', '=', 'expense'), ('company_id', '=', id)]",
        help="Expense account for bank charges on bounced checks (optional)."
    )

    # ==================================================================
    # THREE-WAY MATCH CONFIGURATION
    # ==================================================================

    three_way_match_required = fields.Boolean(
        string='Require Three-Way Match',
        default=False,
        help="When enabled, vendor bills must pass three-way match validation "
             "(PO ↔ Receipt ↔ Invoice) before they can be posted. "
             "Bills without PO reference or with quantity discrepancies will be blocked."
    )

    three_way_match_tolerance = fields.Float(
        string='Match Tolerance %',
        default=0.0,
        help="Acceptable variance percentage for quantity matching. "
             "For example, 5.0 means 5% tolerance is allowed. "
             "Set to 0 for exact matching."
    )
