# OPS Matrix Framework - Vault Builder Guide

## Overview

The Vault Builder ([`build_vault.sh`](build_vault.sh)) is a production hardening script that compiles Python source code into binary `.so` files using Cython. This protects intellectual property by making the source code unreadable while maintaining full functionality.

## Purpose

- **IP Protection**: Source code is compiled into binary format that cannot be reverse-engineered
- **Production Deployment**: Creates a production-ready version of OPS Matrix modules
- **Performance**: Compiled code can offer slight performance improvements
- **Security**: Prevents unauthorized access to business logic and algorithms

---

## Quick Start

```bash
# Show help
./scripts/build_vault.sh --help

# Test build (skips Odoo validation)
./scripts/build_vault.sh --test-mode

# Full production build
./scripts/build_vault.sh

# Restore from backup
./scripts/build_vault.sh --restore
```

---

## Prerequisites

The script automatically checks and installs:

1. **Cython** - Python-to-C compiler
2. **python3-dev** - Python development headers
3. **build-essential** - GCC compiler and build tools
4. **Git** - For repository status checking

### Manual Installation (if needed)

```bash
pip3 install Cython
apt-get install -y python3-dev build-essential
```

---

## Build Process

### 1. Pre-Build Phase

**Checks performed:**
- ✓ Verifies Python 3.x is available
- ✓ Ensures Cython is installed
- ✓ Confirms GCC compiler is present
- ✓ Checks git repository status
- ✓ Warns about uncommitted changes

**Backup creation:**
- Full backup of all three modules created in `vault_backup_YYYYMMDD_HHMMSS/`
- Backup includes complete directory structure
- Used for automatic rollback on failure

### 2. Compilation Phase

For each module (`ops_matrix_core`, `ops_matrix_accounting`, `ops_matrix_reporting`):

**Step 1: Generate setup.py**
- Automatically discovers all `.py` files
- Excludes `__init__.py`, `__manifest__.py`
- Skips `tests/` and `migrations/` directories
- Configures Cython with Python 3 language level

**Step 2: Run Cythonization**
```bash
python3 setup.py build_ext --inplace
```
- Compiles Python to C code
- Compiles C code to `.so` binaries
- Generates architecture-specific binaries

**Step 3: Cleanup**
- Deletes source `.py` files (except protected ones)
- Removes intermediate `.c` files
- Cleans up build artifacts
- Preserves all XML, CSV, and static files

### 3. Validation Phase

**Structure checks:**
- ✓ `__manifest__.py` exists
- ✓ `__init__.py` exists in all directories
- ✓ `.so` binaries were generated
- ✓ No unprotected `.py` files remain

**Odoo integration tests (unless `--test-mode`):**
- ✓ Odoo boots successfully with compiled modules
- ✓ Modules can be upgraded without errors
- ✓ No runtime errors during initialization

### 4. Reporting Phase

Generates comprehensive build report with:
- Number of `.so` files per module
- Remaining `.py` files (should be 0)
- Backup location
- Build log location
- Important deployment notes

---

## Protected Files (Never Deleted)

The script protects these critical files from deletion:

### Python Files
- `__init__.py` - Required for Python module loading
- `__manifest__.py` - Required for Odoo module metadata
- `migrations/**/*.py` - Migration scripts (kept as source)

### Non-Python Files (Untouched)
- `*.xml` - Views, data, security rules
- `*.csv` - Access control lists
- `*.js`, `*.css` - Static assets
- `*.png`, `*.jpg`, `*.ico` - Images
- `*.md` - Documentation
- `static/**/*` - All static resources

---

## Command-Line Options

### `--test-mode`

**Purpose**: Test the build process without Odoo validation

**Use cases:**
- Development and testing
- Verifying compilation works
- Debugging build issues
- CI/CD pipelines

**What it skips:**
- Odoo boot test
- Module upgrade test

**Example:**
```bash
./scripts/build_vault.sh --test-mode
```

### `--restore`

**Purpose**: Restore modules from the latest backup

**Use cases:**
- Build failed and needs rollback
- Testing revealed issues
- Need to return to source version

**Process:**
1. Finds latest `vault_backup_*` directory
2. Shows backup location
3. Asks for confirmation
4. Restores all three modules

**Example:**
```bash
./scripts/build_vault.sh --restore
```

