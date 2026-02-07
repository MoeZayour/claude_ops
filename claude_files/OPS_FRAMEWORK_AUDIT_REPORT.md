# OPS Framework — Corporate Audit Report

**Date:** 2026-02-07
**Database:** mz-db | **Instance:** gemini_odoo19 | **Odoo Version:** 19.0
**Auditor:** Claude Code (Corporate Audit Team — 4 parallel agents)

---

## Executive Summary

The OPS Framework was subjected to a comprehensive 4-stream audit covering **security isolation**, **governance enforcement**, **data accuracy**, and **code quality**. The framework was seeded with realistic business data (5 branches, 4 business units, 18 users, 20 sales orders, 15 purchase orders, 29 accounting entries, 8 assets, 8 PDCs, 4 budgets) to simulate production conditions.

### Overall Scorecard

| Audit Stream | Pass | Fail | Warn | Total |
|-------------|------|------|------|-------|
| Security Isolation | 94 | 10 | 0 | 104 |
| Governance & Approvals | 111 | 0 | 9 | 120 |
| Data Accuracy & KPI | 53 | 1 | 10 | 64 |
| Code Quality | — | — | — | — |
| **TOTALS** | **258** | **11** | **19** | **288** |

**Overall Pass Rate: 89.6% (258/288)** | **Critical Issues: 4** | **High Issues: 4**

---

## PART 1: SECURITY ISOLATION AUDIT

### 1.1 IT Admin Financial Blindness ✅ PASS (5/5)

| Test | Result | Mechanism |
|------|--------|-----------|
| Invoices (account.move) | **BLOCKED** | ACL — no Accounting group |
| Payments (account.payment) | **BLOCKED** | ACL — no Accounting group |
| Sales Orders (sale.order) | **BLOCKED** | ACL — no Sales group |
| Purchase Orders (purchase.order) | **BLOCKED** | ACL — no Purchase group |
| Budgets (ops.budget) | **BLOCKED** | ACL — no OPS Manager/User group |

**Verdict:** IT Admin (it.admin@mztrading.com) is **completely blind** to all financial and business data. The framework's claimed "IT Admin Blindness" feature **is true**.

### 1.2 Branch Record Rules ✅ PASS (52 rules)

52 OPS-specific record rules are active covering:
- **Branch Isolation:** ops.budget, ops.asset, ops.pdc.receivable/payable, ops.matrix.snapshot, ops.report.template, ops.fiscal.period.branch.lock, ops.period.close.checklist, stock.quant, stock.picking
- **Manager/Admin Full Access:** Present for all major models (overrides for managers)
- **Cross-Branch BU Leader:** sale.order, purchase.order, account.move
- **Multi-Company:** ops.asset, ops.asset.category, ops.asset.depreciation
- **Persona/Delegation:** ops.persona, ops.persona.delegation

### 1.3 Segregation of Duties ✅ PASS (6/6 rules, all blocking)

| SoD Rule | Status | Mode |
|----------|--------|------|
| Sales Order: Create + Confirm Separation | Active | **Blocking** |
| Purchase Order: Create + Confirm Separation | Active | **Blocking** |
| Invoice: Create + Post Separation | Active | **Blocking** |
| Payment: Create + Post Separation | Active | **Blocking** |
| Bank Reconciliation: Reconcile + Approve | Active | **Blocking** |
| Inventory Adjustment: Create + Approve | Active | **Blocking** |

### 1.4 Governance Rules ✅ PASS (9/9 active and enabled)

| Rule | Code | Model | Status |
|------|------|-------|--------|
| Cross-Branch Order Warning | GR_BR_001 | sale.order | Active |
| Custom Payment Terms Approval | GR_INV_001 | account.move | Active |
| Customer Credit Limit Change Approval | GR_CUS_001 | res.partner | Active |
| Customer Credit Limit Warning | GR_SO_003 | sale.order | Active |
| High Value Order Approval | GR_SO_001 | sale.order | Active |
| Large Discount Approval Required | GR_SO_002 | sale.order | Active |
| Large Stock Adjustment Approval | GR_INV_002 | stock.quant | Active |
| Purchase Order Approval - Over 100K | GR_PO_002 | purchase.order | Active |
| Purchase Order Approval - Over 50K | GR_PO_001 | purchase.order | Active |

### 1.5 SLA Templates ✅ PASS (4/4 active)

