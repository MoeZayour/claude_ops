# OPS Framework - Critical Security & Data Integrity Fixes

## MISSION
Implement IT Admin Blindness rules and fix Budget SQL constraints to make OPS Framework production-ready.

**Duration**: 3 hours  
**Mode**: Autonomous - fix errors without stopping  
**Priority**: P0 CRITICAL - Security & Data Integrity  
**Date**: January 30, 2026

---

## CONTEXT

**Issue 1 - IT Admin Blindness (SECURITY)**:
- The group `group_ops_it_admin` EXISTS in `/opt/gemini_odoo19/addons/ops_matrix_core/data/res_groups.xml`
- But the RECORD RULES to block access are MISSING from `ir_rule.xml`
- Result: IT Admin can see ALL business data (sales, purchases, invoices, etc.)
- Required: Add 20 record rules with domain `[(1, '=', 0)]` to block access

**Issue 2 - Budget Constraints (DATA INTEGRITY)**:
- `ops_budget.py` uses invalid `models.Constraint()` syntax
- Odoo ignores this, allowing duplicate budgets
- Required: Convert to proper `_sql_constraints` format

---

## PHASE 1: BACKUP & INVESTIGATE (10 min)

### Task 1.1: Create Backups

```bash
echo "========================================"
echo "PHASE 1: BACKUP & INVESTIGATE"
echo "========================================"

cd /opt/gemini_odoo19/addons

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Creating backups ==="
cp ops_matrix_core/security/ir_rule.xml ops_matrix_core/security/ir_rule.xml.backup.$TIMESTAMP
cp ops_matrix_accounting/models/ops_budget.py ops_matrix_accounting/models/ops_budget.py.backup.$TIMESTAMP 2>/dev/null || echo "Budget file path may differ"

echo "✅ Backups created"
```

### Task 1.2: Verify Current State

```bash
echo "=== Verify IT Admin group exists ==="
grep -n "group_ops_it_admin" /opt/gemini_odoo19/addons/ops_matrix_core/data/res_groups.xml

echo ""
echo "=== Count existing IT Admin rules in ir_rule.xml ==="
grep -v "<!--" /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml | grep -c "it_admin" || echo "0 rules found"

echo ""
echo "=== Find Budget file ==="
find /opt/gemini_odoo19/addons/ops_matrix_accounting -name "*budget*" -type f

echo ""
echo "=== Check current budget constraint syntax ==="
grep -n "Constraint\|_sql_constraints\|_unique" /opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_budget.py 2>/dev/null | head -20

echo "✅ Task 1.2 complete"
```

### Task 1.3: Find Insertion Point in ir_rule.xml

```bash
echo "=== Finding where to insert IT Admin rules ==="
grep -n "IT ADMIN\|BRANCH MANAGER\|BU LEADER" /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml

echo ""
echo "=== Show last 30 lines of ir_rule.xml ==="
tail -30 /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml

echo "✅ Phase 1 complete"
```

---

## PHASE 2: IMPLEMENT IT ADMIN BLINDNESS RULES (60 min)

### Task 2.1: Add IT Admin Blindness Rules

The following XML block must be added to `/opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml`.

Find the section with the comment about IT Admin (or the end of the file before `</odoo>`) and insert these rules:

