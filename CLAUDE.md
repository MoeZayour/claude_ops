# CLAUDE.md - Claude Code CLI Configuration

## 🎯 Identity & Role

You are **Claude Code**, the primary development agent for the OPS Framework project.
Your job is to deliver **fully working Odoo 19 custom modules**.

**Golden Rule:** Everything must be done through **source code only**. You are **strictly forbidden** from directly manipulating the database.

---

## 📍 Project Location

```
Path: /opt/gemini_odoo19
Port: 8089
Database: mz-db
Container: gemini_odoo19
Odoo Version: 19.0
GitHub: https://github.com/MoeZayour/claude_ops
```

---

## 📁 Directory Structure

```
/opt/gemini_odoo19/                 ← YOUR ROOT WORKSPACE
├── addons/                         ← Primary development (modules)
│   ├── ops_matrix_core/
│   ├── ops_matrix_accounting/
│   ├── ops_matrix_reporting/
│   ├── ops_matrix_asset_management/
│   ├── oca_reporting_engine/      ← Dependency (READ-ONLY)
│   └── report_xlsx/               ← Dependency (READ-ONLY)
├── claude_files/                   ← Documentation & reports
├── docs/                           ← User/admin documentation
├── config/                         ← Configuration (READ-ONLY)
├── _backup/                        ← Backups (NEVER TOUCH)
├── .roo/                           ← System files (NEVER TOUCH)
├── logs/                           ← Log files (READ-ONLY)
├── OPS_FRAMEWORK_FEATURES_MASTER.md ← Feature tracking
└── docker-compose.yml              ← Docker config (READ-ONLY)
```

---

## ✅ PERMISSIONS

### FULL ACCESS (Read/Write/Create/Delete)
- `/opt/gemini_odoo19/addons/ops_matrix_*/` - Module development
- `/opt/gemini_odoo19/claude_files/` - Documentation
- `/opt/gemini_odoo19/docs/` - Project documentation
- `/opt/gemini_odoo19/*.md` - Root markdown files
- `/opt/gemini_odoo19/*.py` - Root python scripts
- `/opt/gemini_odoo19/*.sh` - Root shell scripts

### READ-ONLY ACCESS
- `/opt/gemini_odoo19/addons/oca_reporting_engine/` - External dependency
- `/opt/gemini_odoo19/addons/report_xlsx/` - External dependency
- `/opt/gemini_odoo19/config/` - Configuration files
- `/opt/gemini_odoo19/logs/` - Log files
- `/opt/gemini_odoo19/docker-compose.yml` - Docker configuration

### NO ACCESS (NEVER TOUCH)
- `/opt/gemini_odoo19/_backup/` - System backups
- `/opt/gemini_odoo19/.roo/` - System files
- Anything outside `/opt/gemini_odoo19/`

---

## ✅ MUST DO

### 1. Stay Within Project Root
All work must be inside `/opt/gemini_odoo19/`. Never access files outside this directory.

### 2. Follow Odoo 19 Standards

**Python:**
- PEP 8 compliant
- 4 spaces indentation (no tabs)
- Max line length: 120 characters
- Docstrings for all public methods
- Type hints where appropriate

**XML:**
- 2 spaces indentation
- Always close tags properly
- Use meaningful IDs: `module_name.view_model_type`

**Model Naming:**
```python
_name = 'ops.feature.model'  # e.g., ops.branch, ops.budget.line
# Auto table: ops_feature_model (e.g., ops_branch, ops_budget_line)
```

### 3. Use Odoo ORM Exclusively

```python
# ✅ CORRECT
record = self.env['ops.branch'].create({'name': 'Test'})
records = self.env['ops.branch'].search([('active', '=', True)])
record.write({'name': 'Updated'})

# ❌ WRONG - Never use raw SQL
self.env.cr.execute("INSERT INTO ops_branch ...")
```

### 4. Test Before Committing

```bash
# Test in Odoo shell
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
# Your test code here
PYTHON
```

### 5. Update Module After Changes

```bash
docker exec gemini_odoo19 odoo \
  -c /etc/odoo/odoo.conf \
  -d mz-db \
  -u MODULE_NAME \
  --stop-after-init \
  --no-http
```

### 6. Check Logs

```bash
docker logs gemini_odoo19 --tail 100 | grep -i error
docker logs gemini_odoo19 --tail 50 --follow
```

### 7. Git Operations

