#!/bin/bash

# OPS Matrix Framework - UAT Data Seeding Script
# ================================================
# This script executes the test data seeding process inside the running Odoo container.

set -e  # Exit on any error

echo "========================================="
echo "OPS Matrix UAT Data Seeding"
echo "========================================="
echo "Starting seeding process..."

# Execute the seeding script inside the Odoo container
docker exec -i gemini_odoo19 odoo shell --no-http -d mz-db << 'EOF'
# Execute the seeding code directly
exec(open('/mnt/extra-addons/ops_matrix_core/data/ops_seed_test_data.py').read())
seed_test_data(env)
EOF

echo "========================================="
echo "Seeding script execution completed."
echo "Check container logs for seeding results."
echo "========================================="