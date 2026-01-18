# OPS Reporting App - User Guide

**Version:** 1.0
**Last Updated:** 2026-01-18
**Target Audience:** Sales Managers, Branch Managers, Executives

---

## 1. Accessing the Reporting App

The **Reporting** app is available to users with Manager or Executive roles.

### Navigation

From the main Odoo menu bar, click **Reporting**.

```
┌─────────────────────────────────────────────────────────────┐
│ [Approvals] [Sales] [Purchase] [Inventory] [Accounting]     │
│ [REPORTING] [HR] [Settings]                                 │
└─────────────────────────────────────────────────────────────┘
```

### Who Has Access?

| Role | Access Level |
|------|--------------|
| Sales Representative | No access |
| Sales Manager | Full access |
| Branch Manager | Full access |
| CFO / Executive | Full access |
| Administrator | Full access (Settings) |

**Note:** If you don't see the Reporting app, contact your administrator to verify your persona includes the `group_ops_manager` or `group_ops_executive` security group.

---

## 2. The Executive Dashboard

### Dashboard Structure

The Reporting app is organized into four main sections:

```
REPORTING
├── Dashboards
│   └── Analytics           ← KPIs, charts, widgets
├── Financial Reports       ← P&L, Balance Sheet, Cash Flow
├── Operational Reports     ← Sales Analysis, Inventory
└── Governance              ← Rules, Approvals, SLA
```

### Key Metrics Displayed

| Metric | Description | Source |
|--------|-------------|--------|
| **Total Sales** | Sum of all confirmed Sales Orders (Booked Revenue) | `sale.order` with `state=sale` |
| **Inventory Value** | Real-time valuation of stock in your allowed branches | `stock.quant` |
| **Total Margin** | Gross profit: (Sales Price - Cost) | Computed from order lines |
| **Open Orders** | Pending sales orders awaiting confirmation | `sale.order` with `state=draft` |
| **Pending Approvals** | Items waiting for your decision | `ops.approval.request` |

### Automatic Branch Filtering

**Important:** All dashboard data is automatically filtered based on your **Allowed Branches** and **Allowed Business Units**.

#### Example Scenarios

| User | Primary Branch | Allowed Branches | What They See |
|------|----------------|------------------|---------------|
| Sarah (Sales Mgr) | Dubai | Dubai, Abu Dhabi | Dubai + Abu Dhabi data |
| John (Dubai Rep) | Dubai | Dubai only | Dubai data only |
| Ahmed (Regional VP) | HQ | All branches | Company-wide data |

This filtering is **automatic** and **cannot be bypassed** by regular users. It ensures data isolation and governance compliance.

---

## 3. Understanding the "Sales by Branch" Chart

### What It Shows

The Sales by Branch visualization displays revenue distribution across your allowed branches.

```
       Sales by Branch (Current Month)
       ┌──────────────────────────────────────┐
       │ Dubai      ████████████████ 45%      │
       │ Abu Dhabi  ██████████       28%      │
       │ Sharjah    ██████           17%      │
       │ Ajman      ████             10%      │
       └──────────────────────────────────────┘
```

### Interpreting the Data

| Element | Meaning |
|---------|---------|
| **Bar Length** | Proportional to revenue |
| **Percentage** | Branch contribution to total |
| **Color Coding** | Blue = On Target, Red = Below Target |
| **Date Range** | Current month by default (adjustable) |

### Drill-Down Actions

1. **Click a branch bar** to see detailed sales orders
2. **Hover** for tooltip with exact figures
3. **Right-click** for export options

### Reading the Numbers

- **Total Sales:** Combined revenue from all your branches
- **Branch %:** Each branch's contribution to total
- **YoY Change:** Comparison to same period last year (if configured)
- **Target %:** Progress toward monthly/quarterly targets

---

## 4. Dashboard Filters

### Applying Filters

Most dashboards support the following filters:

| Filter | Purpose | Example |
|--------|---------|---------|
| **Date Range** | Select time period | "This Month", "Q1 2026", "Last 90 Days" |
| **Branch** | Focus on specific branch(es) | Filter to "Dubai" only |
| **Business Unit** | Filter by business line | "Retail" vs "Wholesale" |
| **Product Category** | Narrow by product type | "Electronics", "Furniture" |
| **Sales Team** | View by team | "Enterprise Sales", "Inside Sales" |

### Using Quick Filters

Click the filter icons at the top of the dashboard:

```
[This Month ▼] [All Branches ▼] [All BUs ▼] [🔄 Refresh]
```

### Saving Filter Combinations

1. Apply your desired filters
2. Click **Favorites** > **Save current search**
3. Name your filter (e.g., "Dubai Q1 Retail")
4. Access it anytime from the Favorites menu

---

## 5. Using the Approvals Menu

### Accessing Approvals

From the main menu, click **Approvals**.

```
APPROVALS
├── My Approvals          ← Dashboard view
├── Pending Approvals     ← Items awaiting your decision
├── Approval History      ← All processed requests
├── SLA Tracking          ← (Managers only)
└── Violations & Alerts   ← (Admins only)
```

### Understanding Approval Triggers

