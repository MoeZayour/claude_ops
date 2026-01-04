# OPS Matrix Framework - Implementation Plan: Option 2 (Full Features)

**Version**: 1.0
**Created**: January 4, 2026
**Deployment Strategy**: Full Features (6-8 weeks)
**Target Date**: February 28, 2026
**Status**: DRAFT - Pending approval

---

## EXECUTIVE SUMMARY

### Scope
Deploy complete OPS Matrix Framework with all features including:
- Three-Way Match Enforcement (Priority #7)
- Auto-Escalation (Priority #8)
- Auto-List Accounts (Priority #9)
- Excel Import for Sale Orders (Priority #6 - Already complete)
- All 18 persona templates
- All 25 governance rule templates
- Complete security architecture
- IT Admin blindness
- Cost/Margin locking

### Timeline: 6-8 Weeks

```
Week 1-2: Installation & Core Testing (Priorities #6-9)
Week 3-4: Governance & Security Completion
Week 5-6: User Acceptance & Training
Week 7-8: Production Deployment & Monitoring
```

### Resources Required
- Development: 40-60 hours (RooCode + Claude)
- Testing: 20-30 hours (User Acceptance)
- Training: 10-15 hours (User training)
- Documentation: 10-15 hours

### Success Metrics
- Zero critical bugs in production
- All 18 personas functional
- 100% approval workflow success rate
- < 5 second response time for approval actions
- User satisfaction > 80%

---

## WEEK 1: INSTALLATION & CORE VALIDATION

### Week 1, Day 1-2: Module Installation & Verification

#### Objectives
1. Install new modules (Priorities #7, #8, #9) on VPS
2. Verify database schema updates
3. Confirm no breaking errors
4. Validate data files loaded

#### Tasks

**Pre-Installation Checklist**:
- [ ] Full database backup created
- [ ] Docker containers healthy
- [ ] Git repository synced to VPS
- [ ] Odoo service can be stopped/started
- [ ] Access to VPS terminal confirmed

**Installation Steps**:
```bash
# 1. Connect to VPS
ssh user@vps-address

# 2. Navigate to project
cd /opt/gemini_odoo19

# 3. Pull latest code
git pull origin main

# 4. Verify commit SHA
git log --oneline -5
# Should show: f72414c and 6d848fc (Priorities 7-9)

# 5. Stop Odoo
docker-compose stop

# 6. Backup database
docker exec postgres pg_dump -U odoo mz-db > backup_$(date +%Y%m%d_%H%M%S).sql

# 7. Upgrade module
docker exec gemini_odoo19 odoo \
  -c /etc/odoo/odoo.conf \
  -d mz-db \
  -u ops_matrix_core \
  --stop-after-init

# 8. Check logs for errors
tail -100 logs/odoo.log | grep -i error

# 9. Start Odoo
docker-compose start

# 10. Verify service running
curl http://localhost:8069/web/health
```

**Post-Installation Verification**:
- [ ] Odoo starts without errors
- [ ] Login successful
- [ ] Apps menu shows ops_matrix_core installed
- [ ] No error messages in browser console
- [ ] Database tables created:
  - ops_three_way_match
  - ops_report_template
  - ops_report_template_line
- [ ] Cron jobs scheduled:
  - Three-Way Match Recalculation (daily)
  - Auto-Escalation Check (hourly)

**Deliverables**:
- Installation log (saved to `logs/installation_2026-01-XX.log`)
- Verification checklist (completed)
- Rollback plan (if needed)

**Go/No-Go Decision Point**:
- **GO**: No critical errors, all tables created, Odoo stable
- **NO-GO**: Critical errors, missing tables, Odoo crashes → Rollback

---

### Week 1, Day 3-4: Priority #6 Validation (Excel Import)

#### Objectives
1. Verify Priority #6 (Excel Import) still works after upgrade
2. Test template download
3. Test validation rules
4. Test bulk import (100+ lines)

#### Test Scenarios

**Test 1: Template Download**
- [ ] Open Sale Order
- [ ] Click "Import from Excel" button
- [ ] Click "Download Template"
- [ ] Verify Excel file downloads
- [ ] Verify template has correct headers:
  - Product Code
  - Product Name
  - Quantity
  - Unit Price
  - Discount %
  - Tax
  - Description

**Test 2: Successful Import (Happy Path)**
- [ ] Fill template with 10 valid products
- [ ] Upload Excel file
- [ ] Click "Validate"
- [ ] Verify: "Validation successful" message
- [ ] Click "Import"
- [ ] Verify: 10 lines created in sale order
- [ ] Verify: Chatter message posted
- [ ] Verify: Totals calculated correctly

**Test 3: Validation Errors**
- [ ] Upload file with invalid product code
- [ ] Verify: Error message shows which row failed
- [ ] Verify: NO lines created (all-or-nothing)
- [ ] Fix error and re-upload
- [ ] Verify: Import succeeds

**Test 4: Performance Test**
- [ ] Create template with 100 lines
- [ ] Upload and import
- [ ] Measure time: Should be < 10 seconds
- [ ] Verify: All 100 lines created
- [ ] Verify: No timeout errors

**Test 5: Edge Cases**
- [ ] Empty file → Should show friendly error
- [ ] Missing required columns → Should show error
- [ ] Duplicate products → Should allow (qty adds up)
- [ ] Negative quantity → Should reject
- [ ] Invalid tax → Should reject

**Acceptance Criteria**:
- ✅ All 5 tests pass
- ✅ No errors in logs
- ✅ Import time < 10 seconds for 100 lines
- ✅ Chatter audit trail complete

**Deliverables**:
- Test results spreadsheet
- Screenshots of successful imports
- Performance metrics logged

---

### Week 1, Day 5: Priority #7 Testing (Three-Way Match)

#### Objectives
1. Test three-way match validation
2. Test tolerance settings
3. Test override workflow
4. Verify blocking behavior

#### Test Scenarios

**Test 1: Perfect Match (Happy Path)**
- [ ] Create PO: 100 units @ $10 each
- [ ] Receive: 100 units
- [ ] Create Vendor Bill: 100 units @ $10 each
- [ ] Expected: Match status = MATCHED
- [ ] Expected: Invoice validation succeeds
- [ ] Verify: Three-way match report shows match

**Test 2: Under-Billing (Should Pass)**
- [ ] Create PO: 100 units
- [ ] Receive: 100 units
- [ ] Create Vendor Bill: 90 units (under-billed)
- [ ] Expected: Match status = UNDER_BILLED
- [ ] Expected: Invoice validation succeeds (no blocking)
- [ ] Verify: Variance shown in report

**Test 3: Over-Billing (Should Block)**
- [ ] Create PO: 100 units
- [ ] Receive: 95 units
- [ ] Create Vendor Bill: 100 units (over-billed)
- [ ] Expected: Match status = OVER_BILLED
- [ ] Expected: Invoice validation BLOCKED
- [ ] Expected: Error message: "Cannot bill more than received"
- [ ] Verify: Invoice state = draft

**Test 4: No Receipt (Should Block)**
- [ ] Create PO: 100 units
- [ ] Do NOT receive
- [ ] Create Vendor Bill: 100 units
- [ ] Expected: Match status = NO_RECEIPT
- [ ] Expected: Invoice validation BLOCKED
- [ ] Expected: Error message: "No receipt found for this PO"

**Test 5: Tolerance Settings**
- [ ] Set company tolerance: 5%
- [ ] Create PO: 100 units
- [ ] Receive: 100 units
- [ ] Create Vendor Bill: 105 units (within 5% tolerance)
- [ ] Expected: Match status = MATCHED
- [ ] Expected: Invoice validation succeeds
- [ ] Create Vendor Bill: 106 units (exceeds 5% tolerance)
- [ ] Expected: Match status = OVER_BILLED
- [ ] Expected: Invoice validation BLOCKED

**Test 6: Override Workflow (Phase 2)**
- [ ] Block invoice due to over-billing
- [ ] Click "Request Override"
- [ ] Fill justification: "Vendor added shipping charges"
- [ ] Submit request
- [ ] Expected: Approval request created
- [ ] Expected: Assigned to Purchase Manager persona
- [ ] Login as Purchase Manager
- [ ] Open approval request
- [ ] Approve with comment
- [ ] Expected: Invoice unlocked
- [ ] Validate invoice → Should succeed
- [ ] Verify: Chatter shows full audit trail

**Test 7: Three-Way Match Report**
- [ ] Navigate to Three-Way Match report
- [ ] Filter by: Status = Over-Billed
- [ ] Verify: Shows all over-billed invoices
- [ ] Verify: Columns show:
  - PO Number
  - Ordered Qty
  - Received Qty
  - Billed Qty
  - Variance %
  - Match Status
  - Blocking Reason
- [ ] Export report to Excel
- [ ] Verify: Export includes all data

**Acceptance Criteria**:
- ✅ All blocking scenarios work correctly
- ✅ Tolerance calculation accurate
- ✅ Override workflow functional
- ✅ Audit trail complete
- ✅ Report shows accurate data

**Deliverables**:
- Test results matrix
- Screenshots of each scenario
- Three-way match report sample

---

## WEEK 2: ADVANCED FEATURES TESTING

### Week 2, Day 1-2: Priority #8 Testing (Auto-Escalation)

#### Objectives
1. Test escalation triggers
2. Test multi-level escalation
3. Test email notifications
4. Verify escalation history

#### Test Scenarios

**Test 1: Escalation Configuration**
- [ ] Open Governance Rule configuration
- [ ] Find "Sales Order > $5,000" rule
- [ ] Verify escalation settings:
  - Enable Auto-Escalation: True
  - Timeout: 24 hours
  - L1 Escalation: Branch Manager
  - L2 Escalation: BU Leader
  - L3 Escalation: CFO
- [ ] Save configuration

**Test 2: Level 0 → Level 1 Escalation**
- [ ] Create Sale Order: $6,000
- [ ] Submit for approval
- [ ] Expected: Approval request assigned to Sales Manager (L0)
- [ ] Wait OR manually set escalation_timeout_hours = 0.1 (6 minutes)
- [ ] Run cron manually:
  ```python
  self.env['ops.approval.request']._cron_escalate_overdue_approvals()
  ```
- [ ] Expected: Escalation level = 1
- [ ] Expected: Assigned to Branch Manager
- [ ] Expected: Email sent to Sales Manager (reminder)
- [ ] Expected: Email sent to Branch Manager (new task)
- [ ] Verify chatter: "Escalated to Level 1: Branch Manager"
- [ ] Verify escalation history updated

**Test 3: Level 1 → Level 2 Escalation**
- [ ] Continue from Test 2
- [ ] Do not approve as Branch Manager
- [ ] Run cron again after timeout
- [ ] Expected: Escalation level = 2
- [ ] Expected: Assigned to BU Leader
- [ ] Expected: Emails sent to Branch Manager + BU Leader
- [ ] Verify chatter: "Escalated to Level 2: BU Leader"

**Test 4: Level 2 → Level 3 Escalation**
- [ ] Continue from Test 3
- [ ] Do not approve as BU Leader
- [ ] Run cron again after timeout
- [ ] Expected: Escalation level = 3
- [ ] Expected: Assigned to CFO
- [ ] Expected: Emails sent
- [ ] Verify chatter: "Escalated to Level 3: CFO"

**Test 5: Final Approval After Escalation**
- [ ] Continue from Test 4
- [ ] Login as CFO
- [ ] Approve request
- [ ] Expected: Sale Order approved
- [ ] Expected: Final escalation history complete
- [ ] Verify: Timeline shows all escalations

**Test 6: Dashboard Filters**
- [ ] Open Approvals dashboard
- [ ] Filter: "Overdue Approvals"
- [ ] Verify: Shows only overdue items
- [ ] Filter: "Escalation Level = 1"
- [ ] Verify: Shows only L1 escalations
- [ ] Filter: "Escalation Level = 3"
- [ ] Verify: Shows only L3 escalations

**Test 7: Email Templates**
- [ ] Check inbox for escalation emails
- [ ] Verify reminder email contains:
  - Document number
  - Current approver name
  - Hours pending
  - Link to approve
- [ ] Verify new approver email contains:
  - Document number
  - Previous approver name
  - Escalation level
  - Link to approve

**Acceptance Criteria**:
- ✅ All escalation levels trigger correctly
- ✅ Timeouts calculated accurately
- ✅ Emails sent successfully
- ✅ Chatter audit trail complete
- ✅ Dashboard filters work

**Deliverables**:
- Escalation test matrix
- Email screenshots
- Escalation history report

---

### Week 2, Day 3-4: Priority #9 Testing (Auto-List Accounts)

#### Objectives
1. Test preloaded templates
2. Test template application
3. Test account filtering
4. Verify report generation

#### Test Scenarios

**Test 1: Verify Preloaded Templates**
- [ ] Navigate to: Accounting > Configuration > Report Templates
- [ ] Verify templates exist:
  - Standard P&L
  - Standard Balance Sheet
  - Standard Trial Balance
  - Standard Cash Flow
- [ ] Open "Standard P&L" template
- [ ] Verify sections:
  - REVENUE (account_type = income)
  - COST OF GOODS SOLD (account_type = expense, code LIKE '5%')
  - OPERATING EXPENSES (account_type = expense, code LIKE '6%')
  - OTHER INCOME/EXPENSE
- [ ] Verify: is_system_template = True (cannot edit)

**Test 2: Apply Standard P&L Template**
- [ ] Navigate to: Accounting > Reporting > Financial Reports
- [ ] Create new report: "Monthly P&L - January 2026"
- [ ] Select report type: Profit & Loss
- [ ] Click "Apply Template"
- [ ] Select "Standard P&L"
- [ ] Set date range: 2026-01-01 to 2026-01-31
- [ ] Click "Apply"
- [ ] Expected: Report auto-populated with:
  - Section: REVENUE
  - All income accounts listed (400x codes)
  - Section: COST OF GOODS SOLD
  - All COGS accounts listed (5000-5999)
  - Section: OPERATING EXPENSES
  - All OPEX accounts listed (6000-6999)
- [ ] Verify: Accounts sorted by code
- [ ] Verify: Section headers displayed
- [ ] Verify: Totals calculated per section

**Test 3: Apply Standard Balance Sheet Template**
- [ ] Create new report: "Balance Sheet - January 2026"
- [ ] Select report type: Balance Sheet
- [ ] Click "Apply Template"
- [ ] Select "Standard Balance Sheet"
- [ ] Set date: 2026-01-31
- [ ] Expected: Report shows:
  - Section: ASSETS (all asset accounts)
  - Section: LIABILITIES (all liability accounts)
  - Section: EQUITY (all equity accounts)
- [ ] Verify: Assets = Liabilities + Equity

**Test 4: Create Custom Template**
- [ ] Navigate to Report Templates
- [ ] Click "Create"
- [ ] Name: "Expense Analysis by Department"
- [ ] Report Type: Custom
- [ ] Add line:
  - Section: "Marketing Expenses"
  - Account Type: Expense
  - Code Pattern: "6100%" (marketing codes)
  - Sort: By Code
- [ ] Add line:
  - Section: "IT Expenses"
  - Account Type: Expense
  - Code Pattern: "6200%" (IT codes)
  - Sort: By Code
- [ ] Save template
- [ ] Apply to new report
- [ ] Verify: Only marketing and IT expenses shown
- [ ] Verify: Sections separate

**Test 5: Branch/BU Filtering**
- [ ] Apply Standard P&L template
- [ ] Add filter: Branch = "Main Branch"
- [ ] Expected: Only Main Branch accounts shown
- [ ] Change filter: BU = "Retail Division"
- [ ] Expected: Only Retail BU accounts shown
- [ ] Remove filters
- [ ] Expected: All accounts shown

**Test 6: Template Reusability**
- [ ] Create report "February P&L"
- [ ] Apply "Standard P&L" template
- [ ] Change date range to February
- [ ] Expected: Same account structure
- [ ] Expected: Different balances (February data)
- [ ] Compare with January P&L
- [ ] Verify: Same accounts, different amounts

**Test 7: Export to Excel**
- [ ] Open any report with template applied
- [ ] Click "Export to Excel"
- [ ] Verify Excel file includes:
  - Section headers
  - Account codes
  - Account names
  - Debit/Credit/Balance
  - Section subtotals
- [ ] Verify: Formatting preserved

**Acceptance Criteria**:
- ✅ All preloaded templates exist
- ✅ Template application works
- ✅ Account filtering accurate
- ✅ Custom templates functional
- ✅ Branch/BU filtering works
- ✅ Excel export successful

**Deliverables**:
- Sample reports (P&L, Balance Sheet, Custom)
- Template configuration screenshots
- Export samples (Excel)

---

### Week 2, Day 5: Integration Testing

#### Objectives
1. Test integration between Priorities #6-9
2. Verify data consistency
3. Test performance under load
4. Identify any conflicts

#### Integration Test Scenarios

**Test 1: Excel Import → Three-Way Match**
- [ ] Create PO using Excel import (50 lines)
- [ ] Receive all items
- [ ] Create vendor bill for same PO
- [ ] Expected: Three-way match validates successfully
- [ ] Verify: No conflicts between features

**Test 2: Approval Escalation → Three-Way Match Override**
- [ ] Block vendor bill due to over-billing
- [ ] Request override
- [ ] Let approval request escalate (don't approve)
- [ ] Expected: Escalation works normally
- [ ] Approve at L2 level
- [ ] Expected: Invoice unlocks
- [ ] Validate invoice
- [ ] Expected: Success

**Test 3: Auto-List Accounts → Report Generation**
- [ ] Apply P&L template
- [ ] Generate report for current month
- [ ] Verify: All transactions included
- [ ] Verify: Balances match trial balance
- [ ] Export to Excel
- [ ] Expected: No errors

**Test 4: Performance Test (Load Testing)**
- [ ] Create 10 Sale Orders simultaneously (different users)
- [ ] Import 100 lines each via Excel
- [ ] Submit all for approval
- [ ] Expected: No timeouts
- [ ] Expected: All imports succeed
- [ ] Expected: Response time < 5 seconds per action
- [ ] Check database performance:
  ```sql
  SELECT * FROM pg_stat_activity WHERE state = 'active';
  ```
- [ ] Verify: No long-running queries

**Test 5: Data Consistency Check**
- [ ] Run database integrity checks
- [ ] Verify: No orphaned records
- [ ] Verify: All foreign keys valid
- [ ] Verify: Computed fields accurate
- [ ] Check logs for any warnings

**Acceptance Criteria**:
- ✅ All features work together harmoniously
- ✅ No data conflicts
- ✅ Performance within acceptable limits
- ✅ No database integrity issues

**Go/No-Go Decision Point**:
- **GO**: All tests pass, performance good, no critical bugs
- **NO-GO**: Critical bugs found → Fix before proceeding to Week 3

**Deliverables**:
- Integration test report
- Performance metrics
- Database integrity report
- Bug list (if any)

---

## WEEK 3-4: GOVERNANCE & SECURITY COMPLETION

### Week 3, Day 1-3: Governance Rule Templates

#### Objectives
1. Verify all 25 governance rule templates exist
2. Test governance rule application
3. Complete any missing templates
4. Test approval workflows

#### Tasks

**Governance Rule Verification**:
- [ ] Sales Order Rules (5):
  1. Discount > 10% requires approval ✓
  2. Amount > $5,000 requires approval ✓
  3. Amount > $25,000 requires multi-level approval ✓
  4. Credit limit check required ✓
  5. Customer on hold blocks order ✓

- [ ] Margin Rules (2):
  1. Margin < 15% requires approval ✓
  2. Negative margin blocks sale ✓

- [ ] Purchase Order Rules (3):
  1. Amount > $10,000 requires approval ✓
  2. Amount > $50,000 requires multi-level approval ✓
  3. Vendor not approved blocks PO ✓

- [ ] Payment Rules (2):
  1. Payment > $5,000 requires approval ✓
  2. Multi-level approval for large payments ✓

- [ ] Inventory Rules (3):
  1. Inventory adjustment > 10% requires approval ✓
  2. Scrap > $1,000 requires approval ✓
  3. Negative stock blocks delivery ✓

- [ ] Invoice Rules (1):
  1. Credit note requires approval ✓

- [ ] Master Data Rules (4):
  1. Customer credit limit change requires approval ✓
  2. Customer credit hold requires approval ✓
  3. Vendor status change requires approval ✓
  4. Product cost change > 20% requires approval ✓

- [ ] User Management Rules (2):
  1. User creation requires approval ✓
  2. Permission change requires approval ✓

- [ ] Transfer Rules (2):
  1. Cross-BU transfer requires approval ✓
  2. Inter-branch transfer > $10k requires approval ✓

- [ ] Asset Rules (1):
  1. Asset disposal requires approval ✓

**Testing Each Rule**:
For EACH rule above:
- [ ] Trigger the condition
- [ ] Verify: Approval request created
- [ ] Verify: Correct persona assigned
- [ ] Verify: Document locked
- [ ] Approve request
- [ ] Verify: Document unlocks
- [ ] Complete transaction

**Missing Templates Development**:
If any templates are missing or incomplete:
- [ ] Create technical specification
- [ ] Develop template (RooCode)
- [ ] Test template
- [ ] Document template

**Acceptance Criteria**:
- ✅ All 25 governance rules exist and tested
- ✅ Approval workflows functional for each
- ✅ Document locking works consistently
- ✅ No conflicts between rules

**Deliverables**:
- Governance rule test matrix (25 x 5 tests = 125 test cases)
- Missing templates list (if any)
- New template specifications (if needed)

---

### Week 3, Day 4-5: Security Group Completion

#### Objectives
1. Verify all 19 security groups functional
2. Test access rights
3. Test record rules (IT Admin blindness)
4. Test field visibility

#### Security Group Tests

**Group 1: IT Admin Blindness**
- [ ] Login as IT Admin
- [ ] Navigate to Sales
- [ ] Expected: Menu visible
- [ ] Try to open Sale Order
- [ ] Expected: "No records found" OR "Access Denied"
- [ ] Navigate to Settings > Technical > Database Structure
- [ ] Expected: Can view/edit models
- [ ] Try to export data from Sale Order
- [ ] Expected: Blocked OR only metadata visible

**Group 2: Cost Visibility**
- [ ] Create user WITHOUT group_ops_see_cost
- [ ] Login as that user
- [ ] Open Product form
- [ ] Expected: Cost field INVISIBLE
- [ ] Grant group_ops_see_cost
- [ ] Refresh page
- [ ] Expected: Cost field VISIBLE

**Group 3: Margin Visibility**
- [ ] Create user WITHOUT group_ops_see_margin
- [ ] Login as that user
- [ ] Open Sale Order Line
- [ ] Expected: Margin field INVISIBLE
- [ ] Grant group_ops_see_margin
- [ ] Expected: Margin field VISIBLE

**Group 4: Segregation of Duties**
- [ ] Create Sale Order as Sales Rep
- [ ] Try to approve own order (if > threshold)
- [ ] Expected: BLOCKED with SoD violation message
- [ ] Request approval from manager
- [ ] Manager approves
- [ ] Expected: Success

**Group 5-19: Functional Groups**
For each functional group:
- [ ] Create user with ONLY that group
- [ ] Test menu visibility (should see relevant menus only)
- [ ] Test document access (should see relevant docs only)
- [ ] Test branch/BU isolation (should see own branch only)

**Record Rule Verification**:
```sql
-- Check record rules exist
SELECT name, model_id, domain_force 
FROM ir_rule 
WHERE name LIKE '%ops%it_admin%';

-- Should return 20+ rules
```

**Access Rights Verification**:
```sql
-- Check access rights
SELECT * FROM ir_model_access 
WHERE name LIKE '%ops%';

-- Should return 50+ access rules
```

**Acceptance Criteria**:
- ✅ IT Admin cannot see business data
- ✅ Cost/Margin locked by default
- ✅ Segregation of Duties enforced
- ✅ Branch/BU isolation works
- ✅ All 19 groups functional

**Deliverables**:
- Security test matrix
- Record rule verification report
- Access rights verification report
- Screenshots of blocked access

---

### Week 4, Day 1-3: Persona Testing

#### Objectives
1. Test all 18 personas end-to-end
2. Verify persona combinations
3. Test persona-specific workflows
4. Document persona capabilities

#### Persona Test Plan

For EACH of 18 personas:
1. Create test user
2. Assign persona
3. Login as user
4. Test typical workflows
5. Verify access boundaries
6. Document results

**Example: P06 - Sales Manager**
- [ ] Create user: "John Smith - Sales Manager"
- [ ] Assign persona: P06
- [ ] Login as John
- [ ] Expected menu access:
  - Sales (full access)
  - Customers (full access)
  - Products (read-only)
  - Reports (sales reports only)
- [ ] Test workflows:
  - Create Sale Order → Success
  - Approve Sale Order > $5k → Success
  - View cost prices → Success (has see_cost group)
  - View margins → Success (has see_margin group)
  - Create Purchase Order → BLOCKED
  - Approve expense → BLOCKED (not expense approver)
- [ ] Test branch isolation:
  - Create order for Main Branch → Success
  - Try to view Other Branch orders → BLOCKED
- [ ] Document capabilities in persona reference card

**Persona Combination Testing**:
- [ ] Create user with P06 (Sales Manager) + P10 (Sales Rep)
- [ ] Expected: Union of both persona capabilities
- [ ] Test: Should be able to create AND approve sales
- [ ] Verify: No SoD violations (can't approve own)

**Acceptance Criteria**:
- ✅ All 18 personas functional
- ✅ Access boundaries enforced
- ✅ Persona combinations work
- ✅ Reference cards complete

**Deliverables**:
- Persona test matrix (18 personas x 10 tests = 180 tests)
- Persona reference cards (18 one-pagers)
- Persona combination guide

---

### Week 4, Day 4-5: Data Isolation & Export Security

#### Objectives
1. Test branch data isolation
2. Test BU data isolation
3. Test export restrictions
4. Test sensitive field hiding

#### Data Isolation Tests

**Branch Isolation**:
- [ ] Create 3 branches: Main, Branch A, Branch B
- [ ] Create user assigned to Branch A only
- [ ] Create Sale Order in Branch A
- [ ] Login as Branch A user
- [ ] Expected: Can see Branch A order
- [ ] Try to view Branch B order
- [ ] Expected: BLOCKED or not visible in list
- [ ] Try to change order branch to Branch B
- [ ] Expected: BLOCKED

**BU Isolation**:
- [ ] Create 2 BUs: Retail, Wholesale
- [ ] Create user assigned to Retail BU only
- [ ] Create products in both BUs
- [ ] Login as Retail user
- [ ] Expected: Can see Retail products only
- [ ] Try to view Wholesale products
- [ ] Expected: Not in product list

**Export Restrictions**:
- [ ] Login as regular user (non-admin)
- [ ] Open Sale Order list (10 orders visible)
- [ ] Click Export
- [ ] Expected: ONLY visible orders exported (not all 1000 in DB)
- [ ] Verify exported file:
  - Should have 10 rows (not 1000)
  - Should exclude cost_price column
  - Should exclude margin column (unless user has access)
  - Should exclude bank account details
  - Should exclude supplier information (in sales context)

**Sensitive Field Hiding**:
- [ ] Login as Sales Rep
- [ ] Open Product form
- [ ] Expected fields HIDDEN:
  - Standard Price (cost)
  - Supplier list
  - Inventory valuation
- [ ] Expected fields VISIBLE:
  - Sales Price
  - Description
  - Stock quantity (no value)

**Export Logging**:
- [ ] Perform data export
- [ ] Check export log:
  ```python
  # Should log:
  # - User ID
  # - Model exported
  # - Number of records
  # - Timestamp
  # - Fields included
  ```
- [ ] Verify log entry created

**Acceptance Criteria**:
- ✅ Branch isolation complete
- ✅ BU isolation complete
- ✅ Export limited to viewed records
- ✅ Sensitive fields hidden
- ✅ Export logging functional

**Deliverables**:
- Data isolation test report
- Export security verification
- Sample export logs

---

## WEEK 5-6: USER ACCEPTANCE & TRAINING

### Week 5, Day 1-2: User Acceptance Testing (UAT)

#### Objectives
1. End users test the system
2. Collect feedback
3. Identify usability issues
4. Prioritize fixes

#### UAT Approach

**Participants**:
- 2-3 users per persona type (5-8 total users)
- Mix of technical and non-technical
- Different departments (Sales, Purchase, Finance)

**UAT Scenarios**:
Provide users with realistic scenarios:

1. **Sales Scenario**:
   - "Customer calls with urgent order for 50 items"
   - "Use Excel import to quickly create order"
   - "Check if customer has credit available"
   - "Submit order for approval (over $5k threshold)"
   - "Track approval status"

2. **Purchase Scenario**:
   - "Create purchase order for 100 units"
   - "Receive partial shipment (80 units)"
   - "Vendor sends invoice for 100 units"
   - "System blocks over-billing"
   - "Request override with justification"

3. **Finance Scenario**:
   - "Generate monthly P&L using template"
   - "Review revenue by branch"
   - "Export to Excel for board presentation"
   - "Create custom expense analysis report"

**UAT Checklist**:
For each scenario:
- [ ] User completes task independently (no help)
- [ ] Task completion time measured
- [ ] Number of clicks/steps counted
- [ ] User satisfaction rated (1-5 stars)
- [ ] Issues/confusion documented
- [ ] Feedback collected

**UAT Feedback Form**:
```
1. How easy was it to complete this task? (1-5)
2. Did the system behave as expected? (Y/N)
3. What confused you? (Free text)
4. What would make this better? (Free text)
5. Would you use this feature daily? (Y/N)
```

**Acceptance Criteria**:
- ✅ 80% of users rate tasks 4+ stars
- ✅ 90% task completion rate
- ✅ Average completion time meets targets
- ✅ No critical usability issues
- ✅ Users willing to adopt system

**Deliverables**:
- UAT report with user feedback
- Task completion metrics
- Usability issues log
- Recommended improvements

---

### Week 5, Day 3-5: Bug Fixes & Improvements

#### Objectives
1. Fix critical bugs from UAT
2. Implement quick wins
3. Improve user experience
4. Re-test fixes

#### Bug Triage Process

**Priority Levels**:
- **CRITICAL**: Blocks core functionality → Fix immediately
- **HIGH**: Major usability issue → Fix this week
- **MEDIUM**: Minor inconvenience → Fix if time allows
- **LOW**: Enhancement request → Backlog

**Example Bug Fixes**:

**Critical Bugs** (Must fix):
- [ ] "Excel import fails with special characters in product name"
  - Fix: Sanitize input, handle unicode
  - Test: Re-run Excel import with special chars
  - Deploy: Immediately

- [ ] "Three-way match blocks legitimate invoice"
  - Fix: Adjust tolerance calculation
  - Test: Re-run blocking scenarios
  - Deploy: Immediately

**High Priority** (Should fix):
- [ ] "Approval email doesn't link to correct document"
  - Fix: Update email template URL
  - Test: Send test approval email
  - Deploy: Before UAT Round 2

**Quick Wins** (Nice to have):
- [ ] "Add 'Download Template' button to Purchase Order too"
  - Effort: 30 minutes (reuse SO code)
  - Value: High (user requested)
  - Decision: Implement

- [ ] "Show pending approvals count on dashboard"
  - Effort: 1 hour
  - Value: High (visibility)
  - Decision: Implement

**Deployment Process**:
1. Fix bug in development
2. Test fix locally
3. Commit to GitHub
4. Deploy to VPS
5. Smoke test on VPS
6. Notify users of fix
7. Re-run UAT for affected scenarios

**Acceptance Criteria**:
- ✅ All CRITICAL bugs fixed
- ✅ 80% of HIGH bugs fixed
- ✅ Quick wins implemented
- ✅ Fixes tested and deployed
- ✅ No regressions introduced

**Deliverables**:
- Bug fix log
- Commit history
- Deployment notes
- Re-test results

---

### Week 6, Day 1-3: User Documentation

#### Objectives
1. Create user guides
2. Create admin documentation
3. Create quick reference cards
4. Create training materials

#### Documentation Deliverables

**1. Quick Start Guide** (5 pages)
- Welcome to OPS Framework
- How to login
- How to navigate menus
- How to get help
- Common tasks (create order, submit for approval)

**2. Feature User Guides** (10 pages each)

**Excel Import User Guide**:
- When to use Excel import
- How to download template
- How to fill template correctly
- How to upload and validate
- Common errors and solutions
- Tips for bulk orders

**Three-Way Match User Guide**:
- What is three-way match?
- How it protects your business
- What happens when invoices are blocked
- How to request override
- How to view match report

**Approval Workflow User Guide**:
- What triggers approvals
- How to check approval status
- How to approve/reject
- What is escalation?
- How to recall approval

**Financial Reporting User Guide**:
- How to apply report templates
- How to customize reports
- How to filter by branch/BU
- How to export to Excel
- How to schedule reports

**3. Admin Documentation** (20 pages)

**System Setup Guide**:
- Initial configuration checklist
- How to create branches
- How to create business units
- How to set company defaults
- How to configure governance rules

**User Management Guide**:
- How to create users
- How to assign personas
- How to combine personas
- How to grant cost/margin access
- How to handle user requests

**Security Configuration Guide**:
- IT Admin setup (blindness)
- Record rules configuration
- Access rights verification
- Export security settings
- Audit log review

**4. Persona Reference Cards** (18 one-pagers)

For EACH persona:
- Role description
- Typical responsibilities
- Menu access
- Document access
- Special permissions
- Workflow examples
- Common tasks
- Support contact

**5. Training Materials**

Presentation slides:
- Introduction to OPS Framework (10 slides)
- Excel Import Tutorial (15 slides)
- Approval Workflow Tutorial (15 slides)
- Financial Reporting Tutorial (20 slides)
- Security & Compliance (10 slides)

**6. Video Scripts** (Future - Optional)
- Excel Import Demo (3 minutes)
- Approval Workflow Demo (5 minutes)
- Report Templates Demo (5 minutes)
- IT Admin Setup Demo (10 minutes)

**Acceptance Criteria**:
- ✅ All user guides complete
- ✅ Admin documentation complete
- ✅ Persona cards ready
- ✅ Training materials ready
- ✅ Documents reviewed and approved

**Deliverables**:
- Quick Start Guide (PDF)
- 4 Feature User Guides (PDF)
- Admin Documentation (PDF)
- 18 Persona Reference Cards (PDF)
- Training Presentation (PPTX)
- Video Scripts (Markdown)

---

### Week 6, Day 4-5: User Training

#### Objectives
1. Train end users
2. Train administrators
3. Answer questions
4. Build confidence

#### Training Schedule

**Session 1: System Overview** (2 hours)
- Audience: All users
- Topics:
  - What is OPS Framework?
  - Why we're using it
  - Key features overview
  - How to get help
  - Q&A

**Session 2: Sales Team Training** (3 hours)
- Audience: Sales Managers, Sales Reps
- Topics:
  - Creating sale orders
  - Using Excel import
  - Checking credit limits
  - Approval workflows
  - Reporting
  - Hands-on practice
  - Q&A

**Session 3: Purchase Team Training** (3 hours)
- Audience: Purchase Managers, Purchase Officers
- Topics:
  - Creating purchase orders
  - Receiving goods
  - Three-way match
  - Override requests
  - Vendor management
  - Hands-on practice
  - Q&A

**Session 4: Finance Team Training** (4 hours)
- Audience: Finance Manager, Accountant, AR/AP Clerks
- Topics:
  - Financial reporting
  - Report templates
  - Branch/BU analysis
  - Three-way match verification
  - Approval workflows
  - PDC management
  - Hands-on practice
  - Q&A

**Session 5: Admin Training** (4 hours)
- Audience: IT Admin, System Admin
- Topics:
  - User management
  - Persona assignment
  - Security configuration
  - Governance rules
  - Troubleshooting
  - Backup/restore
  - Hands-on practice
  - Q&A

**Training Approach**:
1. Presentation (30%)
2. Live demo (30%)
3. Hands-on practice (30%)
4. Q&A (10%)

**Training Environment**:
- Use COPY of production database
- Create sample data for practice
- Users can experiment safely
- Mistakes are OK (it's training!)

**Training Materials**:
- Printed handouts (Quick Start + relevant guides)
- Persona reference cards
- Practice scenarios
- Cheat sheets
- Support contact card

**Post-Training Support**:
- Office hours: 2 hours/day for first week
- Email support: support@company.com
- Internal Slack/Teams channel
- Documentation library (shared drive)

**Acceptance Criteria**:
- ✅ All sessions completed
- ✅ 90%+ attendance
- ✅ Post-training quiz: 80%+ pass rate
- ✅ Users feel confident
- ✅ Questions answered

**Deliverables**:
- Training attendance logs
- Training evaluation forms
- Post-training quiz results
- Q&A summary document
- Support contact list

---

## WEEK 7-8: PRODUCTION DEPLOYMENT & MONITORING

### Week 7, Day 1-2: Production Readiness Review

#### Objectives
1. Final system validation
2. Performance tuning
3. Security audit
4. Backup/recovery test

#### Production Readiness Checklist

**Infrastructure**:
- [ ] VPS resources adequate (CPU, RAM, Disk)
- [ ] Database optimized (indexes, vacuum)
- [ ] Backup strategy configured
- [ ] Backup tested (can restore)
- [ ] Monitoring tools installed
- [ ] Alert rules configured
- [ ] SSL certificate valid
- [ ] Domain name configured
- [ ] Email SMTP configured and tested
- [ ] Firewall rules configured

**Application**:
- [ ] All modules installed and upgraded
- [ ] All features tested and working
- [ ] All bugs fixed (critical + high)
- [ ] Performance benchmarks met
- [ ] No errors in logs
- [ ] Cron jobs running
- [ ] Email templates working
- [ ] Reports generating correctly
- [ ] Exports working
- [ ] Mobile responsive (if applicable)

**Data**:
- [ ] Chart of Accounts loaded
- [ ] Branches created
- [ ] Business Units created
- [ ] Users created and assigned personas
- [ ] Governance rules configured
- [ ] SLA templates configured
- [ ] Report templates loaded
- [ ] Sample data tested (optional)
- [ ] Data migration complete (if applicable)
- [ ] Data validation complete

**Security**:
- [ ] IT Admin blindness verified
- [ ] Cost/Margin locking verified
- [ ] Segregation of Duties enforced
- [ ] Branch/BU isolation verified
- [ ] Export restrictions verified
- [ ] Password policy enforced
- [ ] Two-factor authentication (optional)
- [ ] Audit logging enabled
- [ ] Security groups verified
- [ ] Record rules verified

**Documentation**:
- [ ] User guides complete
- [ ] Admin documentation complete
- [ ] Persona reference cards ready
- [ ] Training materials ready
- [ ] API documentation (if applicable)
- [ ] Troubleshooting guide ready
- [ ] Support runbook ready

**Training & Support**:
- [ ] All users trained
- [ ] Admin trained
- [ ] Support team ready
- [ ] Escalation process defined
- [ ] Office hours scheduled
- [ ] Help desk tickets system ready

**Performance Benchmarks**:
- [ ] Login: < 2 seconds
- [ ] Sale Order creation: < 3 seconds
- [ ] Excel import (100 lines): < 10 seconds
- [ ] Approval action: < 5 seconds
- [ ] Report generation: < 5 seconds
- [ ] Dashboard load: < 3 seconds
- [ ] Database queries: < 1 second
- [ ] Concurrent users: 20+ without slowdown

**Go/No-Go Decision Criteria**:

**GO Criteria** (All must be YES):
- ✅ All CRITICAL items checked
- ✅ All HIGH priority bugs fixed
- ✅ Performance benchmarks met
- ✅ Security audit passed
- ✅ Backup/restore tested successfully
- ✅ Users trained and confident
- ✅ Support team ready

**NO-GO Criteria** (Any is NO-GO):
- ❌ Critical bugs remaining
- ❌ Performance issues
- ❌ Security vulnerabilities
- ❌ Backup/restore failed
- ❌ Users not trained
- ❌ Support team not ready

**Acceptance Criteria**:
- ✅ All checklist items completed
- ✅ Go/No-Go decision made
- ✅ Production deployment approved

**Deliverables**:
- Production readiness report
- Go/No-Go decision document
- Final deployment plan

---

### Week 7, Day 3: Production Deployment

#### Objectives
1. Deploy to production
2. Cutover from old system
3. Verify everything works
4. Minimal downtime

#### Deployment Timeline

**Pre-Deployment** (Day before):
- [ ] Announce deployment: "System maintenance Saturday 8 AM - 12 PM"
- [ ] Send reminder emails to all users
- [ ] Prepare rollback plan
- [ ] Backup current production database
- [ ] Stage deployment scripts
- [ ] Test deployment in staging environment

**Deployment Day** (Saturday, Low traffic day):

**8:00 AM - Deployment Start**
- [ ] Put system in maintenance mode
- [ ] Display: "System upgrade in progress, back online at 12 PM"
- [ ] Stop all Odoo services
- [ ] Final database backup

**8:30 AM - Code Deployment**
- [ ] Pull latest code from GitHub (main branch)
- [ ] Verify commit SHA matches approved version
- [ ] Update file permissions
- [ ] Clear Python cache

**9:00 AM - Database Upgrade**
- [ ] Run module upgrade:
  ```bash
  docker exec gemini_odoo19 odoo \
    -c /etc/odoo/odoo.conf \
    -d mz-db \
    -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting \
    --stop-after-init
  ```
- [ ] Check upgrade log for errors
- [ ] Verify database integrity

**9:30 AM - Data Migration** (if needed)
- [ ] Run data migration scripts
- [ ] Verify data migration
- [ ] Check data consistency

**10:00 AM - Service Start**
- [ ] Start Odoo services
- [ ] Verify services running
- [ ] Check logs for errors

**10:30 AM - Smoke Testing**
- [ ] Login as admin
- [ ] Test critical workflows:
  - Create Sale Order → Success
  - Submit for approval → Success
  - Approve request → Success
  - Excel import → Success
  - Three-way match → Success
  - Generate report → Success
- [ ] Test as regular user
- [ ] Verify all features working

**11:00 AM - User Acceptance**
- [ ] Invite key users to test
- [ ] Users verify their workflows
- [ ] Collect immediate feedback
- [ ] Fix any critical issues

**11:30 AM - Go Live**
- [ ] Remove maintenance mode
- [ ] Send "System Online" announcement
- [ ] Monitor error logs
- [ ] Monitor user activity
- [ ] Stand by for support requests

**12:00 PM - Deployment Complete**
- [ ] System fully operational
- [ ] Users can access
- [ ] Support team on standby
- [ ] Monitoring active

**Post-Deployment** (Next 4 hours):
- [ ] Monitor error logs continuously
- [ ] Monitor performance metrics
- [ ] Monitor user activity
- [ ] Respond to support requests immediately
- [ ] Document any issues

**Rollback Plan** (If deployment fails):
1. Stop Odoo services
2. Restore database backup
3. Revert code to previous version
4. Restart services
5. Verify system operational
6. Notify users of rollback
7. Investigate failure
8. Reschedule deployment

**Acceptance Criteria**:
- ✅ Deployment completed within 4-hour window
- ✅ All critical features working
- ✅ No errors in logs
- ✅ Users can login and work
- ✅ No rollback needed

**Deliverables**:
- Deployment log
- Smoke test results
- Performance metrics
- User feedback
- Issues log (if any)

---

### Week 7, Day 4-5 & Week 8: Post-Deployment Monitoring

#### Objectives
1. Monitor system stability
2. Address production issues
3. Optimize performance
4. Support users

#### Monitoring Plan

**Week 7, Day 4-5 (First 2 days - CRITICAL)**:

**24/7 Monitoring**:
- [ ] Error logs checked every 2 hours
- [ ] Performance metrics checked every 4 hours
- [ ] User support requests monitored continuously
- [ ] On-call support available

**Daily Tasks**:
- [ ] Review error logs (morning + evening)
- [ ] Check performance metrics
- [ ] Review user activity
- [ ] Respond to all support tickets
- [ ] Document issues and resolutions
- [ ] Deploy hotfixes if needed

**Week 8 (Days 1-5 - Stabilization Week)**:

**Monitoring Frequency**:
- Error logs: Every 4 hours → Daily
- Performance: Every 8 hours → Daily
- Support: Business hours only (8 AM - 6 PM)

**Daily Tasks**:
- [ ] Morning health check (15 minutes)
  - Review overnight logs
  - Check database size
  - Check disk space
  - Check backup status
- [ ] Afternoon review (30 minutes)
  - Review user activity
  - Check support tickets
  - Review performance trends
- [ ] Evening wrap-up (15 minutes)
  - Document day's issues
  - Plan next day's tasks

**Key Metrics to Monitor**:

**System Metrics**:
- CPU usage (should be < 70%)
- Memory usage (should be < 80%)
- Disk space (should have > 20% free)
- Database size (growth rate)
- Network traffic

**Application Metrics**:
- Active users (concurrent)
- Requests per minute
- Average response time
- Error rate (should be < 1%)
- Failed logins

**Business Metrics**:
- Sale Orders created
- Approval requests processed
- Excel imports performed
- Three-way matches validated
- Reports generated
- Escalations triggered

**User Adoption Metrics**:
- Daily active users
- Feature usage (Excel import, Reports, etc.)
- Support ticket volume
- User satisfaction (survey)

**Monitoring Tools**:

**Log Monitoring**:
```bash
# Real-time error monitoring
tail -f logs/odoo.log | grep -i error

# Error count
grep -c "ERROR" logs/odoo.log

# Recent errors
tail -100 logs/odoo.log | grep "ERROR"
```

**Performance Monitoring**:
```sql
-- Slow queries
SELECT query, calls, total_time/calls as avg_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Active connections
SELECT count(*) FROM pg_stat_activity 
WHERE state = 'active';

-- Database size
SELECT pg_size_pretty(pg_database_size('mz-db'));
```

**User Activity**:
```sql
-- Daily logins
SELECT date(create_date), count(*)
FROM res_users_log
WHERE create_date >= CURRENT_DATE - 7
GROUP BY date(create_date);

-- Feature usage
SELECT model, count(*)
FROM mail_message
WHERE create_date >= CURRENT_DATE - 7
GROUP BY model;
```

**Issue Response Plan**:

**Critical Issues** (System down, data loss):
- Response time: Immediate (< 15 minutes)
- Escalation: System Admin + Developer
- Communication: Email + SMS to all users
- Resolution target: < 2 hours

**High Priority** (Feature broken, blocking users):
- Response time: < 1 hour
- Escalation: Support team + Developer
- Communication: Email to affected users
- Resolution target: < 4 hours

**Medium Priority** (Minor bug, workaround exists):
- Response time: < 4 hours
- Escalation: Support team
- Communication: Support ticket update
- Resolution target: < 24 hours

**Low Priority** (Enhancement request):
- Response time: < 24 hours
- Escalation: None
- Communication: Support ticket update
- Resolution target: Next release

**Performance Optimization**:

If performance issues detected:
- [ ] Identify slow queries (pg_stat_statements)
- [ ] Add database indexes where needed
- [ ] Optimize computed fields
- [ ] Add caching where appropriate
- [ ] Review record rule complexity
- [ ] Consider database tuning (shared_buffers, etc.)

**User Support**:

**Office Hours** (Week 8):
- Monday-Friday: 9 AM - 12 PM, 2 PM - 5 PM
- Support channel: Slack/Teams
- Email: support@company.com
- Phone: Emergency only

**Support Ticket Categories**:
1. How do I...? (Training issue)
2. System not working (Bug)
3. Feature request (Enhancement)
4. Access issue (Security/Permissions)

**Support Response SLA**:
- Critical: < 1 hour
- High: < 4 hours
- Medium: < 1 day
- Low: < 3 days

**Acceptance Criteria**:
- ✅ System stable (uptime > 99.5%)
- ✅ Error rate < 1%
- ✅ Performance meets benchmarks
- ✅ All support tickets resolved or tracked
- ✅ Users productive
- ✅ No critical issues outstanding

**Deliverables**:
- Daily monitoring reports (Week 8)
- Issue log with resolutions
- Performance optimization report
- User feedback summary
- Lessons learned document

---

## GOVERNANCE COMPLETION PLAN

### Missing Governance Components

Based on TODO_MASTER.md analysis:

#### 1. Governance Rule Templates - Status

**Complete** (25/25 rules exist in specs):
- ✅ Sales Order rules (5)
- ✅ Margin rules (2)
- ✅ Purchase Order rules (3)
- ✅ Payment rules (2)
- ✅ Inventory rules (3)
- ✅ Invoice rules (1)
- ✅ Master Data rules (4)
- ✅ User Management rules (2)
- ✅ Transfer rules (2)
- ✅ Asset rules (1)

**Action Required**: Verify all 25 implemented in code (Week 3)

#### 2. SLA Templates

**Status**: Model exists, templates needed

**Templates to Create**:
1. **Sales Order SLA**
   - Quote response: 24 hours
   - Order confirmation: 4 hours
   - Delivery: 3 days

2. **Purchase Order SLA**
   - PO creation: 24 hours after requisition
   - PO approval: 48 hours
   - Receipt processing: Same day

3. **Invoice Processing SLA**
   - Invoice entry: 24 hours after receipt
   - Invoice approval: 48 hours
   - Payment: 30/60/90 days per terms

4. **Approval Request SLA**
   - L0 approval: 24 hours
   - L1 approval: 24 hours
   - L2 approval: 48 hours
   - L3 approval: 48 hours

**Implementation**:
- Create data XML file: `ops_sla_templates.xml`
- Set all as archived by default
- Include in module data files
- Test SLA tracking

#### 3. Approval Workflow Templates

**Status**: Engine exists, templates needed

**Templates to Create**:
1. **Single-Level Approval**
   - Approver: Immediate manager
   - Timeout: 24 hours
   - Escalation: To manager's manager

2. **Multi-Level Approval** (Amount-based)
   - $0-$5k: Branch Manager
   - $5k-$25k: BU Leader
   - $25k+: CFO

3. **Committee Approval**
   - Requires 2 of 3 approvers
   - Use case: Asset disposal, credit limit increase

**Implementation**:
- Enhance governance rule model if needed
- Create workflow templates
- Test each template

#### 4. Security Group Assignments

**Status**: Groups exist, assignments needed

**Persona to Group Mapping**:
Create comprehensive mapping document showing:
- Which security groups each persona gets
- Rationale for each assignment
- Conflicts/dependencies

**Example**:
```
P06 - Sales Manager:
- group_ops_user (base)
- group_ops_manager (branch management)
- group_sale_manager (Odoo sales manager)
- group_ops_see_cost (cost visibility)
- group_ops_see_margin (margin visibility)
- group_ops_sales_manager (OPS-specific sales)
```

**Implementation**:
- Document all 18 personas
- Create persona creation wizard (auto-assigns groups)
- Test each persona

#### 5. Preloaded Chart of Accounts

**Status**: TODO

**Requirements**:
- FIFO inventory valuation
- Direct costing method
- Multi-currency support
- Branch/BU compatible

**Account Structure**:
```
1000-1999: Assets
2000-2999: Liabilities
3000-3999: Equity
4000-4999: Revenue
5000-5999: Cost of Goods Sold
6000-6999: Operating Expenses
7000-7999: Other Income/Expense
8000-8999: Tax Accounts
```

**Implementation**:
- Create account.account.template records
- Create account.chart.template
- Include in module data files
- Test installation

---

## DOCUMENTATION REQUIREMENTS

### Technical Documentation

**Already Complete**:
- ✅ Core Technical Spec
- ✅ Accounting Technical Spec
- ✅ Reporting Technical Spec
- ✅ Priority #6 Spec (Excel Import)
- ✅ Priority #7 Spec (Three-Way Match)
- ✅ Priority #8 Spec (Auto-Escalation)
- ✅ Priority #9 Spec (Auto-List Accounts)
- ✅ Project Structure
- ✅ Development Workflow

**To Create**:

1. **Security Groups Reference** (Week 3)
   - All 19 groups documented
   - Purpose of each group
   - Which personas get which groups
   - Dependencies between groups

2. **Record Rules Reference** (Week 3)
   - All record rules documented
   - Model, domain, groups affected
   - IT Admin blindness rules
   - Branch/BU isolation rules

3. **API Reference** (Optional)
   - External API endpoints
   - Authentication
   - Request/response formats
   - Rate limits
   - Examples

4. **Developer Extension Guide** (Optional)
   - How to extend OPS Framework
   - Custom modules
   - Best practices
   - Examples

### User Documentation

**To Create** (Week 6):

1. Quick Start Guide (5 pages)
2. Excel Import User Guide (10 pages)
3. Three-Way Match User Guide (10 pages)
4. Approval Workflow User Guide (10 pages)
5. Financial Reporting User Guide (15 pages)
6. Admin Setup Guide (20 pages)
7. User Management Guide (15 pages)
8. Security Configuration Guide (15 pages)
9. 18 Persona Reference Cards (1 page each)
10. Training Presentation (60 slides)

**Total**: ~120 pages + 60 slides

**Estimated Effort**: 10-15 hours

---

## PRODUCTION READINESS CHECKLIST

### Infrastructure Requirements

**VPS Specifications**:
- CPU: 4 cores minimum (8 recommended)
- RAM: 8 GB minimum (16 GB recommended)
- Disk: 100 GB SSD minimum
- Network: 100 Mbps minimum
- OS: Ubuntu 22.04 LTS or later

**Docker Configuration**:
- Docker version: 20.10+
- Docker Compose version: 2.0+
- Containers:
  - Odoo 19 Community
  - PostgreSQL 15
  - Nginx (reverse proxy)

**Database Configuration**:
```
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 64MB
max_connections = 100
```

**Odoo Configuration**:
```
[options]
db_host = postgres
db_port = 5432
db_user = odoo
db_password = <secure_password>
addons_path = /opt/gemini_odoo19/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
logfile = /var/log/odoo/odoo.log
log_level = info
workers = 4
max_cron_threads = 2
limit_time_cpu = 600
limit_time_real = 1200
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
```

**Backup Strategy**:

**Daily Backups**:
- Database: Full backup at 2 AM
- Files: Backup attachments/data_dir
- Retention: 7 days
- Location: External storage (S3/Backblaze)

**Weekly Backups**:
- Full system backup
- Retention: 4 weeks

**Monthly Backups**:
- Archive backup
- Retention: 12 months

**Backup Script**:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups

# Database backup
docker exec postgres pg_dump -U odoo mz-db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Filestore backup
tar -czf $BACKUP_DIR/filestore_$DATE.tar.gz /var/lib/odoo/filestore

# Upload to S3 (example)
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://mybucket/backups/
aws s3 cp $BACKUP_DIR/filestore_$DATE.tar.gz s3://mybucket/backups/

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "filestore_*.tar.gz" -mtime +7 -delete
```

**Recovery Procedures**:

**Database Restore**:
```bash
# Stop Odoo
docker-compose stop odoo

# Drop current database
docker exec postgres dropdb -U odoo mz-db

# Create new database
docker exec postgres createdb -U odoo mz-db

# Restore backup
gunzip < db_20260204_020000.sql.gz | docker exec -i postgres psql -U odoo mz-db

# Start Odoo
docker-compose start odoo
```

**Filestore Restore**:
```bash
# Stop Odoo
docker-compose stop odoo

# Restore filestore
tar -xzf filestore_20260204_020000.tar.gz -C /var/lib/odoo/

# Fix permissions
chown -R odoo:odoo /var/lib/odoo/filestore

# Start Odoo
docker-compose start odoo
```

**Monitoring Setup**:

**System Monitoring** (Prometheus/Grafana):
- CPU usage
- Memory usage
- Disk I/O
- Network traffic
- Container health

**Application Monitoring** (Odoo logs):
- Error rate
- Response time
- Active sessions
- Database connections
- Cron job status

**Alert Rules**:
- CPU > 80% for 5 minutes → Alert
- Memory > 90% → Alert
- Disk space < 10% → Alert
- Error rate > 5% → Alert
- Odoo container down → Critical Alert
- Database container down → Critical Alert

**Security Configuration**:

**Firewall** (UFW):
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

**SSL Certificate** (Let's Encrypt):
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (cron)
0 0 1 * * certbot renew --quiet
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /longpolling {
        proxy_pass http://localhost:8072;
    }
}
```

---

## ROOCODE KICKSTART INSTRUCTIONS

See separate file: `ROOCODE_KICKSTART_PROMPT.md`

---

## SUCCESS METRICS

### Technical Metrics

**System Performance**:
- Uptime: > 99.5%
- Average response time: < 3 seconds
- Error rate: < 1%
- Database query time: < 1 second
- Concurrent users supported: 20+

**Feature Adoption**:
- Excel Import usage: > 50% of sales orders
- Three-Way Match: 100% of purchase invoices validated
- Auto-Escalation: < 5% of approvals escalated
- Report Templates: > 80% of reports use templates

### Business Metrics

**Efficiency Gains**:
- Sale Order entry time: 50 min → 5 sec (for bulk orders)
- Invoice validation time: 10 min → 2 min (automated matching)
- Report generation time: 30 min → 2 min (templates)
- Approval processing time: 2 days → 8 hours (auto-escalation)

**Compliance**:
- Three-way match compliance: 100%
- Segregation of duties violations: 0
- IT Admin data access violations: 0
- Unapproved transactions: 0

**User Satisfaction**:
- Overall satisfaction: > 80%
- Would recommend: > 80%
- Training effectiveness: > 85%
- Support satisfaction: > 90%

### Risk Reduction

**Before OPS Framework**:
- Manual invoice matching: High risk of overpayment
- No approval enforcement: Risk of unauthorized transactions
- No IT admin controls: Risk of data breach
- No segregation of duties: Risk of fraud

**After OPS Framework**:
- Automated three-way match: Overpayment risk eliminated
- Enforced approvals: Unauthorized transactions blocked
- IT admin blindness: Data breach risk reduced
- SoD enforcement: Fraud risk significantly reduced

---

## PROJECT TIMELINE SUMMARY

```
WEEK 1: Installation & Core Testing
├── Day 1-2: Module installation, verification
├── Day 3-4: Priority #6 validation (Excel Import)
└── Day 5: Priority #7 testing (Three-Way Match)

WEEK 2: Advanced Features Testing
├── Day 1-2: Priority #8 testing (Auto-Escalation)
├── Day 3-4: Priority #9 testing (Auto-List Accounts)
└── Day 5: Integration testing

WEEK 3: Governance & Security (Part 1)
├── Day 1-3: Governance rule templates (all 25)
└── Day 4-5: Security group completion

WEEK 4: Governance & Security (Part 2)
├── Day 1-3: Persona testing (all 18)
└── Day 4-5: Data isolation & export security

WEEK 5: User Acceptance & Training Prep
├── Day 1-2: User acceptance testing (UAT)
└── Day 3-5: Bug fixes & improvements

WEEK 6: Documentation & Training
├── Day 1-3: User documentation creation
└── Day 4-5: User training sessions

WEEK 7: Production Deployment
├── Day 1-2: Production readiness review
├── Day 3: PRODUCTION DEPLOYMENT
└── Day 4-5: Initial monitoring (critical period)

WEEK 8: Stabilization & Handover
└── Day 1-5: Post-deployment monitoring & optimization
```

---

## RISK MANAGEMENT

### Identified Risks

**Technical Risks**:

1. **Database Performance**
   - Risk: Slow queries under load
   - Mitigation: Performance testing (Week 2), indexing, query optimization
   - Contingency: Rollback, schedule maintenance window

2. **Module Upgrade Failures**
   - Risk: Upgrade fails, database corrupted
   - Mitigation: Test in staging first, full backup before upgrade
   - Contingency: Restore from backup, fix issues, retry

3. **Email Delivery Issues**
   - Risk: Approval/escalation emails not sent
   - Mitigation: Test SMTP configuration (Week 1)
   - Contingency: Use alternative notification method (in-app)

**User Adoption Risks**:

1. **Resistance to Change**
   - Risk: Users prefer old system
   - Mitigation: Effective training (Week 6), show benefits
   - Contingency: Executive sponsorship, mandatory adoption

2. **Insufficient Training**
   - Risk: Users don't know how to use system
   - Mitigation: Comprehensive training (Week 6), documentation
   - Contingency: Extended support period, office hours

3. **Support Overwhelm**
   - Risk: Too many support requests
   - Mitigation: Good documentation, effective training
   - Contingency: Additional support staff, extended office hours

**Business Risks**:

1. **Business Disruption**
   - Risk: Downtime during deployment
   - Mitigation: Deploy on weekend, minimize downtime
   - Contingency: Rollback plan ready

2. **Data Migration Issues**
   - Risk: Data loss or corruption
   - Mitigation: Thorough testing, backups
   - Contingency: Restore from backup

3. **Compliance Violations**
   - Risk: Security gaps, data leaks
   - Mitigation: Security audit (Week 7), testing
   - Contingency: Immediate fix, incident response plan

---

## CHANGE MANAGEMENT

### Communication Plan

**Week 1-2**: "Testing Phase"
- Audience: Key stakeholders
- Message: "We're testing the new system"
- Channel: Email update

**Week 3-4**: "Preparation Phase"
- Audience: All users
- Message: "New system coming soon, training scheduled"
- Channel: Email + team meetings

**Week 5**: "UAT Phase"
- Audience: UAT participants + all users
- Message: "Help us test the new system"
- Channel: Email + internal announcement

**Week 6**: "Training Phase"
- Audience: All users
- Message: "Training sessions this week, please attend"
- Channel: Email + calendar invites + posters

**Week 7**: "Go-Live Phase"
- Audience: All users
- Message: "New system goes live Saturday, here's what to expect"
- Channel: Email + SMS + team meetings

**Week 8**: "Support Phase"
- Audience: All users
- Message: "We're here to help, office hours available"
- Channel: Email + Slack/Teams + daily tips

### Stakeholder Management

**Executive Sponsors**:
- Weekly status updates
- Go/No-Go decision involvement
- Budget approval (if needed)
- Conflict resolution

**Department Heads**:
- Bi-weekly updates
- UAT participation
- Training coordination
- User adoption enforcement

**End Users**:
- Training attendance
- UAT participation (selected users)
- Feedback provision
- System usage

**IT Team**:
- Technical implementation
- Infrastructure management
- Backup/recovery
- Monitoring

---

## LESSONS LEARNED & CONTINUOUS IMPROVEMENT

### Post-Implementation Review

**Week 9** (After go-live):
- Conduct retrospective meeting
- Document what went well
- Document what could be improved
- Create action items for future

**Review Questions**:
1. Did we meet timeline? If not, why?
2. Did we meet budget? If not, why?
3. Were users satisfied? What feedback did we get?
4. What technical issues did we face?
5. What would we do differently next time?
6. What should we continue doing?

**Continuous Improvement**:
- Monthly review of system performance
- Quarterly feature enhancement review
- Annual security audit
- User feedback surveys (quarterly)

---

## APPENDICES

### Appendix A: Glossary

- **BU**: Business Unit
- **COGS**: Cost of Goods Sold
- **P&L**: Profit & Loss
- **PO**: Purchase Order
- **SLA**: Service Level Agreement
- **SoD**: Segregation of Duties
- **UAT**: User Acceptance Testing
- **VPS**: Virtual Private Server

### Appendix B: Contact List

**Project Team**:
- Project Manager: [Name, Email, Phone]
- Technical Lead: [Name, Email, Phone]
- Business Analyst: [Name, Email, Phone]

**Support Team**:
- Support Email: support@company.com
- Support Slack: #ops-framework-support
- Emergency: [Phone]

**Escalation**:
- Level 1: Support Team
- Level 2: Technical Lead
- Level 3: Project Manager
- Level 4: CTO/CFO

### Appendix C: References

**Documentation**:
- OPS Framework User Experience v1.2
- Core Technical Specification
- Accounting Technical Specification
- Reporting Technical Specification
- Priority #6-9 Specifications
- TODO Master

**External Resources**:
- Odoo Documentation: https://www.odoo.com/documentation/19.0/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Docker Documentation: https://docs.docker.com/

---

## VERSION HISTORY

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-04 | Initial implementation plan created | Claude |

---

**END OF IMPLEMENTATION PLAN**

**Next Step**: Review and approve plan, then proceed to ROOCODE_KICKSTART_PROMPT.md
