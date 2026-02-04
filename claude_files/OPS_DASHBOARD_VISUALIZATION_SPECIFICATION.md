# OPS Dashboard - Advanced Visualization Specification

## Beyond KPI Cards: Charts, Graphs & Interactive Widgets

**Document Type:** Visualization Enhancement Specification  
**Author:** Enterprise BI Architect  
**Date:** January 31, 2026  
**Purpose:** Transform OPS Dashboard from card-based to full BI experience

---

## EXECUTIVE SUMMARY

KPI cards are excellent for **at-a-glance metrics**, but corporate decision-makers need:

1. **Trend Analysis** - How are we doing compared to last month/quarter/year?
2. **Distribution Insights** - Where is revenue/cost concentrated?
3. **Comparison Views** - Branch vs Branch, BU vs BU, Rep vs Rep
4. **Drill-Down Capability** - Click to see underlying details
5. **Predictive Indicators** - Are we on track for targets?

---

## RECOMMENDED VISUALIZATION TYPES BY KPI CATEGORY

### 1. SALES PERFORMANCE

| KPI | Current | Recommended Visualization | Why |
|-----|---------|---------------------------|-----|
| Revenue MTD/YTD | Card | **Area Chart + Card** | Show daily accumulation trend |
| Orders MTD | Card | **Bar Chart + Card** | Compare daily/weekly volumes |
| Gross Margin % | Card | **Gauge + Trend Line** | Show target vs actual + history |
| Quotation Pipeline | Card | **Funnel Chart** | Show conversion stages |
| Sales by Rep | N/A | **Horizontal Bar (Leaderboard)** | Rank performance |
| Revenue by Product | N/A | **Treemap** | Show product contribution |
| Revenue by Customer | N/A | **Pareto Chart (80/20)** | Identify key accounts |

**Recommended Dashboard Layout for Sales Manager:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Revenue MTD: 125,000 QR  │  Orders: 47  │  Margin: 28.5%       │
│ [=========>    ] 78%     │  ▲ +12%      │  [●●●●●○○○○○]        │
├─────────────────────────────────────────────────────────────────┤
│                    REVENUE TREND (Last 30 Days)                 │
│     ▄▄                                                          │
│   ▄▄██▄▄      ▄▄                    ▄▄▄▄                        │
│ ▄▄████████▄▄▄▄██▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄██████▄▄                     │
│ ─────────────────────────────────────────── Target: 160K        │
├─────────────────────────┬───────────────────────────────────────┤
│ TOP 5 SALES REPS        │  SALES BY PRODUCT CATEGORY            │
│ Ahmed ████████████ 45K  │  ┌─────────┬─────────┬───────┐        │
│ Sara  █████████ 38K     │  │Electronics│ Furniture│Tools │       │
│ Omar  ███████ 32K       │  │  45%     │  30%     │ 25%  │        │
│ Fatma █████ 25K         │  └─────────┴─────────┴───────┘        │
│ Khalid ████ 20K         │  (Treemap showing revenue share)      │
├─────────────────────────┴───────────────────────────────────────┤
│                    QUOTATION FUNNEL                             │
│  Draft (25) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 500K                  │
│  Sent (18)  ━━━━━━━━━━━━━━━━━━━━━ 380K                          │
│  Won (12)   ━━━━━━━━━━━━━ 250K                                  │
│  Lost (5)   ━━━━━ 100K                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2. FINANCIAL OVERVIEW (CFO)

| KPI | Recommended Visualization | Why |
|-----|---------------------------|-----|
| P&L Summary | **Waterfall Chart** | Show revenue → expenses → profit flow |
| Revenue vs Target | **Bullet Chart** | Compact target comparison |
| Cash Position | **Gauge (Speedometer)** | Quick health check |
| AR Aging | **Stacked Bar Chart** | Show aging buckets |
| AP Aging | **Stacked Bar Chart** | Show aging buckets |
| Cash Flow Forecast | **Line Chart (Dual Axis)** | Show inflows/outflows + net |
| Budget vs Actual | **Variance Bar Chart** | Show over/under by department |
| YoY Comparison | **Grouped Bar Chart** | This year vs Last year |

