# RooCode Kickstart Prompt - OPS Framework Installation & Testing

**Date**: January 4, 2026
**Phase**: Installation of Priorities #7, #8, #9
**Estimated Time**: 2-3 hours
**Status**: Ready to execute

---

## CONTEXT

You (RooCode) have successfully completed development of three major priorities:
- **Priority #7**: Three-Way Match Enforcement (Phases 1+2)
- **Priority #8**: Auto-Escalation with multi-level approval
- **Priority #9**: Auto-List Accounts in Reports

The code has been committed to GitHub (commits: f72414c and 6d848fc) and reviewed by Claude (Documentation Agent). The code review shows **5/5 stars quality** and is **approved for production**.

Now you need to:
1. Install these modules on the VPS
2. Run comprehensive tests
3. Verify everything works
4. Document results

---

## YOUR MISSION

### Phase 1: Pre-Installation Verification (15 minutes)

**Step 1.1: Environment Check**

Run these commands and verify outputs:

```bash
# 1. Navigate to project directory
cd /opt/gemini_odoo19

# 2. Verify Git status
git status
# Expected: On branch main, up to date

# 3. Pull latest code (just in case)
git pull origin main

# 4. Verify commit history
git log --oneline -5
# Expected output should include:
# f72414c (or similar) - Priorities 7-9 implementation
# 6d848fc (or similar) - Related commits

# 5. Check Docker containers
docker ps
# Expected: gemini_odoo19 and postgres containers RUNNING

# 6. Check disk space
df -h
# Expected: At least 10GB free on /opt volume
```

**Step 1.2: Pre-Installation Backup**

```bash
# Create backup directory with timestamp
BACKUP_DIR="/opt/gemini_odoo19/_backup/pre_install_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker exec postgres pg_dump -U odoo mz-db | gzip > $BACKUP_DIR/database_backup.sql.gz

# Verify backup created
ls -lh $BACKUP_DIR/database_backup.sql.gz
# Expected: File size > 1MB (indicates data exists)

# Document backup location
echo "Backup created at: $BACKUP_DIR" | tee installation_log.txt
echo "Backup size: $(du -h $BACKUP_DIR/database_backup.sql.gz | cut -f1)" | tee -a installation_log.txt
```

**Checkpoint**: Confirm all pre-checks passed before proceeding.

---

### Phase 2: Module Installation (30 minutes)

**Step 2.1: Stop Odoo Service**

```bash
# Stop Odoo gracefully
docker-compose stop odoo

# Verify stopped
docker ps | grep odoo
# Expected: No output (odoo container not running)

# Log the action
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Odoo service stopped" | tee -a installation_log.txt
```

**Step 2.2: Run Module Upgrade**

```bash
# Upgrade ops_matrix_core module
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting module upgrade..." | tee -a installation_log.txt

docker exec gemini_odoo19 odoo \
  -c /etc/odoo/odoo.conf \
  -d mz-db \
  -u ops_matrix_core \
  --stop-after-init \
  2>&1 | tee -a upgrade_log.txt

# Check exit code
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Module upgrade SUCCESS" | tee -a installation_log.txt
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Module upgrade FAILED - Check upgrade_log.txt" | tee -a installation_log.txt
    exit 1
fi
```

**Step 2.3: Verify Upgrade Log**

```bash
# Check for errors in upgrade log
echo "Checking for errors..." | tee -a installation_log.txt
grep -i "error\|exception\|traceback" upgrade_log.txt | tee -a installation_log.txt

# If any errors found, STOP and investigate
# If no errors, proceed

echo "[$(date '+%Y-%m-%d %H:%M:%S')] No critical errors found" | tee -a installation_log.txt
```

**Step 2.4: Verify Database Changes**

```bash
# Connect to database and verify new tables
docker exec -i postgres psql -U odoo mz-db << EOF
-- Check for new tables
\dt ops_three_way_match
\dt ops_report_template
\dt ops_report_template_line

-- Count records in approval request (should have escalation fields)
\d ops_approval_request

-- Verify cron jobs created
SELECT id, name, active FROM ir_cron WHERE name LIKE '%three%way%' OR name LIKE '%escalat%';

-- Exit
\q
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Database tables verified" | tee -a installation_log.txt
```

**Step 2.5: Start Odoo Service**

