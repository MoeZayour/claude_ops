# OPS Framework v1.5.0 - Quick Reference Card

## Test Credentials

All test users have password: `test123`

| User | Login | Persona | Branch | Purpose |
|------|-------|---------|--------|---------|
| IT Admin | it.admin | P13 | NONE | Test zero business data access |
| Sales Dubai | sales.dxb | P10 | Dubai HQ | Test Dubai-only visibility |
| Sales AUH | sales.auh | P10 | Abu Dhabi | Test AUH-only visibility |

## Quick UAT Tests

### Test 1: IT Administrator Blindness
1. Login as: it.admin / test123
2. Navigate to: Sales > Orders
3. Expected: No records visible or access denied
4. Navigate to: Invoicing > Invoices  
5. Expected: No records visible or access denied
6. Navigate to: Settings
7. Expected: Full access to system configuration

### Test 2: Branch Isolation
1. Login as: sales.dxb / test123
2. Create a sales order for Dubai branch
3. Logout
4. Login as: sales.auh / test123
5. Navigate to: Sales > Orders
6. Expected: Dubai order is NOT visible

## Organizational Structure

### Branches
- DXB-HQ: HQ - Dubai
- AUH-BR: Branch - Abu Dhabi
- SHJ-BR: Branch - Sharjah

### Business Units
- BU-SALES: Sales Division
- BU-OPS: Operations Division
- BU-FIN: Finance Division

### Personas (18 total)
P01-ADMIN, P02-CEO, P03-CFO, P04-BU_LEADER, P05-BRANCH_MANAGER, P06-SALES_MANAGER, 
P07-PURCHASE_MANAGER, P08-INVENTORY_MANAGER, P09-ACCOUNTANT, P10-SALES_PERSON,
P11-PURCHASE_OFFICER, P12-WAREHOUSE_STAFF, **P13-IT_ADMIN**, P14-COST_CONTROLLER, 
P15-TREASURY, P16-BRANCH_ACCOUNTANT, P17-APPROVER_L1, P18-APPROVER_L2

## Reports Location

- Main Report: /opt/gemini_odoo19/DATA_SEEDING_REPORT.md
- Quick Reference: /opt/gemini_odoo19/QUICK_REFERENCE.md

**Status**: Ready for UAT and CEO Review
