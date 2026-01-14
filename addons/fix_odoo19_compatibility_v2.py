#!/usr/bin/env python3
"""
Enhanced Odoo 19 Compatibility Fixer for OPS Matrix Modules
Fixes all attrs= patterns including complex multi-condition cases
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class EnhancedOdoo19Fixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / f"backups_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.changes_log = []
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'attrs_fixes': 0,
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
        
    def convert_domain_to_expression(self, domain_str):
        """Convert Odoo domain to Python expression"""
        try:
            domain_str = domain_str.strip()
            
            # Handle negation operators
            domain_str = domain_str.replace('not in', 'NOT_IN')
            
            # Convert tuples to expressions
            # Pattern: ('field', 'operator', value)
            
            # Equality with strings
            domain_str = re.sub(r"\('([^']+)',\s*'=',\s*'([^']+)'\)", r"\1 == '\2'", domain_str)
            domain_str = re.sub(r'\("([^"]+)",\s*"=",\s*"([^"]+)"\)', r"\1 == '\2'", domain_str)
            
            # Inequality with strings
            domain_str = re.sub(r"\('([^']+)',\s*'!=',\s*'([^']+)'\)", r"\1 != '\2'", domain_str)
            domain_str = re.sub(r'\("([^"]+)",\s*"!=",\s*"([^"]+)"\)', r"\1 != '\2'", domain_str)
            
            # Equality with booleans
            domain_str = re.sub(r"\('([^']+)',\s*'=',\s*True\)", r"\1", domain_str)
            domain_str = re.sub(r'\("([^"]+)",\s*"=",\s*True\)', r"\1", domain_str)
            domain_str = re.sub(r"\('([^']+)',\s*'=',\s*False\)", r"not \1", domain_str)
            domain_str = re.sub(r'\("([^"]+)",\s*"=",\s*False\)', r"not \1", domain_str)
            
            # in operator with lists
            domain_str = re.sub(r"\('([^']+)',\s*'in',\s*\[([^\]]+)\]\)", r"\1 in [\2]", domain_str)
            domain_str = re.sub(r'\("([^"]+)",\s*"in",\s*\[([^\]]+)\]\)', r"\1 in [\2]", domain_str)
            
            # not in operator with lists (restore from NOT_IN)
            domain_str = domain_str.replace('NOT_IN', 'not in')
            domain_str = re.sub(r"\('([^']+)',\s*'not in',\s*\[([^\]]+)\]\)", r"\1 not in [\2]", domain_str)
            domain_str = re.sub(r'\("([^"]+)",\s*"not in",\s*\[([^\]]+)\]\)', r"\1 not in [\2]", domain_str)
            
            # Clean up list brackets if present
            domain_str = domain_str.strip('[]').strip()
            
            return domain_str
            
        except Exception as e:
            print(f"  Warning: Could not convert domain '{domain_str}': {e}")
            return None
    
    def fix_attrs_comprehensive(self, content, file_path):
        """Comprehensive attrs= conversion to Odoo 19 expressions"""
        changes = []
        new_content = content
        modified = False
        
        # Pattern to match attrs with any combination of invisible, readonly, required
        # This handles both single and double quotes, and complex nested structures
        attrs_pattern = r'''attrs=(["'])(\{[^}]+\})\1'''
        
        matches = list(re.finditer(attrs_pattern, new_content, re.DOTALL))
        
        for match in reversed(matches):  # Process in reverse to maintain positions
            try:
                quote_char = match.group(1)
                attrs_content = match.group(2)
                
                # Parse the attrs dictionary
                new_attrs = []
                
                # Extract invisible conditions
                invisible_match = re.search(r"'invisible':\s*(\[[^\]]+\])", attrs_content)
                if invisible_match:
                    domain = invisible_match.group(1)
                    expr = self.convert_domain_to_expression(domain)
                    if expr:
                        new_attrs.append(f'invisible="{expr}"')
                
                # Extract readonly conditions
                readonly_match = re.search(r"'readonly':\s*(\[[^\]]+\])", attrs_content)
                if readonly_match:
                    domain = readonly_match.group(1)
                    expr = self.convert_domain_to_expression(domain)
                    if expr:
                        new_attrs.append(f'readonly="{expr}"')
                
                # Extract required conditions
                required_match = re.search(r"'required':\s*(\[[^\]]+\])", attrs_content)
                if required_match:
                    domain = required_match.group(1)
                    expr = self.convert_domain_to_expression(domain)
                    if expr:
                        new_attrs.append(f'required="{expr}"')
                
                if new_attrs:
                    # Replace the old attrs with new individual attributes
                    old_text = match.group(0)
                    new_text = ' '.join(new_attrs)
                    
                    # Calculate positions
                    start = match.start()
                    end = match.end()
                    
                    new_content = new_content[:start] + new_text + new_content[end:]
                    
                    changes.append(f"Converted attrs: {old_text[:50]}...")
                    self.stats['attrs_fixes'] += 1
                    modified = True
                    
            except Exception as e:
                error_msg = f"Error converting attrs in {file_path}: {str(e)} - {match.group(0)[:100]}"
                self.stats['errors'].append(error_msg)
                print(f"  ✗ {error_msg}")
        
        if changes:
            self.log_change(file_path, 'attrs_conversion', f"Converted {len(changes)} attrs")
            
        return new_content, modified
    
    def process_xml_file(self, file_path):
        """Process a single XML file"""
        try:
            self.stats['files_processed'] += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Check if file has attrs= that need conversion
            if 'attrs=' not in original_content:
                return
            
            content, file_modified = self.fix_attrs_comprehensive(original_content, file_path)
            
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
        
        print(f"Found {len(modules)} OPS modules to process")
        print()
        
        # Process each module
        for module in modules:
            print(f"\nProcessing module: {module.name}")
            print('-'*60)
            
            # Find and process all XML files
            xml_files = list(module.rglob('*.xml'))
            
            for xml_file in xml_files:
                self.process_xml_file(xml_file)
    
    def print_summary(self):
        """Print summary of all changes"""
        print("\n" + "="*60)
        print("ENHANCED ATTRS CONVERSION SUMMARY")
        print("="*60)
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files modified: {self.stats['files_modified']}")
        print(f"attrs= conversions: {self.stats['attrs_fixes']}")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print("\n✓ No errors encountered!")
        
        if self.backup_dir.exists():
            print(f"\nBackups saved to: {self.backup_dir}")
        
        if self.changes_log:
            print("\nFiles modified:")
            print("-" * 60)
            for change in self.changes_log:
                file_rel = Path(change['file']).relative_to(self.base_path)
                print(f"  {file_rel}: {change['details']}")

def main():
    """Main execution"""
    base_path = Path('/opt/gemini_odoo19/addons')
    
    print("Enhanced Odoo 19 attrs= Converter for OPS Matrix Modules")
    print("="*60)
    print(f"Base path: {base_path}")
    print()
    
    fixer = EnhancedOdoo19Fixer(base_path)
    fixer.process_all_modules()
    fixer.print_summary()
    
    print("\n" + "="*60)
    print("✓ ENHANCED ATTRS CONVERSION COMPLETED!")
    print("="*60)

if __name__ == '__main__':
    main()
