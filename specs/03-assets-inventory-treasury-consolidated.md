# OPS Framework Financial Intelligence Reports
## Part 3 (Continued): Asset Intelligence & Part 4: Inventory & Treasury

---

## 📊 REPORT 10: Fixed Asset Register (Continued)

### Layout (Continued)

```
│  │ OFFICE EQUIPMENT                                                          │ │
│  │ Method: Straight Line | Useful Life: 5 years                              │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ FA-050  │ Server Room Equip. │ 12/04/21 │  28,000 │  16,800 │    11,200 │HQ │Active │ │
│  │ FA-051  │ Office Furniture   │ 12/04/21 │  15,200 │   9,120 │     6,080 │HQ │Active │ │
│  │ FA-052  │ IT Equipment       │ 08/09/22 │  12,500 │   5,000 │     7,500 │HQ │Active │ │
│  │ FA-053  │ Old Printer        │ 15/01/19 │   2,800 │   2,800 │         0 │HQ │F.Dep  │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Subtotal Office Equipment              │  58,500 │  33,720 │    24,780 │   │       │ │
│  │                                                                           │ │
│  │ MOTOR VEHICLES                                                            │ │
│  │ Method: Declining Balance | Useful Life: 5 years                          │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ FA-080  │ Delivery Van #1    │ 20/02/22 │  35,000 │  21,000 │    14,000 │WH1│Active │ │
│  │ FA-081  │ Company Car        │ 15/08/23 │  42,000 │  12,600 │    29,400 │HQ │Active │ │
│  │ FA-082  │ Old Truck (Sold)   │ 10/05/19 │  28,000 │  28,000 │         0 │— │Disposed│ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Subtotal Motor Vehicles                │ 105,000 │  61,600 │    43,400 │   │       │ │
│  │                                                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│  │ TOTAL ALL FIXED ASSETS                 │ 534,000 │ 158,870 │   375,130 │   │       │ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  SUMMARY BY STATUS                                                              │
│  ─────────────────                                                              │
│  Active Assets:           118 assets      Book Value:    372,850                │
│  Fully Depreciated:         6 assets      Book Value:          0                │
│  Disposed This Year:        3 assets      Proceeds:       12,500                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### QWeb Template Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <template id="ops_report_fixed_asset_register_document">
        <t t-call="web.external_layout">
            <div class="ops-financial-report ops-asset-register">
                
                <!-- Report Title Block -->
                <div class="ops-report-title-block">
                    <div class="ops-document-type">Capital Asset Inventory</div>
                    <h1 class="ops-report-title">FIXED ASSET REGISTER</h1>
                    <div class="ops-report-meta">
                        <span class="ops-period">
                            As at <t t-esc="doc.as_at_date.strftime('%d %B %Y')"/>
                        </span>
                    </div>
                </div>
                
                <!-- Summary Bar -->
                <div class="ops-asset-summary-bar">
                    <div class="ops-asset-kpi">
                        <span class="ops-kpi-label">Total Assets</span>
                        <span class="ops-kpi-value">
                            <t t-esc="doc.total_assets_count"/>
                        </span>
                    </div>
                    <div class="ops-asset-kpi">
                        <span class="ops-kpi-label">Total Cost</span>
                        <span class="ops-kpi-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_cost)"/>
                        </span>
                    </div>
                    <div class="ops-asset-kpi">
                        <span class="ops-kpi-label">Accum. Depreciation</span>
                        <span class="ops-kpi-value">
                            (<t t-esc="'{:,.0f}'.format(doc.total_accumulated_depreciation)"/>)
                        </span>
                    </div>
                    <div class="ops-asset-kpi ops-kpi-highlight">
                        <span class="ops-kpi-label">Net Book Value</span>
                        <span class="ops-kpi-value">
                            <t t-esc="'{:,.0f}'.format(doc.total_book_value)"/>
                        </span>
                    </div>
                </div>
                
                <!-- Asset Categories -->
                <t t-foreach="doc.categories" t-as="category">
                    <div class="ops-asset-category-block">
                        
                        <!-- Category Header -->
                        <div class="ops-asset-category-header">
                            <div class="ops-category-title">
                                <t t-esc="category.category_name.upper()"/>
                            </div>
                            <div class="ops-category-meta">
                                Method: <t t-esc="category.depreciation_method"/> | 
                                Useful Life: <t t-esc="category.useful_life_years"/> years
                            </div>
                        </div>
                        
                        <!-- Assets Table -->
                        <table class="ops-data-table ops-asset-table">
                            <thead>
                                <tr>
                                    <th class="ops-col-code">Code</th>
                                    <th class="ops-col-desc">Description</th>
                                    <th class="ops-col-date">Acquired</th>
                                    <th class="ops-col-amount">Cost</th>
                                    <th class="ops-col-amount">Accum Dep</th>
                                    <th class="ops-col-amount">Book Value</th>
                                    <th class="ops-col-loc">Loc</th>
                                    <th class="ops-col-status">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="category.assets" t-as="asset">
                                    <tr t-attf-class="ops-row-item #{('ops-row-disposed' if asset.status == 'Disposed' else 'ops-row-fully-dep' if asset.status == 'Fully Depreciated' else '')}">
                                        <td class="ops-col-code">
                                            <t t-esc="asset.asset_code"/>
                                        </td>
                                        <td class="ops-col-desc">
                                            <t t-esc="asset.asset_name"/>
                                        </td>
                                        <td class="ops-col-date">
                                            <t t-esc="asset.acquisition_date.strftime('%d/%m/%y')"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(asset.original_cost)"/>
                                        </td>
                                        <td class="ops-col-amount">
                                            <t t-esc="'{:,.0f}'.format(asset.accumulated_depreciation)"/>
                                        </td>
                                        <td class="ops-col-amount ops-col-book-value">
                                            <t t-if="asset.book_value > 0">
                                                <t t-esc="'{:,.0f}'.format(asset.book_value)"/>
                                            </t>
                                            <t t-else="">
                                                <span class="ops-value-zero">0</span>
                                            </t>
                                        </td>
                                        <td class="ops-col-loc">
                                            <t t-esc="asset.location"/>
                                        </td>
                                        <td t-attf-class="ops-col-status ops-status-#{asset.status.lower().replace(' ', '-')}">
                                            <t t-esc="asset.status"/>
                                        </td>
                                    </tr>
                                </t>
                            </tbody>
                            <tfoot>
                                <tr class="ops-row-subtotal">
                                    <td colspan="3" class="ops-col-label">
                                        Subtotal <t t-esc="category.category_name"/>
                                    </td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(category.subtotal_cost)"/>
                                    </td>
                                    <td class="ops-col-amount">
                                        <t t-esc="'{:,.0f}'.format(category.subtotal_accum_dep)"/>
                                    </td>
                                    <td class="ops-col-amount ops-col-book-value">
                                        <t t-esc="'{:,.0f}'.format(category.subtotal_book_value)"/>
                                    </td>
                                    <td colspan="2"></td>
                                </tr>
                            </tfoot>
                        </table>
                        
                    </div>
                </t>
                
                <!-- Grand Total -->
                <div class="ops-asset-grand-total">
                    <span class="ops-total-label">TOTAL ALL FIXED ASSETS</span>
                    <span class="ops-total-cost">
                        <t t-esc="'{:,.0f}'.format(doc.total_cost)"/>
                    </span>
                    <span class="ops-total-dep">
                        <t t-esc="'{:,.0f}'.format(doc.total_accumulated_depreciation)"/>
                    </span>
                    <span class="ops-total-nbv">
                        <t t-esc="'{:,.0f}'.format(doc.total_book_value)"/>
                    </span>
                </div>
                
            </div>
        </t>
    </template>
</odoo>
```

