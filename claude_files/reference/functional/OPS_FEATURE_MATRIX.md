# OPS Framework -- Features & Competitive Positioning

> **Version:** 2.0 | **Date:** 2026-02-13 | **Odoo Version:** 19.0 Community Edition
> **Modules:** ops_matrix_core v19.0.1.14.0 | ops_matrix_accounting v19.0.21.0.0 | ops_kpi v19.0.2.1.0 | ops_theme v19.0.21.0.0

---

## 1. Executive Summary

### What Is OPS Framework?

OPS Framework is a **enterprise-grade governance, security, and business intelligence layer** built on top of Odoo 19 Community Edition. It transforms Odoo CE from a single-entity SMB tool into a **multi-branch, multi-business-unit corporate platform** with audit-grade security, persona-based access control, and executive-level reporting -- capabilities previously available only in Odoo Enterprise or expensive third-party ERP systems.

### By the Numbers

| Metric | Count |
|--------|-------|
| Custom Models | 95+ |
| ACL Rules (ir.model.access.csv) | 411+ (165 core + 246 accounting) |
| Record Rules | 116+ |
| Security Groups | 20+ |
| Pre-Configured Personas | 18 |
| Segregation of Duties Rules | 6 (default, admin-activated) |
| Governance Rule Templates | 8+ |
| SLA Policy Templates | 4 |
| Pre-Built KPI Definitions | 50+ |
| Persona-Specific KPI Boards | 10+ |
| Financial Report Wizards | 14 |
| REST API Endpoints | 10+ |
| Automated Cron Jobs | 8+ |

### Key Differentiators vs. Standard Odoo

| Capability | Odoo 19 CE | Odoo 19 Enterprise | OPS Framework (CE) |
|-----------|------------|--------------------|--------------------|
| Multi-Branch Isolation | No | Partial | Full matrix isolation |
| Business Unit Structure | No | No | Native BU hierarchy |
| Persona-Based Access | No | No | 18 pre-configured personas |
| IT Admin Blindness | No | No | 24 models blocked from IT |
| Segregation of Duties | No | No | 6 configurable SoD rules |
| 3-Way Match (PO/GRN/Invoice) | No | Enterprise-only | Built-in with override workflow |
| Post-Dated Cheques | No | No | Full PDC lifecycle management |
| Fixed Asset Management | No | Enterprise-only | Full depreciation/disposal/impairment |
| IFRS 16 Lease Accounting | No | Enterprise-only | ROU asset + lease liability |
| Budget Management | No | Enterprise-only | Budget vs Actual reporting |
| FX Revaluation | No | Enterprise-only | Unrealized gain/loss calculation |
| Period Close Workflow | No | Enterprise-only | Guided checklist with soft/hard lock |
| Corporate Consolidation | No | Enterprise-only | 4 consolidation report types |
| KPI Dashboards | No | Spreadsheet-only | 50+ KPIs with persona-filtered boards |
| REST API | No | No | Full API with key auth + rate limiting |
| Corporate Audit Trail | No | Partial | SOX/ISO/GDPR-grade audit logging |
| Debranding | No | No | Full white-label capability |
| Skin/Theme System | No | No | 10-color palette presets |
| Excel Import (SO/PO) | No | No | Line-level Excel import wizards |
| Secure Data Export | No | No | Audited export with field visibility |

---

## 2. Feature Matrix Table

### Legend
- **Module:** Which OPS module provides the feature
- **Models:** Key database models involved
- **Category:** Functional grouping
- **Competitive Advantage:** What makes this feature unique

