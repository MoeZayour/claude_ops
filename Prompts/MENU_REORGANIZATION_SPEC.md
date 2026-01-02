# OPS Matrix Framework - Menu Reorganization Specification

> **Version:** 1.0
> **Date:** 2025-01-XX
> **Status:** Pending Implementation

## Overview

This document defines the complete menu restructuring for the OPS Matrix Framework.

## Table of Contents

1. [Current State Audit](#phase-1-audit)
2. [Modular Architecture](#phase-2-architecture)
3. [Implementation Files](#phase-3-implementation)
4. [Validation Checklist](#phase-4-validation)

---


## 🔄 Updated Gemini 2.5 Pro Prompt (Modular Version)


You are an expert Odoo 19 CE developer. Your task is to reorganize menu items across the OPS Matrix Framework while **maintaining full modularity**.

## CRITICAL REQUIREMENT: MODULAR DESIGN

The OPS Matrix Framework is designed for selective installation:
- Customer A might install: `ops_matrix_core` only
- Customer B might install: `ops_matrix_core` + `ops_matrix_accounting`
- Customer C might install: all modules

**Each module MUST be self-contained for menus:**
1. A module defines ONLY menus for its own features
2. A module defines its own parent/container menus (not shared)
3. NO references to menus from optional sibling modules
4. Dependencies flow DOWN only (child depends on parent, never reverse)

```
CORRECT DEPENDENCY FLOW:
                    
    ops_matrix_core (base - always installed)
           │
    ┌──────┴──────┐
    ▼             ▼
ops_matrix    ops_matrix
accounting    reporting
    │             │
    ▼             ▼
(optional)    (optional)

WRONG: ops_matrix_core referencing ops_matrix_accounting menus
WRONG: ops_matrix_reporting depending on ops_matrix_accounting
```

---

## PHASE 1: AUDIT CURRENT STATE

### Step 1.1: Map Module Dependencies

```bash
# Check current dependencies
grep -A5 "'depends'" addons/ops_matrix_core/__manifest__.py
grep -A5 "'depends'" addons/ops_matrix_accounting/__manifest__.py
grep -A5 "'depends'" addons/ops_matrix_reporting/__manifest__.py
```

### Step 1.2: Identify Cross-Module Menu References (VIOLATIONS)

```bash
# Find menus in ops_matrix_core that reference ops_matrix_accounting
grep -rn 'ops_matrix_accounting\.' addons/ops_matrix_core/views/*.xml

# Find menus in ops_matrix_reporting that reference ops_matrix_accounting  
grep -rn 'ops_matrix_accounting\.' addons/ops_matrix_reporting/views/*.xml

# Find menus referencing non-existent parents
grep -rn 'parent="menu_ops' addons/ops_matrix_*/views/*.xml | grep -v "ops_matrix_core"
```

### Step 1.3: Current Menu Ownership

Run this to create ownership map:

```bash
echo "=== ops_matrix_core menus ===" && \
grep -h 'id="menu_ops' addons/ops_matrix_core/views/*.xml | grep -oP 'id="\K[^"]+' | sort

echo "=== ops_matrix_accounting menus ===" && \
grep -h 'id="menu_ops' addons/ops_matrix_accounting/views/*.xml | grep -oP 'id="\K[^"]+' | sort

echo "=== ops_matrix_reporting menus ===" && \
grep -h 'id="menu_ops' addons/ops_matrix_reporting/views/*.xml | grep -oP 'id="\K[^"]+' | sort
```

---

## PHASE 2: DEFINE MODULAR MENU ARCHITECTURE

### Principle: Each Module Owns Its Menu Tree

```
📦 ops_matrix_core (STANDALONE - No optional dependencies)
│
├── 📱 Settings (base.menu_administration)
│   └── 📁 OPS Matrix [menu_ops_matrix_settings] ← DEFINED HERE
│       ├── 📁 Organization [menu_ops_organization]
│       │   ├── Companies [menu_ops_companies]
│       │   ├── Branches [menu_ops_branch]
│       │   └── Business Units [menu_ops_business_unit]
│       ├── 📁 Governance [menu_ops_governance]
│       │   ├── Rules, Approvals, Violations...
│       │   └── (all governance features)
│       ├── 📁 Personas [menu_ops_personas]
│       ├── 📁 SLA [menu_ops_sla]
│       └── 📁 API [menu_ops_api]
│
└── 📱 Inventory (stock.menu_stock_root) - IF stock in depends
    └── Inter-Branch Transfer [menu_ops_inter_branch_transfer]


📦 ops_matrix_accounting (DEPENDS ON: ops_matrix_core, account)
│
└── 📱 Accounting (account.menu_finance)
    └── 📁 OPS Accounting [menu_ops_accounting_root] ← DEFINED HERE
        ├── 📁 Assets [menu_ops_asset_root]
        │   ├── Asset List
        │   ├── Depreciation
        │   └── Configuration
        ├── 📁 Reports [menu_ops_reports]
        │   ├── General Ledger
        │   ├── Financial Report
        │   ├── Budget
        │   └── Consolidation Reports
        └── 📁 PDC [menu_ops_pdc_root]
            ├── PDC Receivable
            └── PDC Payable


📦 ops_matrix_reporting (DEPENDS ON: ops_matrix_core)
│
├── 📱 Settings (via ops_matrix_core.menu_ops_matrix_settings)
│   └── 📁 Reporting Tools [menu_ops_reporting_tools] ← DEFINED HERE
│       └── Excel Export
│
├── 📱 Sales (sale.sale_menu_root) - CONDITIONAL
│   └── 📁 OPS Analytics [menu_ops_sales_analytics_root] ← DEFINED HERE
│       └── Sales Analytics
│
└── 📱 Inventory (stock.menu_stock_root)
    └── 📁 OPS Analytics [menu_ops_inventory_analytics_root] ← DEFINED HERE
        └── Inventory Analytics


📦 oca_reporting_engine (EXTERNAL - DO NOT MODIFY)
```

---

## PHASE 3: IMPLEMENTATION RULES

### Rule 1: Module Defines Its Own Container Menus

**❌ WRONG (Cross-module dependency):**
```xml
<!-- In ops_matrix_reporting/views/reporting_menu.xml -->
<menuitem id="menu_ops_sales_analytics"
          parent="ops_matrix_accounting.menu_ops_accounting_reports"/>  <!-- BAD! -->
```

**✅ CORRECT (Self-contained):**
```xml
<!-- In ops_matrix_reporting/views/reporting_menu.xml -->
<!-- Define own parent menu under native Odoo menu -->
<menuitem id="menu_ops_sales_analytics_root"
          name="OPS Analytics"
          parent="sale.sale_menu_root"
          sequence="90"/>

<menuitem id="menu_ops_sales_analytics"
          name="Sales Analytics"
          parent="menu_ops_sales_analytics_root"
          action="action_ops_sales_analytics"
          sequence="10"/>
```

### Rule 2: Use Conditional Menus for Optional Dependencies

When a menu depends on an optional module (like `sale`), use `groups` or check in manifest:

**Option A: Via Groups (Recommended)**
```xml
<menuitem id="menu_ops_sales_analytics_root"
          name="OPS Analytics"
          parent="sale.sale_menu_root"
          sequence="90"
          groups="sales_team.group_sale_salesman"/>
```

**Option B: Separate Data Files with Conditions**
```python
# In __manifest__.py
{
    'data': [
        'views/reporting_base_menus.xml',  # Always loaded
    ],
    'demo': [],
    # Conditional data based on installed modules - NOT STANDARD
    # Better to use proper depends
}
```

**Option C: Check Module Installation (for edge cases)**
```xml
<!-- Use ir.model.data to check if parent exists -->
<function model="ir.ui.menu" name="_parent_store_compute"/>
```

### Rule 3: ops_matrix_core Provides ONLY Core Settings Menus

**File: `ops_matrix_core/views/ops_menu_settings.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- ================================================================
         OPS MATRIX CORE - SETTINGS MENUS ONLY
         
         This module defines menus for Settings app only.
         Other modules (accounting, reporting) define their own app menus.
         ================================================================ -->

    <!-- Main OPS Matrix menu under Settings -->
    <menuitem id="menu_ops_matrix_settings"
              name="OPS Matrix"
              parent="base.menu_administration"
              sequence="50"
              groups="base.group_system,base.group_erp_manager"/>

    <!-- ==================== ORGANIZATION ==================== -->
    <menuitem id="menu_ops_organization"
              name="Organization"
              parent="menu_ops_matrix_settings"
              sequence="10"/>

    <!-- Leaf menus with actions -->
    <menuitem id="menu_ops_companies"
              name="Companies"
              parent="menu_ops_organization"
              action="action_ops_companies"
              sequence="10"/>

    <menuitem id="menu_ops_branch"
              name="Branches"
              parent="menu_ops_organization"
              action="action_ops_branch"
              sequence="20"/>

    <menuitem id="menu_ops_business_unit"
              name="Business Units"
              parent="menu_ops_organization"
              action="action_ops_business_unit"
              sequence="30"/>

    <!-- ==================== GOVERNANCE ==================== -->
    <menuitem id="menu_ops_governance"
              name="Governance"
              parent="menu_ops_matrix_settings"
              sequence="20"/>

    <menuitem id="menu_ops_governance_rules"
              name="Governance Rules"
              parent="menu_ops_governance"
              action="action_ops_governance_rules"
              sequence="10"/>

    <menuitem id="menu_ops_approval_dashboard"
              name="Approval Dashboard"
              parent="menu_ops_governance"
              action="action_ops_approval_dashboard"
              sequence="20"/>

    <menuitem id="menu_ops_approval_request"
              name="Approval Requests"
              parent="menu_ops_governance"
              action="action_ops_approval_request"
              sequence="30"/>

    <menuitem id="menu_ops_governance_violation_report"
              name="Violations Report"
              parent="menu_ops_governance"
              action="action_ops_governance_violation_report"
              sequence="40"/>

    <menuitem id="menu_ops_archive_policy"
              name="Archive Policies"
              parent="menu_ops_governance"
              action="action_ops_archive_policy"
              sequence="50"/>

    <menuitem id="menu_ops_dashboard_widget_management"
              name="Dashboard Widgets"
              parent="menu_ops_governance"
              action="action_ops_dashboard_widget_management"
              sequence="60"/>

    <!-- ==================== PERSONAS ==================== -->
    <menuitem id="menu_ops_personas"
              name="Personas &amp; Delegation"
              parent="menu_ops_matrix_settings"
              sequence="30"/>

    <menuitem id="menu_ops_persona"
              name="Personas"
              parent="menu_ops_personas"
              action="action_ops_persona"
              sequence="10"/>

    <menuitem id="menu_ops_persona_delegation"
              name="Delegations"
              parent="menu_ops_personas"
              action="action_ops_persona_delegation"
              sequence="20"/>

    <!-- ==================== SLA ==================== -->
    <menuitem id="menu_ops_sla"
              name="SLA Management"
              parent="menu_ops_matrix_settings"
              sequence="40"/>

    <menuitem id="menu_ops_sla_template"
              name="SLA Templates"
              parent="menu_ops_sla"
              action="action_ops_sla_template"
              sequence="10"/>

    <menuitem id="menu_ops_sla_instance"
              name="SLA Instances"
              parent="menu_ops_sla"
              action="action_ops_sla_instance"
              sequence="20"/>

    <!-- ==================== API ==================== -->
    <menuitem id="menu_ops_api"
              name="API &amp; Integration"
              parent="menu_ops_matrix_settings"
              sequence="50"/>

    <menuitem id="menu_ops_api_keys"
              name="API Keys"
              parent="menu_ops_api"
              action="action_ops_api_keys"
              sequence="10"/>

    <menuitem id="menu_ops_audit_logs"
              name="Audit Logs"
              parent="menu_ops_api"
              action="action_ops_audit_logs"
              sequence="20"/>

    <menuitem id="menu_ops_api_analytics"
              name="API Analytics"
              parent="menu_ops_api"
              action="action_ops_api_analytics"
              sequence="30"/>

    <!-- ==================== ANALYTIC (Accounting config but in core) ==================== -->
    <menuitem id="menu_ops_analytic_setup"
              name="Analytic Setup"
              parent="account.menu_finance_configuration"
              action="action_ops_analytic_setup"
              sequence="100"/>

    <!-- ==================== INVENTORY OPERATIONS ==================== -->
    <!-- Only if stock is in depends -->
    <menuitem id="menu_ops_inter_branch_transfer"
              name="Inter-Branch Transfers"
              parent="stock.menu_stock_warehouse_mgmt"
              action="action_ops_inter_branch_transfer"
              sequence="50"/>

</odoo>
```

### Rule 4: ops_matrix_accounting Defines All Accounting Menus

**File: `ops_matrix_accounting/views/ops_menu_accounting.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- ================================================================
         OPS MATRIX ACCOUNTING - ACCOUNTING APP MENUS
         
         This module defines its own menu tree under Accounting app.
         Does NOT depend on any sibling module menus.
         ================================================================ -->

    <!-- ==================== MAIN CONTAINER ==================== -->
    <menuitem id="menu_ops_accounting_root"
              name="OPS Accounting"
              parent="account.menu_finance"
              sequence="90"/>

    <!-- ==================== ASSETS ==================== -->
    <menuitem id="menu_ops_asset_root"
              name="Assets"
              parent="menu_ops_accounting_root"
              sequence="10"/>

    <menuitem id="menu_ops_asset_list"
              name="Assets"
              parent="menu_ops_asset_root"
              action="action_ops_asset"
              sequence="10"/>

    <menuitem id="menu_ops_asset_depreciation"
              name="Depreciation Entries"
              parent="menu_ops_asset_root"
              action="action_ops_asset_depreciation"
              sequence="20"/>

    <menuitem id="menu_ops_asset_config"
              name="Configuration"
              parent="menu_ops_asset_root"
              sequence="50"/>

    <menuitem id="menu_ops_asset_category"
              name="Asset Categories"
              parent="menu_ops_asset_config"
              action="action_ops_asset_category"
              sequence="10"/>

    <!-- ==================== REPORTS ==================== -->
    <menuitem id="menu_ops_reports"
              name="Financial Reports"
              parent="menu_ops_accounting_root"
              sequence="20"/>

    <menuitem id="menu_ops_general_ledger_report"
              name="General Ledger"
              parent="menu_ops_reports"
              action="action_ops_general_ledger_wizard"
              sequence="10"/>

    <menuitem id="menu_ops_general_ledger_enhanced"
              name="Enhanced General Ledger"
              parent="menu_ops_reports"
              action="action_ops_general_ledger_enhanced"
              sequence="15"/>

    <menuitem id="menu_ops_financial_report_wizard"
              name="Financial Report"
              parent="menu_ops_reports"
              action="action_ops_financial_report_wizard"
              sequence="20"/>

    <menuitem id="menu_ops_budget"
              name="Budget Analysis"
              parent="menu_ops_reports"
              action="action_ops_budget"
              sequence="30"/>

    <menuitem id="menu_ops_company_consolidation"
              name="Company Consolidation"
              parent="menu_ops_reports"
              action="action_ops_company_consolidation"
              sequence="40"/>

    <menuitem id="menu_ops_branch_report"
              name="Branch Report"
              parent="menu_ops_reports"
              action="action_ops_branch_report"
              sequence="50"/>

    <menuitem id="menu_ops_business_unit_report"
              name="Business Unit Report"
              parent="menu_ops_reports"
              action="action_ops_business_unit_report"
              sequence="60"/>

    <menuitem id="menu_ops_consolidated_balance_sheet"
              name="Consolidated Balance Sheet"
              parent="menu_ops_reports"
              action="action_ops_consolidated_balance_sheet"
              sequence="70"/>

    <menuitem id="menu_ops_matrix_profitability"
              name="Matrix Profitability"
              parent="menu_ops_reports"
              action="action_ops_matrix_profitability"
              sequence="80"/>

    <!-- ==================== PDC MANAGEMENT ==================== -->
    <menuitem id="menu_ops_pdc_root"
              name="PDC Management"
              parent="menu_ops_accounting_root"
              sequence="30"/>

    <menuitem id="menu_ops_pdc_receivable"
              name="PDC Receivable"
              parent="menu_ops_pdc_root"
              action="action_ops_pdc_receivable"
              sequence="10"/>

    <menuitem id="menu_ops_pdc_payable"
              name="PDC Payable"
              parent="menu_ops_pdc_root"
              action="action_ops_pdc_payable"
              sequence="20"/>

</odoo>
```

### Rule 5: ops_matrix_reporting Uses Native App Parents

**File: `ops_matrix_reporting/views/ops_menu_reporting.xml`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- ================================================================
         OPS MATRIX REPORTING - ANALYTICS MENUS
         
         This module adds analytics menus to NATIVE Odoo apps.
         It does NOT depend on ops_matrix_accounting.
         Uses ops_matrix_core for settings integration.
         ================================================================ -->

    <!-- ==================== SETTINGS: TOOLS ==================== -->
    <!-- Extends the core settings menu -->
    <menuitem id="menu_ops_reporting_tools"
              name="Reporting Tools"
              parent="ops_matrix_core.menu_ops_matrix_settings"
              sequence="60"/>

    <menuitem id="menu_ops_excel_export"
              name="Excel Export"
              parent="menu_ops_reporting_tools"
              action="action_ops_excel_export_wizard"
              sequence="10"/>

    <!-- ==================== ACCOUNTING ANALYTICS ==================== -->
    <!-- Only appears if account module is installed (via depends) -->
    <menuitem id="menu_ops_accounting_analytics"
              name="OPS Analytics"
              parent="account.menu_finance_reports"
              sequence="100"/>

    <menuitem id="menu_ops_financial_analytics"
              name="Financial Analytics"
              parent="menu_ops_accounting_analytics"
              action="action_ops_financial_analytics"
              sequence="10"/>

    <!-- ==================== SALES ANALYTICS ==================== -->
    <!-- Only appears if sale module is installed -->
    <menuitem id="menu_ops_sales_analytics_root"
              name="OPS Analytics"
              parent="sale.sale_menu_root"
              sequence="90"
              groups="sales_team.group_sale_salesman"/>

    <menuitem id="menu_ops_sales_analytics"
              name="Sales Analytics"
              parent="menu_ops_sales_analytics_root"
              action="action_ops_sales_analytics"
              sequence="10"/>

    <!-- ==================== INVENTORY ANALYTICS ==================== -->
    <menuitem id="menu_ops_inventory_analytics_root"
              name="OPS Analytics"
              parent="stock.menu_stock_root"
              sequence="90"/>

    <menuitem id="menu_ops_inventory_analytics"
              name="Inventory Analytics"
              parent="menu_ops_inventory_analytics_root"
              action="action_ops_inventory_analytics"
              sequence="10"/>

</odoo>
```

---

## PHASE 4: HANDLE OPTIONAL MODULE DEPENDENCIES

### Problem: ops_matrix_reporting has sales analytics, but `sale` might not be installed

**Solution A: Separate Data Files (Recommended)**

```python
# ops_matrix_reporting/__manifest__.py
{
    'name': 'OPS Matrix Reporting',
    'version': '19.0.1.0.0',
    'depends': [
        'ops_matrix_core',  # Always required
        'account',          # Always required for financial analytics
        'stock',            # Always required for inventory analytics
        # 'sale' is NOT in depends - optional
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ops_menu_reporting_base.xml',      # Core menus (settings, accounting, inventory)
        # Sales menus are in a separate file - see below
    ],
}
```

**Create bridge module for Sale integration:**

```python
# ops_matrix_reporting_sale/__manifest__.py
{
    'name': 'OPS Matrix Reporting - Sales',
    'version': '19.0.1.0.0',
    'depends': [
        'ops_matrix_reporting',
        'sale',  # Now we can safely depend on sale
    ],
    'data': [
        'views/ops_menu_reporting_sale.xml',  # Sales analytics menus
    ],
    'auto_install': True,  # Auto-install when both deps are present!
}
```

**Solution B: Use Try/Except in Post-Init Hook (Not Recommended)**

---

## PHASE 5: CLEANUP & CONSOLIDATION

### Step 5.1: Remove Old Scattered Menu Files

After creating the consolidated menu files, remove or empty these:

```bash
# List files to review for consolidation
find addons/ops_matrix_* -name "*menu*.xml" -type f

# Expected old files to consolidate:
# - ops_matrix_accounting/views/ops_accounting_menus.xml → merge into ops_menu_accounting.xml
# - ops_matrix_accounting/views/ops_asset_menu.xml → merge into ops_menu_accounting.xml
# - ops_matrix_core/views/res_company_views.xml (menu parts) → extract to ops_menu_settings.xml
# - ops_matrix_reporting/views/reporting_menu.xml → replace with ops_menu_reporting.xml
```

### Step 5.2: Update Manifests

Ensure new menu files are loaded FIRST:

```python
# ops_matrix_core/__manifest__.py
{
    'data': [
        # 1. Menus first (defines parent containers)
        'views/ops_menu_settings.xml',
        
        # 2. Security
        'security/ir.model.access.csv',
        
        # 3. Views (in dependency order)
        'views/ops_branch_views.xml',
        'views/ops_business_unit_views.xml',
        # ... etc
    ],
}
```

### Step 5.3: Remove Broken References

Fix these identified broken parents:

```xml
<!-- BEFORE: ops_asset_menu.xml line 7 -->
parent="ops_matrix_accounting.menu_ops_accounting"  <!-- DOESN'T EXIST -->

<!-- AFTER -->
parent="ops_matrix_accounting.menu_ops_asset_root"
```

```xml
<!-- BEFORE: ops_product_request_views.xml -->
parent="ops_approval_dashboard_views.menu_ops_matrix_root"  <!-- DOESN'T EXIST -->

<!-- AFTER -->
parent="ops_matrix_core.menu_ops_governance"  <!-- Or appropriate parent -->
```

---

## PHASE 6: VALIDATION CHECKLIST

Run these validations:

### 6.1: No Cross-Module Menu References

```bash
# Should return EMPTY for sibling modules
grep -rn 'ops_matrix_accounting\.' addons/ops_matrix_core/views/*.xml
grep -rn 'ops_matrix_accounting\.' addons/ops_matrix_reporting/views/*.xml
grep -rn 'ops_matrix_reporting\.' addons/ops_matrix_core/views/*.xml
grep -rn 'ops_matrix_reporting\.' addons/ops_matrix_accounting/views/*.xml
```

### 6.2: All Parents Exist

```bash
# Extract all parent references
grep -rh 'parent="' addons/ops_matrix_*/views/*.xml | \
    grep -oP 'parent="\K[^"]+' | sort -u > /tmp/parents.txt

# Check each one exists (manual review needed for native Odoo menus)
cat /tmp/parents.txt
```

### 6.3: Test Each Module Independently

```bash
# Test core alone
./odoo-bin -d test_core --init=ops_matrix_core --stop-after-init

# Test core + accounting
./odoo-bin -d test_acc --init=ops_matrix_core,ops_matrix_accounting --stop-after-init

# Test core + reporting (without accounting)
./odoo-bin -d test_rep --init=ops_matrix_core,ops_matrix_reporting --stop-after-init

# Test all together
./odoo-bin -d test_all --init=ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init
```

---

## DELIVERABLES

1. **Modular Menu Files:**
   - `ops_matrix_core/views/ops_menu_settings.xml` (NEW)
   - `ops_matrix_accounting/views/ops_menu_accounting.xml` (NEW)
   - `ops_matrix_reporting/views/ops_menu_reporting.xml` (NEW)

2. **Bridge Module (if needed):**
   - `ops_matrix_reporting_sale/` (for optional sale integration)

3. **Updated Manifests:**
   - All `__manifest__.py` files with correct data loading order

4. **Cleanup:**
   - List of old files to remove/archive
   - Migration script for existing installations

5. **Validation Report:**
   - Screenshot of each module installed independently
   - Confirmation of no cross-module references

---

## SUCCESS CRITERIA

| Criteria | Validation |
|----------|------------|
| ✅ Core installs alone | Menu appears in Settings only |
| ✅ Core + Accounting | Settings + Accounting menus appear |
| ✅ Core + Reporting | Settings + Analytics menus (no accounting) |
| ✅ All modules | Complete menu structure |
| ✅ No broken parents | Zero XML errors on upgrade |
| ✅ No empty containers | Every parent has children or is hidden |
| ✅ Consistent naming | All use `menu_ops_*` pattern |
```

---

## 📊 Summary: Modular vs Centralized

| Aspect | ❌ Centralized | ✅ Modular |
|--------|---------------|-----------|
| **ops_matrix_core** | Defines ALL menus | Defines ONLY its menus |
| **ops_matrix_accounting** | Just updates parents | Defines own menu tree |
| **ops_matrix_reporting** | References accounting menus | Uses native Odoo parents |
| **Install core only** | Empty accounting menus visible | Clean - only core menus |
| **Dependency errors** | Possible | Eliminated |
| **Maintenance** | Single point of failure | Each module independent |

This updated prompt ensures your framework remains **truly modular** and works correctly for any combination of installed modules! 🎯

---

## Implementation Progress

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Audit | ⬜ Pending | |
| 2. Architecture Review | ⬜ Pending | |
| 3. Create Menu Files | ⬜ Pending | |
| 4. Update Manifests | ⬜ Pending | |
| 5. Cleanup Old Files | ⬜ Pending | |
| 6. Validation | ⬜ Pending | |