### Fixed Asset Register Specific CSS

```css
/* Fixed Asset Register Styles */
.ops-asset-summary-bar {
    display: flex;
    justify-content: space-between;
    padding: var(--space-4) var(--space-6);
    margin-bottom: var(--space-6);
    background-color: var(--ops-gray-100);
    border: 1px solid var(--ops-gray-300);
}

.ops-asset-kpi {
    text-align: center;
}

.ops-asset-kpi .ops-kpi-label {
    display: block;
    font-size: var(--text-xs);
    color: var(--ops-gray-600);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wide);
    margin-bottom: var(--space-1);
}

.ops-asset-kpi .ops-kpi-value {
    font-family: var(--font-display);
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--ops-black);
}

.ops-asset-kpi.ops-kpi-highlight {
    padding: var(--space-2) var(--space-4);
    background-color: var(--ops-black);
    margin: calc(-1 * var(--space-4)) calc(-1 * var(--space-6));
    margin-left: var(--space-4);
}

.ops-asset-kpi.ops-kpi-highlight .ops-kpi-label {
    color: var(--ops-gray-400);
}

.ops-asset-kpi.ops-kpi-highlight .ops-kpi-value {
    color: var(--ops-paper);
}

.ops-asset-category-block {
    margin-bottom: var(--space-6);
}

.ops-asset-category-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: var(--space-2) 0;
    border-bottom: var(--border-section);
    margin-bottom: var(--space-3);
}

.ops-category-title {
    font-size: var(--text-md);
    font-weight: 700;
    color: var(--ops-black);
    letter-spacing: var(--tracking-wide);
}

.ops-category-meta {
    font-size: var(--text-sm);
    color: var(--ops-gray-600);
}

/* Asset Table */
.ops-asset-table .ops-col-code {
    width: 60px;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
}

.ops-asset-table .ops-col-desc {
    width: auto;
}

.ops-asset-table .ops-col-date {
    width: 60px;
    font-size: var(--text-xs);
    text-align: center;
}

.ops-asset-table .ops-col-amount {
    width: 70px;
    text-align: right;
    font-family: var(--font-display);
}

.ops-asset-table .ops-col-book-value {
    background-color: var(--ops-gray-100);
    font-weight: 600;
}

.ops-asset-table .ops-col-loc {
    width: 35px;
    text-align: center;
    font-size: var(--text-xs);
    font-family: var(--font-mono);
}

.ops-asset-table .ops-col-status {
    width: 55px;
    text-align: center;
    font-size: var(--text-xs);
    font-weight: 600;
}

.ops-status-active { color: var(--ops-positive); }
.ops-status-fully-depreciated { color: var(--ops-gray-500); }
.ops-status-disposed { color: var(--ops-negative); }

.ops-row-disposed td { color: var(--ops-gray-500); text-decoration: line-through; }
.ops-row-fully-dep td { color: var(--ops-gray-500); font-style: italic; }

.ops-asset-grand-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-4) var(--space-6);
    background-color: var(--ops-black);
    color: var(--ops-paper);
    font-weight: 700;
}
```

