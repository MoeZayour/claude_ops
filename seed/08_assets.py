# -*- coding: utf-8 -*-
"""
Seed Script 08: Fixed Assets and Asset Categories
==================================================
Usage:
    cat seed/08_assets.py | docker exec -i gemini_odoo19 \
        odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http

Idempotent: checks for existing records before creating.
"""
import sys

def log(msg):
    sys.stderr.write(f"[08_assets] {msg}\n")

log("Starting fixed assets seed...")

# ============================================================================
# HELPERS
# ============================================================================

def get_branch(name):
    """Find branch by name (partial match)."""
    branch = env['ops.branch'].search([('name', 'ilike', name)], limit=1)
    if not branch:
        log(f"  WARNING: Branch '{name}' not found, using first available")
        branch = env['ops.branch'].search([], limit=1)
    return branch

def get_bu(name):
    """Find business unit by name (partial match)."""
    bu = env['ops.business.unit'].search([('name', 'ilike', name)], limit=1)
    if not bu:
        log(f"  WARNING: Business Unit '{name}' not found, using first available")
        bu = env['ops.business.unit'].search([], limit=1)
    return bu

# ============================================================================
# LOOKUP BRANCHES AND BUSINESS UNITS
# ============================================================================
log("Looking up branches and business units...")

branch_dubai = get_branch('Dubai')
branch_riyadh = get_branch('Riyadh')
branch_sharjah = get_branch('Sharjah')
branch_abudhabi = get_branch('Abu Dhabi')
branch_doha = get_branch('Doha')

bu_electronics = get_bu('Electronics')
bu_fb = get_bu('F&B')
bu_luxury = get_bu('Luxury')
bu_it = get_bu('IT Solutions')

# ============================================================================
# ASSET CATEGORIES (4)
# ============================================================================
log("Creating/verifying asset categories...")

# Map depreciation method names to what the model expects:
# 'straight_line' = linear, 'declining_balance' = degressive
category_data = [
    {
        'name': 'Office Equipment',
        'depreciation_method': 'straight_line',
        'method_number': 60,    # 5 years * 12 months
        'method_period': 1,     # Monthly
        'method_progress_factor': 0.0,
    },
    {
        'name': 'IT Equipment',
        'depreciation_method': 'straight_line',
        'method_number': 36,    # 3 years * 12 months
        'method_period': 1,     # Monthly
        'method_progress_factor': 0.0,
    },
    {
        'name': 'Vehicles',
        'depreciation_method': 'declining_balance',
        'method_number': 60,    # 5 years * 12 months
        'method_period': 1,     # Monthly
        'method_progress_factor': 0.3,
    },
    {
        'name': 'Furniture',
        'depreciation_method': 'straight_line',
        'method_number': 84,    # 7 years * 12 months
        'method_period': 1,     # Monthly
        'method_progress_factor': 0.0,
    },
]

categories = {}
cats_created = 0
cats_skipped = 0

for cat_data in category_data:
    existing = env['ops.asset.category'].search([
        ('name', '=ilike', cat_data['name'])
    ], limit=1)

    if existing:
        categories[cat_data['name']] = existing
        log(f"  EXISTS: Category '{cat_data['name']}' (id={existing.id})")
        cats_skipped += 1
        continue

    vals = {
        'name': cat_data['name'],
        'depreciation_method': cat_data['depreciation_method'],
        'method_number': cat_data['method_number'],
        'method_period': cat_data['method_period'],
        'method_progress_factor': cat_data['method_progress_factor'],
        'prorata': True,
        'date_first_depreciation': 'manual',
    }

    # Try to set accounting accounts if available
    # Asset account (1xxxxx or fixed asset type)
    asset_acct = env['account.account'].search([
        ('account_type', '=', 'asset_non_current')
    ], limit=1)
    if asset_acct:
        vals['asset_account_id'] = asset_acct.id

    # Accumulated depreciation account
    deprec_acct = env['account.account'].search([
        ('account_type', '=', 'asset_non_current'),
        ('id', '!=', asset_acct.id if asset_acct else 0),
    ], limit=1)
    # Try depreciation-specific search
    deprec_acct2 = env['account.account'].search([
        ('name', 'ilike', '%depreciation%'),
    ], limit=1)
    if deprec_acct2:
        vals['depreciation_account_id'] = deprec_acct2.id
    elif deprec_acct:
        vals['depreciation_account_id'] = deprec_acct.id

    # Expense account for depreciation
    expense_acct = env['account.account'].search([
        ('account_type', '=', 'expense_depreciation')
    ], limit=1)
    if not expense_acct:
        expense_acct = env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1)
    if expense_acct:
        vals['expense_account_id'] = expense_acct.id

    # Journal for depreciation entries
    general_journal = env['account.journal'].search([
        ('type', '=', 'general')
    ], limit=1)
    if general_journal:
        vals['journal_id'] = general_journal.id

    try:
        category = env['ops.asset.category'].create(vals)
        categories[cat_data['name']] = category
        log(f"  CREATED: Category '{cat_data['name']}' (id={category.id})")
        cats_created += 1
    except Exception as e:
        log(f"  ERROR creating category '{cat_data['name']}': {e}")
        # Try without accounting fields
        try:
            simple_vals = {
                'name': cat_data['name'],
                'depreciation_method': cat_data['depreciation_method'],
                'method_number': cat_data['method_number'],
                'method_period': cat_data['method_period'],
                'method_progress_factor': cat_data['method_progress_factor'],
                'prorata': True,
                'date_first_depreciation': 'manual',
            }
            category = env['ops.asset.category'].create(simple_vals)
            categories[cat_data['name']] = category
            log(f"  CREATED (no accounting): Category '{cat_data['name']}' (id={category.id})")
            cats_created += 1
        except Exception as e2:
            log(f"  FATAL: Cannot create category '{cat_data['name']}': {e2}")

