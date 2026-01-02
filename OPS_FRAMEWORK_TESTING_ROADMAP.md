# OPS FRAMEWORK TESTING ROADMAP
**PHASE 5: HUMAN HANDOVER - MANUAL TESTING & VALIDATION**

**Generated:** 2025-12-28  
**Database:** mz-db  
**Container:** gemini_odoo19  
**Port:** 8089  
**Target User:** Mohamad (Manual Testing & Production Validation)

---

## 📋 EXECUTIVE SUMMARY

### What Was Audited

This testing roadmap consolidates all discovery and testing performed across Phases 1-4:

| Phase | Scope | Results |
|-------|-------|---------|
| **Phase 1** | Feature Discovery | 50+ models, 15+ API endpoints, 413-line governance mixin |
| **Phase 2/2B** | Infrastructure Seeding | 10 branches, 10 BUs, 4 users, 5 products created |
| **Phase 3A** | Procurement Workflow | PO P00002 ($24,000) created, governance tested |
| **Phase 3B** | Sales Workflow | SO S00001 ($7,740) created, Cost Shield issue found |
| **Phase 3C** | API Security | 15+ endpoints validated, security gaps identified |
| **Phase 3D** | Reporting System | Database schema error discovered (blocker) |
| **Phase 4** | Safety Verification | 21 issues consolidated, 61.2% production ready |

### Current Production Readiness

**Overall Score:** 🟡 **61.2%** (NOT PRODUCTION READY)  
**Target Score:** 95%  
**Gap to Close:** 33.8 percentage points

### Critical Issues Summary

| ID | Issue | Impact | Status |
|----|-------|--------|--------|
| **ISS-001** | Database schema error (JSONB type) | 🔴 Blocks all reporting | CRITICAL |
| **ISS-002** | Cost Shield not implemented | 🔴 Sales can see margins | CRITICAL |
| **ISS-003** | Missing accounting journals | 🔴 Cannot create invoices | CRITICAL |

**All 3 must be resolved before production deployment**

### Test Data Created

| Resource | Count | Status | Location |
|----------|-------|--------|----------|
| **Branches** | 10 | ✅ Persistent | Database mz-db |
| **Business Units** | 10 | ✅ Persistent | Database mz-db |
| **Test Users** | 4 | ✅ Persistent | ops_sales_rep, ops_sales_mgr, ops_accountant, ops_treasury |
| **Test Products** | 5 | ✅ Persistent | WIDGET-A/B, SOLUTION-C, EQUIPMENT-D, SUPPLIES-E |
| **Sales Orders** | 1 | ✅ Persistent | S00001 ($7,740) |
| **Purchase Orders** | 1 | ✅ Persistent | P00002 ($24,000) |

### Timeline to Production

**Estimated Time:** 2 weeks (10 business days)

**Week 1:**
- Day 1-2: Fix critical issues (5.5 hours)
- Day 3-5: Production hardening (11.25 hours)

**Week 2:**
- Day 6-8: Complete testing & validation
- Day 9-10: Security audit & sign-off

### Quick Start Instructions

**For Immediate Testing:**

```bash
# 1. Access Odoo Web UI
Open: http://localhost:8089
Login: admin / admin

# 2. Test User Logins
ops_sales_rep / 123456
ops_sales_mgr / 123456
ops_accountant / 123456
ops_treasury / 123456

# 3. View Test Data
Navigate to: Sales → Orders → S00001
Navigate to: Purchase → Orders → P00002
```

---

## 🔐 SECTION 2: DATABASE ACCESS & TEST ENVIRONMENT

### Database Connection Details

**Database:** `mz-db`  
**Container:** `gemini_odoo19`  
**Port:** `8089`  
**Odoo Version:** 19.0 CE  
**Modules:** ops_matrix_core 19.0.1.2, ops_matrix_accounting 19.0.1.0.0, ops_matrix_reporting 19.0.1.0

### Access Methods

#### Web UI Access
```
URL: http://localhost:8089
Admin Login: admin
Admin Password: admin
```

#### Odoo Shell Access
```bash
# Standard Odoo shell
docker exec -it gemini_odoo19 odoo shell -d mz-db --stop-after-init

# With no HTTP server (for scripts)
docker exec -it gemini_odoo19 odoo shell -d mz-db --no-http
```

#### PostgreSQL Direct Access
```bash
# Connect to PostgreSQL
docker exec -it gemini_odoo19_db psql -U odoo -d mz-db

# Quick queries
docker exec -i gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT COUNT(*) FROM ops_branch;"
```

### Test User Credentials

All test users created in [Phase 2B](DeepSeek Dev Phases/PHASE_2B_USER_CREATION_COMPLETION_REPORT.md):

| Login | Password | Name | User ID | Persona | Branch | BU |
|-------|----------|------|---------|---------|--------|-----|
| **ops_sales_rep** | 123456 | OPS Sales Representative | 9 | Sales Rep | Branch-North | BU-Sales |
| **ops_sales_mgr** | 123456 | OPS Sales Manager | 10 | Sales Manager | Branch-North | BU-Sales |
| **ops_accountant** | 123456 | OPS Financial Controller | 11 | Financial Controller | Branch-HQ | BU-Finance |
| **ops_treasury** | 123456 | OPS Treasury Officer | 12 | Treasury Officer | Branch-HQ | BU-Finance |

**Security Note:** All passwords are test credentials. Change before production deployment.

---

## 📦 SECTION 3: TEST DATA INVENTORY

### 3.1 Branches (10 Created)

From [`PHASE_2_INFRASTRUCTURE_SEEDING_REPORT.md`](DeepSeek Dev Phases/PHASE_2_INFRASTRUCTURE_SEEDING_REPORT.md):

| Code | Name | Status | Analytic Account |
|------|------|--------|------------------|
| BRN | Branch-North | ✅ Active | Auto-generated |
| BRS | Branch-South | ✅ Active | Auto-generated |
| BRE | Branch-East | ✅ Active | Auto-generated |
| BRW | Branch-West | ✅ Active | Auto-generated |
| BRC | Branch-Central | ✅ Active | Auto-generated |
| BRH | Branch-HQ | ✅ Active | Auto-generated |
| BRA | Branch-Regional-A | ✅ Active | Auto-generated |
| BRB | Branch-Regional-B | ✅ Active | Auto-generated |
| BRI | Branch-International | ✅ Active | Auto-generated |
| BRD | Branch-Digital | ✅ Active | Auto-generated |

**Verification Command:**
```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --stop-after-init << 'EOF'
branches = env['ops.branch'].search([])
print(f'Total Branches: {len(branches)}')
for b in branches:
    print(f'  [{b.code}] {b.name} - Active: {b.active}')
EOF
```

**Expected Output:** 10 branches listed

---

### 3.2 Business Units (10 Created)

| Code | Name | Status | Branch Coverage |
|------|------|--------|-----------------|
| SAL | BU-Sales | ✅ Active | All 10 branches |
| PRC | BU-Procurement | ✅ Active | All 10 branches |
| FIN | BU-Finance | ✅ Active | All 10 branches |
| OPS | BU-Operations | ✅ Active | All 10 branches |
| HRD | BU-HR | ✅ Active | All 10 branches |
| ITD | BU-IT | ✅ Active | All 10 branches |
| MKT | BU-Marketing | ✅ Active | All 10 branches |
| LOG | BU-Logistics | ✅ Active | All 10 branches |
| RND | BU-R&D | ✅ Active | All 10 branches |
| CUS | BU-Customer-Service | ✅ Active | All 10 branches |

**Matrix Combinations:** 10 Branches × 10 BUs = 100 dimensional combinations

**Verification Command:**
```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --stop-after-init << 'EOF'
bus = env['ops.business.unit'].search([])
print(f'Total Business Units: {len(bus)}')
for bu in bus:
    print(f'  [{bu.code}] {bu.name} - Branches: {len(bu.branch_ids)}')
EOF
```

**Expected Output:** 10 business units, each with 10 branches assigned

---

### 3.3 Test Users & Personas

From [`PHASE_2B_USER_CREATION_COMPLETION_REPORT.md`](DeepSeek Dev Phases/PHASE_2B_USER_CREATION_COMPLETION_REPORT.md):

#### Persona Authority Matrix

| Persona | Code | Approval Limit | Authorities |
|---------|------|----------------|-------------|
| Sales Rep | SALES_REP | $0 | Basic sales (no special permissions) |
| Sales Manager | SALES_MGR | $50,000 | Approver, BU Leader |
| Financial Controller | FIN_CTRL | $100,000 | Cost access, Validate invoices, Post journals |
| Treasury Officer | TREASURY | $200,000 | Cost access, Execute payments, Manage PDC |

#### User-Persona Mapping