| Template | Response Time | Resolution |
|----------|-------------|------------|
| Platinum Support - VIP Corporate | 1 hour | 4 hours |
| Gold Support - Priority Business | 4 hours | 24 hours |
| Internal IT Critical - System Down | 2 hours | 8 hours |
| Standard Sales Inquiry - New Leads | 24 hours | — |

### 1.6 Known Security Gaps ❌

| Finding | Severity | Detail |
|---------|----------|--------|
| **Payments not branch-isolated** | **CRITICAL** | `account.payment` lacks `ops_branch_id` and `ops_business_unit_id` fields. Payments cannot be filtered by branch at the record rule level. |
| **CEO/CFO missing Odoo security groups** | **HIGH** | CEO and CFO users are blocked at ACL level from accessing sale.order and account.move. They need Sales/Accounting group assignments so OPS record rules can provide full-access elevation. |
| **Persona assignment gap** | **HIGH** | Only 2 of 18 users (sales.rep1, sales.rep2) have the legacy `persona_id` field populated. The modern M2M `ops_persona_ids` works through `user_id` on `ops.persona`, but the computed `persona_id` shows NONE for 16 users. |
| **[TEMPLATE] Branch** still default | **MEDIUM** | 5 of 6 audited users show `ops_branch_id = [TEMPLATE] Branch` instead of a real operational branch. Only sales.rep1 is on Dubai HQ. |

---

## PART 2: GOVERNANCE & APPROVAL AUDIT

### 2.1 Governance Models ✅ (Comprehensive)

The framework provides a rich governance infrastructure:

| Model | Purpose | Records |
|-------|---------|---------|
| ops.governance.rule | Dynamic rule engine | 9 |
| ops.governance.discount.limit | Per-persona discount limits | 0 |
| ops.governance.margin.rule | Category/BU margin thresholds | 0 |
| ops.governance.price.authority | Price override authority | 0 |
| ops.approval.workflow | Multi-step approval workflows | 0 |
| ops.approval.request | Approval tracking | 0 |
| ops.approval.rule | Lightweight approval rules | 0 |
| ops.product.request | Product creation gatekeeper | 0 |
| ops.field.visibility.rule | Field-level data hiding | 13 |
| ops.archive.policy | Data retention policies | 2 |

### 2.2 Approval & Delegation Infrastructure ✅

- `ops.approval.workflow` and `ops.approval.request` models exist and are functional
- `ops.persona.delegation` supports delegation with:
  - Self-delegation prevention constraint
  - Overlapping delegation detection
  - Delegation-based approval verification
- **Warning:** 0 approval workflows, 0 delegations, 0 approval requests configured

### 2.3 Audit Trail ✅ (Models present, partial data)

| Audit Model | Records | Status |
|-------------|---------|--------|
| ops.audit.log (API audit) | 0 | Model exists, immutable (write/unlink protected) |
| ops.corporate.audit.log | 0 | Model exists, has `log_event`, `log_crud`, `log_authentication`, `log_financial_change`, `log_approval`, `log_export` methods |
| ops.security.audit | 82 | **Active** — 82 security events logged (type: `override_used`) |

### 2.4 Field Visibility Rules ✅ (13 rules, not enabled)

| Model | Hidden Fields | Target Group |
|-------|--------------|--------------|
| product.product | standard_price | Sales Users |
| product.template | standard_price | Sales Users |
| purchase.order | customer_id | Purchase Users |
| purchase.order.line | margin, margin_percent, sale_price | Purchase Users |
| sale.order.line | margin, margin_percent, purchase_price | Sales Users |
| stock.move | cost, value | Warehouse Users |
| stock.quant | cost, value | Warehouse Users |

**Warning:** All 13 rules are `active=True` but `enabled=False`. They won't enforce until enabled.

### 2.5 Archive Policies ✅

| Policy | Model | Retention |
|--------|-------|-----------|
| Archive Cancelled Sales Orders | sale.order | 12 months |
| Archive Old Journal Entries | account.move | 12 months |

Financial safety constraint confirmed: blocks archiving `account.move`, `account.move.line`, `stock.move`, `stock.valuation.layer`.

### 2.6 Additional Security Models ✅

- **ops.ip.whitelist** — IP-based access control (0 entries)
- **ops.session.manager** — Session management
- **ops.api.key** — API key management (0 keys)
- **ops.security.compliance** — Compliance framework

---

## PART 3: DATA ACCURACY AUDIT

### 3.1 Company Structure ✅