### `--help`

**Purpose**: Display usage information

**Example:**
```bash
./scripts/build_vault.sh --help
```

---

## Build Output

### Directory Structure After Build

```
addons/ops_matrix_core/
├── __init__.py              ✓ Kept
├── __manifest__.py          ✓ Kept
├── models/
│   ├── __init__.py          ✓ Kept
│   ├── ops_branch.so        ✓ Compiled binary
│   ├── ops_persona.so       ✓ Compiled binary
│   └── ...
├── views/
│   ├── ops_branch_views.xml ✓ Untouched
│   └── ...
├── security/
│   ├── ir.model.access.csv  ✓ Untouched
│   └── ir_rule.xml          ✓ Untouched
├── migrations/
│   └── 19.0.1.0/
│       ├── __init__.py      ✓ Kept as source
│       └── post_migration.py ✓ Kept as source
└── static/
    └── ...                  ✓ All untouched
```

### Log Files

**Location**: `logs/vault_build_YYYYMMDD_HHMMSS.log`

**Contains:**
- Timestamp for each operation
- Prerequisite check results
- Compilation output for each module
- Validation results
- Error messages (if any)
- Final statistics

---

## Architecture and Platform Requirements

### Compiled Binaries Are Platform-Specific

The `.so` files generated are **only compatible with**:

| Requirement | Value |
|------------|-------|
| **Operating System** | Linux |
| **Architecture** | x86_64 (64-bit Intel/AMD) |
| **Python Version** | 3.10+ |
| **Odoo Version** | 19.0 |

### Cross-Platform Considerations

❌ **Will NOT work on:**
- Windows (requires `.pyd` files, different compilation)
- macOS (requires `.dylib` files, different compilation)
- ARM architecture (Raspberry Pi, Apple Silicon)
- Different Python versions (3.8, 3.9, 3.11+)

✓ **Will work on:**
- Linux x86_64 servers
- Docker containers based on Linux x86_64
- Cloud VMs (AWS, GCP, Azure) running Linux x86_64

### Recompilation for Different Platforms

If you need to deploy to a different platform:

1. Copy source code to target platform
2. Run the build script on that platform
3. Binaries will be compiled for the target architecture

---

## Error Handling and Rollback

### Automatic Rollback Triggers

The script automatically rolls back if:
- Compilation fails for any module
- Module validation fails (missing files)
- Odoo boot test fails
- Module upgrade test fails

### Rollback Process

1. Script detects failure
2. Displays error message
3. Restores all modules from backup
4. Exits with error code

### Manual Rollback

```bash
# Using the restore option
./scripts/build_vault.sh --restore

# Or manually copy from backup
cp -r vault_backup_20251228_120000/ops_matrix_core addons/
cp -r vault_backup_20251228_120000/ops_matrix_accounting addons/
cp -r vault_backup_20251228_120000/ops_matrix_reporting addons/
```

---

## Testing Protocol

### Phase 1: Test Mode Build

```bash
# Run build without Odoo validation
./scripts/build_vault.sh --test-mode
```

**Verify:**
- ✓ Compilation succeeds for all modules
- ✓ `.so` files are generated
- ✓ No source `.py` files remain (except protected)
- ✓ `__init__.py` and `__manifest__.py` intact
- ✓ XML/CSV files untouched

### Phase 2: Manual Verification

```bash
# Check one module structure
ls -la addons/ops_matrix_core/models/

# Should see:
# - __init__.py
# - *.so files (compiled binaries)
# - NO *.py files (except __init__.py)

# Count compiled files
find addons/ops_matrix_core -name "*.so" | wc -l

# Check for remaining source files
find addons/ops_matrix_core -name "*.py" ! -name "__init__.py" ! -name "__manifest__.py" ! -path "*/migrations/*"
```

### Phase 3: Full Build with Odoo Tests

```bash
# Run full build with validation
./scripts/build_vault.sh
```

**Verify:**
- ✓ Odoo boots successfully
- ✓ Modules upgrade without errors
- ✓ No error messages in Odoo log

### Phase 4: Functional Testing

1. **Login Test**
   ```bash
   # Access Odoo UI
   http://localhost:8089
   # Login with admin/admin
   ```

2. **Module Functionality**
   - Navigate to OPS Matrix menus
   - Create/edit Branches, Personas, BUs
   - Test governance rules
   - Verify dashboards load
   - Check security rules work

