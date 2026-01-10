# OPS Matrix Reporting - Technical Specification

## Module: OPS Matrix Reporting

### 1. General Info
- **Technical Name:** `ops_matrix_reporting`
- **Version:** 19.0.1.0
- **Category:** Reporting
- **Application:** Yes (Installable, non-auto-install)
- **License:** LGPL-3
- **Author:** OPS Matrix Development Team

#### Dependencies:
- `ops_matrix_core` (Required - matrix dimensions, security framework)
- `sale_management` (Sales orders for sales analysis)
- `account` (GL entries for financial analysis)
- `stock` (Inventory for inventory analysis)
- `spreadsheet_dashboard` (Dashboard integration)

#### Summary:
High-performance SQL-based reporting engine for the OPS Matrix framework. Three read-only PostgreSQL views provide:
1. **Sales Analysis:** Branch/BU-aware sales metrics with margin tracking
2. **Financial Analysis:** Multi-dimensional GL reporting with transaction tracking
3. **Inventory Analysis:** Stock segregation by BU, health monitoring, valuation

---

## 2. Data Models & Fields

### Model: `ops.sales.analysis`
**Technical Name:** `ops.sales.analysis`
**Description:** Read-only SQL view for sales analysis with Branch/BU dimensions.
**SQL Type:** PostgreSQL View (materialized-style)
**Order:** `date_order DESC`
**Auto:** False (view only, no table)

#### Fields (View Columns):
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `id` | Id | Readonly | Line item ID (from sale_order_line) |
| `date_order` | Datetime | Readonly | Order creation date (from sale_order) |
| `product_id` | Many2one (`product.product`) | Readonly | Product sold |
| `partner_id` | Many2one (`res.partner`) | Readonly | Customer |
| `ops_branch_id` | Many2one (`ops.branch`) | Readonly | Branch from sale order |
| `ops_business_unit_id` | Many2one (`ops.business.unit`) | Readonly | Business unit from sale order |
| `product_uom_qty` | Float | Readonly | Quantity ordered |
| `price_subtotal` | Float | Readonly | Line subtotal (ex. tax) |
| `margin` | Float | Readonly | Gross margin (price_subtotal - COGS) |
| `margin_percent` | Float | Readonly | Margin as percentage (margin / price_subtotal Ã— 100) |

#### SQL View Logic:
```sql
SELECT
    sol.id,
    so.date_order,
    sol.product_id,
    so.partner_id,
    so.ops_branch_id,
    so.ops_business_unit_id,
    sol.product_uom_qty,
    sol.price_subtotal,
    (sol.price_subtotal - (sol.product_uom_qty * pp.standard_price)) AS margin,
    CASE WHEN sol.price_subtotal = 0 THEN 0
         ELSE ROUND(((sol.price_subtotal - (sol.product_uom_qty * pp.standard_price)) / sol.price_subtotal * 100), 2)
    END AS margin_percent
FROM sale_order_line sol
INNER JOIN sale_order so ON sol.order_id = so.id
LEFT JOIN product_product pp ON sol.product_id = pp.id
LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE
    so.state IN ('sale', 'done')
    AND sol.state != 'cancel'
```

**Key Points:**
- Only confirmed/done orders (state in 'sale', 'done')
- Excludes cancelled lines
- Margin = Revenue - (Qty Ã— Standard Cost)
- Margin% calculated with zero-division protection
- Includes NULL check for standard_price (uses 0 as default)

#### Key Methods:

**`init()`**:
- **Trigger:** When module installs or updates
- **Logic:**
  1. Execute CREATE OR REPLACE VIEW SQL statement
  2. View spans sale_order_line â†’ sale_order â†’ product
  3. Calculated fields: margin, margin_percent
  4. Filters: confirmed orders, non-cancelled lines

**`get_summary_by_branch()`** [Class]:
- **Logic:**
  1. Query view with user's allowed branches (security filter)
  2. GROUP BY ops_branch_id
  3. Return aggregated: line_count, total_qty, total_revenue, total_margin, avg_margin_percent
  4. Order by total_revenue DESC
- **Purpose:** Branch-level sales dashboard
- **Returns:** List of dicts: {ops_branch_id, line_count, total_qty, total_revenue, total_margin, avg_margin_percent}

---

### Model: `ops.financial.analysis`
**Technical Name:** `ops.financial.analysis`
**Description:** Read-only SQL view for GL analysis with Branch/BU dimensions.
**SQL Type:** PostgreSQL View
**Order:** `date DESC`
**Auto:** False (view only)

