# OPS Framework - Reporting Implementation Plan

**Based on:** REPORTING_PHILOSOPHY.md
**Version:** 1.0
**Timeline:** 3 weeks (prioritized)

---

## 🎯 IMPLEMENTATION STRATEGY

### 1. Fix Critical Gaps (Week 1)
Establish the foundation by resolving admin access, enabling record creation, and surfacing the financial report wizard.

### 2. Operational Rollout (Week 2)
Implement specialized reports for Sales, Inventory, and Purchases, ensuring dimension-based security is strictly enforced.

### 3. Dashboard & Visualization (Week 3)
Resolve RPC errors in existing dashboards and add advanced KPIs for executive visibility.

---

## 📅 WEEK 1: FOUNDATION & ACCESSIBILITY

### Day 1-2: Security & Admin Access (P0)
- **Task**: Audit and fix `group_ops_admin_power`.
- **Task**: Remove `create="0"` from Business Unit and Branch tree/form views.
- **Task**: Verify Admin User is correctly associated with all OPS security groups.
- **Deliverable**: Admin can create/edit company structure.

### Day 3-5: Financial Reporting Foundation (P0)
- **Task**: Surface `ops.financial.report.wizard` in the Reporting menu.
- **Task**: Ensure the wizard generates standard Balance Sheet and P&L (PDF).
- **Task**: Fix visibility for `account.group_account_manager`.
- **Deliverable**: Workable financial reporting wizard accessible from main menu.

---

## 📅 WEEK 2: OPERATIONAL REPORTING

### Day 6-8: Sales & Inventory Analytics (P1)
- **Task**: Enhance `ops.sales.analysis` with margin-tier filtering.
- **Task**: Implement Inventory Valuation report by Business Unit.
- **Task**: Integrate Analytics views directly into the root Reporting menu.

### Day 9-10: Governance & PDC (P1)
- **Task**: Create "Approvals" root menu with Pending/History submenus.
- **Task**: Fix PDC list view action types (`view_mode="list,form"`).
- **Task**: Implement SLA Compliance report.

---

## 📅 WEEK 3: DASHBOARDS & POLISH

### Day 11-13: Dashboard Recovery (P1)
- **Task**: Refactor `ops_matrix_reporting` JS/OWL components for Odoo 19 service compatibility.
- **Task**: Fix RPC query errors in Executive and Branch dashboards.

### Day 14-15: Final Testing & Documentation (P2)
- **Task**: User Acceptance Testing (UAT) for all 4 core financial reports.
- **Task**: Update USER_MANUAL.md with reporting navigation sections.
- **Task**: Final code cleanup and Git tagging (`v1.4.0-reporting-update`).

---

## ✅ SUCCESS CRITERIA
- [ ] Admin has full CRUD on all OPS models.
- [ ] Financial Reports Wizard is visible and functional for managers.
- [ ] No RPC errors on Dashboards.
- [ ] Approvals menu exists and tracks SLA compliance.

