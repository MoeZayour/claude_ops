#!/usr/bin/env python3
"""Final OPS Framework seed data - creates personas and test data"""
print("="*60)
print("OPS FRAMEWORK FINAL SEED DATA")
print("="*60)

# Get company
company = env['res.company'].search([], limit=1)
print(f"\nCompany: {company.name}")

# Get branches
branches = env['ops.branch'].search([])
print(f"Branches: {len(branches)}")

# Get BUs
bus = env['ops.business.unit'].search([])
print(f"BUs: {len(bus)}")

# Get users
users = env['res.users'].search([('login', '!=', 'admin')])
print(f"Users: {len(users)}")

# Create Personas for each user
print("\n--- Creating Personas ---")
for user in users:
    # Skip if persona already exists
    existing = env['ops.persona'].search([('user_id', '=', user.id)], limit=1)
    if existing:
        print(f"  ⏭ {user.name}: Persona exists")
        continue
    
    # Create appropriate persona based on user email/login
    if 'ceo' in user.login.lower() or 'admin' in user.login.lower():
        persona = env['ops.persona'].create({
            'name': f'{user.name} - Executive',
            'code': f'PRS-{user.login.upper().replace("@", "").replace(".", "")}',
            'user_id': user.id,
            'company_id': company.id,
            'branch_ids': [(6, 0, branches.ids)],
            'business_unit_ids': [(6, 0, bus.ids)],
            'is_approver': True,
            'approval_limit': 1000000,
            'is_branch_manager': True,
            'is_bu_leader': True,
            'is_matrix_administrator': True,
        })
        print(f"  ✓ {user.name}: Executive Persona")
    
    elif 'cfo' in user.login.lower() or 'account' in user.login.lower():
        persona = env['ops.persona'].create({
            'name': f'{user.name} - Finance',
            'code': f'PRS-{user.login.upper().replace("@", "").replace(".", "")}',
            'user_id': user.id,
            'company_id': company.id,
            'branch_ids': [(6, 0, branches.ids)],
            'business_unit_ids': [(6, 0, bus.ids)],
            'is_approver': True,
            'approval_limit': 500000,
            'can_validate_invoices': True,
            'can_access_cost_prices': True,
        })
        print(f"  ✓ {user.name}: Finance Persona")
    
    elif 'bm.' in user.login.lower() or 'manager' in user.login.lower() or 'branch' in user.login.lower():
        # Assign first branch
        branch = branches[0] if branches else False
        persona = env['ops.persona'].create({
            'name': f'{user.name} - Branch Manager',
            'code': f'PRS-{user.login.upper().replace("@", "").replace(".", "")}',
            'user_id': user.id,
            'company_id': company.id,
            'branch_ids': [(6, 0, [branch.id] if branch else [])],
            'business_unit_ids': [(6, 0, bus.ids[:2])],
            'is_branch_manager': True,
            'is_approver': True,
            'approval_limit': 50000,
            'can_adjust_inventory': True,
        })
        print(f"  ✓ {user.name}: Branch Manager Persona")
    
    elif 'sales' in user.login.lower():
        branch = branches[0] if branches else False
        persona = env['ops.persona'].create({
            'name': f'{user.name} - Sales',
            'code': f'PRS-{user.login.upper().replace("@", "").replace(".", "")}',
            'user_id': user.id,
            'company_id': company.id,
            'branch_ids': [(6, 0, [branch.id] if branch else [])],
            'business_unit_ids': [(6, 0, bus.ids[:1])],
            'can_access_cost_prices': False,
            'max_discount_percent': 5.0,
        })
        print(f"  ✓ {user.name}: Sales Persona")
    
    elif 'warehouse' in user.login.lower() or 'wh' in user.login.lower():
        persona = env['ops.persona'].create({
            'name': f'{user.name} - Warehouse',
            'code': f'PRS-{user.login.upper().replace("@", "").replace(".", "")}',
            'user_id': user.id,
            'company_id': company.id,
            'branch_ids': [(6, 0, branches.ids)],
            'business_unit_ids': [(6, 0, bus.ids)],
            'can_adjust_inventory': True,
            'can_access_cost_prices': True,
        })
        print(f"  ✓ {user.name}: Warehouse Persona")
    
    else:
        # Default persona
        branch = branches[0] if branches else False
        persona = env['ops.persona'].create({
            'name': f'{user.name} - Staff',
            'code': f'PRS-{user.login.upper().replace("@", "").replace(".", "")}',
            'user_id': user.id,
            'company_id': company.id,
            'branch_ids': [(6, 0, [branch.id] if branch else [])],
            'business_unit_ids': [(6, 0, bus.ids[:1])],
        })
        print(f"  ✓ {user.name}: Staff Persona")

