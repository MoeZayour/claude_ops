# Phase 1: Module Installation

**Duration:** 60 minutes  
**Objective:** Install all 4 OPS modules in dependency order

---

## INSTALLATION ORDER (CRITICAL)

```
1. ops_matrix_core       (foundation - no OPS dependencies)
2. ops_matrix_accounting (depends on ops_matrix_core)
3. ops_theme             (standalone, but recommended after core)
4. ops_dashboard         (depends on core + accounting)
```

---

## Task 1.1: Install ops_matrix_core

```bash
echo "========================================"
echo "PHASE 1: MODULE INSTALLATION"
echo "========================================"

echo "=== Installing ops_matrix_core ==="
echo "Started: $(date)"

docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i ops_matrix_core --stop-after-init 2>&1 | tee /tmp/install_core.log

echo "=== Checking installation result ==="
tail -50 /tmp/install_core.log | grep -E "(ERROR|error|Exception|Traceback|installed)"

echo "=== Verifying module state ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name = 'ops_matrix_core';"

echo "Completed: $(date)"
echo "✅ ops_matrix_core installation attempted"
```

**If errors occur:**
- Read the full error from `/tmp/install_core.log`
- Fix the source code issue
- Re-attempt installation
- Document fix in `02_ERROR_FIX_REPORT.md`

---

## Task 1.2: Install ops_matrix_accounting

```bash
echo "=== Installing ops_matrix_accounting ==="
echo "Started: $(date)"

docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i ops_matrix_accounting --stop-after-init 2>&1 | tee /tmp/install_accounting.log

echo "=== Checking installation result ==="
tail -50 /tmp/install_accounting.log | grep -E "(ERROR|error|Exception|Traceback|installed)"

echo "=== Verifying module state ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name = 'ops_matrix_accounting';"

echo "Completed: $(date)"
echo "✅ ops_matrix_accounting installation attempted"
```

---

## Task 1.3: Install ops_theme

```bash
echo "=== Installing ops_theme ==="
echo "Started: $(date)"

docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i ops_theme --stop-after-init 2>&1 | tee /tmp/install_theme.log

echo "=== Checking installation result ==="
tail -50 /tmp/install_theme.log | grep -E "(ERROR|error|Exception|Traceback|installed)"

echo "=== Verifying module state ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name = 'ops_theme';"

echo "Completed: $(date)"
echo "✅ ops_theme installation attempted"
```

---

## Task 1.4: Install ops_dashboard

```bash
echo "=== Installing ops_dashboard ==="
echo "Started: $(date)"

docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i ops_dashboard --stop-after-init 2>&1 | tee /tmp/install_dashboard.log

echo "=== Checking installation result ==="
tail -50 /tmp/install_dashboard.log | grep -E "(ERROR|error|Exception|Traceback|installed)"

echo "=== Verifying module state ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name = 'ops_dashboard';"

echo "Completed: $(date)"
echo "✅ ops_dashboard installation attempted"
```

---

## Task 1.5: Verify All Modules Installed

```bash
echo "=== Final verification of all OPS modules ==="

docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT name, state, latest_version 
FROM ir_module_module 
WHERE name LIKE 'ops_%' 
ORDER BY name;
"

echo "=== Checking for any module errors ==="
docker logs gemini_odoo19 --tail 200 | grep -E "(ERROR|error)" | head -20

echo "✅ Module installation phase complete"
```

---

## Task 1.6: Restart Odoo

```bash
echo "=== Restarting Odoo container ==="
docker restart gemini_odoo19
sleep 15

echo "=== Verifying Odoo is responding ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login || echo "Checking via docker..."
docker logs gemini_odoo19 --tail 20

echo "✅ Odoo restarted"
```

---

## Task 1.7: Generate Installation Report

Create `/opt/gemini_odoo19/claude_files/go_live_audit/01_INSTALLATION_REPORT.md`:

```markdown
# Module Installation Report

**Date:** [DATE]
**Executor:** Claude Code

## Installation Summary

| Module | Version | State | Install Time | Errors |
|--------|---------|-------|--------------|--------|
| ops_matrix_core | X.X.X | installed/error | Xm Xs | 0/X |
| ops_matrix_accounting | X.X.X | installed/error | Xm Xs | 0/X |
| ops_theme | X.X.X | installed/error | Xm Xs | 0/X |
| ops_dashboard | X.X.X | installed/error | Xm Xs | 0/X |

## Installation Details

### ops_matrix_core
- Started: [TIME]
- Completed: [TIME]
- Result: [SUCCESS/FAILED]
- Errors encountered: [LIST]
- Fixes applied: [LIST]

### ops_matrix_accounting
[Same structure]

### ops_theme
[Same structure]

### ops_dashboard
[Same structure]

## Dependencies Resolved

[List any dependency issues and resolutions]

## Post-Installation Verification

- [ ] All modules show state = 'installed'
- [ ] No ERROR messages in logs
- [ ] Odoo web interface accessible
- [ ] Login page loads correctly
```

---

## Phase 1 Completion Checklist

- [ ] ops_matrix_core installed successfully (state = 'installed')
- [ ] ops_matrix_accounting installed successfully
- [ ] ops_theme installed successfully
- [ ] ops_dashboard installed successfully
- [ ] No critical errors in Odoo logs
- [ ] Odoo web interface accessible
- [ ] Installation report created

---

## Git Commit (if all modules installed)

```bash
cd /opt/gemini_odoo19
git add -A
git status

git commit -m "[GO-LIVE] Phase 1: All OPS modules installed

- ops_matrix_core: v19.0.1.11.0
- ops_matrix_accounting: v19.0.16.2.0
- ops_theme: v19.0.3.1.0
- ops_dashboard: v19.0.1.0.0

Tested: Basic installation verified
Errors Fixed: [X]"

git push origin main
```

---

## PROCEED TO PHASE 2 (or loop back to fix errors)