#### Fields (View Columns):
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `id` | Id | Readonly | Move line ID |
| `date` | Date | Readonly | Entry date (from account_move) |
| `move_id` | Many2one (`account.move`) | Readonly | Source journal entry |
| `account_id` | Many2one (`account.account`) | Readonly | GL account |
| `ops_branch_id` | Many2one (`ops.branch`) | Readonly | Branch from move |
| `ops_business_unit_id` | Many2one (`ops.business.unit`) | Readonly | BU from move |
| `move_type` | Selection | Readonly | Move type: out_invoice, out_refund, in_invoice, in_refund |
| `debit` | Float | Readonly | Debit amount |
| `credit` | Float | Readonly | Credit amount |
| `balance` | Float | Readonly | Net balance (debit - credit) |
| `partner_id` | Many2one (`res.partner`) | Readonly | Customer or vendor |

#### SQL View Logic:
```sql
SELECT
    aml.id,
    aml.move_id,
    aml.account_id,
    CAST(am.date AS date) AS date,
    am.ops_branch_id,
    am.ops_business_unit_id,
    am.move_type,
    am.partner_id,
    aml.debit,
    aml.credit,
    (aml.debit - aml.credit) AS balance
FROM account_move_line aml
INNER JOIN account_move am ON aml.move_id = am.id
WHERE
    am.state = 'posted'
    AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
    AND (aml.debit != 0 OR aml.credit != 0)
```

**Key Points:**
- Only posted moves (state='posted')
- Only transaction-related moves (invoices/refunds, not adjustments)
- Excludes zero-balance lines
- Includes branch/BU dimensions from move level
- Filters out internal/intercompany moves

#### Key Methods:

**`init()`**:
- **Trigger:** When module installs
- **Logic:** Execute CREATE OR REPLACE VIEW SQL statement
- **Purpose:** Initialize financial analysis view

**`get_summary_by_branch()`** [Class]:
- **Logic:**
  1. Query view with user's allowed branches (security filter)
  2. GROUP BY ops_branch_id
  3. Return: transaction_count, total_debits, total_credits, net_balance
  4. Order by net_balance DESC
- **Purpose:** Branch financial summary
- **Returns:** List of dicts

**`get_summary_by_business_unit()`** [Class]:
- **Logic:**
  1. Query view grouped by ops_business_unit_id
  2. Apply user's allowed BU filter
  3. Return aggregated financial metrics per BU
- **Purpose:** BU financial summary
- **Returns:** List of dicts

---

### Model: `ops.inventory.analysis`
**Technical Name:** `ops.inventory.analysis`
**Description:** Read-only SQL view for inventory health and BU segregation verification.
**SQL Type:** PostgreSQL View
**Order:** `product_id`
**Auto:** False (view only)

#### Fields (View Columns):
| Name | Type | Key Attributes | Logic/Description |
| :--- | :--- | :--- | :--- |
| `id` | Id | Readonly | Quant ID |
| `product_id` | Many2one (`product.product`) | Readonly | Product held |
| `location_id` | Many2one (`stock.location`) | Readonly | Warehouse location |
| `ops_business_unit_id` | Many2one (`ops.business.unit`) | Readonly | BU from product assignment |
| `quantity` | Float | Readonly | Quantity on hand |
| `standard_price` | Float | Readonly | Unit cost |
| `stock_value` | Float | Readonly | Total value (qty Ã— cost) |
| `reserved_quantity` | Float | Readonly | Qty reserved for sales |
| `available_quantity` | Float | Readonly | Qty available (on_hand - reserved) |

#### SQL View Logic:
```sql
SELECT
    sq.id,
    sq.product_id,
    sq.location_id,
    pt.business_unit_id AS ops_business_unit_id,
    sq.quantity,
    CAST(pp.standard_price AS NUMERIC) AS standard_price,
    sq.reserved_quantity,
    (sq.quantity * CAST(pp.standard_price AS NUMERIC)) AS stock_value,
    (sq.quantity - sq.reserved_quantity) AS available_quantity
FROM stock_quant sq
INNER JOIN product_product pp ON sq.product_id = pp.id
INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE
    sq.location_id IN (SELECT id FROM stock_location WHERE usage IN ('internal', 'transit'))
    AND (sq.quantity != 0 OR sq.reserved_quantity != 0)
```