| # | Feature | Module | Key Models | Category | Description | Competitive Advantage |
|---|---------|--------|------------|----------|-------------|----------------------|
| 1 | Branch Matrix | core | ops.branch | Structure | Multi-branch organizational hierarchy with isolation | Full data isolation per branch via record rules |
| 2 | Business Unit Matrix | core | ops.business.unit | Structure | Cross-branch business unit grouping | BU leaders see all branches within their unit |
| 3 | Persona Engine | core | ops.persona | Security | 18 pre-defined corporate role templates | Ready-to-deploy persona suite with SoD authority fields |
| 4 | Persona Delegation | core | ops.persona.delegation | Security | Temporary authority delegation with expiry | Time-bound authority transfer for vacation/absence |
| 5 | IT Admin Blindness | core | Record rules on 24 models | Security | IT staff cannot see business transactions | Zero-trust pattern: IT manages systems, not data |
| 6 | Segregation of Duties | core | ops.segregation.of.duties | Compliance | Configurable SoD rules with thresholds | Block violations at transaction level, not just audit |
| 7 | Governance Rules Engine | core | ops.governance.rule | Compliance | Configurable business rules with approval workflows | Code-based conditions with persona-targeted approvals |
| 8 | Approval Workflow | core | ops.approval.request, ops.approval.rule | Workflow | Multi-level approval with recall capability | Recall + reject wizards with mandatory reason capture |
| 9 | 3-Way Match | core | ops.three.way.match | Procurement | PO vs GRN vs Invoice matching | Automatic blocking with manager override workflow |
| 10 | SLA Engine | core | ops.sla.template, ops.sla.instance | Operations | Service level tracking with escalation | Timer-based SLA with automatic breach detection |
| 11 | Corporate Audit Trail | core | ops.corporate.audit.log | Compliance | SOX/ISO/GDPR-compliant audit logging | Immutable log with IP tracking, user agent capture |
| 12 | API Key Authentication | core | ops.api.key | Integration | REST API key management per persona | Persona-scoped API access with usage tracking |
| 13 | API Audit Log | core | ops.audit.log | Integration | Full request/response logging for API calls | Response time tracking, error capture, IP logging |
| 14 | Session Management | core | ops.session.manager | Security | Active session tracking and control | Force logout, concurrent session limits |
| 15 | IP Whitelisting | core | ops.ip.whitelist | Security | IP-based access restrictions | Per-user or global IP allow/deny lists |
| 16 | Data Archival | core | ops.data.archival, ops.archive.policy | Performance | Policy-driven data archival for scalability | Age-based archiving with configurable policies |
| 17 | Performance Monitor | core | ops.performance.monitor | Operations | System performance tracking and alerting | Threshold-based alerts on query time, memory |
| 18 | Inter-Branch Transfer | core | ops.inter.branch.transfer | Operations | Transfer goods/value between branches | Dual journal entry for inter-branch accounting |
| 19 | Product Request | core | ops.product.request | Procurement | Controlled product creation workflow | Users request, approvers create -- prevents catalog bloat |
| 20 | Field Visibility Rules | core | field.visibility.rule | Security | Dynamic field show/hide based on groups | Cost prices hidden from non-authorized users |
| 21 | Price Manager Control | core | group_ops_price_manager | Sales | Control who can modify selling prices | SO line price locked unless user has Price Manager group |
| 22 | Secure Export Wizard | core | ops.secure.export.wizard | Compliance | Audited data export with matrix filtering | Every export logged; field visibility enforced in export |
| 23 | Persona Drift Detection | core | ops.persona.drift.wizard | Compliance | Detect permission drift from assigned persona | Identifies extra/missing permissions with severity levels |
| 24 | Audit Evidence Package | core | ops.audit.evidence.wizard | Compliance | Generate compliance evidence workbooks | 7-sheet Excel package for SOX/ISO auditors |
| 25 | Excel SO Import | core | ops.sale.order.import.wizard | Data Entry | Import sale order lines from Excel | Column mapping, validation, error reporting |
| 26 | Excel PO Import | core | ops.purchase.order.import.wizard | Data Entry | Import purchase order lines from Excel | Column mapping, validation, error reporting |
| 27 | Report Template Engine | core | ops.report.template | Reporting | Configurable report templates with apply wizard | Save/load filter configurations as reusable templates |
| 28 | Dashboard Configuration | core | ops.dashboard.config, ops.dashboard.widget | BI | Configurable dashboard widgets | Persona-scoped dashboard definitions |
| 29 | Post-Dated Cheques (Recv) | accounting | ops.pdc.receivable | Finance | Receivable PDC lifecycle management | Register -> Deposit -> Collect/Bounce workflow |
| 30 | Post-Dated Cheques (Pay) | accounting | ops.pdc.payable | Finance | Payable PDC lifecycle management | Issue -> Clear/Bounce workflow with journal entries |
| 31 | Fixed Asset Management | accounting | ops.asset, ops.asset.category | Finance | Full asset lifecycle with depreciation | Straight-line + declining balance, disposal + impairment |
| 32 | Asset Depreciation | accounting | ops.asset.depreciation | Finance | Automated depreciation schedule generation | Cron-driven monthly depreciation with journal posting |
| 33 | Asset Disposal | accounting | ops.asset.disposal.wizard | Finance | Asset disposal with gain/loss calculation | Wizard-driven disposal with automatic journal entries |
| 34 | Asset Impairment | accounting | ops.asset.impairment.wizard | Finance | Asset impairment write-down | IFRS-compliant impairment loss recognition |
| 35 | Budget Management | accounting | ops.budget, ops.budget.line | Finance | Budget definition with period allocation | Budget vs Actual reporting with variance analysis |
| 36 | IFRS 16 Lease Accounting | accounting | ops.lease | Finance | Right-of-use asset and lease liability | Automatic ROU amortization + interest calculation |
| 37 | Fiscal Period Management | accounting | ops.fiscal.period | Finance | Define and lock fiscal periods | Soft lock (warnings) vs hard lock (blocking) |
| 38 | Period Close Workflow | accounting | ops.period.close.wizard | Finance | Guided period close with checklist | Step-by-step close process with validation checks |
| 39 | FX Revaluation | accounting | ops.fx.revaluation.wizard | Finance | Unrealized foreign exchange gains/losses | Calculate + post workflow with account type filtering |
| 40 | Consolidation Intelligence | accounting | ops.consolidation.intelligence.wizard | Reporting | 4 consolidation report types | Company P&L, Branch P&L, BU Report, Consolidated BS |
| 41 | Company Consolidation P&L | accounting | ops.company.consolidation | Reporting | Company-level profit & loss | Hierarchical account grouping with period comparison |
| 42 | Branch P&L Report | accounting | ops.branch.report | Reporting | Per-branch profit & loss analysis | Branch-isolated financial performance |
| 43 | BU Report | accounting | ops.business.unit.report | Reporting | Business unit performance report | Cross-branch aggregation within BU |
| 44 | Consolidated Balance Sheet | accounting | ops.consolidated.balance.sheet | Reporting | Full consolidated balance sheet | Multi-entity balance sheet with eliminations |
| 45 | General Ledger | accounting | ops.gl.wizard | Reporting | Enhanced general ledger report | Branch/BU filtering, PDF/Excel/HTML output |
| 46 | Trial Balance | accounting | ops.tb.wizard | Reporting | Trial balance report | Comparative periods, branch isolation |
| 47 | Profit & Loss Statement | accounting | ops.pnl.wizard | Reporting | Income statement report | Hierarchical grouping, period comparison |
| 48 | Balance Sheet | accounting | ops.bs.wizard | Reporting | Balance sheet report | As-of-date reporting, branch filtering |
| 49 | Cash Flow Statement | accounting | ops.cf.wizard | Reporting | Cash flow report | Direct/indirect method support |
| 50 | Aged Receivables/Payables | accounting | ops.aged.wizard | Reporting | Aging analysis report | Configurable aging buckets, partner filtering |
| 51 | Partner Ledger | accounting | ops.partner.ledger.wizard | Reporting | Partner transaction ledger | Receivable/payable filtering, reconciliation status |
| 52 | Treasury Report | accounting | ops.treasury.report.wizard | Reporting | Cash position and flow analysis | Multi-account cash visibility |
| 53 | Asset Report | accounting | ops.asset.report.wizard | Reporting | Asset register and depreciation schedule | Asset category filtering, NBV calculations |
| 54 | Inventory Report | accounting | ops.inventory.report.wizard | Reporting | Stock valuation and movement report | Branch-isolated inventory visibility |
| 55 | Daily Reports | accounting | ops.daily.reports.wizard | Reporting | Bankbook, cashbook, daybook | Daily transaction summaries per account |
| 56 | Budget vs Actual | accounting | ops.budget.vs.actual.wizard | Reporting | Budget variance analysis | Variance calculation with percentage deviation |
| 57 | Report Engine v2 | accounting | ops.base.report.wizard (abstract) | Reporting | Unified report framework with 3 shape templates | Lines/Hierarchy/Matrix shapes, template save/load |
| 58 | Financial Report Config | accounting | ops.financial.report.config | Reporting | Configurable report definitions | Reusable report structure templates |
| 59 | Profitability Analysis | accounting | ops.matrix.profitability.analysis | Analytics | Multi-dimensional profitability analysis | Branch x BU x Product category margins |
| 60 | Trend Analysis | accounting | ops.trend.analysis | Analytics | Historical trend analysis | MoM, QoQ, YoY comparison engine |
| 61 | Matrix Snapshot | accounting | ops.matrix.snapshot | Analytics | Point-in-time financial snapshots | Cron-driven periodic financial state capture |
| 62 | Recurring Journal Templates | accounting | ops.recurring, ops.journal.template | Finance | Automated recurring journal entries | Template-based with cron execution |
| 63 | Customer Followup | accounting | ops.followup | Finance | Automated customer payment followup | Multi-level followup with email templates |
| 64 | Bank Reconciliation | accounting | ops.bank.reconciliation | Finance | Enhanced bank statement reconciliation | SoD-enforced reconciliation + approval |
| 65 | Interbranch Transfer (Acctg) | accounting | ops.interbranch.transfer | Finance | Accounting entries for inter-branch moves | Automatic balancing entries between branches |
| 66 | SoD Accounting Rules | accounting | ops.sod.accounting | Compliance | Accounting-specific SoD extensions | Bank reconciliation SoD enforcement |
| 67 | Report Audit Trail | accounting | ops.report.audit | Compliance | Track every report generation | Who ran what report, when, with what filters |
| 68 | KPI Definitions | kpi | ops.kpi | BI | 50+ pre-built KPI definitions | 13 categories covering all business functions |
| 69 | KPI Boards | kpi | ops.kpi.board | BI | Persona-specific dashboard boards | IT Admin sees only system KPIs; CEO sees everything |
| 70 | KPI Widgets | kpi | ops.kpi.widget | BI | Configurable dashboard widgets per board | Sequence, size, refresh settings per widget |
| 71 | KPI Values | kpi | ops.kpi.value | BI | Historical KPI value storage | Time-series storage for trend analysis |
| 72 | KPI Time Series | kpi | ops.kpi.get_time_series() | BI | Daily/weekly/monthly trend data | Sparkline data for dashboard cards |
| 73 | KPI Breakdown | kpi | ops.kpi.get_breakdown() | BI | Group-by analysis (branch, BU, company) | Donut/bar charts for dimensional analysis |
| 74 | KPI Comparison | kpi | ops.kpi.get_comparison() | BI | MoM and YoY comparison | Automatic prior-period calculation |
| 75 | KPI Auto-Refresh | kpi | OWL systray component | BI | Configurable auto-refresh (30s to 10min) | Systray toggle for live dashboard updates |
| 76 | KPI Alert System | kpi | ops.kpi.board.get_chart_data() | BI | Threshold-based KPI alerts | Critical/warning/success severity levels |
| 77 | ApexCharts Integration | kpi | chart_components.js | BI | Professional chart rendering | Area, bar, donut, sparkline chart types |
| 78 | Debranding | theme | SCSS + OWL patches | UI | Remove all Odoo branding | Full white-label: navbar, title, favicon, links |
| 79 | Login Page | theme | _login.scss | UI | Split-screen branded login | Corporate login experience |
| 80 | Skin System | theme | ops.theme.skin model + ir.asset | UI | 10-color palette presets | Bootstrap compile-time color injection |
| 81 | Chatter Position | theme | chatter_position_patch.js | UI | Toggle chatter between bottom and side | Per-user preference persisted to database |
| 82 | Sidebar Control | theme | ops_sidebar.js | UI | Collapsible sidebar with size options | Invisible/small/large modes per user |
| 83 | Favicon Override | theme | theme_controller.py | UI | Custom favicon per company | Uploaded via settings, served via controller |
| 84 | Group Expand/Collapse | theme | ops_group_controls.js | UI | Expand/collapse all groups in list views | Cog menu controls for grouped views |
| 85 | Auto-Refresh Systray | theme | ops_auto_refresh.js | UI | Systray button for page auto-refresh | Configurable interval, visual indicator |
| 86 | Home Menu Customization | theme | ops_home_menu.js | UI | Enhanced home menu display | Branded app menu experience |
| 87 | Dialog Patches | theme | ops_dialog_patch.js | UI | Styled confirmation/warning dialogs | Corporate-branded dialog appearance |
| 88 | Report CSS | theme | ops_report_css.xml | Printing | Corporate report styling | Branded PDF output across all documents |
| 89 | External Layout | theme | ops_external_layout.xml | Printing | Custom external document layout | Corporate header/footer for printed documents |
| 90 | REST API v1 | core | controllers/ops_matrix_api.py | Integration | Full RESTful API | 10+ endpoints with key auth + rate limiting |