```xml
        <!-- =========================================================== -->
        <!-- IT ADMIN BLINDNESS RULES                                    -->
        <!-- =========================================================== -->
        <!-- Purpose: Block group_ops_it_admin from ALL business data    -->
        <!-- Domain [(1,'=',0)] = Always FALSE = Zero records returned   -->
        <!-- IT Admin can: manage users, configure system, view logs     -->
        <!-- IT Admin cannot: see sales, purchases, invoices, payments   -->
        <!-- =========================================================== -->

        <!-- 1. Sale Order - BLOCKED -->
        <record id="rule_it_admin_blind_sale_order" model="ir.rule">
            <field name="name">IT Admin Blindness: Sale Orders</field>
            <field name="model_id" ref="sale.model_sale_order"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 2. Sale Order Line - BLOCKED -->
        <record id="rule_it_admin_blind_sale_order_line" model="ir.rule">
            <field name="name">IT Admin Blindness: Sale Order Lines</field>
            <field name="model_id" ref="sale.model_sale_order_line"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 3. Purchase Order - BLOCKED -->
        <record id="rule_it_admin_blind_purchase_order" model="ir.rule">
            <field name="name">IT Admin Blindness: Purchase Orders</field>
            <field name="model_id" ref="purchase.model_purchase_order"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 4. Purchase Order Line - BLOCKED -->
        <record id="rule_it_admin_blind_purchase_order_line" model="ir.rule">
            <field name="name">IT Admin Blindness: Purchase Order Lines</field>
            <field name="model_id" ref="purchase.model_purchase_order_line"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 5. Account Move (Invoices/Bills/Journal Entries) - BLOCKED -->
        <record id="rule_it_admin_blind_account_move" model="ir.rule">
            <field name="name">IT Admin Blindness: Invoices/Journal Entries</field>
            <field name="model_id" ref="account.model_account_move"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 6. Account Move Line - BLOCKED -->
        <record id="rule_it_admin_blind_account_move_line" model="ir.rule">
            <field name="name">IT Admin Blindness: Journal Items</field>
            <field name="model_id" ref="account.model_account_move_line"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 7. Account Payment - BLOCKED -->
        <record id="rule_it_admin_blind_account_payment" model="ir.rule">
            <field name="name">IT Admin Blindness: Payments</field>
            <field name="model_id" ref="account.model_account_payment"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 8. Bank Statement - BLOCKED -->
        <record id="rule_it_admin_blind_bank_statement" model="ir.rule">
            <field name="name">IT Admin Blindness: Bank Statements</field>
            <field name="model_id" ref="account.model_account_bank_statement"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 9. Bank Statement Line - BLOCKED -->
        <record id="rule_it_admin_blind_bank_statement_line" model="ir.rule">
            <field name="name">IT Admin Blindness: Bank Statement Lines</field>
            <field name="model_id" ref="account.model_account_bank_statement_line"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 10. Stock Valuation Layer - BLOCKED -->
        <record id="rule_it_admin_blind_stock_valuation" model="ir.rule">
            <field name="name">IT Admin Blindness: Stock Valuation</field>
            <field name="model_id" ref="stock.model_stock_valuation_layer"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 11. Stock Picking - BLOCKED -->
        <record id="rule_it_admin_blind_stock_picking" model="ir.rule">
            <field name="name">IT Admin Blindness: Stock Transfers</field>
            <field name="model_id" ref="stock.model_stock_picking"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 12. Stock Move - BLOCKED -->
        <record id="rule_it_admin_blind_stock_move" model="ir.rule">
            <field name="name">IT Admin Blindness: Stock Moves</field>
            <field name="model_id" ref="stock.model_stock_move"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 13. Stock Move Line - BLOCKED -->
        <record id="rule_it_admin_blind_stock_move_line" model="ir.rule">
            <field name="name">IT Admin Blindness: Stock Move Lines</field>
            <field name="model_id" ref="stock.model_stock_move_line"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 14. CRM Lead/Opportunity - BLOCKED -->
        <record id="rule_it_admin_blind_crm_lead" model="ir.rule">
            <field name="name">IT Admin Blindness: CRM Leads</field>
            <field name="model_id" ref="crm.model_crm_lead"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 15. Product Pricelist - BLOCKED -->
        <record id="rule_it_admin_blind_pricelist" model="ir.rule">
            <field name="name">IT Admin Blindness: Pricelists</field>
            <field name="model_id" ref="product.model_product_pricelist"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 16. Product Pricelist Item - BLOCKED -->
        <record id="rule_it_admin_blind_pricelist_item" model="ir.rule">
            <field name="name">IT Admin Blindness: Pricelist Items</field>
            <field name="model_id" ref="product.model_product_pricelist_item"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 17. Account Analytic Line - BLOCKED -->
        <record id="rule_it_admin_blind_analytic_line" model="ir.rule">
            <field name="name">IT Admin Blindness: Analytic Lines</field>
            <field name="model_id" ref="analytic.model_account_analytic_line"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 18. PDC Receivable - BLOCKED -->
        <record id="rule_it_admin_blind_pdc_receivable" model="ir.rule">
            <field name="name">IT Admin Blindness: PDC Receivable</field>
            <field name="model_id" ref="ops_matrix_accounting.model_ops_pdc_receivable"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 19. PDC Payable - BLOCKED -->
        <record id="rule_it_admin_blind_pdc_payable" model="ir.rule">
            <field name="name">IT Admin Blindness: PDC Payable</field>
            <field name="model_id" ref="ops_matrix_accounting.model_ops_pdc_payable"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- 20. Budget - BLOCKED -->
        <record id="rule_it_admin_blind_budget" model="ir.rule">
            <field name="name">IT Admin Blindness: Budgets</field>
            <field name="model_id" ref="ops_matrix_accounting.model_ops_budget"/>
            <field name="domain_force">[(1, '=', 0)]</field>
            <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_it_admin'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- =========================================================== -->
        <!-- END OF IT ADMIN BLINDNESS RULES                             -->
        <!-- =========================================================== -->
```