| User | Persona ID | Branch | BU | SoD Role |
|------|------------|--------|-----|----------|
| ops_sales_rep | 18 | Branch-North | BU-Sales | Order Creator |
| ops_sales_mgr | 19 | Branch-North | BU-Sales | Approver (up to $50K) |
| ops_accountant | 20 | Branch-HQ | BU-Finance | Invoice Validator |
| ops_treasury | 21 | Branch-HQ | BU-Finance | Payment Executor |

**Verification Command:**
```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --stop-after-init << 'EOF'
users = env['res.users'].search([('login', 'like', 'ops_%')])
print(f'Total Test Users: {len(users)}')
for u in users:
    persona = u.persona_id.name if u.persona_id else 'None'
    print(f'  {u.login}: {persona} | Branch: {u.primary_branch_id.name if u.primary_branch_id else "N/A"}')
EOF
```

**Expected Output:** 4 users with persona assignments

---

### 3.4 Test Products (5 Created)

From [`PHASE_2_INFRASTRUCTURE_SEEDING_REPORT.md`](DeepSeek Dev Phases/PHASE_2_INFRASTRUCTURE_SEEDING_REPORT.md):

| Product | Code | Type | Cost | Price | Margin | Category |
|---------|------|------|------|-------|--------|----------|
| Standard Widget A | WIDGET-A-001 | Consumable | $50.00 | $75.00 | $25.00 (33%) | Raw Materials |
| Premium Widget B | WIDGET-B-002 | Consumable | $250.00 | $399.00 | $149.00 (37%) | Finished Goods |
| Enterprise Solution C | SOLUTION-C-003 | Service | $5,000.00 | $8,500.00 | $3,500.00 (41%) | Services |
| Industrial Equipment D | EQUIPMENT-D-004 | Consumable | $12,000.00 | $18,000.00 | $6,000.00 (33%) | Equipment |
| Office Supplies Pack E | SUPPLIES-E-005 | Consumable | $15.00 | $25.00 | $10.00 (40%) | Consumables |

**Purpose:** Test Cost Shield functionality (sales reps should NOT see cost/margin columns)

**Verification Command:**
```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --stop-after-init << 'EOF'
products = env['product.template'].search([
    ('default_code', 'in', ['WIDGET-A-001', 'WIDGET-B-002', 'SOLUTION-C-003', 'EQUIPMENT-D-004', 'SUPPLIES-E-005'])
])
print(f'Total Test Products: {len(products)}')
for p in products:
    print(f'  [{p.default_code}] {p.name}')
    print(f'    Cost: ${p.standard_price:.2f} | Price: ${p.list_price:.2f}')
EOF
```

**Expected Output:** 5 products with cost and pricing data

---

### 3.5 Test Transactions

#### Sales Order S00001 (Phase 3B)

From [`PHASE_3B_SALES_STRESS_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3B_SALES_STRESS_TEST_REPORT.md):

- **Order Number:** S00001
- **Order ID:** 1
- **Customer:** ABC Corporation (ID: 15)
- **Amount Total:** $7,740.00
- **State:** sale (confirmed)
- **Branch:** My Company (res.company)
- **Business Unit:** BU-Sales
- **Created By:** Admin (OdooBot)

**Order Lines:**
1. Premium Widget B × 10 units = $3,990.00
2. Standard Widget A × 50 units = $3,750.00

**Verification Command:**
```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --stop-after-init << 'EOF'
so = env['sale.order'].browse(1)
print(f'SO: {so.name} | Customer: {so.partner_id.name}')
print(f'Amount: ${so.amount_total:,.2f} | State: {so.state}')
print('Order Lines:')
for line in so.order_line:
    print(f'  - {line.product_id.name}: {line.product_uom_qty} x ${line.price_unit:.2f} = ${line.price_subtotal:.2f}')
EOF
```

**Expected Output:** S00001 with 2 order lines, total $7,740.00

---

#### Purchase Order P00002 (Phase 3A)

From [`PHASE_3A_PROCUREMENT_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3A_PROCUREMENT_TEST_REPORT.md):

- **Order Number:** P00002
- **Order ID:** 2
- **Vendor:** Industrial Supplier Ltd (ID: 14)
- **Amount Total:** $24,000.00
- **State:** purchase (confirmed)
- **Branch:** My Company (res.company)
- **Business Unit:** BU-Procurement
- **Created By:** Admin (OdooBot)

**Order Lines:**
1. Industrial Equipment D × 2 units = $24,000.00

**Verification Command:**
```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --stop-after-init << 'EOF'
po = env['purchase.order'].browse(2)
print(f'PO: {po.name} | Vendor: {po.partner_id.name}')
print(f'Amount: ${po.amount_total:,.2f} | State: {po.state}')
print('Order Lines:')
for line in po.order_line:
    print(f'  - {line.product_id.name}: {line.product_qty} x ${line.price_unit:.2f} = ${line.price_subtotal:.2f}')
EOF
```

**Expected Output:** P00002 with 1 order line, total $24,000.00

---

## 🧪 SECTION 4: TESTING ROADMAP BY FEATURE

### 4.1 PROCUREMENT-TO-PAYMENT WORKFLOW

Reference: [`PHASE_3A_PROCUREMENT_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3A_PROCUREMENT_TEST_REPORT.md)

| User | Feature Tested | Document Number | Expected Visual Result | Status |
|------|----------------|-----------------|------------------------|--------|
| admin | View PO P00002 | P00002 | Should show $24,000, state=purchase, Branch=My Company, BU=BU-Procurement | ✅ Created |
| admin | Check governance bypass logs | P00002 | Chatter should show "Admin bypass" log entries | ✅ Verified |
| admin | Attempt to print PO | P00002 | PDF should generate (admin bypass allows) | ⚠️ Test manually |
| ops_accountant | View PO P00002 (cross-branch) | P00002 | Should be visible (finance can see all branches) | ⚠️ Test manually |
| ops_sales_rep | Try to view PO P00002 | P00002 | Should be filtered out (Branch isolation: Sales is Branch-North, PO is My Company) | ⚠️ Test manually |
| admin | Create vendor bill from PO | P00002 | ❌ **BLOCKED** - Missing purchase journal (ISS-003) | 🔴 Fix required |
| ops_treasury | Execute payment from bill | P00002 | ⚠️ Dependent on bill creation | ⚠️ Test after fix |

#### Manual Test Steps: View PO P00002

```gherkin
Given I am logged in as admin
When I navigate to Purchase → Orders → P00002
Then I should see:
  - Amount Total: $24,000.00
  - State: Purchase Order
  - Vendor: Industrial Supplier Ltd
  - Branch: My Company
  - Business Unit: BU-Procurement

When I check the Chatter (message log)
Then I should see governance bypass log entries:
  - "OPS Governance: Admin bypass for PO P00002"
  - "Security override: User admin used override on purchase.order 2"

When I click "Print" button
Then PDF should generate without errors (admin bypass allows)
```

#### Manual Test Steps: Branch Isolation

```gherkin
Given I am logged in as ops_sales_rep (Branch-North)
When I navigate to Purchase → Orders
Then I should NOT see PO P00002 in the list
  (Reason: PO is for My Company, sales rep is restricted to Branch-North)

Given I am logged in as ops_accountant (Finance role)
When I navigate to Purchase → Orders
Then I should see PO P00002 in the list
  (Reason: Finance roles can see all branches)
```

---

### 4.2 SALES-TO-INVOICING WORKFLOW

Reference: [`PHASE_3B_SALES_STRESS_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3B_SALES_STRESS_TEST_REPORT.md)

| User | Feature Tested | Document Number | Expected Visual Result | Status |
|------|----------------|-----------------|------------------------|--------|
| admin | View SO S00001 | S00001 | Should show $7,740, state=sale, 2 order lines | ✅ Created |
| ops_sales_rep | View SO S00001 | S00001 | Should see order but NOT cost/margin fields | 🔴 **ISS-002: Cost Shield missing** |
| ops_sales_mgr | View cost on SO line | S00001 | Should see cost/margin (manager authority) | 🔴 **ISS-002: Fields don't exist** |
| ops_accountant | View full profitability | S00001 | Should see cost, margin, margin % | 🔴 **ISS-002: Fields don't exist** |
| admin | Create invoice from SO | S00001 | ❌ **BLOCKED** - Missing sales journal (ISS-003) | 🔴 Fix required |
| ops_sales_rep | Try to post customer invoice | Invoice | Should be BLOCKED (SoD: only accountant can post) | ⚠️ Test after fix |
| ops_accountant | Post customer invoice | Invoice | Should succeed (has account.group_account_invoice) | ⚠️ Test after fix |

#### 🔴 CRITICAL TEST: Cost Shield Verification

**Purpose:** Verify that sales reps CANNOT see product costs

