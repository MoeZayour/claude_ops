# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from typing import List, Dict, Any

class OpsBusinessUnit(models.Model):
    _name = 'ops.business.unit'
    _description = 'Strategic Business Unit (Profit Center)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    # ---------------------------------------------------------
    # Basic Fields
    # ---------------------------------------------------------
    name = fields.Char(
        required=True,
        tracking=True,
        string='Business Unit Name',
        help='Business Unit name representing a distinct business vertical, product line, or profit center. '
             'Examples: "Retail Division", "Wholesale Operations", "E-Commerce", "Professional Services". '
             'This name appears throughout the system in: reports, product catalogs, financial statements, access control. '
             'Best Practice: Use consistent naming that reflects your organizational structure. '
             'A BU typically has its own P&L and may operate across multiple branches.'
    )
    code = fields.Char(
        string='Code',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
        help='Unique identifier for this Business Unit across all companies. '
             'Auto-generated on save (format: BU-XXXX). '
             'Used in: Product codes, financial reports, analytics, security rules. '
             'Cannot be changed after creation. '
             'Examples: BU-RETAIL, BU-WHSL, BU-ONLINE, BU-SERV. '
             'Format: Alphanumeric, no spaces, typically 6-12 characters. '
             'This code becomes part of product identifiers if product silo is enabled.'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of this Business Unit\'s purpose, scope, and responsibilities. '
             'Include: Products/services offered, target market, key objectives, operational scope. '
             'Example: "Retail Division handles all consumer-facing retail sales across our store network, '
             'including electronics, appliances, and accessories. Target customers: individual consumers and small businesses." '
             'Use Cases: Onboarding new employees, documenting organizational structure, clarifying BU boundaries. '
             'Best Practice: Keep updated as the BU evolves.'
    )
    sequence = fields.Integer(
        default=10,
        string='Sequence',
        help='Controls the display order of Business Units in lists, reports, and drop-down menus. '
             'Lower numbers appear first. Default is 10. '
             'Example: Set 1 for flagship BU, 5 for major BUs, 10 for standard BUs, 20 for support BUs. '
             'Use Cases: Prioritize frequently-used BUs, group by importance, order by revenue contribution. '
             'Tip: Use increments of 5 or 10 to allow easy reordering without affecting other BUs.'
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
        help='If unchecked, this Business Unit becomes invisible in most views but historical data is preserved. '
             'Use this instead of deleting BUs that have: historical transactions, products, or financial records. '
             'Inactive BUs cannot be selected for new: products, sales orders, or transactions. '
             'Existing products and transactions remain visible and reportable. '
             'To reactivate: check this box again. '
             'Use Cases: Discontinued product lines, merged BUs, seasonal operations, restructured divisions.'
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
        help='Color coding for visual identification in kanban, calendar, and dashboard views. '
             'Values 0-11 map to predefined Odoo colors. '
             'Use Cases: Color code by BU type (Blue=Retail, Green=Wholesale, Yellow=Services), '
             'by performance (Green=profitable, Red=needs attention), or by market segment. '
             'Example: All B2C BUs use color 2 (blue), B2B BUs use color 3 (yellow). '
             'Tip: Maintain consistent color schemes for easy recognition across reports and views.'
    )
    target_margin_percent = fields.Float(
        string='Target Margin %',
        help='Target profit margin percentage for this Business Unit (e.g., 15.0 for 15%). '
             'Used for: Performance dashboards, variance analysis, manager KPIs, executive reports. '
             'The system compares actual margin against this target and highlights variances. '
             'Example: Retail BUs might target 25%, Wholesale 10%, Services 40%. '
             'Calculation: (Revenue - COGS - Operating Expenses) / Revenue × 100. '
             'Best Practice: Review and adjust quarterly based on market conditions and strategic goals. '
             'Leave at 0 if margin targets don\'t apply to this BU.'
    )

    # ---------------------------------------------------------
    # Hierarchy - Link to Branches (not Companies)
    # ---------------------------------------------------------
    branch_ids = fields.Many2many(
        'ops.branch',
        'business_unit_branch_rel',
        'business_unit_id',
        'branch_id',
        string='Operating Branches',
        required=True,
        help='Branches where this Business Unit operates. Required: At least one branch must be selected. '
             'A BU can operate in multiple branches (multi-location BUs) or a single branch (location-specific BUs). '
             'Examples: '
             '- "Retail Electronics" operates in all retail store branches '
             '- "Warehouse Operations" operates only in the distribution center branch '
             '- "Regional Services" operates in all branches within a region. '
             'Access Control: Users need access to BOTH a branch AND this BU to see related transactions. '
             'Reporting: BU reports can be filtered by branch to analyze performance by location.'
    )
    
    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
        compute='_compute_company_ids',
        store=True,
        help='Legal entities (companies) where this BU operates. Computed automatically from operating branches. '
             'A BU spans companies if its branches belong to different legal entities. '
             'This field is READ-ONLY and automatically maintained. '
             'Used for: Multi-company filtering, legal entity reporting, compliance. '
             'Example: If BU operates in branches from Company A and Company B, both companies are listed. '
             'Important: Cannot be edited directly - change the operating branches to update companies.'
    )
    
    primary_branch_id = fields.Many2one(
        'ops.branch',
        string='Primary Branch',
        tracking=True,
        help='The main/headquarters branch for this Business Unit. '
             'This is where the BU Leader typically sits and where administrative functions are based. '
             'Must be one of the branches selected in "Operating Branches" above. '
             'Used for: Default financial reporting location, primary contact branch, cost allocations. '
             'Example: A regional BU operates in 20 stores but has headquarters in the regional office branch. '
             'Optional: Leave empty if there is no primary branch (all branches are equal). '
             'This does NOT restrict operations to only this branch.'
    )

    # ---------------------------------------------------------
    # Leadership
    # ---------------------------------------------------------
    leader_id = fields.Many2one(
        'res.users',
        string='Unit Leader',
        domain="[('share', '=', False)]",
        tracking=True,
        help='User responsible for this Business Unit\'s overall performance and operations. '
             'Typically has: P&L responsibility, strategic decision authority, resource allocation control. '
             'The leader typically receives: performance reports, approval requests, budget variance alerts. '
             'Only internal users (not portal users) can be BU leaders. '
             'Examples: "VP of Retail", "Wholesale Operations Director", "E-Commerce Manager". '
             'Related: Configure a Persona for the leader to set approval limits and delegation rules. '
             'Best Practice: Assign a leader for each active BU to ensure clear accountability.'
    )

    # ---------------------------------------------------------
    # Analytic Integration
    # ---------------------------------------------------------
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=False,
        readonly=True,
        help='Auto-generated analytic account for tracking this BU as a profit center. '
             'Automatically created when the BU is saved. '
             'Used to: Generate P&L by BU, track revenue and costs, analyze profitability, allocate shared expenses. '
             'Format: Code and name match the BU (e.g., "BU-RETAIL - Retail Division"). '
             'All financial transactions for this BU are tagged with this analytic account. '
             'This field is READ-ONLY and managed automatically by the system. '
             'Financial reports can filter by this account to show BU-specific performance.'
    )

    # ---------------------------------------------------------
    # Computed Fields
    # ---------------------------------------------------------
    branch_count = fields.Integer(
        compute='_compute_branch_count',
        string='Branch Count',
        help='Total number of branches where this Business Unit currently operates. '
             'Computed automatically from the "Operating Branches" list. '
             'Click the smart button to view the full list of branches. '
             'Examples: Single-branch BU shows 1, regional BU might show 10-20, nationwide BU could show 100+. '
             'Use Cases: Assessing BU scale, resource planning, understanding operational complexity. '
             'Performance Tip: BUs operating in many branches may need dedicated coordination roles.'
    )

    @api.depends('branch_ids')
    def _compute_branch_count(self) -> None:
        """Count branches for this BU."""
        for bu in self:
            bu.branch_count = len(bu.branch_ids)

    @api.depends('branch_ids', 'branch_ids.company_id')
    def _compute_company_ids(self) -> None:
        """Compute companies from branches."""
        for bu in self:
            bu.company_ids = bu.branch_ids.mapped('company_id')

    # ---------------------------------------------------------
    # Constraints & Validation
    # ---------------------------------------------------------
    @api.constrains('branch_ids')
    def _check_branch_ids(self) -> None:
        """Business Unit must operate in at least one branch."""
        for bu in self:
            if not bu.branch_ids:
                raise ValidationError(_("Business Unit must operate in at least one branch."))

    @api.constrains('primary_branch_id', 'branch_ids')
    def _check_primary_branch(self) -> None:
        """Primary branch must be in operating branches."""
        for bu in self:
            if bu.primary_branch_id and bu.primary_branch_id not in bu.branch_ids:
                raise ValidationError(_(
                    "Primary branch '%s' must be in the list of operating branches."
                ) % bu.primary_branch_id.name)

    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         'Business Unit Code must be unique!')
    ]

    # ---------------------------------------------------------
    # CRUD & Analytic Sync
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'OpsBusinessUnit':
        """Create BU with auto-generated code and analytic account."""
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.business.unit') or 'New'
        
        records = super().create(vals_list)
        records._create_analytic_accounts()
        return records

    def write(self, vals: Dict[str, Any]) -> bool:
        """Update BU and sync analytic account if name/code changed."""
        result = super().write(vals)
        if 'name' in vals or 'code' in vals:
            self._sync_analytic_account_name()
        return result

    # ---------------------------------------------------------
    # Analytic Account Management
    # ---------------------------------------------------------
    def _create_analytic_accounts(self) -> None:
        """Create one analytic account per BU (not per branch)."""
        for bu in self:
            if not bu.analytic_account_id:
                # Use primary branch's company, or first company if no primary
                company_id = False
                if bu.primary_branch_id:
                    company_id = bu.primary_branch_id.company_id.id
                elif bu.company_ids:
                    company_id = bu.company_ids[0].id
                else:
                    company_id = self.env.company.id
                
                analytic_plan = self._get_or_create_analytic_plan('Business Unit')
                analytic_account = self.env['account.analytic.account'].create({
                    'name': f"{bu.code} - {bu.name}",
                    'code': bu.code,
                    'plan_id': analytic_plan.id,
                    'company_id': company_id,
                })
                bu.analytic_account_id = analytic_account.id

    def _sync_analytic_account_name(self) -> None:
        """Sync analytic account name when BU name/code changes."""
        for bu in self:
            if bu.analytic_account_id:
                bu.analytic_account_id.write({
                    'name': f"{bu.code} - {bu.name}",
                    'code': bu.code,
                })

    def _get_or_create_analytic_plan(self, plan_type: str) -> 'account.analytic.plan':
        """Get or create analytic plan for Business Unit dimension."""
        plan_name = f"Matrix {plan_type}"
        plan = self.env['account.analytic.plan'].search([('name', '=', plan_name)], limit=1)
        if not plan:
            plan = self.env['account.analytic.plan'].create({
                'name': plan_name,
                # Note: company_id removed - not available in Odoo 19
                'description': f'{plan_type} dimension for Matrix reporting',
            })
        return plan

    # ---------------------------------------------------------
    # Display Name
    # ---------------------------------------------------------
    def name_get(self):
        """Display as '[CODE] Name'."""
        result = []
        for bu in self:
            name = f"[{bu.code}] {bu.name}"
            result.append((bu.id, name))
        return result
