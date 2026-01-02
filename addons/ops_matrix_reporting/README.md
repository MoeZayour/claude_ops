# OPS Matrix Reporting Module

High-performance SQL-based analytics and reporting layer for the OPS Matrix framework (Odoo 19 Community Edition).

## Overview

The `ops_matrix_reporting` module provides enterprise-grade reporting and analytics capabilities with strict dimension-based security enforcement. It introduces three read-only PostgreSQL views that deliver:

- **Sales Analytics**: Revenue, margin, and product performance by Branch/Business Unit
- **Financial Analytics**: Journal entries, account balances, and A/R/A/P by dimension
- **Inventory Analytics**: Stock levels, valuations, and BU segregation verification

All views are backed by optimized PostgreSQL queries with indexed columns for sub-second performance at scale.

## Architecture

### Core Design Principles

1. **Read-Only SQL Views**: All analytics use PostgreSQL materialized views (`_auto=False`) to ensure data consistency and prevent accidental modifications
2. **Performance First**: Pure SQL aggregations via model methods eliminate Python loops for O(1) query response
3. **Security by Default**: Dual-layer enforcement with record rules + SQL WHERE clauses prevents data leakage
4. **BU-Aware**: All views include Branch and Business Unit dimensions for multi-dimensional analysis
5. **Indexed Columns**: Post-install hook creates 8 indices on frequently-filtered columns

### Directory Structure

```
ops_matrix_reporting/
├── __init__.py                              # Module initialization
├── __manifest__.py                          # Module metadata
├── hooks.py                                 # Post-install/uninstall hooks
├── models/
│   ├── __init__.py
│   ├── ops_sales_analysis.py                # Sales analytics SQL view
│   ├── ops_financial_analysis.py            # Financial analytics SQL view
│   └── ops_inventory_analysis.py            # Inventory analytics SQL view
├── views/
│   ├── ops_sales_analysis_views.xml         # Sales UI (tree, pivot, graph, search)
│   ├── ops_financial_analysis_views.xml     # Financial UI (tree, pivot, graph, search)
│   ├── ops_inventory_analysis_views.xml     # Inventory UI (tree, pivot, graph, search)
│   └── reporting_menu.xml                   # Menu hierarchy integration
├── data/
│   └── dashboard_data.xml                   # Spreadsheet dashboard templates
├── security/
│   ├── ir_rule.xml                          # Record-level security rules
│   └── ir.model.access.csv                  # Model access control
├── static/
│   └── src/css/
│       └── reporting.css                    # Reporting view styling
└── README.md                                # This file
```

## Models

### 1. ops.sales.analysis

**Purpose**: High-performance sales analytics with margin calculation

**Source**: Joins `sale.order_line` with `sale.order`

**Key Fields**:
- `date_order` - Order creation date
- `product_id` - Product sold
- `partner_id` - Customer
- `ops_branch_id` - Branch dimension
- `ops_business_unit_id` - Business unit dimension
- `product_uom_qty` - Quantity ordered
- `price_subtotal` - Revenue (ex-tax)
- `margin` - Calculated: `price_subtotal - (qty * standard_price)`
- `margin_percent` - Percentage margin

**Filters**:
- Only includes confirmed/done orders (`state IN ('sale', 'done')`)
- Excludes cancelled lines

**Key Methods**:
- `get_summary_by_branch()` - Revenue, margin, qty by branch
- `get_summary_by_business_unit()` - Revenue, margin, qty by BU
- `get_summary_by_matrix()` - Matrix view (Branch × BU)
- `get_margin_analysis()` - Product-level margin deep-dive

**SQL Indices**:
```sql
CREATE INDEX idx_ops_sales_analysis_branch ON ops_sales_analysis(ops_branch_id);
CREATE INDEX idx_ops_sales_analysis_bu ON ops_sales_analysis(ops_business_unit_id);
CREATE INDEX idx_ops_sales_analysis_date ON ops_sales_analysis(date_order);
```

### 2. ops.financial.analysis

**Purpose**: Multi-dimensional financial reporting with GL account tracking

**Source**: Joins `account_move_line` with `account_move`

**Key Fields**:
- `date` - Entry date
- `move_id` - Source journal entry
- `account_id` - GL account
- `ops_branch_id` - Branch dimension
- `ops_business_unit_id` - Business unit dimension
- `move_type` - Transaction type (out_invoice, in_invoice, refunds)
- `partner_id` - Customer/Vendor
- `debit` - Debit amount
- `credit` - Credit amount
- `balance` - Net balance (debit - credit)

