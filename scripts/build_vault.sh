#!/bin/bash
# OPS Matrix Framework - Vault Builder
# Compiles Python modules to .so binaries for production deployment
# Usage: ./scripts/build_vault.sh [--test-mode] [--restore] [--help]

set -e  # Exit on error

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

WORKSPACE_ROOT="/opt/gemini_odoo19"
MODULES=("ops_matrix_core" "ops_matrix_accounting" "ops_matrix_reporting")
BACKUP_DIR="${WORKSPACE_ROOT}/vault_backup_$(date +%Y%m%d_%H%M%S)"
BUILD_DIR="${WORKSPACE_ROOT}/vault_build"
LOG_DIR="${WORKSPACE_ROOT}/logs"
LOG_FILE="${LOG_DIR}/vault_build_$(date +%Y%m%d_%H%M%S).log"
TEST_MODE=false
RESTORE_MODE=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} | $1" | tee -a "${LOG_FILE}"
}

log_success() {
    log "${GREEN}✓${NC} $1"
}

log_error() {
    log "${RED}❌${NC} $1"
}

log_warning() {
    log "${YELLOW}⚠️${NC}  $1"
}

log_info() {
    log "${BLUE}ℹ${NC}  $1"
}

show_help() {
    cat << EOF
OPS Matrix Framework - Vault Builder

USAGE:
    ./scripts/build_vault.sh [OPTIONS]

OPTIONS:
    --test-mode     Skip Odoo boot tests (for development)
    --restore       Restore from latest backup
    --help          Show this help message

DESCRIPTION:
    This script compiles Python source code in OPS Matrix modules into
    binary .so files for production deployment and intellectual property
    protection.

    Modules processed:
    - ops_matrix_core
    - ops_matrix_accounting
    - ops_matrix_reporting

PROCESS:
    1. Check prerequisites (Cython, python3-dev)
    2. Verify git status and create backup
    3. Generate setup.py for each module
    4. Compile Python files to .so binaries
    5. Clean up source files (keep __init__.py, __manifest__.py)
    6. Validate module structure
    7. Test Odoo boot (unless --test-mode)
    8. Generate build report

IMPORTANT NOTES:
    - Compiled binaries are architecture-specific (Linux x86_64)
    - Source code cannot be recovered from .so files
    - XML, CSV, and static files remain unchanged
    - Always keep backups for potential rollback

EOF
}

# ═══════════════════════════════════════════════════════════
# COMMAND-LINE ARGUMENT PARSING
# ═══════════════════════════════════════════════════════════

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test-mode)
                TEST_MODE=true
                shift
                ;;
            --restore)
                RESTORE_MODE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# ═══════════════════════════════════════════════════════════
# RESTORE FUNCTION
# ═══════════════════════════════════════════════════════════

restore_from_backup() {
    log_info "Looking for backup directories..."
    
    # Find the latest backup
    LATEST_BACKUP=$(find "${WORKSPACE_ROOT}" -maxdepth 1 -type d -name "vault_backup_*" | sort -r | head -n 1)
    
    if [ -z "${LATEST_BACKUP}" ]; then
        log_error "No backup found to restore"
        exit 1
    fi
    
    log_info "Found backup: ${LATEST_BACKUP}"
    log_warning "This will overwrite current modules!"
    
    read -p "Continue with restore? (y/N): " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
    
    for module in "${MODULES[@]}"; do
        if [ -d "${LATEST_BACKUP}/${module}" ]; then
            log_info "Restoring ${module}..."
            rm -rf "addons/${module}"
            cp -r "${LATEST_BACKUP}/${module}" "addons/"
            log_success "${module} restored"
        else
            log_warning "${module} not found in backup"
        fi
    done
    
    log_success "Restore complete!"
    exit 0
}