# Create sample SoD Rules
print("\n--- Creating SoD Rules ---")
sod_count = env['ops.segregation.of.duties'].search_count([])
if sod_count == 0:
    # Create 3 SoD rules
    env['ops.segregation.of.duties'].create({
        'name': 'No Approve & Record Payments',
        'description': 'Prevents users from approving and recording the same payment',
        'model_id': env.ref('account.model_account_payment').id,
        'action_1': 'approve',
        'action_2': 'create',
        'severity': 'high',
        'active': True,
    })
    print("  ✓ SoD: Approve vs Record Payments")
    
    env['ops.segregation.of.duties'].create({
        'name': 'No Create & Approve Invoices',
        'description': 'Prevents users from creating and approving their own invoices',
        'model_id': env.ref('account.model_account_move').id,
        'action_1': 'create',
        'action_2': 'approve',
        'severity': 'critical',
        'active': True,
    })
    print("  ✓ SoD: Create vs Approve Invoices")
    
    env['ops.segregation.of.duties'].create({
        'name': 'No Cost Modification',
        'description': 'Prevents sales from modifying product cost prices',
        'model_id': env.ref('product.model_product_product').id,
        'action_1': 'write',
        'action_2': 'read',
        'severity': 'medium',
        'active': True,
    })
    print("  ✓ SoD: Cost Modification Restriction")
else:
    print(f"  ⏭ SoD rules already exist ({sod_count})")

# Create sample Field Visibility Rules
print("\n--- Creating Field Visibility Rules ---")
fv_count = env['ops.field.visibility.rule'].search_count([])
if fv_count == 0:
    # Get groups
    sales_group = env.ref('sales_team.group_sale_salesman')
    purchase_group = env.ref('purchase.group_purchase_user')
    
    # Hide cost from sales
    env['ops.field.visibility.rule'].create({
        'model_name': 'product.product',
        'field_name': 'standard_price',
        'field_label': 'Cost',
        'security_group_id': sales_group.id,
        'visibility_mode': 'hidden',
        'description': 'Hide product cost from sales team to protect margins',
        'is_active': True,
    })
    print("  ✓ Field Rule: Hide cost from Sales")
    
    # Hide supplier info from sales
    env['ops.field.visibility.rule'].create({
        'model_name': 'product.product',
        'field_name': 'seller_ids',
        'field_label': 'Vendors',
        'security_group_id': sales_group.id,
        'visibility_mode': 'hidden',
        'description': 'Hide vendor information from sales team',
        'is_active': True,
    })
    print("  ✓ Field Rule: Hide vendors from Sales")
else:
    print(f"  ⏭ Field visibility rules already exist ({fv_count})")

# Create sample SLA Templates
print("\n--- Creating SLA Templates ---")
sla_count = env['ops.sla.template'].search_count([])
if sla_count == 0:
    env['ops.sla.template'].create({
        'name': 'Sales Order Approval',
        'model_id': env.ref('sale.model_sale_order').id,
        'target_hours': 4,
        'priority': 'standard',
        'active': True,
    })
    print("  ✓ SLA: Sales Order Approval (4 hours)")
    
    env['ops.sla.template'].create({
        'name': 'Invoice Validation',
        'model_id': env.ref('account.model_account_move').id,
        'target_hours': 24,
        'priority': 'high',
        'active': True,
    })
    print("  ✓ SLA: Invoice Validation (24 hours)")
    
    env['ops.sla.template'].create({
        'name': 'Vendor Payment',
        'model_id': env.ref('account.model_account_payment').id,
        'target_hours': 48,
        'priority': 'standard',
        'active': True,
    })
    print("  ✓ SLA: Vendor Payment (48 hours)")
else:
    print(f"  ⏭ SLA templates already exist ({sla_count})")

# Create sample Assets
print("\n--- Creating Sample Assets ---")
asset_count = env['ops.asset'].search_count([])
if asset_count == 0:
    # Get asset category
    category = env['ops.asset.category'].search([], limit=1)
    if not category:
        # Create a category first
        journal = env['account.journal'].search([('type', '=', 'general')], limit=1)
        category = env['ops.asset.category'].create({
            'name': 'General Equipment',
            'code': 'GEN-EQ',
            'account_asset_id': env['account.account'].search([('account_type', '=', 'asset')], limit=1).id or False,
            'account_depreciation_id': env['account.account'].search([('account_type', '=', 'liability')], limit=1).id or False,
            'method': 'linear',
            'method_number': 36,
            'method_period': 12,
        })
    
    # Create sample assets
    assets = [
        ('Office Furniture', 15000),
        ('Laptop Computers', 25000),
        ('Office Equipment', 10000),
        ('Vehicle', 75000),
        ('Server Equipment', 50000),
    ]
    
    for name, value in assets:
        env['ops.asset'].create({
            'name': name,
            'code': f'AST-{name[:3].upper()}-001',
            'category_id': category.id,
            'value': value,
            'asset_type': 'fixed',
            'method': 'linear',
            'method_number': 36,
            'state': 'running',
        })
        print(f"  ✓ Asset: {name} ({value})")
else:
    print(f"  ⏭ Assets already exist ({asset_count})")

# Summary
print("\n" + "="*60)
print("SEED DATA SUMMARY")
print("="*60)
print(f"Personas: {env['ops.persona'].search_count([])}")
print(f"SoD Rules: {env['ops.segregation.of.duties'].search_count([])}")
print(f"Field Rules: {env['ops.field.visibility.rule'].search_count([])}")
print(f"SLA Templates: {env['ops.sla.template'].search_count([])}")
print(f"Assets: {env['ops.asset'].search_count([])}")
print("="*60)
print("SEEDING COMPLETE!")