**CFO Dashboard Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Revenue    │  Gross Margin  │  Net Profit   │  Cash Balance   │
│  850K QR    │    32.5%       │   125K QR     │   420K QR       │
│  ▲ +15% YoY │   ▲ +2.3pp     │   ▲ +22%      │   ▼ -8%         │
├─────────────────────────────────────────────────────────────────┤
│              PROFIT & LOSS WATERFALL (MTD)                      │
│                                                                 │
│  Revenue    ████████████████████████████████████████│ 850K      │
│  COGS                      ████████████████████████│-574K      │
│  Gross Profit              ████████████████│ 276K               │
│  OpEx                            ████████│-120K                 │
│  Other                              ████│-31K                   │
│  Net Profit                         ████│ 125K                  │
│                                                                 │
├───────────────────────────┬─────────────────────────────────────┤
│   AR AGING DISTRIBUTION   │      CASH FLOW FORECAST (7 Days)    │
│                           │                                     │
│   Current ████████ 320K   │   In  ━━━━━━━━━━━━━━━━━━━━          │
│   1-30    ███ 85K         │   Out ━━━━━━━━━━━━━━                │
│   31-60   ██ 45K          │   Net ━━━━━━━━━━━━━━━━              │
│   61-90   █ 25K           │         Mon Tue Wed Thu Fri Sat Sun │
│   90+     ██ 40K          │                                     │
│                           │   Expected: +85K net by Sunday      │
├───────────────────────────┴─────────────────────────────────────┤
│              BUDGET VS ACTUAL BY DEPARTMENT                     │
│                                                                 │
│  Sales      [████████████░░] 82%  │  On Track                   │
│  Marketing  [██████████████░] 95% │  ⚠ Warning                  │
│  Operations [████████░░░░░░] 58%  │  Under Budget               │
│  Admin      [███████████████] 108%│  ⛔ Over Budget             │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. AR/AP MANAGEMENT

| KPI | Recommended Visualization | Why |
|-----|---------------------------|-----|
| AR Total | **Card + Sparkline** | Show trend in small space |
| Aging Breakdown | **Donut Chart** | Show distribution |
| Collection Trend | **Line Chart** | Track collection efficiency |
| Top Overdue Customers | **Table with Progress Bars** | Actionable list |
| PDC Maturity | **Calendar Heatmap** | Show upcoming maturities |
| DSO (Days Sales Outstanding) | **Gauge** | Industry benchmark comparison |

**AR Clerk Dashboard:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Total AR      │  Overdue        │  Collected MTD  │  DSO       │
│  515K QR       │  110K QR (21%)  │  285K QR        │  42 days   │
│  ▬▬▬▬▬▬▬▬      │  ⚠ Needs Action │  ▲ +18%         │  Target: 35│
├─────────────────────────────────────────────────────────────────┤
│   AR AGING DONUT        │     COLLECTION TREND (6 Months)       │
│                         │                                       │
│      ┌───────┐          │         ▄▄                            │
│     /  320K   \         │       ▄▄██▄▄     ▄▄                   │
│    │  Current  │        │     ▄▄██████▄▄▄▄██▄▄▄▄▄▄▄▄▄▄          │
│    │   62%    │         │   ──────────────────────────          │
│     \   ▓▓▓  /          │   Aug Sep Oct Nov Dec Jan             │
│      └───────┘          │                                       │
│    ▓ 1-30: 85K (17%)    │   Avg: 265K/month                     │
│    ▒ 31-60: 45K (9%)    │                                       │
│    ░ 61-90: 25K (5%)    │                                       │
│    █ 90+: 40K (8%)      │                                       │
├─────────────────────────┴───────────────────────────────────────┤
│              TOP 10 OVERDUE CUSTOMERS                           │
│ ─────────────────────────────────────────────────────────────── │
│ Customer          │ Amount   │ Days │ Last Contact │ Action     │
│ ABC Trading       │ 35,000   │  45  │ 5 days ago   │ [Call]     │
│ XYZ Industries    │ 28,500   │  38  │ 12 days ago  │ [Email]    │
│ Global Imports    │ 22,000   │  52  │ 3 days ago   │ [Escalate] │
│ ...               │          │      │              │            │
├─────────────────────────────────────────────────────────────────┤
│              PDC MATURITY CALENDAR (Next 14 Days)               │
│  Mon  Tue  Wed  Thu  Fri  Sat  Sun                              │
│  ░░   ░░   ██   ░░   ▓▓   ░░   ░░   ← This Week                 │
│  ░░   ▓▓   ░░   ██   ░░   ░░   ░░   ← Next Week                 │
│                                                                 │
│  ██ High (>50K)  ▓▓ Medium (20-50K)  ░░ Low (<20K)              │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4. INVENTORY & WAREHOUSE