### Task 2.2: Insert Rules into ir_rule.xml

```bash
echo "========================================"
echo "PHASE 2: INSERT IT ADMIN BLINDNESS RULES"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_core/security

# Find the line number of the closing </odoo> tag or existing IT ADMIN comment
echo "=== Finding insertion point ==="
grep -n "</odoo>\|IT ADMIN" ir_rule.xml | tail -5

# The XML block above should be inserted BEFORE the </odoo> closing tag
# Use your preferred method: nano, vim, or sed

echo ""
echo "MANUAL STEP REQUIRED:"
echo "1. Open /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml"
echo "2. Find the </odoo> closing tag at the end"
echo "3. Insert the 20 IT Admin Blindness rules BEFORE </odoo>"
echo "4. Save the file"
echo ""
echo "Or use this command to open the file:"
echo "nano /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml"
```

### Task 2.3: Verify XML After Edit

```bash
echo "=== Verifying XML is valid ==="
python3 -c "import xml.etree.ElementTree as ET; ET.parse('/opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml')" && echo "✅ XML is valid" || echo "❌ XML has errors - check syntax"

echo ""
echo "=== Count IT Admin blindness rules ==="
grep -c "rule_it_admin_blind" /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml

echo ""
echo "=== List all IT Admin blindness rule IDs ==="
grep "rule_it_admin_blind" /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml | grep -o 'id="[^"]*"'

echo "✅ Phase 2 complete"
```

---

## PHASE 3: FIX BUDGET SQL CONSTRAINTS (30 min)

### Task 3.1: Check for Duplicate Budgets First

```bash
echo "========================================"
echo "PHASE 3: FIX BUDGET SQL CONSTRAINTS"
echo "========================================"

echo "=== Checking for duplicate budgets in database ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT ops_branch_id, ops_business_unit_id, date_from, date_to, COUNT(*) as cnt
FROM ops_budget
GROUP BY ops_branch_id, ops_business_unit_id, date_from, date_to
HAVING COUNT(*) > 1;
" 2>/dev/null || echo "Table may not exist yet or no duplicates found"

echo ""
echo "=== Checking for duplicate budget lines ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT budget_id, general_account_id, COUNT(*) as cnt
FROM ops_budget_line
GROUP BY budget_id, general_account_id
HAVING COUNT(*) > 1;
" 2>/dev/null || echo "Table may not exist yet or no duplicates found"

echo "✅ Task 3.1 complete"
```

### Task 3.2: Find and Fix Budget Constraint Syntax

```bash
echo "=== Locating budget file ==="
BUDGET_FILE=$(find /opt/gemini_odoo19/addons/ops_matrix_accounting -name "ops_budget.py" | head -1)
echo "Found: $BUDGET_FILE"

echo ""
echo "=== Current constraint definitions ==="
grep -n "Constraint\|_sql_constraints\|_unique" "$BUDGET_FILE" | head -20
```

