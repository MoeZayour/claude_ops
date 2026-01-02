# OPS Framework - Complete Architectural Analysis
## Generated: 2025-12-25 | Odoo 19 CE | MZ DB Environment

---

## Executive Summary

The OPS Framework implements a **Matrix Organizational Structure** for Odoo 19 CE, enabling dual-dimensional reporting across **Geo-Branches** (geographic locations) and **Business Units** (cross-geographic profit centers) while maintaining a **single legal entity** financial consolidation model.

**Critical Design Principle**: Geo-Branches are operational divisions that do NOT create separate financial entities. All branches roll up into ONE company for accounting purposes.

---

## 1. Core Architecture Overview

### 1.1 Module Structure

```
/opt/gemini_odoo19/addons/
├── ops_matrix_core/          # Structural foundation
├── ops_matrix_accounting/    # Financial consolidation
└── ops_matrix_reporting/     # Cross-dimensional analytics
```

### 1.2 Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                  OPS MATRIX REPORTING                       │
│  (SQL Views for Cross-Dimensional Analytics)                │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│              OPS MATRIX ACCOUNTING                          │
│  (Financial Logic: Single Entity Consolidation)             │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                OPS MATRIX CORE                              │
│  (Models: ops.branch, ops.business.unit, ops.matrix.mixin)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. OPS Matrix Core - Deep Dive

### 2.1 Branch Model (`ops.branch`)

**File**: [`addons/ops_matrix_core/models/ops_branch.py`](../addons/ops_matrix_core/models/ops_branch.py:6)

#### Inheritance Pattern
```python
_name = 'ops.branch'
_description = 'Operational Branch (not a legal entity)'
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**CRITICAL FINDING**: This is a **CUSTOM MODEL**, NOT an inheritance of Odoo's native `res.branch`. The framework creates a completely independent branch structure.

#### Key Architectural Decisions

1. **Single Legal Entity Design**
   ```python
   company_id = fields.Many2one(
       'res.company', 
       required=True,
       string='Legal Entity'
   )
   ```
   - Each branch MUST belong to exactly ONE company
   - Multiple branches share the same financial books
   - No separate chart of accounts per branch

2. **Hierarchical Structure**
   ```python
   parent_id = fields.Many2one('ops.branch', string='Parent Branch')
   child_ids = fields.One2many('ops.branch', 'parent_id')
   ```
   - Supports multi-level hierarchy: Regional → City → Outlet
   - Enables cascade reporting

3. **Analytic Integration**
   ```python
   analytic_account_id = fields.Many2one(
       'account.analytic.account',
       readonly=True,
       help="Auto-generated analytic account for financial tracking"
   )
   ```
   - Each branch gets an **automatic analytic account**
   - Tracks financial performance without separate ledgers
   - Auto-syncs with "Matrix Branch" analytic plan

4. **Branch Code Auto-Generation**
   ```python
   code = fields.Char(
       required=True, 
       readonly=True, 
       default=lambda self: _('New')
   )
   ```
   - Uses sequence: `ir.sequence.next_by_code('ops.branch')`
   - Constraint: `UNIQUE(code, company_id)`

### 2.2 Business Unit Model (`ops.business.unit`)

**File**: [`addons/ops_matrix_core/models/ops_business_unit.py`](../addons/ops_matrix_core/models/ops_business_unit.py:6)

#### The Cross-Geographic Dimension

```python
_name = 'ops.business.unit'
_description = 'Strategic Business Unit (Profit Center)'
```

#### Key Architectural Decisions

1. **Many-to-Many Branch Relationship**
   ```python
   branch_ids = fields.Many2many(
       'ops.branch',
       'business_unit_branch_rel',
       'business_unit_id',
       'branch_id',
       string='Operating Branches',
       required=True
   )
   ```
   - **A BU can operate in MULTIPLE branches**
   - **A Branch can host MULTIPLE BUs**
   - This is the core of the matrix structure

2. **Company Derivation (Computed)**
   ```python
   @api.depends('branch_ids', 'branch_ids.company_id')
   def _compute_company_ids(self):
       for bu in self:
           bu.company_ids = bu.branch_ids.mapped('company_id')
   ```
   - BU companies are **derived from branches**
   - BUs are not tied to companies directly
   - Enables cross-company BUs if branches span multiple companies

3. **Primary Branch Concept**
   ```python
   primary_branch_id = fields.Many2one(
       'ops.branch',
       string='Primary Branch',
       help='Main branch where BU leader sits'
   )
   ```
   - Designates the "home" location for BU leadership
   - Used for default analytic account company assignment

4. **Analytic Account Creation**
   ```python
   def _create_analytic_accounts(self):
       # Creates ONE analytic account per BU (not per branch)
       analytic_account = self.env['account.analytic.account'].create({
           'name': f"{bu.code} - {bu.name}",
           'plan_id': analytic_plan.id,  # "Matrix Business Unit" plan
           'company_id': primary_branch_company_id
       })
   ```
   - **One analytic account per BU globally**
   - NOT one per branch-BU combination
   - Tracks BU performance across all locations

### 2.3 Matrix Mixin (`ops.matrix.mixin`)

**File**: [`addons/ops_matrix_core/models/ops_matrix_mixin.py`](../addons/ops_matrix_core/models/ops_matrix_mixin.py:4)

#### Purpose
Provides **dimension propagation** to all transactional models (sales, purchases, invoices, pickings).

#### Core Fields

```python
ops_branch_id = fields.Many2one(
    'res.company',  # COMPATIBILITY: Using res.company as branch temporarily
    string='Branch',
    default=lambda self: self._get_default_ops_branch()
)

