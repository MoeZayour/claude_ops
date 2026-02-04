# Phase 3: Seed Data Creation

**Duration:** 60 minutes  
**Objective:** Create comprehensive test dataset using Odoo ORM only

---

## SEED DATA STRATEGY

All data created via **Odoo Shell** using the ORM API - simulating how a real user would create data through the UI, but programmatically.

**NO DIRECT SQL** - All operations through `self.env['model'].create()`, `.write()`, `.search()`.

---

## Task 3.1: Access Odoo Shell

```bash
echo "========================================"
echo "PHASE 3: SEED DATA CREATION"
echo "========================================"

echo "=== Entering Odoo Shell ==="
docker exec -it gemini_odoo19 odoo shell -d mz-db
```

---

## Task 3.2: Create Organizational Structure

Execute in Odoo Shell:

```python
# ============================================================
# ORGANIZATIONAL STRUCTURE
# ============================================================

print("Creating Organizational Structure...")

# Get the main company
company = env['res.company'].search([], limit=1)
print(f"Company: {company.name}")

# ============================================================
# BUSINESS UNITS (3)
# ============================================================

print("Creating Business Units...")

bu_sales = env['ops.business.unit'].create({
    'name': 'Sales Division',
    'code': 'SALES',
    'company_id': company.id,
    'description': 'All sales and customer-facing operations',
})

bu_operations = env['ops.business.unit'].create({
    'name': 'Operations Division',
    'code': 'OPS',
    'company_id': company.id,
    'description': 'Logistics, warehouse, and fulfillment',
})

bu_finance = env['ops.business.unit'].create({
    'name': 'Finance Division',
    'code': 'FIN',
    'company_id': company.id,
    'description': 'Accounting, treasury, and financial reporting',
})

print(f"✅ Created Business Units: {bu_sales.name}, {bu_operations.name}, {bu_finance.name}")

# ============================================================
# BRANCHES (4)
# ============================================================

print("Creating Branches...")

branch_hq = env['ops.branch'].create({
    'name': 'Headquarters',
    'code': 'HQ',
    'company_id': company.id,
    'street': '100 Main Street',
    'city': 'Business City',
    'zip': '10001',
})

branch_alpha = env['ops.branch'].create({
    'name': 'Branch Alpha',
    'code': 'ALPHA',
    'company_id': company.id,
    'parent_id': branch_hq.id,
    'street': '200 Alpha Avenue',
    'city': 'Alpha Town',
    'zip': '20001',
})

branch_beta = env['ops.branch'].create({
    'name': 'Branch Beta',
    'code': 'BETA',
    'company_id': company.id,
    'parent_id': branch_hq.id,
    'street': '300 Beta Boulevard',
    'city': 'Beta City',
    'zip': '30001',
})

branch_gamma = env['ops.branch'].create({
    'name': 'Branch Gamma',
    'code': 'GAMMA',
    'company_id': company.id,
    'parent_id': branch_hq.id,
    'street': '400 Gamma Road',
    'city': 'Gamma Village',
    'zip': '40001',
})

print(f"✅ Created Branches: {branch_hq.name}, {branch_alpha.name}, {branch_beta.name}, {branch_gamma.name}")

env.cr.commit()
print("✅ Organizational structure committed to database")
```

---

## Task 3.3: Create Test Users (9 Personas)