```gherkin
# TEST 1: Product Form View
Given I am logged in as ops_sales_rep
When I navigate to Inventory → Products → Premium Widget B (WIDGET-B-002)
Then I should see:
  ✅ Sales Price: $399.00
  ❌ Cost field (should be HIDDEN)
  ❌ Standard Price field (should be HIDDEN)

# TEST 2: Sales Order Line
Given I am logged in as ops_sales_rep
When I open Sales Order S00001
And I click on an order line
Then I should see:
  ✅ Unit Price: $399.00
  ✅ Quantity: 10
  ✅ Subtotal: $3,990.00
  ❌ Cost field (should NOT exist - ISS-002)
  ❌ Margin field (should NOT exist - ISS-002)
  ❌ Margin % field (should NOT exist - ISS-002)

# TEST 3: Manager View (After Cost Shield Implemented)
Given I am logged in as ops_sales_mgr
When I open Sales Order S00001
And I click on an order line for Premium Widget B
Then I should see:
  ✅ Unit Price: $399.00
  ✅ Cost: $250.00 (visible to manager)
  ✅ Margin: $149.00
  ✅ Margin %: 37.3%
```

**Current Status:** 🔴 **FAIL** - Cost/Margin fields do not exist on [`sale.order.line`](addons/ops_matrix_core/models/sale_order.py)

**Fix Required:** Install `sale_margin` module OR implement custom margin tracking (4 hours, ISS-002)

---

### 4.3 GOVERNANCE & APPROVAL TESTING

Reference: [`PHASE_3A_PROCUREMENT_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3A_PROCUREMENT_TEST_REPORT.md)

| User | Feature Tested | Document Number | Expected Visual Result | Status |
|------|----------------|-----------------|------------------------|--------|
| ops_sales_rep | Create PO > $10K | New PO | Should trigger approval requirement or admin bypass | ⚠️ No rules configured (CFG-003) |
| ops_sales_rep | Try to approve own PO | New PO | Should be blocked by SoD (self-approval prevention) | ⚠️ Test after rules configured |
| ops_sales_mgr | Approve PO $10K-$50K | New PO | Should succeed (within approval limit $50K) | ⚠️ Test after rules configured |
| ops_sales_mgr | Try to approve PO >$50K | P00002 ($24K) | Within limit, should succeed | ⚠️ Test after rules configured |
| ops_accountant | Try to approve PO >$50K | New PO >$50K | Should succeed (limit $100K) | ⚠️ Test after rules configured |
| admin | Override any approval | Any PO | Admin bypass should log and succeed | ✅ Verified (Phase 3A) |

#### Manual Test Steps: Approval Workflow (After Configuration)

**Prerequisites:** Configure governance rules (CFG-003)

```bash
# Create approval rule for high-value POs
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
rule = env['ops.governance.rule'].create({
    'name': 'PO Approval Required >$10K',
    'model_id': env['ir.model'].search([('model', '=', 'purchase.order')]).id,
    'action_type': 'require_approval',
    'trigger_type': 'on_write',
    'condition_code': 'result = record.amount_total > 10000 and record.state == "draft"',
    'error_message': 'Purchase orders over $10,000 require managerial approval.',
    'lock_on_approval_request': True,
    'active': True,
    'sequence': 10,
})
env.cr.commit()
print(f'Created rule: {rule.name} (ID: {rule.id})')
EOF
```

**Test Scenario:**

```gherkin
Given governance rule exists: "PO >$10K requires approval"
And I am logged in as ops_sales_rep

# Test 1: Trigger Approval
When I create Purchase Order P00003 for $15,000
And I click "Confirm Order"
Then I should see error message: "Purchase orders over $10,000 require managerial approval"
And an approval request should be created
And approver should be ops_sales_mgr (within $50K limit)

# Test 2: Self-Approval Prevention (SoD)
When I try to approve my own PO P00003
Then I should see error: "Self-approval prohibited (Segregation of Duties)"

# Test 3: Manager Approval
When ops_sales_mgr logs in
And approves PO P00003
Then PO state should change to "purchase"
And approval request state should be "approved"
And Chatter should log: "Approved by OPS Sales Manager"
```

---

### 4.4 BRANCH/BU ISOLATION TESTING

Reference: [`PHASE_3C_API_SECURITY_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3C_API_SECURITY_TEST_REPORT.md)

| User | Feature Tested | Verification | Expected Result | Status |
|------|----------------|--------------|------------------|--------|
| ops_sales_rep | View assigned branches | OPS → Configuration → Branches | Should only see Branch-North (1 branch) | ⚠️ Test manually |
| ops_sales_rep | View unassigned branches | Try to access Branch-South | Access denied or filtered out | ⚠️ Test manually |
| ops_accountant | View all branches | OPS → Configuration → Branches | Should see all 10 branches (finance role) | ⚠️ Test manually |
| ops_sales_rep | View assigned BUs | OPS → Configuration → Business Units | Should only see BU-Sales | ⚠️ Test manually |
| ops_accountant | View all BUs | OPS → Configuration → Business Units | Should see all 10 BUs | ⚠️ Test manually |
| ops_sales_rep | Create SO in assigned branch | New SO | Should default to Branch-North | ⚠️ Test manually |
| ops_sales_rep | Try SO in unassigned branch | New SO | Branch field should be restricted | ⚠️ Test manually |

#### Manual Test Steps: Branch Isolation

```gherkin
# Test 1: Sales Rep (Restricted Access)
Given I am logged in as ops_sales_rep
When I navigate to OPS → Configuration → Branches
Then I should see exactly 1 branch:
  ✅ Branch-North (BRN)
  ❌ Should NOT see: Branch-South, Branch-East, etc.

When I navigate to Sales → Orders → Create
Then the Branch field should default to: Branch-North
And I should NOT be able to select other branches

# Test 2: Accountant (Global Access)
Given I am logged in as ops_accountant
When I navigate to OPS → Configuration → Branches
Then I should see all 10 branches:
  ✅ Branch-North, Branch-South, Branch-East, Branch-West,
      Branch-Central, Branch-HQ, Branch-Regional-A, Branch-Regional-B,
      Branch-International, Branch-Digital

When I navigate to Sales → Orders
Then I should see sales orders from ALL branches

# Test 3: Cross-Branch Data Isolation
Given SO S00001 exists for My Company
And ops_sales_rep is assigned to Branch-North only

When ops_sales_rep navigates to Sales → Orders
Then they should NOT see SO S00001
  (Reason: S00001 is for My Company, not Branch-North)

When ops_accountant navigates to Sales → Orders
Then they should see SO S00001
  (Reason: Finance roles have global access)
```

---

### 4.5 API SECURITY TESTING