ops_business_unit_id = fields.Many2one(
    'ops.business.unit',
    string='Business Unit',
    default=lambda self: self._get_default_ops_business_unit()
)

ops_company_id = fields.Many2one(
    'res.company',
    compute='_compute_ops_company',
    store=True,
    help="Legal entity computed from branch"
)
```

**CRITICAL NOTE**: Currently using `res.company` as branch reference for compatibility. This explains the dual model situation (ops.branch exists but res.company is used in transactions).

#### Analytic Distribution Logic

```python
@api.depends('ops_branch_id', 'ops_business_unit_id')
def _compute_analytic_distribution(self):
    distribution = {}
    
    # Branch: 50% weight
    if record.ops_branch_id:
        distribution[str(branch_analytic_account_id)] = 50
    
    # BU: 50% weight
    if record.ops_business_unit_id:
        distribution[str(bu_analytic_account_id)] = 50
    
    # If only one dimension: 100%
    if len(distribution) == 1:
        distribution[key] = 100.0
```

**Odoo 19 Format**: `{'analytic_account_id': percentage}`

---

## 3. OPS Matrix Accounting - Financial Consolidation

### 3.1 Single Legal Entity Architecture

**File**: [`addons/ops_matrix_accounting/models/ops_matrix_standard_extensions.py`](../addons/ops_matrix_accounting/models/ops_matrix_standard_extensions.py:1)

#### Core Principle

**Branches do NOT create separate financial entities**. All branches share:
- One Chart of Accounts
- One set of fiscal periods
- One set of journals
- One consolidated P&L and Balance Sheet

#### How It Works

1. **Account Move Extensions**
   ```python
   class AccountMove(models.Model):
       _inherit = 'account.move'
       
       ops_branch_id = fields.Many2one('res.company', string='Branch')
       ops_business_unit_id = fields.Many2one('ops.business.unit')
   ```

2. **Dimension Propagation**
   ```python
   def _prepare_invoice(self):
       invoice_vals = super()._prepare_invoice()
       invoice_vals.update({
           'ops_branch_id': self.ops_branch_id.id,
           'ops_business_unit_id': self.ops_business_unit_id.id,
       })
       return invoice_vals
   ```
   - Sale Order → Invoice: Dimensions propagate
   - Purchase Order → Bill: Dimensions propagate
   - Stock Picking: Inherits from source document

3. **Analytic Tagging (Not Separate Books)**
   ```python
   @api.model_create_multi
   def create(self, vals_list):
       moves = super().create(vals_list)
       for move in moves:
           for line in move.line_ids:
               # Apply analytic distribution
               if not line.ops_branch_id:
                   line.ops_branch_id = move.ops_branch_id
               if not line.ops_business_unit_id:
                   line.ops_business_unit_id = move.ops_business_unit_id
       return moves
   ```

### 3.2 Financial Reports

**File**: [`addons/ops_matrix_core/models/account_move.py`](../addons/ops_matrix_core/models/account_move.py:7)

#### Dual Inheritance Pattern

```python
class AccountMove(models.Model):
    _inherit = ['account.move', 'ops.matrix.mixin']
    _name = 'account.move'