---

## 3. ops_matrix_core -- Foundation Module

### 3.1 Organizational Structure

**Branch Model (`ops.branch`)**
- Full organizational branch with address, manager, contact info
- Links to `res.company` for multi-company alignment
- Active/archive toggle for soft deactivation
- Used as the primary isolation dimension across all transactional models

**Business Unit Model (`ops.business.unit`)**
- Cross-branch organizational grouping (e.g., "Retail", "Wholesale", "Corporate")
- BU Leader can see all branches within their assigned BU
- Independent from company structure -- enables matrix reporting

**Matrix Mixin (`ops.matrix.mixin`)**
- Abstract mixin inherited by all transactional models
- Automatically adds: `ops_branch_id`, `ops_business_unit_id`, `ops_persona_id`
- Computes `ops_company_id` from branch -> company relationship
- Provides `ops_analytic_distribution` for automatic analytic tagging

### 3.2 Persona Engine

**18 Pre-Configured Personas:**

| Code | Persona | Level | SoD Authority |
|------|---------|-------|---------------|
| FIN_CTRL | Financial Controller | Executive | Anchor -- validates invoices, posts JE, no payments |
| CEO | Chief Executive Officer | Executive | Full authority across all operations |
| CFO | Chief Financial Officer | Executive | Full financial authority |
| SALES_LEADER | Sales Leader | Director | Sales approval, cost/margin visibility |
| SALES_MGR | Sales Manager | Manager | Branch-level sales management |
| PURCHASE_MGR | Purchase Manager | Manager | Branch-level purchase operations |
| LOGISTICS_MGR | Logistics Manager | Manager | Inventory and warehouse operations |
| TREASURY | Treasury Officer | Manager | Payment execution, cash management |
| HR_MGR | HR Manager | Manager | Human resource operations |
| CHIEF_ACCT | Chief Accountant | Manager | Full accounting operations |
| SYS_ADMIN | System Administrator | Technical | System config, NO business data access |
| SALES_REP | Sales Representative | Operational | Own records only |
| PURCHASE_OFF | Purchase Officer | Operational | Own records only |
| LOG_CLERK | Logistics Clerk | Operational | Own records only |
| ACCOUNTANT | Accountant | Operational | Assigned accounting tasks |
| AR_CLERK | AR Clerk | Operational | Receivables processing |
| AP_CLERK | AP Clerk | Operational | Payables processing |
| TECH_SUPPORT | Technical Support | Operational | System support tasks |

Each persona carries **SoD authority fields** that define fine-grained permissions:
- `can_modify_product_master` -- Product catalog changes
- `can_access_cost_prices` -- Cost price visibility
- `can_validate_invoices` -- Invoice posting authority
- `can_post_journal_entries` -- Journal entry posting
- `can_execute_payments` -- Payment execution authority
- `can_adjust_inventory` -- Inventory adjustment authority
- `can_manage_pdc` -- Post-dated cheque management

**Persona Delegation (`ops.persona.delegation`)**
- Temporary authority transfer between users
- Start/end date enforcement
- Automatic expiry -- no forgotten elevated permissions
- Full audit trail of delegation events

### 3.3 Security Framework

**20+ Security Groups:**

| Group | XML ID | Purpose |
|-------|--------|---------|
| OPS User | `group_ops_user` | Basic access -- view branch/BU info |
| OPS Manager | `group_ops_manager` | Manage operations within branch |
| OPS Administrator | `group_ops_admin_power` | Full OPS feature access (no system bypass) |
| Matrix Administrator | `group_ops_matrix_administrator` | Full matrix configuration |
| IT Administrator | `group_ops_it_admin` | System admin, BLIND to business data |
| Can See Product Costs | `group_ops_see_cost` | Cost price visibility |
| Can See Profit Margins | `group_ops_see_margin` | Margin data visibility |
| Can See Stock Valuation | `group_ops_see_valuation` | Inventory valuation visibility |
| Price Manager | `group_ops_price_manager` | Can modify selling prices on SO lines |
| Executive / CEO | `group_ops_executive` | Read-only oversight across all entities |
| CFO / Owner | `group_ops_cfo` | Full financial access, all entities |
| Branch Manager | `group_ops_branch_manager` | Single branch operations |
| BU Leader | `group_ops_bu_leader` | Multi-branch within BU |
| Cross-Branch BU Leader | `group_ops_cross_branch_bu_leader` | Full BU cross-branch visibility |
| Sales Manager | `group_ops_sales_manager` | Sales + cost/margin visibility |
| Purchase Manager | `group_ops_purchase_manager` | Purchase + cost visibility |
| Inventory Manager | `group_ops_inventory_manager` | Inventory + valuation visibility |
| Finance Manager | `group_ops_finance_manager` | Full financial visibility |
| Cost Controller | `group_ops_cost_controller` | Cost and margin controls |
| Accountant / Controller | `group_ops_accountant` | Full accounting data access |
| Treasury Officer | `group_ops_treasury` | Cash/payment management |
| Compliance Officer | `group_ops_compliance_officer` | Governance/audit read access |
| Can Export Data | `group_ops_can_export` | Secure export permission |
| Product Approver | `group_ops_product_approver` | Approve product creation requests |

**IT Admin Blindness -- 24 Blocked Models:**

Core (17 models):
`sale.order`, `sale.order.line`, `purchase.order`, `purchase.order.line`, `account.move`, `account.move.line`, `account.payment`, `account.bank.statement`, `account.bank.statement.line`, `stock.picking`, `stock.move`, `stock.move.line`, `stock.quant`, `stock.valuation.layer`, `product.pricelist`, `product.pricelist.item`, `account.analytic.line`

Accounting (7 models):
`ops.pdc.receivable`, `ops.pdc.payable`, `ops.budget`, `ops.budget.line`, `ops.asset`, `ops.asset.category`, `ops.asset.depreciation`

Rule: `[(0, '=', 1)]` -- mathematically impossible domain that returns zero records.

### 3.4 Segregation of Duties (SoD)

**6 Default SoD Rules (admin-activated):**

| Rule | Model | Actions | Threshold | Purpose |
|------|-------|---------|-----------|---------|
| SO Create + Confirm | sale.order | create / confirm | $5,000 | Independent review of sales commitments |
| PO Create + Confirm | purchase.order | create / confirm | $5,000 | Independent approval of purchases |
| Invoice Create + Post | account.move | create / post | $0 (all) | Prevent unauthorized financial recording |
| Payment Create + Post | account.payment | create / post | $2,000 | Dual control over cash disbursements |
| Inventory Create + Approve | stock.picking | create / approve | $0 (all) | Independent review of stock changes |
| Bank Recon + Approve | ops.bank.reconciliation | reconcile / approve | $0 (all) | Independent review of cash positions |

All rules ship **disabled** (`enabled=False`) -- administrators explicitly enable after reviewing company policy. Rules can be configured with:
- Blocking mode (hard stop) or warning mode (log only)
- Configurable monetary thresholds
- System rule flag (prevents accidental deletion)

### 3.5 Governance Rules Engine

**8+ Pre-Configured Governance Rule Templates:**

| Code | Rule | Model | Trigger | Action |
|------|------|-------|---------|--------|
| GR_SO_001 | High Value Order >$50K | sale.order | on_create | Require approval (Sales Manager) |
| GR_SO_002 | Discount >20% | sale.order | on_write | Require approval (Sales Leader) |
| GR_SO_003 | Credit Limit Warning | sale.order | on_create | Warning (90% of limit) |
| GR_PO_001 | PO >$50K | purchase.order | on_create | Require approval (Purchase Manager) |
| GR_PO_002 | PO >$100K | purchase.order | on_create | Require approval (CEO) |
| GR_INV_* | Invoice rules | account.move | on_create | Configurable |
| GR_PAY_* | Payment rules | account.payment | on_create | Configurable |
| GR_STOCK_* | Stock rules | stock.picking | on_create | Configurable |