```bash
# Start Odoo
docker-compose start odoo

# Wait for service to be ready (30 seconds)
echo "Waiting for Odoo to start..."
sleep 30

# Check if Odoo is running
docker ps | grep odoo

# Check logs for startup
docker logs --tail 50 gemini_odoo19 | tee -a installation_log.txt

# Verify no errors
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Odoo service started" | tee -a installation_log.txt
```

**Step 2.6: Verify Web Access**

```bash
# Test web access
curl -I http://localhost:8069/web/login
# Expected: HTTP/1.1 200 OK

# Log result
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Web interface accessible" | tee -a installation_log.txt
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Web interface NOT accessible - investigate" | tee -a installation_log.txt
    exit 1
fi
```

**Checkpoint**: Module installed successfully, Odoo running, web accessible.

---

### Phase 3: Priority #7 Testing - Three-Way Match (30 minutes)

**Test 3.1: Access Web Interface**

```
1. Open browser: http://localhost:8069
2. Login with admin credentials
3. Navigate to: Settings > Apps
4. Search for: ops_matrix_core
5. Verify: Version shows 19.0.1.4 or higher
6. Verify: No error messages on dashboard
```

**Test 3.2: Three-Way Match Configuration**

```
Manual Steps:
1. Navigate to: Settings > Companies > Your Company
2. Scroll to: Three-Way Match Configuration
3. Verify fields exist:
   - Enable Three-Way Match (checkbox)
   - Tolerance Percentage (float)
4. Set:
   - Enable = True
   - Tolerance = 5.0 (5%)
5. Save
6. Verify: No errors
```

**Test 3.3: Perfect Match Scenario**

```
Manual Steps:
1. Create Purchase Order:
   - Vendor: Any vendor
   - Product: Any product
   - Quantity: 100
   - Unit Price: $10
   - Confirm PO

2. Receive Goods:
   - Open PO > Receipt > Validate
   - Quantity: 100 (full receipt)

3. Create Vendor Bill:
   - Open PO > Create Bill
   - Quantity: 100
   - Unit Price: $10
   - Click Validate

4. Expected Result:
   - Bill validates successfully
   - Status: Posted
   - No blocking messages

5. Check Three-Way Match Report:
   - Navigate to: Purchase > Reporting > Three-Way Match
   - Find your PO
   - Verify:
     - Match Status = MATCHED
     - Ordered Qty = 100
     - Received Qty = 100
     - Billed Qty = 100
     - Variance = 0%
```

**Test 3.4: Over-Billing Scenario (Should Block)**

```
Manual Steps:
1. Create new Purchase Order:
   - Quantity: 100
   - Confirm

2. Receive Partial:
   - Receipt > Validate
   - Quantity: 90 (partial receipt)

3. Try to bill for more than received:
   - Create Bill
   - Quantity: 100 (more than received)
   - Click Validate

4. Expected Result:
   - Validation BLOCKED
   - Error message: "Over-billing detected: Cannot bill 100 units when only 90 received"
   - Bill remains in Draft

5. Check Three-Way Match Report:
   - Status = OVER_BILLED
   - Variance = +10 units (+11.1%)
   - Blocking = True
```

**Test 3.5: Override Workflow**

```
Manual Steps:
1. Continue from blocked bill above
2. Look for button: "Request Override"
3. Click "Request Override"
4. Fill justification: "Vendor added shipping charges, approved by manager"
5. Submit

6. Expected:
   - Approval request created
   - Assigned to: Purchase Manager persona
   - Document locked

7. Login as Purchase Manager (or use admin)
8. Navigate to: Approvals > My Approvals
9. Find the override request
10. Click Approve
11. Add comment: "Approved - shipping charges confirmed"

12. Return to Vendor Bill
13. Click Validate again

14. Expected:
   - Validation succeeds
   - Bill posted
   - Chatter shows full audit trail:
     - Override requested
     - Approval granted
     - Invoice validated
```

**Test 3.6: Cron Job Verification**

```bash
# Verify cron job exists and is active
docker exec -i postgres psql -U odoo mz-db << EOF
SELECT 
    id, 
    name, 
    active, 
    interval_type, 
    interval_number,
    nextcall
FROM ir_cron 
WHERE name LIKE '%three%way%match%';
EOF

# Expected output:
# Should show 1 cron job
# Name: Three-Way Match Recalculation
# Active: True
# Interval: Daily (or as configured)
```

**Document Test Results**:

```bash
echo "" >> installation_log.txt
echo "=== Priority #7: Three-Way Match Tests ===" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 3.2: Configuration - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 3.3: Perfect Match - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 3.4: Over-Billing Block - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 3.5: Override Workflow - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 3.6: Cron Job - PASS/FAIL" >> installation_log.txt
echo "" >> installation_log.txt
```

