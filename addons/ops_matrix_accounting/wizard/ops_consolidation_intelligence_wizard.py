# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Consolidation Intelligence Wizard
==========================================================

Unified wizard providing access to all 4 consolidation reports:
- Branch P&L Report
- Business Unit Report
- Company Consolidation P&L
- Consolidated Balance Sheet

Routes user selection to the correct underlying report model.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import date_utils
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class OpsConsolidationIntelligenceWizard(models.TransientModel):
    """Consolidation Intelligence Wizard - unified entry point for consolidated reports."""
    _name = 'ops.consolidation.intelligence.wizard'
    _description = 'Consolidation Intelligence Wizard'

    # -------------------------------------------------------------------------
    # REPORT SELECTION
    # -------------------------------------------------------------------------
    report_type = fields.Selection([
        ('company_consolidation', 'Company Consolidation P&L'),
        ('branch_pl', 'Branch Profit & Loss'),
        ('bu_report', 'Business Unit Report'),
        ('consolidated_bs', 'Consolidated Balance Sheet'),
    ], string='Report Type', required=True, default='company_consolidation')

    # -------------------------------------------------------------------------
    # COMMON FILTERS
    # -------------------------------------------------------------------------
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    date_from = fields.Date(
        string='From Date',
        default=lambda self: date_utils.start_of(datetime.now(), 'month'),
    )

    date_to = fields.Date(
        string='To Date',
        default=lambda self: date_utils.end_of(datetime.now(), 'month'),
    )

    as_of_date = fields.Date(
        string='As of Date',
        default=fields.Date.today,
        help='Balance sheet cutoff date',
    )

    ops_branch_ids = fields.Many2many(
        'ops.branch',
        'ops_consol_wizard_branch_rel',
        'wizard_id', 'branch_id',
        string='Branches',
        help='Leave empty for all branches',
    )

    ops_business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'ops_consol_wizard_bu_rel',
        'wizard_id', 'bu_id',
        string='Business Units',
        help='Leave empty for all business units',
    )

    # -------------------------------------------------------------------------
    # COMPANY CONSOLIDATION SPECIFIC
    # -------------------------------------------------------------------------
    report_detail_level = fields.Selection([
        ('summary', 'Summary Only'),
        ('by_branch', 'By Branch'),
        ('by_bu', 'By Business Unit'),
        ('by_account', 'By Account Group'),
    ], string='Detail Level', default='summary')

    compare_with_previous = fields.Boolean(
        string='Compare with Previous Period',
        default=True,
    )

    # -------------------------------------------------------------------------
    # CONSOLIDATED BS SPECIFIC
    # -------------------------------------------------------------------------
    company_ids = fields.Many2many(
        'res.company',
        'ops_consol_wizard_company_rel',
        'wizard_id', 'company_id_rel',
        string='Companies',
        default=lambda self: self.env.company,
    )

    include_intercompany = fields.Boolean(
        string='Intercompany Eliminations',
        default=True,
    )

    # -------------------------------------------------------------------------
    # BRANCH PL SPECIFIC
    # -------------------------------------------------------------------------
    branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        help='Select a specific branch for the Branch P&L report',
    )

    # -------------------------------------------------------------------------
    # BU REPORT SPECIFIC
    # -------------------------------------------------------------------------
    business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        help='Select a specific business unit for the BU Report',
    )

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    def action_generate(self):
        """Route to the correct report based on report_type selection."""
        self.ensure_one()

        if self.report_type == 'company_consolidation':
            return self._generate_company_consolidation()
        elif self.report_type == 'branch_pl':
            return self._generate_branch_pl()
        elif self.report_type == 'bu_report':
            return self._generate_bu_report()
        elif self.report_type == 'consolidated_bs':
            return self._generate_consolidated_bs()
        else:
            raise UserError(_('Please select a report type.'))

    def _generate_company_consolidation(self):
        """Create Company Consolidation record and generate its PDF."""
        vals = {
            'company_id': self.company_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': self.report_detail_level or 'summary',
            'compare_with_previous': self.compare_with_previous,
        }
        if self.ops_branch_ids:
            vals['branch_ids'] = [(6, 0, self.ops_branch_ids.ids)]

        record = self.env['ops.company.consolidation'].create(vals)
        return self.env.ref(
            'ops_matrix_accounting.report_company_consolidation_pdf'
        ).report_action(record)

    def _generate_branch_pl(self):
        """Create Branch Report record and generate its PDF."""
        if not self.branch_id:
            raise UserError(_('Please select a Branch for the Branch P&L report.'))

        vals = {
            'branch_id': self.branch_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        if self.ops_business_unit_ids:
            vals['business_unit_ids'] = [(6, 0, self.ops_business_unit_ids.ids)]

        record = self.env['ops.branch.report'].create(vals)
        return self.env.ref(
            'ops_matrix_accounting.report_branch_pl_pdf'
        ).report_action(record)

    def _generate_bu_report(self):
        """Create Business Unit Report record and generate its PDF."""
        if not self.business_unit_id:
            raise UserError(_('Please select a Business Unit for the BU Report.'))

        vals = {
            'business_unit_id': self.business_unit_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        if self.ops_branch_ids:
            vals['branch_ids'] = [(6, 0, self.ops_branch_ids.ids)]

        record = self.env['ops.business.unit.report'].create(vals)
        return self.env.ref(
            'ops_matrix_accounting.report_business_unit_pdf'
        ).report_action(record)

    def _generate_consolidated_bs(self):
        """Create Consolidated Balance Sheet record and generate its PDF."""
        companies = self.company_ids if self.company_ids else self.company_id
        vals = {
            'company_ids': [(6, 0, companies.ids)],
            'date': self.as_of_date or fields.Date.today(),
            'include_intercompany': self.include_intercompany,
        }

        record = self.env['ops.consolidated.balance.sheet'].create(vals)
        return self.env.ref(
            'ops_matrix_accounting.report_consolidated_balance_sheet_pdf'
        ).report_action(record)