# ═══════════════════════════════════════════════════════════
# PRE-BUILD VALIDATION
# ═══════════════════════════════════════════════════════════

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "python3 not found"
        exit 1
    fi
    log_success "Python 3 found: $(python3 --version)"
    
    # Check/Install Cython
    if ! python3 -c "import Cython" 2>/dev/null; then
        log_warning "Cython not found. Installing..."
        pip3 install Cython || {
            log_error "Failed to install Cython"
            exit 1
        }
    fi
    log_success "Cython available: $(python3 -c 'import Cython; print(Cython.__version__)')"
    
    # Check/Install python3-dev
    if ! dpkg -l | grep -q python3-dev; then
        log_warning "python3-dev not found. Installing..."
        apt-get update && apt-get install -y python3-dev build-essential || {
            log_error "Failed to install python3-dev"
            exit 1
        }
    fi
    log_success "python3-dev and build-essential available"
    
    # Check gcc
    if ! command -v gcc &> /dev/null; then
        log_error "gcc not found (needed for compilation)"
        exit 1
    fi
    log_success "GCC compiler found: $(gcc --version | head -n1)"
}

check_git_status() {
    log_info "Checking git status..."
    
    cd "${WORKSPACE_ROOT}"
    
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        log_warning "Uncommitted changes detected!"
        git status --short
        echo
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
    else
        log_success "Working directory clean"
    fi
}

create_backup() {
    log_info "Creating backup at: ${BACKUP_DIR}"
    mkdir -p "${BACKUP_DIR}"
    
    for module in "${MODULES[@]}"; do
        if [ -d "addons/${module}" ]; then
            log_info "Backing up ${module}..."
            cp -r "addons/${module}" "${BACKUP_DIR}/"
            log_success "${module} backed up"
        else
            log_error "Module not found: addons/${module}"
            exit 1
        fi
    done
    
    log_success "Backup complete"
}

# ═══════════════════════════════════════════════════════════
# COMPILATION LOGIC
# ═══════════════════════════════════════════════════════════

generate_setup_py() {
    local module_path=$1
    local module_name=$2
    
    cat > "${module_path}/setup.py" << 'SETUP_EOF'
from setuptools import setup
from Cython.Build import cythonize
import os

# Find all .py files except __init__.py and __manifest__.py
py_files = []
for root, dirs, files in os.walk('.'):
    # Skip __pycache__, tests, migrations, wizard directories
    if '__pycache__' in root or '/tests' in root or '/migrations' in root:
        continue
    
    for file in files:
        if file.endswith('.py') and file not in ['__init__.py', '__manifest__.py', 'setup.py']:
            rel_path = os.path.join(root, file)
            py_files.append(rel_path)

if not py_files:
    print("Warning: No Python files found to compile")
else:
    print(f"Found {len(py_files)} Python files to compile")
    for f in py_files:
        print(f"  - {f}")

setup(
    name='MODULE_NAME_vault',
    ext_modules=cythonize(
        py_files,
        compiler_directives={
            'language_level': '3',
            'embedsignature': True,
        },
        nthreads=4,
    ) if py_files else [],
)
SETUP_EOF
    
    # Replace MODULE_NAME placeholder
    sed -i "s/MODULE_NAME/${module_name}/g" "${module_path}/setup.py"
}

compile_module() {
    local module=$1
    local module_path="addons/${module}"
    
    log_info "═══════════════════════════════════════════════════════════"
    log_info "Compiling ${module}..."
    log_info "═══════════════════════════════════════════════════════════"
    
    # Generate setup.py
    log_info "Generating setup.py..."
    generate_setup_py "${module_path}" "${module}"
    
    # Run compilation
    log_info "Running Cythonization..."
    cd "${module_path}"
    
    if python3 setup.py build_ext --inplace 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "Compilation successful"
    else
        log_error "Compilation failed for ${module}"
        cd "${WORKSPACE_ROOT}"
        return 1
    fi
    
    cd "${WORKSPACE_ROOT}"
    
    # Count compiled files
    local so_count=$(find "${module_path}" -name "*.so" | wc -l)
    log_success "Generated ${so_count} .so files"
    
    return 0
}

