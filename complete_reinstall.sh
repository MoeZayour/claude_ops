#!/bin/bash

set -e

echo "════════════════════════════════════════════════════════════"
echo "STEP 1: REINSTALL ALL MODULES"
echo "════════════════════════════════════════════════════════════"
echo "Starting at: $(date)"

# Stop container
echo "Stopping existing container..."
docker stop gemini_odoo19 || true
sleep 5

# Run module reinstall
echo "Running module reinstall..."
docker run --rm --network host \
  -v /opt/gemini_odoo19/addons:/mnt/extra-addons:ro \
  -v /opt/gemini_odoo19/config:/etc/odoo \
  odoo:19.0 odoo -c /etc/odoo/odoo.conf -d mz-db \
  -i sale_management,purchase,stock,account,ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management \
  --stop-after-init

echo "Module reinstall completed at: $(date)"
sleep 10

echo ""
echo "════════════════════════════════════════════════════════════"
echo "STEP 2: RESTART ODOO"
echo "════════════════════════════════════════════════════════════"

docker compose -f /opt/gemini_odoo19/docker-compose.yml up -d
sleep 20

echo "Odoo restarted at: $(date)"

# Verify running
echo ""
echo "Container status:"
docker ps | grep gemini_odoo19

echo ""
echo "════════════════════════════════════════════════════════════"
echo "STEP 3: RUN SEEDING SCRIPT"
echo "════════════════════════════════════════════════════════════"

cd /opt/gemini_odoo19
bash addons/ops_matrix_core/data/execute_seeding.sh

echo "Seeding completed at: $(date)"
sleep 10

echo ""
echo "════════════════════════════════════════════════════════════"
echo "STEP 4: VERIFY FINAL COUNTS"
echo "════════════════════════════════════════════════════════════"

echo ""
echo "--- Data Counts ---"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT 'Business Units' as item, COUNT(*)::text as count FROM ops_business_unit
UNION ALL SELECT 'Branches', COUNT(*)::text FROM ops_branch
UNION ALL SELECT 'Customers', COUNT(*)::text FROM res_partner WHERE customer_rank > 0
UNION ALL SELECT 'Vendors', COUNT(*)::text FROM res_partner WHERE supplier_rank > 0
UNION ALL SELECT 'Products', COUNT(*)::text FROM product_product WHERE default_code IN ('LAP-BUS-001','MSE-WRL-001','CBL-USC-002','MON-27K-001','KBD-MEC-RGB')
UNION ALL SELECT 'Sales Orders', COUNT(*)::text FROM sale_order WHERE create_date > NOW() - INTERVAL '1 hour'
UNION ALL SELECT 'Purchase Orders', COUNT(*)::text FROM purchase_order WHERE create_date > NOW() - INTERVAL '1 hour';"

echo ""
echo "--- Duplicate Check (should be 0 rows) ---"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "
SELECT default_code, COUNT(*) as duplicates
FROM product_product 
WHERE default_code IS NOT NULL 
GROUP BY default_code 
HAVING COUNT(*) > 1;"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "FINAL SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo "✓ Modules reinstalled successfully"
echo "✓ Odoo restarted"
echo "✓ Seeding completed"
echo "✓ System ready for UAT testing at https://dev.mz-im.com/"
echo ""
echo "Completed at: $(date)"
echo "════════════════════════════════════════════════════════════"