3. **API Testing**
   ```bash
   # Test API endpoints (if applicable)
   curl http://localhost:8089/ops_matrix_api/test
   ```

4. **Error Log Check**
   ```bash
   docker logs gemini_odoo19 | grep -i error
   ```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Git repository is clean (all changes committed)
- [ ] Full backup created and verified
- [ ] Test mode build completed successfully
- [ ] Full build with Odoo tests passed
- [ ] Functional testing completed
- [ ] Log files reviewed for errors

### Deployment

- [ ] Transfer compiled modules to production server
- [ ] Verify target platform matches (Linux x86_64, Python 3.10+)
- [ ] Stop Odoo service
- [ ] Replace module directories
- [ ] Upgrade modules: `odoo -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting`
- [ ] Restart Odoo service
- [ ] Monitor logs for errors

### Post-Deployment

- [ ] Test basic functionality
- [ ] Verify user access and permissions
- [ ] Check all dashboards load
- [ ] Test critical workflows
- [ ] Monitor performance
- [ ] Keep backup for 30 days minimum

---

## Troubleshooting

### Issue: Compilation Fails

**Symptom**: Build stops during compilation phase

**Possible causes:**
- Missing dependencies (Cython, python3-dev)
- Syntax errors in Python code
- Import errors

**Solution:**
1. Check the log file for specific errors
2. Fix syntax errors in source code first
3. Ensure all dependencies are installed
4. Try test mode to isolate the issue

### Issue: Odoo Won't Boot

**Symptom**: Odoo boot test fails

**Possible causes:**
- Import errors in compiled modules
- Missing dependencies
- Database incompatibility

**Solution:**
1. Automatic rollback will restore source
2. Check Odoo logs: `docker logs gemini_odoo19`
3. Test with source version first
4. Fix issues before recompiling

### Issue: Remaining .py Files

**Symptom**: Validation shows non-zero remaining .py files

**Possible causes:**
- New files not excluded properly
- Test files in non-standard locations

**Investigation:**
```bash
# Find remaining files
find addons/ops_matrix_core -name "*.py" \
  ! -name "__init__.py" \
  ! -name "__manifest__.py" \
  ! -path "*/migrations/*"
```

**Action:**
- If they're test files: Safe to ignore or add to exclusion
- If they're model files: They should have been compiled - check logs

### Issue: Module Upgrade Fails

**Symptom**: Module upgrade test fails

**Possible causes:**
- Database schema changes not compatible
- Missing XML/CSV files
- Broken dependencies

**Solution:**
1. Automatic rollback restores source
2. Test upgrade with source version
3. Check `__manifest__.py` is intact
4. Verify all data files present

---

## Security Considerations

### What is Protected

✓ **Python source code** - Business logic, algorithms, models
✓ **Custom methods** - Your proprietary implementations
✓ **Computed fields** - Calculation logic
✓ **Domain logic** - Security and filtering rules (in Python)

### What is NOT Protected

❌ **XML views** - UI structure visible in files
❌ **CSV data** - Access rules visible in files
❌ **JavaScript** - Frontend code visible
❌ **Database structure** - Can be inspected via Odoo UI
❌ **Workflow logic** - Visible through Odoo interface

### Additional Security Measures

1. **Obfuscate XML IDs**: Use cryptic naming conventions
2. **Encrypt Database**: Use PostgreSQL encryption
3. **Access Control**: Limit file system access
4. **SSL/TLS**: Encrypt all network traffic
5. **Audit Logs**: Enable comprehensive logging

---

## Backup Management

### Automatic Backups

- Created before each build
- Named: `vault_backup_YYYYMMDD_HHMMSS`
- Contains full module directories
- Never automatically deleted

### Manual Backup Cleanup

```bash
# List all backups
ls -ld vault_backup_*

# Remove old backups (after confirming production works)
rm -rf vault_backup_20251201_*

# Keep at least the last 3 backups
ls -td vault_backup_* | tail -n +4 | xargs rm -rf
```

### Backup Retention Policy

**Recommended:**
- Keep last 3 build backups
- Keep one backup per month for 6 months
- Archive to external storage before deletion

---

## Performance Considerations

### Compilation Time