### Task 3.3: Apply Budget Fix

**Find in ops_budget.py (ops.budget class):**
```python
# FIND AND REMOVE THIS (invalid syntax):
_unique_matrix_budget = models.Constraint(
    'unique(ops_branch_id, ops_business_unit_id, date_from, date_to)',
    'A budget already exists for this Branch/Business Unit combination in the specified date range!'
)
```

**REPLACE WITH:**
```python
_sql_constraints = [
    ('unique_matrix_budget', 
     'unique(ops_branch_id, ops_business_unit_id, date_from, date_to)',
     'A budget already exists for this Branch/Business Unit combination in the specified date range!')
]
```

**Find in ops_budget.py (ops.budget.line class):**
```python
# FIND AND REMOVE THIS (invalid syntax):
_unique_account_per_budget = models.Constraint(
    'unique(budget_id, general_account_id)',
    'You can only have one budget line per account!'
)
```

**REPLACE WITH:**
```python
_sql_constraints = [
    ('unique_account_per_budget', 
     'unique(budget_id, general_account_id)',
     'You can only have one budget line per account!')
]
```

### Task 3.4: Verify Budget Fix

```bash
echo "=== Verify Python syntax ==="
BUDGET_FILE=$(find /opt/gemini_odoo19/addons/ops_matrix_accounting -name "ops_budget.py" | head -1)
python3 -m py_compile "$BUDGET_FILE" && echo "✅ Python syntax OK" || echo "❌ Python syntax error"

echo ""
echo "=== Verify constraint format ==="
grep -A3 "_sql_constraints" "$BUDGET_FILE"

echo "✅ Phase 3 complete"
```

---

## PHASE 4: UPDATE MODULES & TEST (30 min)

### Task 4.1: Update ops_matrix_core

```bash
echo "========================================"
echo "PHASE 4: UPDATE MODULES & TEST"
echo "========================================"

echo "=== Updating ops_matrix_core ==="
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core --stop-after-init 2>&1 | tail -50

echo ""
echo "=== Check for errors ==="
docker logs gemini_odoo19 --tail 30 | grep -i "error\|traceback\|failed" || echo "✅ No errors found"

echo "✅ Task 4.1 complete"
```

### Task 4.2: Update ops_matrix_accounting

```bash
echo "=== Updating ops_matrix_accounting ==="
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -50

echo ""
echo "=== Check for errors ==="
docker logs gemini_odoo19 --tail 30 | grep -i "error\|traceback\|failed" || echo "✅ No errors found"

echo "✅ Task 4.2 complete"
```

### Task 4.3: Restart Odoo

```bash
echo "=== Restarting Odoo ==="
docker restart gemini_odoo19
sleep 15

echo "=== Verify Odoo is running ==="
docker ps | grep gemini_odoo19 && echo "✅ Odoo is running" || echo "❌ Odoo not running"

echo "✅ Task 4.3 complete"
```

### Task 4.4: Verify IT Admin Rules in Database

```bash
echo "=== Verify IT Admin rules loaded in database ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT name, model_id, domain_force 
FROM ir_rule 
WHERE name LIKE '%IT Admin Blindness%'
ORDER BY name;
"

echo ""
echo "=== Count IT Admin rules ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT COUNT(*) as rule_count 
FROM ir_rule 
WHERE name LIKE '%IT Admin Blindness%';
"

echo "✅ Task 4.4 complete"
```

### Task 4.5: Verify Budget Constraints in Database

```bash
echo "=== Verify budget constraints exist ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT conname, contype 
FROM pg_constraint 
WHERE conname LIKE '%budget%';
"

echo "✅ Task 4.5 complete"
```

---

## PHASE 5: GIT COMMIT (10 min)

### Task 5.1: Commit All Changes

