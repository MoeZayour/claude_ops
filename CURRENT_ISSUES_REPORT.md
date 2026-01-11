# OPS Framework - Current Issues Report

**Generated:** 2026-01-11
**Database:** ops_testing
**Version:** v1.3.0/v1.3.1

---

## 🔴 CRITICAL ISSUES

### 1. Financial Reports Wizard Missing
**Status:** NOT FOUND / INCOMPLETE
**Impact:** HIGH - Users cannot generate financial reports
**Description:** 
- Although `ops.financial.report.wizard` exists in `ops_matrix_accounting`, it is either not installed, hidden by security groups, or incomplete.
- Users expect a wizard for Balance Sheet, P&L, Trial Balance, Cash Flow with date range and branch/BU filters.
- Current analytics are pivot-based; formal PDF/Excel output via wizard is missing or non-functional.

**Location Expected:** 
- Reporting → Financial Reports → Generate Report (wizard)
- Or: Accounting → Reports → Financial Reports

**Action Required:** Verify installation, fix security access, and ensure wizard handles all 4 core reports.

---

### 2. Admin Privileges Not Working
**Status:** BROKEN
**Impact:** CRITICAL - Admin cannot manage system
**Description:**
- `group_ops_admin_power` exists but may not be correctly assigned to the admin user.
- Security rules in `ir_rule.xml` and ACLs in `ir.model.access.csv` might have conflicts or missing permissions for certain models.

**Action Required:** 
- Ensure admin user is in OPS Admin Power group.
- Grant full CRUD access on all OPS models.
- Fix any restrictive record rules that block admin visibility.

---

### 3. No Create Button on BU/Branches
**Status:** BROKEN
**Impact:** HIGH - Cannot create company structure
**Description:**
- "Business Units" and "Branches" views lack the ability to create new records.
- Likely caused by `create="0"` in tree/form views or restrictive ACLs.

**Action Required:** Fix views and security to allow creation for admins/managers.

---

### 4. OPS Matrix in Main Menu
**Status:** INCORRECT PLACEMENT
**Impact:** MEDIUM - Confusing navigation
**Description:**
- "OPS Matrix" appears as a top-level menu.
- Should be moved to Configuration or a dedicated submenu to avoid clutter.

**Action Required:** 
- Relocate OPS Matrix menu items.
- Streamline the main menu bar.

---

### 5. Approvals Menu Missing
**Status:** NOT FOUND
**Impact:** HIGH - Core feature not accessible
**Description:**
- No dedicated "Approvals" top-level menu.
- Users need a central place for My Approvals, Pending Approvals, History, and SLA Tracking.

**Action Required:** Create a unified Approvals root menu and submenus.

---

## 🟡 MEDIUM ISSUES

### 6. Dashboard RPC Errors
**Status:** BROKEN
**Impact:** MEDIUM - Dashboards don't load
**Description:** All 4 dashboards in `ops_matrix_reporting` show RPC service errors (likely due to Odoo 19 service changes).
**Action Required:** Update dashboard JS/OWL components to use correct ORM calls.

### 7. PDC View Type Errors
**Status:** BROKEN
**Impact:** MEDIUM - PDC menus don't work
**Description:** Using 'tree' instead of 'list' as the view type in action definitions (Odoo 17+ standard).
**Action Required:** Update actions to use `view_mode="list,form"`.

---

## 📋 INVESTIGATION FINDINGS

- **Module Inventory**: Core modules are present, but the accounting integration for reporting is disjointed from the standalone reporting module.
- **Security**: The "Admin Power" group is defined but not effectively applied.
- **Redundancy**: Multiple actions pointing to the same wizard suggest fragmented development.

---

## 🎯 PRIORITY MATRIX

**P0 (Blocking Production):**
1. Admin privileges & Create buttons
2. Financial Reports wizard accessibility
3. Approvals menu creation

**P1 (Core Features):**
4. Dashboard RPC fixes
5. PDC view type fixes
6. Menu organization (OPS Matrix cleanup)

**P2 (Polish):**
7. Report templates styling
8. Documentation synchronization

---

**Status:** DRAFT - Investigation Complete
**Next Step:** Define Reporting Philosophy based on these gaps.