---

## 📊 REPORT 11: Depreciation Schedule

### Report ID: `OPS-AST-002`
### Priority: High
### Category: Asset Intelligence Engine

---

### Purpose
Project future depreciation expenses for budgeting and financial forecasting.

### Data Requirements

```python
class DepreciationScheduleData:
    # Header Info
    company_name: str
    projection_start: date
    projection_months: int  # e.g., 12, 24, 36
    
    # Asset Data
    assets: List[AssetDepreciation]
    
    # Monthly Projections
    monthly_totals: List[MonthlyDepreciation]
    
    # Summary
    total_annual_depreciation: Decimal
    total_projected_depreciation: Decimal

class AssetDepreciation:
    asset_code: str
    asset_name: str
    category: str
    acquisition_date: date
    original_cost: Decimal
    current_book_value: Decimal
    monthly_depreciation: Decimal
    remaining_months: int
    monthly_schedule: List[Decimal]  # Amount per month

class MonthlyDepreciation:
    month: date
    land_buildings: Decimal
    machinery: Decimal
    equipment: Decimal
    vehicles: Decimal
    total: Decimal
```

### Layout: Monthly Projection Grid

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Future Expense Projection                                                      │
│  ═════════════════════════                                                      │
│  DEPRECIATION SCHEDULE                                                          │
│  12-Month Projection from January 2025                                          │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Annual Depreciation Expense (Projected):                        158,400   │ │
│  │ Monthly Average:                                                  13,200   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  MONTHLY PROJECTION BY CATEGORY                                                 │
│  ──────────────────────────────                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Month    │ Land/Bldg │Machinery│Equipment│ Vehicles │   TOTAL   │         │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Jan 2025 │    1,340  │  2,850  │  1,420  │   2,100  │    7,710  │         │ │
│  │ Feb 2025 │    1,340  │  2,850  │  1,420  │   2,100  │    7,710  │         │ │
│  │ Mar 2025 │    1,340  │  2,850  │  1,420  │   2,100  │    7,710  │         │ │
│  │ Apr 2025 │    1,340  │  2,850  │  1,420  │   2,100  │    7,710  │         │ │
│  │ May 2025 │    1,340  │  2,850  │  1,420  │   2,100  │    7,710  │         │ │
│  │ Jun 2025 │    1,340  │  2,850  │  1,420  │   2,100  │    7,710  │         │ │
│  │ Jul 2025 │    1,340  │  2,850  │  1,320  │   2,100  │    7,610  │ *       │ │
│  │ Aug 2025 │    1,340  │  2,850  │  1,320  │   2,100  │    7,610  │         │ │
│  │ Sep 2025 │    1,340  │  2,450  │  1,320  │   2,100  │    7,210  │ **      │ │
│  │ Oct 2025 │    1,340  │  2,450  │  1,320  │   2,100  │    7,210  │         │ │
│  │ Nov 2025 │    1,340  │  2,450  │  1,320  │   2,100  │    7,210  │         │ │
│  │ Dec 2025 │    1,340  │  2,450  │  1,320  │   2,100  │    7,210  │         │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTAL    │   16,080  │ 33,600  │ 16,440  │  25,200  │   91,320  │         │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  * FA-052 IT Equipment fully depreciated Jul 2025                               │
│  ** FA-016 Packaging Line fully depreciated Sep 2025                            │
│                                                                                 │
│  ASSETS EXPIRING IN PROJECTION PERIOD                                           │
│  ─────────────────────────────────────                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Asset     │ Description       │ End Date │ Final Book Value │ Action     │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ FA-052    │ IT Equipment      │ Jul 2025 │          0       │ Review     │ │
│  │ FA-016    │ Packaging Line    │ Sep 2025 │          0       │ Replace?   │ │
│  │ FA-053    │ Old Printer       │ Already  │          0       │ Dispose    │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 REPORT 12: CAPEX Analysis (YTD)