Reference: [`PHASE_3C_API_SECURITY_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3C_API_SECURITY_TEST_REPORT.md)

| Endpoint | Test | Expected Result | Status |
|----------|------|-----------------|--------|
| `/api/v1/ops_matrix/health` | Public access (no auth) | HTTP 200, returns DB name and timestamp | ✅ Available |
| `/api/v1/ops_matrix/me` | With API key | Returns user info, allowed branches/BUs | ⚠️ Need API key field (ISS-004) |
| `/api/v1/ops_matrix/branches` | As ops_sales_rep | Only returns Branch-North | ⚠️ Test after API keys added |
| `/api/v1/ops_matrix/branches` | As ops_accountant | Returns all 10 branches | ⚠️ Test after API keys added |
| `/api/v1/ops_matrix/branches/1` | As ops_sales_rep | HTTP 200 (Branch-North assigned) | ⚠️ Test after API keys added |
| `/api/v1/ops_matrix/branches/2` | As ops_sales_rep | HTTP 403 Forbidden (Branch-South not assigned) | ⚠️ Test after API keys added |

#### Testing Prerequisites

**Fix ISS-004 first:** Implement API key field

```bash
# Add API key field to res.users
# Then generate keys for test users
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
for login in ['ops_sales_rep', 'ops_sales_mgr', 'ops_accountant', 'ops_treasury']:
    user = env['res.users'].search([('login', '=', login)], limit=1)
    if user:
        api_key = user.generate_api_key()  # Implement this method
        print(f'{login}: {api_key}')
env.cr.commit()
EOF
```

#### Manual Test Steps: API Authentication

```bash
# Test 1: Public Health Check (No Auth Required)
curl http://localhost:8089/api/v1/ops_matrix/health

# Expected Response:
# {
#   "success": true,
#   "database": "mz-db",
#   "timestamp": "2025-12-28T21:00:00Z"
# }

# Test 2: Authenticated /me Endpoint
curl -X POST http://localhost:8089/api/v1/ops_matrix/me \
  -H "X-API-Key: SALES_REP_API_KEY_HERE"

# Expected Response:
# {
#   "success": true,
#   "data": {
#     "id": 9,
#     "login": "ops_sales_rep",
#     "name": "OPS Sales Representative",
#     "allowed_branches": [{"id": 1, "name": "Branch-North"}],
#     "allowed_business_units": [{"id": 1, "name": "BU-Sales"}]
#   }
# }

# Test 3: Branch Isolation via API
# Access assigned branch (should succeed)
curl -X POST http://localhost:8089/api/v1/ops_matrix/branches/1 \
  -H "X-API-Key: SALES_REP_API_KEY_HERE"
# Expected: HTTP 200

# Access unassigned branch (should fail)
curl -X POST http://localhost:8089/api/v1/ops_matrix/branches/2 \
  -H "X-API-Key: SALES_REP_API_KEY_HERE"
# Expected: HTTP 403 Forbidden

# Test 4: Invalid API Key
curl -X POST http://localhost:8089/api/v1/ops_matrix/me \
  -H "X-API-Key: invalid_key_12345"
# Expected: HTTP 401 Unauthorized
```

---

### 4.6 REPORTING SYSTEM TESTING

Reference: [`PHASE_3D_REPORTING_AUDIT_REPORT.md`](DeepSeek Dev Phases/PHASE_3D_REPORTING_AUDIT_REPORT.md)

| User | Report Tested | Expected Result | Status |
|------|---------------|-----------------|--------|
| admin | Sales Analysis | 🔴 **DATABASE ERROR** - JSONB type mismatch (ISS-001) | 🔴 BLOCKER |
| admin | Financial Analysis | Blocked by ISS-001 (transaction abort) | ⚠️ Fix ISS-001 first |
| admin | Inventory Analysis | Blocked by ISS-001 (transaction abort) | ⚠️ Fix ISS-001 first |
| ops_accountant | General Ledger | Wizard available, can generate report | ⚠️ Test manually |
| ops_accountant | Excel Export | Should export to XLSX format | ⚠️ Test manually |
| ops_sales_rep | Sales Analysis (after fix) | Should only see Branch-North data | ⚠️ Test after ISS-001 fixed |

#### 🔴 CRITICAL BLOCKER: Database Schema Error (ISS-001)

**Error:**
```sql
ERROR: cannot cast jsonb object to type numeric
Query: SELECT "ops_sales_analysis"."margin", "ops_sales_analysis"."margin_percent"
```

**Impact:** ALL reporting functionality is blocked

**Manual Verification (Will Fail):**

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
try:
    sales_data = env['ops.sales.analysis'].search([], limit=1)
    print('✅ No error - issue may be fixed')
except Exception as e:
    print(f'🔴 Error confirmed: {str(e)[:200]}')
EOF
```

**Expected Output (Current):** 🔴 Error message about JSONB casting

**After Fix:** ✅ No error message

**DO NOT TEST REPORTING UNTIL ISS-001 IS FIXED**

#### Manual Test Steps: General Ledger Report (After Fix)

```gherkin
Given ISS-001 is fixed
And I am logged in as ops_accountant

When I navigate to Accounting → Reporting → OPS General Ledger
Then I should see the General Ledger wizard

When I set date range: 2025-01-01 to 2025-12-31
And I select Branch: Branch-HQ
And I select BU: BU-Finance
And I click "Generate Report"

Then report should display:
  ✅ All journal entries for BU-Finance
  ✅ Grouped by account
  ✅ Filtered by date range
  ✅ Branch/BU dimensions visible

When I click "Export to Excel"
Then XLSX file should download
And file should contain all report data
```

---

## 🐛 SECTION 5: KNOWN ISSUES TESTING GUIDE

From [`PHASE_4_SAFETY_VERIFICATION_REPORT.md`](DeepSeek Dev Phases/PHASE_4_SAFETY_VERIFICATION_REPORT.md):

### ISS-001: Database Schema Error (CRITICAL) 🔴

**Severity:** CRITICAL  
**Impact:** Blocks all reporting functionality  
**Module:** [`ops_matrix_reporting`](addons/ops_matrix_reporting/)  
**File:** [`ops_sales_analysis.py`](addons/ops_matrix_reporting/models/ops_sales_analysis.py)

#### How to Confirm the Issue

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
try:
    # Try to read sales analysis records
    sales_data = env['ops.sales.analysis'].search_read([], ['margin', 'margin_percent'], limit=1)
    print('✅ NO ERROR - Issue is fixed')
    print(f'   Data: {sales_data}')
except Exception as e:
    print('🔴 ERROR CONFIRMED')
    print(f'   Error type: {type(e).__name__}')
    print(f'   Message: {str(e)[:200]}')
    if 'cannot cast jsonb' in str(e).lower():
        print('   ✅ Matches ISS-001 signature (JSONB casting error)')
EOF
```

**Expected Output (Current):**
```
🔴 ERROR CONFIRMED
   Error type: ProgrammingError
   Message: cannot cast jsonb object to type numeric
   ✅ Matches ISS-001 signature (JSONB casting error)
```

**After Fix:**
```
✅ NO ERROR - Issue is fixed
   Data: [{'id': 1, 'margin': 2740.0, 'margin_percent': 35.4}]
```

---

### ISS-002: Cost Shield Not Implemented (CRITICAL) 🔴

**Severity:** CRITICAL  
**Impact:** Sales reps can see product costs and margins  
**Module:** [`ops_matrix_core`](addons/ops_matrix_core/)  
**File:** [`sale_order.py`](addons/ops_matrix_core/models/sale_order.py)

#### How to Confirm the Issue

**Test 1: Check if cost/margin fields exist**

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
# Check if margin fields exist on sale.order.line
sol_model = env['sale.order.line']
has_purchase_price = 'purchase_price' in sol_model._fields
has_margin = 'margin' in sol_model._fields
has_margin_percent = 'margin_percent' in sol_model._fields

print('Cost Shield Field Verification:')
print(f'  purchase_price field exists: {has_purchase_price}')
print(f'  margin field exists: {has_margin}')
print(f'  margin_percent field exists: {has_margin_percent}')

if not (has_purchase_price and has_margin and has_margin_percent):
    print('\n🔴 ISS-002 CONFIRMED: Cost Shield fields missing')
else:
    print('\n✅ Cost Shield fields exist - proceed to UI test')
EOF
```

**Expected Output (Current):**
```
Cost Shield Field Verification:
  purchase_price field exists: False
  margin field exists: False
  margin_percent field exists: False

🔴 ISS-002 CONFIRMED: Cost Shield fields missing
```

**Test 2: UI Verification (After Fields Added)**

```gherkin
Given Cost Shield fields have been implemented
And I am logged in as ops_sales_rep

When I navigate to Sales → Orders → S00001
And I open an order line for Premium Widget B
Then I should see:
  ✅ Product: Premium Widget B
  ✅ Quantity: 10
  ✅ Unit Price: $399.00
  ✅ Subtotal: $3,990.00

But I should NOT see (fields should be hidden by groups parameter):
  ❌ Cost field
  ❌ Margin field
  ❌ Margin % field

When I logout and login as ops_accountant
And I open the same order line
Then I should now see:
  ✅ Cost: $250.00
  ✅ Margin: $149.00
  ✅ Margin %: 37.3%
```

**Current Status:** 🔴 Fields don't exist, so UI test cannot be performed

---

### ISS-003: Missing Accounting Journals (CRITICAL) 🔴

**Severity:** CRITICAL  
**Impact:** Cannot create invoices from sales orders or purchase orders  
**Module:** Configuration (not code issue)

#### How to Confirm the Issue

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
# Check for required journals
sales_journals = env['account.journal'].search([('type', '=', 'sale')])
purchase_journals = env['account.journal'].search([('type', '=', 'purchase')])

print('Accounting Journal Verification:')
print(f'  Sales Journals: {len(sales_journals)}')
for j in sales_journals:
    print(f'    - {j.name} ({j.code})')

print(f'  Purchase Journals: {len(purchase_journals)}')
for j in purchase_journals:
    print(f'    - {j.name} ({j.code})')

if len(sales_journals) == 0:
    print('\n🔴 ISS-003 CONFIRMED: Missing sales journal')
if len(purchase_journals) == 0:
    print('\n🔴 ISS-003 CONFIRMED: Missing purchase journal')

if len(sales_journals) == 0 or len(purchase_journals) == 0:
    print('\nImpact: Cannot create invoices from SO/PO')
else:
    print('\n✅ Required journals exist')
EOF
```

**Expected Output (Current):**
```
Accounting Journal Verification:
  Sales Journals: 0
  Purchase Journals: 0

🔴 ISS-003 CONFIRMED: Missing sales journal
🔴 ISS-003 CONFIRMED: Missing purchase journal

Impact: Cannot create invoices from SO/PO
```

**After Fix:**
```
Accounting Journal Verification:
  Sales Journals: 1
    - Customer Invoices (INV)
  Purchase Journals: 1
    - Vendor Bills (BILL)

✅ Required journals exist
```

**UI Test After Fix:**

```gherkin
Given sales and purchase journals are configured
And I am logged in as admin

# Test 1: Create invoice from sales order
When I navigate to Sales → Orders → S00001
And I click "Create Invoice"
Then invoice should be created without errors
And invoice journal should be "Customer Invoices (INV)"

# Test 2: Create bill from purchase order
When I navigate to Purchase → Orders → P00002
And I click "Create Bill"
Then vendor bill should be created without errors
And bill journal should be "Vendor Bills (BILL)"
```

---

## 📊 SECTION 6: DATABASE INSPECTION COMMANDS

### SQL Queries (Direct Database Access)

```sql
-- View all branches
SELECT id, name, code, active, company_id 
FROM ops_branch 
ORDER BY name;

-- View all business units with branch count
SELECT bu.id, bu.name, bu.code, bu.active, COUNT(br.ops_branch_id) as branch_count
FROM ops_business_unit bu
LEFT JOIN ops_branch_ops_business_unit_rel br ON br.ops_business_unit_id = bu.id
GROUP BY bu.id, bu.name, bu.code, bu.active
ORDER BY bu.name;

-- View test users with persona assignments
SELECT u.id, u.login, u.name, u.active, p.name as persona, p.code as persona_code
FROM res_users u
LEFT JOIN ops_persona p ON p.id = u.persona_id
WHERE u.login LIKE 'ops_%'
ORDER BY u.login;

-- View test personas with authority levels
SELECT id, name, code, approval_limit, is_approver, is_bu_leader,
       can_access_cost_prices, can_validate_invoices, can_post_journal_entries,
       can_execute_payments, can_manage_pdc
FROM ops_persona
ORDER BY approval_limit;

-- View sales order S00001 with dimensions
SELECT so.id, so.name, so.partner_id, p.name as customer, 
       so.amount_total, so.state, so.date_order,
       so.ops_branch_id, so.ops_business_unit_id
FROM sale_order so
LEFT JOIN res_partner p ON p.id = so.partner_id
WHERE so.name = 'S00001';

-- View purchase order P00002 with dimensions
SELECT po.id, po.name, po.partner_id, p.name as vendor,
       po.amount_total, po.state, po.date_order,
       po.ops_branch_id, po.ops_business_unit_id
FROM purchase_order po
LEFT JOIN res_partner p ON p.id = po.partner_id
WHERE po.name = 'P00002';

-- View security audit logs (governance bypass tracking)
SELECT sa.id, sa.create_date, u.login as user, 
       sa.model_name, sa.record_id, sa.reason
FROM ops_security_audit sa
LEFT JOIN res_users u ON u.id = sa.user_id
WHERE sa.model_name IN ('sale.order', 'purchase.order')
ORDER BY sa.create_date DESC
LIMIT 20;

-- View accounting journals
SELECT id, name, code, type, company_id, active
FROM account_journal
WHERE type IN ('sale', 'purchase')
ORDER BY type, name;

-- View analytic accounts for branches
SELECT b.id, b.name as branch, b.code,
       aa.id as analytic_id, aa.name as analytic_name
FROM ops_branch b
LEFT JOIN account_analytic_account aa ON aa.id = b.analytic_account_id
ORDER BY b.name;

-- Check for orphaned records (referential integrity)
SELECT 'Users without persona' as issue, COUNT(*) as count
FROM res_users
WHERE active = true 
  AND login NOT IN ('admin', '__system__')
  AND persona_id IS NULL
UNION ALL
SELECT 'Branches without company', COUNT(*)
FROM ops_branch
WHERE company_id IS NULL
UNION ALL
SELECT 'BUs without branches', COUNT(*)
FROM ops_business_unit bu
WHERE NOT EXISTS (
    SELECT 1 FROM ops_branch_ops_business_unit_rel r 
    WHERE r.ops_business_unit_id = bu.id
);
```

### Odoo Shell Queries (ORM Access)

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
# === INFRASTRUCTURE VERIFICATION ===
print('='*60)
print('INFRASTRUCTURE DATA VERIFICATION')
print('='*60)

# Branches
branches = env['ops.branch'].search([])
print(f'\nBranches: {len(branches)}')
for b in branches:
    print(f'  [{b.code}] {b.name} - Analytic: {b.analytic_account_id.name if b.analytic_account_id else "Missing"}')

# Business Units
bus = env['ops.business.unit'].search([])
print(f'\nBusiness Units: {len(bus)}')
for bu in bus:
    print(f'  [{bu.code}] {bu.name} - Branches: {len(bu.branch_ids)}')

# Users
users = env['res.users'].search([('login', 'like', 'ops_%')])
print(f'\nTest Users: {len(users)}')
for u in users:
    persona = u.persona_id.name if u.persona_id else 'None'
    branch = u.primary_branch_id.name if u.primary_branch_id else 'None'
    print(f'  {u.login}: {persona} | Branch: {branch}')

# Personas
personas = env['ops.persona'].search([])
print(f'\nPersonas: {len(personas)}')
for p in personas:
    print(f'  [{p.code}] {p.name} - Approval Limit: ${p.approval_limit:,.0f}')

# Products
products = env['product.template'].search([
    ('default_code', 'in', ['WIDGET-A-001', 'WIDGET-B-002', 'SOLUTION-C-003', 'EQUIPMENT-D-004', 'SUPPLIES-E-005'])
])
print(f'\nTest Products: {len(products)}')
for p in products:
    print(f'  [{p.default_code}] {p.name} - Cost: ${p.standard_price:.2f} / Price: ${p.list_price:.2f}')

# === TRANSACTION VERIFICATION ===
print('\n' + '='*60)
print('TRANSACTION DATA VERIFICATION')
print('='*60)

# Sales Orders
so = env['sale.order'].browse(1)
if so.exists():
    print(f'\nSales Order: {so.name}')
    print(f'  Customer: {so.partner_id.name}')
    print(f'  Amount: ${so.amount_total:,.2f}')
    print(f'  State: {so.state}')
    print(f'  Lines: {len(so.order_line)}')
    for line in so.order_line:
        print(f'    - {line.product_id.name}: {line.product_uom_qty} x ${line.price_unit:.2f}')

# Purchase Orders
po = env['purchase.order'].browse(2)
if po.exists():
    print(f'\nPurchase Order: {po.name}')
    print(f'  Vendor: {po.partner_id.name}')
    print(f'  Amount: ${po.amount_total:,.2f}')
    print(f'  State: {po.state}')
    print(f'  Lines: {len(po.order_line)}')
    for line in po.order_line:
        print(f'    - {line.product_id.name}: {line.product_qty} x ${line.price_unit:.2f}')

# === CONFIGURATION VERIFICATION ===
print('\n' + '='*60)
print('CONFIGURATION VERIFICATION')
print('='*60)

# Journals
sales_journals = env['account.journal'].search([('type', '=', 'sale')])
purchase_journals = env['account.journal'].search([('type', '=', 'purchase')])
print(f'\nSales Journals: {len(sales_journals)}')
for j in sales_journals:
    print(f'  - {j.name} ({j.code})')
print(f'Purchase Journals: {len(purchase_journals)}')
for j in purchase_journals:
    print(f'  - {j.name} ({j.code})')

# Governance Rules
gov_rules = env['ops.governance.rule'].search([('active', '=', True)])
print(f'\nActive Governance Rules: {len(gov_rules)}')
for rule in gov_rules:
    model = rule.model_id.model
    print(f'  - {rule.name} ({model}): {rule.action_type}')

# Security Audits
audits = env['ops.security.audit'].search([], order='create_date desc', limit=10)
print(f'\nRecent Security Audits: {len(audits)}')
for audit in audits:
    print(f'  - {audit.create_date} | {audit.user_id.login} | {audit.model_name} {audit.record_id}: {audit.reason}')

print('\n' + '='*60)
print('VERIFICATION COMPLETE')
print('='*60)
EOF
```

---

## 🔧 SECTION 7: FIX INSTRUCTIONS (PRIORITY ORDER)

### Fix 1: Database Schema Error (ISS-001) - 1 Hour

**Priority:** 🔴 CRITICAL  
**Effort:** 1 hour  
**Module:** [`ops_matrix_reporting`](addons/ops_matrix_reporting/)

#### Step-by-Step Fix

**IMPORTANT:** Do NOT use direct SQL commands. Use migration scripts (per `.roorules`).

```bash
# Step 1: Create migration directory
mkdir -p /opt/gemini_odoo19/addons/ops_matrix_reporting/migrations/19.0.1.1

# Step 2: Create migration script
cat > /opt/gemini_odoo19/addons/ops_matrix_reporting/migrations/19.0.1.1/post-migration.py << 'EOF'
# -*- coding: utf-8 -*-
"""
Migration script to fix JSONB type mismatch in ops.sales.analysis

Root Cause: Fields defined as Float in Python but created as JSONB in database
Fix: Drop incorrect columns and let Odoo recreate with correct types
"""

def migrate(cr, version):
    """
    Drop JSONB columns that should be numeric.
    Module upgrade will recreate them with correct types.
    """
    # Drop margin field if it exists and is wrong type
    cr.execute("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ops_sales_analysis' 
        AND column_name = 'margin'
    """)
    result = cr.fetchone()
    if result and result[0] == 'jsonb':
        cr.execute("ALTER TABLE ops_sales_analysis DROP COLUMN IF EXISTS margin")
        print("Dropped incorrect 'margin' column (was JSONB, should be numeric)")
    
    # Drop margin_percent field if it exists and is wrong type
    cr.execute("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = 'ops_sales_analysis' 
        AND column_name = 'margin_percent'
    """)
    result = cr.fetchone()
    if result and result[0] == 'jsonb':
        cr.execute("ALTER TABLE ops_sales_analysis DROP COLUMN IF EXISTS margin_percent")
        print("Dropped incorrect 'margin_percent' column (was JSONB, should be numeric)")
    
    print("Migration complete: ops_sales_analysis schema fixed")
EOF

# Step 3: Upgrade module to apply migration
docker exec gemini_odoo19 odoo -d mz-db -u ops_matrix_reporting --stop-after-init

# Step 4: Verify fix
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
try:
    sales_data = env['ops.sales.analysis'].search_read([], ['margin', 'margin_percent'], limit=1)
    print('✅ ISS-001 FIXED: Sales analysis queries working')
    print(f'   Sample data: {sales_data}')
except Exception as e:
    print(f'❌ ISS-001 NOT FIXED: {str(e)[:100]}')
EOF
```

**Expected Output After Fix:**
```
✅ ISS-001 FIXED: Sales analysis queries working
   Sample data: [{'id': 1, 'margin': 2740.0, 'margin_percent': 35.4}]
```

---

### Fix 2: Configure Accounting Journals (ISS-003) - 30 Minutes

**Priority:** 🔴 CRITICAL  
**Effort:** 30 minutes  
**Module:** Configuration (no code changes)

#### Option A: Via Odoo Shell (Recommended)

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
company = env['res.company'].browse(1)

# Create Sales Journal
sales_journal = env['account.journal'].create({
    'name': 'Customer Invoices',
    'code': 'INV',
    'type': 'sale',
    'company_id': company.id,
    'sequence': 10,
})
print(f'✅ Created sales journal: {sales_journal.name} (ID: {sales_journal.id})')

# Create Purchase Journal
purchase_journal = env['account.journal'].create({
    'name': 'Vendor Bills',
    'code': 'BILL',
    'type': 'purchase',
    'company_id': company.id,
    'sequence': 20,
})
print(f'✅ Created purchase journal: {purchase_journal.name} (ID: {purchase_journal.id})')

env.cr.commit()
print('\n✅ ISS-003 FIXED: Accounting journals configured')
EOF
```

#### Option B: Via Odoo UI

```gherkin
Given I am logged in as admin
When I navigate to Accounting → Configuration → Journals
And I click "Create"

# Create Sales Journal
Then I fill in:
  Name: Customer Invoices
  Type: Sales
  Short Code: INV
  Company: My Company
And I click "Save"

# Create Purchase Journal
When I click "Create" again
Then I fill in:
  Name: Vendor Bills
  Type: Purchase
  Short Code: BILL
  Company: My Company
And I click "Save"
```

#### Verification

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
sales_journals = env['account.journal'].search([('type', '=', 'sale')])
purchase_journals = env['account.journal'].search([('type', '=', 'purchase')])

if len(sales_journals) > 0 and len(purchase_journals) > 0:
    print('✅ ISS-003 FIXED: Required journals exist')
    print(f'   Sales: {sales_journals[0].name}')
    print(f'   Purchase: {purchase_journals[0].name}')
else:
    print('❌ ISS-003 NOT FIXED: Missing journals')
EOF
```

#### Test Invoice Creation After Fix

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
# Test creating invoice from SO S00001
so = env['sale.order'].browse(1)
if so.exists() and so.state == 'sale':
    invoice = so._create_invoices()
    print(f'✅ Invoice created from SO: {invoice.name}')
    print(f'   Journal: {invoice.journal_id.name}')
else:
    print('⚠️ SO S00001 not in correct state for invoicing')
EOF
```

---

### Fix 3: Implement Cost Shield (ISS-002) - 4 Hours

**Priority:** 🔴 CRITICAL  
**Effort:** 4 hours  
**Module:** [`ops_matrix_core`](addons/ops_matrix_core/)

#### Option A: Install sale_margin Module (Recommended, 1 Hour)

```bash
# Step 1: Install sale_margin module (includes margin tracking)
docker exec gemini_odoo19 odoo -d mz-db -i sale_margin --stop-after-init

# Step 2: Restart Odoo service
docker restart gemini_odoo19

# Step 3: Verify fields exist
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
sol_model = env['sale.order.line']
has_purchase_price = 'purchase_price' in sol_model._fields
has_margin = 'margin' in sol_model._fields

if has_purchase_price and has_margin:
    print('✅ sale_margin module installed successfully')
    print('   Fields: purchase_price, margin exist')
else:
    print('❌ sale_margin installation failed')
EOF

# Step 4: Apply field-level security (add groups parameter)
# Edit addons/ops_matrix_core/views/sale_order_views.xml
# Add groups="product.group_product_pricelist" to cost fields
```

**Field Security Configuration:**

Add to [`sale_order_views.xml`](addons/ops_matrix_core/views/sale_order_views.xml):

```xml
<record id="view_order_form_cost_shield" model="ir.ui.view">
    <field name="name">sale.order.form.cost.shield</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='order_line']/tree/field[@name='price_unit']" position="after">
            <!-- Cost fields visible only to managers/accountants -->
            <field name="purchase_price" groups="product.group_product_pricelist"/>
            <field name="margin" groups="product.group_product_pricelist"/>
            <field name="margin_percent" groups="product.group_product_pricelist"/>
        </xpath>
    </field>