**Checkpoint**: Three-Way Match fully functional.

---

### Phase 4: Priority #8 Testing - Auto-Escalation (30 minutes)

**Test 4.1: Escalation Configuration**

```
Manual Steps:
1. Navigate to: Settings > Governance Rules
2. Find rule: "Sale Order > $5,000 requires approval"
3. Edit rule
4. Verify escalation fields exist:
   - Enable Auto-Escalation (checkbox)
   - Escalation Timeout (Hours) (float)
   - Level 1 Escalation Persona
   - Level 2 Escalation Persona
   - Level 3 Escalation Persona

5. Configure (for testing purposes):
   - Enable = True
   - Timeout = 0.1 hours (6 minutes for testing)
   - L1 = Branch Manager
   - L2 = BU Leader
   - L3 = CFO

6. Save
```

**Test 4.2: Create Approval Request**

```
Manual Steps:
1. Create Sale Order:
   - Customer: Any customer
   - Product: Any product
   - Amount: $6,000 (exceeds threshold)
   - Confirm

2. Expected:
   - Approval request created automatically
   - Assigned to: Sales Manager (Level 0)
   - Status: Pending
   - Document locked

3. Note the approval request ID
```

**Test 4.3: Trigger Escalation Manually**

```bash
# Run escalation cron manually (don't wait 6 minutes)
docker exec gemini_odoo19 odoo shell -d mz-db << EOF
# Run escalation
self.env['ops.approval.request']._cron_escalate_overdue_approvals()
self.env.cr.commit()
exit()
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Escalation cron triggered manually" >> installation_log.txt
```

**Test 4.4: Verify Escalation to Level 1**

```
Manual Steps:
1. Refresh approval request page
2. Verify:
   - Escalation Level = 1
   - Assigned to = Branch Manager
   - Chatter message: "Escalated to Level 1: Branch Manager"
   - Escalation history updated

3. Check original approver (Sales Manager):
   - Should have received reminder email (check email or logs)

4. Check new approver (Branch Manager):
   - Should have received notification email
```

**Test 4.5: Continue Escalation to Level 2**

```bash
# Run escalation again (simulating another timeout)
docker exec gemini_odoo19 odoo shell -d mz-db << EOF
self.env['ops.approval.request']._cron_escalate_overdue_approvals()
self.env.cr.commit()
exit()
EOF
```

```
Manual Steps:
1. Refresh approval request
2. Verify:
   - Escalation Level = 2
   - Assigned to = BU Leader
   - Chatter shows escalation to Level 2
   - History complete
```

**Test 4.6: Final Approval**

```
Manual Steps:
1. Login as BU Leader (or admin)
2. Navigate to approval request
3. Click Approve
4. Add comment: "Approved after escalation"

5. Verify:
   - Approval request status = Approved
   - Sale Order unlocked
   - Escalation history shows full timeline
   - Chatter complete with all escalations + approval
```

**Test 4.7: Dashboard Filters**

```
Manual Steps:
1. Navigate to: Approvals > Approval Dashboard
2. Test filters:
   - "Overdue Approvals" → Should show overdue items
   - "Escalation Level = 1" → Should show L1 escalations
   - "Escalation Level = 2" → Should show L2 escalations
3. Verify filter results accurate
```

**Test 4.8: Email Template Verification**

```bash
# Check if email templates exist
docker exec -i postgres psql -U odoo mz-db << EOF
SELECT name, model FROM mail_template 
WHERE name LIKE '%escalat%' OR name LIKE '%reminder%';
EOF

# Expected: At least 2 templates
# - Escalation Reminder
# - Escalation Notification
```

**Document Test Results**:

```bash
echo "=== Priority #8: Auto-Escalation Tests ===" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 4.1: Configuration - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 4.2: Approval Request - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 4.4: L1 Escalation - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 4.5: L2 Escalation - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 4.6: Final Approval - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 4.7: Dashboard - PASS/FAIL" >> installation_log.txt
echo "" >> installation_log.txt
```

**Checkpoint**: Auto-Escalation fully functional.

---

### Phase 5: Priority #9 Testing - Auto-List Accounts (30 minutes)

**Test 5.1: Verify Report Templates**

