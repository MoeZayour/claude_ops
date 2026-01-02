#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Configure Accounting Journals for OPS Framework
Fix ISS-003: Create missing journals (INV, BILL, PDC)
"""

import logging

_logger = logging.getLogger(__name__)

# Journal configuration
REQUIRED_JOURNALS = [
    {
        'code': 'INV',
        'name': 'Sales Journal',
        'type': 'sale',
    },
    {
        'code': 'BILL',
        'name': 'Purchase Journal',
        'type': 'purchase',
    },
    {
        'code': 'PDC',
        'name': 'Post-Dated Checks Journal',
        'type': 'general',
    },
]

def create_missing_journals():
    """Check and create missing accounting journals"""
    
    print("\n" + "="*60)
    print("OPS Framework - Journal Auto-Configuration")
    print("="*60 + "\n")
    
    # Get the journal model
    Journal = env['account.journal']
    
    # Get the main company (first company in database)
    company = env['res.company'].search([], limit=1)
    if not company:
        print("ERROR: No company found in database!")
        return
    
    print(f"Target Company: {company.name} (ID: {company.id})\n")
    
    created_count = 0
    existing_count = 0
    
    for journal_config in REQUIRED_JOURNALS:
        code = journal_config['code']
        name = journal_config['name']
        journal_type = journal_config['type']
        
        # Check if journal already exists
        existing_journal = Journal.search([
            ('code', '=', code),
            ('company_id', '=', company.id)
        ], limit=1)
        
        if existing_journal:
            print(f"✓ Journal '{code}' already exists")
            print(f"  - Name: {existing_journal.name}")
            print(f"  - Type: {existing_journal.type}")
            print(f"  - ID: {existing_journal.id}\n")
            existing_count += 1
        else:
            try:
                # Create the journal (Odoo 19 auto-creates sequences)
                new_journal = Journal.create({
                    'name': name,
                    'code': code,
                    'type': journal_type,
                    'company_id': company.id,
                    'show_on_dashboard': True,
                })
                
                print(f"✓ Created journal '{code}'")
                print(f"  - Name: {new_journal.name}")
                print(f"  - Type: {new_journal.type}")
                print(f"  - ID: {new_journal.id}\n")
                created_count += 1
                
            except Exception as e:
                print(f"✗ ERROR creating journal '{code}': {str(e)}\n")
    
    # Commit changes to database
    try:
        env.cr.commit()
        print("="*60)
        print("Database changes committed successfully!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"ERROR committing changes: {str(e)}")
        return
    
    # Summary
    print("\nSummary:")
    print(f"  - Existing journals: {existing_count}")
    print(f"  - Created journals: {created_count}")
    print(f"  - Total journals: {existing_count + created_count}\n")
    
    if created_count > 0:
        print("✓ Journal auto-configuration completed successfully!")
    else:
        print("✓ All required journals already exist - no action needed.")
    
    print("\n" + "="*60 + "\n")

# Execute the function
if __name__ == '__main__':
    create_missing_journals()