| KPI | Recommended Visualization | Why |
|-----|---------------------------|-----|
| Inventory Value | **Card + Trend** | Track investment |
| Stock by Category | **Treemap** | Visual hierarchy |
| Low Stock Alerts | **Alert List with Icons** | Immediate action |
| Turnover Ratio | **Gauge** | Industry benchmark |
| Warehouse Utilization | **Progress Bar** | Capacity planning |
| Stock Movement | **Sankey Diagram** | Flow visualization |

---

### 5. EXECUTIVE (CEO) DASHBOARD

| Widget Type | Content | Visualization |
|-------------|---------|---------------|
| Scorecard Row | Revenue, Orders, Cash, AR | **Card Row with Sparklines** |
| Performance | YTD vs Target | **Bullet Charts** |
| Trend | 12-Month Revenue | **Area Chart** |
| Comparison | Branch Performance | **Horizontal Bar Chart** |
| Distribution | Revenue by BU | **Pie/Donut Chart** |
| Geographic | Sales by Region | **Map (if applicable)** |
| Alerts | KPIs Requiring Attention | **Alert Cards** |

**CEO Dashboard Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│     Revenue YTD      │    Net Profit    │    Cash Position      │
│     8.5M QR          │    1.2M QR       │    2.1M QR            │
│  ▬▬▬▬▬▬▬▬▬▬▬▬▬      │  ▬▬▬▬▬▬▬▬▬▬▬    │   ▬▬▬▬▬▬▬▬▬▬▬▬       │
│  [85% of 10M target] │  [105% target]   │   [Healthy]           │
├─────────────────────────────────────────────────────────────────┤
│              REVENUE TREND (12 Months)                          │
│                                                    ▄▄▄▄         │
│                                              ▄▄▄▄▄▄████▄        │
│                                        ▄▄▄▄▄▄████████████       │
│                                  ▄▄▄▄▄▄██████████████████▄      │
│  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄██████████████████████████       │
│  Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec Jan                │
│  ─ ─ ─ ─ ─ ─ ─ ─ Target Line ─ ─ ─ ─ ─ ─ ─ ─ ─                  │
├───────────────────────────┬─────────────────────────────────────┤
│   BRANCH COMPARISON       │      REVENUE BY BUSINESS UNIT       │
│                           │                                     │
│   Doha    ██████████ 2.8M │          ┌──────────────────┐       │
│   Wakra   ███████ 2.1M    │         /    Electronics    \       │
│   Rayyan  █████ 1.8M      │        │       45%          │       │
│   Khor    ████ 1.2M       │        │   ┌─────────┐      │       │
│   Dukhan  ██ 0.6M         │        │   │Furniture│      │       │
│                           │        │   │  30%    │      │       │
│   Target: ─ ─ 2.5M each   │         \  └─────────┘     /        │
│                           │          └──────────────────┘       │
├───────────────────────────┴─────────────────────────────────────┤
│  ⚠ ALERTS REQUIRING ATTENTION                                   │
│  ──────────────────────────────────────────────────────────────  │
│  🔴 AR Overdue > 90 days increased by 25% (40K → 50K)           │
│  🟡 Rayyan Branch below target by 18%                           │
│  🟡 Inventory turnover dropped to 4.2 (target: 5.0)             │
│  🟢 Cash collection improved by 15% MoM                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## RECOMMENDED CHART TYPES BY PURPOSE