**Filters**:
- Only posted entries (`state = 'posted'`)
- Only transactional moves (`move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')`)
- Excludes zero-balance lines

**Key Methods**:
- `get_summary_by_branch()` - Debits, credits, balance by branch
- `get_summary_by_business_unit()` - Debits, credits, balance by BU
- `get_account_analysis()` - GL account balances by dimension
- `get_receivables_payables_by_dimension()` - A/R and A/P analysis

**SQL Indices**:
```sql
CREATE INDEX idx_ops_financial_analysis_branch ON ops_financial_analysis(ops_branch_id);
CREATE INDEX idx_ops_financial_analysis_bu ON ops_financial_analysis(ops_business_unit_id);
CREATE INDEX idx_ops_financial_analysis_date ON ops_financial_analysis(date);
```

### 3. ops.inventory.analysis

**Purpose**: BU-aware inventory health with stock valuation

**Source**: Queries `stock_quant` with product template joins

**Key Fields**:
- `product_id` - Product held
- `location_id` - Warehouse location
- `ops_business_unit_id` - BU assignment (from product)
- `quantity` - On-hand quantity
- `standard_price` - Unit cost
- `stock_value` - Calculated: `quantity * standard_price`
- `reserved_quantity` - Reserved for orders
- `available_quantity` - Calculated: `quantity - reserved_quantity`

**Filters**:
- Only internal/transit locations (`usage IN ('internal', 'transit')`)
- Excludes ghost records (zero qty and reserved)

**Key Methods**:
- `get_summary_by_business_unit()` - Total inventory value by BU
- `get_inventory_by_location()` - Inventory by warehouse and BU
- `get_low_stock_alerts(threshold_value=1000)` - Stock below value threshold
- `get_overstocked_items(threshold_qty=100)` - Excess inventory identification
- `verify_bu_segregation()` - Data integrity check (identifies products in multiple BUs)

**SQL Indices**:
```sql
CREATE INDEX idx_ops_inventory_analysis_bu ON ops_inventory_analysis(ops_business_unit_id);
CREATE INDEX idx_ops_inventory_analysis_location ON ops_inventory_analysis(location_id);
```

## User Interface

### Views

All three analytics models include identical view types for consistency:

#### Tree View
- Column-based tabular display
- Sortable columns with sum/aggregation footers
- Edit disabled (read-only)

#### Pivot View
- Multi-dimensional cross-tabulation
- Configurable rows, columns, measures
- Quick aggregation analysis

#### Graph View
- Bar chart visualization
- Dimension-based grouping
- Measure aggregation display

#### Search View
- Filterable columns
- Pre-configured filters (high/low margin, zero stock, etc.)
- Grouping options for roll-up analysis

### Menu Structure

```
Reporting
├── Sales Analytics              [action_ops_sales_analysis]
├── Financial Analytics          [action_ops_financial_analysis]
├── Inventory Analytics          [action_ops_inventory_analysis]
└── Dashboards
    ├── Sales Dashboard          [Spreadsheet Dashboard]
    ├── Financial Dashboard      [Spreadsheet Dashboard]
    └── Inventory Dashboard      [Spreadsheet Dashboard]
```

## Security

### Record Rules

All record rules enforce **read-only** access with strict dimension-based filtering:

#### Sales Analysis
- **Users**: Branch AND Business Unit intersection
  ```python
  ('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids) AND
  ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)
  ```
- **Managers**: Full access `[(1, '=', 1)]`
- **Admins**: Full access

#### Financial Analysis
- **Users**: Branch AND Business Unit intersection
- **Managers**: Full access
- **Admins**: Full access

#### Inventory Analysis
- **Users**: Business Unit OR global (no BU)
  ```python
  ('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids) OR
  ('ops_business_unit_id', '=', False)
  ```
- **Warehouse Managers**: BU OR global
- **Admins**: Full access