</record>
```

#### Option B: Custom Implementation (4 Hours)

If sale_margin module is not available, implement custom fields:

```python
# In addons/ops_matrix_core/models/sale_order.py

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    purchase_price = fields.Float(
        string='Cost',
        compute='_compute_purchase_price',
        groups='product.group_product_pricelist',  # Hide from sales reps
        store=True,
        help='Product cost price'
    )
    
    margin = fields.Float(
        string='Margin',
        compute='_compute_margin',
        groups='product.group_product_pricelist',
        store=True,
        help='Line margin amount (Price - Cost)'
    )
    
    margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin',
        groups='product.group_product_pricelist',
        store=True,
        help='Line margin percentage'
    )
    
    @api.depends('product_id', 'product_uom_qty')
    def _compute_purchase_price(self):
        for line in self:
            line.purchase_price = line.product_id.standard_price * line.product_uom_qty
    
    @api.depends('price_subtotal', 'purchase_price')
    def _compute_margin(self):
        for line in self:
            line.margin = line.price_subtotal - line.purchase_price
            if line.price_subtotal:
                line.margin_percent = (line.margin / line.price_subtotal) * 100
            else:
                line.margin_percent = 0.0
```

#### Verification

```bash
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
# Test Cost Shield
sol_model = env['sale.order.line']
has_fields = all([
    'purchase_price' in sol_model._fields,
    'margin' in sol_model._fields,
    'margin_percent' in sol_model._fields
])