| Entity | Expected | Found | Status |
|--------|----------|-------|--------|
| Company name | MZ International Trading LLC | ✅ | PASS |
| Branches | 5 (Dubai HQ, Abu Dhabi, Sharjah, Riyadh, Doha) | 5 | PASS |
| Business Units | 4 (Electronics, F&B, Luxury, IT Solutions) | 4 | PASS |
| Warehouses | 5 linked to branches | 5 | PASS |
| Dubai HQ is_headquarters | True | ✅ | PASS |

### 3.2 Users & Personas ✅ (18 users, 17 assigned personas)

18 internal users created with proper persona assignments. 1 orphaned persona (Technical Support — no user).

### 3.3 Transaction Data ✅

| Record Type | Count | Breakdown |
|-------------|-------|-----------|
| Sale Orders | 20 | 15 confirmed, 5 draft |
| Purchase Orders | 15 | 10 confirmed, 5 draft |
| Account Moves | 29 | 11 journal entries (posted), 7 customer invoices, 4 vendor bills, 7 drafts |
| Payments | 9 | All in "in_process" state |

All confirmed orders have positive amounts. All posted invoices have branches assigned.

### 3.4 Budget Data ⚠️ (1 CRITICAL finding)

| Budget | Branch | BU | State | Planned | Committed | Available | Utilization |
|--------|--------|----|-------|---------|-----------|-----------|-------------|
| Electronics Q1 2026 | Dubai HQ | Electronics | confirmed | 850,000 | 420,000 | 430,000 | 49.4% |
| Luxury Q1 2026 | Dubai HQ | Luxury | confirmed | 1,330,000 | 110,000 | 1,220,000 | 8.3% |
| **F&B Q1 2026** | Dubai HQ | **Electronics** ❌ | draft | 180,000 | 420,000 | -240,000 | **233%** ⚠️ |
| IT Solutions Q1 2026 | Dubai HQ | IT Solutions | draft | 340,000 | 0 | 340,000 | 0% |

**CRITICAL:** "F&B BU Budget Q1 2026" is incorrectly assigned to Electronics BU instead of Food & Beverage. This is a seed data error that needs correction.

### 3.5 PDC Verification ✅

| Type | Count | States |
|------|-------|--------|
| PDC Receivable | 5 | 3 draft, 2 deposited |
| PDC Payable | 3 | 3 draft |

No overdue PDCs. All have proper branch/partner/maturity dates.

### 3.6 Asset Verification ✅ (with observation)

8 assets (5 running, 3 draft). All running assets have depreciation schedules generated.

**Observation:** All running assets show `accumulated_depreciation = 0` — no depreciation entries posted yet. Schedule lines exist in draft state.

**Finding:** Asset codes all show "New" — the `ops.asset` sequence is missing from `ir.sequence` data.

### 3.7 KPI Dashboard ✅

| Component | Count |
|-----------|-------|
| KPI Boards | 10 |
| KPI Widgets | 74 |
| KPI Definitions | 46 |

All 46 KPIs have valid source models configured. 10 boards cover: Executive, Finance, Branch Ops, Sales, Procurement, Sales Rep, Receivables, Payables, Treasury, System Health.

### 3.8 Cross-Reference Gaps ⚠️

| Check | Result |
|-------|--------|
| Confirmed POs → Vendor Bills | **0% linked** (10 POs, 0 with matching bills via invoice_origin) |
| Confirmed SOs → Customer Invoices | **0% linked** (15 SOs, 0 with matching invoices via invoice_origin) |
| Payment Reconciliation | **No posted payments to check** |

Invoices were created independently from SO/PO workflows, breaking standard Odoo traceability.

### 3.9 Missing Sequences ⚠️

| Sequence | Status |
|----------|--------|
| ops.branch | ✅ (BR-, next: 12) |
| ops.business.unit | ✅ (BU-, next: 9) |
| ops.pdc.receivable | ✅ (PDCR/, next: 11) |
| ops.pdc.payable | ✅ (PDCP/, next: 7) |
| ops.persona.code | ❌ NOT FOUND |
| ops.asset | ❌ NOT FOUND |

---

## PART 4: CODE QUALITY AUDIT

### 4.1 Deprecated APIs ✅ CLEAN

| Pattern | Status |
|---------|--------|
| `_check_recursion()` | Not found |
| `self._context` | Not found |
| `@api.multi` / `@api.one` | Not found |
| `fields.Datetime.now()` (callable) | Not found |
| `print()` statements | Not found |
| TODO/FIXME/HACK comments | Not found |
| Bare `except:` | Not found |
| Hardcoded secrets | Not found |