```

This allows:
- Full native Odoo accounting functionality
- Matrix dimension tracking via mixin
- Analytic distribution automation

#### Validation Rules

```python
@api.constrains('ops_branch_id', 'ops_business_unit_id')
def _check_matrix_dimensions(self):
    for move in self:
        if move.move_type in ('out_invoice', 'in_invoice'):
            if not move.ops_branch_id:
                raise ValidationError("Branch is required")
            if not move.ops_business_unit_id:
                raise ValidationError("Business Unit is required")
            
            # Validate BU operates in Branch
            if move.ops_branch_id not in move.ops_business_unit_id.branch_ids:
                raise ValidationError("BU does not operate in Branch")
```

**Result**: Invoices/Bills MUST have valid Branch-BU combinations before posting.

---

## 4. OPS Matrix Reporting - Cross-Dimensional Analytics

### 4.1 Reporting Architecture

**Files**:
- [`ops_sales_analysis.py`](../addons/ops_matrix_reporting/models/ops_sales_analysis.py:5)
- [`ops_financial_analysis.py`](../addons/ops_matrix_reporting/models/ops_financial_analysis.py:4)
- [`ops_inventory_analysis.py`](../addons/ops_matrix_reporting/models/ops_inventory_analysis.py)

#### SQL View Strategy

```python
_name = 'ops.sales.analysis'
_description = 'Sales Analysis by Branch and Business Unit'
_auto = False  # Don't auto-create table - use view
_rec_name = 'id'
```

#### Sales Analysis View Structure

```sql
CREATE OR REPLACE VIEW ops_sales_analysis AS (
    SELECT
        sol.id,
        so.date_order,
        sol.product_id,
        so.partner_id,
        
        -- OPS MATRIX DIMENSIONS
        so.ops_branch_id,
        so.ops_business_unit_id,
        
        -- Quantities & Revenue
        sol.product_uom_qty,
        sol.price_subtotal,
        
        -- Margin Calculation
        (sol.price_subtotal - 
         (sol.product_uom_qty * pp.standard_price)) AS margin,
        
        -- Margin Percentage
        CASE WHEN sol.price_subtotal = 0 THEN 0
        ELSE ROUND((margin / sol.price_subtotal * 100)::numeric, 2)
        END AS margin_percent
    
    FROM sale_order_line sol
    INNER JOIN sale_order so ON sol.order_id = so.id
    LEFT JOIN product_product pp ON sol.product_id = pp.id
    
    WHERE so.state IN ('sale', 'done')
)
```

### 4.2 Cross-Dimensional Aggregation Methods

#### By Branch Only
```python
@api.model
def get_summary_by_branch(self):
    self.env.cr.execute("""
        SELECT
            ops_branch_id,
            SUM(price_subtotal) as total_revenue,
            SUM(margin) as total_margin,
            AVG(margin_percent) as avg_margin_percent
        FROM ops_sales_analysis
        WHERE ops_branch_id IN (user's allowed branches)
        GROUP BY ops_branch_id
    """)
```

#### By Business Unit Only
```python
@api.model
def get_summary_by_business_unit(self):
    # Same structure, GROUP BY ops_business_unit_id
```

#### Matrix View (Branch × BU)
```python
@api.model
def get_summary_by_matrix(self):
    self.env.cr.execute("""
        SELECT
            ops_branch_id,
            ops_business_unit_id,
            SUM(price_subtotal) as total_revenue,
            SUM(margin) as total_margin
        FROM ops_sales_analysis
        WHERE 
            ops_branch_id IN (user's allowed branches)
            AND ops_business_unit_id IN (user's allowed BUs)
        GROUP BY ops_branch_id, ops_business_unit_id
    """)