```
Manual Steps:
1. Navigate to: Accounting > Configuration > Report Templates
2. Verify templates exist:
   - Standard P&L
   - Standard Balance Sheet
   - Standard Trial Balance
   - Standard Cash Flow

3. Open "Standard P&L"
4. Verify:
   - is_system_template = True
   - Cannot edit (read-only)
   - Has template lines:
     - REVENUE
     - COST OF GOODS SOLD
     - OPERATING EXPENSES
```

**Test 5.2: Apply P&L Template**

```
Manual Steps:
1. Navigate to: Accounting > Reporting > Financial Reports
2. Create new report
3. Name: "Test P&L - January 2026"
4. Report Type: Profit & Loss
5. Click "Apply Template"
6. Select: "Standard P&L"
7. Date Range: 2026-01-01 to 2026-01-31
8. Click "Apply"

9. Verify:
   - Report auto-populated
   - Section: REVENUE (with income accounts)
   - Section: COST OF GOODS SOLD (expense accounts 5xxx)
   - Section: OPERATING EXPENSES (expense accounts 6xxx)
   - Accounts sorted by code
   - Section headers visible
   - Totals calculated
```

**Test 5.3: Apply Balance Sheet Template**

```
Manual Steps:
1. Create new report
2. Name: "Test Balance Sheet - January 2026"
3. Report Type: Balance Sheet
4. Apply Template: "Standard Balance Sheet"
5. Date: 2026-01-31

6. Verify:
   - Section: ASSETS (all asset accounts)
   - Section: LIABILITIES (all liability accounts)
   - Section: EQUITY (all equity accounts)
   - Assets = Liabilities + Equity (balance check)
```

**Test 5.4: Create Custom Template**

```
Manual Steps:
1. Navigate to: Report Templates
2. Create new template
3. Name: "Custom Expense Analysis"
4. Report Type: Custom
5. Add line:
   - Section: "Marketing Expenses"
   - Account Type: Expense
   - Code Pattern: "61%"
   - Sort: By Code
6. Add line:
   - Section: "IT Expenses"
   - Account Type: Expense
   - Code Pattern: "62%"
   - Sort: By Code
7. Save

8. Apply to new report
9. Verify: Only marketing and IT expenses shown
```

**Test 5.5: Export to Excel**

```
Manual Steps:
1. Open any report created above
2. Click "Export to Excel"
3. Download Excel file
4. Open in Excel/LibreOffice
5. Verify:
   - Section headers preserved
   - Account codes
   - Account names
   - Debit/Credit/Balance columns
   - Subtotals per section
   - Formatting clean
```

**Test 5.6: Template Reusability**

```
Manual Steps:
1. Create report "February P&L"
2. Apply "Standard P&L" template
3. Change date range to February
4. Verify:
   - Same account structure as January
   - Different balances (February data)
5. Compare side-by-side with January
```

**Document Test Results**:

```bash
echo "=== Priority #9: Auto-List Accounts Tests ===" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 5.1: Templates Exist - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 5.2: P&L Template - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 5.3: Balance Sheet - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 5.4: Custom Template - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 5.5: Excel Export - PASS/FAIL" >> installation_log.txt
echo "" >> installation_log.txt
```

**Checkpoint**: Auto-List Accounts fully functional.

---

### Phase 6: Integration Testing (20 minutes)

**Test 6.1: Three-Way Match + Escalation**

```
Manual Steps:
1. Create PO (100 units)
2. Receive partial (90 units)
3. Create bill for 100 units (over-billed)
4. Expected: Blocked
5. Request override
6. Expected: Approval request created
7. DO NOT approve (let it sit)
8. Run escalation cron
9. Expected: Request escalates to L1
10. Approve at L1
11. Expected: Invoice unlocks
12. Validate invoice
13. Expected: Success
14. Verify: Full audit trail in chatter
```

**Test 6.2: Excel Import + Three-Way Match**

```
Manual Steps:
1. Create PO using Excel import (50 lines)
2. Receive all items
3. Create vendor bill for same PO
4. Expected: Three-way match validates successfully
5. Verify: No conflicts between features
```

**Test 6.3: Performance Test**

```bash
# Create 10 sale orders simultaneously to test performance
for i in {1..10}; do
  echo "Creating sale order $i..."
  # Use Odoo shell or API to create orders
  # Measure time
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Performance test: 10 orders created" >> installation_log.txt
```

**Document Test Results**:

```bash
echo "=== Integration Tests ===" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 6.1: Match + Escalation - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 6.2: Excel + Match - PASS/FAIL" >> installation_log.txt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test 6.3: Performance - PASS/FAIL" >> installation_log.txt
echo "" >> installation_log.txt
```