```bash
# Stage & commit
git add .
git commit -m "type(scope): description"
git push origin main

# Pull updates
git pull origin main

# Check status
git status
git log --oneline -10
```

### 8. Feature Tracking

Always check `OPS_FRAMEWORK_FEATURES_MASTER.md` before development:
- Mark implemented features: `[x] ✅`
- Mark partial features: `[~] 🚧`
- Track missing features: `[ ] ❌`

---

## ❌ NEVER DO

| Forbidden Action | Reason |
|------------------|--------|
| ❌ Access files outside `/opt/gemini_odoo19/` | Outside project scope |
| ❌ Direct database manipulation | Source code only |
| ❌ Use raw SQL queries | ORM only |
| ❌ Modify `oca_reporting_engine/` | External dependency |
| ❌ Modify `report_xlsx/` | External dependency |
| ❌ Modify `config/` or `docker-compose.yml` | Infrastructure locked |
| ❌ Access `_backup/` or `.roo/` | System files |
| ❌ Skip testing before commit | Quality required |
| ❌ Break existing functionality | Preserve working code |

---

## 🔧 Common Commands

### Module Management
```bash
# Update single module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core --stop-after-init --no-http

# Update multiple modules
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting --stop-after-init --no-http
```

### Debugging
```bash
# Check module states
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
modules = self.env['ir.module.module'].search([('name', 'like', 'ops_matrix_%')])
for m in modules: print(f"{m.name}: {m.state}")
PYTHON

# Interactive shell
docker exec -it gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http
```

---

## 🏗️ Module Structure

```
ops_matrix_newmodule/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── model_name.py
├── views/
│   └── model_name_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security_rules.xml
├── wizards/
│   ├── __init__.py
│   └── wizard_name.py
├── reports/
│   └── report_template.xml
└── static/description/icon.png
```

### Manifest Template
```python
{
    'name': 'OPS Matrix - Module Name',
    'version': '19.0.1.0.0',
    'category': 'OPS Framework',
    'author': 'Antigravity AI',
    'license': 'LGPL-3',
    'depends': ['base', 'ops_matrix_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/model_name_views.xml',
    ],
    'installable': True,
    'application': False,
}
```

---

## 🎯 Installed Modules

| Module | Status | Purpose |
|--------|--------|---------|
| `ops_matrix_core` | ✅ Installed | Core framework, personas, security |
| `ops_matrix_accounting` | ✅ Installed | Accounting, budgets, PDC |
| `ops_matrix_reporting` | ✅ Installed | Reports, dashboards, analytics |
| `ops_matrix_asset_management` | ✅ Installed | Asset tracking, depreciation |

---

## 🧪 Development Workflow

1. Pull latest code from GitHub
2. Check `OPS_FRAMEWORK_FEATURES_MASTER.md` for requirements
3. Write/modify code following standards
4. Test in Odoo shell
5. Update module
6. Check logs for errors
7. Test in browser (port 8089)
8. Update feature master with status
9. Commit with conventional message
10. Push to GitHub

---

## 📊 Feature Status Tracking

After implementing features, update `OPS_FRAMEWORK_FEATURES_MASTER.md`:

```markdown
- [x] ✅ **Feature Name** - (model: ops.x.y, views: 2, working)
- [~] 🚧 **Partial Feature** - (model exists, views incomplete)
- [ ] ❌ **Missing Feature** - (not implemented)
```

Generate completion stats:
```markdown
## 📊 IMPLEMENTATION STATUS
**Module Completion:**
- OPS_MATRIX_CORE: X% (Y/Z complete)
**Overall: X% Complete**
**Last Audit**: [timestamp]
```

---

## ⚠️ Critical Reminders

> **Database `mz-db` is production.**
> All changes via source code only.

> **Deliver complete, working modules.**
> Not partial solutions. Fully functional code.

> **Stay within `/opt/gemini_odoo19/`.**
> Full access here, no access outside.

> **Check existing code first.**
> Patterns are in `ops_matrix_core`.

> **Update feature master after changes.**
> Track implementation progress.

---

## 🔗 Quick Links

- System: http://localhost:8089 or https://dev.mz-im.com
- GitHub: https://github.com/MoeZayour/claude_ops
- Features: `/opt/gemini_odoo19/OPS_FRAMEWORK_FEATURES_MASTER.md`
- Docs: `/opt/gemini_odoo19/docs/`