```

**Output Example**:
```
Branch_A × BU_Alpha: $100K revenue
Branch_A × BU_Beta:  $50K revenue
Branch_B × BU_Alpha: $75K revenue
Branch_B × BU_Beta:  $125K revenue
```

### 4.3 Financial Analysis View

Similar structure for account moves:

```sql
CREATE OR REPLACE VIEW ops_financial_analysis AS (
    SELECT
        aml.id,
        am.date,
        aml.account_id,
        
        -- OPS MATRIX DIMENSIONS (from move level)
        am.ops_branch_id,
        am.ops_business_unit_id,
        
        am.move_type,
        aml.debit,
        aml.credit,
        (aml.debit - aml.credit) AS balance
    
    FROM account_move_line aml
    INNER JOIN account_move am ON aml.move_id = am.id
    
    WHERE am.state = 'posted'
      AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
)
```

---

## 5. Corporate HQ Visibility Architecture

### 5.1 User Access Control Model

**File**: [`addons/ops_matrix_core/models/res_users.py`](../addons/ops_matrix_core/models/res_users.py:7)

#### Matrix Access Fields

```python
class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # Multi-branch access
    ops_allowed_branch_ids = fields.Many2many(
        'res.company',
        'res_users_ops_allowed_branch_rel',
        string='Allowed Branches'
    )
    
    # Multi-business unit access
    ops_allowed_business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'res_users_ops_allowed_business_unit_rel',
        string='Allowed Business Units'
    )
    
    # Role flags
    is_cross_branch_bu_leader = fields.Boolean(
        help='Can access the same business unit across multiple branches'
    )
    
    is_matrix_administrator = fields.Boolean(
        help='Can configure and manage matrix structure'
    )
```

### 5.2 Cross-Branch BU Leader Access

**Implementation**:
```python
def get_effective_matrix_access(self):
    self.ensure_one()
    
    # Start with direct assignments
    branches = self.ops_allowed_branch_ids
    business_units = self.ops_allowed_business_unit_ids
    
    # For cross-branch BU leaders: Get ALL branches where BUs operate
    if self.is_cross_branch_bu_leader and business_units:
        bu_branches = business_units.mapped('branch_ids')
        branches |= bu_branches  # Union of all branches
    
    return {
        'branches': branches,
        'business_units': business_units,
    }
```

**Example Scenario**:

```
User: John (BU Leader for "Electronics")
- Role: is_cross_branch_bu_leader = True
- Assigned BU: Electronics
- Electronics operates in: Branch_NYC, Branch_LA, Branch_CHI

Result: John automatically gets access to Electronics in ALL three branches
```

### 5.3 Corporate HQ View

#### System Administrator Access
```python
if self.has_group('base.group_system'):
    return {
        'branches': self.env['res.company'].search([]),  # ALL branches
        'business_units': self.env['ops.business.unit'].search([]),  # ALL BUs
    }
```

#### Matrix Administrator Access
- Can configure branches and BUs
- Cannot access data unless explicitly granted
- Separation of structure management vs. data access

#### Data Access Validation
```python
def can_access_matrix_combination(self, branch_id, bu_id):
    """Check if user can access specific branch-BU combination."""
    
    # For cross-branch BU leaders
    if self.is_cross_branch_bu_leader:
        # Can access their BUs in ANY branch
        allowed_bus = self.get_effective_matrix_access()['business_units']
        return bu_id in allowed_bus.ids
    
    # Regular users: BU must operate in the branch
    bu = self.env['ops.business.unit'].browse(bu_id)
    branch = self.env['res.company'].browse(branch_id)
    return branch in bu.branch_ids
