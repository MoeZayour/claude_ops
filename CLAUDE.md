# CLAUDE.md - Claude Code CLI Configuration

## 🎯 Identity & Role

You are **Claude Code**, the execution agent for the OPS Framework project.
Your job is to deliver **fully working Odoo 19 CE custom modules** via source code.

**Golden Rule:** Everything must be done through **source code only**. You are **strictly forbidden** from directly manipulating the database (no raw INSERT/UPDATE/DELETE).

---

## 📍 Project Location

```
Host Path:      /opt/gemini_odoo19           ← YOUR ROOT WORKSPACE (git repo)
Container:      gemini_odoo19                ← Docker container name
Container Map:  ./addons → /mnt/extra-addons ← Odoo reads addons from here
Config Map:     ./config → /etc/odoo (ro)    ← Read-only config mount
Port:           8089 (HTTP), 8082 (longpoll)
Database:       mz-db (PostgreSQL via gemini_odoo19_db container)
URL:            https://ops.mz-im.com
GitHub:         https://github.com/MoeZayour/claude_ops
Odoo Version:   19.0 Community Edition
```

### Path Reference for MCP (Claude Chat)
When Claude Chat accesses this VPS via MCP tools, host paths appear under `/mnt/host-opt/`:
- MCP sees: `/mnt/host-opt/gemini_odoo19/` = Host `/opt/gemini_odoo19/`
- MCP sees: `/mnt/host-opt/gemini_odoo19/addons/` = Container `/mnt/extra-addons/`

---

## 📁 Directory Structure

```
/opt/gemini_odoo19/                     ← GIT REPO ROOT
├── CLAUDE.md                           ← THIS FILE (Claude Code config)
├── README.md                           ← Project readme
├── docker-compose.yml                  ← Docker config (READ-ONLY)
├── config/
│   └── odoo.conf                       ← Odoo configuration (READ-ONLY)
├── addons/                             ← PRIMARY DEVELOPMENT TARGET
│   ├── ops_matrix_core/                ← Foundation: structure, security, governance
│   ├── ops_matrix_accounting/          ← Finance: PDC, assets, budgets, IFRS 16
│   ├── ops_theme/                      ← UI: debranding, dark mode, login
│   └── ops_kpi/                        ← BI: KPI dashboards, widgets, auto-refresh
├── claude_files/                       ← Working docs, audit reports, specs
├── docs/                               ← User/admin documentation
├── seed/                               ← Demo data seed scripts
├── specs/                              ← Report implementation specs
├── report_waves/                       ← Report implementation wave plans
├── Clone/                              ← Reference modules (READ-ONLY)
├── _archive/                           ← Archived code versions
├── .claude/                            ← Claude Code CLI config
│   ├── commands/                       ← Custom slash commands
│   ├── skills/                         ← Installed skills
│   ├── agents/                         ← Agent definitions
│   └── settings.local.json            ← Permissions config
└── [various .md/.py files]             ← Audit reports, test scripts
```

---

## 🎯 Installed Modules (Current State)

| Module | Status | Purpose | Key Models |
|--------|--------|---------|------------|
| `ops_matrix_core` | ✅ Installed | Foundation, personas, security, governance | 40+ models |
| `ops_matrix_accounting` | ✅ Installed | PDC, assets, budgets, leases, reporting | 47+ models |
| `ops_theme` | ✅ Installed | Debranding, dark mode, login, UI enhancements | Extensions only |
| `ops_kpi` | ✅ Installed | KPI dashboards, widgets, auto-refresh | 4 models |

**Total:** 95+ models, 370+ ACL rules, 116+ record rules, 18 personas, 12 security groups

---

## ✅ PERMISSIONS

### FULL ACCESS (Read/Write/Create/Delete)
- `/opt/gemini_odoo19/addons/ops_*/` — Module development
- `/opt/gemini_odoo19/claude_files/` — Documentation & reports
- `/opt/gemini_odoo19/docs/` — Project documentation
- `/opt/gemini_odoo19/seed/` — Seed data scripts
- `/opt/gemini_odoo19/*.md` — Root markdown files
- `/opt/gemini_odoo19/*.py` — Root python scripts

### READ-ONLY ACCESS
- `/opt/gemini_odoo19/Clone/` — Reference modules
- `/opt/gemini_odoo19/config/` — Odoo configuration
- `/opt/gemini_odoo19/docker-compose.yml` — Docker config

### NO ACCESS (NEVER TOUCH)
- `/opt/gemini_odoo19/_archive/` — Archived code
- Anything outside `/opt/gemini_odoo19/`

---

## 🔒 SECURITY PROTOCOL (NON-NEGOTIABLE)

Every new transactional model MUST have ALL of these:

1. **ir.model.access.csv** — 3-tier ACL (user R, manager RWC, admin RWCD)
2. **ops_branch_id** field — `fields.Many2one('ops.branch', tracking=True)`
3. **Branch isolation record rule** — `[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]`
4. **IT Admin blindness rule** — `[(0, '=', 1)]` for `group_ops_it_admin`
5. **Cost field visibility** — `groups='ops_matrix_core.group_ops_see_cost'`
6. **mail.thread + mail.activity.mixin** inheritance
7. **company_id** field with `default=lambda self: self.env.company`
8. **tracking=True** on key fields (name, state, amounts)
9. **_sql_constraints** for uniqueness per company
10. **_description** on model class

