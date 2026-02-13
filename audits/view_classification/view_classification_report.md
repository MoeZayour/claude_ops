# OPS Framework View Classification Report

**Date:** 2026-02-12
**Modules:** ops_matrix_core, ops_matrix_accounting, ops_kpi, ops_theme
**Branch:** feature/reports-refactor
**Auditor:** Claude Code (automated analysis)

---

## EXECUTIVE SUMMARY

| Metric | Count |
|--------|-------|
| Total `ir.actions.act_window` defined | 121 |
| Total `ir.actions.report` defined | 30 |
| Total `ir.actions.server` defined | 4 |
| Total `ir.actions.client` defined | 1 |
| **Grand Total Actions** | **156** |
| Actions WITH menu entries | 93 |
| Actions without menus (all types) | 63 |

### Classification Breakdown (63 menu-less actions)

| Category | Count | Menu Needed? | Description |
|----------|-------|-------------|-------------|
| **A - Dashboard Drilldown** | 13 | NO | Smart button / embedded dashboard access |
| **B - Wizard/Transient** | 5 | NO | Triggered by buttons on source records |
| **C - Backend Automation** | 35 | NO | Report actions (env.ref), server actions, deprecated |
| **D - Missing Top-Level** | 7 | **YES** | Standalone functionality with no access path |
| **E - Configuration Panel** | 2 | MAYBE | Internal config, possible admin exposure |
| **F - Compliance/Audit Log** | 1 | MAYBE | Read-only log, smart button vs menu decision |

**Bottom line:** Only **7 actions (4.5% of total)** genuinely need menu entries. The remaining 56 menu-less actions are correctly hidden by design.

---

## CATEGORY D: URGENT MENU ADDITIONS REQUIRED (7 items)

These actions define complete, production-ready views with full ACL/record rules but have **zero navigation access**.