| Purpose | Best Chart Type | Alternative |
|---------|-----------------|-------------|
| **Trend over time** | Line Chart, Area Chart | Sparkline |
| **Part of whole** | Pie, Donut, Treemap | Stacked Bar |
| **Comparison** | Bar Chart (Horizontal) | Grouped Bar |
| **Distribution** | Histogram, Box Plot | Violin Plot |
| **Relationship** | Scatter Plot | Bubble Chart |
| **Ranking** | Horizontal Bar | Lollipop Chart |
| **Progress to goal** | Bullet Chart, Gauge | Progress Bar |
| **Flow/Process** | Sankey, Funnel | Flow Diagram |
| **Geographic** | Map, Choropleth | Bubble Map |
| **Calendar data** | Heatmap Calendar | Timeline |
| **Variance** | Waterfall, Variance Bar | Butterfly Chart |

---

## INTERACTIVITY FEATURES TO IMPLEMENT

### 1. Drill-Down Capability
```
Revenue MTD: 125,000 QR
    ↓ Click
Revenue by Branch:
    Doha: 45,000
    Wakra: 38,000
    ↓ Click on Doha
Doha Revenue by Product:
    Electronics: 25,000
    Furniture: 12,000
    ↓ Click on Electronics
Order List (filterable)
```

### 2. Period Selection
```
[Today] [This Week] [This Month] [This Quarter] [This Year] [Custom Range]
```

### 3. Comparison Mode
```
Compare: [This Month ▼] vs [Last Month ▼]
         [This Year ▼] vs [Last Year ▼]
         [Branch A ▼] vs [Branch B ▼]
```

### 4. Filter Panels
```
Filters:
  Branch: [All ▼]
  Business Unit: [All ▼]
  Salesperson: [All ▼]
  Date Range: [Jan 1 - Jan 31]
  [Apply] [Reset]
```

### 5. Export Options
```
[📊 Export to Excel] [📄 Export to PDF] [🔄 Refresh] [⚙ Settings]
```

---

## IMPLEMENTATION PRIORITY

### Phase 1: Essential Charts (Week 1)
| Chart | For Dashboard | Priority |
|-------|---------------|----------|
| Line/Area Chart | Revenue Trend | P0 |
| Horizontal Bar | Branch Comparison | P0 |
| Donut Chart | AR Aging | P0 |
| Gauge | Margin %, DSO | P0 |
| Sparklines | All KPI Cards | P0 |

### Phase 2: Advanced Charts (Week 2)
| Chart | For Dashboard | Priority |
|-------|---------------|----------|
| Funnel | Sales Pipeline | P1 |
| Waterfall | P&L Summary | P1 |
| Bullet Chart | Target vs Actual | P1 |
| Treemap | Product/Category Mix | P1 |
| Calendar Heatmap | PDC Maturity | P1 |

### Phase 3: Interactive Features (Week 3)
| Feature | Priority |
|---------|----------|
| Drill-down navigation | P1 |
| Period comparison | P1 |
| Filter panels | P2 |
| Export to Excel/PDF | P2 |

### Phase 4: Advanced Analytics (Future)
| Feature | Priority |
|---------|----------|
| Predictive trend lines | P3 |
| Anomaly detection alerts | P3 |
| What-if scenarios | P3 |

---

## CHART LIBRARY RECOMMENDATION

### For OPS Dashboard (OWL Components):

**Primary: Chart.js**
- Lightweight (~60KB)
- 8 chart types built-in
- Responsive
- Easy OWL integration
- MIT License

**Alternative: ApexCharts**
- More chart types
- Better animations
- Built-in interactivity
- Slightly heavier (~120KB)

**For Complex Visualizations: D3.js**
- Custom visualizations
- Sankey, Treemap, Choropleth
- Steeper learning curve
- Maximum flexibility

### Recommended Stack:
```javascript
// Primary charts
import Chart from 'chart.js/auto';

// For gauges and advanced
import ApexCharts from 'apexcharts';

// For complex custom charts
import * as d3 from 'd3';
```

---

## WIDGET COMPONENT ARCHITECTURE