### IT Admin Blocked Models (24 total)
Core (17): sale.order, sale.order.line, purchase.order, purchase.order.line, account.move, account.move.line, account.payment, account.bank.statement, account.bank.statement.line, stock.picking, stock.move, stock.move.line, stock.quant, stock.valuation.layer, product.pricelist, product.pricelist.item, account.analytic.line

Accounting (7): ops.pdc.receivable, ops.pdc.payable, ops.budget, ops.budget.line, ops.asset, ops.asset.category, ops.asset.depreciation

### SQL Injection Prevention
```python
# ✅ ALWAYS parameterized
self.env.cr.execute("SELECT id FROM table WHERE name = %s", (value,))

# ❌ NEVER string formatting
self.env.cr.execute(f"SELECT id FROM table WHERE name = '{value}'")
```

---

## 🔧 Common Commands

### Module Management
```bash
# Update single module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core --stop-after-init

# Update multiple modules
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting --stop-after-init

# Install new module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i NEW_MODULE --stop-after-init

# Restart container
docker restart gemini_odoo19
```

### Diagnostics
```bash
# View logs
docker logs gemini_odoo19 --tail 100 -f

# Check for errors
docker logs gemini_odoo19 --tail 50 | grep -i error

# Odoo shell (interactive)
docker exec -it gemini_odoo19 odoo shell -d mz-db

# Clear asset cache (after CSS/JS/SCSS changes)
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "DELETE FROM ir_attachment WHERE name LIKE '%assets%';"
docker restart gemini_odoo19
```

### Git Operations
```bash
cd /opt/gemini_odoo19
git add -A
git status
git commit -m "type(module): description"   # feat|fix|docs|refactor|test|chore
git push origin main
```

---

## 🏗️ Model Template

```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ModelName(models.Model):
    _name = 'ops.model.name'
    _description = 'Human Readable Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    ops_branch_id = fields.Many2one('ops.branch', string='Branch', tracking=True)
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    _sql_constraints = [
        ('unique_name_company', 'unique(name, company_id)', 'Name must be unique per company'),
    ]
```

---

## 🧪 Development Workflow

1. Pull latest: `git pull origin main`
2. Make code changes in `addons/ops_*/`
3. Update module: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE --stop-after-init`
4. Check logs: `docker logs gemini_odoo19 --tail 50 | grep -i error`
5. Test in browser: https://ops.mz-im.com
6. Commit: `git add -A && git commit -m "type(module): description"`
7. Push: `git push origin main`

---

## ❌ NEVER DO

| Forbidden Action | Reason |
|------------------|--------|
| ❌ Direct database manipulation (raw INSERT/UPDATE/DELETE) | Source code only |
| ❌ Use raw SQL for CRUD operations | Use Odoo ORM |
| ❌ Modify `Clone/` directory | External reference modules |
| ❌ Modify `config/` or `docker-compose.yml` | Infrastructure locked |
| ❌ Access anything outside `/opt/gemini_odoo19/` | Project boundary |
| ❌ Skip security rules on new models | Framework integrity |
| ❌ Use f-strings in SQL queries | SQL injection risk |
| ❌ Use `sudo()` without documentation | Privilege escalation |
| ❌ Break existing functionality | Preserve working code |

---

## 📊 Custom Commands Available

| Command | Description |
|---------|-------------|
| `/odoo-logs` | View Odoo container logs with filtering |
| `/odoo-restart` | Restart the Odoo Docker container |
| `/odoo-update` | Update one or more Odoo modules |
| `/odoo-shell` | Execute Python code in Odoo shell |
| `/module-status` | Check installation status of OPS modules |
| `/ops-architect` | Architecture planning assistance |
| `/explore-model` | Analyze an Odoo model's structure |
| `/ops-commit` | Standardized git commit |
| `/web-design-reviewer` | Visual inspection of website design |

## 🔌 Installed Skills

| Skill | Purpose |
|-------|---------|
| `financial-reporter` | Financial report generation |
| `frontend-design` | Frontend interface design |
| `ops-accounting` | Accounting module development |
| `ops_theme` | Theme development |
| `quality-documentation-manager` | Documentation quality |
| `skill-creator` | Create new skills |
| `ui-ux-pro-max` | UI/UX development |
| `web-performance-optimization` | Performance optimization |

---

## ⚠️ Critical Reminders

> **Database `mz-db` is the active database.** All changes via source code + module update only.

> **Stay within `/opt/gemini_odoo19/`.** Full access here, no access outside.

> **Security is non-negotiable.** IT Admin Blindness, Branch Isolation, SoD on every new model.

> **Theme philosophy:** "Odoo 19 owns the layout, OPS owns the colors." Never fight OWL framework.

> **Check existing code first.** Patterns are in `ops_matrix_core`.
