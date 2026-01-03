# OPS Framework - User Experience Document v1.2

**Framework**: OPS Matrix Framework for Odoo 19 Community Edition  
**Document Version**: 1.2  
**Date**: January 2, 2026  
**Status**: LIVING DOCUMENT  

---

## TABLE OF CONTENTS

1. [Philosophy & Core Principles](#1-philosophy--core-principles)
2. [Administrator Types - Critical Distinction](#2-administrator-types---critical-distinction)
3. [Complete Persona Catalog](#3-complete-persona-catalog)
4. [Segregation of Duties Matrix](#4-segregation-of-duties-matrix)
5. [Information Compartmentalization](#5-information-compartmentalization)
6. [Sales Department Experience](#6-sales-department-experience)
7. [Purchase Department Experience](#7-purchase-department-experience)
8. [Inventory Department Experience](#8-inventory-department-experience)
9. [Accounting Department Experience](#9-accounting-department-experience)
10. [Administration & Support Experience](#10-administration--support-experience)
11. [Feature Matrix by Persona](#11-feature-matrix-by-persona)
12. [Reports & Dashboards by Persona](#12-reports--dashboards-by-persona)
13. [Governance & Approval Workflows](#13-governance--approval-workflows)
14. [Security Groups Mapping](#14-security-groups-mapping)
15. [New Menus & Navigation](#15-new-menus--navigation)
16. [Data Export Security](#16-data-export-security)
17. [Implementation Checklist](#17-implementation-checklist)

---

## 1. PHILOSOPHY & CORE PRINCIPLES

### 1.1 Zero-Trust Decentralized Framework

The OPS Matrix Framework implements a **zero-trust, decentralized authority structure** where:

- **No single individual** can complete a fraudulent transaction from initiation to execution
- **Segregation of Duties (SoD)** is enforced at system level, not policy level
- **Information compartmentalization** prevents cross-functional data leakage
- **Audit trails** capture every action with timestamp and user identity

### 1.2 The Three Pillars

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    OPS MATRIX FRAMEWORK                         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”‚
â”‚   â”‚   BRANCHES    â”‚  â”‚ BUSINESS UNITSâ”‚  â”‚   PERSONAS    â”‚      â”‚
â”‚   â”‚  (Data Silos) â”‚  â”‚ (Oversight)   â”‚  â”‚ (Identity)    â”‚      â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â”‚
â”‚          â”‚                  â”‚                  â”‚                â”‚
â”‚          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                â”‚
â”‚                             â”‚                                   â”‚
â”‚                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”                         â”‚
â”‚                    â”‚   GOVERNANCE    â”‚                         â”‚
â”‚                    â”‚   ENGINE        â”‚                         â”‚
â”‚                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                         â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 1.3 Core Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Least Privilege** | Users get minimum access needed for their role |
| **Separation of Duties** | Creator â‰  Approver â‰  Executor â‰  Verifier |
| **Cost/Margin Locked** | Hidden from ALL by default - must grant manually |
| **Export Controlled** | Limited to viewed document, critical data excluded |
| **Defense in Depth** | Multiple layers: Groups + Personas + Record Rules |
| **Audit Everything** | All actions logged, no silent failures |

---

## 2. ADMINISTRATOR TYPES - CRITICAL DISTINCTION

### 2.1 The Two Admin Paradigms

**This is the most critical architectural decision in OPS Framework.**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    ADMINISTRATOR HIERARCHY                       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚   â”‚              SYSTEM ADMIN (Odoo base.group_system)       â”‚  â”‚
â”‚   â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€   â”‚  â”‚
â”‚   â”‚  â€¢ BYPASSES ALL RULES                                    â”‚  â”‚
â”‚   â”‚  â€¢ Full database access                                  â”‚  â”‚
â”‚   â”‚  â€¢ Can modify any record                                 â”‚  â”‚
â”‚   â”‚  â€¢ Emergency "break-glass" account                       â”‚  â”‚
â”‚   â”‚  â€¢ Should be: External consultant / Vendor / Owner       â”‚  â”‚
â”‚   â”‚  â€¢ NOT a daily-use account                               â”‚  â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                             â”‚                                   â”‚
â”‚                             â”‚ â† Clear separation                â”‚
â”‚                             â”‚                                   â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚   â”‚              IT ADMIN (ops.group_it_administrator)       â”‚  â”‚
â”‚   â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€   â”‚  â”‚
â”‚   â”‚  â€¢ CANNOT see transactional data (invoices, orders)      â”‚  â”‚
â”‚   â”‚  â€¢ CANNOT approve business transactions                  â”‚  â”‚
â”‚   â”‚  â€¢ CAN manage user accounts & access rights              â”‚  â”‚
â”‚   â”‚  â€¢ CAN configure workflows & governance rules            â”‚  â”‚
â”‚   â”‚  â€¢ CAN view audit logs & system health                   â”‚  â”‚
â”‚   â”‚  â€¢ Internal IT staff / Company admin                     â”‚  â”‚
â”‚   â”‚  â€¢ Daily operational account                             â”‚  â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 2.2 Why This Distinction Matters

| Scenario | System Admin | IT Admin |
|----------|--------------|----------|
| Create user accounts | âœ… | âœ… |
| Assign personas/groups | âœ… | âœ… |
| Configure governance rules | âœ… | âœ… |
| View all sales orders | âœ… | âŒ **BLIND** |
| View all invoices | âœ… | âŒ **BLIND** |
| View bank account balances | âœ… | âŒ **BLIND** |
| Approve a purchase order | âœ… | âŒ CANNOT |
| Execute a payment | âœ… | âŒ CANNOT |
| Modify audit logs | âœ… | âŒ CANNOT |
| Debug system issues | âœ… | âœ… (technical logs only) |

### 2.3 IT Admin Blindness Rules

The IT Admin **CANNOT ACCESS**:

```
BLIND TO:
â”œâ”€â”€ Sales Module
â”‚   â”œâ”€â”€ Sales Orders (amounts, customers)
â”‚   â”œâ”€â”€ Quotations
â”‚   â””â”€â”€ Commissions
â”œâ”€â”€ Purchase Module
â”‚   â”œâ”€â”€ Purchase Orders (amounts, vendors)
â”‚   â””â”€â”€ Vendor Bills
â”œâ”€â”€ Accounting Module
â”‚   â”œâ”€â”€ Invoices (AR/AP)
â”‚   â”œâ”€â”€ Payments
â”‚   â”œâ”€â”€ Bank Statements
â”‚   â””â”€â”€ Financial Reports
â”œâ”€â”€ Inventory (values)
â”‚   â”œâ”€â”€ Stock Valuation
â”‚   â””â”€â”€ Product Costs
â””â”€â”€ CRM
    â””â”€â”€ Pipeline values
```

The IT Admin **CAN ACCESS**:

```
VISIBLE TO:
â”œâ”€â”€ Settings
â”‚   â”œâ”€â”€ Users & Groups
â”‚   â”œâ”€â”€ Email Configuration
â”‚   â””â”€â”€ Technical Settings
â”œâ”€â”€ OPS Matrix Configuration
â”‚   â”œâ”€â”€ Branches (structure only)
â”‚   â”œâ”€â”€ Business Units (structure only)
â”‚   â”œâ”€â”€ Personas (definition only)
â”‚   â””â”€â”€ Governance Rules (configuration)
â”œâ”€â”€ Audit & Monitoring
â”‚   â”œâ”€â”€ Audit Logs (metadata, not content)
â”‚   â”œâ”€â”€ Login History
â”‚   â”œâ”€â”€ API Usage
â”‚   â””â”€â”€ System Health
â””â”€â”€ Technical
    â”œâ”€â”€ Scheduled Actions
    â”œâ”€â”€ Server Actions
    â””â”€â”€ Automation Rules
```

---

## 3. COMPLETE PERSONA CATALOG

### 3.1 Persona Hierarchy

```
                           â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                           â”‚   SYSTEM ADMIN   â”‚ â† Bypasses everything
                           â”‚  (break-glass)   â”‚
                           â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”‚                     â”‚                     â”‚
     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
     â”‚    IT ADMIN     â”‚   â”‚  EXECUTIVE    â”‚   â”‚   CFO/OWNER     â”‚
     â”‚ (config only)   â”‚   â”‚  (oversight)  â”‚   â”‚ (full business) â”‚
     â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â”‚                    â”‚                    â”‚
              â”‚            â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”           â”‚
              â”‚            â”‚  BU LEADER    â”‚           â”‚
              â”‚            â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜           â”‚
              â”‚                    â”‚                   â”‚
              â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
              â”‚   â”‚                â”‚                â”‚  â”‚
         â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â–¼â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â–¼â”€â”€â–¼â”€â”€â”€â”€â”
         â”‚   BRANCH    â”‚   â”‚   BRANCH    â”‚   â”‚  FINANCE   â”‚
         â”‚   MANAGER   â”‚   â”‚   MANAGER   â”‚   â”‚  MANAGER   â”‚
         â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                â”‚                 â”‚                 â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚           â”‚           â”‚     â”‚     â”‚           â”‚           â”‚
â”Œâ”€â”€â”€â–¼â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â–¼â”€â”€â”€â” â”‚ â”Œâ”€â”€â”€â–¼â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â–¼â”€â”€â”€â”
â”‚ SALES â”‚  â”‚PURCHASE â”‚  â”‚ STOCK â”‚ â”‚ â”‚  AR   â”‚  â”‚   AP    â”‚  â”‚TREASURYâ”‚
â”‚  REP  â”‚  â”‚ OFFICER â”‚  â”‚ USER  â”‚ â”‚ â”‚ CLERK â”‚  â”‚  CLERK  â”‚  â”‚OFFICER â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                  â”‚
                           â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”
                           â”‚ ACCOUNTANT/ â”‚
                           â”‚ CONTROLLER  â”‚
                           â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 3.2 Complete Persona Definitions

#### TIER 1: SYSTEM LEVEL

| ID | Persona | OPS Group | Odoo Groups | Branch Access | BU Access |
|----|---------|-----------|-------------|---------------|-----------|
| P00 | System Administrator | - | base.group_system | ALL | ALL |
| P01 | IT Administrator | group_it_admin | Settings/Admin | Config Only | Config Only |

#### TIER 2: EXECUTIVE LEVEL

| ID | Persona | OPS Group | Odoo Groups | Branch Access | BU Access |
|----|---------|-----------|-------------|---------------|-----------|
| P02 | Executive/CEO | group_ops_executive | Read-only all | ALL (view) | ALL (view) |
| P03 | CFO/Owner | group_ops_cfo | Account/Adviser | ALL | ALL |

#### TIER 3: BUSINESS UNIT LEVEL

| ID | Persona | OPS Group | Odoo Groups | Branch Access | BU Access |
|----|---------|-----------|-------------|---------------|-----------|
| P04 | Business Unit Leader | group_ops_bu_leader | Sales+Purchase/Manager | BU Branches | Own BU |

#### TIER 4: BRANCH MANAGEMENT LEVEL

| ID | Persona | OPS Group | Odoo Groups | Branch Access | BU Access |
|----|---------|-----------|-------------|---------------|-----------|
| P05 | Branch Manager | group_ops_manager | Sales+Inventory/Manager | Own Branch | Own BU |
| P06 | Sales Manager | group_ops_manager | Sales/Administrator | Own Branch | Own BU |
| P07 | Purchase Manager | group_ops_manager | Purchase/Administrator | Own Branch | Own BU |
| P08 | Inventory Manager | group_ops_manager | Inventory/Administrator | Own Branch | Own BU |
| P09 | Finance Manager | group_ops_manager | Account/Adviser | Own Branch | Own BU |

#### TIER 5: USER LEVEL

| ID | Persona | OPS Group | Odoo Groups | Branch Access | BU Access |
|----|---------|-----------|-------------|---------------|-----------|
| P10 | Sales Representative | group_ops_user | Sales/User, CRM/User | Own Branch | - |
| P11 | Purchase Officer | group_ops_user | Purchase/User | Own Branch | - |
| P12 | Warehouse Operator | group_ops_user | Inventory/User | Own Branch | - |
| P13 | AR Clerk | group_ops_user | Account/Billing | Own Branch | - |
| P14 | AP Clerk | group_ops_user | Account/Billing | Own Branch | - |
| P15 | Treasury Officer | group_ops_user | Account/Billing + Payment Auth | Own Branch | - |
| P16 | Accountant/Controller | group_ops_user | Account/Adviser | Own Branch | - |
| P17 | HR/Payroll Specialist | group_ops_user | Employees/User | Own Branch | - |

---

## 4. SEGREGATION OF DUTIES MATRIX

### 4.1 Transaction Lifecycle

Every business transaction follows the **4-Person Rule**:

| Activity | Initiator | Approver | Executor | Verifier |
|----------|-----------|----------|----------|----------|
| **Sales Order** | Sales Rep (P10) | Sales Manager (P06) | Warehouse (P12) | Accountant (P16) |
| **Purchase Order** | Purchase Officer (P11) | Purchase Manager (P07) | Vendor (external) | Warehouse (P12) |
| **Goods Receipt** | Warehouse (P12) | Inventory Manager (P08) | N/A | Accountant (P16) |
| **Customer Invoice** | AR Clerk (P13) | Accountant (P16) | N/A | Bank Reconciliation |
| **Vendor Bill** | AP Clerk (P14) | Accountant (P16) | N/A | Purchase Manager (P07) |
| **Payment Execution** | AP Clerk (P14) | Accountant/CFO | Treasury (P15) | Bank Reconciliation |
| **Inventory Adjustment** | Warehouse (P12) | Inventory Manager (P08) | N/A | External Auditor |

### 4.2 Forbidden Combinations (System Enforced)

```
âŒ SAME USER CANNOT:
â”œâ”€â”€ Create AND Confirm Sales Order (if > threshold)
â”œâ”€â”€ Create AND Confirm Purchase Order (if > threshold)
â”œâ”€â”€ Create Invoice AND Validate Invoice
â”œâ”€â”€ Create Payment AND Execute Payment
â”œâ”€â”€ Create Inventory Adjustment AND Approve Adjustment
â”œâ”€â”€ Receive Goods AND Record Vendor Bill
â””â”€â”€ Create User AND Assign Admin Rights (without approval)
```

---

## 5. INFORMATION COMPARTMENTALIZATION

### 5.1 What Each Department Can/Cannot See

#### Sales Department (P10, P06)
```
âœ… CAN SEE:
â”œâ”€â”€ Customer data (name, contact, address)
â”œâ”€â”€ Sales prices (list prices, discounts)
â”œâ”€â”€ Own commission rates
â”œâ”€â”€ Sales pipeline and opportunities
â””â”€â”€ Product availability (qty, not value)

âŒ CANNOT SEE:
â”œâ”€â”€ Product cost prices
â”œâ”€â”€ Supplier/vendor information
â”œâ”€â”€ Profit margins
â”œâ”€â”€ Other salespeople's commissions
â”œâ”€â”€ Accounting data (invoices, payments)
â””â”€â”€ Bank account information
```

#### Purchase Department (P11, P07)
```
âœ… CAN SEE:
â”œâ”€â”€ Vendor data (name, contact, terms)
â”œâ”€â”€ Purchase prices and costs
â”œâ”€â”€ Product specifications
â”œâ”€â”€ Delivery schedules
â””â”€â”€ Stock levels (qty)

âŒ CANNOT SEE:
â”œâ”€â”€ Sales prices
â”œâ”€â”€ Customer information
â”œâ”€â”€ Profit margins
â”œâ”€â”€ Commission structures
â””â”€â”€ Financial reports
```

#### Warehouse Department (P12, P08)
```
âœ… CAN SEE:
â”œâ”€â”€ Stock quantities and locations
â”œâ”€â”€ Product movements (in/out)
â”œâ”€â”€ Delivery addresses
â”œâ”€â”€ Product specifications
â””â”€â”€ Reorder points

âŒ CANNOT SEE:
â”œâ”€â”€ Product costs
â”œâ”€â”€ Sales prices
â”œâ”€â”€ Supplier details (beyond delivery)
â”œâ”€â”€ Customer details (beyond delivery)
â””â”€â”€ Financial data
```

#### Accounting Department (P13-P16)
```
âœ… CAN SEE:
â”œâ”€â”€ All financial transactions
â”œâ”€â”€ Invoices (AR and AP)
â”œâ”€â”€ Payments and bank statements
â”œâ”€â”€ Cost and margin data
â””â”€â”€ Financial reports

âŒ CANNOT SEE:
â”œâ”€â”€ Physical inventory locations
â”œâ”€â”€ CRM pipeline details
â”œâ”€â”€ Purchase negotiations
â”œâ”€â”€ Sales commission details
â””â”€â”€ HR/Payroll data
```

#### IT Administrator (P01)
```
âœ… CAN SEE:
â”œâ”€â”€ User accounts and groups
â”œâ”€â”€ System configuration
â”œâ”€â”€ Audit logs (metadata)
â”œâ”€â”€ API usage statistics
â””â”€â”€ Technical settings

âŒ CANNOT SEE:
â”œâ”€â”€ Transaction amounts
â”œâ”€â”€ Customer/Vendor details
â”œâ”€â”€ Invoice contents
â”œâ”€â”€ Payment details
â”œâ”€â”€ Stock valuations
â””â”€â”€ Any business data
```

---

## 6. SALES DEPARTMENT EXPERIENCE

### 6.1 Sales Representative (P10)

**What's NEW vs Standard Odoo:**

| Feature | Standard Odoo | With OPS Framework |
|---------|--------------|-------------------|
| Sales Order | Simple form | + Branch auto-assignment |
| Data Visibility | See all sales | See ONLY own branch sales |
| Pricing | See cost if configured | Cost ALWAYS hidden |
| Confirmation | Can confirm | CANNOT confirm if > threshold |
| Product Request | None | Can request new products |

**Screen: Sales Order Form**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ SALES ORDER: SO00123                              [Send by Email]â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ [Request Approval]  Status: Draft                                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Customer: ABC Company                                            â”‚
â”‚                                                                  â”‚
â”‚ â”Œâ”€ Matrix Information â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚
â”‚ â”‚ Branch:        [Downtown Store    ] â† Auto-set, read-only    â”‚â”‚
â”‚ â”‚ Business Unit: [Retail Division   ] â† Auto-set, read-only    â”‚â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”‚
â”‚                                                                  â”‚
â”‚ Order Lines:                                                     â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚
â”‚ â”‚ Product    | Qty | Unit Price | Discount | Subtotal          â”‚â”‚
â”‚ â”‚ Widget A   | 10  | $100.00    | 5%       | $950.00           â”‚â”‚
â”‚ â”‚                                                               â”‚â”‚
â”‚ â”‚ âš ï¸ Cost, Margin columns NOT VISIBLE to Sales Rep              â”‚â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”‚
â”‚                                                                  â”‚
â”‚ Total: $950.00                                                   â”‚
â”‚                                                                  â”‚
â”‚ âš ï¸ Orders > $5,000 require Sales Manager approval                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Restrictions Enforced:**
- âŒ CANNOT see Cost Price column
- âŒ CANNOT see Margin column  
- âŒ CANNOT confirm orders > threshold
- âŒ CANNOT view other branches' orders
- âŒ CANNOT access Accounting module

### 6.2 Sales Manager (P06)

**Additional Capabilities:**
- âœ… CAN see Cost and Margin columns
- âœ… CAN confirm Sales Orders
- âœ… CAN approve discount requests > X%
- âœ… CAN view all sales reps' orders in branch
- âœ… CAN access Branch Performance Dashboard

**Screen: Sales Order Form (Manager View)**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ SALES ORDER: SO00123                    [Confirm] [Send by Email]â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Order Lines:                                                     â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚
â”‚ â”‚ Product  | Qty | Price  | Cost   | Margin | Margin% | Subtotalâ”‚
â”‚ â”‚ Widget A | 10  | $100   | $60    | $40    | 40%     | $950    â”‚â”‚
â”‚ â”‚          â†‘             â†‘        â†‘       â†‘                     â”‚â”‚
â”‚ â”‚          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”´â”€ VISIBLE TO MANAGER â”‚â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 7. PURCHASE DEPARTMENT EXPERIENCE

### 7.1 Purchase Officer (P11)

**Restrictions Enforced:**
- âŒ CANNOT confirm Purchase Orders (requires manager)
- âŒ CANNOT see sales prices
- âŒ CANNOT see customer information
- âŒ CANNOT validate vendor bills
- âŒ CANNOT access payment modules

**Key Workflow: Product Request**

```
Sales Rep                Purchase Officer           Purchase Manager
    â”‚                          â”‚                          â”‚
    â”‚ Creates Product          â”‚                          â”‚
    â”‚ Request â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶                          â”‚
    â”‚                          â”‚                          â”‚
    â”‚                    Sets product data                â”‚
    â”‚                    (cost, vendor, specs)            â”‚
    â”‚                          â”‚                          â”‚
    â”‚                          â”‚ Submits for â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¶
    â”‚                          â”‚ Approval                 â”‚
    â”‚                          â”‚                          â”‚
    â”‚                          â”‚                    Reviews & Approves
    â”‚                          â”‚                          â”‚
    â”‚ Notified â—€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚â—€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”‚
    â”‚ "Product Available"      â”‚                          â”‚
```

### 7.2 Purchase Manager (P07)

**Additional Capabilities:**
- âœ… CAN confirm Purchase Orders
- âœ… CAN approve product requests
- âœ… CAN negotiate vendor contracts
- âœ… CAN manage reordering rules

**Restrictions (SoD):**
- âŒ CANNOT validate vendor bills (Accounting does this)
- âŒ CANNOT register payments
- âŒ CANNOT receive goods (Warehouse does this)

---

## 8. INVENTORY DEPARTMENT EXPERIENCE

### 8.1 Warehouse Operator (P12)

**What They See:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ DELIVERY ORDER: WH/OUT/00045                                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Source: Downtown Store / Stock                                   â”‚
â”‚ Destination: Customer Location                                   â”‚
â”‚                                                                  â”‚
â”‚ Products to Deliver:                                             â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚
â”‚ â”‚ Product    | Demand | Reserved | Done | Location             â”‚â”‚
â”‚ â”‚ Widget A   | 10     | 10       | 0    | Shelf A-01           â”‚â”‚
â”‚ â”‚                                                               â”‚â”‚
â”‚ â”‚ âš ï¸ NO PRICE COLUMNS - Warehouse sees quantities only          â”‚â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜â”‚
â”‚                                                                  â”‚
â”‚ [Validate]                                                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Restrictions Enforced:**
- âŒ CANNOT see product costs
- âŒ CANNOT see sales/purchase prices
- âŒ CANNOT adjust inventory quantities (requires manager)
- âŒ CANNOT scrap inventory (requires manager)
- âŒ CANNOT create/modify orders

### 8.2 Inventory Manager (P08)

**Additional Capabilities:**
- âœ… CAN approve inventory adjustments
- âœ… CAN approve scrap orders
- âœ… CAN see stock valuation
- âœ… CAN configure warehouse locations

**Control: Inventory Adjustment Workflow**

```
Adjustment > $Y value requires:
1. Warehouse Operator creates adjustment
2. Inventory Manager approves
3. Accountant verifies (if > $Z value)
4. External auditor reviews (monthly)
```

---

## 9. ACCOUNTING DEPARTMENT EXPERIENCE

### 9.1 AR Clerk (P13)

**Capabilities:**
- âœ… Create draft customer invoices
- âœ… Send invoices to customers
- âœ… Record customer payment receipts (draft)
- âœ… Record customer PDC checks
- âœ… Set customer credit limits
- âœ… Block customers (with approval)

**Restrictions:**
- âŒ CANNOT validate/post invoices
- âŒ CANNOT create credit notes independently
- âŒ CANNOT access AP functions
- âŒ CANNOT perform bank reconciliation

### 9.2 AP Clerk (P14)

**Capabilities:**
- âœ… Create draft vendor bills
- âœ… Verify three-way match (PO â†’ Receipt â†’ Bill)
- âœ… Prepare payment batches
- âœ… Record vendor PDC checks

**Restrictions:**
- âŒ CANNOT validate/post vendor bills
- âŒ CANNOT execute payments
- âŒ CANNOT access AR functions
- âŒ CANNOT modify payment terms

### 9.3 Treasury Officer (P15)

**Capabilities:**
- âœ… Execute approved payments
- âœ… Process customer refunds (after authorization)
- âœ… Manage bank transfers
- âœ… Physical check printing

**Restrictions:**
- âŒ CANNOT create or validate bills/invoices
- âŒ CANNOT perform bank reconciliation
- âŒ CANNOT create orders

**Control: Dual Authorization**
```
Payments > $Z require:
1. AP Clerk creates payment batch
2. Accountant approves batch
3. CFO authorizes (if > $Z)
4. Treasury Officer executes
```

### 9.4 Accountant/Controller (P16)

**Capabilities:**
- âœ… Validate and post invoices/bills
- âœ… Perform bank reconciliation
- âœ… Create manual journal entries
- âœ… Generate financial reports
- âœ… Configure pricing and pricelists

**Restrictions:**
- âŒ CANNOT execute payments
- âŒ CANNOT confirm Sales/Purchase Orders
- âŒ CANNOT receive goods
- âŒ CANNOT modify user access

---

## 10. ADMINISTRATION & SUPPORT EXPERIENCE

### 10.1 IT Administrator (P01) - THE BLIND ADMIN

**This is the key differentiator in OPS Framework.**

**What IT Admin SEES:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ IT ADMINISTRATOR DASHBOARD                                       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                  â”‚
â”‚ â”Œâ”€ System Health â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€ User Activity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ Active Users: 45         â”‚  â”‚ Logins Today: 127             â”‚ â”‚
â”‚ â”‚ API Calls (24h): 2,340   â”‚  â”‚ Failed Logins: 3              â”‚ â”‚
â”‚ â”‚ System Load: Normal      â”‚  â”‚ New Users (7d): 5             â”‚ â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚                                                                  â”‚
â”‚ â”Œâ”€ Configuration Quick Links â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ [Users & Groups]  [Personas]  [Branches]  [Governance Rules]â”‚ â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚                                                                  â”‚
â”‚ â”Œâ”€ Audit Log Summary (Metadata Only) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ User          | Action      | Model        | Count (24h)    â”‚ â”‚
â”‚ â”‚ john.doe      | create      | sale.order   | 15             â”‚ â”‚
â”‚ â”‚ jane.smith    | write       | purchase.order| 8             â”‚ â”‚
â”‚ â”‚ âš ï¸ CANNOT see: amounts, customer names, invoice details      â”‚ â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚                                                                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**What IT Admin CANNOT Access:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ âŒ ACCESS DENIED                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                  â”‚
â”‚ You do not have permission to access:                            â”‚
â”‚                                                                  â”‚
â”‚ â€¢ Sales Orders                                                   â”‚
â”‚ â€¢ Purchase Orders                                                â”‚
â”‚ â€¢ Customer/Vendor Invoices                                       â”‚
â”‚ â€¢ Payments                                                       â”‚
â”‚ â€¢ Bank Statements                                                â”‚
â”‚ â€¢ Financial Reports                                              â”‚
â”‚ â€¢ Stock Valuations                                               â”‚
â”‚                                                                  â”‚
â”‚ Contact your supervisor if you need business data access.        â”‚
â”‚                                                                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 10.2 System Administrator (P00) - BREAK-GLASS

**Usage Protocol:**
1. Only used in emergencies (system failure, key personnel absence)
2. Every use logged and reviewed by Board within 48 hours
3. Temporary access via IT Admin with auto-expiry (24 hours)
4. 2FA mandatory
5. Should NOT be used for daily operations

### 10.3 HR/Payroll Specialist (P17)

**Capabilities:**
- âœ… Manage employee master data
- âœ… Process payroll
- âœ… Track attendance and leave
- âœ… Manage expense claims

**Restrictions:**
- âŒ CANNOT access sales, purchase, accounting
- âŒ CANNOT see financial reports
- âŒ CANNOT modify user access

---

## 11. FEATURE MATRIX BY PERSONA

### 11.1 Module Access

| Module | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:------:|
| Sales | âœ… | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ‘ï¸ | âŒ |
| CRM | âœ… | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ |
| Purchase | âŒ | âœ… | âŒ | âŒ | âŒ | âŒ | ðŸ‘ï¸ | âŒ |
| Inventory | ðŸ‘ï¸ | ðŸ‘ï¸ | âœ… | âŒ | âŒ | âŒ | ðŸ‘ï¸ | âŒ |
| Accounting | âŒ | âŒ | âŒ | âœ… | âœ… | âœ… | âœ… | âŒ |
| Settings | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |
| OPS Matrix | âœ… | âœ… | âœ… | âœ… | âœ… | âœ… | âœ… | âœ… |

Legend: âœ… Full Access | ðŸ‘ï¸ Read Only | âŒ No Access

### 11.2 Data Visibility

| Data Type | P10 | P11 | P12 | P13 | P14 | P15 | P16 | P06 Mgr | P01 IT |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:-------:|:------:|
| Sales Prices | âœ… | âŒ | âŒ | âœ… | âŒ | âŒ | âœ… | âœ… | âŒ |
| Cost Prices | âŒ | âœ… | âŒ | âŒ | âœ… | âŒ | âœ… | âœ… | âŒ |
| Margins | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âœ… | âŒ |
| Stock Qty | âœ… | âœ… | âœ… | âŒ | âŒ | âŒ | âœ… | âœ… | âŒ |
| Stock Value | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âœ… | âŒ |
| Bank Balance | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âœ… | âŒ | âŒ |
| Audit Logs | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ‘ï¸* |

*IT Admin sees metadata only (user, action, model) - not transaction details

### 11.3 Action Capabilities

| Action | P10 | P11 | P12 | P13 | P14 | P15 | P16 | Mgr | IT |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:--:|
| Create SO | âœ… | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ |
| Confirm SO | âŒ* | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ |
| Create PO | âŒ | âœ… | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ |
| Confirm PO | âŒ | âŒ* | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ |
| Receive Goods | âŒ | âŒ | âœ… | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ |
| Create Invoice | âŒ | âŒ | âŒ | âœ… | âŒ | âŒ | âœ… | âŒ | âŒ |
| Post Invoice | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ | âŒ |
| Execute Payment | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ | âŒ | âŒ |
| Bank Reconcile | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ | âŒ |
| Adjust Inventory | âŒ | âŒ | âŒ* | âŒ | âŒ | âŒ | âŒ | âœ… | âŒ |
| Create Users | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |
| Assign Personas | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |

*Can initiate but requires manager approval above threshold

---

## 12. REPORTS & DASHBOARDS BY PERSONA

### 13.1 Report Access Matrix

**Legend:** âœ… Full Access | ðŸ”¶ Branch Only | ðŸ”· BU Only | âŒ No Access | ðŸ’° Requires Cost Grant

#### Financial Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **Profit & Loss** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Balance Sheet** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Cash Flow** | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Trial Balance** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ |
| **General Ledger** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ |
| **Journal Entries** | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | âŒ | âŒ | âŒ |

#### Accounts Receivable Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **AR Aging** | âŒ | âŒ | âŒ | ðŸ”¶ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Customer Statement** | ðŸ”¶ | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Invoice Register** | âŒ | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **PDC Receivable** | âŒ | âŒ | âŒ | ðŸ”¶ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Collection Report** | ðŸ”¶ | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |

#### Accounts Payable Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **AP Aging** | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Vendor Statement** | âŒ | ðŸ”¶ | âŒ | âŒ | ðŸ”¶ | âŒ | ðŸ”¶ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Bills Register** | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | âŒ | ðŸ”¶ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **PDC Payable** | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Payment Schedule** | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |

#### Sales Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **Sales by Customer** | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Sales by Product** | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Sales by Salesperson** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Margin Analysis** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ðŸ’° | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Quotation Analysis** | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Commission Report** | Own | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |

#### Purchase Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **Purchase by Vendor** | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Purchase by Product** | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Vendor Performance** | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Price Comparison** | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **RFQ Analysis** | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |

#### Inventory Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **Stock on Hand** | ðŸ”¶ Qty | ðŸ”¶ Qty | ðŸ”¶ Qty | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Stock Valuation** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ðŸ’° | ðŸ”¶ðŸ’° | ðŸ”·ðŸ’° | âŒ |
| **Stock Movements** | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Reorder Report** | âŒ | ðŸ”¶ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Dead Stock** | âŒ | ðŸ”¶ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |
| **Inter-Branch Transfers** | âŒ | âŒ | ðŸ”¶ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”· | âŒ |

#### Asset Reports

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **Asset Register** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Depreciation Schedule** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Asset by Location** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |
| **Asset Disposal** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | ðŸ”¶ | ðŸ”¶ | ðŸ”· | âŒ |

#### System & Audit Reports (IT Admin)

| Report | P10 Sales | P11 Purch | P12 Stock | P13 AR | P14 AP | P15 Treas | P16 Acct | P05 BrMgr | P04 BU | P01 IT |
|--------|:---------:|:---------:|:---------:|:------:|:------:|:---------:|:--------:|:---------:|:------:|:------:|
| **User Activity Log** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ…* |
| **Login History** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |
| **Permission Changes** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |
| **API Usage** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |
| **Export Log** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |
| **Failed Actions** | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âŒ | âœ… |

*IT Admin sees metadata only (user, action, model, timestamp) - NOT transaction amounts or details

---

### 13.2 Dashboard Access by Persona

| Dashboard | Description | Personas with Access |
|-----------|-------------|---------------------|
| **Executive Dashboard** | Company-wide KPIs, all BUs | P02 Executive, P03 CFO |
| **BU Performance** | All branches in BU, aggregated | P04 BU Leader |
| **Branch Performance** | Single branch KPIs | P05 Branch Manager, P06-P09 Dept Managers |
| **Sales Dashboard** | Pipeline, conversions, targets | P10 Sales Rep (own), P06 Sales Mgr (team) |
| **Purchase Dashboard** | PO status, vendor metrics | P11 Purchase Officer (own), P07 Purchase Mgr |
| **Warehouse Dashboard** | Receipts, deliveries, transfers | P12 Warehouse Op, P08 Inventory Mgr |
| **AR Dashboard** | Outstanding invoices, collections | P13 AR Clerk, P16 Accountant |
| **AP Dashboard** | Bills due, payment schedule | P14 AP Clerk, P15 Treasury, P16 Accountant |
| **Cash Position** | Bank balances, cash flow | P15 Treasury, P16 Accountant, P03 CFO |
| **IT Dashboard** | System health, user stats | P01 IT Admin (NO business data) |
| **Approval Dashboard** | Pending approvals | All users (filtered to their queue) |

---

### 13.3 Report Content Rules

#### Branch Manager (P05) Report Experience

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ BRANCH MANAGER: Downtown Store                                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                  â”‚
â”‚ Reports Available:                                               â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ FINANCIAL (if Cost Grant given)                             â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ P&L Statement (Branch only)                             â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Balance Sheet (Branch only)                             â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Cash Flow (Branch only)                                 â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ ACCOUNTS RECEIVABLE                                         â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ AR Aging (Branch customers)                             â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Customer Statements                                     â”‚ â”‚
â”‚ â”‚ â””â”€â”€ PDC Status                                              â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ ACCOUNTS PAYABLE (if Cost Grant given)                      â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ AP Aging (Branch vendors)                               â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Payment Schedule                                        â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ SALES                                                       â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Sales by Customer                                       â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Sales by Product                                        â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Sales by Salesperson                                    â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Margin Analysis (if Cost Grant)                         â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ INVENTORY                                                   â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Stock on Hand                                           â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Stock Valuation (if Cost Grant)                         â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Inter-Branch Transfers                                  â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ ASSETS                                                      â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Asset Register                                          â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Depreciation Schedule                                   â”‚ â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚                                                                  â”‚
â”‚ âš ï¸ All reports filtered to Downtown Store only                   â”‚
â”‚ âš ï¸ Cannot see other branches' data                               â”‚
â”‚ âš ï¸ Cost/Margin reports require explicit grant                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

#### IT Admin (P01) Report Experience

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ IT ADMINISTRATOR                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                  â”‚
â”‚ Reports Available:                                               â”‚
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚ â”‚ SYSTEM MONITORING                                           â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ User Activity Log (metadata only)                       â”‚ â”‚
â”‚ â”‚ â”‚   â””â”€â”€ Shows: User, Action, Model, Timestamp               â”‚ â”‚
â”‚ â”‚ â”‚   â””â”€â”€ HIDDEN: Amounts, Customer/Vendor names, Details     â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Login History                                           â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Failed Login Attempts                                   â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Session Report                                          â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ SECURITY & COMPLIANCE                                       â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Permission Change Log                                   â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Export Activity Log                                     â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ API Usage Statistics                                    â”‚ â”‚
â”‚ â”‚ â””â”€â”€ SoD Violation Attempts                                  â”‚ â”‚
â”‚ â”‚                                                             â”‚ â”‚
â”‚ â”‚ SYSTEM HEALTH                                               â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Scheduled Actions Status                                â”‚ â”‚
â”‚ â”‚ â”œâ”€â”€ Email Queue Status                                      â”‚ â”‚
â”‚ â”‚ â””â”€â”€ Database Size & Growth                                  â”‚ â”‚
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚                                                                  â”‚
â”‚ âŒ NO ACCESS TO:                                                 â”‚
â”‚ â”œâ”€â”€ P&L, Balance Sheet, Cash Flow                               â”‚
â”‚ â”œâ”€â”€ AR/AP Reports                                               â”‚
â”‚ â”œâ”€â”€ Sales/Purchase Reports                                      â”‚
â”‚ â”œâ”€â”€ Stock Valuation                                             â”‚
â”‚ â””â”€â”€ Any report with financial amounts                           â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 13. GOVERNANCE & APPROVAL WORKFLOWS

### 13.1 Threshold-Based Approvals

| Transaction Type | Threshold | Approver Required |
|------------------|-----------|-------------------|
| Sales Order | > $5,000 | Sales Manager |
| Sales Discount | > 10% | Sales Manager |
| Purchase Order | > $2,500 | Purchase Manager |
| Purchase Order | > $10,000 | Purchase Manager + CFO |
| Inventory Adjustment | > $1,000 | Inventory Manager |
| Inventory Adjustment | > $5,000 | Inventory Manager + Accountant |
| Payment | > $5,000 | Accountant |
| Payment | > $25,000 | Accountant + CFO |

### 13.2 Automated Locks

```
SYSTEM-ENFORCED LOCKS:
â”œâ”€â”€ Confirmed Sales Orders â†’ Cannot be edited by Sales Rep
â”œâ”€â”€ Confirmed Purchase Orders â†’ Cannot be edited by Purchase Officer
â”œâ”€â”€ Posted Invoices â†’ Cannot be deleted (only credit note reversal)
â”œâ”€â”€ Validated Payments â†’ Require cancellation workflow
â”œâ”€â”€ Approved Adjustments â†’ Locked from further changes
â””â”€â”€ Pending Approval â†’ Document locked until approved/rejected
```

### 13.3 SLA Monitoring

| Process | Target Time | Warning | Breach Action |
|---------|-------------|---------|---------------|
| Quote Response | 24 hours | 20 hours | Notify Sales Manager |
| PO Approval | 48 hours | 40 hours | Notify Purchase Manager |
| Invoice Validation | 24 hours | 20 hours | Notify Finance Manager |
| Payment Approval | 72 hours | 60 hours | Notify CFO |

---

## 14. SECURITY GROUPS MAPPING

### 13.1 OPS Security Groups (To Be Created)

```xml
<!-- OPS Security Groups Hierarchy -->

<!-- Base User Groups -->
group_ops_user          â†’ Basic OPS access
group_ops_manager       â†’ Branch/BU management
group_ops_admin         â†’ OPS configuration

<!-- Department-Specific Groups -->
group_ops_sales_user    â†’ Sales Rep capabilities
group_ops_sales_manager â†’ Sales Manager + cost visibility
group_ops_purchase_user â†’ Purchase Officer capabilities
group_ops_purchase_manager â†’ Purchase Manager + approvals
group_ops_inventory_user â†’ Warehouse Operator capabilities
group_ops_inventory_manager â†’ Inventory Manager + adjustments
group_ops_ar_clerk      â†’ AR Clerk capabilities
group_ops_ap_clerk      â†’ AP Clerk capabilities
group_ops_treasury      â†’ Treasury Officer capabilities
group_ops_accountant    â†’ Accountant/Controller capabilities

<!-- Special Groups -->
group_ops_it_admin      â†’ IT Admin (blind to business data)
group_ops_executive     â†’ Executive read-only
group_ops_cfo           â†’ CFO full access
group_ops_bu_leader     â†’ BU Leader cross-branch
group_ops_product_approver â†’ Can approve product requests

<!-- Hidden Data Groups -->
group_ops_see_cost      â†’ Can see cost prices
group_ops_see_margin    â†’ Can see margins
group_ops_see_valuation â†’ Can see stock valuation
```

### 13.2 Persona to Group Mapping

| Persona | OPS Groups | Implied Odoo Groups |
|---------|------------|---------------------|
| P01 IT Admin | group_ops_it_admin | base.group_erp_manager |
| P10 Sales Rep | group_ops_user, group_ops_sales_user | sales_team.group_sale_salesman |
| P06 Sales Manager | group_ops_manager, group_ops_sales_manager, group_ops_see_cost, group_ops_see_margin | sales_team.group_sale_manager |
| P11 Purchase Officer | group_ops_user, group_ops_purchase_user | purchase.group_purchase_user |
| P07 Purchase Manager | group_ops_manager, group_ops_purchase_manager | purchase.group_purchase_manager |
| P12 Warehouse Operator | group_ops_user, group_ops_inventory_user | stock.group_stock_user |
| P08 Inventory Manager | group_ops_manager, group_ops_inventory_manager | stock.group_stock_manager |
| P13 AR Clerk | group_ops_user, group_ops_ar_clerk | account.group_account_invoice |
| P14 AP Clerk | group_ops_user, group_ops_ap_clerk | account.group_account_invoice |
| P15 Treasury | group_ops_user, group_ops_treasury | account.group_account_invoice |
| P16 Accountant | group_ops_manager, group_ops_accountant, group_ops_see_cost, group_ops_see_margin, group_ops_see_valuation | account.group_account_manager |

---

## 15. NEW MENUS & NAVIGATION

### 14.1 OPS Matrix App Menu Structure

```
OPS Matrix (Top-Level App)
â”œâ”€â”€ Dashboards
â”‚   â”œâ”€â”€ Executive Dashboard        â†’ P02, P03 only
â”‚   â”œâ”€â”€ Branch Performance         â†’ P05, P06, P07, P08, P09
â”‚   â”œâ”€â”€ BU Performance             â†’ P04
â”‚   â”œâ”€â”€ Sales Performance          â†’ P10, P06
â”‚   â”œâ”€â”€ Security Dashboard         â†’ P01 (IT Admin)
â”‚   â””â”€â”€ Approval Dashboard         â†’ All (filtered by role)
â”‚
â”œâ”€â”€ Governance
â”‚   â”œâ”€â”€ My Approvals               â†’ All users
â”‚   â”œâ”€â”€ Pending Requests           â†’ Managers
â”‚   â”œâ”€â”€ Rules Configuration        â†’ P01, P03
â”‚   â”œâ”€â”€ SLA Monitoring             â†’ Managers
â”‚   â””â”€â”€ Violations Report          â†’ P01, P03
â”‚
â”œâ”€â”€ Configuration (IT Admin + CFO only)
â”‚   â”œâ”€â”€ Companies
â”‚   â”œâ”€â”€ Business Units
â”‚   â”œâ”€â”€ Branches
â”‚   â”œâ”€â”€ Personas
â”‚   â”œâ”€â”€ Security Groups
â”‚   â””â”€â”€ Audit Settings
â”‚
â””â”€â”€ API Integration (IT Admin only)
    â”œâ”€â”€ API Keys
    â”œâ”€â”€ API Audit Logs
    â””â”€â”€ Usage Analytics
```

### 14.2 Module-Specific Additions

**Sales App (P10, P06):**
```
Sales
â”œâ”€â”€ ... (standard menus)
â””â”€â”€ OPS Analytics
    â””â”€â”€ Sales Analytics (branch-filtered)
```

**Purchase App (P11, P07):**
```
Purchase
â”œâ”€â”€ ... (standard menus)
â”œâ”€â”€ Product Requests    â†’ NEW
â””â”€â”€ OPS Analytics
    â””â”€â”€ Procurement Analytics (branch-filtered)
```

**Inventory App (P12, P08):**
```
Inventory
â”œâ”€â”€ ... (standard menus)
â”œâ”€â”€ Inter-Branch Transfers    â†’ NEW
â””â”€â”€ OPS Analytics
    â””â”€â”€ Inventory Analytics (branch-filtered)
```

**Accounting App (P13-P16):**
```
Accounting
â”œâ”€â”€ ... (standard menus)
â”œâ”€â”€ OPS Matrix
â”‚   â”œâ”€â”€ Asset Management
â”‚   â”œâ”€â”€ PDC Management
â”‚   â””â”€â”€ Budget Tracking
â””â”€â”€ OPS Analytics
    â””â”€â”€ Financial Analytics (branch-filtered)
```

---

## 16. DATA EXPORT SECURITY

### 16.1 Export Philosophy

**Core Principle:** Data export is a security-critical operation. By default, exports are restricted to prevent data leakage.

### 16.2 Export Rules

| Rule | Description |
|------|-------------|
| **Document Scope** | Export limited to currently viewed document/list only |
| **No Bulk Export** | Cannot export entire database tables |
| **Field Filtering** | Critical fields excluded from all exports |
| **Audit Logging** | Every export attempt logged with user, time, content |
| **Manager Approval** | High-value exports may require approval (configurable) |

### 16.3 Fields Excluded from Export

```
ALWAYS EXCLUDED FROM EXPORT:
â”œâ”€â”€ Cost prices (unless user has Cost Grant)
â”œâ”€â”€ Margin data (unless user has Cost Grant)  
â”œâ”€â”€ Bank account numbers
â”œâ”€â”€ Credit card information
â”œâ”€â”€ Password fields
â”œâ”€â”€ API keys and tokens
â”œâ”€â”€ Internal notes marked confidential
â””â”€â”€ Audit log details (IT Admin sees metadata only)
```

### 16.4 Export by Persona

| Persona | Can Export | Restrictions |
|---------|------------|--------------|
| P10 Sales Rep | Own quotes/orders | No cost, no other reps' data |
| P11 Purchase Officer | Own POs/RFQs | No sales data |
| P12 Warehouse | Picking lists, stock reports | No valuations |
| P13 AR Clerk | Customer invoices, statements | Own branch only |
| P14 AP Clerk | Vendor bills | Own branch only |
| P15 Treasury | Payment reports | No vendor costs |
| P16 Accountant | Financial reports | Branch only, with cost grant |
| P05 Branch Mgr | Branch reports | With cost grant if needed |
| P04 BU Leader | BU reports | Aggregated, with cost grant |
| P01 IT Admin | System logs only | NO business data export |

### 16.5 Export Audit Log

Every export creates a log entry:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ EXPORT AUDIT LOG                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Timestamp:    2026-01-02 14:35:22                                â”‚
â”‚ User:         john.doe (P10 - Sales Rep)                         â”‚
â”‚ Branch:       Downtown Store                                     â”‚
â”‚ Action:       Excel Export                                       â”‚
â”‚ Model:        sale.order                                         â”‚
â”‚ Records:      5 (SO00123, SO00124, SO00125, SO00126, SO00127)   â”‚
â”‚ Fields:       name, date, customer, total (cost EXCLUDED)        â”‚
â”‚ IP Address:   192.168.1.45                                       â”‚
â”‚ Status:       Completed                                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 17. IMPLEMENTATION CHECKLIST

### 17.1 Phase 1: Security Groups (Week 1)

- [ ] Create all OPS security groups in res_groups.xml
- [ ] Define group hierarchy and implications
- [ ] Create "hidden data" groups (see_cost, see_margin, see_valuation)
- [ ] Create IT Admin group with business data exclusion

### 17.2 Phase 2: Record Rules (Week 2)

- [ ] Branch-level isolation rules for all models
- [ ] BU-level aggregation rules for managers
- [ ] Cost/Margin field hiding via groups
- [ ] IT Admin exclusion from business models

### 17.3 Phase 3: Persona Templates (Week 2)

- [ ] Create all 18 persona templates
- [ ] Map personas to security groups
- [ ] Create persona assignment UI

### 17.4 Phase 4: Governance Engine (Week 3)

- [ ] Threshold-based approval workflows
- [ ] SLA monitoring and breach detection
- [ ] Automated document locking
- [ ] Audit logging for all actions

### 17.5 Phase 5: UI/UX (Week 4)

- [ ] Role-specific dashboards
- [ ] Field visibility by group
- [ ] Menu filtering by persona
- [ ] Warning messages for restrictions

### 17.6 Testing Checklist by Persona

**P01 IT Admin Testing:**
- [ ] Can create users
- [ ] Can assign personas
- [ ] CANNOT view sales orders
- [ ] CANNOT view invoices
- [ ] CANNOT view bank statements
- [ ] CAN view audit log metadata
- [ ] CANNOT view audit log transaction details

**P10 Sales Rep Testing:**
- [ ] Can create sales orders
- [ ] CANNOT see cost column
- [ ] CANNOT see margin column
- [ ] CANNOT confirm orders > threshold
- [ ] CANNOT view other branches' orders
- [ ] CAN request product additions

**P16 Accountant Testing:**
- [ ] Can validate invoices
- [ ] Can perform bank reconciliation
- [ ] CANNOT execute payments
- [ ] CAN see all cost/margin data
- [ ] CANNOT confirm sales/purchase orders

---

## DOCUMENT HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-02 | Initial User Experience Document |
| 1.1 | 2026-01-02 | Added full SoD framework, 18 personas, IT Admin blindness concept |
| 1.2 | 2026-01-02 | Added Reports & Dashboards by Persona, Data Export Security |

---

## APPENDIX A: Quick Reference - "Who Can Do What"

| Action | Role | Cannot Be Done By |
|--------|------|-------------------|
| Create Sales Order | Sales Rep | Purchase, Warehouse, Accounting, IT |
| Confirm Sales Order | Sales Manager | Sales Rep (if > threshold), IT |
| Create Purchase Order | Purchase Officer | Sales, Warehouse, Accounting, IT |
| Confirm Purchase Order | Purchase Manager | Purchase Officer (if > threshold), IT |
| Receive Goods | Warehouse | Purchase, Sales, Accounting, IT |
| Create Invoice | AR/AP Clerk | Sales, Purchase, Warehouse, IT |
| Validate Invoice | Accountant | AR/AP Clerk, Sales, Purchase, IT |
| Execute Payment | Treasury Officer | Accountant, AP Clerk, IT |
| Bank Reconciliation | Accountant | Treasury Officer, AP Clerk, IT |
| Adjust Inventory | Inventory Manager | Warehouse (if > threshold), IT |
| Create Users | IT Admin | All other roles |
| View Business Data | Business Users | IT Admin |

---

**END OF USER EXPERIENCE DOCUMENT v1.1**