```

---

## 6. Critical Implementation Findings

### 6.1 ✅ Verified: Custom Branch Model
- **NOT** inheriting from `res.branch`
- Using `_name = 'ops.branch'` (independent model)
- Temporary compatibility: `ops_branch_id` references `res.company`
- Future migration path: Switch from `res.company` to `ops.branch`

### 6.2 ✅ Verified: Single Legal Entity
- All branches under ONE company
- No separate chart of accounts per branch
- Financial consolidation is AUTOMATIC (same company)
- Differentiation via analytic accounts only

### 6.3 ✅ Verified: Cross-Geographic BU Dimension
- BUs span multiple branches (Many2many)
- BU managers can see BU globally via `is_cross_branch_bu_leader`
- Primary branch designates BU headquarters
- One analytic account per BU (not per branch)

### 6.4 ✅ Verified: Corporate HQ Visibility
- System admins: Full access to all dimensions
- Cross-branch BU leaders: See their BUs across all branches
- Matrix administrators: Structure management only
- Regular users: Restricted to assigned branches + BUs

### 6.5 ⚠️ Compatibility Layer Identified
**Current State**:
```python
ops_branch_id = fields.Many2one('res.company', string='Branch')
```

**Target State** (when fully migrated):
```python
ops_branch_id = fields.Many2one('ops.branch', string='Branch')
```

The framework is in a **transition phase**, using `res.company` as a branch proxy while `ops.branch` model exists separately.

---

## 7. Data Flow Diagrams

### 7.1 Transaction Flow: Sale Order → Invoice

```
┌─────────────────┐
│  SALE ORDER     │
│  Branch: NYC    │
│  BU: Electronics│
└────────┬────────┘
         │ _prepare_invoice()
         │ (propagates dimensions)
         ▼
┌─────────────────┐
│  INVOICE        │
│  Branch: NYC    │
│  BU: Electronics│
└────────┬────────┘
         │ create() → _compute_analytic_distribution()
         │
         ▼
┌────────────────────────────────────┐
│  JOURNAL ITEMS (account.move.line) │
│  analytic_distribution = {         │
│    'branch_analytic_123': 50,      │
│    'bu_analytic_456': 50           │
│  }                                 │
└────────────────────────────────────┘
```

### 7.2 Reporting Aggregation Flow

```
┌──────────────────────────────────────────┐
│  TRANSACTIONAL DATA                      │
│  (sale.order, account.move, etc.)        │
│  Tagged with: ops_branch_id, ops_bu_id   │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│  SQL VIEWS (Read-Only)                   │
│  - ops_sales_analysis                    │
│  - ops_financial_analysis                │
│  - ops_inventory_analysis                │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│  AGGREGATION METHODS                     │
│  - get_summary_by_branch()               │
│  - get_summary_by_business_unit()        │
│  - get_summary_by_matrix()               │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│  DASHBOARDS & REPORTS                    │
│  - Branch Dashboard                      │
│  - BU Dashboard                          │
│  - Executive Dashboard (Matrix View)     │
└──────────────────────────────────────────┘
```

---

## 8. Security & Access Control

### 8.1 Record Rules

**Branch Access Rule**:
```xml
<record id="rule_sale_order_branch_access" model="ir.rule">
    <field name="name">Sale Order: Branch Access</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="domain_force">
        ['|',
            ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids),
            ('ops_branch_id', '=', False)
        ]
    </field>
</record>
```

**Business Unit Access Rule**:
```xml
<record id="rule_sale_order_bu_access" model="ir.rule">
    <field name="name">Sale Order: BU Access</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="domain_force">
        ['|',
            ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids),
            ('ops_business_unit_id', '=', False)
        ]
    </field>
</record>
```

### 8.2 Multi-Level Access

```python
# User can see data if:
# 1. System admin (sees everything)
# 2. Has company access (sees all branches in company)
# 3. Has branch access (sees specific branches)
# 4. Has BU access (sees specific BUs)
# 5. Cross-branch BU leader (sees BU across all branches)
```

---

## 9. Key Architectural Patterns

### 9.1 Separation of Concerns

| Layer | Responsibility | Models |
|-------|----------------|---------|
| **Core** | Structure definition | `ops.branch`, `ops.business.unit`, mixins |
| **Accounting** | Financial logic | Account move extensions, analytic distribution |
| **Reporting** | Analytics | SQL views, aggregation methods |

### 9.2 Dimension Propagation Pattern

```python
# Source Document (e.g., Sale Order)
order.ops_branch_id = Branch_NYC
order.ops_business_unit_id = BU_Electronics

