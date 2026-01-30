# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Installation Hooks
Handles post-installation setup that requires existing records.
"""

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Post-installation hook for ops_matrix_accounting.
    Creates asset categories with proper journal references.

    This runs AFTER all module data is loaded, ensuring
    that accounting records exist.
    """
    _logger.info("OPS Matrix Accounting: Running post_init_hook...")

    try:
        _create_asset_categories(env)
        _create_budget_indexes(env)
        _logger.info("OPS Matrix Accounting: post_init_hook completed successfully.")
    except Exception as e:
        _logger.warning(
            "OPS Matrix Accounting: post_init_hook encountered an error: %s. "
            "Asset categories may need to be created manually.", str(e)
        )


def _create_budget_indexes(env):
    """
    Create database indexes for budget performance optimization.

    These indexes improve query performance for:
    - Committed amount calculation (PO lines by branch/date/state)
    - Practical amount calculation (account move lines)
    - Product category expense account lookups
    """
    _logger.info("OPS Matrix Accounting: Creating budget performance indexes...")

    indexes = [
        # Index for PO committed amount queries
        (
            "idx_po_branch_date_state",
            """
            CREATE INDEX IF NOT EXISTS idx_po_branch_date_state
            ON purchase_order(ops_branch_id, date_order, state)
            WHERE state IN ('purchase', 'done')
            """
        ),
        # Index for product category expense account lookups
        (
            "idx_product_category_expense_account",
            """
            CREATE INDEX IF NOT EXISTS idx_product_category_expense_account
            ON product_category(property_account_expense_categ_id)
            WHERE property_account_expense_categ_id IS NOT NULL
            """
        ),
        # Index for account move line practical amount queries
        (
            "idx_aml_account_branch_date",
            """
            CREATE INDEX IF NOT EXISTS idx_aml_account_branch_date
            ON account_move_line(account_id, ops_branch_id, date)
            WHERE ops_branch_id IS NOT NULL
            """
        ),
    ]

    for index_name, index_sql in indexes:
        try:
            env.cr.execute(index_sql)
            _logger.info("Budget index '%s' created/verified", index_name)
        except Exception as e:
            _logger.warning("Could not create budget index '%s': %s", index_name, e)


def _get_or_create_misc_journal(env, company):
    """
    Find or create a miscellaneous journal for asset transactions.
    
    Search priority:
    1. Journal with code 'MISC'
    2. Journal with code 'MSC'
    3. Any journal of type 'general'
    4. Create a new 'Miscellaneous Operations' journal
    """
    Journal = env['account.journal']
    
    # Search for existing miscellaneous journal
    journal = Journal.search([
        ('company_id', '=', company.id),
        ('code', 'in', ['MISC', 'MSC', 'MIS']),
        ('type', '=', 'general'),
    ], limit=1)
    
    if journal:
        _logger.info(f"Found existing miscellaneous journal: {journal.name} ({journal.code})")
        return journal
    
    # Search for any general journal
    journal = Journal.search([
        ('company_id', '=', company.id),
        ('type', '=', 'general'),
    ], limit=1)
    
    if journal:
        _logger.info(f"Using existing general journal: {journal.name} ({journal.code})")
        return journal
    
    # Create a new miscellaneous journal
    _logger.info("Creating new Miscellaneous Operations journal...")
    journal = Journal.create({
        'name': 'Miscellaneous Operations',
        'code': 'MISC',
        'type': 'general',
        'company_id': company.id,
    })
    
    # Create external ID for future reference
    env['ir.model.data'].create({
        'name': 'ops_miscellaneous_journal_%s' % company.id,
        'module': 'ops_matrix_accounting',
        'model': 'account.journal',
        'res_id': journal.id,
        'noupdate': True,
    })
    
    return journal


