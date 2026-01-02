#!/usr/bin/env python3
"""
Automated refactoring script to replace ops.branch with res.company
in XML, data, and test files.
"""

import os
import re
from pathlib import Path

# Define the root directory
ROOT_DIR = Path(__file__).parent / "addons"

# Files to update (excluding ops_branch_views.xml which will be deleted)
XML_FILES = [
    "ops_matrix_core/demo/ops_demo_data.xml",
    "ops_matrix_core/data/templates/ops_governance_rule_templates.xml",
    "ops_matrix_core/data/ops_governance_rule_templates.xml",
    "ops_matrix_core/views/ops_persona_views.xml",
    "ops_matrix_core/views/res_users_views.xml",
    "ops_matrix_core/views/ops_product_request_views.xml",
    "ops_matrix_core/views/sale_order_views.xml",
    "ops_matrix_core/views/stock_warehouse_orderpoint_views.xml",
    "ops_matrix_accounting/views/ops_pdc_views.xml",
    "ops_matrix_accounting/views/ops_budget_views.xml",
    "ops_matrix_accounting/views/ops_financial_report_wizard_views.xml",
    "ops_matrix_reporting/views/ops_sales_analysis_views.xml",
    "ops_matrix_reporting/views/ops_financial_analysis_views.xml",
    "ops_matrix_reporting/data/dashboard_data.xml",
]

PYTHON_TEST_FILES = [
    "ops_matrix_core/tests/test_branch_flow.py",
    "ops_matrix_core/tests/test_01_branch_creation.py",
    "ops_matrix_core/tests/test_autopilot_suite.py",
    "ops_matrix_core/tests/test_matrix_lifecycle.py",
]

HOOK_FILES = [
    "ops_matrix_core/hooks.py",
    "ops_matrix_reporting/hooks.py",
]

def replace_in_file(filepath, replacements):
    """Apply multiple replacements to a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in replacements:
            if isinstance(pattern, str):
                content = content.replace(pattern, replacement)
            else:
                # Regex pattern
                content = pattern.sub(replacement, content)
        
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
    print("REFACTORING XML/DATA FILES: ops.branch → res.company")
    print("=" * 70)
    
    # Define replacements for XML files
    xml_replacements = [
        ('model="ops.branch"', 'model="res.company"'),
        ('ref="model_ops_branch"', 'ref="base.model_res_company"'),
        ("ops.branch", "res.company"),
        ("demo_branch_", "demo_company_"),
        ("id FROM ops_branch", "id FROM res_company"),
        ("ops_branch_id", "ops_branch_id"),  # Keep field names the same
    ]
    
    # Define replacements for Python test files
    python_test_replacements = [
        ("'ops.branch'", "'res.company'"),
        ('"ops.branch"', '"res.company"'),
        ("self.Branch = self.env['ops.branch']", "self.Branch = self.env['res.company']"),
        ("Branch = self.env['ops.branch']", "Branch = self.env['res.company']"),
        ("env['ops.branch']", "env['res.company']"),
    ]
    
    # Define replacements for hooks
    hooks_replacements = [
        ("'ops.branch'", "'res.company'"),
        ('"ops.branch"', '"res.company"'),
        ("env['ops.branch']", "env['res.company']"),
        ("Branch = env['ops.branch']", "Branch = env['res.company']"),
        ("FROM ops_branch", "FROM res_company"),
        ("UPDATE ops_branch", "UPDATE res_company"),
        ("ALTER TABLE ops_branch", "ALTER TABLE res_company"),
        ("INSERT INTO ops_branch", "INSERT INTO res_company"),
    ]
    
    updated_count = 0
    
    # Update XML files
    print("\n📄 Updating XML/Data files...")
    for rel_path in XML_FILES:
        filepath = ROOT_DIR / rel_path
        if filepath.exists():
            if replace_in_file(filepath, xml_replacements):
                updated_count += 1
        else:
            print(f"  File not found: {filepath}")
    
    # Update Python test files
    print("\n🧪 Updating test files...")
    for rel_path in PYTHON_TEST_FILES:
        filepath = ROOT_DIR / rel_path
        if filepath.exists():
            if replace_in_file(filepath, python_test_replacements):
                updated_count += 1
        else:
            print(f"  File not found: {filepath}")
    
    # Update hook files
    print("\n🔧 Updating hook files...")
    for rel_path in HOOK_FILES:
        filepath = ROOT_DIR / rel_path
        if filepath.exists():
            if replace_in_file(filepath, hooks_replacements):
                updated_count += 1
        else:
            print(f"  File not found: {filepath}")
    
    print("\n" + "=" * 70)
    print(f"✅ Refactoring complete! Updated {updated_count} files.")
    print("=" * 70)

if __name__ == "__main__":
    main()