### Report ID: `OPS-AST-003`
### Priority: Medium
### Category: Asset Intelligence Engine

---

### Purpose
Track capital expenditure investments made during the year compared to budget.

### Data Requirements

```python
class CapexAnalysisData:
    # Header Info
    company_name: str
    year: int
    as_at_date: date
    
    # CAPEX by Category
    categories: List[CapexCategory]
    
    # Summary
    total_budget: Decimal
    total_actual: Decimal
    total_variance: Decimal
    variance_pct: Decimal
    committed_not_spent: Decimal

class CapexCategory:
    category_name: str
    budget: Decimal
    actual_ytd: Decimal
    committed: Decimal
    variance: Decimal
    variance_pct: Decimal
    acquisitions: List[CapexAcquisition]

class CapexAcquisition:
    asset_code: str
    description: str
    acquisition_date: date
    cost: Decimal
    po_reference: str
    vendor: str
    status: str  # 'Completed', 'In Progress', 'Pending'
```

### Layout: Budget vs Actual Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Capital Investment Analysis                                                    │
│  ═══════════════════════════                                                    │
│  CAPEX REPORT — YTD 2024                                                        │
│  As at 31 December 2024                                                         │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │          Budget        Actual       Committed      Variance               │ │
│  │         ━━━━━━━       ━━━━━━━━      ━━━━━━━━━     ━━━━━━━━━               │ │
│  │         150,000        98,500        22,000       +29,500 (19.7%)         │ │
│  │                                                                           │ │
│  │   ████████████████████████████████░░░░░░░░░░░░░░░░░░░░  65.7% Spent      │ │
│  │   ████████████████████████████████████████░░░░░░░░░░░░  80.3% Committed  │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  BREAKDOWN BY CATEGORY                                                          │
│  ─────────────────────                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Category             │ Budget  │ Actual  │Committed│ Variance │   Var %  │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Land & Buildings     │  50,000 │  45,200 │     —   │   +4,800 │   +9.6%  │ │
│  │ Machinery & Equip.   │  60,000 │  32,500 │  18,000 │   +9,500 │  +15.8%  │ │
│  │ Office Equipment     │  25,000 │  12,800 │   4,000 │   +8,200 │  +32.8%  │ │
│  │ Motor Vehicles       │  15,000 │   8,000 │     —   │   +7,000 │  +46.7%  │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTAL                │ 150,000 │  98,500 │  22,000 │  +29,500 │  +19.7%  │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ACQUISITIONS THIS YEAR                                                         │
│  ──────────────────────                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Date     │ Asset    │ Description       │    Cost │ PO Ref    │ Status   │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ 15 Feb   │ FA-095   │ New CNC Machine   │  32,500 │ PO-2024-12│ Complete │ │
│  │ 22 Mar   │ FA-096   │ Server Upgrade    │   8,400 │ PO-2024-18│ Complete │ │
│  │ 10 Jun   │ FA-097   │ Warehouse Ext.    │  45,200 │ PO-2024-25│ Complete │ │
│  │ 18 Sep   │ FA-098   │ Delivery Van      │   8,000 │ PO-2024-42│ Complete │ │
│  │ —        │ —        │ Assembly Robot    │  18,000 │ PO-2024-51│ Pending  │ │
│  │ —        │ —        │ Office Furniture  │   4,000 │ PO-2024-55│ Pending  │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 🏭 INVENTORY INTELLIGENCE ENGINE

---

## 📊 REPORT 13: Stock Valuation Report

### Report ID: `OPS-INV-001`
### Priority: High
### Category: Inventory Intelligence Engine

---

### Purpose
Show the current value of inventory by location, category, and valuation method.

### Data Requirements

