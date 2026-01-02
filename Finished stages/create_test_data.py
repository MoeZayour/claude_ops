#!/usr/bin/env python3
"""
Create visual test data for OPS Matrix System
Demonstrates Branch x Business Unit matrix in action
"""

print("=" * 80)
print("OPS MATRIX CORE - Test Data Population")
print("=" * 80)

# Get main company
main_company = env.company
print(f"\n✓ Main Company: {main_company.name} ({main_company.ops_code})")

# Create a second branch (company)
print("\n Creating additional branch...")
branch_west = env['res.company'].create({
    'name': 'West Region',
    'email': 'west@example.com',
    'phone': '+1-555-0002',
})
print(f"✓ Created Branch: {branch_west.name} ({branch_west.ops_code})")

# Create 2 Business Units
print("\n📦 Creating Business Units...")

bu_tech = env['ops.business.unit'].create({
    'name': 'Technology Services',
    'code': 'TECH',
    'leader_id': env.user.id,
})
print(f"✓ Created BU: {bu_tech.name} ({bu_tech.code})")

bu_sales = env['ops.business.unit'].create({
    'name': 'Sales & Marketing',
    'code': 'SALES',
    'leader_id': env.user.id,
})
print(f"✓ Created BU: {bu_sales.name} ({bu_sales.code})")

# Create a sample partner
print("\n👤 Creating sample customer...")
partner = env['res.partner'].create({
    'name': 'Acme Corporation',
    'email': 'contact@acme.com',
})
print(f"✓ Created Partner: {partner.name}")

# Create a sample product
print("\n📦 Creating sample product...")
product = env['product.product'].create({
    'name': 'Professional Services - Consulting',
    'type': 'service',
    'list_price': 150.00,
    'standard_price': 80.00,
})
print(f"✓ Created Product: {product.name}")

# Create a sample invoice to demonstrate matrix
print("\n🧾 Creating sample invoice with Matrix distribution...")
invoice = env['account.move'].create({
    'move_type': 'out_invoice',
    'partner_id': partner.id,
    'ops_branch_id': main_company.id,
    'ops_business_unit_id': bu_tech.id,
    'invoice_date': '2025-12-25',
    'invoice_line_ids': [(0, 0, {
        'product_id': product.id,
        'quantity': 10,
        'price_unit': 150.00,
        'name': 'Professional Consulting Services - December',
    })],
})
print(f"✓ Created Invoice: {invoice.name}")
print(f"  - Branch: {invoice.ops_branch_id.name}")
print(f"  - Business Unit: {invoice.ops_business_unit_id.name}")
print(f"  - Amount: ${invoice.amount_total:,.2f}")

# Create another invoice for different matrix combination
invoice2 = env['account.move'].create({
    'move_type': 'out_invoice',
    'partner_id': partner.id,
    'ops_branch_id': branch_west.id,
    'ops_business_unit_id': bu_sales.id,
    'invoice_date': '2025-12-25',
    'invoice_line_ids': [(0, 0, {
        'product_id': product.id,
        'quantity': 5,
        'price_unit': 150.00,
        'name': 'Sales Consulting Services - December',
    })],
})
print(f"✓ Created Invoice: {invoice2.name}")
print(f"  - Branch: {invoice2.ops_branch_id.name}")
print(f"  - Business Unit: {invoice2.ops_business_unit_id.name}")
print(f"  - Amount: ${invoice2.amount_total:,.2f}")

print("\n" + "=" * 80)
print("✅ TEST DATA CREATION COMPLETE")
print("=" * 80)
print("\n📊 Summary:")
print(f"  - Companies/Branches: {env['res.company'].search_count([])}")
print(f"  - Business Units: {env['ops.business.unit'].search_count([])}")
print(f"  - Invoices Created: 2")
print(f"  - Total Revenue: ${invoice.amount_total + invoice2.amount_total:,.2f}")
print("\n🔍 WHERE TO LOOK:")
print("  1. Login at http://localhost:8089")
print("  2. Credentials: admin / admin")
print("  3. Database: mz-db")
print("  4. Go to: Accounting → Customers → Invoices")
print("  5. See the Matrix dimensions (Branch x BU) on each invoice")
print("  6. Go to: OPS Dashboards → Executive View")
print("\n" + "=" * 80)
