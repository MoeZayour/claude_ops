#!/bin/bash
# Wrapper script to execute the test data seeding

docker exec gemini_odoo19 /usr/bin/python3 << 'PYTHON_SCRIPT'
import odoo
from odoo import api, SUPERUSER_ID
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Configure Odoo
odoo.tools.config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'mz-db'])

# Get registry
registry = odoo.registry('mz-db')

# Execute in transaction
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    _logger.info("Executing seeding script...")
    
    # Read and execute the seeding script
    with open('/mnt/extra-addons/ops_matrix_core/data/ops_seed_test_data.py', 'r') as f:
        script_content = f.read()
    
    # Execute with env in context
    exec(script_content, {'env': env, '_logger': _logger})
    
    # Commit
    cr.commit()
    _logger.info("✅ Transaction committed successfully")

PYTHON_SCRIPT
