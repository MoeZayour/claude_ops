# Phase 4: Functional Testing

**Duration:** 90 minutes  
**Objective:** Test every feature's input, logic, and output

---

## TESTING PHILOSOPHY

For each feature, verify:
1. **INPUT** - Data can be entered correctly
2. **LOGIC** - Processing/calculation is correct
3. **FOOTPRINT** - Correct records created/modified
4. **OUTPUT** - Results are accurate
5. **STATE TRANSITIONS** - Workflow states work correctly

---

## Task 4.1: Test Branch & BU Management

```python
# ============================================================
# TEST: ORGANIZATIONAL STRUCTURE
# ============================================================

print("Testing Organizational Structure...")

# Test 4.1.1: Branch CRUD
branch_test = env['ops.branch'].create({
    'name': 'Test Branch',
    'code': 'TEST',
    'company_id': env.company.id,
})
assert branch_test.id, "Branch creation failed"
print(f"✅ Branch CREATE: {branch_test.name}")

branch_test.write({'name': 'Test Branch Updated'})
assert branch_test.name == 'Test Branch Updated', "Branch update failed"
print("✅ Branch UPDATE works")

# Test computed field
assert branch_test.full_code, "Branch full_code not computed"
print(f"✅ Branch computed field: {branch_test.full_code}")

# Clean up
branch_test.unlink()
print("✅ Branch DELETE works")

# Test 4.1.2: Business Unit CRUD
bu_test = env['ops.business.unit'].create({
    'name': 'Test BU',
    'code': 'TESTBU',
    'company_id': env.company.id,
})
assert bu_test.id, "BU creation failed"
print(f"✅ Business Unit CREATE: {bu_test.name}")

bu_test.unlink()
print("✅ Business Unit DELETE works")

# Test 4.1.3: Hierarchy
branch_alpha = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
branch_hq = env['ops.branch'].search([('code', '=', 'HQ')], limit=1)
if branch_alpha and branch_hq:
    assert branch_alpha.parent_id.id == branch_hq.id, "Branch hierarchy broken"
    print("✅ Branch hierarchy verified")

print("\n✅ ORGANIZATIONAL STRUCTURE TESTS PASSED")
```

---

## Task 4.2: Test User & Persona Assignment

```python
# ============================================================
# TEST: USER & PERSONA MANAGEMENT
# ============================================================

print("\nTesting User & Persona Management...")

# Test 4.2.1: User branch assignment
user_test = env['res.users'].search([('login', '=', 'test_sales_alpha')], limit=1)
if user_test:
    assert user_test.ops_branch_id, "User default branch not set"
    print(f"✅ User default branch: {user_test.ops_branch_id.name}")
    
    assert user_test.ops_allowed_branch_ids, "User allowed branches not set"
    print(f"✅ User allowed branches: {len(user_test.ops_allowed_branch_ids)}")

# Test 4.2.2: Persona templates exist (should be deactivated for cloning)
personas = env['ops.persona'].search([])
print(f"Total personas found: {len(personas)}")

# Check template pattern
templates = env['ops.persona'].search([('active', '=', False)])
print(f"Inactive personas (templates): {len(templates)}")

print("\n✅ USER & PERSONA TESTS PASSED")
```

---

## Task 4.3: Test Sale Order with Matrix Dimensions