Rules use **code-based conditions** (`condition_code` field) that are evaluated at runtime against the record. This allows complex business logic (e.g., checking discount percentages across order lines) without custom development.

### 3.6 3-Way Match

The 3-way match system compares:
1. **Purchase Order** (what was ordered)
2. **Goods Receipt Note** (what was received)
3. **Vendor Invoice** (what was billed)

Status values:
- `not_applicable` -- Non-purchase invoices
- `matched` -- All three documents align
- `blocked` -- Mismatch detected, invoice cannot be posted
- `override_approved` -- Manager approved the mismatch

Override workflow: blocked invoice -> manager opens Override Wizard -> provides reason -> invoice unblocked.

### 3.7 SLA Engine

**4 Pre-Configured SLA Templates:**

| Template | Target | Response | Resolution |
|----------|--------|----------|------------|
| Platinum Support | sale.order | 1 hour | 4 hours |
| Gold Support | sale.order | 4 hours | 24 hours |
| IT Critical | stock.picking | 2 hours | 8 hours |
| Standard Sales | sale.order | 24 hours | 24 hours |

SLA instances are automatically created when documents match template criteria. Timer-based tracking with:
- Automatic breach detection
- Escalation notifications
- SLA performance reporting

### 3.8 Approval Workflow

- **Multi-level approval chains** defined per governance rule
- **Approval requests** created automatically when rules trigger
- **Recall wizard** -- requestor can recall pending approvals with mandatory reason
- **Reject wizard** -- approver provides mandatory rejection reason
- **Approval locking** (`ops.approval.mixin`) -- document fields locked during approval
- **State injection** -- `waiting_approval` state added to sale.order and other models

### 3.9 Enterprise Security Features

**Session Management (`ops.session.manager`)**
- Track active user sessions with IP, user agent, login time
- Force logout capability for compromised accounts
- Concurrent session limits per user/group

**IP Whitelisting (`ops.ip.whitelist`)**
- Allow/deny IP ranges per user or globally
- Supports CIDR notation
- Enforcement at login and API authentication

**Data Archival (`ops.data.archival` + `ops.archive.policy`)**
- Age-based archival policies (e.g., archive orders older than 2 years)
- Cron-driven automatic archival
- Configurable per model with retention periods

**Performance Monitoring (`ops.performance.monitor`)**
- System metrics tracking (query time, memory, disk)
- Threshold-based alerting
- Historical performance data for capacity planning

**Security Audit (`ops.security.audit`)**
- Log security-relevant events: admin overrides, SoD violations, failed logins
- Compliance dashboard for security officers
- Export capability for external audit tools

**Corporate Audit Trail (`ops.corporate.audit.log`)**
- SOX/ISO/GDPR-compliant immutable audit log
- Captures: user, action, model, record, timestamp, IP, user agent
- Sequential numbering (ir.sequence) for tamper detection
- Cannot be deleted or modified after creation

### 3.10 Compliance Wizards

**Persona Drift Detection (`ops.persona.drift.wizard`)**
- Analyzes current permissions vs assigned persona definition
- Detects: `extra_permissions`, `missing_permissions`, `drift`, `no_persona`
- Severity levels: `ok`, `warning`, `critical`
- Generates compliance report for all or selected users

**Audit Evidence Package (`ops.audit.evidence.wizard`)**
- Generates Excel workbook for external auditors
- 7 configurable sheets:
  1. IT Admin Blindness Rules
  2. Security Groups
  3. User-Group Assignment Matrix
  4. Record Rules
  5. ACL Coverage Analysis
  6. SoD Rules & Violations
  7. Persona Assignments
- One-click generation for SOX/ISO audit preparation

**Secure Export Wizard (`ops.secure.export.wizard`)**
- Matrix-filtered data export (branch isolation enforced in export)
- Field visibility rules applied to exported columns
- Cost/margin access checks on financial fields
- Full audit logging: who exported what, when, how many records
- XLSX and CSV format support

### 3.11 Data Entry Wizards

**Excel Sale Order Import (`ops.sale.order.import.wizard`)**
- Upload Excel file with order line data
- Column mapping for product, quantity, unit price, UoM
- Validation: product existence, numeric values, required fields
- Error reporting with line-by-line detail
- Batch import into existing or new sale order

**Excel Purchase Order Import (`ops.purchase.order.import.wizard`)**
- Same capabilities as SO import, for purchase orders
- Vendor-specific product matching
- Tax and account mapping

---

## 4. ops_matrix_accounting -- Finance Module

### 4.1 Post-Dated Cheques (PDC)

**Receivable PDC (`ops.pdc.receivable`)**
Lifecycle: Register -> Under Collection -> Collected / Bounced / Returned

Fields: cheque number, bank name, drawer name, amount, date, maturity date, branch, partner.

Journal entries:
- Register: Debit PDC Receivable, Credit Customer Account
- Collect: Debit Bank, Credit PDC Receivable
- Bounce: Reverse collection entry + penalty charges

**Payable PDC (`ops.pdc.payable`)**
Lifecycle: Draft -> Issued -> Cleared / Bounced

Journal entries:
- Issue: Debit Vendor Account, Credit PDC Payable
- Clear: Debit PDC Payable, Credit Bank
- Bounce: Reverse clearing entry

**PDC Sequences:** Auto-generated reference numbers via ir.sequence.
**Menu Structure:** Separate menus for Receivable PDC, Payable PDC, and PDC Reports.

### 4.2 Fixed Asset Management

**Asset Categories (`ops.asset.category`)**
- Depreciation method: straight-line, declining balance
- Useful life in months
- Default accounts: asset, depreciation, expense
- Journal assignment
- Salvage value percentage

**Assets (`ops.asset`)**
- Full asset lifecycle: draft -> running -> fully_depreciated -> disposed
- Acquisition date, gross value, salvage value
- Computed: accumulated depreciation, net book value
- Branch and BU assignment
- Linked to purchase invoice for acquisition tracking

**Depreciation Schedule (`ops.asset.depreciation`)**
- Auto-generated depreciation lines based on category settings
- Cron job (`cron_depreciation.xml`) for monthly automatic posting
- Manual depreciation trigger via wizard
- Journal entry generation for each depreciation period

**Asset Disposal Wizard (`ops.asset.disposal.wizard`)**
- Calculate disposal gain/loss: proceeds - net book value
- Generate disposal journal entry
- Update asset status to disposed
- Record disposal date and method

**Asset Impairment Wizard (`ops.asset.impairment.wizard`)**
- IFRS-compliant impairment loss recognition
- Reduce carrying amount to recoverable amount
- Generate impairment loss journal entry
- Recalculate remaining depreciation schedule

### 4.3 Budget Management

**Budget (`ops.budget`)**
- Budget definition per fiscal period
- Budget lines by account, analytic account, branch
- Status: draft -> confirmed -> validated -> done -> cancelled
- Approval workflow integration

**Budget Lines (`ops.budget.line`)**
- Planned amount per account/period
- Actual amount (computed from posted entries)
- Variance calculation: planned - actual
- Percentage utilization

**Budget vs Actual Wizard (`ops.budget.vs.actual.wizard`)**
- Variance analysis report
- Period filtering
- Branch/BU filtering
- PDF and Excel output

### 4.4 IFRS 16 Lease Accounting

**Lease Model (`ops.lease`)**
- Right-of-Use (ROU) asset recognition
- Lease liability calculation
- Payment schedule generation
- Interest expense calculation using implicit rate
- Automatic ROU amortization journal entries
- Lease modification handling

### 4.5 Fiscal Period Management

**Fiscal Period (`ops.fiscal.period`)**
- Define fiscal years and periods (monthly, quarterly, custom)
- Period status: open, soft_lock, closed
- Soft lock: warnings on posting but not blocked
- Hard lock: completely prevents posting to closed periods

**Period Close Wizard (`ops.period.close.wizard`)**
- Guided step-by-step period close process
- Configurable checklist items:
  - Bank reconciliation completed
  - All invoices posted
  - Depreciation run
  - Accruals recorded
  - Currency revaluation done
- Soft lock vs hard lock option
- Audit trail of close events

### 4.6 FX Revaluation

**FX Revaluation Wizard (`ops.fx.revaluation.wizard`)**
- Calculate unrealized foreign exchange gains and losses
- Account type filtering: all, receivable/payable only, bank only
- Multi-currency support using Odoo's currency rates
- Two-step workflow: Calculate (preview) -> Post (create journal entries)
- Branch filtering for revaluation scope
- Gain/loss accounts configurable in company settings