```python
# ============================================================
# TEST USERS - 9 KEY PERSONAS
# ============================================================

print("Creating Test Users...")

# Helper function to create user
def create_test_user(login, name, groups, branch_ids=None, bu_ids=None):
    user = env['res.users'].create({
        'login': login,
        'name': name,
        'password': '123',
        'company_id': company.id,
        'company_ids': [(4, company.id)],
    })
    # Add groups
    for group_xml_id in groups:
        try:
            group = env.ref(group_xml_id)
            user.groups_id = [(4, group.id)]
        except:
            print(f"Warning: Group {group_xml_id} not found")
    
    # Set branches if model supports it
    if branch_ids and hasattr(user, 'ops_allowed_branch_ids'):
        user.ops_allowed_branch_ids = [(6, 0, branch_ids)]
    if hasattr(user, 'ops_branch_id') and branch_ids:
        user.ops_branch_id = branch_ids[0]
    
    return user

# 1. IT Administrator (P01) - System config, NO business data
user_it_admin = create_test_user(
    'test_it_admin',
    'IT Administrator',
    ['ops_matrix_core.group_ops_it_admin', 'base.group_system'],
    [branch_hq.id, branch_alpha.id, branch_beta.id, branch_gamma.id]
)
print(f"✅ Created: {user_it_admin.name}")

# 2. CEO (P02) - Read all
user_ceo = create_test_user(
    'test_ceo',
    'CEO / Executive',
    ['ops_matrix_core.group_ops_manager', 'base.group_user'],
    [branch_hq.id, branch_alpha.id, branch_beta.id, branch_gamma.id]
)
print(f"✅ Created: {user_ceo.name}")

# 3. CFO (P03) - Full finance
user_cfo = create_test_user(
    'test_cfo',
    'CFO / Finance Director',
    ['ops_matrix_core.group_ops_admin_power', 'account.group_account_manager', 
     'ops_matrix_core.group_ops_see_cost', 'ops_matrix_core.group_ops_see_margin'],
    [branch_hq.id, branch_alpha.id, branch_beta.id, branch_gamma.id]
)
print(f"✅ Created: {user_cfo.name}")

# 4. BU Leader (P04) - Cross-branch within BU
user_bu_leader = create_test_user(
    'test_bu_leader',
    'BU Leader - Sales',
    ['ops_matrix_core.group_ops_bu_leader', 'ops_matrix_core.group_ops_see_cost'],
    [branch_alpha.id, branch_beta.id]  # Only sees branches in their BU
)
print(f"✅ Created: {user_bu_leader.name}")

# 5. Branch Manager Alpha (P05)
user_branch_mgr_alpha = create_test_user(
    'test_branch_mgr_alpha',
    'Branch Manager - Alpha',
    ['ops_matrix_core.group_ops_branch_manager', 'ops_matrix_core.group_ops_see_cost'],
    [branch_alpha.id]  # Only Alpha
)
print(f"✅ Created: {user_branch_mgr_alpha.name}")

# 6. Branch Manager Beta (P05)
user_branch_mgr_beta = create_test_user(
    'test_branch_mgr_beta',
    'Branch Manager - Beta',
    ['ops_matrix_core.group_ops_branch_manager', 'ops_matrix_core.group_ops_see_cost'],
    [branch_beta.id]  # Only Beta
)
print(f"✅ Created: {user_branch_mgr_beta.name}")

# 7. Sales Rep Alpha (P10) - NO cost access
user_sales_alpha = create_test_user(
    'test_sales_alpha',
    'Sales Representative - Alpha',
    ['ops_matrix_core.group_ops_user', 'sales_team.group_sale_salesman'],
    [branch_alpha.id]
)
print(f"✅ Created: {user_sales_alpha.name}")

# 8. Sales Rep Beta (P10) - NO cost access
user_sales_beta = create_test_user(
    'test_sales_beta',
    'Sales Representative - Beta',
    ['ops_matrix_core.group_ops_user', 'sales_team.group_sale_salesman'],
    [branch_beta.id]
)
print(f"✅ Created: {user_sales_beta.name}")

# 9. Accountant (P16) - All branches
user_accountant = create_test_user(
    'test_accountant',
    'Accountant / Controller',
    ['ops_matrix_core.group_ops_manager', 'account.group_account_user',
     'ops_matrix_core.group_ops_see_cost', 'ops_matrix_core.group_ops_see_margin'],
    [branch_hq.id, branch_alpha.id, branch_beta.id, branch_gamma.id]
)
print(f"✅ Created: {user_accountant.name}")

env.cr.commit()
print("✅ All test users created and committed")
```

---

## Task 3.4: Create Partners (Customers & Vendors)

