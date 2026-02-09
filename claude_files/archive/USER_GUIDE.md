# OPS Matrix Framework - User Guide

**Version:** 19.0.1.5.0
**Last Updated:** January 14, 2026

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Understanding the Matrix](#2-understanding-the-matrix)
3. [Financial Reporting](#3-financial-reporting)
4. [PDC Management](#4-pdc-management)
5. [Approval Workflows](#5-approval-workflows)
6. [Asset Management](#6-asset-management)
7. [Dashboards](#7-dashboards)
8. [Governance Rules](#8-governance-rules)

---

## 1. Getting Started

### 1.1 What is OPS Matrix?

OPS Matrix is an enterprise framework that adds multi-dimensional security and governance to Odoo:

- **Branch**: Geographic or operational divisions (e.g., Dubai, Abu Dhabi)
- **Business Unit**: Product/service lines (e.g., Electronics, Furniture)
- **Persona**: User roles with specific permissions

### 1.2 Your First Login

1. Log in with your credentials
2. Your Branch and Business Unit are automatically assigned
3. You'll only see data relevant to your assignment
4. Access the OPS menu for framework features

### 1.3 Navigation

| Menu | Purpose |
|------|---------|
| **OPS Matrix** | Core settings and configuration |
| **Approvals** | Pending approvals and history |
| **Dashboards** | Performance dashboards |
| **Reporting** | Analytics and reports |

---

## 2. Understanding the Matrix

### 2.1 How Data Filtering Works

When you access any record (sales order, invoice, etc.):

1. System checks your assigned Branch
2. System checks your assigned Business Unit
3. Only matching records are displayed
4. You cannot access data outside your scope

### 2.2 Security Groups

| Group | Access Level |
|-------|--------------|
| OPS User | Read-only to most data |
| OPS Manager | Create/Edit within scope |
| OPS Admin | Full access to all data |
| System Admin | Bypass all restrictions |

### 2.3 Cross-Branch Operations

To access data from another branch:
1. Request Inter-Branch Transfer
2. Submit for approval
3. Wait for source branch manager approval
4. Access granted upon approval

---

## 3. Financial Reporting

### 3.1 Accessing Financial Reports

**Menu**: Accounting → OPS Reports → Financial Report Wizard

### 3.2 Available Report Types

| Report | Description |
|--------|-------------|
| Balance Sheet | Assets, Liabilities, Equity snapshot |
| Profit & Loss | Revenue and Expenses for period |
| Trial Balance | All account balances |
| Cash Flow | Cash movements by category |

### 3.3 Generating a Report

1. Open Financial Report Wizard
2. Select Report Type
3. Set Date Range (From/To)
4. Optional: Filter by Branch
5. Optional: Filter by Business Unit
6. Click "Generate Report"

### 3.4 Export Options

- **Preview**: View in browser
- **PDF**: Download PDF document
- **Excel**: Download Excel spreadsheet

### 3.5 Matrix Filtering

Reports automatically filter based on your permissions:
- Branch Manager: Sees all BUs in their branch
- BU Head: Sees only their BU data
- System Admin: Sees all company data

---

## 4. PDC Management

### 4.1 What are PDCs?

Post-Dated Checks are checks with future dates. OPS tracks them until clearance.

### 4.2 PDC Receivable (Customer Checks)

**Menu**: Accounting → Customers → PDC Receivable

**Workflow**:
```
Draft → Deposited → Cleared
              ↘ Bounced
```

**Actions**:
| Action | When to Use |
|--------|-------------|
| Deposit | Check submitted to bank |
| Clear | Bank confirms payment received |
| Bounce | Bank returns check unpaid |
| Cancel | Void the PDC entry |

### 4.3 PDC Payable (Vendor Checks)

**Menu**: Accounting → Vendors → PDC Payable

**Workflow**:
```
Draft → Issued → Presented → Cleared
```

**Actions**:
| Action | When to Use |
|--------|-------------|
| Issue | Check given to vendor |
| Present | Vendor submits to bank |
| Clear | Payment completed |

### 4.4 PDC Form Fields

| Field | Description |
|-------|-------------|
| Partner | Customer/Vendor name |
| Check Number | Bank check number |
| Amount | Check value |
| Check Date | Date written on check |
| Maturity Date | When check can be deposited |
| Bank | Issuing bank |

---

## 5. Approval Workflows

### 5.1 When Approvals Are Required

Approvals trigger automatically when:
- Discount exceeds your limit
- Order value exceeds threshold
- Purchase requires budget approval
- Policy violation detected

### 5.2 My Approvals Dashboard

**Menu**: Approvals → My Approvals

View:
- Pending requests awaiting your action
- Requests you submitted
- Approval history

### 5.3 Approving a Request

1. Open the approval request
2. Review the details
3. Click "Approve" or "Reject"
4. If rejecting, provide reason

### 5.4 Escalation

If not approved within SLA:
- Level 1: Reminder sent (8 hours)
- Level 2: Manager notified (24 hours)
- Level 3: Director notified (48 hours)

### 5.5 Approval Form Fields

| Field | Description |
|-------|-------------|
| Request Name | What needs approval |
| Requested By | Who submitted |
| Requested Date | When submitted |
| Priority | Normal/Urgent/Critical |
| Approvers | Who can approve |
| State | Pending/Approved/Rejected |

---

## 6. Asset Management

### 6.1 Creating an Asset

**Menu**: Accounting → OPS Accounting → Fixed Assets

1. Click "Create"
2. Enter Asset Name
3. Select Category (determines depreciation method)
4. Enter Purchase Value
5. Set Purchase Date
6. Set Salvage Value (optional)
7. Save

### 6.2 Asset Lifecycle

```
Draft → Running → Sold/Disposed
           ↕
        Paused
```

### 6.3 Asset Actions

| Action | Description |
|--------|-------------|
| Confirm | Start depreciation schedule |
| Pause | Temporarily stop depreciation |
| Resume | Continue depreciation |
| Sell | Record sale of asset |
| Dispose | Write off asset |
| Reset to Draft | Revert for editing |

### 6.4 Depreciation Schedule

After confirming:
1. System generates monthly depreciation lines
2. Each line shows date and amount
3. Post lines to create journal entries
4. Track accumulated depreciation

### 6.5 Asset Categories

| Category | Method | Duration |
|----------|--------|----------|
| IT Equipment | Straight-line | 5 years |
| Furniture | Straight-line | 7 years |
| Vehicles | Declining | 5 years |
| Buildings | Straight-line | 25 years |

---

## 7. Dashboards

### 7.1 Available Dashboards

**Menu**: Dashboards → [Select Dashboard]

| Dashboard | Audience |
|-----------|----------|
| Executive | Management overview |
| Branch | Branch managers |
| BU | Business unit heads |
| Sales | Sales team |

### 7.2 Dashboard Widgets

| Widget Type | Shows |
|-------------|-------|
| KPI Card | Single metric with trend |
| Bar Chart | Comparison data |
| Line Chart | Trends over time |
| Pie Chart | Distribution breakdown |
| Data List | Top items list |

### 7.3 Customizing Dashboards

Managers can:
1. Open Dashboard Configuration
2. Add/remove widgets
3. Arrange widget positions
4. Set data sources

### 7.4 Dashboard Refresh

- Auto-refresh every 60 seconds
- Manual refresh: Click refresh button
- Data is real-time from database

---

## 8. Governance Rules

### 8.1 What are Governance Rules?

Automated policies that enforce business rules:
- Discount limits by role
- Approval thresholds
- Segregation of duties
- Data validation

### 8.2 Viewing Active Rules

**Menu**: Settings → OPS Configuration → Governance Rules

### 8.3 Rule Types

| Type | Example |
|------|---------|
| Discount Limit | Max 10% for sales reps |
| Approval Threshold | PO > $10,000 needs approval |
| Price Authority | ±5% from list price |
| Margin Protection | Minimum 15% margin |

### 8.4 When Rules Trigger

Rules check on:
- Record creation
- Record modification
- State changes
- Document confirmation

### 8.5 Handling Violations

When a rule triggers:
1. Warning message appears
2. Action may be blocked
3. Approval request created (if configured)
4. Violation logged for audit

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save record |
| Ctrl+D | Duplicate record |
| Alt+N | New record |
| Alt+A | Archive/Unarchive |
| Escape | Cancel/Close |

---

## Appendix B: Common Error Messages

| Error | Solution |
|-------|----------|
| "Access Denied" | Contact admin for permissions |
| "Approval Required" | Submit for approval |
| "Invalid Branch" | Select correct branch |
| "Budget Exceeded" | Request budget increase |

---

## Appendix C: Getting Help

- **Technical Support**: Contact your IT administrator
- **User Training**: Request training session
- **Documentation**: Check `claude_files/` folder
- **Bug Reports**: Submit via internal ticketing system

---

**Document Version:** 1.0
**Last Updated:** January 14, 2026
**Author:** Claude Opus 4.5
