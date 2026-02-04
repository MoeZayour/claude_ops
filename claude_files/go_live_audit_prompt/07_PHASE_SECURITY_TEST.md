# Phase 6: Security Testing

**Duration:** 45 minutes  
**Objective:** Verify all security rules work correctly

---

## SECURITY TESTING SCOPE

1. **IT Admin Blindness** - 24 models blocked
2. **Branch Isolation** - Users only see own branch data
3. **Cost/Margin Visibility** - Hidden from unauthorized users
4. **Segregation of Duties** - Creator ≠ Approver

---

## Task 6.1: Test IT Admin Blindness

```python
# ============================================================
# IT ADMIN BLINDNESS TEST
# ============================================================

print("Testing IT Admin Blindness...")
print("="*60)

# Get IT Admin user
it_admin = env['res.users'].search([('login', '=', 'test_it_admin')], limit=1)

if not it_admin:
    print("❌ IT Admin user not found - creating...")
    it_admin = env['res.users'].create({
        'login': 'test_it_admin',
        'name': 'IT Administrator',
        'password': '123',
    })
    it_group = env.ref('ops_matrix_core.group_ops_it_admin', raise_if_not_found=False)
    if it_group:
        it_admin.groups_id = [(4, it_group.id)]

print(f"Testing as: {it_admin.name} (ID: {it_admin.id})")

# Models that should be BLOCKED for IT Admin
blocked_models = [
    'sale.order',
    'sale.order.line',
    'purchase.order',
    'purchase.order.line',
    'account.move',
    'account.move.line',
    'account.payment',
    'stock.picking',
    'stock.move',
    'stock.quant',
]

print("\nBlocked Models Test:")
blindness_results = []

for model_name in blocked_models:
    try:
        admin_count = env[model_name].search_count([])
        it_admin_env = env(user=it_admin.id)
        it_count = it_admin_env[model_name].search_count([])
        
        if it_count == 0 and admin_count > 0:
            result = "✅ BLOCKED"
            status = "PASS"
        elif it_count == 0 and admin_count == 0:
            result = "⚠️ NO DATA"
            status = "SKIP"
        else:
            result = f"❌ VISIBLE ({it_count}/{admin_count})"
            status = "FAIL"
        
        blindness_results.append({
            'model': model_name,
            'admin_count': admin_count,
            'it_admin_count': it_count,
            'status': status
        })
        
        print(f"  {model_name}: {result}")
        
    except Exception as e:
        print(f"  {model_name}: ⚠️ Error - {e}")

# Test OPS-specific models
ops_blocked = [
    'ops.pdc.receivable',
    'ops.pdc.payable',
    'ops.budget',
    'ops.asset',
]

print("\nOPS-specific Blocked Models:")
for model_name in ops_blocked:
    try:
        admin_count = env[model_name].search_count([])
        it_admin_env = env(user=it_admin.id)
        it_count = it_admin_env[model_name].search_count([])
        
        if it_count == 0 and admin_count > 0:
            print(f"  {model_name}: ✅ BLOCKED ({it_count}/{admin_count})")
        elif it_count == 0 and admin_count == 0:
            print(f"  {model_name}: ⚠️ NO DATA")
        else:
            print(f"  {model_name}: ❌ VISIBLE ({it_count}/{admin_count})")
            
    except KeyError:
        print(f"  {model_name}: ⚠️ Model not found")
    except Exception as e:
        print(f"  {model_name}: ⚠️ Error - {e}")

print("\n✅ IT ADMIN BLINDNESS TEST COMPLETED")
```

---

## Task 6.2: Test Branch Isolation

