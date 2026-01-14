# OPS Framework - Architectural Specification & Gap Analysis

**Version:** 2.0 (Target Framework Definition)
**Date:** January 14, 2026
**Status:** DRAFT (Awaiting Execution of Recovery Plan)

---

## 1. Executive Summary

The **OPS Framework** is an enterprise-grade extension for Odoo 19 Community Edition designed to transform the standard ERP into a **Corporate Matrix Operation System**.

Unlike standard Odoo, which is company-centric, OPS Framework introduces a **Matrix Architecture** where every transaction and access right is governed by the intersection of three dimensions:
1.  **Branch** (Geographical/Operational Location)
2.  **Business Unit** (Strategic Line of Business)
3.  **Persona** (Role-based Dimensional Access)

### Current State Assessment (v1.5.0)
While the core "Matrix" logic (`ops_matrix_core`) is implemented and functional, the peripheral systems—specifically **Reporting**, **Financial Controls**, and **Dashboarding**—have deviated significantly from the original comprehensive vision. The framework is currently ~80% complete technically but only ~60% complete functionally against the original "Big Plan."

---

## 2. The Matrix Philosophy (Core Architecture)

The heart of the framework is the **OPS Matrix**, defined in `ops_matrix_core`.

### 2.1 The Three Dimensions

| Dimension | Model | Description | Implementation |
| :--- | :--- | :--- | :--- |
| **Branch** | `ops.branch` | Distinct from Odoo Multi-Company. Represents a physical reporting location (e.g., "Dubai HQ", "Jeddah Warehouse"). | **Implemented.** Linked to Transactions & Accounting entries. |
| **Business Unit** (BU) | `ops.business.unit` | A vertical P&L center (e.g., "Retail", "Wholesale", "Projects"). Cross-cuts through Branches. | **Implemented.** Critical for "Segment Reporting". |
| **Persona** | `ops.persona` | The User's avatar in the Matrix. A user can have multiple Personas (e.g., "Dubai Sales Manager" vs "Projects Director"). | **Implemented.** Defines the *intersection* of accessible Branches and BUs. |

### 2.2 Security Model: "Blindness by Default"
- **Rule:** A user can *only* see records that match BOTH their active Persona's Branch list AND Business Unit list.
- **IT Admin Blindness:** IT Admins have system rights but *zero* record-level access to business transactions (Sales, Invoices, Salaries).
- **Status:** ✅ **Implemented & Verified.**

---

## 3. Module Breakdown & Technical implementation

### 3.1 `ops_matrix_core` (The Foundation)
- **Status:** ✅ **Solid**
- **Responsibilities:**
    - Schema definitions for Branch, BU, Persona.
    - `OpsMatrixMixin`: Abstract model injected into *every* transactional model (Sale Order, Invoice, Picking) to enforce Matrix rules.
    - Security Rules (`ir.rule`) utilizing the Persona logic.

### 3.2 `ops_matrix_accounting` (The Controller)
- **Status:** ⚠️ **Partial / Divergent**
- **Vision:** Complete financial control including Assets, PDCs, Budgets, and Matrix-based GL.
- **Reality:**
    - **PDC Management:** Code exists (`ops.pdc.receivable`) but UI and Menus are fragmented.
    - **Asset Management:** Standard feature set, needs better integration with BU dimension.
    - **Financial Reporting:** The `ops.financial.report.wizard` is the critical missing link for simplified, robust reporting.

### 3.3 `ops_matrix_reporting` (The Lens)
- **Status:** ❌ **Critical Gap**
- **Vision:** A centralized "Reporting Center" that pulls from all modules to generate unified snapshots (PDF/Excel) and live Dashboards.
- **Reality:**
    - Dashboards suffer from Odoo 19 RPC compatibility issues.
    - Reports are scattered across standard Odoo menus rather than central "Reporting" root.
    - "Unified Truth" philosophy (REPORTING_PHILOSOPHY.md) is not yet enforcing stricter controls.

---

## 4. Gap Analysis: Vision vs. Reality

| Feature Priority | Original Plan (Vision) | Current Reality (v1.5.0) | Gap Severity |
| :--- | :--- | :--- | :--- |
| **1. Company Structure** | Multi-Branch/BU Matrix | Implemented ✅ | None |
| **2. Persona System** | Role-based Matrix Access | Implemented ✅ | None |
| **3. Security** | Strict Field-Level & Record-Level | Mostly Implemented ✅ | Low |
| **4. SoD (Segregation of Duties)** | Governance Rules Model | Basic Implementation | Medium |
| **5. Governance / SLA** | Auto-Escalation & Approvals | Missing UI / Menus ❌ | **High** |
| **6. Excel Import/Export** | Dedicated Wizard Tools | Missing / Standard Odoo | Medium |
| **7. Three-Way Match** | Strict Invoice Validation | Logic exists, not enforced | Medium |
| **8. PDC Management** | Full Lifecycle (Hold/Deposit) | Backend only, No UI | **High** |
| **9. Budget Control** | Matrix-based Budgeting | Configured but untested | High |
| **10. Asset Management** | Integrated Assets | Module installed ✅ | Low |
| **11. Financial Reports** | **One Wizard to Rule Them All** | **MISSING ENTIRELY** ❌ | **CRITICAL** |
| **12. Dashboards** | Executive/Branch/BU Views | Broken (RPC Errors) ❌ | **High** |
| **13. Auto-List Accounts** | Dynamic GL Mapping | Not Implemented | Medium |
| **14. User Experience** | "Apple-like" Aesthetics | Standard Odoo UI | Low |
| **15. Documentation** | Full Technical & User Manuals | Draft Quality | Medium |

---

## 5. Recovery Plan (The "Fix")

To bridge the gap between v1.5.0 and the Vision, the following phases are required.

### Phase 1: The Reporting Rescue (Immediate)
**Goal:** Restore visibility and trust.
1.  **Implement `ops.financial.report.wizard`:** A single UI to generate Balance Sheet, P&L, and Cash Flow, filtered by Branch/BU.
2.  **Fix Dashboards:** Update JS/OWL code to fix Odoo 19 RPC errors.
3.  **Centralize Reporting:** Move all reports to a root "Reporting" menu.

### Phase 2: Governance & Flow (Short Term)
**Goal:** Enforce control.
1.  **Activate "Approvals" Menu:** Expose the Governance logic to users.
2.  **Enable PDC UI:** Create Views and Actions for Post-Dated Checks.
3.  **Enforce SoD:** Activate the blocking rules for conflicting duties.

### Phase 3: Polish & "Unified Truth" (Final)
**Goal:** Perfection.
1.  **Data Seeding:** prove all 15 priorities with live data.
2.  **Styles:** Apply the "Premium" aesthetic tweaks.
3.  **Documentation:** Finalize the User Manuals.

---
**Verdict:** The framework is structurally sound but functionally incomplete. The "Deviations" are primarily in the *UI/UX layer* (menus, wizards, dashboards) and *process enforcement*, while the backend data model remains true to the Matrix design.