if has_fields:
    print('✅ ISS-002 FIXED: Cost Shield fields exist')
    # Test field security
    so = env['sale.order'].browse(1)
    if so.exists():
        line = so.order_line[0]
        print(f'   Test line: {line.product_id.name}')
        print(f'   Cost: ${line.purchase_price:.2f}')
        print(f'   Margin: ${line.margin:.2f} ({line.margin_percent:.1f}%)')
else:
    print('❌ ISS-002 NOT FIXED: Cost Shield fields missing')
EOF
```

---

## 📋 SECTION 8: PRODUCTION SIGN-OFF CHECKLIST

### Phase 1: Critical Fixes ✅/❌

**Deadline:** Day 1-2 (5.5 hours total)

- [ ] **ISS-001: Database schema error fixed**
  - [ ] Migration script created in `ops_matrix_reporting/migrations/19.0.1.1/`
  - [ ] Module upgraded successfully (`odoo -u ops_matrix_reporting`)
  - [ ] Sales analysis queries working (no JSONB errors)
  - [ ] Verified with: `env['ops.sales.analysis'].search_read([], ['margin'])`
  
- [ ] **ISS-002: Cost Shield implemented**
  - [ ] `sale_margin` installed OR custom fields added
  - [ ] Field-level security applied (`groups="product.group_product_pricelist"`)
  - [ ] Tested with ops_sales_rep user (cost fields hidden)
  - [ ] Tested with ops_accountant user (cost fields visible)
  - [ ] View inheritance added to [`sale_order_views.xml`](addons/ops_matrix_core/views/sale_order_views.xml)
  
- [ ] **ISS-003: Accounting journals configured**
  - [ ] Sales journal created (Customer Invoices / INV)
  - [ ] Purchase journal created (Vendor Bills / BILL)
  - [ ] Test invoice creation from SO S00001 (should succeed)
  - [ ] Test bill creation from PO P00002 (should succeed)

**Criteria:** ALL 3 must pass before proceeding to Phase 2

---

### Phase 2: High Priority ✅/❌

**Deadline:** Week 1 (11.25 hours total)

- [ ] **API Production Ready (ISS-004-007)**
  - [ ] API key field implemented in [`res_users.py`](addons/ops_matrix_core/models/res_users.py)
  - [ ] Keys generated for all test users
  - [ ] Redis rate limiting deployed
  - [ ] API access logging active (`ops.api.log` model)
  - [ ] Keys hashed in database (SHA-256)
  - [ ] API stress test passed (1000+ requests)
  
- [ ] **Governance Active (ISS-008-009)**
  - [ ] Approval rules configured for PO >$10K
  - [ ] Approval rules configured for SO discount >10%
  - [ ] Governance logging bug fixed (model_name defined)
  - [ ] Test approval workflow: create → approve → confirm
  - [ ] SoD enforcement verified (self-approval blocked)
  
- [ ] **Analytic Accounts Verified (ISS-010)**
  - [ ] All 10 branches have analytic accounts (80%+ target)
  - [ ] SO S00001 has analytic tags
  - [ ] PO P00002 has analytic tags
  - [ ] P&L by Branch/BU working

**Criteria:** ALL items must pass for production deployment

---

### Phase 3: Feature Validation ✅/❌

**Deadline:** Week 2

- [ ] **End-to-End Procurement Workflow**
  - [ ] Sales rep creates order → manager approves → invoice posted
  - [ ] Purchase order → vendor bill → payment executed
  - [ ] PDC lifecycle: register → deposit → clear
  
- [ ] **End-to-End Sales Workflow**
  - [ ] Create SO as ops_sales_rep → Confirm
  - [ ] Cost fields HIDDEN from sales rep
  - [ ] Create invoice as ops_accountant → Post
  - [ ] Verify governance logs in Chatter
  
- [ ] **Branch/BU Isolation**
  - [ ] ops_sales_rep sees only Branch-North (1 branch)
  - [ ] ops_accountant sees all 10 branches
  - [ ] Cross-branch data filtered correctly
  - [ ] API endpoints respect branch isolation
  
- [ ] **Reporting Functional**
  - [ ] Sales Analysis generates without errors
  - [ ] Financial Analysis accessible
  - [ ] Inventory Analysis accessible
  - [ ] General Ledger report works
  - [ ] Excel export generates XLSX files

**Criteria:** 100% pass rate required

---

### Phase 4: Security Validation ✅/❌

- [ ] **API Security**
  - [ ] Authentication working (valid keys accepted, invalid rejected)
  - [ ] Authorization enforced (branch/BU filtering)
  - [ ] Rate limiting prevents abuse
  - [ ] Access logged for auditing
  
- [ ] **Cost Shield**
  - [ ] Sales rep CANNOT see cost fields
  - [ ] Manager CAN see cost/margin
  - [ ] Accountant CAN see full profitability
  - [ ] Groups parameter enforced
  
- [ ] **SoD Enforcement**
  - [ ] Self-approval blocked
  - [ ] Cross-functional approvals required
  - [ ] Escalation to parent persona working
  - [ ] Admin bypass logged
  
- [ ] **Audit Trail**
  - [ ] All governance overrides logged
  - [ ] Security audit records created
  - [ ] Chatter messages for approval actions
  - [ ] User context properly tracked

**Criteria:** 100% pass rate required

---

### Phase 5: Data Integrity ✅/❌

- [ ] **Test Data Persistent**
  - [ ] All 10 branches exist and active
  - [ ] All 10 BUs exist and active
  - [ ] All 4 test users can login
  - [ ] All 4 personas have correct authority levels
  - [ ] All 5 products exist with cost/price
  - [ ] SO S00001 displays correctly ($7,740)
  - [ ] PO P00002 displays correctly ($24,000)
  
- [ ] **Referential Integrity**
  - [ ] No orphaned users (all have personas)
  - [ ] No orphaned branches (all have companies)
  - [ ] No orphaned BUs (all have branches)
  - [ ] Foreign keys intact
  
- [ ] **Analytic Tagging**
  - [ ] All transactions have Branch dimension
  - [ ] All transactions have BU dimension
  - [ ] Analytic accounts properly linked
  - [ ] P&L reports filter correctly

**Criteria:** 100% verification required

---

### Phase 6: Performance Testing ✅/❌

- [ ] **Query Performance**
  - [ ] Matrix queries (10×10) complete in <2 seconds
  - [ ] Report generation <5 seconds for 100 orders
  - [ ] API responses <200ms average
  - [ ] Database indexes optimized
  
- [ ] **Load Testing**
  - [ ] 100 concurrent users supported
  - [ ] API rate limiting functional under load
  - [ ] No memory leaks after 1000 transactions
  - [ ] Redis connection pool stable

**Criteria:** Performance targets met

---

## 📚 SECTION 9: QUICK REFERENCE

### All Phase Reports

**Phase Discovery & Planning:**
- [`OPS_FEATURE_MAP.md`](OPS_FEATURE_MAP.md) - Complete feature inventory (50+ models, 15+ API endpoints)

**Phase 2: Infrastructure Seeding:**
- [`PHASE_2_INFRASTRUCTURE_SEEDING_REPORT.md`](DeepSeek Dev Phases/PHASE_2_INFRASTRUCTURE_SEEDING_REPORT.md) - 10 branches, 10 BUs, 5 products
- [`PHASE_2B_USER_CREATION_COMPLETION_REPORT.md`](DeepSeek Dev Phases/PHASE_2B_USER_CREATION_COMPLETION_REPORT.md) - 4 users, 4 personas

**Phase 3: Workflow Testing:**
- [`PHASE_3A_PROCUREMENT_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3A_PROCUREMENT_TEST_REPORT.md) - PO P00002 ($24K), governance tested
- [`PHASE_3B_SALES_STRESS_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3B_SALES_STRESS_TEST_REPORT.md) - SO S00001 ($7.7K), Cost Shield issue
- [`PHASE_3C_API_SECURITY_TEST_REPORT.md`](DeepSeek Dev Phases/PHASE_3C_API_SECURITY_TEST_REPORT.md) - 15+ endpoints validated
- [`PHASE_3D_REPORTING_AUDIT_REPORT.md`](DeepSeek Dev Phases/PHASE_3D_REPORTING_AUDIT_REPORT.md) - Database schema error found

**Phase 4: Safety Verification:**
- [`PHASE_4_SAFETY_VERIFICATION_REPORT.md`](DeepSeek Dev Phases/PHASE_4_SAFETY_VERIFICATION_REPORT.md) - 21 issues, 61.2% ready

### All Test Scripts

**Located in:** [`scripts/`](scripts/)

**Infrastructure Scripts:**
- [`phase2_seed_infrastructure.py`](scripts/phase2_seed_infrastructure.py) - Seeds branches, BUs, products
- [`phase2b_create_users_simple.py`](scripts/phase2b_create_users_simple.py) - Creates test users
- [`phase2b_create_users.py`](scripts/phase2b_create_users.py) - Full-featured user creation

**Workflow Test Scripts:**
- [`phase3a_procurement_stress_test.py`](scripts/phase3a_procurement_stress_test.py) - Tests procurement workflow
- [`phase3a_test_odoo_shell.py`](scripts/phase3a_test_odoo_shell.py) - Odoo shell compatible test
- [`phase3b_sales_stress_test.py`](scripts/phase3b_sales_stress_test.py) - Tests sales workflow

**Audit Scripts:**
- [`phase3d_reporting_audit.py`](scripts/phase3d_reporting_audit.py) - Audits reporting system
- [`phase3d_audit_simple.py`](scripts/phase3d_audit_simple.py) - Simplified audit
- [`phase3d_audit_robust.py`](scripts/phase3d_audit_robust.py) - Comprehensive audit

**Utility Scripts:**
- [`check_ops_modules.py`](scripts/check_ops_modules.py) - Verifies module installation
- [`list_personas.py`](scripts/list_personas.py) - Lists all personas
- [`run_phase3d_audit.sh`](scripts/run_phase3d_audit.sh) - Bash wrapper for audits

### Key Files Reference

**Core Module:**
- [`ops_governance_mixin.py`](addons/ops_matrix_core/models/ops_governance_mixin.py) - 413 lines, governance logic
- [`ops_persona.py`](addons/ops_matrix_core/models/ops_persona.py) - 1231 lines, authority system
- [`ops_matrix_api.py`](addons/ops_matrix_core/controllers/ops_matrix_api.py) - 852 lines, REST API
- [`res_users.py`](addons/ops_matrix_core/models/res_users.py) - User extensions
- [`sale_order.py`](addons/ops_matrix_core/models/sale_order.py) - Sales order extensions
- [`purchase_order.py`](addons/ops_matrix_core/models/purchase_order.py) - Purchase order extensions

**Accounting Module:**
- [`ops_pdc.py`](addons/ops_matrix_accounting/models/ops_pdc.py) - Post-dated check management
- [`ops_budget.py`](addons/ops_matrix_accounting/models/ops_budget.py) - Budget tracking

**Reporting Module:**
- [`ops_sales_analysis.py`](addons/ops_matrix_reporting/models/ops_sales_analysis.py) - Sales analytics (ISS-001)
- [`ops_financial_analysis.py`](addons/ops_matrix_reporting/models/ops_financial_analysis.py) - Financial analytics
- [`ops_inventory_analysis.py`](addons/ops_matrix_reporting/models/ops_inventory_analysis.py) - Inventory analytics

---

## ⏱️ SECTION 10: TIMELINE TO PRODUCTION

### Current Status

**Production Readiness:** 61.2%
**Target:** 95%
**Gap:** 33.8 percentage points
**Estimated Time:** 2 weeks (10 business days)

### Week 1: Critical Path

#### Day 1-2: Critical Fixes (5.5 hours)

**Priority 1:** ISS-001 - Database Schema Error (1 hour)
- Create migration script
- Upgrade ops_matrix_reporting module
- Verify sales analysis queries working
- **Deliverable:** Reporting system functional

**Priority 2:** ISS-002 - Cost Shield (4 hours)
- Install sale_margin module OR implement custom
- Apply field-level security groups
- Test with ops_sales_rep (should NOT see costs)
- Test with ops_accountant (should see costs)
- **Deliverable:** Margin protection active

**Priority 3:** ISS-003 - Configure Journals (30 minutes)
- Create sales journal (Customer Invoices / INV)
- Create purchase journal (Vendor Bills / BILL)
- Test invoice creation from SO S00001
- **Deliverable:** Invoicing workflow operational

**Status After Day 2:** 75% Production Ready

---

#### Day 3-5: Production Hardening (11.25 hours)

**Priority 4:** ISS-004 - API Key Field (30 minutes)
- Add ops_api_key field to res.users model
- Generate keys for test users
- **Deliverable:** API authentication ready

**Priority 5:** ISS-005 - Redis Rate Limiting (4 hours)
- Install Redis server
- Implement sliding window rate limiter
- Test with 1000+ requests
- **Deliverable:** API production-ready

**Priority 6:** ISS-006 - API Access Logging (3 hours)
- Create ops.api.log model
- Add logging middleware
- Test log generation
- **Deliverable:** API auditing active

**Priority 7:** ISS-007 - Hash API Keys (1 hour)
- Implement SHA-256 hashing
- Migrate existing keys
- Test validation logic
- **Deliverable:** API keys secured

**Priority 8:** ISS-008 - Configure Governance Rules (2 hours)
- Create PO approval rules (>$10K, >$50K, >$100K)
- Create SO approval rules (discount >10%)
- Set approval limits on personas
- **Deliverable:** Governance workflows active

**Priority 9:** ISS-009 - Fix Governance Logging (30 minutes)
- Define model_name before use
- Test admin override logging
- **Deliverable:** Governance logs working

**Priority 10:** ISS-010 - Verify Analytic Accounts (15 minutes)
- Check all 10 branches have analytic accounts
- Verify SO/PO have analytic tags
- **Deliverable:** P&L by Branch/BU operational

**Status After Day 5:** 90% Production Ready

---

### Week 2: Final Validation

#### Day 6-8: Complete Testing (3 hours)

**Test Suite 1:** End-to-End Workflows
- Procurement: Create PO → Approve → Bill → Pay
- Sales: Create SO → Approve → Invoice → Collect
- Reporting: Generate all reports without errors

**Test Suite 2:** Security Validation
- Cost Shield: Sales rep cannot see costs
- SoD: Self-approval blocked
- Branch Isolation: Users see only assigned branches
- API: Authentication and authorization enforced

**Test Suite 3:** Data Integrity
- All test data persistent
- Referential integrity intact
- Analytic tagging correct
- Audit trail complete

**Status After Day 8:** 95% Production Ready

---

#### Day 9-10: Security Audit & Sign-Off (2 hours)

**External Security Audit:**
- Penetration testing (API endpoints)
- SQL injection testing
- Authorization bypass attempts
- Performance stress testing

**Final Sign-Off:**
- All checklists completed
- All test scenarios passed
- Performance targets met
- Documentation updated

**Status After Day 10:** 95%+ Production Ready ✅

---

### Risk Mitigation

**Risk 1:** Fix takes longer than estimated
- **Mitigation:** Start with ISS-001 (highest impact)
- **Fallback:** Skip ISS-011-015 (medium priority)

**Risk 2:** New issues discovered during testing
- **Mitigation:** 5-trial rule (stop and ask for help)
- **Fallback:** Document issue, continue with other tests

**Risk 3:** External dependencies (Redis, modules)
- **Mitigation:** Test installation on Day 1
- **Fallback:** Use in-memory rate limiting temporarily

---

## 🎓 SECTION 11: TESTING BEST PRACTICES

### For Mohamad: Manual Testing Guidelines

#### 1. Start Simple, Build Complexity

```
Day 1: Verify test data exists (5 minutes)
Day 2: Login as each test user (10 minutes)
Day 3: View test transactions (10 minutes)
Day 4: Test single workflow (30 minutes)
Day 5: Test cross-functional scenarios (1 hour)
```

#### 2. Document Everything

For each test:
- **Expected Result:** What should happen
- **Actual Result:** What actually happened
- **Screenshots:** Visual evidence
- **Error Messages:** Copy exact text
- **Reproduction Steps:** How to reproduce issue

#### 3. Test as Different Users

```bash
# Always test with multiple user roles:
1. admin (unrestricted access)
2. ops_sales_rep (restricted to Branch-North)
3. ops_accountant (global access)
4. ops_treasury (payment authority)
```

#### 4. Use Verification Commands

After each fix, run verification command:
```bash
# Example: Verify ISS-001 fix
docker exec -i gemini_odoo19 odoo shell -d mz-db --no-http << 'EOF'
try:
    env['ops.sales.analysis'].search_read([], ['margin'], limit=1)
    print('✅ PASS')
except:
    print('❌ FAIL')
EOF
```

#### 5. Check Database State

Before and after critical operations:
```sql
-- Count records before test
SELECT COUNT(*) FROM sale_order;

-- Run test...

-- Count records after test
SELECT COUNT(*) FROM sale_order;
-- Should be +1 if order was created
```

---

## 🎯 CONCLUSION

This testing roadmap provides Mohamad with complete instructions to:

1. ✅ **Access the test environment** (Section 2)
2. ✅ **Verify all test data** (Section 3)
3. ✅ **Test all features systematically** (Section 4)
4. ✅ **Confirm known issues** (Section 5)
5. ✅ **Inspect database state** (Section 6)
6. ✅ **Apply fixes in priority order** (Section 7)
7. ✅ **Sign off on production readiness** (Section 8)

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Test Data Created** | 10 branches, 10 BUs, 4 users, 5 products, 2 transactions |
| **Test Scenarios** | 50+ manual tests across 6 feature areas |
| **Known Issues** | 3 critical, 7 high, 5 medium, 6 configuration |
| **Fix Time Estimate** | 5.5 hours (critical) + 11.25 hours (high) = 16.75 hours |
| **Production Timeline** | 2 weeks (10 business days) |
| **Current Readiness** | 61.2% → Target: 95% |

### Next Actions for Mohamad

**Immediate (Today):**
1. Read Executive Summary (Section 1)
2. Access test environment (Section 2)
3. Run test data verification commands (Section 3)
4. Confirm the 3 critical issues (Section 5)

**Tomorrow:**
5. Apply Fix 1: Database Schema Error (Section 7)
6. Apply Fix 2: Configure Journals (Section 7)
7. Apply Fix 3: Cost Shield (Section 7)

**Week 1:**
8. Complete all manual tests (Section 4)
9. Apply high-priority fixes (Section 7)
10. Run production sign-off checklist (Section 8)

**Week 2:**
11. Security audit and performance testing
12. Final validation and sign-off
13. Prepare for production deployment

### Success Criteria

**The OPS Framework is ready for production when:**

- ✅ All 3 critical issues resolved (ISS-001, 002, 003)
- ✅ All high-priority issues resolved (ISS-004 through 010)
- ✅ All test scenarios pass 100%
- ✅ Production readiness score ≥95%
- ✅ Security audit completed with no major findings
- ✅ Performance targets met
- ✅ Documentation complete and verified

---

**Report Generated:** 2025-12-28
**Generated By:** Phase 5 - Human Handover Testing Roadmap
**For:** Mohamad (Manual Testing & Production Validation)
**Status:** ✅ COMPLETE - Ready for Manual Testing
**Next Phase:** Manual validation and production deployment

---

**END OF OPS FRAMEWORK TESTING ROADMAP**