```python
# ============================================================
# BRANCH ISOLATION TEST
# ============================================================

print("\nTesting Branch Isolation...")
print("="*60)

# Get test users
user_alpha = env['res.users'].search([('login', '=', 'test_sales_alpha')], limit=1)
user_beta = env['res.users'].search([('login', '=', 'test_sales_beta')], limit=1)

# Get branches
branch_alpha = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
branch_beta = env['ops.branch'].search([('code', '=', 'BETA')], limit=1)

if not all([user_alpha, user_beta, branch_alpha, branch_beta]):
    print("⚠️ Missing test users or branches - test incomplete")
else:
    print(f"User Alpha: {user_alpha.name}, Branch: {user_alpha.ops_branch_id.name if user_alpha.ops_branch_id else 'None'}")
    print(f"User Beta: {user_beta.name}, Branch: {user_beta.ops_branch_id.name if user_beta.ops_branch_id else 'None'}")
    
    # Create test sale orders in each branch
    customer = env['res.partner'].search([('customer_rank', '>', 0)], limit=1)
    product = env['product.product'].search([], limit=1)
    
    # Create SO in Alpha branch
    so_alpha = env['sale.order'].create({
        'partner_id': customer.id,
        'ops_branch_id': branch_alpha.id,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_uom_qty': 1,
            'price_unit': 100,
        })],
    })
    print(f"\nCreated SO in Alpha: {so_alpha.name}")
    
    # Create SO in Beta branch
    so_beta = env['sale.order'].create({
        'partner_id': customer.id,
        'ops_branch_id': branch_beta.id,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_uom_qty': 1,
            'price_unit': 100,
        })],
    })
    print(f"Created SO in Beta: {so_beta.name}")
    
    # Test: User Alpha should NOT see Beta's SO
    env_alpha = env(user=user_alpha.id)
    alpha_visible_sos = env_alpha['sale.order'].search([('id', 'in', [so_alpha.id, so_beta.id])])
    
    can_see_own = so_alpha.id in alpha_visible_sos.ids
    can_see_other = so_beta.id in alpha_visible_sos.ids
    
    print(f"\nUser Alpha visibility test:")
    print(f"  Can see own branch SO (Alpha): {'✅ YES' if can_see_own else '❌ NO'}")
    print(f"  Can see other branch SO (Beta): {'❌ YES (SECURITY ISSUE!)' if can_see_other else '✅ NO (Correct)'}")
    
    # Test: User Beta should NOT see Alpha's SO
    env_beta = env(user=user_beta.id)
    beta_visible_sos = env_beta['sale.order'].search([('id', 'in', [so_alpha.id, so_beta.id])])
    
    can_see_own = so_beta.id in beta_visible_sos.ids
    can_see_other = so_alpha.id in beta_visible_sos.ids
    
    print(f"\nUser Beta visibility test:")
    print(f"  Can see own branch SO (Beta): {'✅ YES' if can_see_own else '❌ NO'}")
    print(f"  Can see other branch SO (Alpha): {'❌ YES (SECURITY ISSUE!)' if can_see_other else '✅ NO (Correct)'}")
    
    # Clean up test SOs
    so_alpha.unlink()
    so_beta.unlink()
    print("\n✅ Test SOs cleaned up")

print("\n✅ BRANCH ISOLATION TEST COMPLETED")
```

---

## Task 6.3: Test Cost/Margin Visibility

```python
# ============================================================
# COST/MARGIN VISIBILITY TEST
# ============================================================

print("\nTesting Cost/Margin Visibility...")
print("="*60)

# Get users with and without cost access
user_sales = env['res.users'].search([('login', '=', 'test_sales_alpha')], limit=1)  # NO cost access
user_cfo = env['res.users'].search([('login', '=', 'test_cfo')], limit=1)  # HAS cost access

cost_group = env.ref('ops_matrix_core.group_ops_see_cost', raise_if_not_found=False)
margin_group = env.ref('ops_matrix_core.group_ops_see_margin', raise_if_not_found=False)

if user_sales and cost_group:
    has_cost = cost_group.id in user_sales.groups_id.ids
    print(f"Sales Rep has cost access: {'❌ YES (WRONG!)' if has_cost else '✅ NO (Correct)'}")

if user_cfo and cost_group:
    has_cost = cost_group.id in user_cfo.groups_id.ids
    print(f"CFO has cost access: {'✅ YES' if has_cost else '❌ NO (Should have access!)'}")

# Test field visibility in views
try:
    product = env['product.product'].search([], limit=1)
    if product:
        # Check if standard_price field exists
        print(f"\nProduct: {product.name}")
        print(f"  List Price: {product.list_price}")
        print(f"  Cost Price (standard_price): {product.standard_price}")
        
        # Check if field is visible in form view
        form_view = env['product.product'].get_view(view_type='form')
        arch = form_view.get('arch', '')
        
        cost_in_view = 'standard_price' in arch
        groups_check = 'group_ops_see_cost' in arch
        
        print(f"\n  Cost field in view: {'Yes' if cost_in_view else 'No'}")
        print(f"  Has group restriction: {'✅ Yes' if groups_check else '⚠️ No'}")
except Exception as e:
    print(f"⚠️ Cost visibility test error: {e}")

print("\n✅ COST/MARGIN VISIBILITY TEST COMPLETED")
```

