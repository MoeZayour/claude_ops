# OPS Matrix Framework Architecture

> Version: 19.0 | Last Updated: Phase 20

## Overview

The OPS Matrix Framework is a multi-dimensional enterprise management system built on Odoo 19. It provides:

- **Matrix Organization**: Branch + Business Unit dual-dimension tracking
- **Security Isolation**: Role-based access with branch-level data segregation
- **Financial Reporting**: Executive-grade PDF reports with wkhtmltopdf
- **Asset Management**: Fixed asset tracking with depreciation schedules

---

## Module Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                     OPS MATRIX FRAMEWORK                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               ops_matrix_core (Foundation)                │  │
│  │  • Branch/BU Structure    • Personas/Delegations         │  │
│  │  • Matrix Mixin           • Approval Workflows           │  │
│  │  • Security Framework     • SLA Management               │  │
│  │  • Governance Rules       • Audit Logging                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐    ┌──────────────────┐   ┌────────────────┐ │
│  │ ops_matrix_ │    │  ops_matrix_     │   │ ops_matrix_    │ │
│  │ accounting  │    │  reporting       │   │ asset_mgmt     │ │
│  │             │    │                  │   │                │ │
│  │ • Budgets   │    │ • Dashboards     │   │ • Assets       │ │
│  │ • PDC       │    │ • Analytics      │   │ • Depreciation │ │
│  │ • Reports   │    │ • KPIs           │   │ • Disposal     │ │
│  │ • Snapshots │    │ • Trends         │   │                │ │
│  └─────────────┘    └──────────────────┘   └────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            External Dependencies (READ-ONLY)              │  │
│  │  • oca_reporting_engine    • report_xlsx                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Module (ops_matrix_core)

### Purpose
Foundation module providing organizational structure, security, and shared functionality for all OPS modules.

### Key Models

| Model | Technical Name | Purpose |
|-------|----------------|---------|
| **Branch** | `ops.branch` | Physical/logical organizational unit |
| **Business Unit** | `ops.business.unit` | Cross-branch operational division |
| **Persona** | `ops.persona` | Role-based identity with permissions |
| **Matrix Mixin** | `ops.matrix.mixin` | Branch/BU tracking for transactions |
| **Approval Request** | `ops.approval.request` | Multi-level approval workflow |
| **Governance Rule** | `ops.governance.rule` | Business rule enforcement |
| **SLA Template** | `ops.sla.template` | Service level definitions |
| **Audit Log** | `ops.audit.log` | Change tracking |

### The Matrix Mixin

The `ops.matrix.mixin` is the cornerstone of the framework. It provides:

```python
class OpsMatrixMixin(models.AbstractModel):
    _name = 'ops.matrix.mixin'

    # Core dimension fields
    ops_branch_id = fields.Many2one('ops.branch')
    ops_business_unit_id = fields.Many2one('ops.business.unit')
    ops_company_id = fields.Many2one('res.company', compute='_compute_ops_company')
    ops_persona_id = fields.Many2one('ops.persona')
    ops_analytic_distribution = fields.Json(compute='_compute_analytic_distribution')

    # Key methods
    def _get_branch_domain(self)        # Get user's allowed branches
    def _apply_branch_filter(domain)    # Add branch filter to search
    def _check_branch_access(self)      # Verify branch permissions
    def _propagate_matrix_to_lines()    # Copy dimensions to child records
```

### Security Groups

| Group | Technical ID | Purpose |
|-------|--------------|---------|
| **Matrix User** | `group_ops_matrix_user` | Basic access |
| **Branch Manager** | `group_ops_branch_manager` | Manage single branch |
| **BU Leader** | `group_ops_bu_leader` | Manage business unit |
| **Cross-Branch BU** | `group_ops_cross_branch_bu_leader` | Multi-branch BU access |
| **Matrix Admin** | `group_ops_matrix_admin` | Full system access |

---

## Accounting Module (ops_matrix_accounting)

### Purpose
Enterprise accounting extensions with branch-aware financial reporting and asset management.

### Key Models

| Model | Technical Name | Purpose |
|-------|----------------|---------|
| **Budget** | `ops.budget` | Budget planning and tracking |
| **Budget Line** | `ops.budget.line` | Individual budget items |
| **PDC (Post-Dated Check)** | `ops.pdc` | Check management with states |
| **Matrix Snapshot** | `ops.matrix.snapshot` | Financial data snapshots |
| **Financial Report Wizard** | `ops.financial.report.wizard` | Report generation |

### Financial Reports

| Report | Type | Features |
|--------|------|----------|
| **Profit & Loss** | `pl` | Income, Expenses, Net Profit, Margin |
| **Balance Sheet** | `bs` | Assets, Liabilities, Equity |
| **Trial Balance** | `tb` | Debit/Credit verification |
| **Cash Flow** | `cf` | Inflows, Outflows, Net |
| **Aged Balance** | `aged` | Partner aging analysis |
| **General Ledger** | `gl` | Transaction details |