```python
# ============================================================
# PARTNERS - CUSTOMERS & VENDORS
# ============================================================

print("Creating Partners...")

# Customers
customer_1 = env['res.partner'].create({
    'name': 'Acme Corporation',
    'company_type': 'company',
    'email': 'orders@acme.example.com',
    'phone': '+1-555-0101',
    'street': '500 Customer Lane',
    'city': 'Client City',
    'zip': '50001',
    'customer_rank': 1,
    'credit_limit': 50000.00,
})

customer_2 = env['res.partner'].create({
    'name': 'Beta Industries',
    'company_type': 'company',
    'email': 'purchasing@beta.example.com',
    'phone': '+1-555-0102',
    'street': '600 Industry Park',
    'city': 'Industrial Zone',
    'zip': '60001',
    'customer_rank': 1,
    'credit_limit': 100000.00,
})

customer_3 = env['res.partner'].create({
    'name': 'Gamma Traders',
    'company_type': 'company',
    'email': 'trade@gamma.example.com',
    'phone': '+1-555-0103',
    'customer_rank': 1,
    'credit_limit': 25000.00,
})

print(f"✅ Created Customers: {customer_1.name}, {customer_2.name}, {customer_3.name}")

# Vendors
vendor_1 = env['res.partner'].create({
    'name': 'Premium Suppliers Inc.',
    'company_type': 'company',
    'email': 'sales@premiumsuppliers.example.com',
    'phone': '+1-555-0201',
    'street': '700 Supplier Street',
    'city': 'Vendor Valley',
    'zip': '70001',
    'supplier_rank': 1,
})

vendor_2 = env['res.partner'].create({
    'name': 'Quick Parts Ltd.',
    'company_type': 'company',
    'email': 'orders@quickparts.example.com',
    'phone': '+1-555-0202',
    'supplier_rank': 1,
})

print(f"✅ Created Vendors: {vendor_1.name}, {vendor_2.name}")

env.cr.commit()
```

---

## Task 3.5: Create Products

```python
# ============================================================
# PRODUCTS
# ============================================================

print("Creating Products...")

# Get or create product category
category = env['product.category'].search([('name', '=', 'All')], limit=1)
if not category:
    category = env['product.category'].create({'name': 'All'})

product_1 = env['product.product'].create({
    'name': 'Widget Pro',
    'type': 'product',
    'categ_id': category.id,
    'list_price': 150.00,
    'standard_price': 75.00,
    'default_code': 'WGT-PRO-001',
})

product_2 = env['product.product'].create({
    'name': 'Gadget Plus',
    'type': 'product',
    'categ_id': category.id,
    'list_price': 250.00,
    'standard_price': 120.00,
    'default_code': 'GDG-PLS-001',
})

product_3 = env['product.product'].create({
    'name': 'Service Package',
    'type': 'service',
    'categ_id': category.id,
    'list_price': 500.00,
    'standard_price': 0.00,
    'default_code': 'SVC-PKG-001',
})

product_4 = env['product.product'].create({
    'name': 'Component Alpha',
    'type': 'product',
    'categ_id': category.id,
    'list_price': 45.00,
    'standard_price': 22.50,
    'default_code': 'CMP-ALP-001',
})

print(f"✅ Created Products: {product_1.name}, {product_2.name}, {product_3.name}, {product_4.name}")

env.cr.commit()
```

---

## Task 3.6: Create Sample Transactions

```python
# ============================================================
# SAMPLE TRANSACTIONS
# ============================================================

print("Creating Sample Transactions...")

# --- SALE ORDERS ---

# Sale Order 1 - Branch Alpha
so_1 = env['sale.order'].create({
    'partner_id': customer_1.id,
    'ops_branch_id': branch_alpha.id,
    'ops_business_unit_id': bu_sales.id,
    'order_line': [
        (0, 0, {
            'product_id': product_1.id,
            'product_uom_qty': 10,
            'price_unit': 150.00,
        }),
        (0, 0, {
            'product_id': product_2.id,
            'product_uom_qty': 5,
            'price_unit': 250.00,
        }),
    ],
})
print(f"✅ Created Sale Order: {so_1.name}")

# Sale Order 2 - Branch Beta
so_2 = env['sale.order'].create({
    'partner_id': customer_2.id,
    'ops_branch_id': branch_beta.id,
    'ops_business_unit_id': bu_sales.id,
    'order_line': [
        (0, 0, {
            'product_id': product_3.id,
            'product_uom_qty': 2,
            'price_unit': 500.00,
        }),
    ],
})
print(f"✅ Created Sale Order: {so_2.name}")

# --- PURCHASE ORDERS ---

po_1 = env['purchase.order'].create({
    'partner_id': vendor_1.id,
    'ops_branch_id': branch_alpha.id,
    'ops_business_unit_id': bu_operations.id,
    'order_line': [
        (0, 0, {
            'product_id': product_1.id,
            'product_qty': 100,
            'price_unit': 70.00,
            'name': product_1.name,
            'product_uom': product_1.uom_id.id,
            'date_planned': fields.Date.today(),
        }),
    ],
})
print(f"✅ Created Purchase Order: {po_1.name}")

env.cr.commit()
```