def _get_default_accounts(env, company):
    """
    Get default accounts for asset categories.
    Returns a dict with account references or None values.
    """
    Account = env['account.account']
    
    def find_account(codes, account_type=None):
        """Find account by code patterns."""
        for code in codes:
            domain = [
                ('company_id', '=', company.id),
                ('code', '=like', code + '%'),
            ]
            if account_type:
                domain.append(('account_type', '=', account_type))
            account = Account.search(domain, limit=1)
            if account:
                return account
        return None
    
    return {
        # Fixed Assets (typically 15xxxx or 16xxxx)
        'account_asset': find_account(['15', '16', '12'], 'asset_non_current'),
        # Accumulated Depreciation (typically 15xxxx or 17xxxx)
        'account_depreciation': find_account(['159', '175', '17', '15']),
        # Depreciation Expense (typically 68xxxx)
        'account_expense': find_account(['68', '6', '5']),
    }


def _create_asset_categories(env):
    """
    Create default asset categories for each company.
    """
    AssetCategory = env.get('ops.asset.category')
    
    if AssetCategory is None:
        _logger.warning("Model 'ops.asset.category' not found. Skipping category creation.")
        return
    
    companies = env['res.company'].search([])
    
    categories_data = [
        {
            'name': 'Buildings',
            'method': 'linear',
            'method_number': 240,  # 20 years
            'method_period': 12,   # Monthly
        },
        {
            'name': 'Vehicles',
            'method': 'linear',
            'method_number': 60,   # 5 years
            'method_period': 12,
        },
        {
            'name': 'Office Equipment',
            'method': 'linear',
            'method_number': 36,   # 3 years
            'method_period': 12,
        },
        {
            'name': 'Computer Equipment',
            'method': 'linear',
            'method_number': 36,   # 3 years
            'method_period': 12,
        },
        {
            'name': 'Furniture & Fixtures',
            'method': 'linear',
            'method_number': 60,   # 5 years
            'method_period': 12,
        },
        {
            'name': 'Machinery & Equipment',
            'method': 'linear',
            'method_number': 120,  # 10 years
            'method_period': 12,
        },
        {
            'name': 'Leasehold Improvements',
            'method': 'linear',
            'method_number': 60,   # 5 years (or lease term)
            'method_period': 12,
        },
        {
            'name': 'Intangible Assets',
            'method': 'linear',
            'method_number': 60,   # 5 years
            'method_period': 12,
        },
    ]
    
    for company in companies:
        _logger.info(f"Creating asset categories for company: {company.name}")
        
        # Get journal and accounts
        journal = _get_or_create_misc_journal(env, company)
        accounts = _get_default_accounts(env, company)
        
        for cat_data in categories_data:
            # Check if category already exists
            existing = AssetCategory.search([
                ('name', '=', cat_data['name']),
                ('company_id', '=', company.id),
            ], limit=1)
            
            if existing:
                _logger.debug(f"Category '{cat_data['name']}' already exists for {company.name}")
                continue
            
            # Prepare category values
            values = {
                'name': cat_data['name'],
                'company_id': company.id,
                'journal_id': journal.id,
                'method': cat_data['method'],
                'method_number': cat_data['method_number'],
                'method_period': cat_data['method_period'],
            }
            
            # Add accounts if found
            if accounts.get('account_asset'):
                values['account_asset_id'] = accounts['account_asset'].id
            if accounts.get('account_depreciation'):
                values['account_depreciation_id'] = accounts['account_depreciation'].id
            if accounts.get('account_expense'):
                values['account_depreciation_expense_id'] = accounts['account_expense'].id
            
            try:
                category = AssetCategory.create(values)
                
                # Create external ID
                xml_id = 'ops_asset_category_%s_%s' % (
                    cat_data['name'].lower().replace(' ', '_').replace('&', 'and'),
                    company.id
                )
                env['ir.model.data'].create({
                    'name': xml_id,
                    'module': 'ops_matrix_accounting',
                    'model': 'ops.asset.category',
                    'res_id': category.id,
                    'noupdate': True,
                })
                
                _logger.info(f"Created asset category: {cat_data['name']} for {company.name}")
                
            except Exception as e:
                _logger.warning(f"Failed to create category '{cat_data['name']}': {e}")
                continue
    
    # Commit the transaction
    env.cr.commit()


def uninstall_hook(env):
    """
    Cleanup hook when module is uninstalled.
    """
    _logger.info("OPS Matrix Accounting: Running uninstall_hook...")
    # Asset categories will be deleted via cascade or manually
    # No special cleanup needed