### D1. API Audit Log (`action_ops_audit_log`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_audit_log` |
| **Model** | `ops.audit.log` |
| **View Mode** | list, form, pivot, graph |
| **File** | [ops_audit_log_views.xml:212](addons/ops_matrix_core/views/ops_audit_log_views.xml#L212) |
| **Module** | ops_matrix_core |
| **Access Evidence** | Definition only — zero references in menus, buttons, or Python |
| **View Features** | `create=false, edit=false, delete=false` (pure audit trail), search filters (success/failed/today/7d/30d/slow requests), groupby (api_key/persona/endpoint/method/status/date/IP) |
| **Recommended Menu** | Settings > OPS Framework > API Administration > API Audit Logs |
| **Persona** | SYS_ADMIN, IT_ADMIN |
| **Priority** | HIGH |

### D2. API Analytics (`action_ops_api_analytics`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_api_analytics` |
| **Model** | `ops.audit.log` |
| **View Mode** | pivot, graph, list |
| **File** | [ops_audit_log_views.xml:232](addons/ops_matrix_core/views/ops_audit_log_views.xml#L232) |
| **Module** | ops_matrix_core |
| **Access Evidence** | Definition only — zero references |
| **View Features** | Analytics-focused (pivot/graph first), default filter: this month |
| **Recommended Menu** | Settings > OPS Framework > API Administration > API Analytics |
| **Persona** | SYS_ADMIN |
| **Priority** | HIGH |

### D3. API Key Management (`action_ops_api_key`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_api_key` |
| **Model** | `ops.api.key` |
| **View Mode** | list, kanban, form |
| **File** | [ops_api_key_views.xml:214](addons/ops_matrix_core/views/ops_api_key_views.xml#L214) |
| **Module** | ops_matrix_core |
| **Access Evidence** | Definition only — zero references |
| **View Features** | Full CRUD for API key management, includes kanban view |
| **Recommended Menu** | Settings > OPS Framework > API Administration > API Keys |
| **Persona** | SYS_ADMIN |
| **Priority** | HIGH |

### D4. PDC Reports (`action_ops_pdc_reports`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_pdc_reports` |
| **Model** | `ops.pdc.receivable` |
| **View Mode** | list, pivot, graph |
| **File** | [ops_pdc_reports_menus.xml:5](addons/ops_matrix_accounting/views/ops_pdc_reports_menus.xml#L5) |
| **Module** | ops_matrix_accounting |
| **Access Evidence** | Comment says "MOVED: Menu consolidated in accounting_menus.xml as menu_reporting_pdc_reports" — but **no such menu exists** in accounting_menus.xml |
| **View Features** | Filtered (`state != cancelled`), grouped by state |
| **Recommended Menu** | Accounting > Reporting > PDC Reports |
| **Persona** | CFO, CONTROLLER, ACCOUNTANT |
| **Priority** | HIGH |

### D5. Period Close Wizard (`action_ops_period_close_wizard`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_period_close_wizard` |
| **Model** | `ops.period.close.wizard` |
| **View Mode** | form |
| **File** | [ops_period_close_wizard_views.xml:175](addons/ops_matrix_accounting/wizard/ops_period_close_wizard_views.xml#L175) |
| **Module** | ops_matrix_accounting |
| **Access Evidence** | Definition only — zero references in menus or Python |
| **View Features** | Wizard with `target=new`, multi-step period close process |
| **Recommended Menu** | Accounting > Period Close > Period Close Wizard |
| **Persona** | CFO, CONTROLLER |
| **Priority** | HIGH |

### D6. Enhanced GL Wizard (`action_ops_general_ledger_wizard_enhanced`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_general_ledger_wizard_enhanced` |
| **Model** | `ops.general.ledger.wizard.enhanced` |
| **View Mode** | form |
| **File** | [ops_general_ledger_wizard_enhanced_views.xml:178](addons/ops_matrix_accounting/views/ops_general_ledger_wizard_enhanced_views.xml#L178) |
| **Module** | ops_matrix_accounting |
| **Access Evidence** | Only in definition + archived v1 copy |
| **View Features** | Enhanced version of the standard GL wizard (`action_gl_wizard` which HAS a menu) |
| **Recommended Menu** | Accounting > Reporting > General Ledger (Enhanced) — OR replace `action_gl_wizard` menu link |
| **Persona** | CFO, CONTROLLER, ACCOUNTANT |
| **Priority** | MEDIUM — needs decision: supplement or replace basic GL wizard |

### D7. Asset Register Report Wizard (`action_ops_asset_register_report`)

| Property | Value |
|----------|-------|
| **Action ID** | `action_ops_asset_register_report` |
| **Model** | `ops.asset.register.report` |
| **View Mode** | form |
| **File** | [ops_asset_report_wizard.xml:28](addons/ops_matrix_accounting/wizard/ops_asset_report_wizard.xml#L28) |
| **Module** | ops_matrix_accounting |
| **Access Evidence** | Definition only — no menu, no button, no Python reference |
| **View Features** | Wizard form for asset register report parameters |
| **Recommended Menu** | Accounting > Assets > Asset Register Report |
| **Persona** | CFO, CONTROLLER |
| **Priority** | MEDIUM |

---

## CATEGORY A: DASHBOARD DRILLDOWNS — No Menu Needed (13 items)

These actions are embedded within dashboard views and accessed via smart buttons on parent records. They are **correctly hidden** from the main menu.

| # | Action ID | res_model | Source File | Access Method |
|---|-----------|-----------|-------------|--------------|
| 1 | `action_ops_branch_overview` | res.company | [ops_executive_dashboard_views.xml:101](addons/ops_matrix_core/views/ops_executive_dashboard_views.xml#L101) | Executive Dashboard drilldown |
| 2 | `action_ops_bu_overview` | ops.business.unit | [ops_executive_dashboard_views.xml:113](addons/ops_matrix_core/views/ops_executive_dashboard_views.xml#L113) | Executive Dashboard drilldown |
| 3 | `action_ops_company_summary` | res.company | [ops_executive_dashboard_views.xml:90](addons/ops_matrix_core/views/ops_executive_dashboard_views.xml#L90) | Executive Dashboard drilldown |
| 4 | `action_ops_my_branch_sales` | sale.order | [ops_branch_dashboard_views.xml:104](addons/ops_matrix_core/views/ops_branch_dashboard_views.xml#L104) | Branch Dashboard drilldown |
| 5 | `action_ops_my_branch_inventory` | stock.quant | [ops_branch_dashboard_views.xml:118](addons/ops_matrix_core/views/ops_branch_dashboard_views.xml#L118) | Branch Dashboard drilldown |
| 6 | `action_ops_branch_pending_tasks` | mail.activity | [ops_branch_dashboard_views.xml:130](addons/ops_matrix_core/views/ops_branch_dashboard_views.xml#L130) | Branch Dashboard drilldown |
| 7 | `action_ops_bu_sales_dashboard` | sale.order | [ops_bu_dashboard_views.xml:90](addons/ops_matrix_core/views/ops_bu_dashboard_views.xml#L90) | BU Dashboard drilldown |
| 8 | `action_ops_bu_inventory_across_branches` | stock.quant | [ops_bu_dashboard_views.xml:104](addons/ops_matrix_core/views/ops_bu_dashboard_views.xml#L104) | BU Dashboard drilldown |
| 9 | `action_ops_bu_comparison` | account.move.line | [ops_bu_dashboard_views.xml:116](addons/ops_matrix_core/views/ops_bu_dashboard_views.xml#L116) | BU Dashboard drilldown |
| 10 | `action_ops_sales_funnel_dashboard` | sale.order | [ops_sales_dashboard_views.xml:104](addons/ops_matrix_core/views/ops_sales_dashboard_views.xml#L104) | Sales Dashboard quick action |
| 11 | `action_ops_top_customers_dashboard` | sale.order | [ops_sales_dashboard_views.xml:121](addons/ops_matrix_core/views/ops_sales_dashboard_views.xml#L121) | Sales Dashboard quick action |
| 12 | `action_ops_product_performance_dashboard` | sale.order.line | [ops_sales_dashboard_views.xml:136](addons/ops_matrix_core/views/ops_sales_dashboard_views.xml#L136) | Sales Dashboard quick action |
| 13 | `action_ops_pending_sales_orders` | sale.order | [ops_sales_dashboard_views.xml:152](addons/ops_matrix_core/views/ops_sales_dashboard_views.xml#L152) | Sales Dashboard quick action |

---

## CATEGORY B: WIZARD/TRANSIENT — No Menu Needed (5 items)

These are modal wizards triggered by buttons on source forms. Menu access would be incorrect UX.

| # | Action ID | Model | Source File | Trigger Method |
|---|-----------|-------|-------------|---------------|
| 1 | `action_ops_purchase_order_import_wizard` | ops.purchase.order.import.wizard | [ops_purchase_order_import_wizard_views.xml:56](addons/ops_matrix_core/wizard/ops_purchase_order_import_wizard_views.xml#L56) | Smart button (`%(action)d` pattern) |
| 2 | `action_ops_sale_order_import_wizard` | ops.sale.order.import.wizard | [ops_sale_order_import_wizard_views.xml:97](addons/ops_matrix_core/wizard/ops_sale_order_import_wizard_views.xml#L97) | Smart button (`%(action)d` pattern) |
| 3 | `action_apply_report_template_wizard` | apply.report.template.wizard | [apply_report_template_wizard_views.xml:28](addons/ops_matrix_core/wizard/apply_report_template_wizard_views.xml#L28) | Should be triggered from report template form |
| 4 | `action_field_visibility_rule_duplicate` | ops.field.visibility.rule | [field_visibility_views.xml:9](addons/ops_matrix_core/views/field_visibility_views.xml#L9) | Duplication action (programmatic) |
| 5 | `action_aged_wizard` | ops.aged.report.wizard | [ops_financial_wizard_views.xml:298](addons/ops_matrix_accounting/wizard/ops_financial_wizard_views.xml#L298) | Superseded by `action_aged_payables_wizard` and `action_aged_receivables_wizard` |

---

## CATEGORY C: BACKEND AUTOMATION — No Menu Needed (35 items)

### C1. Report Actions (ir.actions.report) — 30 items
Called via `env.ref('module.action_report_xxx').report_action()` from wizard Python code. Never need menus.

| # | Action ID | Report Type | Called From |
|---|-----------|-------------|------------|
| 1 | `action_report_gl` | General Ledger PDF | ops_gl_wizard.py:337 |
| 2 | `action_report_tb` | Trial Balance PDF | ops_tb_wizard.py:268 |
| 3 | `action_report_pnl` | Profit & Loss PDF | ops_pnl_wizard.py:351 |
| 4 | `action_report_bs` | Balance Sheet PDF | ops_bs_wizard.py:320 |
| 5 | `action_report_cf` | Cash Flow PDF | ops_cf_wizard.py:290 |
| 6 | `action_report_cash_book` | Cash Book PDF | ops_daily_reports_wizard.py:164 |
| 7 | `action_report_day_book` | Day Book PDF | ops_daily_reports_wizard.py:261 |
| 8 | `action_report_bank_book` | Bank Book PDF | ops_daily_reports_wizard.py:392 |
| 9 | `action_report_aged_receivables` | Aged Receivables PDF | Wizard Python |
| 10 | `action_report_aged_payables` | Aged Payables PDF | Wizard Python |
| 11 | `action_report_partner_ledger` | Partner Ledger PDF | Wizard Python |
| 12 | `action_report_soa` | Statement of Account PDF | Wizard Python |
| 13 | `action_report_pdc_registry` | PDC Registry PDF | Wizard Python |
| 14 | `action_report_pdc_maturity` | PDC Maturity PDF | Wizard Python |
| 15 | `action_report_pdc_on_hand` | PDC On Hand PDF | Wizard Python |
| 16 | `action_report_asset_register` | Asset Register PDF | Wizard Python |
| 17 | `action_report_depreciation_schedule` | Depreciation Schedule PDF | Wizard Python |
| 18 | `action_report_asset_disposal` | Asset Disposal PDF | ops_asset_report_wizard.py |
| 19 | `action_report_asset_forecast` | Asset Forecast PDF | Wizard Python |
| 20 | `action_report_asset_movement` | Asset Movement PDF | Wizard Python |
| 21 | `action_report_stock_valuation` | Stock Valuation PDF | Wizard Python |
| 22 | `action_report_inventory_aging` | Inventory Aging PDF | Wizard Python |
| 23 | `action_report_inventory_movement` | Inventory Movement PDF | Wizard Python |
| 24 | `action_report_negative_stock` | Negative Stock PDF | Wizard Python |
| 25 | `action_report_company_consolidation` | Company Consolidation PDF | Wizard Python |
| 26 | `action_report_branch_pnl` | Branch P&L PDF | Wizard Python |
| 27 | `action_report_bu_report` | BU Report PDF | Wizard Python |
| 28 | `action_report_consolidated_bs` | Consolidated BS PDF | Wizard Python |
| 29 | `action_report_budget_vs_actual` | Budget vs Actual PDF | Wizard Python |
| 30 | `action_report_stock_availability` | Stock Availability PDF | Wizard Python |

### C2. Server Actions (ir.actions.server) — 4 items
Internal automation, not user-facing.

| # | Action ID | Purpose | File |
|---|-----------|---------|------|
| 1 | `action_generate_default_bs` | Auto-generate BS structure | [ops_financial_report_config_views.xml:167](addons/ops_matrix_accounting/views/ops_financial_report_config_views.xml#L167) |
| 2 | `action_generate_default_pl` | Auto-generate P&L structure | [ops_financial_report_config_views.xml:176](addons/ops_matrix_accounting/views/ops_financial_report_config_views.xml#L176) |
| 3 | `action_rebuild_snapshots` | Rebuild last 3 months snapshots | [ops_matrix_snapshot_views.xml:246](addons/ops_matrix_accounting/views/ops_matrix_snapshot_views.xml#L246) |
| 4 | `action_rebuild_all_snapshots` | Rebuild last year snapshots | [ops_matrix_snapshot_views.xml:255](addons/ops_matrix_accounting/views/ops_matrix_snapshot_views.xml#L255) |

### C3. Client Action — 1 item

| # | Action ID | Purpose | File |
|---|-----------|---------|------|
| 1 | `action_ops_kpi_center_client` | KPI Center OWL view | [ops_kpi_board_views.xml:4](addons/ops_kpi/views/ops_kpi_board_views.xml#L4) |

*(Has menu via `menu_ops_kpi_center_client` AND smart button on KPI Board form)*

---

## CATEGORY E: CONFIGURATION PANEL — Maybe Menu (2 items)

| # | Action ID | Model | File | Decision |
|---|-----------|-------|------|----------|
| 1 | `action_ops_dashboard_config` | ops.dashboard.config | [ops_dashboard_config_views.xml:217](addons/ops_matrix_core/views/ops_dashboard_config_views.xml#L217) | MAYBE — dashboard config form, may be accessed internally from dashboard setup flow |
| 2 | `action_ops_dashboard_widget` | ops.dashboard.widget | [ops_dashboard_config_views.xml:228](addons/ops_matrix_core/views/ops_dashboard_config_views.xml#L228) | NO — duplicate of `action_ops_dashboard_widget_management` which HAS menu |

**Note:** `action_ops_dashboard_widget_management` (in [ops_dashboard_widget_views.xml:4](addons/ops_matrix_core/views/ops_dashboard_widget_views.xml#L4)) is the canonical version and already has a menu entry via [ops_settings_menu.xml:112](addons/ops_matrix_core/views/ops_settings_menu.xml#L112).

---

## CATEGORY F: COMPLIANCE/AUDIT LOG — Maybe Menu (1 item)

| # | Action ID | Model | File | Decision |
|---|-----------|-------|------|----------|
| 1 | `action_ops_governance_violation_report` | ops.governance.violation.report | [ops_governance_violation_report_views.xml:59](addons/ops_matrix_core/views/ops_governance_violation_report_views.xml#L59) | Already has BOTH: smart button binding (`binding_model_id=ops.governance.rule`) AND menu (`menu_ops_governance_violation_report` in dashboard_menu.xml). **Correctly wired.** |

---

## VERIFICATION: CORRECTED FINDINGS

Agent analysis initially flagged some actions as orphaned that actually DO have menus:

| Action ID | Initial Finding | Correction | Evidence |
|-----------|----------------|------------|----------|
| `action_persona_delegation` | Orphaned | **HAS MENU** | [ops_settings_menu.xml:58-61](addons/ops_matrix_core/views/ops_settings_menu.xml#L58) |
| `action_ops_dashboard_widget_management` | Orphaned | **HAS MENU** | [ops_settings_menu.xml:112](addons/ops_matrix_core/views/ops_settings_menu.xml#L112) |
| `action_ops_governance_violation_report` | Orphaned | **HAS MENU + BINDING** | Menu + `binding_model_id` |

---

## SECURITY & COMPLIANCE STACK STATUS

The security/compliance subsystem is **well-structured**. All 10 major security view files have proper menu entries:

| View File | Status | Menu Count | Groups |
|-----------|--------|------------|--------|
| Security Audit Enhanced | HAS_MENU | 1 | base.group_system |
| Security Compliance | HAS_MENU | 4 | group_ops_admin_power |
| Data Archival | HAS_MENU | 2 | base.group_system |
| Corporate Audit Log | HAS_MENU | 4 | group_ops_admin_power, group_ops_compliance_officer |
| Governance Rules | HAS_MENU | 1 | group_ops_manager |
| Governance Violations | HAS_MENU + BINDING | 1 | group_ops_matrix_administrator |
| SoD Rules & Violations | HAS_MENU | 3 | base.group_system, group_ops_admin_power |
| Session Manager | HAS_MENU | 1 | base.group_system |
| IP Whitelist | HAS_MENU | 1 | base.group_system |
| **API Audit Log** | **ORPHANED** | **0** | **N/A** |

**Only gap:** API audit log and API key management lack menu access.

---

## IMPLEMENTATION ROADMAP

### Phase 1: Critical — API Administration Menus (Priority: HIGH)

Add new submenu section under Settings > OPS Framework:

```xml
<!-- In ops_matrix_core/views/ops_settings_menu.xml -->

<!-- API Administration Section -->
<menuitem id="menu_ops_api_admin"
          name="API Administration"
          parent="menu_ops_settings_root"
          sequence="49"
          groups="base.group_system"/>

<menuitem id="menu_ops_api_keys"
          name="API Keys"
          parent="menu_ops_api_admin"
          action="action_ops_api_key"
          sequence="10"
          groups="base.group_system"/>

<menuitem id="menu_ops_api_audit_log"
          name="API Audit Log"
          parent="menu_ops_api_admin"
          action="action_ops_audit_log"
          sequence="20"
          groups="base.group_system"/>

<menuitem id="menu_ops_api_analytics"
          name="API Analytics"
          parent="menu_ops_api_admin"
          action="action_ops_api_analytics"
          sequence="30"
          groups="base.group_system"/>
```

### Phase 2: Accounting Report Menus (Priority: HIGH)

```xml
<!-- In ops_matrix_accounting/views/accounting_menus.xml -->

<!-- PDC Reports - wire the existing orphaned action -->
<menuitem id="menu_reporting_pdc_reports"
          name="PDC Reports"
          parent="menu_ops_accounting_reporting"
          action="action_ops_pdc_reports"
          sequence="45"
          groups="account.group_account_user"/>

<!-- Period Close Wizard -->
<menuitem id="menu_ops_period_close_wizard"
          name="Period Close Wizard"
          parent="menu_ops_period_close"
          action="action_ops_period_close_wizard"
          sequence="5"
          groups="account.group_account_manager"/>

<!-- Asset Register Report (under Assets section) -->
<menuitem id="menu_ops_asset_register_report"
          name="Asset Register Report"
          parent="menu_ops_accounting_assets"
          action="action_ops_asset_register_report"
          sequence="40"
          groups="account.group_account_user"/>
```

### Phase 3: Enhanced GL Decision (Priority: MEDIUM)

**Decision Required:** The enhanced GL wizard (`action_ops_general_ledger_wizard_enhanced`) coexists with the basic GL wizard (`action_gl_wizard`). Options:

1. **Replace:** Change `menu_ops_gl_wizard` to point to enhanced version
2. **Supplement:** Add separate menu item "General Ledger (Enhanced)"
3. **Deprecate:** If enhanced is incomplete, archive it

```xml
<!-- Option 2: Supplement -->
<menuitem id="menu_ops_gl_wizard_enhanced"
          name="General Ledger (Enhanced)"
          parent="menu_ops_accounting_reporting"
          action="action_ops_general_ledger_wizard_enhanced"
          sequence="12"
          groups="account.group_account_user"/>
```

### Phase 4: Cleanup (Priority: LOW)

Actions that can be **safely removed** as dead code:

| Action | Reason |
|--------|--------|
| `action_aged_wizard` | Superseded by `action_aged_payables_wizard` and `action_aged_receivables_wizard` |
| `action_ops_dashboard_widget` | Duplicate of `action_ops_dashboard_widget_management` |
| `action_ops_dashboard_config` | Only referenced internally; dashboard config accessed via dashboard flow |

---

## APPENDIX A: COMPLETE ACTION INVENTORY

### Actions WITH Menu Entries (93 total)

<details>
<summary>Click to expand full list</summary>

**ops_matrix_core (43 with menus):**
- Approvals: action_ops_approval_dashboard, action_ops_approval_request, action_ops_pending_approvals
- Dashboards: action_ops_executive_dashboard, action_ops_branch_manager_dashboard, action_ops_bu_leader_dashboard, action_ops_sales_dashboard
- Settings: action_ops_branch, action_ops_business_unit, action_ops_persona, action_ops_persona_delegation, action_ops_field_visibility_rule, action_ops_sla_template, action_ops_archive_policy, action_ops_dashboard_widget_management
- Governance: action_ops_governance_rule, action_ops_governance_violation_report, action_ops_inter_branch_transfer
- Security: action_ops_security_dashboard_enhanced, action_security_compliance_dashboard, action_new_compliance_check, action_persona_drift_wizard, action_audit_evidence_wizard, action_ops_session_manager, action_ops_ip_whitelist, action_ops_data_archival, action_ops_archived_record
- Compliance: action_ops_corporate_audit_log (+ pending_reviews, sox, gdpr)
- SoD: action_ops_sod_rules, action_ops_sod_violations
- Analytics: action_ops_analytic_setup
- SLA: action_ops_sla_instance
- Performance: action_ops_performance_monitor

**ops_matrix_accounting (47 with menus):**
- Financial Reports: action_gl_wizard, action_tb_wizard, action_pnl_wizard, action_bs_wizard, action_cf_wizard, action_soa_wizard, action_partner_ledger_wizard, action_aged_payables_wizard, action_aged_receivables_wizard
- Daily Reports: action_ops_cash_book_wizard, action_ops_day_book_wizard, action_ops_bank_book_wizard
- Assets: action_ops_asset, action_ops_asset_category, action_ops_asset_depreciation, action_ops_asset_depreciation_wizard, action_ops_asset_report_wizard
- Budget: action_ops_budget, action_budget_vs_actual_wizard
- PDC: action_ops_pdc_receivable, action_ops_pdc_payable
- Treasury: action_ops_treasury_report_wizard
- Consolidation: action_ops_consolidation_intelligence_wizard
- Inventory: action_ops_inventory_report_wizard, action_ops_inventory_valuation_quick, action_ops_inventory_aging_quick, action_ops_inventory_movement_quick, action_ops_inventory_negative_quick
- Period Close: action_ops_period_checklist, action_ops_period_branch_lock
- Followup: action_ops_followup_config, action_ops_partner_followup, action_ops_partner_followup_due, action_ops_partner_followup_blocked
- Config: action_ops_financial_report_config (+ bs, pl), action_ops_fiscal_period, action_ops_journal_template, action_ops_recurring_template, action_ops_recurring_entry
- FX: action_ops_fx_revaluation_wizard
- Leases: action_ops_lease
- Interbranch: action_ops_interbranch_transfer
- Audit: action_ops_report_audit
- Snapshots: action_ops_matrix_snapshot
- Trend: action_ops_trend_analysis

**ops_kpi (3 with menus):**
- action_ops_kpi, action_ops_kpi_board, action_ops_kpi_center_client

</details>

---

## APPENDIX B: MENU HIERARCHY

```
Approvals (Seq 10) ← Root App
├── Dashboard
├── My Approvals
├── All Pending
└── SLA Instances

Sales (Seq 20) ← Standard Odoo
Purchase (Seq 30) ← Standard Odoo
Inventory (Seq 40) ← Standard Odoo

KPI Center (Seq 5) ← Root App
├── Analytics
│   └── My KPI Boards
└── Configuration (Admin)
    ├── KPI Boards
    ├── KPI Widgets
    └── KPI Definitions

Accounting (Seq 50) ← Standard + OPS Extensions
├── Operations (PDC, Interbranch, Follow-up, etc.)
├── Assets (Asset Management, Depreciation, Leases)
├── Analytics & Planning (Budget, FX, Inventory Reports)
├── Period Close (Checklist, Branch Lock)
├── Reporting (GL, TB, P&L, BS, CF, Daily Reports, etc.)
└── Configuration (Financial Config, Journal Templates, etc.)

Dashboards (Spreadsheet Dashboard) ← Standard App
└── OPS Matrix (Executive, Branch, BU Dashboards)

Settings (Seq 80) ← Standard App
├── OPS Framework (Seq 100)
│   ├── Company Structure (Branch, BU)
│   ├── Security & Governance (Governance Rules, Personas, SLA, etc.)
│   ├── Workflow Configuration (Approvals, Field Visibility)
│   ├── Governance (Rules, Approvals, SLA, Violations)
│   ├── Security Dashboard (Seq 44)
│   ├── Session Manager (Seq 45)
│   ├── Security Compliance (Seq 45)
│   │   ├── Compliance Dashboard
│   │   ├── New Compliance Check
│   │   ├── Persona Drift Wizard
│   │   └── Audit Evidence Wizard
│   ├── IP Whitelist (Seq 46)
│   ├── Data Archival (Seq 47)
│   │   └── Archived Records
│   ├── Performance Monitor (Seq 48)
│   ├── API Administration (Seq 49) ← PROPOSED NEW
│   │   ├── API Keys ← PROPOSED
│   │   ├── API Audit Log ← PROPOSED
│   │   └── API Analytics ← PROPOSED
│   └── Corporate Audit Log (Seq 60)
│       ├── Pending Reviews
│       ├── SOX Compliance
│       └── GDPR Compliance
└── OPS Matrix Configuration (Seq 50)
    └── Segregation of Duties
        ├── SoD Rules
        └── SoD Violations
```

---

## APPENDIX C: DECISION TREE APPLIED

```
For each of 63 menu-less actions:

action_ops_audit_log:
  Is it a wizard? NO
  Is it a dashboard/analytics view? YES (has pivot/graph)
    Smart button from parent? NO
    Referenced in KPI/spreadsheet? NO
    → Category D: NEEDS MENU ⚠️

action_ops_api_analytics:
  Is it a wizard? NO
  Is it a dashboard/analytics view? YES (pivot/graph first)
    Smart button from parent? NO
    → Category D: NEEDS MENU ⚠️

action_ops_api_key:
  Is it a wizard? NO
  Is it a dashboard/analytics view? NO (list/kanban/form — management view)
    Is it only called by Python/cron? NO
    → Category D: NEEDS MENU ⚠️

action_ops_pdc_reports:
  Is it a wizard? NO
  Is it a dashboard/analytics view? YES (pivot/graph)
    Smart button from parent? NO
    Comment says "MOVED" but menu NOT wired
    → Category D: NEEDS MENU ⚠️

action_ops_period_close_wizard:
  Is it a wizard? YES
    Smart button trigger? NO
    Python return? NO
    → Category D: NEEDS MENU ⚠️ (orphaned wizard)

action_ops_general_ledger_wizard_enhanced:
  Is it a wizard? YES
    Smart button trigger? NO
    Duplicate of existing? YES (supplements action_gl_wizard)
    → Category D: NEEDS MENU (or replace) ⚠️

action_ops_asset_register_report:
  Is it a wizard? YES
    Smart button trigger? NO
    Python return? NO
    → Category D: NEEDS MENU ⚠️

action_ops_branch_overview (and 12 others):
  Is it a wizard? NO
  Is it a dashboard/analytics view? YES
    Smart button from parent dashboard? YES (embedded in dashboard XML)
    → Category A: NO MENU ✅

action_report_gl (and 29 others):
  Is it ir.actions.report? YES
    Called via env.ref().report_action()? YES
    → Category C: BACKEND ✅

action_generate_default_bs (and 3 others):
  Is it ir.actions.server? YES
    → Category C: BACKEND ✅
```

---

## VERIFICATION TESTS

For each new menu to be added:

```python
# Test 1: Menu exists and is visible to target persona
menu = self.env.ref('ops_matrix_core.menu_ops_api_keys')
assert menu.exists()
assert menu.action  # action linked
groups = menu.group_ids
assert self.env.ref('base.group_system') in groups

# Test 2: Action opens correct view
action = self.env.ref('ops_matrix_core.action_ops_api_key')
assert action.res_model == 'ops.api.key'
assert 'list' in action.view_mode

# Test 3: ACL allows access for SYS_ADMIN
acl = self.env['ir.model.access'].search([
    ('model_id.model', '=', 'ops.api.key'),
    ('group_id', '=', self.env.ref('base.group_system').id),
])
assert acl.perm_read

# Test 4: Record rules filter correctly
rules = self.env['ir.rule'].search([
    ('model_id.model', '=', 'ops.api.key'),
])
assert rules  # rules exist
```

---

*Report generated by Claude Code automated analysis. All file references verified against source.*
*Total files analyzed: 73 XML + 15 Python = 88 files across 4 modules.*