```javascript
// Widget Types
const WIDGET_TYPES = {
    'kpi': KPICardWidget,           // Current implementation
    'kpi_sparkline': KPISparkline,  // Card with mini trend
    'line_chart': LineChartWidget,
    'area_chart': AreaChartWidget,
    'bar_chart': BarChartWidget,
    'horizontal_bar': HorizontalBarWidget,
    'pie_chart': PieChartWidget,
    'donut_chart': DonutChartWidget,
    'gauge': GaugeWidget,
    'bullet_chart': BulletChartWidget,
    'funnel': FunnelWidget,
    'waterfall': WaterfallWidget,
    'treemap': TreemapWidget,
    'calendar_heatmap': CalendarHeatmapWidget,
    'data_table': DataTableWidget,
    'alert_list': AlertListWidget,
};

// Widget Grid Layout
const GRID_CONFIG = {
    columns: 12,
    rowHeight: 80,
    margin: 16,
    breakpoints: {
        lg: 1200,
        md: 996,
        sm: 768,
        xs: 480,
    }
};
```

---

## SAMPLE CHART CONFIGURATIONS

### 1. Revenue Trend (Area Chart)
```javascript
{
    type: 'area_chart',
    title: 'Revenue Trend',
    kpi_code: 'SALES_REVENUE_MTD',
    config: {
        period: 'daily',
        duration: 30,  // days
        fill: true,
        gradient: true,
        showTarget: true,
        targetValue: 160000,
        colors: ['#10b981'],
        targetColor: '#ef4444',
    },
    size: { width: 8, height: 3 }
}
```

### 2. Branch Comparison (Horizontal Bar)
```javascript
{
    type: 'horizontal_bar',
    title: 'Branch Performance',
    kpi_code: 'SALES_REVENUE_MTD',
    config: {
        groupBy: 'ops_branch_id',
        showTarget: true,
        sortOrder: 'desc',
        maxItems: 5,
        colors: ['#3b82f6'],
        targetColor: '#6b7280',
    },
    size: { width: 4, height: 4 }
}
```

### 3. AR Aging (Donut Chart)
```javascript
{
    type: 'donut_chart',
    title: 'AR Aging Distribution',
    kpi_codes: ['AR_CURRENT', 'AR_30_60', 'AR_60_90', 'AR_OVER_90'],
    config: {
        showLegend: true,
        showPercentage: true,
        colors: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
        centerText: 'Total AR',
        centerValue: true,
    },
    size: { width: 4, height: 4 }
}
```

### 4. Margin Gauge
```javascript
{
    type: 'gauge',
    title: 'Gross Margin',
    kpi_code: 'SALES_GROSS_MARGIN',
    config: {
        min: 0,
        max: 50,
        target: 30,
        thresholds: [
            { value: 20, color: '#ef4444' },  // Red
            { value: 25, color: '#f59e0b' },  // Yellow
            { value: 30, color: '#10b981' },  // Green
        ],
        suffix: '%',
    },
    size: { width: 2, height: 2 }
}
```

### 5. Sales Funnel
```javascript
{
    type: 'funnel',
    title: 'Quotation Funnel',
    stages: [
        { code: 'SALES_QUOTATIONS_DRAFT', label: 'Draft' },
        { code: 'SALES_QUOTATIONS_SENT', label: 'Sent' },
        { code: 'SALES_ORDERS_WON', label: 'Won' },
        { code: 'SALES_ORDERS_LOST', label: 'Lost' },
    ],
    config: {
        showValues: true,
        showConversion: true,
        colors: ['#3b82f6', '#8b5cf6', '#10b981', '#ef4444'],
    },
    size: { width: 6, height: 4 }
}
```

---

## DASHBOARD TEMPLATES BY PERSONA