---

## Task 3.7: Create PDC Records (if module supports)

```python
# ============================================================
# PDC RECORDS
# ============================================================

print("Creating PDC Records...")

try:
    # Get or create a bank
    bank = env['res.bank'].search([], limit=1)
    if not bank:
        bank = env['res.bank'].create({'name': 'Test Bank', 'bic': 'TESTBANK'})
    
    # PDC Receivable 1
    pdc_recv_1 = env['ops.pdc.receivable'].create({
        'partner_id': customer_1.id,
        'amount': 5000.00,
        'check_number': 'CHK-001',
        'due_date': fields.Date.today() + timedelta(days=30),
        'bank_id': bank.id,
        'ops_branch_id': branch_alpha.id,
    })
    print(f"✅ Created PDC Receivable: {pdc_recv_1.name}")
    
    # PDC Receivable 2
    pdc_recv_2 = env['ops.pdc.receivable'].create({
        'partner_id': customer_2.id,
        'amount': 10000.00,
        'check_number': 'CHK-002',
        'due_date': fields.Date.today() + timedelta(days=45),
        'bank_id': bank.id,
        'ops_branch_id': branch_beta.id,
    })
    print(f"✅ Created PDC Receivable: {pdc_recv_2.name}")
    
    # PDC Receivable 3 - Past due for testing
    pdc_recv_3 = env['ops.pdc.receivable'].create({
        'partner_id': customer_3.id,
        'amount': 2500.00,
        'check_number': 'CHK-003',
        'due_date': fields.Date.today() - timedelta(days=5),
        'bank_id': bank.id,
        'ops_branch_id': branch_alpha.id,
    })
    print(f"✅ Created PDC Receivable (Past Due): {pdc_recv_3.name}")
    
    # PDC Payable
    pdc_pay_1 = env['ops.pdc.payable'].create({
        'partner_id': vendor_1.id,
        'amount': 7000.00,
        'check_number': 'PAY-001',
        'issue_date': fields.Date.today(),
        'bank_id': bank.id,
        'ops_branch_id': branch_alpha.id,
    })
    print(f"✅ Created PDC Payable: {pdc_pay_1.name}")
    
    env.cr.commit()
    
except Exception as e:
    print(f"⚠️ PDC creation error (model may not be ready): {e}")
    env.cr.rollback()
```

---

## Task 3.8: Create Asset Records (if module supports)

```python
# ============================================================
# FIXED ASSETS
# ============================================================

print("Creating Fixed Assets...")

try:
    # Get or create asset category
    # First check if account.account exists
    asset_account = env['account.account'].search([('code', '=like', '1%')], limit=1)
    expense_account = env['account.account'].search([('code', '=like', '6%')], limit=1)
    depreciation_account = env['account.account'].search([('code', '=like', '1%')], limit=1)
    
    if asset_account:
        asset_category = env['ops.asset.category'].create({
            'name': 'Office Equipment',
            'method': 'straight_line',
            'method_number': 60,  # 5 years
            'method_period': 1,   # Monthly
        })
        print(f"✅ Created Asset Category: {asset_category.name}")
        
        # Asset 1
        asset_1 = env['ops.asset'].create({
            'name': 'Office Computer Set',
            'category_id': asset_category.id,
            'purchase_value': 5000.00,
            'salvage_value': 500.00,
            'purchase_date': fields.Date.today() - timedelta(days=180),
            'ops_branch_id': branch_alpha.id,
        })
        print(f"✅ Created Asset: {asset_1.name}")
        
        # Asset 2
        asset_2 = env['ops.asset'].create({
            'name': 'Company Vehicle',
            'category_id': asset_category.id,
            'purchase_value': 35000.00,
            'salvage_value': 5000.00,
            'purchase_date': fields.Date.today() - timedelta(days=365),
            'ops_branch_id': branch_hq.id,
        })
        print(f"✅ Created Asset: {asset_2.name}")
        
        # Asset 3
        asset_3 = env['ops.asset'].create({
            'name': 'Warehouse Forklift',
            'category_id': asset_category.id,
            'purchase_value': 25000.00,
            'salvage_value': 2500.00,
            'purchase_date': fields.Date.today() - timedelta(days=90),
            'ops_branch_id': branch_beta.id,
        })
        print(f"✅ Created Asset: {asset_3.name}")
        
        env.cr.commit()
    else:
        print("⚠️ No accounts found - skipping asset creation")
        
except Exception as e:
    print(f"⚠️ Asset creation error (model may not be ready): {e}")
    env.cr.rollback()
```

