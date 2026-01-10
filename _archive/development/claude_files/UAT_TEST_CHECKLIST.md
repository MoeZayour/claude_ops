# OPS Matrix Framework - UAT Test Checklist

**Tester**: Moe Zayour  
**Date**: January 4, 2026  
**Version**: 19.0.1.3  
**Test Environment**: https://dev.mz-im.com/  

---

## 📋 PRE-TEST SETUP

### Step 0: Seed Test Data

```bash
# On VPS, run the seeding script
cd /opt/gemini_odoo19
bash addons/ops_matrix_core/data/execute_seeding.sh
```

**Expected Output**:
```
✅ Transaction committed successfully
Summary:
  - Company: Test Trading LLC
  - Business Units: 2
  - Branches: 2
  - Customers: 3
  - Vendors: 2
  - Products: 5
  - Users: 5
  - Sales Orders: 3
  - Purchase Orders: 3
  - Vendor Bills: 2
```

**✅ PASS / ❌ FAIL**: _______

**Notes**: _______________________________________________

---

## 🎯 PRIORITY #7: THREE-WAY MATCH ENFORCEMENT

### Test 7.1: Perfect Match Scenario

**Login**: admin / admin  
**Navigate**: Purchase > Orders  

**Test Steps**:
1. Open PO with reference containing "PO00001" (100 Laptops)
2. Verify Receipt is validated (100 units received)
3. Click "Create Bill" or find existing bill
4. Verify Bill shows:
   - Quantity: 100
   - Unit Price: 2,100 AED
   - Total: 210,000 AED
5. Click "Confirm" on the bill
6. Check "Three-Way Match" smart button or report

**Expected Results**:
- ✅ Bill validates without error
- ✅ Match status = "MATCHED" (or similar)
- ✅ No blocking message
- ✅ Bill state = Posted/Confirmed

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 7.2: Partial Receipt - Under-billing (Should Pass)

**Navigate**: Purchase > Orders  

**Test Steps**:
1. Open PO with reference containing "PO00002" (50 Monitors ordered)
2. Verify Receipt shows 30 units received (partial)
3. Check existing bill or create new bill
4. Bill should be for 30 units (matches receipt)
5. Click "Confirm" on the bill

**Expected Results**:
- ✅ Bill validates (30 ≤ 30 received)
- ✅ No over-billing error
- ✅ Bill state = Posted

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 7.3: Over-billing Scenario (Should Block)

**Navigate**: Purchase > Orders  

**Test Steps**:
1. Open PO with reference containing "PO00003" (100 Keyboards)
2. Verify Receipt is validated (100 units received)
3. Click "Create Bill" 
4. Manually change bill quantity to **120 units** (20 more than received)
5. Try to confirm the bill

**Expected Results**:
- ❌ Bill validation BLOCKS
- ❌ Error message appears: "Cannot bill more than received quantity"
- ❌ Bill remains in Draft state
- ✅ Three-Way Match report shows MISMATCH

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 7.4: Override Wizard (If Authorized)

**Prerequisites**: Must have override permission  

**Test Steps**:
1. From blocked bill in Test 7.3
2. Look for "Override" or "Force Approve" button/wizard
3. Click override option
4. Enter reason: "Supplier agreed to free bonus units"
5. Submit override

**Expected Results**:
- ✅ Override wizard appears
- ✅ Reason field is mandatory
- ✅ After override, bill posts successfully
- ✅ Override logged in chatter with reason

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

## 🚀 PRIORITY #8: AUTO-ESCALATION

### Test 8.1: View Approval Requests

**Navigate**: Operations > Approvals > Approval Requests  
(or similar menu)

**Test Steps**:
1. Find approval request for large Sales Order (SO00002)
2. Check current approver
3. Check state (should be "Pending")
4. Note the "Created" timestamp

