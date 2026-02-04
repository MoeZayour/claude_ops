# Phase 0: Environment Verification

**Duration:** 15 minutes  
**Objective:** Verify the environment is ready for module installation

---

## Task 0.1: Verify Docker Container

```bash
echo "========================================"
echo "PHASE 0: ENVIRONMENT VERIFICATION"
echo "========================================"

echo "=== Checking Docker container ==="
docker ps | grep gemini_odoo19

echo "=== Checking Odoo version ==="
docker exec gemini_odoo19 odoo --version

echo "✅ Docker container verified"
```

---

## Task 0.2: Verify Database Connection

```bash
echo "=== Testing database connection ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT version();"

echo "=== Checking installed modules ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ops_%' ORDER BY name;"

echo "✅ Database connection verified"
```

---

## Task 0.3: Verify Module Source Files

```bash
echo "=== Checking module directories ==="
ls -la /opt/gemini_odoo19/addons/

echo "=== Verifying ops_matrix_core exists ==="
ls /opt/gemini_odoo19/addons/ops_matrix_core/__manifest__.py

echo "=== Verifying ops_matrix_accounting exists ==="
ls /opt/gemini_odoo19/addons/ops_matrix_accounting/__manifest__.py

echo "=== Verifying ops_theme exists ==="
ls /opt/gemini_odoo19/addons/ops_theme/__manifest__.py

echo "=== Verifying ops_dashboard exists ==="
ls /opt/gemini_odoo19/addons/ops_dashboard/__manifest__.py

echo "✅ All module directories verified"
```

---

## Task 0.4: Create Report Directory

```bash
echo "=== Creating report directory ==="
mkdir -p /opt/gemini_odoo19/claude_files/go_live_audit

echo "=== Initializing execution log ==="
cat > /opt/gemini_odoo19/claude_files/go_live_audit/00_EXECUTION_LOG.md << 'EOF'
# OPS Framework Go-Live Execution Log

**Started:** $(date)
**Executor:** Claude Code
**Target:** Production Readiness

---

## Execution Timeline

| Time | Phase | Action | Result |
|------|-------|--------|--------|
EOF

echo "✅ Report directory created"
```

---

## Task 0.5: Verify Git Status

```bash
echo "=== Checking git status ==="
cd /opt/gemini_odoo19
git status
git log --oneline -5

echo "✅ Git repository verified"
```

---

## Task 0.6: Clear Previous Logs

```bash
echo "=== Clearing previous Odoo logs ==="
docker logs gemini_odoo19 --tail 10

echo "=== Restarting container for clean state ==="
docker restart gemini_odoo19
sleep 10

echo "=== Verifying container is running ==="
docker ps | grep gemini_odoo19

echo "✅ Container restarted"
```

---

## Phase 0 Completion Checklist

Before proceeding to Phase 1, verify:

- [ ] Docker container `gemini_odoo19` is running
- [ ] Database `mz-db` is accessible
- [ ] All 4 module directories exist with `__manifest__.py`
- [ ] Report directory created at `/opt/gemini_odoo19/claude_files/go_live_audit/`
- [ ] Git repository is clean or changes committed
- [ ] Container restarted successfully

---

## Log Entry

Add to `00_EXECUTION_LOG.md`:
```
| [TIME] | Phase 0 | Environment Verification | ✅ COMPLETE |
```

---

## PROCEED TO PHASE 1
