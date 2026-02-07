#!/bin/bash
# OPS Framework - Master Data Seeding Script
# Run from: /opt/gemini_odoo19/
# Usage: bash seed/run_all.sh

set -e

CONTAINER="gemini_odoo19"
CONF="/etc/odoo/odoo.conf"
DB="mz-db"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  OPS Framework - Data Seeding"
echo "  $(date)"
echo "============================================"

run_seed() {
    local file=$1
    local desc=$2
    echo ""
    echo -e "${YELLOW}--- [$desc] ---${NC}"
    echo "Running: seed/$file"
    if cat "seed/$file" | docker exec -i $CONTAINER odoo shell -c $CONF -d $DB --no-http --log-level=warn 2>&1; then
        echo -e "${GREEN}✓ $desc completed${NC}"
    else
        echo -e "${RED}✗ $desc FAILED${NC}"
        echo "Continuing with next script..."
    fi
}

run_seed "01_company_structure.py" "Step 1/9: Company Structure"
run_seed "02_users_personas.py"    "Step 2/9: Users & Personas"
run_seed "03_partners.py"          "Step 3/9: Partners"
run_seed "04_sales.py"             "Step 4/9: Sales Orders"
run_seed "05_purchases.py"         "Step 5/9: Purchase Orders"
run_seed "06_invoices_payments.py" "Step 6/9: Invoices & Payments"
run_seed "07_pdc_budgets.py"       "Step 7/9: PDC & Budgets"
run_seed "08_assets.py"            "Step 8/9: Fixed Assets"
run_seed "09_governance.py"        "Step 9/9: Governance Rules"

echo ""
echo "============================================"
echo "  All seeding completed!"
echo "  $(date)"
echo "============================================"