---

## Task 6.4: Test Segregation of Duties

```python
# ============================================================
# SEGREGATION OF DUTIES TEST
# ============================================================

print("\nTesting Segregation of Duties...")
print("="*60)

# Test: Creator cannot approve their own document
try:
    user_sales = env['res.users'].search([('login', '=', 'test_sales_alpha')], limit=1)
    customer = env['res.partner'].search([('customer_rank', '>', 0)], limit=1)
    product = env['product.product'].search([], limit=1)
    branch = env['ops.branch'].search([('code', '=', 'ALPHA')], limit=1)
    
    if all([user_sales, customer, product, branch]):
        # Create SO as sales user
        env_sales = env(user=user_sales.id)
        
        so = env_sales['sale.order'].create({
            'partner_id': customer.id,
            'ops_branch_id': branch.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': 100,
            })],
        })
        
        print(f"Created SO by {user_sales.name}: {so.name}")
        print(f"  Created by (create_uid): {so.create_uid.name}")
        
        # Try to approve as the same user
        if hasattr(so, 'action_submit_approval'):
            try:
                so.action_submit_approval()
                print("  Submitted for approval")
                
                # Try to approve own document
                if hasattr(so, 'action_approve'):
                    try:
                        so.action_approve()
                        print("  ❌ SECURITY ISSUE: User approved own document!")
                    except Exception as sod_error:
                        print(f"  ✅ SoD enforced: {sod_error}")
            except Exception as e:
                print(f"  ⚠️ Approval submit error: {e}")
        else:
            print("  ⚠️ action_submit_approval not found on sale.order")
        
        # Clean up
        so_admin = env['sale.order'].browse(so.id)
        so_admin.unlink()
        print("  Test SO cleaned up")
        
except Exception as e:
    print(f"⚠️ SoD test error: {e}")

print("\n✅ SEGREGATION OF DUTIES TEST COMPLETED")
```

---

## Task 6.5: Test Record Rules

```python
# ============================================================
# RECORD RULES VERIFICATION
# ============================================================

print("\nVerifying Record Rules...")
print("="*60)

# Get all OPS-related record rules
rules = env['ir.rule'].search([
    '|', '|',
    ('name', 'ilike', 'ops'),
    ('name', 'ilike', 'branch'),
    ('name', 'ilike', 'it_admin'),
])

print(f"Total OPS-related record rules: {len(rules)}")

# Categorize rules
it_admin_rules = rules.filtered(lambda r: 'it_admin' in r.name.lower() or 'it admin' in r.name.lower())
branch_rules = rules.filtered(lambda r: 'branch' in r.name.lower())
ops_rules = rules.filtered(lambda r: 'ops' in r.name.lower())

print(f"\nIT Admin Blindness rules: {len(it_admin_rules)}")
for rule in it_admin_rules[:10]:
    print(f"  - {rule.name}: {rule.model_id.model}")

print(f"\nBranch Isolation rules: {len(branch_rules)}")
for rule in branch_rules[:10]:
    print(f"  - {rule.name}: {rule.model_id.model}")

print("\n✅ RECORD RULES VERIFICATION COMPLETED")
```

---

## Task 6.6: Test Access Control Lists

