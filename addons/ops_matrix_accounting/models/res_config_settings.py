# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ==================================================================
    # PDC CONFIGURATION (Company-level)
    # ==================================================================

    pdc_receivable_account_id = fields.Many2one(
        related='company_id.pdc_receivable_account_id',
        readonly=False,
        string='PDC Receivable Account',
    )

    pdc_payable_account_id = fields.Many2one(
        related='company_id.pdc_payable_account_id',
        readonly=False,
        string='PDC Payable Account',
    )

    pdc_journal_id = fields.Many2one(
        related='company_id.pdc_journal_id',
        readonly=False,
        string='PDC Journal',
    )

    pdc_bounce_expense_account_id = fields.Many2one(
        related='company_id.pdc_bounce_expense_account_id',
        readonly=False,
        string='PDC Bounce Expense Account',
    )

    # ==================================================================
    # THREE-WAY MATCH CONFIGURATION (Company-level)
    # ==================================================================

    three_way_match_required = fields.Boolean(
        related='company_id.three_way_match_required',
        readonly=False,
        string='Require Three-Way Match',
    )

    three_way_match_tolerance = fields.Float(
        related='company_id.three_way_match_tolerance',
        readonly=False,
        string='Match Tolerance %',
    )
