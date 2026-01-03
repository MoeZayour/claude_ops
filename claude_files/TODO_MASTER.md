# OPS Framework - Development TODO (MASTER)

**Version**: 2.0  
**Created**: January 2, 2026  
**Last Updated**: January 3, 2026  
**Status**: ACTIVE - Single source of truth for all tasks  

---

## IMPORTANT NOTES

**This is the MASTER TODO file** - There should be NO other TODO files.

- Old files (`OPS_FRAMEWORK_TODO.md`, `OPS_FRAMEWORK_TODO_v1_1.md`) are ARCHIVED
- This file is continuously updated (no version suffix)
- Status uses ASCII characters only: `[DONE]`, `[TODO]`, `[IN PROGRESS]`, `[BLOCKED]`

---

## CURRENT SESSION STATUS

**Date**: January 3, 2026  
**Phase**: Phase 1 - Foundation & Security  
**Current Version**: 19.0.1.3  
**Next Version**: 19.0.1.4 (after Priority #5 complete)

### What Was Completed Today (Jan 3, 2026)

1. [DONE] All 18 personas defined in `ops_persona_templates.xml`
2. [DONE] All 25 governance rules defined in `ops_governance_rule_templates.xml`
3. [DONE] IT Admin blindness - 20 record rules in `ir_rule_it_admin.xml`
4. [DONE] Cost/Margin locked by default - all views updated
5. [DONE] Project organization - PROJECT_STRUCTURE.md created
6. [DONE] Agent rules - AGENT_RULES.md created
7. [IN PROGRESS] Documentation consolidation

### What's Next (Immediate Priority)

**Priority #5**: Complete Document Lock During Approval
- File: `models/ops_approval_request.py`
- Status: Basic `approval_locked` field exists, needs completion

---

## PRIORITY LEGEND

- `[CRITICAL]` - Blocks installation/usage
- `[HIGH]` - Core functionality
- `[MEDIUM]` - Important features
- `[LOW]` - Nice to have
- `[DONE]` - Completed
- `[IN PROGRESS]` - Currently working on
- `[BLOCKED]` - Cannot proceed (waiting on something)
- `[TODO]` - Not started

---

## PHASE 1: FOUNDATION & SECURITY

### 1. Installation & Setup

#### 1.1 Data Files (Pre-loaded)
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [CRITICAL] | Create ir_module_category.xml | Completed Jan 2 |
| [DONE] | [CRITICAL] | Create res_groups.xml | 18 groups - Completed Jan 3 |
| [DONE] | [CRITICAL] | Create ir_sequence_data.xml | Completed Jan 2 |
| [DONE] | [CRITICAL] | Create ir_cron_data.xml | Completed Jan 2 |
| [DONE] | [CRITICAL] | Create ops_asset_data.xml | Completed Jan 2 |
| [DONE] | [CRITICAL] | Remove Enterprise dependency | spreadsheet_dashboard removed |
| [TODO] | [HIGH] | Create preloaded Chart of Accounts | FIFO + Direct valuation |
| [TODO] | [HIGH] | Create preloaded SLA templates | Archived by default |
| [TODO] | [MEDIUM] | Create welcome wizard | Company setup |

#### 1.2 Mandatory Configurations
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Inventory valuation settings | Define during sanity check |
| [TODO] | [HIGH] | Accounting method defaults | Define during sanity check |
| [TODO] | [CRITICAL] | Auto-create default Branch on company | Every company needs >= 1 branch |
| [TODO] | [CRITICAL] | Auto-create default BU on company | Every company needs >= 1 BU |
| [DONE] | [CRITICAL] | Cost/Margin LOCKED by default | Completed Jan 3 |
| [TODO] | [CRITICAL] | Export security hooks | Limit to viewed doc only |

---

### 2. Personas & Access Control

#### 2.1 Persona Templates (All Archived by Default)

| Status | Priority | Persona | In Code? | Notes |
|--------|----------|---------|----------|-------|
| [DONE] | [HIGH] | P00 - System Admin | YES | Break-glass only |
| [DONE] | [CRITICAL] | P01 - IT Admin (BLIND) | YES | Daily IT ops |
| [DONE] | [HIGH] | P02 - Executive/CEO | YES | Read-only oversight |
| [DONE] | [HIGH] | P03 - CFO/Owner | YES | Full financial |
| [DONE] | [HIGH] | P04 - BU Leader | YES | Cross-branch in BU |
| [DONE] | [HIGH] | P05 - Branch Manager | YES | Branch oversight |
| [DONE] | [HIGH] | P06 - Sales Manager | YES | Sales + cost/margin |
| [DONE] | [HIGH] | P07 - Purchase Manager | YES | Purchase + cost |
| [DONE] | [HIGH] | P08 - Inventory Manager | YES | Inventory + valuation |
| [DONE] | [HIGH] | P09 - Finance Manager | YES | Finance + cost/margin |
| [DONE] | [HIGH] | P10 - Sales Representative | YES | Sales only |
| [DONE] | [HIGH] | P11 - Purchase Officer | YES | Purchase only |
| [DONE] | [HIGH] | P12 - Warehouse Operator | YES | Warehouse only |
| [DONE] | [HIGH] | P13 - AR Clerk | YES | Receivables |
| [DONE] | [HIGH] | P14 - AP Clerk | YES | Payables |
| [DONE] | [HIGH] | P15 - Treasury Officer | YES | Payments |
| [DONE] | [HIGH] | P16 - Accountant/Controller | YES | Full accounting |
| [DONE] | [MEDIUM] | P17 - HR/Payroll Specialist | YES | HR only |

**Total**: 18/18 personas defined (100% complete)

#### 2.2 Security Groups

| Status | Priority | Group | Purpose |
|--------|----------|-------|---------|
| [DONE] | [CRITICAL] | group_ops_user | Basic OPS access |
| [DONE] | [CRITICAL] | group_ops_manager | Branch/BU management |
| [DONE] | [CRITICAL] | group_ops_admin | OPS configuration |
| [DONE] | [CRITICAL] | group_ops_it_admin | IT Admin (BLIND) |
| [DONE] | [HIGH] | group_ops_see_cost | Cost visibility |
| [DONE] | [HIGH] | group_ops_see_margin | Margin visibility |
| [DONE] | [HIGH] | group_ops_see_valuation | Valuation visibility |
| [DONE] | [HIGH] | 11 other functional groups | Sales, Purchase, etc. |

**Total**: 18/18 security groups defined (100% complete)

#### 2.3 Persona Combination Logic
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Design persona combination UI | Multiple personas per user |
| [TODO] | [HIGH] | Implement group merging | Union of all groups |
| [TODO] | [HIGH] | Handle conflicting rules | Most permissive/restrictive logic |
| [TODO] | [MEDIUM] | Preset combinations | "Small Business Pack" |

---

### 3. IT Admin Blindness

#### 3.1 Record Rules (Exclude from Business Data)
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [CRITICAL] | Exclude from sale.order | 20 rules created |
| [DONE] | [CRITICAL] | Exclude from purchase.order | Completed Jan 3 |
| [DONE] | [CRITICAL] | Exclude from account.move | Completed Jan 3 |
| [DONE] | [CRITICAL] | Exclude from account.payment | Completed Jan 3 |
| [DONE] | [CRITICAL] | Exclude from account.bank.statement | Completed Jan 3 |
| [DONE] | [HIGH] | Exclude from stock valuation | Completed Jan 3 |
| [DONE] | [HIGH] | Allow audit log metadata only | Completed Jan 3 |

#### 3.2 Menu Hiding for IT Admin
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Hide Sales menu | Except OPS config |
| [TODO] | [HIGH] | Hide Purchase menu | Except OPS config |
| [TODO] | [HIGH] | Hide Accounting menu | Except OPS config |
| [TODO] | [HIGH] | Hide Inventory value reports | Keep qty reports |

---

### 4. Governance Engine

#### 4.1 Governance Rule Templates

| Status | Priority | Rule Category | Count | Notes |
|--------|----------|---------------|-------|-------|
| [DONE] | [HIGH] | Sales Order rules | 5 | Discount & amount thresholds |
| [DONE] | [HIGH] | Margin rules | 2 | Minimum margin enforcement |
| [DONE] | [HIGH] | Purchase Order rules | 3 | Amount thresholds |
| [DONE] | [HIGH] | Payment rules | 2 | Multi-level approval |
| [DONE] | [HIGH] | Inventory rules | 3 | Adjustment & scrap |
| [DONE] | [HIGH] | Invoice rules | 1 | Credit note control |
| [DONE] | [HIGH] | Master Data rules | 4 | Credit limits, blocks |
| [DONE] | [HIGH] | User Management rules | 2 | Creation & permissions |
| [DONE] | [HIGH] | Transfer rules | 2 | Cross-BU, inter-branch |
| [DONE] | [HIGH] | Asset rules | 1 | Disposal approval |

**Total**: 25/25 governance rules defined (100% complete)

#### 4.2 Segregation of Duties (SoD)
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [CRITICAL] | Block same user create+confirm SO | If > threshold |
| [TODO] | [CRITICAL] | Block same user create+confirm PO | If > threshold |
| [TODO] | [CRITICAL] | Block same user create+validate invoice | Always |
| [TODO] | [CRITICAL] | Block same user approve+execute payment | Always |
| [TODO] | [HIGH] | Alert on SoD violation attempts | Log + notify admin |

#### 4.3 Document Locking
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [HIGH] | Basic approval_locked field | Exists in ops_approval_request.py |
| [IN PROGRESS] | [CRITICAL] | Complete lock during approval | **PRIORITY #5** |
| [TODO] | [CRITICAL] | Recall with reason | User can recall |
| [TODO] | [CRITICAL] | Reject with mandatory reason | Approver explains |
| [TODO] | [HIGH] | Approval in chatter | Show stages with dates |

---

### 5. Data Compartmentalization

#### 5.1 Cost & Margin Visibility
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [CRITICAL] | Lock cost_price by default | All users |
| [DONE] | [CRITICAL] | Lock margin by default | All users |
| [DONE] | [CRITICAL] | Create group_ops_see_cost | Grant explicitly |
| [DONE] | [CRITICAL] | Create group_ops_see_margin | Grant explicitly |
| [TODO] | [HIGH] | Admin UI to grant access | Per user toggle |

#### 5.2 Field Visibility
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [CRITICAL] | Hide sales_price from Purchase | Via groups |
| [TODO] | [CRITICAL] | Hide all prices from Warehouse | Via groups |
| [TODO] | [HIGH] | Hide supplier from Sales | Via record rules |
| [TODO] | [HIGH] | Hide customer from Purchase | Via record rules |

#### 5.3 Data Export Security
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [CRITICAL] | Limit to viewed document only | No bulk export |
| [TODO] | [CRITICAL] | Exclude critical fields | Cost, margin, bank |
| [TODO] | [CRITICAL] | Log all export attempts | User, doc, timestamp |
| [TODO] | [HIGH] | Block sensitive reports | Financial statements |
| [TODO] | [HIGH] | Export approval workflow | Optional per company |

---

## PHASE 2: SALES & DOCUMENT FEATURES

### 6. Sales Order Enhancements
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Verify SO Print Reports | Check existing |
| [TODO] | [HIGH] | Excel Import for SO lines | Section/Model/Qty format |
| [TODO] | [CRITICAL] | All-or-nothing validation | **PRIORITY #6** |
| [TODO] | [HIGH] | Template download button | Pre-formatted |
| [TODO] | [HIGH] | Hide non-approved from portal | Until approved |
| [TODO] | [HIGH] | Customer credit check | Block if over limit |
| [TODO] | [HIGH] | Minimum margin rule | Configurable |

### 7. Purchase Enhancements
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [MEDIUM] | Excel Import for PO lines | Same as SO format |
| [TODO] | [HIGH] | Three-way match | PO <-> Receipt <-> Bill |

### 8. Inventory Enhancements
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [MEDIUM] | Cycle count scheduling | Auto-generate sheets |
| [TODO] | [HIGH] | Inter-branch transfer workflow | Request -> Approve -> Execute |
| [TODO] | [MEDIUM] | Stock aging report | Dead stock ID |
| [TODO] | [LOW] | Barcode scanning | Receipts/deliveries |

### 9. Accounting Enhancements
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [HIGH] | PDC Management | Exists - may enhance |
| [TODO] | [MEDIUM] | Bank reconciliation wizard | Simplified matching |
| [TODO] | [MEDIUM] | Automated payment reminders | Email overdue |

---

## PHASE 3: WORKFLOW & AUTOMATION

### 10. SLA Management
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [HIGH] | SLA Template model | Exists |
| [DONE] | [HIGH] | SLA Instance tracking | Exists |
| [DONE] | [HIGH] | SLA Mixin | Exists |
| [TODO] | [HIGH] | SLA breach escalation | Auto-notify manager |
| [TODO] | [MEDIUM] | SLA compliance dashboard | % met per team |

### 11. Delegation of Authority
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [HIGH] | Delegation model | Exists |
| [DONE] | [HIGH] | Delegation approval workflow | Exists |
| [DONE] | [HIGH] | Delegation expiry notifications | Exists |
| [TODO] | [MEDIUM] | Delegation audit report | Who/what/when |

### 12. Escalation & Automation
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Auto-escalate after X hours | Configurable |
| [TODO] | [HIGH] | Multi-level escalation | L1 -> L2 -> CFO |
| [TODO] | [MEDIUM] | Escalation notifications | Email + system |
| [TODO] | [HIGH] | Report scheduler | Select, frequency, recipients |
| [TODO] | [HIGH] | Email delivery | PDF attachment |
| [TODO] | [MEDIUM] | Report subscription | Users subscribe |

---

## PHASE 4: REPORTING & ANALYTICS

### 13. Report Configuration
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Auto-list accounts | Based on type |
| [TODO] | [HIGH] | Branch comparison | Side-by-side |
| [TODO] | [HIGH] | Profit center analysis | P&L by BU/Branch |
| [TODO] | [MEDIUM] | Custom dashboard widgets | Drag-drop KPIs |

### 14. Preloaded Templates
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Standard P&L template | Account groups preset |
| [TODO] | [HIGH] | Standard Balance Sheet | Account groups preset |
| [TODO] | [HIGH] | AR Aging template | Standard buckets |
| [TODO] | [HIGH] | AP Aging template | Standard buckets |

---

## PHASE 5: UI/UX & INTEGRATION

### 15. Dashboards
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Executive Dashboard | P02, P03 only |
| [TODO] | [HIGH] | Branch Performance | Branch managers |
| [TODO] | [HIGH] | BU Performance | BU leaders |
| [TODO] | [HIGH] | Sales Dashboard | Sales team |
| [TODO] | [HIGH] | IT Admin Dashboard | System health only |
| [TODO] | [HIGH] | Approval Dashboard | All users, filtered |

### 16. Wizards
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Initial Setup Wizard | Company, CoA, admin |
| [TODO] | [HIGH] | User Creation Wizard | Persona assignment |
| [TODO] | [MEDIUM] | Branch Creation Wizard | With warehouse |
| [TODO] | [MEDIUM] | Governance Rule Wizard | Simplified creation |

### 17. Integration Modules (Separate Addons)
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [MEDIUM] | DHL Integration | Rate, labels |
| [TODO] | [MEDIUM] | Aramex Integration | Rate, labels |
| [TODO] | [MEDIUM] | FedEx Integration | Rate, labels |
| [TODO] | [MEDIUM] | Delivery options in portal | Customer choice |

---

## TESTING & QUALITY

### 18. Persona Testing Scenarios
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [CRITICAL] | IT Admin blindness | Cannot see orders/invoices |
| [TODO] | [CRITICAL] | Sales Rep cost hiding | Cannot see cost/margin |
| [TODO] | [CRITICAL] | SoD enforcement | Cannot self-approve |
| [TODO] | [HIGH] | Combined personas | Multiple roles work |
| [TODO] | [HIGH] | Branch isolation | Cannot see other branches |

### 19. Workflow Testing
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [TODO] | [HIGH] | Approval end-to-end | SO, PO, Payment |
| [TODO] | [HIGH] | Document locking | Cannot edit locked |
| [TODO] | [HIGH] | SLA breach detection | Alerts fire |

---

## DOCUMENTATION

### 20. User Documentation
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [HIGH] | User Experience v1.2 | Complete - 18 personas |
| [TODO] | [MEDIUM] | Quick Start Guide | 5-minute setup |
| [TODO] | [MEDIUM] | Persona Reference Cards | One-pager each |
| [TODO] | [MEDIUM] | Video tutorials | Future |

### 21. Technical Documentation
| Status | Priority | Task | Notes |
|--------|----------|------|-------|
| [DONE] | [HIGH] | Core Technical Spec | Complete |
| [DONE] | [HIGH] | Accounting Technical Spec | Complete |
| [DONE] | [HIGH] | Reporting Technical Spec | Complete |
| [DONE] | [HIGH] | Project Structure | Complete Jan 3 |
| [DONE] | [HIGH] | Agent Rules | Complete Jan 3 |
| [TODO] | [HIGH] | Security Groups Reference | Complete mapping |
| [TODO] | [HIGH] | Record Rules Reference | All rules documented |
| [TODO] | [MEDIUM] | API Reference | Endpoint docs |
| [TODO] | [MEDIUM] | Developer Extension Guide | How to extend |

---

## IMMEDIATE NEXT ACTIONS

**Priority Order** (Work on these in sequence):

1. [CRITICAL] **#5 - Complete Document Lock During Approval**
   - File: `models/ops_approval_request.py`
   - Requirements: No edit, no print, recall with reason, reject with reason
   - Estimated effort: 1-2 sessions

2. [CRITICAL] **#6 - Excel Import for SO Lines**
   - Files: New wizard `wizard/sale_order_import_wizard.py`
   - Requirements: Section|Model|Qty format, all-or-nothing validation
   - Estimated effort: 2-3 sessions

3. [HIGH] **#7 - Three-Way Match Enforcement**
   - Files: Purchase order, receipt, bill models
   - Requirements: PO <-> Receipt <-> Bill validation
   - Estimated effort: 2 sessions

4. [HIGH] **#8 - Auto-Escalation**
   - Files: Governance rule, approval request
   - Requirements: Configurable hours, multi-level
   - Estimated effort: 1-2 sessions

5. [HIGH] **#9 - Auto-List Accounts in Reports**
   - Files: Financial report templates
   - Requirements: Based on report type
   - Estimated effort: 1 session

---

## COMPLETED ITEMS (Summary)

**Date: January 2-3, 2026**

- [x] Created all missing data XML files (11 files)
- [x] Removed Enterprise dependency
- [x] Created 18 persona templates
- [x] Created 25 governance rule templates
- [x] Created IT Admin blindness (20 record rules)
- [x] Implemented cost/margin locked by default
- [x] Created 18 security groups
- [x] Created User Experience Document v1.2
- [x] Created Technical Specifications (Core, Accounting, Reporting)
- [x] Created Project Structure
- [x] Created Agent Rules

**Total Completed**: 40+ tasks

---

## KNOWN ISSUES & BLOCKERS

See: `ISSUES_LOG.md` for detailed issue tracking

Current blockers: NONE

---

## IDEAS BACKLOG

*Capture ideas during development for future consideration*

| Date | Idea | Priority | Notes |
|------|------|----------|-------|
| 2026-01-02 | Small Business Pack | [MEDIUM] | One-click setup <10 employees |
| 2026-01-02 | Onboarding wizard | [MEDIUM] | Help non-tech users |
| 2026-01-03 | Mobile app | [LOW] | Native mobile experience |

---

## CHANGE LOG

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-01-02 | 1.0 | Initial TODO created | Claude |
| 2026-01-03 | 1.1 | Added recent updates | Claude |
| 2026-01-03 | 2.0 | Consolidated to MASTER, ASCII only | Claude (PM) |

---

**END OF TODO MASTER**

This is the single source of truth for all development tasks. Update after every work session.