log(f"Asset categories: {cats_created} created, {cats_skipped} already existed")

# ============================================================================
# FIXED ASSETS (8)
# ============================================================================
log("Creating fixed assets...")

asset_data = [
    {
        'name': 'MacBook Fleet - Dubai Office',
        'category': 'IT Equipment',
        'purchase_value': 60000,
        'purchase_date': '2025-06-01',
        'branch': branch_dubai,
        'bu': bu_electronics,
        'state': 'running',
    },
    {
        'name': 'Office Furniture - Dubai HQ',
        'category': 'Furniture',
        'purchase_value': 120000,
        'purchase_date': '2025-01-15',
        'branch': branch_dubai,
        'bu': None,  # All BUs / no specific BU
        'state': 'running',
    },
    {
        'name': 'Delivery Van - Sharjah',
        'category': 'Vehicles',
        'purchase_value': 85000,
        'purchase_date': '2025-03-20',
        'branch': branch_sharjah,
        'bu': bu_fb,
        'state': 'running',
    },
    {
        'name': 'Server Equipment',
        'category': 'IT Equipment',
        'purchase_value': 45000,
        'purchase_date': '2025-07-01',
        'branch': branch_dubai,
        'bu': bu_it,
        'state': 'running',
    },
    {
        'name': 'Office Chairs & Desks - Abu Dhabi',
        'category': 'Furniture',
        'purchase_value': 35000,
        'purchase_date': '2025-09-01',
        'branch': branch_abudhabi,
        'bu': bu_electronics,
        'state': 'running',
    },
    {
        'name': 'Espresso Machines - Showroom',
        'category': 'Office Equipment',
        'purchase_value': 42500,
        'purchase_date': '2025-10-01',
        'branch': branch_dubai,
        'bu': bu_fb,
        'state': 'draft',
    },
    {
        'name': 'Delivery Van - Riyadh',
        'category': 'Vehicles',
        'purchase_value': 90000,
        'purchase_date': '2025-04-15',
        'branch': branch_riyadh,
        'bu': bu_electronics,
        'state': 'draft',
    },
    {
        'name': 'IT Infrastructure - Doha',
        'category': 'IT Equipment',
        'purchase_value': 25000,
        'purchase_date': '2025-11-01',
        'branch': branch_doha,
        'bu': bu_it,
        'state': 'draft',
    },
]

assets_created = 0
assets_skipped = 0

for ast_data in asset_data:
    # Idempotency: check by name
    existing = env['ops.asset'].search([
        ('name', '=', ast_data['name'])
    ], limit=1)

    if existing:
        log(f"  EXISTS: Asset '{ast_data['name']}' (id={existing.id}, state={existing.state})")
        assets_skipped += 1
        continue

    # Get category
    cat = categories.get(ast_data['category'])
    if not cat:
        log(f"  ERROR: Category '{ast_data['category']}' not found, skipping asset '{ast_data['name']}'")
        continue

    # Salvage value = 10% of purchase value
    salvage = ast_data['purchase_value'] * 0.10

    vals = {
        'name': ast_data['name'],
        'category_id': cat.id,
        'purchase_value': ast_data['purchase_value'],
        'salvage_value': salvage,
        'purchase_date': ast_data['purchase_date'],
        'ops_branch_id': ast_data['branch'].id if ast_data['branch'] else False,
        'ops_business_unit_id': ast_data['bu'].id if ast_data['bu'] else False,
    }

    try:
        asset = env['ops.asset'].create(vals)
        log(f"  CREATED: Asset '{ast_data['name']}' (id={asset.id}, code={asset.code}, salvage={salvage})")

        # Set to running state if requested (via action_confirm which generates schedule)
        if ast_data['state'] == 'running':
            try:
                asset.action_confirm()
                log(f"    -> Confirmed (running), depreciation schedule generated")
            except Exception as conf_err:
                log(f"    -> Could not confirm (accounting config may be missing): {conf_err}")
                # Try direct state change as fallback
                try:
                    asset.write({'state': 'running'})
                    log(f"    -> State set to 'running' directly (no depreciation schedule)")
                except Exception as state_err:
                    log(f"    -> Could not set state: {state_err}")
        else:
            log(f"    -> Left as draft")

        assets_created += 1
    except Exception as e:
        log(f"  ERROR creating asset '{ast_data['name']}': {e}")

log(f"Fixed assets: {assets_created} created, {assets_skipped} skipped")

# ============================================================================
# COMMIT
# ============================================================================
env.cr.commit()
log("=" * 60)
log("SEED 08 COMPLETE")
log(f"  Asset Categories: {cats_created} created, {cats_skipped} already existed")
log(f"  Fixed Assets:     {assets_created} created, {assets_skipped} skipped")
log("=" * 60)
