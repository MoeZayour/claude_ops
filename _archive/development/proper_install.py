#!/usr/bin/env python3
"""Properly install OPS modules via Odoo shell"""
import os
import sys

# Setup environment
os.environ['ODOO_CONFIG'] = '/etc/odoo/odoo.conf'

# Add Odoo to path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import odoo
from odoo.cli import main

# Redirect to install command
sys.argv = [
    'odoo',
    '-c', '/etc/odoo/odoo.conf',
    '-d', 'mz-db',
    '-i', 'ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management',
    '--stop-after-init'
]

if __name__ == '__main__':
    main()