**Expected Results**:
- ✅ Approval request exists
- ✅ Current approver = Ahmed Al Mansouri (Sales Manager)
- ✅ State = Pending
- ✅ Shows timeout configuration (e.g., "Escalates in X hours")

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 8.2: Manual Escalation Trigger

**Note**: Auto-escalation requires waiting for timeout. For UAT, we'll trigger manually if possible.

**Test Steps**:
1. From approval request in Test 8.1
2. Look for "Escalate" button or "Force Escalation" action
3. OR: Run cron job manually:
   ```
   Settings > Technical > Scheduled Actions > 
   Find: "OPS: Escalate Overdue Approvals" > Run Manually
   ```
4. Refresh approval request
5. Check new approver

**Expected Results**:
- ✅ Approval escalated to next level
- ✅ New approver assigned (e.g., CFO or BU Leader)
- ✅ Email notification sent (check email or logs)
- ✅ Escalation logged in chatter

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 8.3: Email Notifications

**Test Steps**:
1. After escalation in Test 8.2
2. Check system email logs:
   ```
   Settings > Technical > Email > Emails
   ```
3. Find email to escalated approver
4. Verify content includes:
   - Approval request details
   - Reason for escalation
   - Link to approve/reject

**Expected Results**:
- ✅ Email queued or sent
- ✅ Recipient = new approver
- ✅ Subject mentions approval needed
- ✅ Body has actionable link

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 8.4: Chatter Logging

**Test Steps**:
1. Open escalated approval request
2. Scroll to bottom chatter section
3. Check for escalation message

**Expected Results**:
- ✅ Message posted: "Approval escalated from [User A] to [User B]"
- ✅ Timestamp shown
- ✅ System user as author
- ✅ Previous approvals history visible

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

## 📊 PRIORITY #9: AUTO-LIST ACCOUNTS IN REPORTS

### Test 9.1: View Report Templates

**Navigate**: Accounting > Reporting > Report Templates  
(or Configuration > Financial Reports > Templates)

**Test Steps**:
1. Check if menu exists
2. List all report templates
3. Verify templates loaded from data

**Expected Results**:
- ✅ Menu accessible
- ✅ At least 1 template visible (e.g., "P&L Template")
- ✅ Templates show account type/category
- ✅ Can open template details

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 9.2: Create New Report Template

**Test Steps**:
1. Click "Create" on Report Templates
2. Enter:
   - Name: "Test Balance Sheet"
   - Report Type: Balance Sheet (or similar)
3. Save
4. Check if account lines auto-populate

**Expected Results**:
- ✅ Template saves successfully
- ✅ Account type field available
- ✅ Lines auto-populated based on type
- ✅ Shows: Assets, Liabilities, Equity sections

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 9.3: Apply Template to Financial Report

**Navigate**: Accounting > Reporting > Financial Reports  

**Test Steps**:
1. Create new financial report or open existing
2. Look for "Apply Template" button/wizard
3. Select "Test Balance Sheet" template
4. Apply
5. Verify accounts populated

**Expected Results**:
- ✅ Apply wizard appears
- ✅ Template selection dropdown works
- ✅ After apply, accounts populate automatically
- ✅ Account groupings match template structure

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test 9.4: Account Auto-Population Logic

**Test Steps**:
1. Create template: "Test P&L"
2. Set Report Type = "Profit & Loss"
3. Save and check auto-listed accounts
4. Verify accounts match type:
   - Revenue accounts (4000 series)
   - Expense accounts (5000 series)

**Expected Results**:
- ✅ Only revenue/expense accounts listed
- ✅ Asset/Liability accounts excluded
- ✅ Account filtering works correctly
- ✅ Can manually add/remove accounts

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

## 🔐 BONUS TESTS: CORE FEATURES

### Test B1: Document Locking (Priority #5)

**Navigate**: Sales > Orders > Open SO00002 (large order)  

**Test Steps**:
1. Check if approval request exists for this SO
2. Try to edit SO (change quantity or customer)
3. Verify edit is blocked

