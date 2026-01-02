#!/usr/bin/env python3
"""
Script to upgrade ops_matrix_core module to create approval_locked field in database.
"""
import os
import sys
import django

# Setup Odoo environment
os.environ.setdefault('ODOO_RC', '/etc/odoo/odoo.conf')

# Import Odoo API
import odoo
from odoo import api, SUPERUSER_ID
from odoo.cli import main as odoo_main
import argparse

def upgrade_module():
    """Upgrade ops_matrix_core module."""
    # Create argument parser to pass to Odoo
    parser = argparse.ArgumentParser(description='Upgrade OPS Matrix Core module')
    args = parser.parse_args(['--database', 'mz-db', '--update', 'ops_matrix_core', '--stop-after-init'])
    
    # This will execute the upgrade
    sys.argv = ['odoo', '--database', 'mz-db', '--update', 'ops_matrix_core', '--stop-after-init']
    return odoo_main()

if __name__ == '__main__':
    print("Starting module upgrade for ops_matrix_core...")
    upgrade_module()
    print("Module upgrade completed!")