```python
class StockValuationData:
    # Header Info
    company_name: str
    as_at_date: date
    valuation_method: str  # 'FIFO', 'Average', 'Standard'
    
    # By Location
    locations: List[LocationStock]
    
    # By Category
    categories: List[CategoryStock]
    
    # Summary
    total_quantity: Decimal
    total_value: Decimal
    average_unit_cost: Decimal

class LocationStock:
    location_name: str
    location_code: str
    products: List[ProductStock]
    subtotal_qty: Decimal
    subtotal_value: Decimal

class ProductStock:
    product_code: str
    product_name: str
    category: str
    uom: str
    quantity: Decimal
    unit_cost: Decimal
    total_value: Decimal
    last_movement_date: date
```

### Layout: Location-Based Inventory Grid

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Inventory Asset Report                                                         │
│  ══════════════════════                                                         │
│  STOCK VALUATION                                                                │
│  As at 31 December 2024                          Valuation Method: FIFO         │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Total Inventory Value:    485,200         Total SKUs: 342                 │ │
│  │ Average Unit Cost:          1,419         Total Qty: 12,450 units         │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │ WAREHOUSE A (WH-A) — Main Distribution                                    │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Code      │ Product             │ Cat.  │ UoM │  Qty   │ Unit $ │  Value  │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ PRD-001   │ Widget Alpha        │ FG    │ EA  │  1,250 │  12.50 │  15,625 │ │
│  │ PRD-002   │ Widget Beta         │ FG    │ EA  │    840 │  18.75 │  15,750 │ │
│  │ PRD-015   │ Component X-42      │ RM    │ KG  │  2,400 │   4.20 │  10,080 │ │
│  │ ...                                                                       │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Subtotal WH-A                           │  8,240 │        │ 285,400 │ │
│  │                                                                           │ │
│  │ WAREHOUSE B (WH-B) — Production                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ ...                                                                       │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Subtotal WH-B                           │  4,210 │        │ 199,800 │ │
│  │                                                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│  │ TOTAL ALL LOCATIONS                     │ 12,450 │        │ 485,200 │ │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 REPORT 14: Dead Stock Analysis

### Report ID: `OPS-INV-002`
### Priority: Medium
### Category: Inventory Intelligence Engine

---

### Purpose
Identify slow-moving and obsolete inventory items that haven't moved in 180+ days.

### Data Requirements

```python
class DeadStockData:
    # Header Info
    company_name: str
    as_at_date: date
    threshold_days: int  # Default 180
    
    # Dead Stock Items
    items: List[DeadStockItem]
    
    # Summary
    total_dead_stock_value: Decimal
    total_dead_stock_qty: int
    pct_of_total_inventory: Decimal
    
    # Recommendations
    write_off_candidates: List[DeadStockItem]
    clearance_candidates: List[DeadStockItem]

class DeadStockItem:
    product_code: str
    product_name: str
    category: str
    location: str
    quantity: Decimal
    unit_cost: Decimal
    total_value: Decimal
    last_movement_date: date
    days_since_movement: int
    recommendation: str  # 'Write-off', 'Clearance', 'Review', 'Return to Vendor'
```

### Layout: Risk-Prioritized Dead Stock

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Inventory Risk Analysis                                                        │
│  ═══════════════════════                                                        │
│  DEAD STOCK REPORT                                                              │
│  Items with No Movement > 180 Days                   As at 31 December 2024     │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │   Dead Stock Value       % of Inventory       Items Affected              │ │
│  │   ━━━━━━━━━━━━━━━━       ━━━━━━━━━━━━━━━     ━━━━━━━━━━━━━━               │ │
│  │       42,850                  8.8%                 28                     │ │
│  │                                                                           │ │
│  │   ⚠ WARNING: Dead stock exceeds 5% threshold. Action required.           │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  AGING BREAKDOWN                                                                │
│  ───────────────                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ 180-270 Days  │████████████████████████░░░░░░░░│  18,200 │ 42.5%│ 12 items│ │
│  │ 271-365 Days  │██████████████░░░░░░░░░░░░░░░░░░│  14,400 │ 33.6%│  9 items│ │
│  │ Over 1 Year   │██████████░░░░░░░░░░░░░░░░░░░░░░│  10,250 │ 23.9%│  7 items│ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  DETAIL — SORTED BY VALUE (HIGHEST FIRST)                                       │
│  ────────────────────────────────────────                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Code    │ Product           │ Loc │  Qty │ Value  │Days│ Recommendation   │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │ ▓ WRITE-OFF CANDIDATES (> 365 days, value < 1,000)                        │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ PRD-089 │ Obsolete Part A   │ WH-B│   45 │    580 │ 412│ Write-off        │ │
│  │ PRD-112 │ Discontinued Item │ WH-A│   22 │    340 │ 385│ Write-off        │ │
│  │                                                                           │ │
│  │ ▒ CLEARANCE CANDIDATES (180-365 days)                                     │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ PRD-045 │ Seasonal Product  │ WH-A│  120 │  4,800 │ 245│ Clearance Sale   │ │
│  │ PRD-067 │ Old Model Widget  │ WH-A│   85 │  3,200 │ 198│ Discount 40%     │ │
│  │                                                                           │ │
│  │ ░ REVIEW REQUIRED                                                         │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ PRD-023 │ Spare Part X      │ WH-B│  200 │  8,400 │ 192│ Check demand     │ │
│  │                                                                           │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTAL DEAD STOCK                       │      │ 42,850 │   │              │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 REPORT 15: Movement Analysis

