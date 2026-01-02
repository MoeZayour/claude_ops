#!/usr/bin/env python3
"""
Emergency Asset Regeneration Script
====================================
Fixes 404 errors on /web/assets/... by clearing corrupted asset bundles.
Run this inside the Odoo container when assets are corrupted.

Usage:
    docker exec -it gemini_odoo19-web-1 python3 /opt/gemini_odoo19/regenerate_assets.py
"""

import sys
import os

# Add Odoo to path
sys.path.append('/opt/odoo')

import odoo
from odoo import api, SUPERUSER_ID

def regenerate_assets():
    """Clear all web asset bundles to force regeneration."""
    print("=" * 70)
    print("EMERGENCY ASSET REGENERATION")
    print("=" * 70)
    
    # Initialize Odoo environment
    odoo.tools.config.parse_config([
        '-c', '/etc/odoo/odoo.conf',
        '-d', 'postgres'
    ])
    
    with odoo.api.Environment.manage():
        registry = odoo.registry('postgres')
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Step 1: Find all asset attachments
            print("\n[1/3] Searching for asset bundles...")
            asset_attachments = env['ir.attachment'].search([
                ('url', 'like', '/web/assets/%')
            ])
            asset_count = len(asset_attachments)
            print(f"    Found {asset_count} asset bundle(s)")
            
            # Step 2: Delete them
            if asset_count > 0:
                print(f"\n[2/3] Deleting {asset_count} corrupted asset bundle(s)...")
                asset_attachments.unlink()
                print("    ✓ Asset bundles deleted")
            else:
                print("\n[2/3] No asset bundles found to delete")
            
            # Step 3: Commit changes
            print("\n[3/3] Committing changes...")
            cr.commit()
            print("    ✓ Changes committed")
            
            print("\n" + "=" * 70)
            print("✓ ASSET REGENERATION COMPLETE")
            print("=" * 70)
            print("\nNext steps:")
            print("  1. Restart Odoo: docker compose restart web")
            print("  2. Clear browser cache: Ctrl+Shift+Delete")
            print("  3. Hard refresh: Ctrl+Shift+R")
            print("  4. Login and check if assets load correctly")
            print()

if __name__ == '__main__':
    try:
        regenerate_assets()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