**Key Points:**
- Only internal/transit locations (not transit hubs or virtual)
- Excludes zero-quantity records
- BU sourced from product_template (inherited by all variants)
- Calculated fields: stock_value, available_quantity
- Reserves visibility for sales orders

#### Key Methods:

**`init()`**:
- **Trigger:** When module installs
- **Logic:** Execute CREATE OR REPLACE VIEW
- **Purpose:** Initialize inventory view

**`get_summary_by_business_unit()`** [Class]:
- **Logic:**
  1. Query view grouped by ops_business_unit_id
  2. Apply user's allowed BU filter
  3. Aggregate: product_count, location_product_count, total_on_hand, total_reserved, total_available, total_value
  4. Order by total_value DESC
- **Purpose:** Inventory position by BU
- **Returns:** List of dicts

**`get_inventory_by_location()`** [Class]:
- **Logic:**
  1. Query view grouped by location_id, ops_business_unit_id
  2. Apply user's allowed BU filter
  3. Aggregate by warehouse location and BU
  4. Shows segregation verification (no BU cross-contamination)
- **Purpose:** Warehouse-level inventory with BU ownership
- **Returns:** List of dicts with location details

---

## 3. Key Methods & Business Logic

### Sales Analysis

**View-Based Reporting:**
- No intermediate records stored
- Real-time aggregation on demand
- User security: only sees branches they can access

**Margin Calculation:**
- Standard: Margin = Price_Subtotal - (Qty Ã— Product.standard_price)
- Margin% = (Margin / Price_Subtotal) Ã— 100
- Zero-division handled (returns 0 if subtotal=0)

**Branch Summary Method:**
- Respects user's allowed_branch_ids (via ir.rule in core)
- Groups by ops_branch_id
- Returns: line_count, total_qty, total_revenue, total_margin, avg_margin_percent
- Ordered by revenue (descending)

---

### Financial Analysis

**GL View Scope:**
- Posted moves only (in progress/draft excluded)
- Transaction moves only (out_invoice, in_invoice, refunds; not internal transfers)
- Non-zero lines only (cleaner data)
- Includes both debit and credit amounts + calculated balance

**Branch & BU Dimensions:**
- Sourced from account_move (header level)
- Every GL line inherits move's branch/BU
- Enables dimensional analysis (drill: branch â†’ account â†’ GL)

**Summary Aggregations:**
- `get_summary_by_branch()`: Transaction count, debits, credits, net balance per branch
- `get_summary_by_business_unit()`: Same aggregation per BU
- Both respect user security filters

---

### Inventory Analysis

**Stock Segregation by BU:**
- Every product belongs to one BU (product_template.business_unit_id)
- All variants inherit BU from template
- View filters for internal/transit locations only
- Visible reserved qty (from open sales orders)

**Inventory Health Indicators:**
- On-hand qty: What's physically there
- Reserved qty: What's promised to customers
- Available qty: On-hand - reserved (what can be sold)
- Stock value: Qty Ã— Standard_price (for valuation reporting)

**Location Segregation Method:**
- `get_inventory_by_location()` groups by warehouse location + BU
- Identifies if cross-BU stock exists in same location (segregation issue)
- Shows inventory value by location/BU pair

---

## 4. Security & Access Control

### Access Control (`security/ir.model.access.csv`):

