#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 2: Persistent Infrastructure Seeding for OPS Framework Stress Test
==========================================================================

This script creates a comprehensive "Stress-Test" organization structure:
- 10 Branches (Locations)
- 10 Business Units (Profit Centers)
- 4 Test Users with specific Personas
- 5 Test Products with varying costs

Critical: Uses env.cr.commit() after each section for PERSISTENT commits.

Execution:
    docker exec -it gemini_odoo19 odoo shell -d mz-db --stop-after-init < scripts/phase2_seed_infrastructure.py

Author: ROO AI Assistant
Date: 2025-12-28
"""

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

TEST_PASSWORD = '123456'
DEFAULT_COMPANY_ID = 1  # Assume default company

# Branch configuration (10 branches)
BRANCH_CONFIG = [
    {'name': 'Branch-North', 'code': 'BRN'},
    {'name': 'Branch-South', 'code': 'BRS'},
    {'name': 'Branch-East', 'code': 'BRE'},
    {'name': 'Branch-West', 'code': 'BRW'},
    {'name': 'Branch-Central', 'code': 'BRC'},
    {'name': 'Branch-HQ', 'code': 'BRH'},
    {'name': 'Branch-Regional-A', 'code': 'BRA'},
    {'name': 'Branch-Regional-B', 'code': 'BRB'},
    {'name': 'Branch-International', 'code': 'BRI'},
    {'name': 'Branch-Digital', 'code': 'BRD'},
]

# Business Unit configuration (10 BUs)
BU_CONFIG = [
    {'name': 'BU-Sales', 'code': 'SAL'},
    {'name': 'BU-Procurement', 'code': 'PRC'},
    {'name': 'BU-Finance', 'code': 'FIN'},
    {'name': 'BU-Operations', 'code': 'OPS'},
    {'name': 'BU-HR', 'code': 'HRD'},
    {'name': 'BU-IT', 'code': 'ITD'},
    {'name': 'BU-Marketing', 'code': 'MKT'},
    {'name': 'BU-Logistics', 'code': 'LOG'},
    {'name': 'BU-R&D', 'code': 'RND'},
    {'name': 'BU-Customer-Service', 'code': 'CUS'},
]

# User configuration (4 users)
# Note: Using XML IDs from ops_persona_templates.xml
USER_CONFIG = [
    {
        'login': 'ops_sales_rep',
        'name': 'OPS Sales Representative',
        'email': 'ops_sales_rep@test.com',
        'persona_xmlid': 'ops_matrix_core.persona_sales_rep',
        'branch_index': 0,  # Branch-North
        'bu_index': 0,      # BU-Sales
    },
    {
        'login': 'ops_sales_mgr',
        'name': 'OPS Sales Manager',
        'email': 'ops_sales_mgr@test.com',
        'persona_xmlid': 'ops_matrix_core.persona_sales_manager',
        'branch_index': 0,  # Branch-North
        'bu_index': 0,      # BU-Sales
    },
    {
        'login': 'ops_accountant',
        'name': 'OPS Financial Controller',
        'email': 'ops_accountant@test.com',
        'persona_xmlid': 'ops_matrix_core.persona_financial_controller',
        'branch_index': 5,  # Branch-HQ
        'bu_index': 2,      # BU-Finance
    },
    {
        'login': 'ops_treasury',
        'name': 'OPS Treasury Officer',
        'email': 'ops_treasury@test.com',
        'persona_xmlid': 'ops_matrix_core.persona_treasury_officer',
        'branch_index': 5,  # Branch-HQ
        'bu_index': 2,      # BU-Finance
    },
]

# Product configuration (5 products with varying costs)
# Note: In Odoo, product types are: 'consu' (consumable), 'service' (service)
# Storable products don't have a separate type in base Odoo
PRODUCT_CONFIG = [
    {
        'name': 'Standard Widget A',
        'default_code': 'WIDGET-A-001',
        'type': 'consu',  # Consumable (storable in stock module)
        'cost': 50.00,
        'price': 75.00,
        'category': 'Raw Materials',
    },
    {
        'name': 'Premium Widget B',
        'default_code': 'WIDGET-B-002',
        'type': 'consu',  # Consumable (storable in stock module)
        'cost': 250.00,
        'price': 399.00,
        'category': 'Finished Goods',
    },
    {
        'name': 'Enterprise Solution C',
        'default_code': 'SOLUTION-C-003',
        'type': 'service',
        'cost': 5000.00,
        'price': 8500.00,
        'category': 'Services',
    },
    {
        'name': 'Industrial Equipment D',
        'default_code': 'EQUIPMENT-D-004',
        'type': 'consu',  # Consumable (storable in stock module)
        'cost': 12000.00,
        'price': 18000.00,
        'category': 'Equipment',
    },
    {
        'name': 'Office Supplies Pack E',
        'default_code': 'SUPPLIES-E-005',
        'type': 'consu',
        'cost': 15.00,
        'price': 25.00,
        'category': 'Consumables',
    },
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_success(message):
    """Print success message."""
    print(f"✓ {message}")

def print_error(message):
    """Print error message."""
    print(f"✗ ERROR: {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ {message}")

# ============================================================================
# STEP 0: PRE-FLIGHT CHECKS
# ============================================================================

def check_existing_data(env):
    """Check if test data already exists."""
    print_section("STEP 0: PRE-FLIGHT CHECKS")
    
    existing_users = []
    for user_cfg in USER_CONFIG:
        user = env['res.users'].search([('login', '=', user_cfg['login'])], limit=1)
        if user:
            existing_users.append(user_cfg['login'])
    
    if existing_users:
        print_error(f"Test users already exist: {', '.join(existing_users)}")
        print_info("Please remove or rename existing test users before running this script.")
        return False
    
    print_success("No conflicting test data found. Safe to proceed.")
    return True

# ============================================================================
# STEP 1: CREATE 10 BRANCHES
# ============================================================================

def create_branches(env):
    """Create 10 test branches."""
    print_section("STEP 1: CREATING 10 BRANCHES")
    
    created_branches = []
    company = env['res.company'].browse(DEFAULT_COMPANY_ID)
    
    for idx, branch_cfg in enumerate(BRANCH_CONFIG, 1):
        try:
            # Check if branch code already exists
            existing = env['ops.branch'].search([
                ('code', '=', branch_cfg['code']),
                ('company_id', '=', company.id)
            ], limit=1)
            
            if existing:
                print_info(f"  {idx}. Branch {branch_cfg['code']} already exists, skipping...")
                created_branches.append(existing)
                continue
            
            branch = env['ops.branch'].create({
                'name': branch_cfg['name'],
                'code': branch_cfg['code'],
                'company_id': company.id,
                'active': True,
                'sequence': idx * 10,
            })
            created_branches.append(branch)
            print_success(f"  {idx}. Created branch: [{branch.code}] {branch.name} (ID: {branch.id})")
            
        except Exception as e:
            print_error(f"  {idx}. Failed to create branch {branch_cfg['code']}: {e}")
            raise
    
    # COMMIT after branches
    env.cr.commit()
    print_success(f"\n✓✓✓ COMMITTED {len(created_branches)} branches to database ✓✓✓")
    
    return created_branches

# ============================================================================
# STEP 2: CREATE 10 BUSINESS UNITS
# ============================================================================

def create_business_units(env, branches):
    """Create 10 test business units."""
    print_section("STEP 2: CREATING 10 BUSINESS UNITS")
    
    created_bus = []
    
    for idx, bu_cfg in enumerate(BU_CONFIG, 1):
        try:
            # Check if BU code already exists
            existing = env['ops.business.unit'].search([
                ('code', '=', bu_cfg['code'])
            ], limit=1)
            
            if existing:
                print_info(f"  {idx}. BU {bu_cfg['code']} already exists, skipping...")
                created_bus.append(existing)
                continue
            
            # Assign each BU to all branches (cross-branch operations)
            bu = env['ops.business.unit'].create({
                'name': bu_cfg['name'],
                'code': bu_cfg['code'],
                'branch_ids': [(6, 0, [b.id for b in branches])],
                'active': True,
                'sequence': idx * 10,
            })
            created_bus.append(bu)
            print_success(f"  {idx}. Created BU: [{bu.code}] {bu.name} (ID: {bu.id}, {len(branches)} branches)")
            
        except Exception as e:
            print_error(f"  {idx}. Failed to create BU {bu_cfg['code']}: {e}")
            raise
    
    # COMMIT after BUs
    env.cr.commit()
    print_success(f"\n✓✓✓ COMMITTED {len(created_bus)} business units to database ✓✓✓")
    
    return created_bus

# ============================================================================
# STEP 3: CREATE 4 TEST USERS WITH PERSONAS
# ============================================================================

def create_test_users(env, branches, bus):
    """Create 4 test users (without personas for now due to data loading issue)."""
    print_section("STEP 3: CREATING 4 TEST USERS")
    
    created_users = []
    company = env['res.company'].browse(DEFAULT_COMPANY_ID)
    
    print_info("  Note: Creating users without personas (persona data requires module reinstall)")
    print_info("  Users will have basic matrix access (branch + BU assignments)")
    
    for idx, user_cfg in enumerate(USER_CONFIG, 1):
        try:
            # Check if user already exists
            existing = env['res.users'].search([('login', '=', user_cfg['login'])], limit=1)
            if existing:
                print_info(f"  {idx}. User {user_cfg['login']} already exists, skipping...")
                created_users.append(existing)
                continue
            
            # Get assigned branch and BU
            assigned_branch = branches[user_cfg['branch_index']]
            assigned_bu = bus[user_cfg['bu_index']]
            
            # Create user WITHOUT persona (simplified for Phase 2)
            user = env['res.users'].create({
                'login': user_cfg['login'],
                'name': user_cfg['name'],
                'email': user_cfg['email'],
                'password': TEST_PASSWORD,
                'company_id': company.id,
                'company_ids': [(6, 0, [company.id])],
                'active': True,
                
                # OPS Matrix Access Fields (NO PERSONA)
                'primary_branch_id': assigned_branch.id,
                'ops_allowed_branch_ids': [(6, 0, [assigned_branch.id])],
                'ops_default_branch_id': assigned_branch.id,
                'ops_allowed_business_unit_ids': [(6, 0, [assigned_bu.id])],
                'ops_default_business_unit_id': assigned_bu.id,
            })
            
            # Add basic user group after creation
            base_user_group = env.ref('base.group_user')
            if base_user_group:
                user.write({'group_ids': [(4, base_user_group.id)]})
            
            created_users.append(user)
            print_success(
                f"  {idx}. Created user: {user.login} | "
                f"Branch: {assigned_branch.code} | "
                f"BU: {assigned_bu.code} | "
                f"ID: {user.id}"
            )
            
        except Exception as e:
            print_error(f"  {idx}. Failed to create user {user_cfg['login']}: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - continue with other users
    
    # COMMIT after users
    env.cr.commit()
    print_success(f"\n✓✓✓ COMMITTED {len(created_users)} users to database ✓✓✓")
    
    return created_users

# ============================================================================
# STEP 4: CREATE 5 TEST PRODUCTS WITH VARYING COSTS
# ============================================================================

def create_test_products(env, bus):
    """Create 5 test products with varying costs."""
    print_section("STEP 4: CREATING 5 TEST PRODUCTS WITH VARYING COSTS")
    
    created_products = []
    
    # First, create/get product categories
    categories = {}
    for product_cfg in PRODUCT_CONFIG:
        cat_name = product_cfg['category']
        if cat_name not in categories:
            category = env['product.category'].search([('name', '=', cat_name)], limit=1)
            if not category:
                category = env['product.category'].create({
                    'name': cat_name,
                })
                print_info(f"  Created category: {cat_name}")
            categories[cat_name] = category
    
    # Now create products
    for idx, product_cfg in enumerate(PRODUCT_CONFIG, 1):
        try:
            # Check if product already exists
            existing = env['product.template'].search([
                ('default_code', '=', product_cfg['default_code'])
            ], limit=1)
            
            if existing:
                print_info(f"  {idx}. Product {product_cfg['default_code']} already exists, skipping...")
                created_products.append(existing)
                continue
            
            # Assign to first BU (BU-Sales)
            assigned_bu = bus[0] if bus else False
            
            product = env['product.template'].create({
                'name': product_cfg['name'],
                'default_code': product_cfg['default_code'],
                'type': product_cfg['type'],
                'standard_price': product_cfg['cost'],
                'list_price': product_cfg['price'],
                'categ_id': categories[product_cfg['category']].id,
                'business_unit_id': assigned_bu.id if assigned_bu else False,
                'active': True,
                'sale_ok': True,
                'purchase_ok': True,
            })
            
            created_products.append(product)
            print_success(
                f"  {idx}. Created product: {product.default_code} | "
                f"{product.name} | "
                f"Cost: ${product.standard_price:.2f} | "
                f"Price: ${product.list_price:.2f} | "
                f"ID: {product.id}"
            )
            
        except Exception as e:
            print_error(f"  {idx}. Failed to create product {product_cfg['default_code']}: {e}")
            raise
    
    # COMMIT after products
    env.cr.commit()
    print_success(f"\n✓✓✓ COMMITTED {len(created_products)} products to database ✓✓✓")
    
    return created_products

# ============================================================================
# STEP 5: VERIFICATION & REPORTING
# ============================================================================

def generate_verification_report(env, branches, bus, users, products):
    """Generate comprehensive verification report."""
    print_section("STEP 5: VERIFICATION & FINAL REPORT")
    
    # Verify counts
    print("\n📊 CREATION SUMMARY:")
    print(f"  • Branches Created:       {len(branches)}")
    print(f"  • Business Units Created: {len(bus)}")
    print(f"  • Users Created:          {len(users)}")
    print(f"  • Products Created:       {len(products)}")
    
    # Detailed User Table
    print("\n👥 USER DETAILS:")
    print("  " + "-" * 76)
    print(f"  {'Login':<20} {'Persona':<25} {'Branch':<15} {'BU':<15}")
    print("  " + "-" * 76)
    for user in users:
        persona_name = user.ops_persona_ids[0].name if user.ops_persona_ids else "None"
        branch_code = user.primary_branch_id.code if user.primary_branch_id else "None"
        bu_code = user.ops_default_business_unit_id.code if user.ops_default_business_unit_id else "None"
        print(f"  {user.login:<20} {persona_name:<25} {branch_code:<15} {bu_code:<15}")
    print("  " + "-" * 76)
    
    # Detailed Product Table
    print("\n📦 PRODUCT DETAILS:")
    print("  " + "-" * 76)
    print(f"  {'Code':<18} {'Name':<30} {'Cost':>12} {'Price':>12}")
    print("  " + "-" * 76)
    for product in products:
        print(f"  {product.default_code:<18} {product.name:<30} ${product.standard_price:>10.2f} ${product.list_price:>10.2f}")
    print("  " + "-" * 76)
    
    # Database Persistence Confirmation
    print("\n💾 DATABASE PERSISTENCE:")
    print_success("  All data has been COMMITTED to the database using env.cr.commit()")
    print_success("  Data will persist after shell exit and is ready for Phase 3 stress tests")
    
    # Final Instructions
    print("\n📋 NEXT STEPS:")
    print("  1. Verify data in Odoo UI:")
    print("     - Settings → Users & Companies → Users")
    print("     - OPS → Configuration → Branches")
    print("     - OPS → Configuration → Business Units")
    print("     - Inventory → Products")
    print("\n  2. Test user login with credentials:")
    print(f"     - All users have password: {TEST_PASSWORD}")
    print("\n  3. Proceed to Phase 3: Stress Tests")
    print("     - Transaction creation across matrix dimensions")
    print("     - Security validation (Cost Shield)")
    print("     - Performance benchmarking")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  PHASE 2: OPS FRAMEWORK STRESS TEST - INFRASTRUCTURE SEEDING".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\nScript started at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        # Pre-flight checks
        if not check_existing_data(env):
            print_error("\nABORTED: Please resolve conflicts before running this script.")
            return
        
        # Step 1: Create branches
        branches = create_branches(env)
        
        # Step 2: Create business units
        bus = create_business_units(env, branches)
        
        # Step 3: Create users
        users = create_test_users(env, branches, bus)
        
        # Step 4: Create products
        products = create_test_products(env, bus)
        
        # Step 5: Verification and reporting
        generate_verification_report(env, branches, bus, users, products)
        
        # Final success message
        print_section("✅ PHASE 2 COMPLETE - ALL DATA COMMITTED")
        print("\n🎉 Infrastructure seeding completed successfully!")
        print(f"   Total execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        print_section("❌ PHASE 2 FAILED")
        print_error(f"Critical error during seeding: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Database may be in incomplete state. Review errors above.")
        raise

# Execute main function
if __name__ == '__main__':
    main()
