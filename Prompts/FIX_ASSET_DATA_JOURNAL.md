
# Fix Asset Data Journal Dependency Error

## Problem
The `ops_matrix_accounting` module fails to install because `ops_asset_data.xml` references `account.miscellaneous_journal`, which doesn't exist at module load time.

## Root Cause
In Odoo 19 CE, journals are created by Chart of Accounts templates during company setup, NOT by the base `account` module. External IDs like `account.miscellaneous_journal` may not exist or have different names depending on the localization.

## Solution Strategy
1. Remove hardcoded journal references from `ops_asset_data.xml`
2. Create a `post_init_hook` to programmatically create asset categories
3. The hook will find an appropriate journal or create one if needed

---

## PHASE 1: Modify ops_asset_data.xml

### File: `addons/ops_matrix_accounting/data/ops_asset_data.xml`

Replace the entire content with:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- 
            Asset Categories are now created via post_init_hook
            to avoid dependency on specific journal external IDs.
            
            See: ops_matrix_accounting/hooks.py
        -->
        
        <!-- Asset Sequence -->
        <record id="seq_ops_asset" model="ir.sequence">
            <field name="name">OPS Asset Sequence</field>
            <field name="code">ops.asset</field>
            <field name="prefix">FA-%(year)s-</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>
        
        <!-- Depreciation Sequence -->
        <record id="seq_ops_asset_depreciation" model="ir.sequence">
            <field name="name">OPS Asset Depreciation Sequence</field>
            <field name="code">ops.asset.depreciation</field>
            <field name="prefix">DEP-%(year)s-</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>
        
    </data>
</odoo>
```

---

## PHASE 2: Create Hooks File

### File: `addons/ops_matrix_accounting/hooks.py`

Create this new file:

```python
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
        _logger.info("OPS Matrix Accounting: post_init_hook completed successfully.")
    except Exception as e:
        _logger.warning(
            "OPS Matrix Accounting: post_init_hook encountered an error: %s. "
            "Asset categories may need to be created manually.", str(e)
        )


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
```

---

## PHASE 3: Update Module __init__.py

### File: `addons/ops_matrix_accounting/__init__.py`

Update to include hooks:

```python
# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting Module
Enterprise-grade accounting extensions for the OPS Framework.
"""

from . import models
from . import wizards
from . import report
from .hooks import post_init_hook, uninstall_hook
```

---

## PHASE 4: Update Module Manifest

### File: `addons/ops_matrix_accounting/__manifest__.py`

Add the hooks to the manifest:

```python
# -*- coding: utf-8 -*-
{
    'name': 'OPS Matrix - Accounting',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'OPS Framework Accounting Extensions',
    'description': """
        OPS Matrix Accounting Module
        ============================
        
        Enterprise-grade accounting features:
        - Fixed Asset Management
        - Post-Dated Checks (PDC)
        - Budget Management
        - Enhanced Financial Reporting
        - Multi-branch Accounting
    """,
    'author': 'OPS Matrix',
    'website': 'https://github.com/MoeZayour',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'ops_matrix_core',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/ops_accounting_security.xml',
        
        # Data (sequences only - categories created via hook)
        'data/ops_asset_data.xml',
        
        # Views
        'views/ops_asset_category_views.xml',
        'views/ops_asset_views.xml',
        'views/ops_asset_depreciation_views.xml',
        'views/ops_budget_views.xml',
        'views/ops_pdc_views.xml',
        
        # Wizards
        'wizards/ops_asset_depreciation_wizard_views.xml',
        'wizards/ops_financial_report_wizard_views.xml',
        
        # Reports
        'report/ops_asset_report.xml',
        
        # Menus (load last)
        'views/ops_accounting_menus.xml',
    ],
    'demo': [
        'demo/ops_asset_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ops_matrix_accounting/static/src/css/ops_accounting.css',
        ],
    },
    
    # === IMPORTANT: Hooks for safe installation ===
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

---

## PHASE 5: Create Empty Demo File (Optional)

### File: `addons/ops_matrix_accounting/demo/ops_asset_demo.xml`

If demo data references journals, also fix it:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- 
            Demo data for OPS Assets
            Note: Uses categories created by post_init_hook
        -->
        
        <!-- Demo assets will be created only if categories exist -->
        <function model="ops.asset" name="_create_demo_assets"/>
        
    </data>
</odoo>
```

Or simply make it empty if not needed:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Demo data created programmatically -->
</odoo>
```

---

## PHASE 6: Verify File Structure

Ensure these files exist:

```
addons/ops_matrix_accounting/
├── __init__.py              # Updated with hooks import
├── __manifest__.py          # Updated with post_init_hook
├── hooks.py                 # NEW FILE
├── models/
│   ├── __init__.py
│   ├── ops_asset.py
│   ├── ops_asset_category.py
│   └── ...
├── data/
│   └── ops_asset_data.xml   # Updated - no journal refs
├── demo/
│   └── ops_asset_demo.xml   # Updated or empty
└── ...
```

---

## PHASE 7: Test Installation

Run these commands to test:

```bash
cd /opt/gemini_odoo19

# Clear any cached pyc files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Update module list first
./odoo-bin -c odoo.conf -d your_database --update=base --stop-after-init

# Install/upgrade the module
./odoo-bin -c odoo.conf -d your_database -i ops_matrix_accounting --stop-after-init

# Check logs for hook execution
grep -i "post_init_hook" /var/log/odoo/odoo.log
```

---

## Troubleshooting

### If ops.asset.category model doesn't exist yet:

The hook will gracefully skip category creation and log a warning.

### If no accounts are found:

Categories will be created without account references. Users must configure accounts manually in the category form.

### If installation still fails:

1. Check that `ops_matrix_core` is installed first
2. Verify the `account` module is installed
3. Check for syntax errors in hooks.py

```bash
# Syntax check
python3 -m py_compile addons/ops_matrix_accounting/hooks.py
```

---

## Expected Outcome

After successful installation:
- 8 asset categories created per company
- Each category linked to a miscellaneous/general journal
- Accounts linked if matching account codes found
- External IDs created for all records
- Log shows: "OPS Matrix Accounting: post_init_hook completed successfully."
```

---

## 🎯 Quick Summary

| Phase | Action | File |
|-------|--------|------|
| 1 | Remove journal refs from XML | `data/ops_asset_data.xml` |
| 2 | Create hooks file | `hooks.py` (NEW) |
| 3 | Import hooks | `__init__.py` |
| 4 | Register hooks in manifest | `__manifest__.py` |
| 5 | Fix demo data | `demo/ops_asset_demo.xml` |
| 6 | Verify structure | All files |
| 7 | Test installation | Shell commands |

---