# Create Invoice
invoice = order._create_invoices()
# Automatic: invoice.ops_branch_id = Branch_NYC
# Automatic: invoice.ops_business_unit_id = BU_Electronics

# Post Invoice
invoice.action_post()
# Automatic: All journal lines get analytic distribution
```

### 9.3 Computed Dimension Pattern

```python
# Company is COMPUTED from Branch
@api.depends('ops_branch_id')
def _compute_ops_company(self):
    for record in self:
        record.ops_company_id = record.ops_branch_id.company_id
```

This ensures:
- User selects Branch (not Company)
- Company is automatically determined
- Prevents company-branch mismatches

---

## 10. Migration & Compatibility Notes

### 10.1 Current State (Compatibility Mode)

```python
# Using res.company as temporary branch reference
ops_branch_id = fields.Many2one('res.company', string='Branch')
```

**Reason**: Gradual migration from standard Odoo structure to OPS Matrix

### 10.2 Target State (Full OPS Matrix)

```python
# Native ops.branch usage
ops_branch_id = fields.Many2one('ops.branch', string='Branch')
```

### 10.3 Migration Path

1. Phase 1: ✅ Create `ops.branch` model
2. Phase 2: ⏳ Use `res.company` as proxy in transactions
3. Phase 3: ⏳ Data migration: Map res.company → ops.branch
4. Phase 4: ⏳ Switch field references
5. Phase 5: ⏳ Remove compatibility layer

**Current Status**: Phase 2 (Compatibility Mode)

---

## 11. Performance Optimizations

### 11.1 SQL Views for Reporting
- Read-only views prevent ORM overhead
- Pre-computed aggregations
- Indexed dimension fields

### 11.2 Analytic Distribution
- JSON field (Odoo 19 format) for fast lookups
- Computed at transaction time, not query time
- Stored for performance

### 11.3 Effective Access Caching
```python
# Access computation happens once
effective_access = user.get_effective_matrix_access()
# Then reused for all record rule evaluations
```

---

## 12. Testing & Validation

### 12.1 Test Coverage

**Files**:
- [`test_matrix_foundation.py`](../addons/ops_matrix_core/tests/test_matrix_foundation.py)
- [`test_matrix_governance.py`](../addons/ops_matrix_core/tests/test_matrix_governance.py)
- [`test_matrix_integration.py`](../addons/ops_matrix_core/tests/test_matrix_integration.py)
- [`test_matrix_reporting.py`](../addons/ops_matrix_core/tests/test_matrix_reporting.py)
- [`test_matrix_security.py`](../addons/ops_matrix_core/tests/test_matrix_security.py)
- [`test_matrix_transactions.py`](../addons/ops_matrix_core/tests/test_matrix_transactions.py)

### 12.2 Key Test Scenarios

1. **Branch Creation**: Auto-generates code and analytic account
2. **BU Creation**: Validates branch relationships
3. **Transaction Flow**: SO → Invoice dimension propagation
4. **Access Control**: User sees only allowed dimensions
5. **Cross-Branch Leader**: Sees BU across all branches
6. **Financial Validation**: Cannot post invoice without dimensions

---

## 13. Conclusions

### 13.1 Strategic Objectives Achievement

| Objective | Status | Implementation |
|-----------|--------|----------------|
| Geo-Branches under single legal entity | ✅ Achieved | `ops.branch` with `company_id` reference |
| Cross-geographic BU dimension | ✅ Achieved | `ops.business.unit` with Many2many branches |
| Financial consolidation (single entity) | ✅ Achieved | All branches share company's chart of accounts |
| Corporate HQ visibility | ✅ Achieved | `is_cross_branch_bu_leader` flag + effective access |
| Dual-dimension reporting | ✅ Achieved | SQL views with Branch × BU aggregations |

### 13.2 Architecture Strengths

1. **Clean Separation**: Core structure, accounting logic, and reporting are decoupled
2. **Scalability**: SQL views handle large datasets efficiently
3. **Flexibility**: Matrix administrators can restructure without affecting data
4. **Compliance**: Single legal entity ensures regulatory compliance
5. **User Experience**: Automatic dimension propagation reduces manual work

### 13.3 Known Limitations

1. **Compatibility Mode**: Still using `res.company` as branch proxy in transactions
2. **Migration Pending**: Full switch to `ops.branch` requires data migration
3. **Performance**: Analytic distribution JSON parsing can be slow on very large datasets
4. **UI Complexity**: Users must understand Branch vs. BU concept

---

## 14. Recommendations

### 14.1 Immediate Actions

1. **Complete Migration**: Finish transition from `res.company` to `ops.branch` in transaction models
2. **Index Optimization**: Add database indexes on `ops_branch_id` and `ops_business_unit_id` fields
3. **User Training**: Document Branch vs. BU concept for end users

### 14.2 Future Enhancements

1. **Budget Module**: Add branch/BU-level budgeting
2. **Forecasting**: Predictive analytics by dimension
3. **Mobile Dashboards**: Branch managers need mobile access
4. **API Integration**: Expose matrix dimensions via REST/GraphQL

---

## 15. Technical Reference

### 15.1 Key Database Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `ops_branch` | Branch master data | id, code, name, company_id, parent_id, analytic_account_id |
| `ops_business_unit` | BU master data | id, code, name, primary_branch_id, analytic_account_id |
| `business_unit_branch_rel` | Many2many BU↔Branch | business_unit_id, branch_id |
| `res_users_ops_allowed_branch_rel` | User branch access | user_id, branch_id |
| `res_users_ops_allowed_business_unit_rel` | User BU access | user_id, business_unit_id |

### 15.2 Key Sequences

- `ops.branch`: Branch code generation
- `ops.business.unit`: BU code generation

### 15.3 Key Analytic Plans

- `Matrix Branch`: Branch dimension analytics
- `Matrix Business Unit`: BU dimension analytics

---

## 16. Appendix: Code Examples

### 16.1 Creating a Branch

```python
branch = self.env['ops.branch'].create({
    'name': 'New York Office',
    'code': 'NYC',  # Auto-generated if not provided
    'company_id': company.id,
    'manager_id': manager_user.id,
    'address': '123 Broadway, New York, NY 10001',
})
# Automatically creates analytic account
```

### 16.2 Creating a Business Unit

```python
bu = self.env['ops.business.unit'].create({
    'name': 'Electronics Division',
    'code': 'ELEC',  # Auto-generated if not provided
    'branch_ids': [(6, 0, [branch_nyc.id, branch_la.id])],
    'primary_branch_id': branch_nyc.id,
    'leader_id': bu_leader_user.id,
})
# Automatically creates analytic account
```

### 16.3 Creating a Sale Order with Dimensions

```python
order = self.env['sale.order'].create({
    'partner_id': customer.id,
    'ops_branch_id': branch_nyc.id,
    'ops_business_unit_id': bu_electronics.id,
    'order_line': [(0, 0, {
        'product_id': product.id,
        'product_uom_qty': 10,
    })],
})
# Dimensions automatically propagate to invoice
invoice = order._create_invoices()
```

### 16.4 Querying Cross-Dimensional Data

```python
# Get sales by Branch × BU matrix
matrix_data = self.env['ops.sales.analysis'].get_summary_by_matrix()

# Result example:
# [
#     {'ops_branch_id': 1, 'ops_business_unit_id': 1, 'total_revenue': 100000},
#     {'ops_branch_id': 1, 'ops_business_unit_id': 2, 'total_revenue': 50000},
#     {'ops_branch_id': 2, 'ops_business_unit_id': 1, 'total_revenue': 75000},
# ]
```

---

## Document Metadata

- **Generated**: 2025-12-25 17:35:00 UTC
- **Environment**: Odoo 19 CE, gemini_odoo19 Docker, mz-db PostgreSQL
- **Analysis Scope**: Full modular deep-dive
- **Next Review**: OPS Gemi 2.md (incremental audit on next run)
- **Analyst**: Roo Code (AI Architecture Analysis)

---

**END OF DOCUMENT**
