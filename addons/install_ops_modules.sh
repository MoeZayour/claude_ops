#!/bin/bash
# Install OPS modules one by one

DB_NAME="mz-db"
CONTAINER="gemini_odoo19"

echo "=========================================="
echo "OPS MODULES INSTALLATION"
echo "=========================================="

# First, stop any running Odoo instance
echo "Stopping Odoo if running..."
docker exec $CONTAINER pkill -9 odoo 2>/dev/null || true
sleep 2

# Function to install a module
install_module() {
    local module=$1
    local desc=$2
    
    echo ""
    echo "=========================================="
    echo "INSTALLING: $module"
    echo "Description: $desc"
    echo "=========================================="
    
    # Use --http-port=0 to prevent server from starting
    # Use -u to upgrade (works for both new installs and upgrades in Odoo 19)
    docker exec $CONTAINER odoo -d $DB_NAME -u $module --stop-after-init --http-port=0 --log-level=error 2>&1 | tee /tmp/${module}_install.log
    
    local exit_code=$?
    
    # Check for actual errors in output
    if [ $exit_code -eq 0 ] && ! grep -q "ParseError\|ValidationError\|Traceback\|CRITICAL\|Error" /tmp/${module}_install.log; then
        echo "✅ SUCCESS: $module"
        return 0
    else
        echo "❌ FAILED: $module (exit code: $exit_code)"
        echo "Error log:"
        grep -A 5 "Error\|Traceback\|ParseError\|ValidationError" /tmp/${module}_install.log | head -30
        return 1
    fi
}

# Track results
declare -A results

# Install modules in sequence
install_module "ops_matrix_core" "Core module"
results["ops_matrix_core"]=$?

install_module "ops_matrix_reporting" "Reporting module"
results["ops_matrix_reporting"]=$?

install_module "ops_matrix_accounting" "Accounting module"
results["ops_matrix_accounting"]=$?

install_module "ops_matrix_asset_management" "Asset Management module"
results["ops_matrix_asset_management"]=$?

# Print summary
echo ""
echo "=========================================="
echo "INSTALLATION SUMMARY"
echo "=========================================="

success_count=0
fail_count=0

for module in ops_matrix_core ops_matrix_reporting ops_matrix_accounting ops_matrix_asset_management; do
    if [ ${results[$module]} -eq 0 ]; then
        echo "✅ SUCCESS: $module"
        ((success_count++))
    else
        echo "❌ FAILED: $module"
        ((fail_count++))
    fi
done

echo ""
echo "=========================================="
echo "Total: $success_count successes, $fail_count failures"
echo "=========================================="

if [ $fail_count -eq 0 ]; then
    echo "🎉 ALL MODULES INSTALLED SUCCESSFULLY!"
    exit 0
else
    echo "⚠️  Some modules failed to install"
    exit 1
fi
