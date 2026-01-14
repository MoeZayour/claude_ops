#!/usr/bin/env python3
"""
Comprehensive Odoo 19 Compatibility Fix Script
Fixes all XML view issues across OPS modules
"""

import os
import re
import sys
from pathlib import Path

class Odoo19Fixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.fixes_applied = []
        self.files_modified = []
        
    def log_fix(self, file_path, fix_type, details):
        """Log a fix that was applied"""
        self.fixes_applied.append({
            'file': str(file_path),
            'type': fix_type,
            'details': details
        })
        
    def fix_xml_file(self, file_path):
        """Fix all Odoo 19 issues in a single XML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_modified = False
        
        # Fix 1: Remove string= from search view <group> elements
        pattern = r'(<group[^>]*)\s+string="[^"]*"([^>]*>)'
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, r'\1\2', content)
            self.log_fix(file_path, "Remove string= from <group>", f"Removed {len(matches)} occurrences")
            file_modified = True
        
        # Fix 2: Remove expand= attributes (deprecated in Odoo 19)
        pattern = r'(<[^>]*)\s+expand="[^"]*"([^>]*>)'
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, r'\1\2', content)
            self.log_fix(file_path, "Remove expand= attribute", f"Removed {len(matches)} occurrences")
            file_modified = True
        
        # Fix 3: Convert <tree> to <list>
        # Handle opening tags
        pattern = r'<tree(\s+[^>]*>|>)'
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(r'<tree(\s+[^>]*>|>)', r'<list\1', content)
            self.log_fix(file_path, "Convert <tree> to <list>", f"Converted {len(matches)} opening tags")
            file_modified = True
        
        # Handle closing tags
        if '</tree>' in content:
            count = content.count('</tree>')
            content = content.replace('</tree>', '</list>')
            self.log_fix(file_path, "Convert </tree> to </list>", f"Converted {count} closing tags")
            file_modified = True
        
        # Fix 4: Replace group_ops_administrator with group_ops_admin_power
        if 'group_ops_administrator' in content:
            count = content.count('group_ops_administrator')
            content = content.replace('group_ops_administrator', 'group_ops_admin_power')
            self.log_fix(file_path, "Fix group reference", f"Replaced group_ops_administrator {count} times")
            file_modified = True
        
        # Fix 5: Remove invalid attrs on <group> in search views
        # Find search views and fix group elements within them
        search_view_pattern = r'<search[^>]*>.*?</search>'
        search_views = re.finditer(search_view_pattern, content, re.DOTALL)
        
        for match in search_views:
            search_content = match.group(0)
            original_search = search_content
            
            # Remove attrs that are not valid for search group elements
            # Valid: name, col, colspan
            # Invalid: string, modifiers, etc.
            group_pattern = r'<group([^>]*)>'
            
            def clean_group_attrs(match):
                attrs = match.group(1)
                # Keep only valid attributes
                valid_attrs = []
                for attr_match in re.finditer(r'(\w+)="([^"]*)"', attrs):
                    attr_name = attr_match.group(1)
                    if attr_name in ['name', 'col', 'colspan']:
                        valid_attrs.append(f'{attr_name}="{attr_match.group(2)}"')
                
                if valid_attrs:
                    return f'<group {" ".join(valid_attrs)}>'
                else:
                    return '<group>'
            
            search_content = re.sub(group_pattern, clean_group_attrs, search_content)
            
            if search_content != original_search:
                content = content.replace(original_search, search_content)
                self.log_fix(file_path, "Clean search group attrs", "Cleaned invalid attributes from search groups")
                file_modified = True
        
        # Fix 6: Fix form view issues - remove string from field groups in specific cases
        # Check for problematic patterns in form views
        form_pattern = r'<group[^>]+string="[^"]*"[^>]*>\s*<field'
        if re.search(form_pattern, content):
            # This is a tricky one - we need context to know if it's valid
            # For now, log it for manual review
            self.log_fix(file_path, "REVIEW", "Contains <group string=> with immediate <field> - may need review")
        
        # Fix 7: Fix any remaining widget issues
        # statusbar widget requires specific attributes in Odoo 19
        if 'widget="statusbar"' in content:
            # Ensure statusbar fields have proper attributes
            statusbar_pattern = r'<field[^>]+widget="statusbar"[^>]+>'
            matches = re.findall(statusbar_pattern, content)
            for match in matches:
                if 'statusbar_visible' not in match and 'options=' not in match:
                    self.log_fix(file_path, "REVIEW", "statusbar widget without statusbar_visible attribute")
        
        # Write back if modified
        if file_modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_modified.append(str(file_path))
            return True
        
        return False
    
    def process_module(self, module_name):
        """Process all XML files in a module"""
        module_path = self.base_path / module_name
        
        if not module_path.exists():
            print(f"⚠️  Module {module_name} not found at {module_path}")
            return
        
        print(f"\n{'='*60}")
        print(f"Processing module: {module_name}")
        print(f"{'='*60}")
        
        # Find all XML files in views directory
        views_path = module_path / 'views'
        if views_path.exists():
            xml_files = list(views_path.glob('*.xml'))
            print(f"Found {len(xml_files)} XML files in views/")
            
            for xml_file in xml_files:
                print(f"\nProcessing: {xml_file.name}")
                if self.fix_xml_file(xml_file):
                    print(f"  ✓ Modified")
                else:
                    print(f"  - No changes needed")
        
        # Also check data directory
        data_path = module_path / 'data'
        if data_path.exists():
            xml_files = list(data_path.glob('*.xml'))
            if xml_files:
                print(f"\nFound {len(xml_files)} XML files in data/")
                
                for xml_file in xml_files:
                    print(f"\nProcessing: {xml_file.name}")
                    if self.fix_xml_file(xml_file):
                        print(f"  ✓ Modified")
                    else:
                        print(f"  - No changes needed")
        
        # Check security directory for group references
        security_path = module_path / 'security'
        if security_path.exists():
            xml_files = list(security_path.glob('*.xml'))
            if xml_files:
                print(f"\nFound {len(xml_files)} XML files in security/")
                
                for xml_file in xml_files:
                    print(f"\nProcessing: {xml_file.name}")
                    if self.fix_xml_file(xml_file):
                        print(f"  ✓ Modified")
                    else:
                        print(f"  - No changes needed")
    
    def print_summary(self):
        """Print summary of all fixes applied"""
        print(f"\n{'='*60}")
        print("SUMMARY OF FIXES")
        print(f"{'='*60}")
        print(f"Total files modified: {len(self.files_modified)}")
        print(f"Total fixes applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\nFixes by type:")
            fix_types = {}
            for fix in self.fixes_applied:
                fix_type = fix['type']
                if fix_type not in fix_types:
                    fix_types[fix_type] = 0
                fix_types[fix_type] += 1
            
            for fix_type, count in sorted(fix_types.items()):
                print(f"  - {fix_type}: {count}")
            
            print("\nDetailed fixes:")
            for fix in self.fixes_applied:
                print(f"  {fix['type']} in {Path(fix['file']).name}: {fix['details']}")
        
        if self.files_modified:
            print(f"\nModified files:")
            for file_path in self.files_modified:
                print(f"  - {file_path}")

def main():
    """Main execution"""
    base_path = Path('/opt/gemini_odoo19/addons')
    
    print("="*60)
    print("Odoo 19 Compatibility Fix Script")
    print("="*60)
    
    fixer = Odoo19Fixer(base_path)
    
    # Process all OPS modules
    modules = [
        'ops_matrix_core',
        'ops_matrix_reporting',
        'ops_matrix_accounting',
        'ops_matrix_asset_management'
    ]
    
    for module in modules:
        fixer.process_module(module)
    
    fixer.print_summary()
    
    print("\n✓ All fixes applied!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
