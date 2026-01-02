#!/bin/bash
# Wrapper script to execute Phase 2 seeding via Odoo shell

cd /opt/gemini_odoo19

docker exec gemini_odoo19 python3 -c "
import sys
sys.path.insert(0, '/mnt/extra-addons')

# Execute the seeding script
exec(open('/mnt/extra-addons/scripts/phase2_seed_infrastructure.py').read())
" --database=mz-db