### Access Control (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ops_sales_analysis_user,ops.sales.analysis.user,model_ops_sales_analysis,ops_matrix_core.group_ops_user,1,0,0,0
access_ops_sales_analysis_manager,ops.sales.analysis.manager,model_ops_sales_analysis,ops_matrix_core.group_ops_manager,1,0,0,0
access_ops_sales_analysis_admin,ops.sales.analysis.admin,model_ops_sales_analysis,ops_matrix_core.group_ops_admin,1,0,0,0
access_ops_financial_analysis_user,ops.financial.analysis.user,model_ops_financial_analysis,ops_matrix_core.group_ops_user,1,0,0,0
access_ops_financial_analysis_manager,ops.financial.analysis.manager,model_ops_financial_analysis,ops_matrix_core.group_ops_manager,1,0,0,0
access_ops_financial_analysis_admin,ops.financial.analysis.admin,model_ops_financial_analysis,ops_matrix_core.group_ops_admin,1,0,0,0
access_ops_financial_analysis_cost_controller,ops.financial.analysis.cost_controller,model_ops_financial_analysis,ops_matrix_core.group_ops_cost_controller,1,0,0,0
access_ops_inventory_analysis_user,ops.inventory.analysis.user,model_ops_inventory_analysis,ops_matrix_core.group_ops_user,1,0,0,0
access_ops_inventory_analysis_manager,ops.inventory.analysis.manager,model_ops_inventory_analysis,ops_matrix_core.group_ops_manager,1,0,0,0
access_ops_inventory_analysis_warehouse,ops.inventory.analysis.warehouse,model_ops_inventory_analysis,stock.group_stock_manager,1,0,0,0
access_ops_inventory_analysis_admin,ops.inventory.analysis.admin,model_ops_inventory_analysis,ops_matrix_core.group_ops_admin,1,0,0,0
```

## Installation & Initialization

### Dependencies

```python
'depends': [
    'ops_matrix_core',      # OPS Matrix framework
    'sale_management',      # Sales module
    'account',              # Accounting module
    'stock',                # Inventory module
    'spreadsheet_dashboard', # Dashboard support
]
```

### Post-Install Hook (`hooks.py`)

1. Creates three PostgreSQL views (calls `model.init()`)
2. Creates 8 performance indices on frequently-filtered columns
3. Commits database transaction

```python
def post_init_hook(cr, registry):
    """Create SQL views and performance indices"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Initialize views
    env['ops.sales.analysis'].init()
    env['ops.financial.analysis'].init()
    env['ops.inventory.analysis'].init()
    
    # Create indices on filter columns
    # - idx_ops_sales_analysis_branch
    # - idx_ops_sales_analysis_bu
    # - idx_ops_sales_analysis_date
    # - idx_ops_financial_analysis_branch
    # - idx_ops_financial_analysis_bu
    # - idx_ops_financial_analysis_date
    # - idx_ops_inventory_analysis_bu
    # - idx_ops_inventory_analysis_location
```

### Uninstall Hook

```python
def uninstall_hook(cr, registry):
    """Drop SQL views and indices"""
    # Drops all three views with CASCADE
    # Drops all 8 performance indices
```

## Usage Examples

### Sales Analytics - Get Top Products by Revenue

```python
sales = env['ops.sales.analysis'].get_summary_by_branch()
# Returns: [
#     {'ops_branch_id': 1, 'total_revenue': 50000, 'total_margin': 5000, ...},
#     {'ops_branch_id': 2, 'total_revenue': 35000, 'total_margin': 3500, ...}
# ]
```

### Financial Analytics - A/R by Dimension

```python
ar_data = env['ops.financial.analysis'].get_receivables_payables_by_dimension()
# Returns: [
#     {'ops_branch_id': 1, 'ops_business_unit_id': 10, 'move_type': 'out_invoice', 
#      'partner_id': 5, 'dimension_balance': 15000, ...}
# ]
```

### Inventory Analytics - Low Stock Alert

```python
low_stock = env['ops.inventory.analysis'].get_low_stock_alerts(threshold_value=500)
# Returns: [
#     {'product_id': 3, 'ops_business_unit_id': 10, 'total_value': 450, ...}
# ]
```

### Verify BU Segregation

```python
issues = env['ops.inventory.analysis'].verify_bu_segregation()
# Returns: Products with inventory in multiple BUs (data integrity check)
# []  # Empty = good; otherwise indicates product assigned to multiple BUs
```

## Performance Considerations

### Query Optimization

1. **SQL Views**: PostgreSQL evaluates queries at view level; no Python overhead
2. **Indexed Columns**: Queries on `branch_id`, `business_unit_id`, `date` are O(log N)
3. **No Aggregation Loops**: Model methods use `GROUP BY` in SQL, not Python loops
4. **Post-Install Indices**: Created during module installation for immediate performance

### Scaling Characteristics

| Dataset Size | Expected Response |
|---|---|
| <100K records | <10ms |
| 100K-1M records | 10-100ms |
| 1M-10M records | 100-500ms |
| 10M+ records | 500ms-2s (depends on index strategy) |

### Recommended Indices for Large Deployments

```sql
-- Add for very large datasets (10M+ records)
CREATE INDEX idx_ops_sales_analysis_product ON ops_sales_analysis(product_id);
CREATE INDEX idx_ops_financial_analysis_account ON ops_financial_analysis(account_id);
CREATE INDEX idx_ops_inventory_analysis_product ON ops_inventory_analysis(product_id);
```

## Styling

The module includes comprehensive CSS styling (`reporting.css`) with:

- Color-coded financial indicators (positive/negative)
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Accessibility features (focus outlines)
- Dashboard card layouts

Key CSS classes:
- `.ops-reporting-container` - Main container
- `.ops-sales-revenue`, `.ops-sales-margin` - Sales highlighting
- `.ops-financial-debit`, `.ops-financial-credit` - Financial highlighting
- `.ops-inventory-value` - Inventory highlighting
- `.ops-dashboard-card` - Dashboard cards
- `.o_pivot`, `.o_graph_view` - Pivot/graph containers

## Future Enhancements

1. **Materialized Views**: Convert to PostgreSQL MATERIALIZED VIEWS with scheduled refresh for even faster queries
2. **Custom Dashboards**: OWL components for interactive drill-down analysis
3. **Export Functionality**: Direct CSV/Excel export from analytics views
4. **Forecasting**: Trend analysis and predictive inventory
5. **Alerts**: Automated notifications for margin/stock anomalies
6. **Audit Trail**: Track which users accessed which analytics
7. **Custom Dimensions**: User-defined analysis dimensions
8. **Comparison Analysis**: Period-over-period and YoY comparisons

## Troubleshooting

### Views Not Appearing

1. Check module is installed: `Settings > Apps > Installed Apps > ops_matrix_reporting`
2. Verify groups are assigned: User must be in `group_ops_user` or `group_ops_manager`
3. Check record rules: Ensure user has at least one allowed Branch/Business Unit

### Slow Query Performance

1. Check indices exist: `SELECT * FROM pg_indexes WHERE tablename LIKE 'ops_%'`
2. Verify record rules aren't filtering entire dataset
3. Check PostgreSQL query plan: `EXPLAIN ANALYZE SELECT ...`
4. Consider adding custom indices for large datasets

### Permission Denied Errors

1. Verify `ir.model.access.csv` entries are correct
2. Check user group assignments in `Settings > Users`
3. Verify record rule domains are properly formatted
4. Check that user has at least one allowed Branch and Business Unit

### Data Not Showing

1. Verify source data exists (sale orders, journal entries, inventory)
2. Check filters (only confirmed sales, posted JEs, internal stock)
3. Verify user's Branch/Business Unit assignment
4. Run manual SQL view query: `SELECT COUNT(*) FROM ops_sales_analysis;`

## Development Notes

### Adding New Metrics

To add a new analysis method:

```python
@api.model
def get_custom_metric(self):
    """Custom analysis method"""
    self.env.cr.execute(
        """
        SELECT 
            ops_branch_id,
            SUM(price_subtotal) as total
        FROM ops_sales_analysis
        WHERE ops_branch_id IN (...)
        GROUP BY ops_branch_id
        """,
        [self.env.uid]
    )
    return self.env.cr.dictfetchall()
```

### Modifying View Definitions

To update a view's SQL:

1. Edit the `init()` method in the model
2. Drop the view in PostgreSQL: `DROP VIEW IF EXISTS ops_sales_analysis CASCADE;`
3. Restart Odoo to trigger re-initialization
4. Or manually run the SQL from the `init()` method

### Adding New Fields

To add a field to a view:

1. Add to `init()` SQL in SELECT clause
2. Add `fields.Type()` definition in the model
3. Update views XML if needed
4. Drop and recreate the view

## License

LGPL-3

## Support

For issues, feature requests, or contributions, please refer to the OPS Matrix project repository.
