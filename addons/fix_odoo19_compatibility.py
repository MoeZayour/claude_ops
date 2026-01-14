#!/usr/bin/env python3
"""
Comprehensive Odoo 19 Compatibility Fixer for OPS Matrix Modules
Fixes:
1. <tree> to <list> conversions
2. group_ops_administrator to group_ops_admin_power
3. attrs= to Odoo 19 Python expressions
4. Invalid search view attributes (expand=)
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

class Odoo19CompatibilityFixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / f"backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_log = []
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'tree_to_list': 0,
            'group_fixes': 0,
            'attrs_fixes': 0,
            'expand_fixes': 0,
            'errors': []
        }
        
    def log_change(self, file_path, change_type, details):
        """Log a change made to a file"""
        self.changes_log.append({
            'file': str(file_path),
            'type': change_type,
            'details': details
        })
        
    def create_backup(self, file_path):
        """Create backup of a file before modification"""
        rel_path = file_path.relative_to(self.base_path)
        backup_path = self.backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
    def fix_tree_to_list(self, content, file_path):
        """Convert <tree> tags to <list> tags"""
        changes = []
        
        # Opening tree tags with attributes
        pattern1 = r'<tree\s+'
        new_content = content
        matches = len(re.findall(pattern1, content))
        if matches > 0:
            new_content = re.sub(pattern1, '<list ', new_content)
            changes.append(f"Opening <tree> tags: {matches}")
            self.stats['tree_to_list'] += matches
            
        # Opening tree tags without attributes (but not self-closing)
        pattern2 = r'<tree>'
        matches = len(re.findall(pattern2, new_content))
        if matches > 0:
            new_content = re.sub(pattern2, '<list>', new_content)
            changes.append(f"Simple <tree> tags: {matches}")
            self.stats['tree_to_list'] += matches
            
        # Closing tree tags
        pattern3 = r'</tree>'
        matches = len(re.findall(pattern3, new_content))
        if matches > 0:
            new_content = re.sub(pattern3, '</list>', new_content)
            changes.append(f"Closing </tree> tags: {matches}")
            
        if changes:
            self.log_change(file_path, 'tree_to_list', ', '.join(changes))
            
        return new_content, bool(changes)
    
    def fix_group_references(self, content, file_path):
        """Fix group_ops_administrator to group_ops_admin_power"""
        changes = []
        new_content = content
        
        # Find all occurrences
        pattern = r'group_ops_administrator'
        matches = len(re.findall(pattern, content))
        
        if matches > 0:
            new_content = re.sub(pattern, 'group_ops_admin_power', new_content)
            changes.append(f"Group references fixed: {matches}")
            self.stats['group_fixes'] += matches
            self.log_change(file_path, 'group_reference', f"Fixed {matches} group_ops_administrator references")
            
        return new_content, bool(changes)
    
    def fix_attrs_syntax(self, content, file_path):
        """Convert attrs= to Odoo 19 Python expressions"""
        changes = []
        new_content = content
        modified = False
        
        # Common attrs patterns to convert
        attrs_patterns = [
            # invisible based on field values
            (r'''attrs="{'invisible':\s*\[([^\]]+)\]}"''', self._convert_invisible_attrs),
            (r"""attrs='{"invisible":\s*\[([^\]]+)\]}'""", self._convert_invisible_attrs),
            # readonly based on field values  
            (r'''attrs="{'readonly':\s*\[([^\]]+)\]}"''', self._convert_readonly_attrs),
            (r"""attrs='{"readonly":\s*\[([^\]]+)\]}'""", self._convert_readonly_attrs),
            # required based on field values
            (r'''attrs="{'required':\s*\[([^\]]+)\]}"''', self._convert_required_attrs),
            (r"""attrs='{"required":\s*\[([^\]]+)\]}'""", self._convert_required_attrs),
        ]
        
        for pattern, converter in attrs_patterns:
            matches = re.finditer(pattern, new_content)
            for match in matches:
                try:
                    new_expr = converter(match.group(1))
                    if new_expr:
                        # Determine attribute name from pattern
                        if 'invisible' in pattern:
                            attr_name = 'invisible'
                        elif 'readonly' in pattern:
                            attr_name = 'readonly'
                        elif 'required' in pattern:
                            attr_name = 'required'
                        else:
                            continue
                            
                        old_attr = match.group(0)
                        new_attr = f'{attr_name}="{new_expr}"'
                        new_content = new_content.replace(old_attr, new_attr, 1)
                        changes.append(f"Converted {attr_name} attrs")
                        self.stats['attrs_fixes'] += 1
                        modified = True
                except Exception as e:
                    self.stats['errors'].append(f"Error converting attrs in {file_path}: {str(e)}")
        
        if changes:
            self.log_change(file_path, 'attrs_conversion', ', '.join(changes))
            
        return new_content, modified
    
    def _convert_invisible_attrs(self, domain_str):
        """Convert attrs invisible domain to Python expression"""
        return self._domain_to_expression(domain_str)
    
    def _convert_readonly_attrs(self, domain_str):
        """Convert attrs readonly domain to Python expression"""
        return self._domain_to_expression(domain_str)
    
    def _convert_required_attrs(self, domain_str):
        """Convert attrs required domain to Python expression"""
        return self._domain_to_expression(domain_str)
    
    def _domain_to_expression(self, domain_str):
        """Convert Odoo domain to Python expression"""
        try:
            # Clean up the domain string
            domain_str = domain_str.strip()
            
            # Simple conversions
            conversions = {
                r"\('([^']+)',\s*'=',\s*'([^']+)'\)": r"\1 == '\2'",
                r'\("([^"]+)",\s*"=",\s*"([^"]+)"\)': r"\1 == '\2'",
                r"\('([^']+)',\s*'!=',\s*'([^']+)'\)": r"\1 != '\2'",
                r'\("([^"]+)",\s*"!=",\s*"([^"]+)"\)': r"\1 != '\2'",
                r"\('([^']+)',\s*'=',\s*True\)": r"\1",
                r'\("([^"]+)",\s*"=",\s*True\)': r"\1",
                r"\('([^']+)',\s*'=',\s*False\)": r"not \1",
                r'\("([^"]+)",\s*"=",\s*False\)': r"not \1",
                r"\('([^']+)',\s*'in',\s*\[([^\]]+)\]\)": r"\1 in [\2]",
                r"\('([^']+)',\s*'not in',\s*\[([^\]]+)\]\)": r"\1 not in [\2]",
            }
            
            result = domain_str
            for pattern, replacement in conversions.items():
                result = re.sub(pattern, replacement, result)
            
            return result
        except Exception as e:
            return None
    
    def fix_search_view_expand(self, content, file_path):
        """Remove invalid expand= attributes from search views"""
        changes = []
        new_content = content
        
        # Remove expand= attributes which are invalid in Odoo 19
        patterns = [
            r'\s+expand="[^"]*"',
            r"\s+expand='[^']*'",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, new_content)
            if matches:
                new_content = re.sub(pattern, '', new_content)
                changes.append(f"Removed {len(matches)} expand attributes")
                self.stats['expand_fixes'] += len(matches)
        
        if changes:
            self.log_change(file_path, 'expand_removal', ', '.join(changes))
            
        return new_content, bool(changes)
    
    def process_xml_file(self, file_path):
        """Process a single XML file"""
        try:
            self.stats['files_processed'] += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            file_modified = False
            
            # Apply all fixes
            content, changed = self.fix_tree_to_list(content, file_path)
            file_modified = file_modified or changed
            
            content, changed = self.fix_group_references(content, file_path)
            file_modified = file_modified or changed
            
            content, changed = self.fix_attrs_syntax(content, file_path)
            file_modified = file_modified or changed
            
            content, changed = self.fix_search_view_expand(content, file_path)
            file_modified = file_modified or changed
            
            # Write changes if file was modified
            if file_modified:
                self.create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stats['files_modified'] += 1
                print(f"✓ Modified: {file_path.relative_to(self.base_path)}")
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"✗ {error_msg}")
    
    def process_python_file(self, file_path):
        """Process a single Python file for group references"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content, changed = self.fix_group_references(original_content, file_path)
            
            if changed:
                self.create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Modified: {file_path.relative_to(self.base_path)}")
                
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(f"✗ {error_msg}")
    
    def find_ops_modules(self):
        """Find all OPS matrix modules"""
        modules = []
        for item in self.base_path.iterdir():
            if item.is_dir() and item.name.startswith('ops_matrix'):
                modules.append(item)
        return sorted(modules)
    
    def process_all_modules(self):
        """Process all OPS modules"""
        modules = self.find_ops_modules()
        
        if not modules:
            print("No OPS modules found!")
            return
        
        print(f"Found {len(modules)} OPS modules to process:")
        for module in modules:
            print(f"  - {module.name}")
        print()
        
        # Process each module
        for module in modules:
            print(f"\n{'='*60}")
            print(f"Processing module: {module.name}")
            print('='*60)
            
            # Find and process all XML files
            xml_files = list(module.rglob('*.xml'))
            print(f"Found {len(xml_files)} XML files")
            
            for xml_file in xml_files:
                self.process_xml_file(xml_file)
            
            # Find and process all Python files
            py_files = list(module.rglob('*.py'))
            print(f"Found {len(py_files)} Python files")
            
            for py_file in py_files:
                self.process_python_file(py_file)
    
    def print_summary(self):
        """Print summary of all changes"""
        print("\n" + "="*60)
        print("COMPATIBILITY FIX SUMMARY")
        print("="*60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"<tree> → <list> conversions: {self.stats['tree_to_list']}")
        print(f"Group reference fixes: {self.stats['group_fixes']}")
        print(f"attrs= conversions: {self.stats['attrs_fixes']}")
        print(f"expand= removals: {self.stats['expand_fixes']}")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print("\n✓ No errors encountered!")
        
        print(f"\nBackups saved to: {self.backup_dir}")
        print("\nDetailed change log:")
        print("-" * 60)
        
        # Group changes by type
        changes_by_type = {}
        for change in self.changes_log:
            change_type = change['type']
            if change_type not in changes_by_type:
                changes_by_type[change_type] = []
            changes_by_type[change_type].append(change)
        
        for change_type, changes in sorted(changes_by_type.items()):
            print(f"\n{change_type.upper().replace('_', ' ')}:")
            for change in changes:
                file_rel = Path(change['file']).relative_to(self.base_path)
                print(f"  {file_rel}: {change['details']}")

def main():
    """Main execution"""
    base_path = Path('/opt/gemini_odoo19/addons')
    
    print("Odoo 19 Compatibility Fixer for OPS Matrix Modules")
    print("="*60)
    print(f"Base path: {base_path}")
    print()
    
    fixer = Odoo19CompatibilityFixer(base_path)
    fixer.process_all_modules()
    fixer.print_summary()
    
    print("\n" + "="*60)
    print("✓ COMPATIBILITY FIX COMPLETED!")
    print("="*60)

if __name__ == '__main__':
    main()
