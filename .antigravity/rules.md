# OPS Framework - Antigravity AI Rules

## 🎯 Project Overview
Enterprise ERP system built on Odoo 19 with 15 core priorities.
Database: mz-db (production-ready development database)
Container: gemini_odoo19 (Docker)

## 📁 File Structure
```
gemini_odoo19/
├── addons/                    ← YOUR WORK HERE
│   ├── ops_matrix_core/
│   ├── ops_matrix_accounting/
│   ├── ops_matrix_reporting/
│   └── ops_matrix_asset_management/
├── claude_files/              ← Documentation only
├── config/                    ← Read-only
└── docker-compose.yml         ← Read-only
```

## ✅ ALWAYS DO

1. **Test Before Committing**
```bash
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
# Your test code
PYTHON
```

2. **Use Odoo ORM** (not raw SQL)
```python
# Good
env['ops.branch'].create({'name': 'Test', 'code': 'TST'})

# Bad
cr.execute("INSERT INTO ops_branch ...")
```

3. **Check Logs After Changes**
```bash
docker logs gemini_odoo19 --tail 100 | grep -i error
```

4. **Commit with Clear Messages**
```bash
git commit -m "feat(module): description"
git commit -m "fix(module): description"
git commit -m "test(module): description"
```

5. **Update Module After Code Changes**
```bash
docker exec gemini_odoo19 odoo \
  -c /etc/odoo/odoo.conf \
  -d mz-db \
  -u [module_name] \
  --stop-after-init \
  --no-http
```

## ❌ NEVER DO

1. ❌ Modify files outside `addons/` directory
2. ❌ Use `ops_production` database (failed, abandoned)
3. ❌ Skip testing before commit
4. ❌ Make changes without understanding context
5. ❌ Touch `_backup/`, `.roo/`, `logs/` directories
6. ❌ Modify `config/` or `docker-compose.yml` without reason
7. ❌ Break existing functionality

## 🎯 Current Status

**Completed:**
- ✅ Phase 1: Project Cleanup (v1.0.2)
- ✅ Phase 2: Module Installation (v1.0.3)
- 🔄 Phase 3: Seed Data (v1.1.0) - VERIFY STATUS
- ⏸️ Phase 4: Testing - PENDING

**Modules Installed (mz-db):**
- ✅ ops_matrix_core
- ✅ ops_matrix_accounting
- ✅ ops_matrix_reporting
- ✅ ops_matrix_asset_management

**15 Priorities:**
1. ✅ Company Structure
2. ✅ Persona System
3. ✅ Security & Access
4. ✅ Segregation of Duties
5. ✅ Governance Framework
6. ✅ Excel Import
7. ✅ Three-Way Match
8. ✅ Auto-Escalation
9. ✅ Auto-List Accounts
10. ✅ PDC Management
11. ✅ Budget Control
12. ✅ Asset Management
13. ✅ Financial Reports
14. ✅ Dashboards
15. ✅ Export Tools

## �� Common Commands

**Restart Odoo:**
```bash
docker restart gemini_odoo19 && sleep 30
```

**Check Database:**
```bash
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
env = self.env
modules = env['ir.module.module'].search([('name', 'like', 'ops_matrix_%')])
for m in modules:
    print(f"{m.name}: {m.state}")
PYTHON
```

**View Logs:**
```bash
docker logs gemini_odoo19 --tail 50 --follow
```

**Git Status:**
```bash
git status
git log --oneline -5
git tag -l "v1.*"
```

## 🎨 Code Style

**Python:**
- Follow PEP 8
- Use 4 spaces (not tabs)
- Max line length: 120
- Docstrings for all methods

**XML:**
- Proper indentation (2 spaces)
- Close all tags
- Use meaningful IDs

**Model Naming:**
- Models: `ops.[feature].[model]` (e.g., `ops.branch`)
- Tables: `ops_[feature]_[model]` (e.g., `ops_branch`)

## 🧪 Testing Protocol

1. Write code
2. Test in Odoo shell
3. Check for errors
4. Update module if needed
5. Restart Odoo
6. Test again
7. Commit only if all tests pass

## 📊 Agent Selection Guide

**Use Gemini 3 Flash for:**
- Quick fixes
- Simple CRUD operations
- Repetitive tasks
- Data seeding

**Use Claude Sonnet 4.5 for:**
- Complex business logic
- Architecture decisions
- Debugging hard issues
- Code refactoring

**Use Gemini 3 Pro for:**
- Large context tasks
- Comprehensive analysis
- Multi-file changes

**Use Claude Opus 4.5 for:**
- Critical features
- Security implementation
- When quality > cost

## 🎯 Next Task

**Verify Phase 3 completion:**
Check if Gemini finished seeding data in mz-db.
Report counts of: BUs, branches, products, customers, transactions.
Verify all 15 priorities functional.
Determine if Phase 4 testing needed or if ready for production.