---

### Phase 7: Final Verification & Documentation (15 minutes)

**Step 7.1: System Health Check**

```bash
# Check Odoo logs for any errors
echo "Checking for errors in Odoo logs..."
docker logs --tail 200 gemini_odoo19 | grep -i "error\|exception\|traceback" > errors.log

# Count errors
ERROR_COUNT=$(wc -l < errors.log)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Total errors in log: $ERROR_COUNT" >> installation_log.txt

if [ $ERROR_COUNT -gt 0 ]; then
    echo "WARNINGS: Found $ERROR_COUNT errors in logs - Review errors.log"
    cat errors.log >> installation_log.txt
else
    echo "SUCCESS: No errors found in logs"
fi
```

**Step 7.2: Database Integrity Check**

```bash
docker exec -i postgres psql -U odoo mz-db << EOF
-- Check for orphaned records
SELECT COUNT(*) FROM ops_approval_request WHERE state = 'pending' AND create_date < NOW() - INTERVAL '30 days';

-- Check three-way matches
SELECT match_state, COUNT(*) FROM ops_three_way_match GROUP BY match_state;

-- Check report templates
SELECT report_type, COUNT(*) FROM ops_report_template GROUP BY report_type;

EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Database integrity check complete" >> installation_log.txt
```

**Step 7.3: Performance Metrics**

```bash
# Check database size
DB_SIZE=$(docker exec postgres psql -U odoo -d mz-db -t -c "SELECT pg_size_pretty(pg_database_size('mz-db'));")
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Database size: $DB_SIZE" >> installation_log.txt

# Check active connections
ACTIVE_CONN=$(docker exec postgres psql -U odoo -d mz-db -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Active connections: $ACTIVE_CONN" >> installation_log.txt
```

**Step 7.4: Create Summary Report**

```bash
# Create comprehensive installation report
cat << EOF > INSTALLATION_REPORT.md
# OPS Framework - Installation Report

**Date**: $(date '+%Y-%m-%d')
**Time**: $(date '+%H:%M:%S')
**Operator**: RooCode (VSCode Agent)
**Status**: COMPLETE

---

## Modules Installed

- Priority #7: Three-Way Match Enforcement
- Priority #8: Auto-Escalation
- Priority #9: Auto-List Accounts in Reports

---

## Installation Summary

**Database Backup**: $BACKUP_DIR/database_backup.sql.gz
**Backup Size**: $(du -h $BACKUP_DIR/database_backup.sql.gz | cut -f1)
**Database Size**: $DB_SIZE
**Error Count**: $ERROR_COUNT

---

## Test Results

### Priority #7: Three-Way Match
- Configuration: PASS/FAIL
- Perfect Match: PASS/FAIL
- Over-Billing Block: PASS/FAIL
- Override Workflow: PASS/FAIL
- Cron Job: PASS/FAIL

### Priority #8: Auto-Escalation
- Configuration: PASS/FAIL
- Approval Request: PASS/FAIL
- L1 Escalation: PASS/FAIL
- L2 Escalation: PASS/FAIL
- Final Approval: PASS/FAIL
- Dashboard: PASS/FAIL

### Priority #9: Auto-List Accounts
- Templates Exist: PASS/FAIL
- P&L Template: PASS/FAIL
- Balance Sheet: PASS/FAIL
- Custom Template: PASS/FAIL
- Excel Export: PASS/FAIL

### Integration Tests
- Match + Escalation: PASS/FAIL
- Excel + Match: PASS/FAIL
- Performance: PASS/FAIL

---

## System Health

**Odoo Status**: Running
**Database Status**: Healthy
**Web Interface**: Accessible
**Errors**: $ERROR_COUNT

---

## Next Steps

1. Review this report with Claude (Documentation Agent)
2. If all tests PASS: Proceed to Week 2 of implementation plan
3. If any tests FAIL: Document failures and create fix plan
4. Update TODO_MASTER.md with progress
5. Commit all changes to GitHub

---

**Report Generated**: $(date)
**Installation Log**: installation_log.txt
**Error Log**: errors.log (if errors found)

EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installation report created: INSTALLATION_REPORT.md" >> installation_log.txt
```

**Step 7.5: Commit Results to GitHub**