```bash
echo "========================================"
echo "PHASE 5: GIT COMMIT"
echo "========================================"

cd /opt/gemini_odoo19

echo "=== Git status ==="
git status

echo ""
echo "=== Adding changes ==="
git add -A

echo ""
echo "=== Committing ==="
git commit -m "fix(security): CRITICAL - Implement IT Admin Blindness + Fix Budget Constraints

SECURITY FIX - IT Admin Blindness:
- Added 20 record rules for group_ops_it_admin
- Domain [(1,'=',0)] blocks all access to business data
- IT Admin can now manage users but CANNOT see:
  * Sales Orders, Purchase Orders
  * Invoices, Payments, Bank Statements
  * Stock Moves, Valuations
  * CRM Leads, Pricelists
  * PDC Receivable/Payable
  * Budgets

DATA INTEGRITY FIX - Budget Constraints:
- Fixed invalid models.Constraint() syntax in ops_budget.py
- Converted to proper _sql_constraints format
- Now enforces unique budget per Branch/BU/Period
- Now enforces unique account per budget line

Production Audit: January 30, 2026
Audit Result: 2 Critical issues RESOLVED"

echo ""
echo "=== Pushing to remote ==="
git push origin main

echo "✅ Git commit complete"
```

---

## PHASE 6: FINAL VERIFICATION (15 min)

### Task 6.1: Complete Verification Report

```bash
echo "========================================"
echo "PHASE 6: FINAL VERIFICATION REPORT"
echo "========================================"

echo ""
echo "========== IT ADMIN BLINDNESS =========="
echo "Rules in XML file:"
grep -c "rule_it_admin_blind" /opt/gemini_odoo19/addons/ops_matrix_core/security/ir_rule.xml

echo ""
echo "Rules in database:"
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT COUNT(*) FROM ir_rule WHERE name LIKE '%IT Admin Blindness%';" -t

echo ""
echo "========== BUDGET CONSTRAINTS =========="
echo "Constraint syntax in code:"
grep "_sql_constraints" /opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_budget.py | head -2

echo ""
echo "Constraints in database:"
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT conname FROM pg_constraint WHERE conname LIKE '%budget%';" -t

echo ""
echo "========== MODULE STATUS =========="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT name, state, latest_version 
FROM ir_module_module 
WHERE name IN ('ops_matrix_core', 'ops_matrix_accounting');
"

echo ""
echo "=========================================="
echo "VERIFICATION COMPLETE"
echo "=========================================="
```

---

## SUCCESS CRITERIA

Before marking complete, verify:

- [ ] **20 IT Admin Blindness rules** exist in ir_rule.xml
- [ ] **20 IT Admin Blindness rules** loaded in database
- [ ] **Budget _sql_constraints** use correct syntax (not models.Constraint)
- [ ] **ops_matrix_core** module updates without errors
- [ ] **ops_matrix_accounting** module updates without errors
- [ ] **Git committed** with descriptive message
- [ ] **Odoo running** and accessible

---

## TESTING INSTRUCTIONS (Manual)

After deployment, test IT Admin Blindness:

1. **Create test user** with ONLY `group_ops_it_admin` group
2. **Login as test user**
3. **Try to access**:
   - Sales → Orders → Should see EMPTY list (not "Access Denied", just empty)
   - Purchase → Orders → Should see EMPTY list
   - Accounting → Invoices → Should see EMPTY list
4. **Verify CAN access**:
   - Settings → Users → Should work
   - Settings → Technical → Should work

If test user sees ANY sales/purchase/accounting data, the rules are not working correctly.

---

## ROLLBACK PROCEDURE

If something goes wrong:

```bash
# Restore backups
cd /opt/gemini_odoo19/addons
cp ops_matrix_core/security/ir_rule.xml.backup.* ops_matrix_core/security/ir_rule.xml
cp ops_matrix_accounting/models/ops_budget.py.backup.* ops_matrix_accounting/models/ops_budget.py

# Update modules
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting --stop-after-init

# Restart
docker restart gemini_odoo19
```

---

**BEGIN AUTONOMOUS EXECUTION NOW.**