### Report ID: `OPS-INV-003`
### Priority: Medium
### Category: Inventory Intelligence Engine

---

### Purpose
Classify inventory by movement velocity (ABC analysis) to optimize stock levels.

### Layout: ABC Classification Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Inventory Velocity Analysis                                                    │
│  ═══════════════════════════                                                    │
│  MOVEMENT ANALYSIS (ABC)                                                        │
│  For the Period 01 January 2024 to 31 December 2024                             │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Classification Summary                                                    │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Class │ Criteria            │ Items │ % Items │ Value    │ % Value       │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │   A   │ Fast Moving (>12x)  │    45 │   13.2% │  342,500 │    70.6%      │ │
│  │   B   │ Medium (6-12x)      │    98 │   28.7% │  108,200 │    22.3%      │ │
│  │   C   │ Slow Moving (<6x)   │   199 │   58.1% │   34,500 │     7.1%      │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTAL │                     │   342 │  100.0% │  485,200 │   100.0%      │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  TOP 20 FAST MOVERS (Class A)                                                   │
│  ────────────────────────────                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Rank│ Code    │ Product          │Turns│ Annual Sales │ Avg Stock│ Value │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │  1  │ PRD-001 │ Widget Alpha     │ 24.5│     125,400  │     5,120│ 15,625│ │
│  │  2  │ PRD-002 │ Widget Beta      │ 22.1│     112,800  │     5,100│ 15,750│ │
│  │  3  │ PRD-008 │ Component Y      │ 19.8│      98,500  │     4,975│ 12,400│ │
│  │ ... │         │                  │     │              │          │       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 💰 TREASURY INTELLIGENCE ENGINE

---

## 📊 REPORT 16: Cash Outflow Forecast

### Report ID: `OPS-TRS-001`
### Priority: Critical
### Category: Treasury Intelligence Engine

---

### Purpose
Project upcoming cash requirements based on scheduled payments and commitments.

### Layout: Weekly Payment Schedule

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Liquidity Management                                                           │
│  ════════════════════                                                           │
│  CASH OUTFLOW FORECAST                                                          │
│  4-Week Projection from 27 January 2025                                         │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Current Cash Balance:    156,890                                          │ │
│  │ Total Projected Outflow: 142,500                                          │ │
│  │ Projected End Balance:    14,390        ⚠ Below Safety Threshold (50,000) │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  WEEKLY BREAKDOWN                                                               │
│  ────────────────                                                               │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │           │ Week 1    │ Week 2    │ Week 3    │ Week 4    │   TOTAL       │ │
│  │           │ 27 Jan-02 Feb│03-09 Feb│10-16 Feb│17-23 Feb│               │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Opening   │   156,890 │   112,390 │    82,890 │    52,390 │               │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Vendor Payments│(35,500)│  (22,500)│  (18,500)│  (28,000)│   (104,500)   │ │
│  │ Salaries       │    —   │     —    │  (12,000)│     —    │    (12,000)   │ │
│  │ Rent           │ (8,000)│     —    │     —    │     —    │     (8,000)   │ │
│  │ Utilities      │ (1,000)│     —    │     —    │   (2,000)│     (3,000)   │ │
│  │ Loan Payment   │    —   │  (7,000) │     —    │     —    │     (7,000)   │ │
│  │ Other          │    —   │     —    │     —    │   (8,000)│     (8,000)   │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ Total Outflow  │(44,500)│  (29,500)│  (30,500)│  (38,000)│   (142,500)   │ │
│  │ Closing        │ 112,390│   82,890 │   52,390 │   14,390 │               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  CRITICAL PAYMENTS THIS WEEK                                                    │
│  ───────────────────────────                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Due Date │ Vendor              │ Invoice    │   Amount │ Priority        │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ 28 Jan   │ Raw Materials Co.   │ BILL-2024-892│  18,500 │ ▓ Critical      │ │
│  │ 29 Jan   │ Landlord            │ RENT-JAN   │   8,000 │ ▓ Critical      │ │
│  │ 30 Jan   │ Equipment Supplier  │ BILL-2024-901│  12,000 │ ▒ High          │ │
│  │ 01 Feb   │ Utilities Provider  │ UTIL-JAN   │   1,000 │ ░ Normal        │ │
│  │ 02 Feb   │ Office Supplies     │ BILL-2024-915│   5,000 │ ░ Normal        │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 REPORT 17: PDC Registry