Approximate build times:
- Small module (10 files): 30-60 seconds
- Medium module (50 files): 2-5 minutes
- Large module (100+ files): 5-10 minutes

**OPS Matrix total**: ~3-5 minutes for all three modules

### Runtime Performance

- Compiled code: ~5-10% faster (varies by use case)
- Startup time: Similar to source version
- Memory usage: Slightly lower

### Storage

- `.so` files are larger than `.py` files
- Expect ~2-3x disk space usage
- Example: 1MB source → 2-3MB compiled

---

## Advanced Usage

### Custom Module List

Edit the script to compile different modules:

```bash
# Edit build_vault.sh
MODULES=("your_module_1" "your_module_2")
```

### Selective Compilation

To compile only specific files, modify `generate_setup_py()` function to add file filters.

### Compiler Optimization

Edit setup.py template for optimization flags:

```python
compiler_directives={
    'language_level': '3',
    'embedsignature': True,
    'optimize.use_switch': True,
    'optimize.unpack_method_calls': True,
}
```

---

## CI/CD Integration

### GitLab CI Example

```yaml
vault_build:
  stage: build
  script:
    - ./scripts/build_vault.sh --test-mode
    - tar -czf ops_matrix_vault.tar.gz addons/ops_matrix_*
  artifacts:
    paths:
      - ops_matrix_vault.tar.gz
    expire_in: 30 days
```

### GitHub Actions Example

```yaml
name: Build Vault
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Vault
        run: |
          ./scripts/build_vault.sh --test-mode
      - name: Archive artifacts
        uses: actions/upload-artifact@v2
        with:
          name: vault-modules
          path: addons/ops_matrix_*
```

---

## Support and Maintenance

### Log Analysis

All operations are logged to `logs/vault_build_*.log`

**Key sections to review:**
- Prerequisite checks
- Compilation output
- Validation results
- Error messages

### Getting Help

If build fails repeatedly:

1. Review the log file
2. Check prerequisites are installed
3. Verify source code has no syntax errors
4. Test in `--test-mode` first
5. Check disk space is sufficient
6. Ensure Docker container is running

### Reporting Issues

When reporting build issues, include:
- Build log file
- Odoo version
- Python version (`python3 --version`)
- Cython version (`python3 -c 'import Cython; print(Cython.__version__)'`)
- Operating system and architecture
- Git commit hash

---

## Frequently Asked Questions

### Q: Can I reverse the compilation?

**A:** No. Once compiled to `.so` files, the source code cannot be recovered. Always keep backups of the original source.

### Q: Will updates break compiled modules?

**A:** Yes. Any Odoo upgrade or Python version change may require recompilation from source.

### Q: Can I mix compiled and source modules?

**A:** Yes. You can have some modules compiled and others as source code.

### Q: Does this work on Windows?

**A:** No. The script and `.so` format are Linux-specific. Windows requires different compilation process.

### Q: How do I update a compiled module?

**A:** Update the source code, then run the build script again. Or restore from backup, make changes, and rebuild.

### Q: Is performance significantly better?

**A:** Typically 5-10% improvement. The main benefit is IP protection, not performance.

### Q: Can I distribute compiled modules?

**A:** Yes, but they're platform-specific. Recipients need matching Python version and architecture.

### Q: What if I need to debug?

**A:** Restore from backup to get source version, debug, fix, then recompile.

---

## Appendix: File Extensions

| Extension | Description | Action |
|-----------|-------------|--------|
| `.py` | Python source | Compiled to `.so` (except protected files) |
| `.so` | Shared object (compiled binary) | Created by build process |
| `.c` | C source code | Temporary, deleted after build |
| `.pyc` | Python bytecode | Deleted (not needed with `.so`) |
| `.xml` | Odoo views/data | Preserved untouched |
| `.csv` | Access control | Preserved untouched |
| `.js` | JavaScript | Preserved untouched |
| `.css` | Stylesheets | Preserved untouched |
| `.png`, `.jpg`, `.ico` | Images | Preserved untouched |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-28 | Initial release with full vault functionality |

---

## License and Legal

**Important**: Compiled modules are derivative works. Ensure you have rights to distribute compiled versions if sharing with others. The compilation process does not change licensing requirements.

---

**End of Guide**

For more information about OPS Matrix Framework, see the main documentation in `addons/ops_matrix_core/static/description/`.