### Report Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION FLOW                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. WIZARD                 2. PARSER                         │
│  ┌─────────────────┐       ┌─────────────────┐              │
│  │ User Parameters │  ───▶ │ _get_report_data│              │
│  │ • date_from     │       │ • _read_group   │              │
│  │ • date_to       │       │ • aggregations  │              │
│  │ • branch_ids    │       │ • calculations  │              │
│  │ • report_type   │       └────────┬────────┘              │
│  └─────────────────┘                │                        │
│                                     ▼                        │
│  3. TEMPLATE                 4. PDF                          │
│  ┌─────────────────┐       ┌─────────────────┐              │
│  │ QWeb Template   │  ───▶ │ wkhtmltopdf     │              │
│  │ • Table layout  │       │ • A4 Format     │              │
│  │ • Hex colors    │       │ • Margins       │              │
│  │ • System fonts  │       │ • Print colors  │              │
│  └─────────────────┘       └─────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Report Templates Architecture

### Layout Inheritance

```
web.html_container
    └── ops_matrix_accounting.ops_external_layout
            └── ops_matrix_accounting.ops_report_styles (CSS)
                    └── Your Report Template
```

### Key Templates

| Template | Purpose |
|----------|---------|
| `ops_report_styles` | Master CSS for all reports |
| `ops_external_layout` | Wrapper with styles included |
| `ops_minimal_layout` | No external header/footer |
| `ops_report_header_template` | Standard report header |
| `ops_info_box_template` | Report metadata box |
| `ops_report_footer_template` | Standard page footer |

### CSS Class System

| Class Pattern | Purpose | Example |
|---------------|---------|---------|
| `.ops-cover-*` | Cover page elements | `.ops-cover-page` |
| `.ops-kpi-*` | KPI cards | `.ops-kpi-card`, `.ops-kpi-value` |
| `.ops-section-*` | Section blocks | `.ops-section-header-bar` |
| `.ops-data-table` | Data tables | `table.ops-data-table` |
| `.ops-value-*` | Value coloring | `.ops-value-positive` |
| `.ops-summary-*` | Summary boxes | `.ops-summary-box` |
| `.ops-status-*` | Status indicators | `.ops-status-pill` |

---

## Data Aggregation Patterns

### Using _read_group

```python
# Aggregate by account
results = self.env['account.move.line']._read_group(
    domain=[
        ('date', '>=', date_from),
        ('date', '<=', date_to),
        ('parent_state', '=', 'posted'),
    ],
    groupby=['account_id'],
    aggregates=['debit:sum', 'credit:sum'],
)

# Process results
for account, debit_sum, credit_sum in results:
    balance = debit_sum - credit_sum
    # ...
```

### Branch-Aware Queries

```python
# Apply branch filter
base_domain = [('state', '=', 'posted')]
domain = self._apply_branch_filter(base_domain)

# Or manually
domain = [
    ('ops_branch_id', 'in', self.env.user.ops_allowed_branch_ids.ids),
    ('state', '=', 'posted'),
]
```

---

## Integration Points

### Standard Odoo Models Extended

| Model | Extension | Purpose |
|-------|-----------|---------|
| `res.company` | OPS fields | Branch relationship |
| `res.users` | Persona, branches | User permissions |
| `sale.order` | Matrix mixin | Branch/BU tracking |
| `purchase.order` | Matrix mixin | Branch/BU tracking |
| `account.move` | Matrix mixin | Branch/BU tracking |
| `stock.picking` | Matrix mixin | Branch/BU tracking |

### Event Hooks

```python
# Post-init hook for module setup
def post_init_hook(env):
    # Initialize default data
    pass

# Uninstall hook for cleanup
def uninstall_hook(env):
    # Remove custom data
    pass
```

---

## Configuration

### Matrix Config Model

```python
config = self.env['ops.matrix.config'].get_config()

# Available settings
config.branch_weight           # % for branch in distribution
config.bu_weight               # % for BU in distribution
config.default_branch_id       # Default branch for new records
config.require_branch          # Enforce branch on transactions
```

---

## Best Practices

### 1. Model Creation

```python
# Always inherit the mixin
class OpsNewModel(models.Model):
    _name = 'ops.new.model'
    _inherit = ['ops.matrix.mixin']
```

### 2. Search Operations

```python
# Always filter by branch
records = self.env['ops.model'].search(
    self._apply_branch_filter([('state', '=', 'active')])
)
```

### 3. Report Data

```python
# Use _read_group for aggregations
# Never loop over large recordsets
data = self.env['model']._read_group(domain, groupby, aggregates)
```

### 4. Template Layout

```xml
<!-- Use tables, not flexbox -->
<table style="width: 100%;">
    <tr>
        <td style="width: 50%;">Left</td>
        <td style="width: 50%;">Right</td>
    </tr>
</table>
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty report | No data matches filters | Check date range, branch filter |
| Colors missing in PDF | Missing print-color-adjust | Add `-webkit-print-color-adjust: exact` |
| Layout broken in PDF | Using flexbox/grid | Convert to table-based layout |
| Access denied | Branch not in user's list | Add branch to user permissions |
| Performance slow | Looping over records | Use `_read_group` |

### Debug Commands

```bash
# Check module state
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
m = self.env['ir.module.module'].search([('name', 'like', 'ops_matrix%')])
for x in m: print(f"{x.name}: {x.state}")
PYTHON

# View recent errors
docker logs gemini_odoo19 --tail 100 | grep -i error
```

---

## Version Compatibility

| Component | Version |
|-----------|---------|
| Odoo | 19.0 |
| Python | 3.10+ |
| PostgreSQL | 14+ |
| wkhtmltopdf | 0.12.6+ |