cleanup_module() {
    local module=$1
    local module_path="addons/${module}"
    
    log_info "Cleaning up ${module}..."
    
    cd "${module_path}"
    
    # Delete source .py files (excluding protected ones)
    log_info "Removing source .py files..."
    find . -type f -name "*.py" \
        ! -name "__init__.py" \
        ! -name "__manifest__.py" \
        ! -path "*/migrations/*" \
        -delete
    
    # Clean up build artifacts
    log_info "Removing build artifacts..."
    find . -type f -name "*.c" -delete
    find . -type f -name "*.pyc" -delete
    find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove setup.py
    rm -f setup.py
    
    cd "${WORKSPACE_ROOT}"
    
    log_success "Cleanup complete for ${module}"
}

# ═══════════════════════════════════════════════════════════
# POST-BUILD VALIDATION
# ═══════════════════════════════════════════════════════════

validate_module_structure() {
    local module=$1
    local module_path="addons/${module}"
    
    log_info "Validating ${module} structure..."
    
    # Check __manifest__.py exists
    if [ ! -f "${module_path}/__manifest__.py" ]; then
        log_error "Missing __manifest__.py in ${module}"
        return 1
    fi
    
    # Check __init__.py exists
    if [ ! -f "${module_path}/__init__.py" ]; then
        log_error "Missing __init__.py in ${module}"
        return 1
    fi
    
    # Check .so files were created
    local so_count=$(find "${module_path}" -name "*.so" | wc -l)
    if [ $so_count -eq 0 ]; then
        log_error "No .so files generated in ${module}"
        return 1
    fi
    
    # Check for remaining .py files (should only be __init__.py and __manifest__.py)
    local py_count=$(find "${module_path}" -name "*.py" ! -name "__init__.py" ! -name "__manifest__.py" ! -path "*/migrations/*" | wc -l)
    
    log_success "Structure validation passed"
    log_info "  - Compiled binaries: ${so_count}"
    log_info "  - Remaining .py files: ${py_count} (should be 0)"
    
    if [ $py_count -gt 0 ]; then
        log_warning "Found ${py_count} non-protected .py files:"
        find "${module_path}" -name "*.py" ! -name "__init__.py" ! -name "__manifest__.py" ! -path "*/migrations/*" | head -n 5
    fi
    
    return 0
}

test_odoo_boot() {
    if [ "$TEST_MODE" = true ]; then
        log_info "Skipping Odoo boot test (--test-mode enabled)"
        return 0
    fi
    
    log_info "Testing Odoo boot with compiled modules..."
    
    # Test basic boot
    if timeout 60s docker exec gemini_odoo19 odoo \
        --database=mz-db \
        --stop-after-init \
        --log-level=error 2>&1 | grep -qi "error"; then
        log_error "Odoo failed to boot with errors"
        return 1
    fi
    
    log_success "Odoo boot successful"
    return 0
}

test_module_upgrade() {
    if [ "$TEST_MODE" = true ]; then
        log_info "Skipping module upgrade test (--test-mode enabled)"
        return 0
    fi
    
    log_info "Testing module upgrade..."
    
    if docker exec gemini_odoo19 odoo \
        -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting \
        --database=mz-db \
        --stop-after-init \
        --log-level=info 2>&1 | tee -a "${LOG_FILE}" | grep -qi "error"; then
        log_error "Module upgrade failed"
        return 1
    fi
    
    log_success "Module upgrade successful"
    return 0
}

# ═══════════════════════════════════════════════════════════
# ROLLBACK FUNCTION
# ═══════════════════════════════════════════════════════════

rollback_build() {
    log_error "Build failed! Rolling back..."
    
    for module in "${MODULES[@]}"; do
        if [ -d "${BACKUP_DIR}/${module}" ]; then
            log_info "Restoring ${module} from backup..."
            rm -rf "addons/${module}"
            cp -r "${BACKUP_DIR}/${module}" "addons/"
        fi
    done
    
    log_success "Rollback complete. Original modules restored."
    exit 1
}

# ═══════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════