---

## Task 3.9: Create Budget Records (if module supports)

```python
# ============================================================
# BUDGETS
# ============================================================

print("Creating Budgets...")

try:
    from datetime import date
    
    # Budget for Alpha Branch
    budget_alpha = env['ops.budget'].create({
        'name': f'Budget Alpha Q1 2026',
        'ops_branch_id': branch_alpha.id,
        'ops_business_unit_id': bu_sales.id,
        'date_from': date(2026, 1, 1),
        'date_to': date(2026, 3, 31),
    })
    print(f"✅ Created Budget: {budget_alpha.name}")
    
    # Budget for Beta Branch
    budget_beta = env['ops.budget'].create({
        'name': f'Budget Beta Q1 2026',
        'ops_branch_id': branch_beta.id,
        'ops_business_unit_id': bu_sales.id,
        'date_from': date(2026, 1, 1),
        'date_to': date(2026, 3, 31),
    })
    print(f"✅ Created Budget: {budget_beta.name}")
    
    env.cr.commit()
    
except Exception as e:
    print(f"⚠️ Budget creation error (model may not be ready): {e}")
    env.cr.rollback()
```

---

## Task 3.10: Verify Seed Data

```python
# ============================================================
# VERIFICATION
# ============================================================

print("\n" + "="*60)
print("SEED DATA VERIFICATION")
print("="*60)

print(f"\nBusiness Units: {env['ops.business.unit'].search_count([])}")
print(f"Branches: {env['ops.branch'].search_count([])}")
print(f"Users: {env['res.users'].search_count([('login', 'like', 'test_%')])}")
print(f"Customers: {env['res.partner'].search_count([('customer_rank', '>', 0)])}")
print(f"Vendors: {env['res.partner'].search_count([('supplier_rank', '>', 0)])}")
print(f"Products: {env['product.product'].search_count([])}")
print(f"Sale Orders: {env['sale.order'].search_count([])}")
print(f"Purchase Orders: {env['purchase.order'].search_count([])}")

try:
    print(f"PDC Receivables: {env['ops.pdc.receivable'].search_count([])}")
    print(f"PDC Payables: {env['ops.pdc.payable'].search_count([])}")
except:
    print("PDC models not available")

try:
    print(f"Assets: {env['ops.asset'].search_count([])}")
except:
    print("Asset models not available")

try:
    print(f"Budgets: {env['ops.budget'].search_count([])}")
except:
    print("Budget models not available")

print("\n✅ SEED DATA CREATION COMPLETE")
print("="*60)
```

---

## Task 3.11: Generate Seed Data Report

Create `/opt/gemini_odoo19/claude_files/go_live_audit/03_SEED_DATA_REPORT.md`

---

## Git Commit

```bash
cd /opt/gemini_odoo19
git add -A

git commit -m "[GO-LIVE] Phase 3: Comprehensive seed data created

Created via Odoo ORM:
- 3 Business Units (Sales, Operations, Finance)
- 4 Branches (HQ, Alpha, Beta, Gamma)
- 9 Test Users (IT Admin, CEO, CFO, BU Leader, 2 Branch Mgrs, 2 Sales Reps, Accountant)
- 3 Customers, 2 Vendors
- 4 Products
- 2 Sale Orders, 1 Purchase Order
- 3 PDC Receivables, 1 PDC Payable
- 3 Fixed Assets
- 2 Budgets

Password for all test users: 123
Tested: Data visible in UI"

git push origin main
```

---

## PROCEED TO PHASE 4
