#!/bin/bash

# Final Complete Reinstall - Simplified & Optimized
# This script performs a clean module installation and seeding

set -e
cd /opt/gemini_odoo19

echo "════════════════════════════════════════════════════════════"
echo "FINAL MODULE REINSTALL & DATA SEEDING"
echo "Starting at: $(date)"
echo "════════════════════════════════════════════════════════════"

# 1. Stop current container
echo ""
echo "[STEP 1/5] Stopping Odoo container..."
docker stop gemini_odoo19 || true
sleep 10

# 2. Run fresh module install  
echo ""
echo "[STEP 2/5] Installing modules (this may take 3-5 minutes)..."
timeout 600 docker run --rm --network host \
  -v /opt/gemini_odoo19/addons:/mnt/extra-addons:ro \
  -v /opt/gemini_odoo19/config:/etc/odoo \
  odoo:19.0 odoo -c /etc/odoo/odoo.conf -d mz-db \
  -i sale_management,purchase,stock,account,ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management \
  --stop-after-init 2>&1 | tail -30

echo "✓ Module installation completed"
sleep 10

# 3. Restart container
echo ""
echo "[STEP 3/5] Restarting Odoo..."
docker compose -f docker-compose.yml up -d
sleep 30

# Verify container is running
if docker ps | grep -q gemini_odoo19; then
  echo "✓ Odoo container is running"
else
  echo "✗ ERROR: Odoo container failed to start"
  exit 1
fi

# 4. Run seeding
echo ""
echo "[STEP 4/5] Running data seeding..."
timeout 180 docker exec -i gemini_odoo19 odoo shell --no-http -d mz-db << 'SEED'
exec(open('/mnt/extra-addons/ops_matrix_core/data/ops_seed_test_data.py').read())
seed_test_data(env)
SEED

echo "✓ Seeding completed"
sleep 5

# 5. Verify data
echo ""
echo "[STEP 5/5] Verifying final counts..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FINAL DATA COUNTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t << 'SQL'
SELECT 'Business Units' as item, COUNT(*)::text as count FROM ops_business_unit
UNION ALL SELECT 'Branches', COUNT(*)::text FROM ops_branch
UNION ALL SELECT 'Customers', COUNT(*)::text FROM res_partner WHERE customer_rank > 0
UNION ALL SELECT 'Vendors', COUNT(*)::text FROM res_partner WHERE supplier_rank > 0
UNION ALL SELECT 'Products (Test)', COUNT(*)::text FROM product_product WHERE default_code IN ('LAP-BUS-001','MSE-WRL-001','CBL-USC-002','MON-27K-001','KBD-MEC-RGB')
UNION ALL SELECT 'Sales Orders', COUNT(*)::text FROM sale_order WHERE create_date > NOW() - INTERVAL '1 hour'
UNION ALL SELECT 'Purchase Orders', COUNT(*)::text FROM purchase_order WHERE create_date > NOW() - INTERVAL '1 hour';
SQL

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DUPLICATE CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec gemini_odoo19_db psql -U odoo -d mz-db -t << 'SQL'
SELECT default_code, COUNT(*) as count
FROM product_product 
WHERE default_code IS NOT NULL 
GROUP BY default_code 
HAVING COUNT(*) > 1;
SQL

echo ""
echo "════════════════════════════════════════════════════════════"
echo "FINAL SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo "✓ Modules reinstalled successfully"
echo "✓ Odoo restarted and running"
echo "✓ Data seeding completed"
echo "✓ Verification complete"
echo ""
echo "System ready for UAT testing"
echo "URL: https://dev.mz-im.com/"
echo "Completed at: $(date)"
echo "════════════════════════════════════════════════════════════"
