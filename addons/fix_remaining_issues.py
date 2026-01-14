#!/usr/bin/env python3
"""
Fix remaining complex expression issues in converted attrs
"""

import re
from pathlib import Path

def fix_list_expressions(file_path):
    """Fix incomplete list expressions in invisible/readonly attributes"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Fix incomplete 'in' expressions like: ('state', 'not in', ['draft', 'failed'
    # Should be: state not in ['draft', 'failed']
    pattern1 = r'''invisible="\('([^']+)',\s*'not in',\s*\[([^\]]+)\]?"'''
    for match in re.finditer(pattern1, content):
        field = match.group(1)
        values = match.group(2).strip()
        # Ensure values end with ]
        if not values.endswith("']"):
            values = values + "']"
        new_expr = f'{field} not in [{values}'
        old = match.group(0)
        new = f'invisible="{new_expr}"'
        content = content.replace(old, new, 1)
        changes.append(f"Fixed 'not in' expression for {field}")
    
    # Fix incomplete 'in' expressions
    pattern2 = r'''invisible="\('([^']+)',\s*'in',\s*\[([^\]]+)\]?"'''
    for match in re.finditer(pattern2, content):
        field = match.group(1)
        values = match.group(2).strip()
        if not values.endswith("']"):
            values = values + "']"
        new_expr = f'{field} in [{values}'
        old = match.group(0)
        new = f'invisible="{new_expr}"'
        content = content.replace(old, new, 1)
        changes.append(f"Fixed 'in' expression for {field}")
    
    # Same for readonly
    pattern3 = r'''readonly="\('([^']+)',\s*'not in',\s*\[([^\]]+)\]?"'''
    for match in re.finditer(pattern3, content):
        field = match.group(1)
        values = match.group(2).strip()
        if not values.endswith("']"):
            values = values + "']"
        new_expr = f'{field} not in [{values}'
        old = match.group(0)
        new = f'readonly="{new_expr}"'
        content = content.replace(old, new, 1)
        changes.append(f"Fixed 'not in' expression for {field}")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, []

def main():
    base_path = Path('/opt/gemini_odoo19/addons')
    
    files_to_fix = [
        base_path / 'ops_matrix_core/views/ops_data_archival_views.xml',
        base_path / 'ops_matrix_core/views/ops_security_audit_enhanced_views.xml',
    ]
    
    print("Fixing remaining expression issues...")
    print("="*60)
    
    total_fixed = 0
    for file_path in files_to_fix:
        if file_path.exists():
            modified, changes = fix_list_expressions(file_path)
            if modified:
                print(f"\n✓ Fixed: {file_path.name}")
                for change in changes:
                    print(f"  - {change}")
                total_fixed += 1
    
    print("\n" + "="*60)
    print(f"✓ Fixed {total_fixed} files")
    print("="*60)

if __name__ == '__main__':
    main()