### 4.2 Critical Code Issues

| # | Severity | File | Finding |
|---|----------|------|---------|
| 1 | **CRITICAL** | ops_budget.py:255 | `OpsBudgetLine.company_id` relates to `budget_id.ops_branch_id` (ops.branch) instead of `res.company`. Type mismatch — any code using `line.company_id.currency_id` will fail. |
| 2 | **HIGH** | ops_performance_monitor.py:286,320 | Raw SQL queries for performance trends (violates ORM-only project rule) |
| 3 | **HIGH** | ops_budget.py:315 | Raw SQL for practical amount calculation (already partially fixed — committed was converted to ORM, but practical still uses raw SQL) |
| 4 | **MEDIUM** | ops_approval_dashboard.py:47 | f-string in SQL `CREATE VIEW` — safe in practice (self._table) but bad pattern |
| 5 | **MEDIUM** | ops_performance_indexes.py:164 | f-string in SQL DDL — values from hardcoded list but sets bad precedent |
| 6 | **MEDIUM** | 6 XML files | `t-raw="0"` usage — deprecated in Odoo 17+, should migrate to `t-out` |
| 7 | **MEDIUM** | ops_matrix_accounting/reports/ | Duplicate `reports/` directory alongside `report/` — identical `ops_asset_register_report.py` |
| 8 | **MEDIUM** | ops_mixin.py vs ops_matrix_mixin.py | Duplicate `_name = 'ops.matrix.mixin'` — confusing legacy file |
| 9 | **LOW** | ~30 fields across 4 modules | Many2one fields missing explicit `ondelete` |
| 10 | **LOW** | 4 manifests | Inconsistent `author` metadata (Gemini Agent / OPS Matrix / OPS Framework) |

### 4.3 Exception Handling ⚠️

~40+ instances of broad `except Exception as e` with logging but no re-raise. While not incorrect, this can hide programming bugs. Key files: ops_kpi.py, ops_followup.py, ops_asset_depreciation.py, ops_recurring.py.

### 4.4 What's Working Well ✅

1. **Zero deprecated Odoo APIs** — No `@api.multi`, `@api.one`, `self._context`, etc.
2. **No bare exceptions** — All handlers specify types
3. **No print() statements** — All logging uses `_logger`
4. **Complete `_description`** on every model
5. **Comprehensive security** — 165+ ACL lines in core, 206+ in accounting
6. **Proper compute dependencies** — All stored computed fields have correct `@api.depends`
7. **Well-structured manifests** with proper dependency chains

---

## PART 5: BUGS FIXED DURING AUDIT

### Already Fixed (during seeding phase)

| # | Bug | File | Fix |
|---|-----|------|-----|
| 1 | `model_name` unbound variable in admin bypass block | ops_governance_mixin.py | Moved `model_name = self._name` before admin bypass if-block |
| 2 | Raw SQL JSONB comparison error (`operator does not exist: jsonb = integer`) | ops_budget.py:347-388 | Rewrote `_compute_committed_amount()` to use ORM-based search on purchase.order.line |

---

## CONSOLIDATED FINDINGS — PRIORITY ORDER

### CRITICAL (Fix Immediately)

| # | Finding | Impact |
|---|---------|--------|
| C-1 | `account.payment` lacks branch/BU fields | Payments are not branch-isolated — undermines matrix security model |
| C-2 | `OpsBudgetLine.company_id` relates to `ops.branch` instead of `res.company` | Type mismatch causes errors when accessing `line.company_id.currency_id` etc. |
| C-3 | Budget "F&B Q1 2026" assigned to Electronics BU | Data integrity error in seed script — needs correction |
| C-4 | CEO/CFO missing Odoo base security groups | C-level executives cannot access sales/accounting data at all |

### HIGH (Fix Soon)

| # | Finding | Impact |
|---|---------|--------|
| H-1 | Raw SQL in `_compute_practical_amount()` | Violates ORM-only rule; already converted committed amount but practical still uses raw SQL |
| H-2 | Raw SQL in `ops_performance_monitor.py` | 4 raw SQL queries for trend/model performance data |
| H-3 | 0% SO/PO to invoice traceability | Invoices were created independently — no `invoice_origin` linking |
| H-4 | Missing `ops.asset` and `ops.persona.code` sequences | Asset codes stuck at "New", persona codes use hardcoded strings |