generate_build_report() {
    echo ""
    log "═══════════════════════════════════════════════════════════"
    log "  ${GREEN}🔒 VAULT BUILD COMPLETE${NC}"
    log "═══════════════════════════════════════════════════════════"
    echo ""
    log "📊 Build Statistics:"
    
    local total_so=0
    local total_py=0
    
    for module in "${MODULES[@]}"; do
        local so_count=$(find "addons/${module}" -name "*.so" | wc -l)
        local py_count=$(find "addons/${module}" -name "*.py" ! -name "__init__.py" ! -name "__manifest__.py" ! -path "*/migrations/*" | wc -l)
        
        total_so=$((total_so + so_count))
        total_py=$((total_py + py_count))
        
        log "  ${BLUE}${module}${NC}:"
        log "    - Compiled binaries: ${so_count}"
        log "    - Remaining .py files: ${py_count} (should be 0)"
        
        if [ $py_count -gt 0 ]; then
            log_warning "    ⚠️  Non-protected .py files found!"
        fi
    done
    
    echo ""
    log "📈 Total Summary:"
    log "  - Total .so binaries: ${total_so}"
    log "  - Total remaining .py: ${total_py}"
    echo ""
    log "💾 Backup location: ${BACKUP_DIR}"
    log "📄 Build log: ${LOG_FILE}"
    echo ""
    log "${YELLOW}⚠️  IMPORTANT NOTES:${NC}"
    log "  1. Test all functionality thoroughly before production deployment"
    log "  2. Keep the backup in case rollback is needed"
    log "  3. .so files are architecture-specific (x86_64 Linux)"
    log "  4. Python version: $(python3 --version)"
    log "  5. Target platform: Linux x86_64"
    log "  6. Source code cannot be recovered from .so files"
    echo ""
    log "✅ Modules are now vault-protected and ready for production deployment"
    log "═══════════════════════════════════════════════════════════"
    echo ""
}

# ═══════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════

main() {
    # Create log directory
    mkdir -p "${LOG_DIR}"
    
    # Start logging
    log "═══════════════════════════════════════════════════════════"
    log "  OPS Matrix Framework - Vault Builder"
    log "  Started: $(date)"
    log "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Parse arguments
    parse_arguments "$@"
    
    # Handle restore mode
    if [ "$RESTORE_MODE" = true ]; then
        restore_from_backup
    fi
    
    # Display mode
    if [ "$TEST_MODE" = true ]; then
        log_warning "Running in TEST MODE (Odoo tests will be skipped)"
    fi
    
    # Change to workspace
    cd "${WORKSPACE_ROOT}"
    
    # Step 1: Prerequisites
    log_info "Step 1/7: Checking prerequisites..."
    check_prerequisites
    echo ""
    
    # Step 2: Git status
    log_info "Step 2/7: Checking git status..."
    check_git_status
    echo ""
    
    # Step 3: Create backup
    log_info "Step 3/7: Creating backup..."
    create_backup
    echo ""
    
    # Step 4: Compile modules
    log_info "Step 4/7: Compiling modules..."
    for module in "${MODULES[@]}"; do
        if ! compile_module "${module}"; then
            rollback_build
        fi
        echo ""
    done
    
    # Step 5: Cleanup
    log_info "Step 5/7: Cleaning up build artifacts..."
    for module in "${MODULES[@]}"; do
        cleanup_module "${module}"
    done
    echo ""
    
    # Step 6: Validate
    log_info "Step 6/7: Validating module structures..."
    for module in "${MODULES[@]}"; do
        if ! validate_module_structure "${module}"; then
            rollback_build
        fi
    done
    echo ""
    
    # Step 7: Test Odoo
    log_info "Step 7/7: Testing Odoo integration..."
    if ! test_odoo_boot; then
        rollback_build
    fi
    
    if ! test_module_upgrade; then
        rollback_build
    fi
    echo ""
    
    # Generate final report
    generate_build_report
    
    log "Build completed successfully at $(date)"
}

# ═══════════════════════════════════════════════════════════
# SCRIPT ENTRY POINT
# ═══════════════════════════════════════════════════════════

# Trap errors and perform rollback
trap 'log_error "An error occurred. Exiting..."; exit 1' ERR

# Run main function
main "$@"
