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

    # ==================================================================
    # REPORT COLOR CONFIGURATION
    # ==================================================================

    ops_report_primary_color = fields.Char(
        string='Report Primary Color',
        default='#5B6BBB',
        help='Primary color used in financial report headers, borders, totals, and section accents. '
             'Independent of UI theme color.',
    )
    ops_report_text_on_primary = fields.Char(
        string='Text on Primary',
        default='#FFFFFF',
        help='Text color on primary-colored backgrounds in reports. '
             'White for dark primaries, dark for light primaries.',
    )
    ops_report_body_text_color = fields.Char(
        string='Report Body Text',
        default='#1a1a1a',
        help='Main body text color for printed reports. '
             'Adjust for print clarity on different printers.',
    )

    def get_report_primary_light(self):
        """Generate light background from primary color (15% opacity blend with white)."""
        primary = self.ops_report_primary_color or '#5B6BBB'
        primary = primary.lstrip('#')
        if len(primary) != 6:
            primary = '5B6BBB'
        try:
            r, g, b = int(primary[0:2], 16), int(primary[2:4], 16), int(primary[4:6], 16)
        except ValueError:
            r, g, b = 0x5B, 0x6B, 0xBB
        opacity = 0.15
        light_r = int(r * opacity + 255 * (1 - opacity))
        light_g = int(g * opacity + 255 * (1 - opacity))
        light_b = int(b * opacity + 255 * (1 - opacity))
        return '#{:02x}{:02x}{:02x}'.format(light_r, light_g, light_b)

    def get_report_primary_dark(self):
        """Generate darker shade for text on light backgrounds."""
        primary = self.ops_report_primary_color or '#5B6BBB'
        primary = primary.lstrip('#')
        if len(primary) != 6:
            primary = '5B6BBB'
        try:
            r, g, b = int(primary[0:2], 16), int(primary[2:4], 16), int(primary[4:6], 16)
        except ValueError:
            r, g, b = 0x5B, 0x6B, 0xBB
        factor = 0.75
        return '#{:02x}{:02x}{:02x}'.format(int(r * factor), int(g * factor), int(b * factor))