### MEDIUM (Plan to Fix)

| # | Finding |
|---|---------|
| M-1 | 13 field visibility rules are `active` but not `enabled` — no enforcement |
| M-2 | 0 approval workflows, 0 discount limits, 0 margin rules configured |
| M-3 | `t-raw` deprecation — migrate 8 instances to `t-out` |
| M-4 | Duplicate `reports/` directory in ops_matrix_accounting |
| M-5 | Duplicate mixin file (ops_mixin.py vs ops_matrix_mixin.py) |
| M-6 | 5 of 6 audited users on "[TEMPLATE] Branch" placeholder |
| M-7 | All 9 payments stuck in "in_process" state |
| M-8 | All 5 running assets have 0 accumulated depreciation |

### LOW (Cosmetic / Best Practice)

| # | Finding |
|---|---------|
| L-1 | ~30 Many2one fields missing explicit `ondelete` |
| L-2 | ~40 broad `except Exception` handlers (logging but no re-raise) |
| L-3 | Inconsistent `author` metadata across 4 manifests |
| L-4 | Excessive `hasattr()` usage in ops_matrix_mixin.py |
| L-5 | Technical Support persona orphaned (no user, no branch, no BU) |
| L-6 | BU leaders not assigned (all 4 BUs have `leader_id = N/A`) |

---

## FEATURE CLAIM VERIFICATION

| OPS Claim | Verdict | Evidence |
|-----------|---------|----------|
| **Persona System** | ✅ VERIFIED | 18 personas, user assignments, role-based access |
| **IT Admin Blindness** | ✅ VERIFIED | 5/5 tests — complete data lockout confirmed |
| **Branch Isolation** | ✅ VERIFIED (framework) ⚠️ (user setup) | 52 record rules present; user branch assignments incomplete |
| **Segregation of Duties** | ✅ VERIFIED | 6 rules active in blocking mode |
| **Governance Rules** | ✅ VERIFIED | 9 rules active and enabled |
| **SLA Templates** | ✅ VERIFIED | 4 templates active |
| **Approval Workflows** | ✅ EXISTS, NOT CONFIGURED | Model infrastructure present, 0 workflows defined |
| **Field Visibility** | ✅ EXISTS, NOT ENABLED | 13 rules defined, all `enabled=False` |
| **Audit Logs** | ✅ PARTIAL | Security audit has 82 entries; API and corporate audit logs have 0 |
| **Archive Policies** | ✅ VERIFIED | 2 policies with financial safety constraints |
| **Product Requests** | ✅ EXISTS, NOT TESTED | Model and workflow methods present, 0 requests created |
| **Budget Control** | ✅ VERIFIED (with bug) | 4 budgets, utilization math correct; company_id field bug |
| **PDC Management** | ✅ VERIFIED | 8 PDCs across receivable/payable with proper state machine |
| **Asset Management** | ✅ VERIFIED | 8 assets, 5 with depreciation schedules (300 lines total) |
| **KPI Center** | ✅ VERIFIED | 10 boards, 74 widgets, 46 KPI definitions |
| **Payment Isolation** | ❌ NOT IMPLEMENTED | account.payment lacks ops_branch_id/ops_business_unit_id |
| **Export Security** | ✅ EXISTS | ops.secure.export.wizard model present |
| **Import Control** | ✅ EXISTS | ops.sale.order.import.wizard model present |

---

## RECOMMENDATIONS

1. **Immediate:** Fix `OpsBudgetLine.company_id` related field path (C-2)
2. **Immediate:** Add `ops_branch_id`/`ops_business_unit_id` to `account.payment` via mixin inheritance (C-1)
3. **Immediate:** Assign proper Odoo security groups to CEO/CFO/Manager users (C-4)
4. **Short-term:** Convert remaining raw SQL in `_compute_practical_amount()` to ORM (H-1)
5. **Short-term:** Create missing IR sequences for ops.asset and ops.persona.code (H-4)
6. **Short-term:** Enable field visibility rules (M-1) and configure approval workflows (M-2)
7. **Medium-term:** Migrate `t-raw` to `t-out` (M-3), clean up duplicate files (M-4, M-5)
8. **Medium-term:** Fix seed scripts to create invoices from SO/PO workflows for traceability (H-3)

---

*Report generated by Claude Code Corporate Audit Team*
*4 parallel audit agents | 288 checks performed | 2026-02-07*