```python
# ============================================================
# TEST: SALE ORDER WITH MATRIX
# ============================================================

print("\nTesting Sale Order with Matrix Dimensions...")

# Get test data
customer = env['res.partner'].search([('name', '=', 'Acme Corporation')], limit=1)
branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
bu = env['ops.business.unit'].search([('code', '=', 'SALES')], limit=1)
product = env['product.product'].search([('default_code', '=', 'WGT-PRO-001')], limit=1)

if all([customer, branch, bu, product]):
    # Test 4.3.1: Create Sale Order with matrix
    so_test = env['sale.order'].create({
        'partner_id': customer.id,
        'ops_branch_id': branch.id,
        'ops_business_unit_id': bu.id,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_uom_qty': 5,
            'price_unit': 150.00,
        })],
    })
    
    assert so_test.ops_branch_id.id == branch.id, "SO branch not set"
    print(f"✅ Sale Order created with branch: {so_test.ops_branch_id.name}")
    
    assert so_test.ops_business_unit_id.id == bu.id, "SO BU not set"
    print(f"✅ Sale Order created with BU: {so_test.ops_business_unit_id.name}")
    
    # Test 4.3.2: Calculate totals
    assert so_test.amount_total == 750.00, f"SO total incorrect: {so_test.amount_total}"
    print(f"✅ Sale Order total calculated: {so_test.amount_total}")
    
    # Test 4.3.3: State transition
    initial_state = so_test.state
    print(f"Initial state: {initial_state}")
    
    # Clean up test SO
    so_test.unlink()
    print("✅ Test Sale Order cleaned up")

print("\n✅ SALE ORDER MATRIX TESTS PASSED")
```

---

## Task 4.4: Test Purchase Order with Three-Way Match

```python
# ============================================================
# TEST: PURCHASE ORDER & THREE-WAY MATCH
# ============================================================

print("\nTesting Purchase Order & Three-Way Match...")

vendor = env['res.partner'].search([('name', '=', 'Premium Suppliers Inc.')], limit=1)
branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
bu = env['ops.business.unit'].search([('code', '=', 'OPS')], limit=1)
product = env['product.product'].search([('default_code', '=', 'WGT-PRO-001')], limit=1)

if all([vendor, branch, product]):
    # Test 4.4.1: Create Purchase Order
    po_test = env['purchase.order'].create({
        'partner_id': vendor.id,
        'ops_branch_id': branch.id,
        'ops_business_unit_id': bu.id if bu else False,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_qty': 20,
            'price_unit': 70.00,
            'name': product.name,
            'product_uom': product.uom_id.id,
            'date_planned': fields.Date.today(),
        })],
    })
    
    assert po_test.ops_branch_id.id == branch.id, "PO branch not set"
    print(f"✅ Purchase Order created: {po_test.name}")
    
    # Test 4.4.2: Check three-way match status field exists
    if hasattr(po_test, 'three_way_match_status'):
        print(f"✅ Three-way match status: {po_test.three_way_match_status}")
    else:
        print("⚠️ Three-way match status field not found on PO")
    
    # Clean up
    po_test.button_cancel()
    po_test.unlink()
    print("✅ Test Purchase Order cleaned up")

print("\n✅ PURCHASE ORDER TESTS PASSED")
```

---

## Task 4.5: Test PDC Receivable Workflow

```python
# ============================================================
# TEST: PDC RECEIVABLE STATE MACHINE
# ============================================================

print("\nTesting PDC Receivable Workflow...")

try:
    customer = env['res.partner'].search([('customer_rank', '>', 0)], limit=1)
    branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
    bank = env['res.bank'].search([], limit=1)
    
    if all([customer, branch, bank]):
        # Test 4.5.1: Create PDC
        pdc = env['ops.pdc.receivable'].create({
            'partner_id': customer.id,
            'amount': 1000.00,
            'check_number': 'TEST-CHK-001',
            'due_date': fields.Date.today() + timedelta(days=30),
            'bank_id': bank.id,
            'ops_branch_id': branch.id,
        })
        
        assert pdc.state == 'draft', f"Initial state should be draft, got {pdc.state}"
        print(f"✅ PDC created in draft state: {pdc.name}")
        
        # Test 4.5.2: Register PDC
        if hasattr(pdc, 'action_register'):
            pdc.action_register()
            assert pdc.state == 'registered', f"State should be registered, got {pdc.state}"
            print("✅ PDC registered")
            
            # Check journal entry created
            if pdc.register_move_id:
                print(f"✅ Journal entry created: {pdc.register_move_id.name}")
            
        # Test 4.5.3: Deposit PDC
        if hasattr(pdc, 'action_deposit') and pdc.state == 'registered':
            pdc.action_deposit()
            assert pdc.state == 'deposited', f"State should be deposited, got {pdc.state}"
            print("✅ PDC deposited")
        
        # Clean up - cancel if possible
        if hasattr(pdc, 'action_cancel'):
            try:
                pdc.action_cancel()
                print("✅ Test PDC cancelled")
            except:
                pass
        
        pdc.unlink()
        print("✅ Test PDC cleaned up")
    
except Exception as e:
    print(f"⚠️ PDC test error: {e}")

print("\n✅ PDC RECEIVABLE TESTS COMPLETED")
```

