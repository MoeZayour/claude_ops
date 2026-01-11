# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from typing import List, Dict, Any

class OpsBranch(models.Model):
    _name = 'ops.branch'
    _description = 'Operational Branch (not a legal entity)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'
    _check_company_auto = True

    # ---------------------------------------------------------
    # Required Fields
    # ---------------------------------------------------------
    name = fields.Char(
        required=True,
        tracking=True,
        string='Branch Name',
        help='Descriptive name for this branch/location. '
             'Example: "Downtown Store", "North Region HQ", "Warehouse 3". '
             'This name appears throughout the system in reports and transactions.'
    )
    code = fields.Char(
        string='Code',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
        help='Unique identifier for this branch within the company. '
             'Auto-generated on save (format: BR-XXXX). '
             'Used in reports, analytics, and as reference in transactions. '
             'Cannot be changed after creation. '
             'Example: BR-001, BR-NORTH, BR-WH3'
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        ondelete='restrict',
        default=lambda self: self.env.company,
        index=True,
        tracking=True,
        string='Legal Entity',
        help='The legal entity (company) this branch belongs to. '
             'All branches must be associated with a company for legal and tax purposes. '
             'A company can have multiple branches, but a branch belongs to one company. '
             'Note: This is the LEGAL entity, not the operational structure. '
             'Cannot be changed after transactions are created.'
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Branch Manager',
        domain="[('share', '=', False)]",
        tracking=True,
        help='User responsible for this branch\'s operations. '
             'The manager typically has: approval authority, access to branch reports, '
             'and ability to manage branch-specific settings. '
             'Only internal users (not portal users) can be managers. '
             'Related: Configure persona for the manager to set approval limits and permissions.'
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
        help='If unchecked, this branch becomes invisible in most views but data is preserved. '
             'Use this instead of deleting branches that have historical transactions. '
             'Inactive branches cannot be selected in new transactions but existing records remain visible. '
             'To reactivate: check this box again. '
             'Use Case: Closed stores, merged branches, or temporarily inactive locations.'
    )
    
    # ---------------------------------------------------------

    is_headquarters = fields.Boolean(
        string='Is Headquarters',
        default=False,
        tracking=True,
        help='Mark this branch as the main headquarters/head office. '
             'Only one branch per company should be marked as HQ. '
             'The HQ branch typically has higher approval authority '
             'and serves as the central point for company-wide reporting.'
    )
    # Optional Fields
    # ---------------------------------------------------------
    parent_id = fields.Many2one(
        'ops.branch',
        string='Parent Branch',
        index=True,
        help='Parent branch in the organizational hierarchy for multi-level structures. '
             'Example: "North Region HQ" (parent) → "Seattle Store" (child) → "Seattle Outlet" (grandchild). '
             'Child branches can inherit settings and roll up reporting to parents. '
             'Leave empty if this is a top-level branch. '
             'Use Cases: Regional→City→Store, Corporate→Division→Department. '
             'Warning: Circular hierarchies (A→B→A) are automatically prevented.'
    )
    child_ids = fields.One2many(
        'ops.branch',
        'parent_id',
        string='Sub-Branches',
        help='Branches that report to this branch in the hierarchy. '
             'Example: If this is "North Region", children might be "Seattle", "Portland", "Vancouver". '
             'Use for consolidated reporting: parent branch reports include all child branch data. '
             'Automatically populated when child branches set this branch as their parent.'
    )
    address = fields.Text(
        string='Physical Address',
        help='Complete physical address of this branch location. '
             'Include: Slistt, City, State/Province, ZIP/Postal Code, Country. '
             'Used in: Customer-facing documents (invoices, delivery notes), shipping labels, branch reports. '
             'Format: Use line breaks for readability. '
             'Example: "123 Main Slistt\\nSuite 400\\nSeattle, WA 98101\\nUnited States". '
             'Best Practice: Keep updated for accurate shipping and legal compliance.'
    )
    phone = fields.Char(
        string='Phone',
        help='Primary contact phone number for this branch. '
             'Used for: Customer service inquiries, inter-branch communication, emergency contacts. '
             'Format: Use your local convention (e.g., +1-555-123-4567, (555) 123-4567, +44 20 1234 5678). '
             'Best Practice: Include country code for international branches. '
             'Example: "+1-206-555-0100" or "(206) 555-0100"'
    )
    email = fields.Char(
        string='Email',
        help='Primary email address for this branch. '
             'Used for: Automated system notifications, inter-branch communication, customer inquiries. '
             'Format: branch@company.com or location-name@company.com. '
             'Examples: "seattle@acme.com", "north-region@acme.com", "warehouse3@acme.com". '
             'Best Practice: Use a group/department email (not personal) to ensure continuity. '
             'This email may appear on customer-facing documents.'
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Primary Warehouse',
        help='The main warehouse associated with this branch for inventory operations. '
             'This warehouse is used by default when creating: stock transfers, sales orders, purchase orders. '
             'A branch can have multiple warehouses, but this is the primary one. '
             'Important: The warehouse must belong to the same company as the branch. '
             'Use Case: For retail branches, this is the stock room; for distribution centers, the main warehouse. '
             'Leave empty if this branch has no inventory operations (e.g., administrative office).'
    )
    sequence = fields.Integer(
        default=10,
        string='Sequence',
        help='Controls the display order of branches in lists and drop-down menus. '
             'Lower numbers appear first. Default is 10. '
             'Example: Set 1 for headquarters, 5 for regional offices, 10 for standard branches. '
             'Use Cases: Prioritize frequently-used branches, group by region, order by importance. '
             'Tip: Use increments of 5 or 10 to allow easy reordering later.'
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
        help='Color coding for visual identification in kanban and calendar views. '
             'Values 0-11 map to predefined colors in the Odoo interface. '
             'Use Cases: Color code by region (Red=West, Blue=East), by type (Green=Retail, Yellow=Warehouse). '
             'Example: All branches in North region use color 2 (blue), South region uses color 1 (red). '
             'Tip: Keep color scheme consistent across your organization for easy recognition.'
    )

    # ---------------------------------------------------------
    # Analytic Integration
    # ---------------------------------------------------------
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=False,
        readonly=True,
        help='Auto-generated analytic account for financial tracking and cost/profit analysis by branch. '
             'Automatically created when the branch is saved. '
             'Used to: Track revenue and expenses by branch, generate P&L reports, allocate costs. '
             'Format: Code and name match the branch (e.g., "BR-001 - Seattle Store"). '
             'This field is READ-ONLY and managed automatically by the system. '
             'Related: All financial transactions for this branch are tagged with this analytic account.'
    )

    # ---------------------------------------------------------
    # Computed Fields
    # ---------------------------------------------------------
    business_unit_count = fields.Integer(
        compute='_compute_business_unit_count',
        string='Business Units Count',
        help='Number of business units (BUs) operating in this branch. '
             'A branch can host multiple BUs (e.g., Retail, Wholesale, Services). '
             'Computed automatically - counts BUs that list this branch in their operating branches. '
             'Click the smart button to view the list of BUs. '
             'Example: "Downtown Store" might have 3 BUs: Retail Electronics, Retail Appliances, Repair Services. '
             'Use Cases: Understanding branch complexity, resource allocation, reporting structure.'
    )

    # ---------------------------------------------------------
    # SQL Constraints
    # ---------------------------------------------------------
    _sql_constraints = [
        ('code_company_unique',
         'UNIQUE(code, company_id)',
         'Branch Code must be unique per company!')
    ]

    # ---------------------------------------------------------
    # Computed Methods
    # ---------------------------------------------------------
    def _compute_business_unit_count(self) -> None:
        """Count business units operating in this branch."""
        for branch in self:
            branch.business_unit_count = self.env['ops.business.unit'].search_count([
                ('branch_ids', 'in', branch.id)
            ])

    # ---------------------------------------------------------
    # Constraints & Validation
    # ---------------------------------------------------------
    @api.constrains('parent_id')
    def _check_parent_recursion(self) -> None:
        """Prevent circular parent relationships."""
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive branch hierarchies.'))

    def unlink(self) -> bool:
        """Prevent deletion if branch has active transactions."""
        for branch in self:
            # Check for related transactions
            transaction_models = [
                'sale.order',
                'purchase.order',
                'account.move',
                'stock.picking',
            ]
            
            for model_name in transaction_models:
                if self.env[model_name].search_count([('ops_branch_id', '=', branch.id)], limit=1) > 0:
                    raise UserError(_(
                        "Cannot delete branch '%s' because it has related transactions. "
                        "Please deactivate it instead."
                    ) % branch.name)
        
        return super().unlink()

    # ---------------------------------------------------------
    # CRUD & Analytic Sync
    # ---------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'OpsBranch':
        """Create branch with auto-generated code and analytic account."""
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.branch') or 'New'
        
        records = super().create(vals_list)
        records._create_analytic_accounts()
        return records

    def write(self, vals: Dict[str, Any]) -> bool:
        """Update branch and sync analytic account if name/code changed."""
        result = super().write(vals)
        if 'name' in vals or 'code' in vals:
            self._sync_analytic_account_name()
        return result

    # ---------------------------------------------------------
    # Analytic Account Management
    # ---------------------------------------------------------
    def _create_analytic_accounts(self) -> None:
        """Auto-create analytic account for each branch."""
        for branch in self:
            if not branch.analytic_account_id:
                analytic_plan = self._get_or_create_analytic_plan('Branch')
                analytic_account = self.env['account.analytic.account'].create({
                    'name': f"{branch.code} - {branch.name}",
                    'code': branch.code,
                    'plan_id': analytic_plan.id,
                    'company_id': branch.company_id.id,
                })
                branch.analytic_account_id = analytic_account.id

    def _sync_analytic_account_name(self) -> None:
        """Sync analytic account name when branch name/code changes."""
        for branch in self:
            if branch.analytic_account_id:
                branch.analytic_account_id.write({
                    'name': f"{branch.code} - {branch.name}",
                    'code': branch.code,
                })

    def _get_or_create_analytic_plan(self, plan_type: str) -> 'account.analytic.plan':
        """Get or create analytic plan for Branch dimension."""
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
        for branch in self:
            name = f"[{branch.code}] {branch.name}"
            result.append((branch.id, name))
        return result