### Report ID: `OPS-TRS-002`
### Priority: High
### Category: Treasury Intelligence Engine

---

### Purpose
Track post-dated checks issued and received for cash flow planning.

### Layout: Dual Registry (Inbound/Outbound)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Post-Dated Check Management                                                    │
│  ═══════════════════════════                                                    │
│  PDC REGISTRY                                                                   │
│  As at 31 January 2025                                                          │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │        PDC RECEIVABLE (Inbound)        │      PDC PAYABLE (Outbound)      │ │
│  │        ━━━━━━━━━━━━━━━━━━━━━━          │      ━━━━━━━━━━━━━━━━━━━━        │ │
│  │        Total: 125,400                  │      Total: 68,200               │ │
│  │        Checks: 18                      │      Checks: 12                  │ │
│  │        Next Due: 05 Feb (28,500)       │      Next Due: 03 Feb (15,000)   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  PDC RECEIVABLE — CHECKS TO DEPOSIT                                             │
│  ──────────────────────────────────                                             │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Due Date │ Customer           │ Check #    │ Bank      │   Amount │Status│ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ 05 Feb   │ ABC Trading        │ CHK-45892  │ QNB       │   28,500 │ Due  │ │
│  │ 10 Feb   │ Gulf Enterprises   │ CHK-12045  │ CBQ       │   18,200 │ Due  │ │
│  │ 15 Feb   │ National Corp.     │ CHK-78451  │ Doha Bank │   22,400 │ Due  │ │
│  │ 28 Feb   │ Premier Holdings   │ CHK-34521  │ QNB       │   35,800 │ Due  │ │
│  │ ...                                                                       │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTAL PDC RECEIVABLE                                │  125,400 │       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  PDC PAYABLE — CHECKS ISSUED                                                    │
│  ───────────────────────────                                                    │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Due Date │ Vendor             │ Check #    │ Bank      │   Amount │Status│ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ 03 Feb   │ Raw Materials Co.  │ CHK-001245 │ QNB       │   15,000 │ Due  │ │
│  │ 15 Feb   │ Equipment Supply   │ CHK-001246 │ QNB       │   22,000 │ Due  │ │
│  │ 28 Feb   │ Landlord           │ CHK-001247 │ QNB       │    8,000 │ Due  │ │
│  │ ...                                                                       │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ TOTAL PDC PAYABLE                                   │   68,200 │       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  NET PDC POSITION: +57,200 (Receivable exceeds Payable)                         │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

# 🏢 CONSOLIDATED INTELLIGENCE

---

## 📊 REPORT 18: Consolidated Financial Statements

### Report ID: `OPS-CON-001`
### Priority: Critical
### Category: Consolidated Intelligence

---

### Purpose
Aggregate financial data from multiple companies into unified consolidated statements with elimination entries.

### Data Requirements

```python
class ConsolidatedData:
    # Header Info
    parent_company: str
    subsidiaries: List[str]
    consolidation_date: date
    reporting_currency: str
    
    # Individual Company Data
    company_data: Dict[str, CompanyFinancials]
    
    # Eliminations
    intercompany_eliminations: List[EliminationEntry]
    
    # Consolidated Results
    consolidated_balance_sheet: BalanceSheetData
    consolidated_pnl: ProfitLossData
    
    # Ownership
    ownership_structure: List[OwnershipInfo]

class EliminationEntry:
    description: str
    debit_account: str
    credit_account: str
    amount: Decimal
    related_companies: List[str]
```