### 4.7 Consolidation Intelligence

**Unified Consolidation Wizard (`ops.consolidation.intelligence.wizard`)**
- Single wizard entry point for 4 consolidation reports
- Uses Shape B (hierarchy) data contracts from Report Engine v2

**4 Consolidation Report Types:**

| Report | Model | Description |
|--------|-------|-------------|
| Company Consolidation P&L | ops.company.consolidation | Company-level income statement |
| Branch P&L | ops.branch.report | Per-branch profit & loss |
| BU Report | ops.business.unit.report | Business unit performance |
| Consolidated Balance Sheet | ops.consolidated.balance.sheet | Multi-entity balance sheet |

### 4.8 Report Engine v2

**Architecture:**
- **Abstract base class** (`ops.base.report.wizard`, 850+ lines) provides all shared functionality
- **3 shape templates**: Lines (tabular), Hierarchy (tree), Matrix (crosstab)
- **Data contracts**: Each wizard returns standardized data dicts consumed by QWeb templates
- **Template system**: Save/load filter configurations as reusable report templates
- **Output formats**: PDF, Excel (XLSX), HTML

**Report Engine v2 XML Structure:**
```
report/ops_report_base.xml         -- Base template components
report/ops_report_shape_lines.xml  -- Tabular line-item layout
report/ops_report_shape_hierarchy.xml -- Hierarchical tree layout
report/ops_report_shape_matrix.xml -- Cross-tab matrix layout
report/ops_report_actions.xml      -- ir.actions.report definitions
report/ops_report_configs.xml      -- Default report configurations
```

**Base Wizard Provides:**
- `_get_engine_name()` -- Subclass identification
- Template loading/saving via `ops.financial.report.config`
- Common validation: date ranges, branch access, period locks
- "The Black Box" -- every report generation is audit-logged to `ops.report.audit`
- Color scheme generation for charts and visual elements
- Number formatting (currency, percentage, integer)
- Currency resolution from company settings
- IT Admin Blindness via `ops.intelligence.security.mixin`
- Branch isolation via security mixin

**14 Report Wizards:**

| Wizard | Key | Shape | Output |
|--------|-----|-------|--------|
| General Ledger | ops.gl.wizard | Lines | PDF/Excel/HTML |
| Trial Balance | ops.tb.wizard | Lines | PDF/Excel/HTML |
| Profit & Loss | ops.pnl.wizard | Hierarchy | PDF/Excel/HTML |
| Balance Sheet | ops.bs.wizard | Hierarchy | PDF/Excel/HTML |
| Cash Flow | ops.cf.wizard | Hierarchy | PDF/Excel/HTML |
| Aged Receivables/Payables | ops.aged.wizard | Lines | PDF/Excel/HTML |
| Partner Ledger | ops.partner.ledger.wizard | Lines | PDF/Excel/HTML |
| Treasury Report | ops.treasury.report.wizard | Lines | PDF/Excel |
| Asset Report | ops.asset.report.wizard | Lines | PDF/Excel |
| Inventory Report | ops.inventory.report.wizard | Lines | PDF/Excel |
| Daily Reports (Bank/Cash/Day) | ops.daily.reports.wizard | Lines | PDF/Excel |
| Budget vs Actual | ops.budget.vs.actual.wizard | Lines | PDF/Excel |
| Consolidation Intelligence | ops.consolidation.intelligence.wizard | Hierarchy | PDF/Excel/HTML |
| Period Close | ops.period.close.wizard | N/A (process) | Checklist |

### 4.9 Additional Accounting Features

**Recurring Journal Entries (`ops.recurring` + `ops.journal.template`)**
- Define recurring journal entry templates
- Cron-driven automatic execution
- Configurable frequency: daily, weekly, monthly, quarterly, annual

**Customer Followup (`ops.followup`)**
- Multi-level payment followup definitions
- Automated email sending via cron
- Configurable delays between followup levels
- Partner-level followup tracking

**Bank Reconciliation (`ops.bank.reconciliation`)**
- Enhanced bank statement reconciliation
- SoD enforcement: reconciler != approver
- Matching algorithm for auto-reconciliation

**Interbranch Transfer (`ops.interbranch.transfer`)**
- Accounting entries for goods/value transfers between branches
- Automatic balancing journal entries
- Branch validation (source != destination)

**Profitability Analysis (`ops.matrix.profitability.analysis`)**
- Multi-dimensional profit analysis
- Dimensions: branch, business unit, product category, customer segment
- Revenue, COGS, gross margin, net margin calculations

**Trend Analysis (`ops.trend.analysis`)**
- Historical data comparison engine
- Period types: MoM (month-over-month), QoQ, YoY
- Percentage and absolute change calculations

**Matrix Snapshot (`ops.matrix.snapshot`)**
- Point-in-time capture of financial state
- Cron-driven periodic snapshots
- Used for dashboard data and trend reporting

### 4.10 Report Styling & Layout

**Corporate Report Layout** (`report/ops_corporate_report_layout.xml`)
- Branded header with company logo
- Corporate footer with document numbering
- Consistent typography and spacing

**Invoice & Payment Reports**
- `report/ops_report_invoice.xml` -- Branded customer invoice
- `report/ops_report_payment.xml` -- Branded payment receipt

**Excel Rendering Infrastructure**
- `report/excel_styles.py` -- Centralized Excel style definitions
- `report/ops_excel_renderer.py` -- Abstract Excel file generation
- Consistent formatting across all Excel exports

---

## 5. ops_kpi -- Business Intelligence Module

### 5.1 KPI Definitions

**50+ Pre-Built KPIs Across 13 Categories:**

| Category | KPI Count | Key Metrics |
|----------|-----------|-------------|
| Sales | 8 | Revenue MTD/YTD, Orders MTD, Avg Order Value, Gross Margin %, Quotation Count, Quotation-to-Order Rate, Top Products |
| Purchase | 6 | PO Value MTD, PO Count, Pending POs, Receipt Count, Avg PO Value, Supplier Count |
| Inventory | 5 | Stock Value, SKU Count, Low Stock Items, Dead Stock, Stock Turnover |
| Finance | 4 | Revenue Total, Expense Total, Net Income, Cash Balance |
| Receivable | 6 | AR Total, AR Overdue, AR Overdue %, AR Aging 30/60/90, Average Collection Days |
| Payable | 5 | AP Total, AP Overdue, AP Overdue %, Average Payment Days, Upcoming Payments |
| PDC | 4 | PDC Registered, PDC Deposited, PDC Bounced, PDC Issued |
| Treasury | 3 | Cash Balance, Cash Inflows, Cash Outflows |
| Budget | 2 | Budget Utilization %, Budget Variance |
| Asset | 2 | Total NBV, Depreciation Due |
| Governance | 2 | 3-Way Match Rate, Pending Approvals |
| System | 3 | Active Users, Error Rate, API Request Count |
| Operations | 2 | Delivery On-Time %, Average Lead Time |

### 5.2 KPI Configuration

Each KPI definition includes:
- `source_model` -- Odoo model to query
- `calculation_type` -- sum, count, average, custom
- `measure_field` -- Field to aggregate
- `domain_filter` -- Odoo domain for record filtering
- `date_field` -- Field for period filtering
- `default_period` -- this_month, this_quarter, this_year
- `format_type` -- currency, integer, percentage, decimal
- `scope_type` -- company, bu, branch, own
- `trend_direction` -- up_good, down_good (for color coding)
- `color` -- Hex color for chart rendering
- `icon` -- FontAwesome icon class

### 5.3 KPI Security

**IT Admin Blindness:** IT administrators see ONLY system-category KPIs (active users, error rate, API requests). All business KPIs return zero values with "Access restricted" message.

**Cost/Margin Access:** KPIs tagged with `requires_cost_access` or `requires_margin_access` are filtered based on the user's `group_ops_see_cost` / `group_ops_see_margin` membership.

**Branch Isolation:** KPIs with `scope_type='branch'` automatically filter data to the user's allowed branches.

**Persona-Based Board Access:** Each dashboard board specifies which personas can view it, using both `persona_codes` (comma-separated) and `persona_ids` (Many2many).

### 5.4 KPI Boards (Persona-Specific Dashboards)

**10+ Pre-Configured Boards:**

