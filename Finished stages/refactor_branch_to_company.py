#!/usr/bin/env python3
"""
Automated refactoring script to replace ops.branch with res.company
across all OPS Matrix modules.
"""

import os
import re
from pathlib import Path

# Define the root directory
ROOT_DIR = Path(__file__).parent / "addons"

# Files to update (Python models)
PYTHON_FILES = [
    "ops_matrix_core/models/sale_order.py",
    "ops_matrix_core/models/account_move.py",
    "ops_matrix_core/models/stock_move.py",
    "ops_matrix_core/models/stock_picking.py",
    "ops_matrix_core/models/stock_warehouse.py",
    "ops_matrix_core/models/stock_warehouse_orderpoint.py",
    "ops_matrix_core/models/res_users.py",
    "ops_matrix_core/models/pricelist.py",
    "ops_matrix_core/models/ops_product_request.py",
    "ops_matrix_core/models/ops_approval_request.py",
    "ops_matrix_core/models/ops_business_unit.py",
    "ops_matrix_accounting/models/ops_pdc.py",
    "ops_matrix_accounting/models/ops_matrix_standard_extensions.py",
    "ops_matrix_accounting/wizard/ops_financial_report_wizard.py",
    "ops_matrix_reporting/models/ops_sales_analysis.py",
    "ops_matrix_reporting/models/ops_financial_analysis.py",
]

def replace_in_file(filepath, replacements):
    """Apply multiple replacements to a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        else:
            print(f"  No changes: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

def main():
    """Main refactoring logic"""
    print("=" * 70)
    print("REFACTORING: ops.branch → res.company")
    print("=" * 70)
    
    # Define replacements for Python files
    python_replacements = [
        ("'ops.branch'", "'res.company'"),
        ('"ops.branch"', '"res.company"'),
        ("model_ops_branch", "base.model_res_company"),
        ("ops.branch", "res.company"),  # For SQL and comments
    ]
    
    updated_count = 0
    
    # Update Python files
    print("\n📄 Updating Python model files...")
    for rel_path in PYTHON_FILES:
        filepath = ROOT_DIR / rel_path
        if filepath.exists():
            if replace_in_file(filepath, python_replacements):
                updated_count += 1
        else:
            print(f"  File not found: {filepath}")
    
    print("\n" + "=" * 70)
    print(f"✅ Refactoring complete! Updated {updated_count} files.")
    print("=" * 70)

if __name__ == "__main__":
    main()