### Layout: Multi-Company Consolidation Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           [ODOO COMPANY HEADER]                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Group Financial Position                                                       │
│  ════════════════════════                                                       │
│  CONSOLIDATED BALANCE SHEET                                                     │
│  As at 31 December 2024                                                         │
│                                                                                 │
│  Group Structure:                                                               │
│  ├── Meridian Holdings (Parent)         100%                                    │
│  ├── Meridian Trading LLC               100%                                    │
│  ├── Meridian Manufacturing WLL          80%                                    │
│  └── Meridian Services Co.              100%                                    │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                  │ Parent  │ Trading │ Manuf.  │  Svc.  │ Elim.  │CONSOL. │ │
│  ├───────────────────────────────────────────────────────────────────────────┤ │
│  │ ASSETS                                                                    │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ Cash             │  45,200 │  28,400 │  52,100 │  31,190│    —   │ 156,890│ │
│  │ Receivables      │  32,500 │  45,200 │  28,400 │  18,240│(35,000)│  89,340│ │
│  │ Interco Receivable│  35,000 │     —   │     —   │     —  │(35,000)│      — │ │
│  │ Inventory        │     —   │  42,800 │  24,650 │     —  │    —   │  67,450│ │
│  │ Fixed Assets     │  85,400 │  42,200 │ 125,800 │  18,600│    —   │ 272,000│ │
│  │ Investment in Sub│ 180,000 │     —   │     —   │     —  │(180,000)│     — │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ TOTAL ASSETS     │ 378,100 │ 158,600 │ 230,950 │  68,030│(250,000)│ 585,680│ │
│  │                                                                           │ │
│  │ EQUITY & LIAB                                                             │ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ Share Capital    │ 200,000 │  50,000 │  80,000 │  30,000│(160,000)│ 200,000│ │
│  │ Retained Earnings│ 112,500 │  65,400 │  98,200 │  22,350│ (55,000)│ 243,450│ │
│  │ NCI              │     —   │     —   │     —   │     —  │  24,200 │  24,200│ │
│  │ Interco Payable  │     —   │  18,200 │  16,800 │     —  │ (35,000)│      — │ │
│  │ Other Liabilities│  65,600 │  25,000 │  35,950 │  15,680│    —    │ 118,030│ │
│  │ ───────────────────────────────────────────────────────────────────────── │ │
│  │ TOTAL E&L        │ 378,100 │ 158,600 │ 230,950 │  68,030│(250,000)│ 585,680│ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ELIMINATION ENTRIES                                                            │
│  ───────────────────                                                            │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ E1: Eliminate investment in subsidiaries              Dr 180,000          │ │
│  │     Against subsidiary equity                         Cr 180,000          │ │
│  │                                                                           │ │
│  │ E2: Eliminate intercompany receivables/payables       Dr  35,000          │ │
│  │     Trading owes Parent                               Cr  35,000          │ │
│  │                                                                           │ │
│  │ E3: Recognize Non-Controlling Interest (20% Manuf.)   Dr  24,200          │ │
│  │     Manufacturing NCI                                 Cr  24,200          │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                           [ODOO COMPANY FOOTER]                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

*[End of Design Documentation - All 18 Reports Specified]*

---

## IMPLEMENTATION SUMMARY

### Files to Create

```
ops_matrix_reports/
├── __manifest__.py
├── __init__.py
├── static/
│   └── src/
│       └── css/
│           └── ops_report_styles.css          # Complete design system CSS
├── report/
│   ├── __init__.py
│   ├── report_actions.xml                     # All 18 report actions
│   ├── paper_formats.xml                      # A4 paper format definitions
│   └── templates/
│       ├── ops_base_layout.xml                # Base template with common elements
│       ├── ops_balance_sheet.xml              # Report 1
│       ├── ops_profit_loss.xml                # Report 2
│       ├── ops_cash_flow.xml                  # Report 3
│       ├── ops_executive_pl.xml               # Report 4
│       ├── ops_trial_balance.xml              # Report 5
│       ├── ops_aged_receivables.xml           # Report 6
│       ├── ops_aged_payables.xml              # Report 7
│       ├── ops_general_ledger.xml             # Report 8
│       ├── ops_partner_ledger.xml             # Report 9
│       ├── ops_fixed_asset_register.xml       # Report 10
│       ├── ops_depreciation_schedule.xml      # Report 11
│       ├── ops_capex_analysis.xml             # Report 12
│       ├── ops_stock_valuation.xml            # Report 13
│       ├── ops_dead_stock.xml                 # Report 14
│       ├── ops_movement_analysis.xml          # Report 15
│       ├── ops_cash_outflow_forecast.xml      # Report 16
│       ├── ops_pdc_registry.xml               # Report 17
│       └── ops_consolidated_statements.xml    # Report 18
├── models/
│   ├── __init__.py
│   └── report_models.py                       # Report wizard models
└── wizards/
    ├── __init__.py
    └── report_wizards.py                      # Report generation wizards
```

### Key Design Principles Applied

1. **Authority Through Restraint** — No unnecessary decoration
2. **Typography Hierarchy** — Weight and size create visual order
3. **Numbers Deserve Respect** — Serif fonts, right-aligned, tabular
4. **Consistent Spacing** — 4px base unit throughout
5. **Print-First Design** — Optimized for PDF/wkhtmltopdf output
6. **Odoo Integration** — Uses `web.external_layout` for company headers/footers