| Board | Type | Personas | KPI Count | Key Focus |
|-------|------|----------|-----------|-----------|
| IT Admin Dashboard | system | SYS_ADMIN | 3 | System health only |
| CEO Executive Overview | executive | CEO | 8 | Cross-entity overview |
| CFO Financial Command | finance | CFO | 14 | Full financial picture |
| Branch Manager Hub | branch | Branch Mgr | 12 | Single branch performance |
| Sales Manager Dashboard | sales | Sales Mgr | 10 | Sales team performance |
| Purchase Manager Hub | purchase | Purchase Mgr | 9 | Procurement metrics |
| Sales Rep My Sales | sales | Sales Rep | 4 | Own records only |
| AR Clerk Receivables | receivable | AR Clerk | 6 | Receivables management |
| AP Clerk Payables | payable | AP Clerk | 5 | Payables management |
| Treasury Dashboard | treasury | Treasury | 8 | Cash management |

### 5.5 Dashboard Features

**KPI Cards**
- Large value display with format-aware rendering (currency symbol, percentage sign)
- Trend indicator: arrow up/down with color (green = good, red = bad)
- Trend percentage: MoM comparison
- Sparkline: mini area chart showing daily values

**Charts (ApexCharts)**
- Area charts: revenue/order trends over time
- Bar charts: branch comparison for selected KPIs
- Donut charts: dimensional breakdowns (by branch, by BU)
- Sparkline: compact inline trend indicators

**Alert System**
- Configurable threshold per board (`alert_threshold` field, default -10%)
- Severity levels: `critical` (>20% decline), `warning` (>10% decline), `success` (>15% improvement)
- Alert messages include formatted values and percentage changes

**Auto-Refresh**
- Configurable interval: 30 seconds, 1/2/5/10 minutes, or manual only
- OWL systray component for global toggle
- Per-board refresh interval setting