```python
# ============================================================
# ACCESS CONTROL VERIFICATION
# ============================================================

print("\nVerifying Access Control Lists...")
print("="*60)

# Get all OPS-related ACLs
acls = env['ir.model.access'].search([
    '|',
    ('name', 'ilike', 'ops'),
    ('model_id.model', 'ilike', 'ops.'),
])

print(f"Total OPS-related ACLs: {len(acls)}")

# Check for missing ACLs on OPS models
ops_models = env['ir.model'].search([('model', 'like', 'ops.%')])

print(f"\nOPS Models: {len(ops_models)}")

missing_acl = []
for model in ops_models:
    model_acls = acls.filtered(lambda a: a.model_id.id == model.id)
    if not model_acls:
        missing_acl.append(model.model)
        print(f"  ⚠️ {model.model}: NO ACL DEFINED")
    else:
        print(f"  ✅ {model.model}: {len(model_acls)} ACLs")

if missing_acl:
    print(f"\n❌ Models missing ACL definitions: {len(missing_acl)}")
else:
    print(f"\n✅ All OPS models have ACL definitions")

print("\n✅ ACCESS CONTROL VERIFICATION COMPLETED")
```

---

## Task 6.7: Generate Security Test Report

Create `/opt/gemini_odoo19/claude_files/go_live_audit/06_SECURITY_TEST.md`:

```markdown
# Security Test Report

**Date:** [DATE]
**Executor:** Claude Code

## Test Summary

| Category | Tests | Passed | Failed | Critical |
|----------|-------|--------|--------|----------|
| IT Admin Blindness | X | X | X | X |
| Branch Isolation | X | X | X | X |
| Cost/Margin Visibility | X | X | X | X |
| Segregation of Duties | X | X | X | X |
| Record Rules | X | X | X | X |
| Access Control | X | X | X | X |
| **TOTAL** | **X** | **X** | **X** | **X** |

## IT Admin Blindness Results

| Model | Admin Count | IT Admin Count | Status |
|-------|-------------|----------------|--------|
| sale.order | X | 0 | ✅ BLOCKED |
| purchase.order | X | 0 | ✅ BLOCKED |
| account.move | X | 0 | ✅ BLOCKED |
| ... | ... | ... | ... |

## Branch Isolation Results

| Test | User | Expected | Actual | Status |
|------|------|----------|--------|--------|
| User Alpha sees Alpha SO | test_sales_alpha | YES | YES | ✅ |
| User Alpha sees Beta SO | test_sales_alpha | NO | NO | ✅ |
| User Beta sees Beta SO | test_sales_beta | YES | YES | ✅ |
| User Beta sees Alpha SO | test_sales_beta | NO | NO | ✅ |

## Cost/Margin Visibility

| User | Has Cost Group | Has Margin Group | Status |
|------|----------------|------------------|--------|
| test_sales_alpha | NO | NO | ✅ |
| test_cfo | YES | YES | ✅ |

## Segregation of Duties

| Test | Result |
|------|--------|
| Creator cannot approve own document | ✅ Enforced |

## Record Rules Summary

| Category | Count | Status |
|----------|-------|--------|
| IT Admin Blindness Rules | X | ✅ |
| Branch Isolation Rules | X | ✅ |
| Other OPS Rules | X | ✅ |

## Security Issues Found

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| - | - | No issues found | - |

## Recommendations

[Security hardening recommendations if any]
```

---

## Git Commit (if all tests pass)

```bash
cd /opt/gemini_odoo19
git add -A

git commit -m "[GO-LIVE] Phase 4-6: Testing complete

Functional Tests:
- Organizational structure: PASS
- User & Persona: PASS
- Sale/Purchase Orders: PASS
- PDC Receivable/Payable: PASS
- Asset Management: PASS
- Budget Management: PASS
- Approval Workflows: PASS
- Governance Rules: PASS

UI Tests:
- All views load: PASS
- Buttons functional: PASS
- Theme applied: PASS

Security Tests:
- IT Admin Blindness: PASS
- Branch Isolation: PASS
- Cost/Margin Lock: PASS
- Segregation of Duties: PASS

Tested: Comprehensive
Issues: [X] found and documented"

git push origin main
```

---

## PROCEED TO PHASE 7 (Final Report)