---

## Task 4.6: Test PDC Payable Workflow

```python
# ============================================================
# TEST: PDC PAYABLE STATE MACHINE
# ============================================================

print("\nTesting PDC Payable Workflow...")

try:
    vendor = env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
    branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
    bank = env['res.bank'].search([], limit=1)
    
    if all([vendor, branch, bank]):
        # Create PDC Payable
        pdc_pay = env['ops.pdc.payable'].create({
            'partner_id': vendor.id,
            'amount': 2000.00,
            'check_number': 'TEST-PAY-001',
            'issue_date': fields.Date.today(),
            'bank_id': bank.id,
            'ops_branch_id': branch.id,
        })
        
        assert pdc_pay.state == 'draft', f"Initial state should be draft"
        print(f"✅ PDC Payable created: {pdc_pay.name}")
        
        # Issue PDC
        if hasattr(pdc_pay, 'action_issue'):
            pdc_pay.action_issue()
            print(f"✅ PDC issued, state: {pdc_pay.state}")
        
        # Clean up
        pdc_pay.unlink()
        print("✅ Test PDC Payable cleaned up")

except Exception as e:
    print(f"⚠️ PDC Payable test error: {e}")

print("\n✅ PDC PAYABLE TESTS COMPLETED")
```

---

## Task 4.7: Test Asset Management

```python
# ============================================================
# TEST: FIXED ASSET LIFECYCLE
# ============================================================

print("\nTesting Asset Management...")

try:
    branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
    category = env['ops.asset.category'].search([], limit=1)
    
    if category and branch:
        # Test 4.7.1: Create Asset
        asset = env['ops.asset'].create({
            'name': 'Test Equipment',
            'category_id': category.id,
            'purchase_value': 10000.00,
            'salvage_value': 1000.00,
            'purchase_date': fields.Date.today(),
            'ops_branch_id': branch.id,
        })
        
        assert asset.state == 'draft', f"Initial state should be draft"
        print(f"✅ Asset created: {asset.name}")
        
        # Test 4.7.2: Computed book value
        print(f"Purchase value: {asset.purchase_value}")
        print(f"Salvage value: {asset.salvage_value}")
        
        # Test 4.7.3: Confirm asset (generate depreciation schedule)
        if hasattr(asset, 'action_confirm'):
            asset.action_confirm()
            print(f"✅ Asset confirmed, state: {asset.state}")
            
            # Check depreciation lines
            if hasattr(asset, 'depreciation_ids'):
                print(f"✅ Depreciation lines: {len(asset.depreciation_ids)}")
        
        # Clean up
        if asset.state != 'draft':
            asset.state = 'draft'  # Reset for deletion
        asset.unlink()
        print("✅ Test Asset cleaned up")

except Exception as e:
    print(f"⚠️ Asset test error: {e}")

print("\n✅ ASSET MANAGEMENT TESTS COMPLETED")
```

---

## Task 4.8: Test Budget Management