**Filter System**
- Period selector: this_month, last_month, this_quarter, this_year, last_year, custom
- Branch filter (populated from user's allowed branches)
- Business unit filter

### 5.6 KPI Data Methods

**`compute_value(period, branch_ids)`** -- Calculate current KPI value with domain, period, and branch filtering.

**`get_time_series(period, granularity)`** -- Return daily/weekly/monthly data points for trend charts. Returns `{data: [{date, value}, ...]}`.

**`get_breakdown(period, group_by)`** -- Return value grouped by dimension (branch, BU, company). Returns `{data: [{label, value}, ...]}`.

**`get_comparison(period)`** -- Return MoM and YoY comparisons. Returns `{current, previous_month, previous_year, mom_change, yoy_change}`.

**`get_chart_data(dashboard_id, period)`** -- Board-level method returning all widget data, trend charts, breakdown charts, comparison data, alerts, and filter options in a single RPC call.

---

## 6. ops_theme -- UI & Branding Module

### 6.1 Architecture Philosophy

> "Odoo 19 owns the layout, OPS owns the colors."

The theme works within Odoo's existing OWL/Bootstrap framework rather than fighting it. It uses:
- **SCSS compile-time** variables to replace Odoo purple with corporate colors
- **Runtime CSS variables** for skin switching
- **OWL patches** for component-level customization (not MutationObserver)

### 6.2 Five Core Features

**1. Debranding**
- `_primary_variables.scss`: Replaces `$o-community-color` (#71639e -> #1e293b)
- `_debranding.scss`: Hides Odoo logos, links, and references via CSS
- `debranding.js`: OWL registry cleanup for JavaScript-rendered branding
- Favicon override via controller endpoint (`/ops_theme/favicon`)
- Browser tab title customization

**2. Login Page**
- `_login.scss`: Split-screen branded login experience
- Left panel: company branding and messaging
- Right panel: login form
- Responsive design for mobile devices

**3. Skin System**
- 10-color palette definitions compiled into CSS bundles
- Colors: brand, action, success, warning, danger, info, background, surface, text, border
- Presets stored in `ops.theme.skin` model
- Applied via `ir.asset` SCSS variable replacement at Bootstrap compile time
- Skin data seeded via `data/ops_theme_skin_data.xml`

**4. Chatter Position**
- Toggle between bottom (default) and side placement
- Per-user preference stored in `res.users.ops_chatter_position`
- `chatter_position_patch.js`: OWL patch on chatter component
- `_chatter_position.scss`: Layout styles for side chatter
- Toggle endpoint: `/ops_theme/toggle_chatter`

**5. Clean UI**
- Remove odoo.com links and branding via CSS + OWL registry cleanup
- No MutationObserver (performance-safe)
- `_ops_overrides.scss`: Structural theme overrides (navbar, buttons, radius, shadow)

### 6.3 Additional UI Features

**Sidebar Control** (`ops_sidebar.js` + `_ops_sidebar.scss`)
- Three sidebar modes: invisible, small, large
- Per-user preference persisted via `/ops_theme/set_sidebar_type`
- Smooth CSS transitions

**Group Expand/Collapse** (`ops_group_controls.js`)
- Cog menu integration for list views with grouping
- "Expand All" and "Collapse All" buttons
- Works with any grouped list view

**Auto-Refresh** (`ops_auto_refresh.js`)
- Systray component for page-level auto-refresh
- Visual indicator when active
- Configurable interval

**Home Menu** (`ops_home_menu.js` + `ops_home_menu.xml`)
- Enhanced application menu appearance
- Corporate branding integration

**Dialog Patches** (`ops_dialog_patch.js`)
- Corporate-styled confirmation and warning dialogs
- Consistent visual language

### 6.4 Report Styling

**Report CSS** (`report/ops_report_css.xml`)
- Print-optimized styles for all PDF reports
- Corporate typography and spacing
- Page break controls

**External Layout** (`report/ops_external_layout.xml`)
- Custom header/footer for external documents
- Company logo placement
- Document numbering

### 6.5 Theme Controller Endpoints

| Endpoint | Auth | Method | Purpose |
|----------|------|--------|---------|
| `/ops_theme/favicon` | public | HTTP | Serve company favicon |
| `/favicon.ico` | public | HTTP | Override default favicon route |
| `/ops_theme/data` | public | JSONRPC | Return theme settings as JSON |
| `/ops_theme/toggle_chatter` | user | JSONRPC | Toggle chatter position |
| `/ops_theme/set_sidebar_type` | user | JSONRPC | Save sidebar type preference |
| `/ops_theme/get_preferences` | user | JSONRPC | Get user's theme preferences |

### 6.6 Asset Bundle Architecture

| Bundle | Files | Purpose |
|--------|-------|---------|
| `web._assets_primary_variables` | `_colors_light.scss`, `_primary_variables.scss` | Bootstrap compile-time color injection |
| `web.assets_frontend` | `_login.scss` | Login page styles |
| `web.assets_backend` | 12 SCSS + 10 JS + 6 XML files | Backend structural overrides |

---

## 7. API Capabilities

### 7.1 REST API v1

**Base URL:** `/api/v1/ops_matrix`

**Authentication:** API key via `X-API-Key` header or `api_key` query parameter. Keys are managed in `ops.api.key` model, scoped to personas.

**Rate Limiting:** 1000 requests/hour per API key (configurable).

**Audit Logging:** Every API request is logged to `ops.audit.log` with:
- Endpoint, HTTP method, IP address, user agent
- Status code, response time, error message (if any)
- API key reference and persona context

### 7.2 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/ops_matrix/health` | GET | Public | Health check and API version info |
| `/api/v1/ops_matrix/me` | GET | API Key | Current user and persona info |
| `/api/v1/ops_matrix/branches` | GET | API Key | List accessible branches |
| `/api/v1/ops_matrix/branches/<id>` | GET | API Key | Branch detail |
| `/api/v1/ops_matrix/business_units` | GET | API Key | List accessible business units |
| `/api/v1/ops_matrix/business_units/<id>` | GET | API Key | Business unit detail |
| `/api/v1/ops_matrix/sales_analysis` | GET | API Key | Sales analysis with period/branch filters |
| `/api/v1/ops_matrix/approval_requests` | GET | API Key | List pending approval requests |
| `/api/v1/ops_matrix/approval_requests/<id>` | GET | API Key | Approval request detail |
| `/api/v1/ops_matrix/approval_requests/<id>/approve` | POST | API Key | Approve a request |
| `/api/v1/ops_matrix/approval_requests/<id>/reject` | POST | API Key | Reject a request (reason required) |
| `/api/v1/ops_matrix/stock_levels` | GET | API Key | Stock level by product/branch |

### 7.3 API Security

- API keys are linked to personas, inheriting that persona's access scope
- Branch isolation is enforced at the API level (users see only their branches)
- IT Admin Blindness applies to API users (IT persona cannot query business endpoints)
- Failed authentication attempts are logged with IP address
- Rate limiting prevents abuse (429 Too Many Requests)

### 7.4 API Response Format

```json
{
    "success": true,
    "data": { ... },
    "code": 200,
    "timestamp": "2026-02-13T12:00:00Z"
}
```

Error response:
```json
{
    "success": false,
    "error": "Description of the error",
    "code": 401
}
```

---

## 8. Report Catalog

### 8.1 Financial Reports (Report Engine v2)

| Report | Wizard Model | Shape | PDF | Excel | HTML | Filters |
|--------|-------------|-------|-----|-------|------|---------|
| General Ledger | ops.gl.wizard | Lines | Yes | Yes | Yes | Date range, accounts, branches, partners, journals |
| Trial Balance | ops.tb.wizard | Lines | Yes | Yes | Yes | As-of date, comparative period, branches |
| Profit & Loss | ops.pnl.wizard | Hierarchy | Yes | Yes | Yes | Date range, comparative period, branches, BU |
| Balance Sheet | ops.bs.wizard | Hierarchy | Yes | Yes | Yes | As-of date, comparative period, branches |
| Cash Flow Statement | ops.cf.wizard | Hierarchy | Yes | Yes | Yes | Date range, method (direct/indirect), branches |
| Aged Receivables | ops.aged.wizard | Lines | Yes | Yes | Yes | As-of date, aging buckets, partners, branches |
| Aged Payables | ops.aged.wizard | Lines | Yes | Yes | Yes | As-of date, aging buckets, partners, branches |
| Partner Ledger | ops.partner.ledger.wizard | Lines | Yes | Yes | Yes | Date range, partners, reconciliation status |

### 8.2 Treasury & Cash Reports

| Report | Wizard Model | Shape | PDF | Excel | Filters |
|--------|-------------|-------|-----|-------|---------|
| Treasury Report | ops.treasury.report.wizard | Lines | Yes | Yes | Date range, bank accounts, branches |
| Bank Book | ops.daily.reports.wizard | Lines | Yes | Yes | Date, bank journal |
| Cash Book | ops.daily.reports.wizard | Lines | Yes | Yes | Date, cash journal |
| Day Book | ops.daily.reports.wizard | Lines | Yes | Yes | Date, all journals |

### 8.3 Asset Reports

| Report | Wizard Model | Shape | PDF | Excel | Filters |
|--------|-------------|-------|-----|-------|---------|
| Asset Register | ops.asset.report.wizard | Lines | Yes | Yes | Categories, branches, status, date range |
| Depreciation Schedule | ops.asset.report.wizard | Lines | Yes | Yes | Categories, branches, period |

### 8.4 Consolidation Reports

| Report | Wizard Model | Shape | PDF | Excel | HTML | Filters |
|--------|-------------|-------|-----|-------|------|---------|
| Company P&L | ops.consolidation.intelligence.wizard | Hierarchy | Yes | Yes | Yes | Period, accounts |
| Branch P&L | ops.consolidation.intelligence.wizard | Hierarchy | Yes | Yes | Yes | Period, branches |
| BU Report | ops.consolidation.intelligence.wizard | Hierarchy | Yes | Yes | Yes | Period, business units |
| Consolidated BS | ops.consolidation.intelligence.wizard | Hierarchy | Yes | Yes | Yes | As-of date |

### 8.5 Budget Reports

| Report | Wizard Model | Shape | PDF | Excel | Filters |
|--------|-------------|-------|-----|-------|---------|
| Budget vs Actual | ops.budget.vs.actual.wizard | Lines | Yes | Yes | Period, budget, branches, accounts |

### 8.6 Inventory Reports

| Report | Wizard Model | Shape | PDF | Excel | Filters |
|--------|-------------|-------|-----|-------|---------|
| Stock Valuation | ops.inventory.report.wizard | Lines | Yes | Yes | Date, warehouse, branches, categories |
| Stock Movement | ops.inventory.report.wizard | Lines | Yes | Yes | Date range, products, branches |

### 8.7 Document Reports (Custom Layouts)

| Report | Template | Description |
|--------|----------|-------------|
| Sale Order / Quotation | ops_report_quotation.xml | Branded quotation with matrix dimensions |
| Purchase Order | ops_report_purchase.xml | Branded PO with approval status |
| Delivery Order | ops_report_delivery.xml | Branded delivery slip |
| Stock Availability | ops_report_stock_availability.xml | Product availability report |
| Customer Invoice | ops_report_invoice.xml | Branded invoice with 3-way match status |
| Payment Receipt | ops_report_payment.xml | Branded payment confirmation |

### 8.8 Report Security

- All report wizards inherit `ops.intelligence.security.mixin`
- IT Admin Blindness: financial reports return "Access Denied" for IT administrators
- Branch isolation: reports filter data to user's allowed branches
- Cost/margin fields: hidden in report output if user lacks visibility group
- Report Audit Trail: every report generation logged to `ops.report.audit` with wizard parameters, user, timestamp

### 8.9 HTML Report Controller

**Endpoint:** `/ops/report/html/<wizard_model>/<wizard_id>`

**Security Whitelist (14 wizard models):**
The controller only renders reports from whitelisted wizard models. All others return 403 Forbidden.

**Shape Templates:**
- Shape A (Lines): Tabular row-based layout for ledgers and listings
- Shape B (Hierarchy): Tree-based layout for P&L, BS, and consolidation reports
- Shape C (Matrix): Cross-tab layout for multi-dimensional analysis

---

## 9. Pre-Configured Data

### 9.1 Seed Templates

| Data File | Content | Count |
|-----------|---------|-------|
| `ops_persona_templates.xml` | Corporate persona definitions | 18 personas |
| `ops_user_templates.xml` | User configuration templates | Maps users to personas |
| `ops_sla_templates.xml` | SLA policy templates | 4 templates |
| `ops_product_templates.xml` | Product category defaults | Standard categories |
| `ops_governance_templates.xml` | Base governance configuration | Matrix structure |
| `ops_governance_rule_templates.xml` | Business rule templates | 8+ rules |
| `ops_default_data_clean.xml` | Default system configuration | Base settings |
| `ops_account_templates.xml` | Chart of accounts extensions | Account types |
| `ops_sod_default_rules.xml` | Segregation of duties rules | 5 core rules |
| `ops_sod_bank_rules.xml` | Bank reconciliation SoD | 1 banking rule |
| `field_visibility_rules.xml` | Field visibility defaults | Cost/margin rules |
| `product_rules.xml` | Product governance rules | Creation controls |

### 9.2 KPI Seed Data

| Data File | Content | Count |
|-----------|---------|-------|
| `ops_kpi_data.xml` | KPI definitions | 50+ KPIs |
| `ops_kpi_board_data.xml` | Persona-specific boards | 10+ boards |

### 9.3 Accounting Seed Data

| Data File | Content |
|-----------|---------|
| `ops_asset_data.xml` | Asset category defaults |
| `pdc_sequence.xml` | PDC reference number sequences |
| `sequences_advanced.xml` | Advanced sequence definitions |
| `ops_budget_templates.xml` | Budget structure templates |
| `followup_data.xml` | Customer followup level definitions |
| `ops_paperformat.xml` | Corporate paper format (A4 with margins) |
| `report_templates.xml` | Report configuration defaults |
| `report_templates_extra.xml` | Extended report configurations |

### 9.4 Theme Seed Data

| Data File | Content |
|-----------|---------|
| `ops_theme_skin_data.xml` | 10-color skin preset definitions |

### 9.5 Cron Jobs (Automated Tasks)

| Cron | Module | Schedule | Purpose |
|------|--------|----------|---------|
| Data Archival | core | Daily | Archive aged records per policy |
| Escalation | core | Hourly | SLA breach escalation notifications |
| KPI Computation | kpi | Per board setting | Refresh KPI values |
| Asset Depreciation | accounting | Monthly | Post depreciation journal entries |
| Recurring Journals | accounting | Per template | Execute recurring journal entries |
| Customer Followup | accounting | Weekly | Send payment reminder emails |
| Matrix Snapshot | accounting | Daily | Capture financial state snapshot |
| Performance Monitor | core | Hourly | System health check |

### 9.6 Security Groups & ACL Seed Data

| Data File | Content |
|-----------|---------|
| `ir_module_category.xml` | OPS module category definitions |
| `res_groups.xml` | 20+ security group definitions |
| `ir.model.access.csv` (core) | 165 ACL rules |
| `ir.model.access.csv` (accounting) | 246 ACL rules |
| `ir_rule.xml` | Branch isolation record rules |
| `ir_rule_it_blind.xml` | IT Admin blindness record rules |
| `ops_matrix_security_rules.xml` | Matrix-level record rules |
| `ops_corporate_audit_rules.xml` | Audit log protection rules |
| `ops_accounting_rules.xml` | Accounting record rules |
| `ops_asset_security.xml` | Asset module security rules |
| `ops_kpi_security.xml` | KPI access security rules |
| `technical_menu_restrictions.xml` | Technical menu hiding rules |

---

## 10. Integration Points

### 10.1 Standard Odoo Model Extensions

OPS Framework extends (via `_inherit`) the following standard Odoo models:

| Standard Model | OPS Module | Mixins Added | Key Fields Added | Key Behaviors Added |
|---------------|------------|--------------|------------------|---------------------|
| `sale.order` | core | governance, matrix, approval, SoD | ops_branch_id, ops_business_unit_id, state='waiting_approval' | Governance checks on confirm, SoD enforcement, branch auto-populate, credit limit checks |
| `sale.order.line` | core | -- | Field visibility (cost/margin) | Price editing restricted to Price Manager group |
| `purchase.order` | core | governance, approval, SoD | ops_branch_id, ops_business_unit_id | SoD on confirm, governance rules, branch propagation |
| `purchase.order.line` | core | -- | Field visibility | Cost visibility controls |
| `account.move` | core + accounting | matrix, approval, SoD | ops_branch_id, three_way_match_status, ops_source_order_id | 3-way match, SoD on posting, branch isolation |
| `account.move.line` | core | -- | -- | Branch isolation via parent move |
| `account.payment` | core | -- | ops_branch_id | SoD on posting, branch isolation |
| `stock.picking` | core | matrix, approval | ops_branch_id, ops_credit_blocked | Credit block enforcement, branch isolation |
| `stock.move` | core | matrix | ops_branch_id | Branch propagation from picking |
| `stock.quant` | core | -- | -- | Branch-filtered visibility |
| `stock.warehouse` | core | -- | ops_branch_id | Branch assignment |
| `stock.warehouse.orderpoint` | core | -- | ops_branch_id | Branch-filtered reorder rules |
| `product.product` | core | -- | Field visibility rules | Cost/margin visibility controls |
| `product.template` | core | -- | Field visibility rules | Cost/margin visibility controls |
| `product.pricelist` | core | -- | -- | IT Admin blindness |
| `res.partner` | core | -- | ops_branch_id, credit_limit fields | Branch assignment, credit tracking |
| `res.company` | core + accounting + theme | -- | 30+ OPS fields | Brand colors, report settings, matrix config |
| `res.users` | core | -- | ops_persona_ids, ops_branch_ids, ops_chatter_position, ops_sidebar_type | Persona assignment, branch access, theme preferences |
| `mail.message` | core | -- | -- | Branch-filtered message visibility |
| `ir.actions.report` | core | -- | -- | Governance enforcement on PDF generation |
| `account.report` | core | -- | -- | Standard report customization |

### 10.2 Mixin Architecture

| Mixin | Module | Purpose | Models Using It |
|-------|--------|---------|-----------------|
| `ops.matrix.mixin` | core | Branch/BU/persona propagation | sale.order, account.move, stock.picking, stock.move |
| `ops.governance.mixin` | core | Rule evaluation on write/create | sale.order, purchase.order |
| `ops.approval.mixin` | core | Document locking during approval | sale.order, purchase.order, account.move, stock.picking |
| `ops.segregation.of.duties.mixin` | core | SoD enforcement on state transitions | sale.order, purchase.order, account.move, account.payment |
| `ops.sla.mixin` | core | SLA timer attachment | sale.order, stock.picking |
| `ops.analytic.mixin` | core | Automatic analytic distribution | Financial models |
| `ops.intelligence.security.mixin` | accounting | IT Admin blindness + branch isolation for wizards | All report wizards |

### 10.3 Module Dependency Chain

```
base, web, mail, account, sale, purchase, stock, hr, analytic
                        |
                   ops_theme          (debranding, skins, UI)
                        |
                ops_matrix_core       (structure, security, governance)
                        |
              ops_matrix_accounting   (PDC, assets, budgets, reports)
                        |
                    ops_kpi           (dashboards, KPIs, charts)
```

### 10.4 External System Integration

**REST API:** Full CRUD-capable API for external systems (BI tools, mobile apps, custom dashboards). See Section 7.

**Excel Import:** Bulk data loading for sale and purchase orders via Excel files.

**Excel Export:** Secure, audited data export with field-level visibility controls.

**Audit Evidence:** Generate compliance documentation packages for external auditors (SOX, ISO 27001, GDPR).

**Email Integration:** Customer followup emails, SLA escalation notifications, approval request notifications.

---

## Appendix A: ACL Rule Summary

### ops_matrix_core (165 rules)

| Model Group | User (R) | Manager (RWC) | Admin (RWCD) | Notes |
|-------------|----------|----------------|--------------|-------|
| ops.branch | Yes | Yes | Yes | Branch isolation via record rules |
| ops.business.unit | Yes | Yes | Yes | BU isolation via record rules |
| ops.persona | Yes | Yes | Yes | Read-only for users |
| ops.approval.request | Yes | Yes | Yes | Filtered by assignee |
| ops.governance.rule | Yes | Yes | Yes | Admin-only modification |
| ops.segregation.of.duties | Yes | Yes | Yes | System rules protected |
| ops.three.way.match | Yes | Yes | Yes | Auto-created on invoice |
| ops.sla.template | Yes | Yes | Yes | Admin configuration |
| ops.sla.instance | Yes | Yes | Yes | Auto-created per SLA |
| ops.audit.log | -- | Read-only | Read-only | Immutable log |
| ops.corporate.audit.log | -- | -- | Read-only | Highest protection |
| ops.api.key | -- | -- | RWCD | Admin-only management |
| ... + 40 more model groups | | | | |

### ops_matrix_accounting (246 rules)

| Model Group | User | Manager | Admin | Finance | CFO | Notes |
|-------------|------|---------|-------|---------|-----|-------|
| ops.pdc.receivable | R | RWC | RWCD | RWC | RWCD | Branch-isolated |
| ops.pdc.payable | R | RWC | RWCD | RWC | RWCD | Branch-isolated |
| ops.asset | R | RWC | RWCD | RWC | RWCD | Category-filtered |
| ops.asset.category | R | R | RWCD | RWC | RWCD | Admin config |
| ops.budget | R | RWC | RWCD | RWC | RWCD | Period-locked |
| ops.budget.line | R | RWC | RWCD | RWC | RWCD | Budget-linked |
| ops.fiscal.period | R | R | RWCD | RWC | RWCD | Admin config |
| ops.lease | R | RWC | RWCD | RWC | RWCD | IFRS 16 |
| Report wizards | -- | -- | -- | RWCD | RWCD | Role-based access |
| ... + 30 more model groups | | | | | | |

---

## Appendix B: Competitive Positioning Summary

### vs. Odoo 19 Enterprise

OPS Framework on Community Edition provides most Enterprise-only accounting features (assets, budgets, consolidation, period close) plus capabilities Enterprise does NOT offer (persona engine, IT Admin blindness, SoD enforcement, multi-branch isolation, REST API, KPI center, debranding).

**Cost advantage:** Odoo Enterprise requires per-user licensing. OPS Framework runs on free Community Edition.

### vs. Third-Party ERP Add-Ons

Most Odoo add-on modules focus on single features (a PDC module, an asset module). OPS Framework is a **unified, integrated platform** where security, governance, and reporting work together as a cohesive system. The persona engine, SoD rules, and governance engine are woven through every feature -- they are not bolt-on additions.

### vs. Enterprise ERP (SAP, Oracle, Microsoft Dynamics)

OPS Framework brings **enterprise-grade governance and compliance** to the Odoo platform at a fraction of the cost and complexity of traditional ERP systems. Features like IT Admin Blindness, Segregation of Duties, Corporate Audit Trail, and Audit Evidence Packages are typically found only in SAP GRC or Oracle internal controls modules.

---

*Document generated: 2026-02-13 | OPS Framework v19.0*
*Total features cataloged: 90 | Total models: 95+ | Total ACL rules: 411+*
