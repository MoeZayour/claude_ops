# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from typing import List, Dict, Any
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    # ==================================================================
    # THREE-WAY MATCH CONFIGURATION
    # ==================================================================
    enable_three_way_match = fields.Boolean('Enable Three-Way Match', default=True)
    three_way_match_tolerance = fields.Float('Match Tolerance (%)', default=5.0)
    three_way_match_block_validation = fields.Boolean('Block Invoice Validation', default=True)

    # ==================================================================
    # OPS MATRIX FIELDS - Legal Entity Only
    # ==================================================================
    
    ops_code = fields.Char(
        string='OPS Code',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        tracking=True,
        help="Legal entity identification code (e.g., QAT-001, UAE-001). Auto-generated."
    )
    
    ops_manager_id = fields.Many2one(
        'res.users',
        string='Country Manager',
        domain="[('share', '=', False)]",
        tracking=True,
        help="Company-level manager (CEO, Country Director)"
    )

    ops_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='OPS Analytic Account',
        copy=False,
        readonly=True,
        tracking=True,
        help="Auto-generated analytic account for company-level financial tracking and reporting. "
             "Used for consolidated P&L reports across all operational branches. "
             "Automatically created when the company is saved."
    )

    # ---------------------------------------------------------
    # Branch Relationship (One2many)
    # ---------------------------------------------------------
    branch_ids = fields.One2many(
        'ops.branch',
        'company_id',
        string='Operational Branches',
        help="Operational branches under this legal entity"
    )

    branch_count = fields.Integer(
        compute='_compute_branch_count',
        string='Number of Branches',
        help="Count of operational branches"
    )

    # ---------------------------------------------------------
    # Computed Methods
    # ---------------------------------------------------------
    @api.depends('branch_ids')
    def _compute_branch_count(self) -> None:
        """Count operational branches."""
        for company in self:
            company.branch_count = len(company.branch_ids)

    # ---------------------------------------------------------
    # SQL Constraints
    # ---------------------------------------------------------
    _sql_constraints = [
        ('ops_code_unique',
         'UNIQUE(ops_code)',
         'OPS Code must be unique across all companies!')
    ]

    # ---------------------------------------------------------
    # CRUD & Sequence Generation
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'ResCompany':
        """Override create to auto-generate OPS code and analytic account."""
        for vals in vals_list:
            if vals.get('ops_code', 'New') == 'New':
                vals['ops_code'] = self.env['ir.sequence'].next_by_code('res.company.ops') or 'New'

        records = super().create(vals_list)
        records._create_ops_analytic_accounts()
        return records
    
    def write(self, vals: Dict[str, Any]) -> bool:
        """
        Override write to auto-generate OPS code when company name changes
        but ops_code is still 'New' (handles pre-configured 'New Company' scenario).
        Also sync analytic account name when name changes.
        """
        result = super().write(vals)

        # If name is being changed and ops_code is still 'New', generate proper code
        if 'name' in vals:
            for company in self:
                if company.ops_code == 'New':
                    new_code = self.env['ir.sequence'].next_by_code('res.company.ops') or 'New'
                    # Use super().write to avoid recursion
                    super(ResCompany, company).write({'ops_code': new_code})
                    _logger.info(
                        f"Auto-generated OPS code '{new_code}' for company '{company.name}' "
                        f"(was 'New')"
                    )

        # Sync analytic account name if name changed
        if 'name' in vals:
            self._sync_ops_analytic_account_name()

        return result

    # ---------------------------------------------------------
    # OPS Analytic Account Management
    # ---------------------------------------------------------
    def _create_ops_analytic_accounts(self) -> None:
        """Auto-create OPS analytic account for each company."""
        for company in self:
            if not company.ops_analytic_account_id:
                analytic_plan = self._get_or_create_ops_analytic_plan()
                analytic_account = self.env['account.analytic.account'].create({
                    'name': f"{company.name} - OPS",
                    'code': company.ops_code or 'OPS',
                    'plan_id': analytic_plan.id,
                    'company_id': company.id,
                })
                company.ops_analytic_account_id = analytic_account.id

    def _sync_ops_analytic_account_name(self) -> None:
        """Sync OPS analytic account name when company name changes."""
        for company in self:
            if company.ops_analytic_account_id:
                company.ops_analytic_account_id.write({
                    'name': f"{company.name} - OPS",
                    'code': company.ops_code or 'OPS',
                })

    def _get_or_create_ops_analytic_plan(self) -> 'account.analytic.plan':
        """Get or create OPS analytic plan for company-level tracking."""
        plan_name = "OPS Company"
        plan = self.env['account.analytic.plan'].search([('name', '=', plan_name)], limit=1)
        if not plan:
            plan = self.env['account.analytic.plan'].create({
                'name': plan_name,
                'description': 'Company-level OPS financial tracking and consolidated reporting',
            })
        return plan