**Expected Results**:
- ✅ Document locked during approval
- ✅ Error message: "Cannot modify while approval pending"
- ✅ Edit button disabled or grayed out

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test B2: Excel Import for SO Lines (Priority #6)

**Navigate**: Sales > Orders > Open SO00003 (empty order)  

**Test Steps**:
1. Check for "Import Lines from Excel" button
2. Download template
3. Verify template has columns: Product Code, Quantity, Price
4. Fill in 3 products:
   - LAP-BUS-001, 5, 3500
   - MSE-WRL-001, 20, 85
   - MON-27K-001, 10, 1200
5. Upload filled template
6. Verify lines created

**Expected Results**:
- ✅ Import button visible
- ✅ Template downloads correctly
- ✅ Upload processes without error
- ✅ 3 lines created in SO
- ✅ Quantities and prices match
- ✅ Total = (5×3500) + (20×85) + (10×1200) = 31,200 AED

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

### Test B3: Cost/Margin Visibility (Security)

**Login**: fatima.sales@testtrading.ae (Sales Rep)  
**Password**: (should be set by admin first)

**Test Steps**:
1. Navigate to Products
2. Open "Laptop - Business Series"
3. Check if "Cost Price" field is visible

**Expected Results**:
- ❌ Cost price field HIDDEN or grayed out
- ❌ Margin fields not visible
- ✅ Only sales price visible
- ✅ Sales rep cannot see cost data

**✅ PASS / ❌ FAIL**: _______

**Actual Results**: _______________________________________________

---

## 📝 TEST SUMMARY

### Overall Results

| Priority | Feature | Status | Notes |
|----------|---------|--------|-------|
| #7 | Three-Way Match - Perfect | ☐ PASS ☐ FAIL | |
| #7 | Three-Way Match - Partial | ☐ PASS ☐ FAIL | |
| #7 | Three-Way Match - Over-bill | ☐ PASS ☐ FAIL | |
| #7 | Override Wizard | ☐ PASS ☐ FAIL | |
| #8 | Approval Requests View | ☐ PASS ☐ FAIL | |
| #8 | Manual Escalation | ☐ PASS ☐ FAIL | |
| #8 | Email Notifications | ☐ PASS ☐ FAIL | |
| #8 | Chatter Logging | ☐ PASS ☐ FAIL | |
| #9 | Report Templates View | ☐ PASS ☐ FAIL | |
| #9 | Create Template | ☐ PASS ☐ FAIL | |
| #9 | Apply Template | ☐ PASS ☐ FAIL | |
| #9 | Auto-Population Logic | ☐ PASS ☐ FAIL | |
| B1 | Document Locking | ☐ PASS ☐ FAIL | |
| B2 | Excel Import | ☐ PASS ☐ FAIL | |
| B3 | Cost Visibility | ☐ PASS ☐ FAIL | |

### Critical Issues Found

_List any blocking issues:_

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Minor Issues Found

_List any non-blocking issues:_

1. _______________________________________________
2. _______________________________________________

### UAT Sign-Off

**Overall Assessment**: ☐ APPROVED ☐ REJECTED ☐ APPROVED WITH MINOR ISSUES

**Tester Signature**: _________________ **Date**: _____________

**Notes**: 
_____________________________________________
_____________________________________________
_____________________________________________

---

## 🔧 TROUBLESHOOTING

### If Seeding Fails

```bash
# Check Odoo logs
docker logs gemini_odoo19 --tail 50

# Verify module installed
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name = 'ops_matrix_core';"

# Re-run seeding
cd /opt/gemini_odoo19
bash addons/ops_matrix_core/data/execute_seeding.sh
```

### If Data Doesn't Appear

- Clear browser cache
- Logout and login again
- Check user permissions
- Verify correct company/branch selected

### If Features Missing

- Confirm module version: 19.0.1.3
- Check installed modules list
- Verify cron jobs running
- Check system logs for errors

---

**End of UAT Checklist**