### CFO Dashboard Template
```javascript
{
    code: 'CFO_ENHANCED',
    name: 'Financial Command Center',
    layout: [
        // Row 1: Scorecard
        { widget: 'kpi_sparkline', kpi: 'SALES_REVENUE_YTD', x: 0, y: 0, w: 3, h: 1 },
        { widget: 'kpi_sparkline', kpi: 'CFO_GROSS_MARGIN', x: 3, y: 0, w: 3, h: 1 },
        { widget: 'kpi_sparkline', kpi: 'CFO_NET_PROFIT', x: 6, y: 0, w: 3, h: 1 },
        { widget: 'gauge', kpi: 'TREASURY_CASH_BALANCE', x: 9, y: 0, w: 3, h: 1 },
        
        // Row 2: Trends
        { widget: 'area_chart', kpi: 'revenue_trend', x: 0, y: 1, w: 8, h: 3 },
        { widget: 'waterfall', kpi: 'pl_waterfall', x: 8, y: 1, w: 4, h: 3 },
        
        // Row 3: AR/AP
        { widget: 'donut_chart', kpi: 'ar_aging', x: 0, y: 4, w: 4, h: 3 },
        { widget: 'donut_chart', kpi: 'ap_aging', x: 4, y: 4, w: 4, h: 3 },
        { widget: 'line_chart', kpi: 'cash_forecast', x: 8, y: 4, w: 4, h: 3 },
        
        // Row 4: Comparisons
        { widget: 'horizontal_bar', kpi: 'branch_revenue', x: 0, y: 7, w: 6, h: 3 },
        { widget: 'bullet_chart', kpi: 'budget_actual', x: 6, y: 7, w: 6, h: 3 },
    ]
}
```

### Sales Manager Dashboard Template
```javascript
{
    code: 'SALES_MGR_ENHANCED',
    name: 'Sales Performance Hub',
    layout: [
        // Row 1: KPIs with targets
        { widget: 'bullet_chart', kpi: 'SALES_REVENUE_MTD', x: 0, y: 0, w: 4, h: 1 },
        { widget: 'kpi_sparkline', kpi: 'SALES_ORDERS_MTD', x: 4, y: 0, w: 2, h: 1 },
        { widget: 'kpi_sparkline', kpi: 'SALES_AVG_ORDER', x: 6, y: 0, w: 2, h: 1 },
        { widget: 'gauge', kpi: 'SALES_GROSS_MARGIN', x: 8, y: 0, w: 2, h: 1 },
        { widget: 'kpi', kpi: 'SALES_QUOTATIONS', x: 10, y: 0, w: 2, h: 1 },
        
        // Row 2: Trend + Funnel
        { widget: 'area_chart', kpi: 'daily_sales', x: 0, y: 1, w: 6, h: 3 },
        { widget: 'funnel', kpi: 'sales_funnel', x: 6, y: 1, w: 6, h: 3 },
        
        // Row 3: Leaderboard + Product Mix
        { widget: 'horizontal_bar', kpi: 'rep_performance', x: 0, y: 4, w: 4, h: 3 },
        { widget: 'treemap', kpi: 'product_revenue', x: 4, y: 4, w: 4, h: 3 },
        { widget: 'data_table', kpi: 'top_customers', x: 8, y: 4, w: 4, h: 3 },
    ]
}
```

---

## NEXT STEPS

1. **Choose Chart Library** - Recommend Chart.js + ApexCharts combo
2. **Create Base Widget Components** - OWL components for each chart type
3. **Add Chart Endpoints** - RPC methods for time-series data
4. **Update Dashboard Model** - Add chart configuration fields
5. **Create Chart Data Files** - Pre-configure dashboard layouts
6. **Test & Iterate** - Start with CFO dashboard as pilot

---

## SUMMARY RECOMMENDATION

| Current State | Enhancement | Business Value |
|---------------|-------------|----------------|
| KPI Cards only | + Trend charts | See direction, not just current value |
| Static numbers | + Interactive drill-down | Find root causes quickly |
| Branch isolation | + Comparison charts | Benchmark performance |
| No targets | + Bullet/Gauge charts | Track against goals |
| No alerts | + Alert widgets | Proactive management |

**Priority Order:**
1. 📈 Line/Area charts (trend visibility)
2. 📊 Horizontal bar (comparisons)
3. 🎯 Gauge/Bullet (targets)
4. 🍩 Donut/Pie (distribution)
5. 🔻 Funnel (pipeline)
6. 📋 Data tables (drill-down)

---

**Document Complete**

**Version:** 1.0  
**Author:** Enterprise BI Architect  
**Date:** January 31, 2026