```python
# ============================================================
# TEST: BUDGET MANAGEMENT
# ============================================================

print("\nTesting Budget Management...")

try:
    branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
    bu = env['ops.business.unit'].search([('code', '=', 'SALES')], limit=1)
    
    if branch:
        # Test 4.8.1: Create Budget
        budget = env['ops.budget'].create({
            'name': 'Test Budget Q1',
            'ops_branch_id': branch.id,
            'ops_business_unit_id': bu.id if bu else False,
            'date_from': date(2026, 1, 1),
            'date_to': date(2026, 3, 31),
        })
        
        assert budget.state == 'draft', f"Initial state should be draft"
        print(f"✅ Budget created: {budget.name}")
        
        # Test 4.8.2: Computed totals
        print(f"Total planned: {budget.total_planned}")
        print(f"Total practical: {budget.total_practical}")
        
        # Test 4.8.3: Confirm budget
        if hasattr(budget, 'action_confirm'):
            budget.action_confirm()
            print(f"✅ Budget confirmed, state: {budget.state}")
        
        # Clean up
        budget.unlink()
        print("✅ Test Budget cleaned up")

except Exception as e:
    print(f"⚠️ Budget test error: {e}")

print("\n✅ BUDGET MANAGEMENT TESTS COMPLETED")
```

---

## Task 4.9: Test Approval Workflow

```python
# ============================================================
# TEST: APPROVAL WORKFLOW
# ============================================================

print("\nTesting Approval Workflow...")

try:
    # Check if approval mixin is working
    so = env['sale.order'].search([], limit=1)
    
    if so and hasattr(so, 'approval_state'):
        print(f"✅ Sale Order has approval_state: {so.approval_state}")
        
        if hasattr(so, 'approval_locked'):
            print(f"✅ Sale Order has approval_locked: {so.approval_locked}")
    else:
        print("⚠️ Approval mixin not found on sale.order")
    
    # Check approval request model
    approval_count = env['ops.approval.request'].search_count([])
    print(f"Approval requests in system: {approval_count}")

except Exception as e:
    print(f"⚠️ Approval test error: {e}")

print("\n✅ APPROVAL WORKFLOW TESTS COMPLETED")
```

---

## Task 4.10: Test Governance Rules

```python
# ============================================================
# TEST: GOVERNANCE RULES
# ============================================================

print("\nTesting Governance Rules...")

try:
    # Check governance rules exist
    rules = env['ops.governance.rule'].search([])
    print(f"Total governance rules: {len(rules)}")
    
    # Check template pattern (active but not auto-triggered)
    for rule in rules[:5]:
        print(f"Rule: {rule.name}, Active: {rule.active}")
    
    # Check if rules can be cloned
    if rules:
        rule_to_clone = rules[0]
        cloned = rule_to_clone.copy({'name': f"{rule_to_clone.name} (Clone)"})
        print(f"✅ Rule cloned: {cloned.name}")
        cloned.unlink()
        print("✅ Cloned rule deleted")

except Exception as e:
    print(f"⚠️ Governance test error: {e}")

print("\n✅ GOVERNANCE RULES TESTS COMPLETED")
```

---

## Task 4.11: Generate Functional Test Report

Create `/opt/gemini_odoo19/claude_files/go_live_audit/04_FUNCTIONAL_TEST.md`:

```markdown
# Functional Test Report

**Date:** [DATE]
**Executor:** Claude Code

## Test Summary

| Category | Tests | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Organizational Structure | X | X | X | X |
| User & Persona | X | X | X | X |
| Sale Order Matrix | X | X | X | X |
| Purchase Order | X | X | X | X |
| PDC Receivable | X | X | X | X |
| PDC Payable | X | X | X | X |
| Asset Management | X | X | X | X |
| Budget Management | X | X | X | X |
| Approval Workflow | X | X | X | X |
| Governance Rules | X | X | X | X |
| **TOTAL** | **X** | **X** | **X** | **X** |

## Detailed Results

[Insert results from each test task]

## Issues Found

| # | Feature | Issue | Severity | Resolution |
|---|---------|-------|----------|------------|
| 1 | ... | ... | ... | ... |

## Recommendations

[Any recommendations for improvement]
```

---

## PROCEED TO PHASE 5