Approval requests are automatically created when transactions violate governance rules:

| Trigger | Condition | Example |
|---------|-----------|---------|
| **Low Margin** | Margin below threshold | Sale at 5% margin (threshold: 15%) |
| **High Value** | Amount exceeds limit | Order > $50,000 |
| **Special Customer** | Flagged accounts | Government client, VIP |
| **Cross-Branch** | Inter-branch transaction | Transfer from Dubai to Abu Dhabi |
| **Budget Override** | Exceeds allocated budget | Purchase > remaining budget |

### Processing an Approval Request

1. Navigate to **Approvals > Pending Approvals**
2. Click on a pending request
3. Review the details:
   - **Document:** The order/transaction requiring approval
   - **Requester:** Who submitted the request
   - **Reason:** Why approval is needed
   - **Amount:** Transaction value
   - **Rule Triggered:** Which governance rule fired

4. Take action:
   - **Approve**: Click the green **Approve** button
   - **Reject**: Click **Reject** and provide a reason
   - **Escalate**: Forward to a higher authority

### Approval Workflow States

```
┌──────────┐    ┌─────────┐    ┌──────────┐
│  DRAFT   │───▶│ PENDING │───▶│ APPROVED │
└──────────┘    └─────────┘    └──────────┘
                    │
                    ▼
               ┌──────────┐
               │ REJECTED │
               └──────────┘
```

### Approval Delegation

If you'll be unavailable:

1. Go to **Settings > Users > [Your User]**
2. Navigate to the **OPS Matrix Access** tab
3. Set up delegation:
   - **Delegate To:** Select backup approver
   - **Start Date / End Date:** Delegation period

**Note:** Delegated approvals are tracked for audit purposes.

---

## 6. Financial Reports

### Available Reports

Navigate to **Reporting > Financial Reports**:

| Report | Purpose | Key Metrics |
|--------|---------|-------------|
| **Profit & Loss** | Revenue vs expenses | Gross Margin, Net Profit |
| **Balance Sheet** | Assets, liabilities, equity | Current Ratio, Debt/Equity |
| **Cash Flow** | Operating, investing, financing | Free Cash Flow |
| **Budget vs Actual** | Performance against plan | Variance %, YTD |
| **Aged Receivables** | Customer payment aging | 30/60/90+ days |
| **Aged Payables** | Vendor payment aging | Due amounts |

### Excel Export

All reports support one-click Excel export:

1. Generate the report with your filters
2. Click the **Export to Excel** button (📊 icon)
3. Download the formatted spreadsheet

**Note:** Excel exports include only data within your allowed branches/BUs.

---

## 7. Operational Reports

### Sales Analysis

Navigate to **Reporting > Operational Reports > Sales Analysis**:

- **Sales by Product:** Top-selling items
- **Sales by Customer:** Key accounts
- **Sales by Salesperson:** Team performance
- **Sales Trends:** Weekly/Monthly patterns

### Inventory Analysis

- **Stock Levels:** Current quantities by location
- **Stock Turnover:** How fast inventory moves
- **Reorder Report:** Items below minimum levels
- **Dead Stock:** Slow-moving inventory

---

## 8. Dashboard Best Practices

### Daily Routine

1. **Morning Check:** Review pending approvals (< 5 minutes)
2. **Quick Glance:** Check key KPIs on dashboard
3. **Action Items:** Address any SLA warnings

### Weekly Review

1. Review Sales by Branch trends
2. Compare actual vs budget
3. Analyze approval turnaround times
4. Check for SLA breaches

### Monthly Actions

1. Export month-end reports to Excel
2. Review team performance metrics
3. Prepare management summary
4. Update forecasts if needed

---

## 9. Troubleshooting

### "No Data Available"

**Cause:** Your user doesn't have any allowed branches/BUs.

**Solution:**
1. Contact your administrator
2. Request Matrix Access configuration
3. Verify your Persona assignment

### "Dashboard Not Loading"

**Causes:**
- Browser cache issue
- Network timeout
- Large data set

**Solutions:**
1. Refresh the page (F5)
2. Clear browser cache
3. Reduce date range filter
4. Contact IT support if persistent

### "Missing Approve Button"

**Cause:** You're not the designated approver for this request.

**Solution:**
1. Check if the request is assigned to you
2. Verify your Persona has approval authority
3. Request delegation if the approver is unavailable

---

## 10. Quick Reference

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Quick search |
| `Ctrl+P` | Print report |
| `F5` | Refresh dashboard |
| `Esc` | Close modal |

### Report Date Ranges

| Option | Period |
|--------|--------|
| Today | Current day |
| This Week | Mon-Sun of current week |
| This Month | 1st to last day of month |
| This Quarter | Q1/Q2/Q3/Q4 |
| This Year | Jan 1 - Dec 31 |
| Last 30 Days | Rolling 30-day window |
| Custom | Select specific dates |

### Support Contacts

- **Dashboard Issues:** IT Help Desk
- **Access Problems:** System Administrator
- **Report Questions:** Finance Team
- **Approval Queries:** Your Direct Manager

---

**Document Version:** 1.0
**Applies to:** OPS Framework v1.3.0+, Odoo 19.0