```bash
# Stage all documentation
git add installation_log.txt
git add INSTALLATION_REPORT.md
git add upgrade_log.txt
[ -f errors.log ] && git add errors.log

# Commit
git commit -m "test: Installation and testing of Priorities #7-9 complete

Installed modules:
- Priority #7: Three-Way Match Enforcement
- Priority #8: Auto-Escalation  
- Priority #9: Auto-List Accounts

All installation tests completed.
See INSTALLATION_REPORT.md for details."

# Push to GitHub
git push origin main

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Results committed to GitHub" >> installation_log.txt
```

---

## EXPECTED OUTCOMES

If everything goes well, you should see:

**✅ Module Installation**:
- ops_matrix_core upgraded successfully
- Version: 19.0.1.4 or higher
- No errors in upgrade log
- All new tables created

**✅ Priority #7: Three-Way Match**:
- Configuration accessible
- Perfect matches pass validation
- Over-billing scenarios blocked correctly
- Override workflow functional
- Cron job scheduled and active

**✅ Priority #8: Auto-Escalation**:
- Escalation configuration available
- Approval requests created
- Escalation triggers on timeout
- Multi-level escalation works (L1, L2, L3)
- Email notifications sent (or templates exist)
- Dashboard filters functional

**✅ Priority #9: Auto-List Accounts**:
- Report templates loaded
- Templates can be applied to reports
- Accounts auto-populate correctly
- Custom templates can be created
- Excel export works

**✅ Integration**:
- All features work together
- No conflicts
- Performance acceptable
- No critical bugs

---

## TROUBLESHOOTING

**If Module Upgrade Fails**:

```bash
# Check upgrade log for specific error
grep -A 10 "ERROR" upgrade_log.txt

# Common issues:
# 1. Missing dependency: Install dependency module
# 2. Database error: Check database logs
# 3. Python error: Check code syntax
# 4. Permission error: Check file permissions

# Restore from backup if needed:
docker-compose stop odoo
docker exec postgres dropdb -U odoo mz-db
docker exec postgres createdb -U odoo mz-db
gunzip < $BACKUP_DIR/database_backup.sql.gz | docker exec -i postgres psql -U odoo mz-db
docker-compose start odoo
```

**If Web Interface Not Accessible**:

```bash
# Check if Odoo is running
docker ps | grep odoo

# Check Odoo logs
docker logs --tail 100 gemini_odoo19

# Restart Odoo
docker-compose restart odoo

# Check port binding
netstat -tlnp | grep 8069
```

**If Tests Fail**:

```bash
# Document the failure
echo "TEST FAILURE: [Test Name] - [Reason]" >> installation_log.txt

# Collect debug info
docker logs --tail 500 gemini_odoo19 > debug.log

# Create GitHub issue
# Title: "Installation Test Failure: [Test Name]"
# Body: Include error details, logs, screenshots
```

---

## SUCCESS CRITERIA

Consider installation successful if:

1. ✅ Module upgrade completed without errors
2. ✅ Odoo starts successfully
3. ✅ Web interface accessible
4. ✅ All 3 priorities tested (at least basic functionality)
5. ✅ No critical errors in logs
6. ✅ Database integrity maintained
7. ✅ Backup created and verified
8. ✅ Results documented and committed to GitHub

**Minimum Passing Score**: 12/15 tests PASS (80%)

---

## HANDOFF TO CLAUDE

After completing all phases:

1. Review INSTALLATION_REPORT.md
2. Note any failures or issues
3. Share report with Claude (Documentation Agent)
4. Claude will:
   - Review test results
   - Update documentation
   - Plan next steps (Week 2 of implementation plan)
   - Update TODO_MASTER.md

---

## TIME ESTIMATE

- Phase 1: Pre-Installation - 15 minutes
- Phase 2: Installation - 30 minutes
- Phase 3: Priority #7 Testing - 30 minutes
- Phase 4: Priority #8 Testing - 30 minutes
- Phase 5: Priority #9 Testing - 30 minutes
- Phase 6: Integration Testing - 20 minutes
- Phase 7: Documentation - 15 minutes

**Total**: 2-3 hours (including any troubleshooting)

---

## NOTES FOR ROOCODE

- Work methodically through each phase
- Don't skip the backup step
- Document EVERYTHING in installation_log.txt
- If you encounter errors, don't panic - troubleshoot systematically
- Mark each test as PASS or FAIL in the log
- The goal is to verify the code works, not to achieve 100% pass rate on first try
- If tests fail, that's valuable information for fixing bugs
- Take screenshots of any UI elements for documentation
- Commit your work frequently

---

**Ready to begin? Start with Phase 1: Pre-Installation Verification**

Good luck! 🚀