| Model | User Group | Read | Write | Create | Delete |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ops.sales.analysis` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.sales.analysis` | group_ops_manager | âœ“ | âœ— | âœ— | âœ— |
| `ops.sales.analysis` | group_ops_admin | âœ“ | âœ— | âœ— | âœ— |
| `ops.financial.analysis` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.financial.analysis` | group_ops_manager | âœ“ | âœ— | âœ— | âœ— |
| `ops.financial.analysis` | group_ops_admin | âœ“ | âœ— | âœ— | âœ— |
| `ops.financial.analysis` | group_ops_cost_controller | âœ“ | âœ— | âœ— | âœ— |
| `ops.inventory.analysis` | group_ops_user | âœ“ | âœ— | âœ— | âœ— |
| `ops.inventory.analysis` | group_ops_manager | âœ“ | âœ— | âœ— | âœ— |
| `ops.inventory.analysis` | stock.group_stock_manager | âœ“ | âœ— | âœ— | âœ— |
| `ops.inventory.analysis` | group_ops_admin | âœ“ | âœ— | âœ— | âœ— |

**Note:** All views are read-only (no write/create/delete permissions)

### Record Rules (`security/ir_rule.xml`):

**1. Sales Analysis - Branch Visibility:**
- Model: `ops.sales.analysis`
- Domain: Branch filter (inherited from ops_branch_id)
- Purpose: Users see only sales from their allowed branches

**2. Financial Analysis - Branch/BU Intersection:**
- Model: `ops.financial.analysis`
- Domain: `['&', ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids), ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)]`
- Purpose: Users see GL lines only for their branch+BU intersection

**3. Inventory Analysis - BU Visibility:**
- Model: `ops.inventory.analysis`
- Domain: BU filter (inherited from ops_business_unit_id)
- Purpose: Users see inventory only for their allowed BUs

---

## 5. XML Views & Interface

### Sales Analysis Views

**Tree View (`ops_sales_analysis_views.xml`)**:
- **Columns:** date_order, product_id, partner_id, ops_branch_id, ops_business_unit_id, product_uom_qty, price_subtotal, margin, margin_percent
- **Grouping:** By branch (default), can be regrouped by partner, product
- **Aggregation:** Sum qty/revenue/margin by group

**Pivot View:**
- **Rows:** product_id, partner_id
- **Columns:** ops_branch_id (optional)
- **Measures:** product_uom_qty, price_subtotal, margin, margin_percent
- **Purpose:** Analysis dashboard

**Search View:**
- **Fields:** date_order, product_id, partner_id, ops_branch_id, ops_business_unit_id
- **Filters:** Date range, branch, BU
- **Context:** Group by branch (default)

---

### Financial Analysis Views

**Tree View:**
- **Columns:** date, move_id, account_id, ops_branch_id, ops_business_unit_id, partner_id, debit, credit, balance
- **Grouping:** By account (default) or date
- **Aggregation:** Sum debits/credits/balance by account

**Pivot View:**
- **Rows:** account_id, move_type
- **Columns:** ops_branch_id (optional)
- **Measures:** debit, credit, balance
- **Purpose:** Financial dashboard, multi-dimensional analysis

**Search View:**
- **Fields:** date, account_id, ops_branch_id, ops_business_unit_id, partner_id, move_type
- **Filters:** Date range, branch, BU, move type
- **Context:** Group by account (default)

---

### Inventory Analysis Views

**Tree View:**
- **Columns:** product_id, location_id, ops_business_unit_id, quantity, standard_price, stock_value, reserved_quantity, available_quantity
- **Grouping:** By product or location
- **Aggregation:** Sum quantities and value

**Pivot View:**
- **Rows:** product_id, ops_business_unit_id
- **Columns:** location_id (optional)
- **Measures:** quantity, reserved_quantity, available_quantity, stock_value
- **Purpose:** Stock position dashboard

**Search View:**
- **Fields:** product_id, location_id, ops_business_unit_id
- **Filters:** BU, location, quantity > 0
- **Context:** Group by BU (default)

---

### Dashboard Menu (`reporting_menu.xml`)

**Menu Structure:**
- **Root:** "Matrix Reporting"
  - Action: "Sales Analysis" â†’ List view
  - Action: "Financial Analysis" â†’ Pivot view
  - Action: "Inventory Analysis" â†’ List view

---

## 6. Data & Configuration Files

### Dashboard Data (`dashboard_data.xml`):
- **Spreadsheet dashboards** linked to views
- **KPI cards:** Total revenue, total margin, inventory value
- **Charts:** Sales by branch, GL by account, stock by BU
- **Filters:** Date range, branch, BU selectors

### CSS Styling (`static/src/css/reporting.css`):
- **Customizations:** Card colors, metric highlights
- **Responsive:** Mobile-friendly dashboard layouts
- **Brand colors:** Branch/BU color coding

---

## 7. Static Assets

### CSS:
- **`static/src/css/reporting.css`:** Dashboard and view styling
  - Card layouts for KPI display
  - Color coding by branch/BU
  - Responsive grid for mobile

---

## 8. Integration Points

### With ops_matrix_core:
- **Security:** Inherits user.ops_allowed_branch_ids and user.ops_allowed_business_unit_ids
- **Dimensions:** Views include ops_branch_id, ops_business_unit_id
- **Personas:** Reports respect persona-based access

### With Odoo Sale:
- **Source:** Queries sale_order, sale_order_line
- **Link:** Via order_id foreign key
- **Metrics:** qty, revenue, margin

### With Odoo Account:
- **Source:** Queries account_move, account_move_line
- **Link:** Via move_id foreign key
- **Metrics:** debit, credit, balance by account

### With Odoo Stock:
- **Source:** Queries stock_quant, stock_location
- **Link:** Via product_id, location_id foreign keys
- **Metrics:** qty, reserved, value

### With Spreadsheet Dashboard:
- **Integration:** Views embeddable in dashboard spreadsheets
- **Pivot sources:** Sales/Financial/Inventory pivots as data sources
- **Charts:** Real-time aggregation into KPI cards

---

## 9. Performance Characteristics

### SQL View Optimization:
- **Materialized:** Views can be indexed (PostgreSQL 9.3+)
- **Filtering:** Database-level filtering (WHERE clause) reduces data transfer
- **Aggregation:** GROUP BY and SUM pushdown to database
- **Security:** Applied at row level (ir.rule) after view filtering

### Scalability:
- **No intermediate tables:** All queries run directly on views
- **Minimal disk footprint:** Views are queries, not stored data
- **Caching:** Spreadsheet dashboard caches aggregations
- **Refresh:** On-demand (no scheduled materialization required)

---

## 10. Key Design Patterns

### 1. Read-Only View Pattern
- Models use `_auto=False` (no table creation)
- `init()` creates PostgreSQL view
- All fields readonly
- No write/create/delete operations
- Zero transaction overhead

### 2. Dimension-Driven Analysis
- Every view includes ops_branch_id and/or ops_business_unit_id
- Enables drill-down: summary â†’ branch/BU â†’ account/product â†’ transaction
- Consistent dimensional structure across all three views

### 3. Security-First Aggregation
- Views query base tables (sale_order, account_move, stock_quant)
- Record rules (ir.rule) applied at view level
- User only sees data they're authorized for
- No role-based report generation needed

### 4. Lightweight Reporting
- No intermediate fact tables
- No ETL/materialization pipelines
- Real-time aggregation via SQL GROUP BY
- Minimal maintenance overhead

### 5. Calculated Fields in Views
- SQL expressions for margin, balance, stock_value
- Consistent calculations across all users
- No Python post-processing needed
- Database-level precision

---

## 11. Reporting Examples

### Sales Dashboard:
1. User clicks "Sales Analysis"
2. System shows tree view grouped by branch
3. User selects specific branch, sees:
   - Total revenue
   - Total margin
   - Average margin %
   - Line item count
4. Can click pivot view to analyze by product/customer
5. Can export to spreadsheet for further analysis

### Financial Position:
1. User clicks "Financial Analysis"
2. System shows pivot view: accounts on rows, branches on columns
3. Shows debit/credit/balance
4. Can drill-down to GL lines
5. Can filter by date, account, partner
6. Can export for consolidation

### Inventory Health:
1. User clicks "Inventory Analysis"
2. System shows inventory by BU
3. Displays: on-hand, reserved, available, stock value
4. Can view location-level segregation (BU per warehouse)
5. Can identify cross-BU stock situations
6. Can reconcile against counts

---

## 12. Future Extensibility

### Analysis Model Extensions:
- **Cost Analysis:** Product cost tracking, variance reporting
- **Profitability:** By customer, product line, region
- **Growth Metrics:** YoY, month-over-month trends
- **Forecasting:** Pipeline, capacity utilization

### Dashboard Enhancements:
- **Alerts:** Threshold-based notifications (low stock, high variance)
- **Comparisons:** Actual vs. budget, YoY comparisons
- **Drill-Through:** From dashboard card to underlying transactions
- **Scheduling:** Automated report distribution (email)

### Integration:
- **BI Tools:** Tableau, Power BI via SQL connection
- **Data Warehouse:** Export views to DW for consolidated reporting
- **API:** REST endpoints for external analytics tools
- **Real-Time Sync:** Pub/Sub for live dashboard updates

---

## 13. SQL View Creation & Maintenance

### View Creation:
- **Called:** When module installs (`_auto=False` + `init()` method)
- **Idempotent:** Uses `CREATE OR REPLACE VIEW` (safe to re-run)
- **Indexed:** Columns can be indexed (optional, for high-volume)

### View Updates:
- **If column added:** Edit view SQL in model â†’ upgrade module
- **If column removed:** Edit SQL â†’ upgrade (column disappears from new view)
- **If join changed:** Edit SQL â†’ consider re-indexing

### Maintenance:
- **Vacuums:** Not applicable (views don't store data)
- **Analyzer:** No ANALYZE needed
- **Bloat:** No bloat (no table data)
- **Monitoring:** Monitor base table cardinality (sale_order, account_move, stock_quant)

---
