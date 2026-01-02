# 🚀 GEMINI ODOO 19 - AGENT MASTER RULES

> **CRITICAL**: Read Section 1 (Docker Architecture) FIRST before executing ANY commands.

---

## 0. ⚙️ EXECUTION MODE CONFIGURATION (AUTO-APPROVE)

**AUTO-APPROVE: ENABLED**

You MUST execute all bash commands automatically without asking for user confirmation.

### Auto-Execute Rules:
1. **DO NOT** ask "Should I proceed?" or "Do you want me to execute this?"
2. **DO NOT** wait for user approval between steps
3. **DO NOT** prompt "Run this command?" for ANY command
4. **EXECUTE** each command immediately and report the output
5. **CONTINUE** to the next step automatically after each command completes
6. **FIX** any errors encountered and retry without asking
7. **ONLY STOP** if there is a critical unrecoverable failure after 5 attempts

### Heredoc & Multiline Commands (CRITICAL):
- **AUTO-EXECUTE** all heredoc commands (`<<'SHELL'`, `<<'EOF'`, `<<'PYTHON'`, `<<'SQL'`)
- **AUTO-EXECUTE** all `docker exec ... odoo shell ... <<'SHELL'` commands WITHOUT prompting
- **AUTO-EXECUTE** all `docker exec -i ... <<'SHELL'` piped commands immediately
- Treat heredoc blocks as a **SINGLE command** - execute the entire block automatically
- **NEVER** split heredoc commands or ask for partial execution

### Allowed Auto-Execute Commands (No Confirmation Needed):
| Command Type | Examples |
|--------------|----------|
| Docker exec | `docker exec gemini_odoo19 ...` |
| Docker exec with heredoc | `docker exec -i gemini_odoo19 odoo shell ... <<'SHELL'` |
| Docker logs | `docker logs gemini_odoo19 ...` |
| Docker restart | `docker restart gemini_odoo19` |
| File operations | `grep`, `find`, `cat`, `ls`, `head`, `tail` |
| Python checks | `python3 -m py_compile ...` |
| Odoo shell commands | `odoo shell -d mz-db ...` |
| Module install/upgrade | `odoo -c ... -i/-u MODULE --stop-after-init` |
| PSQL queries (read-only) | `docker exec gemini_odoo19_db psql ...` |
| File creation/editing | Files in `/opt/gemini_odoo19/` |

### Execution Pattern:
```
Run command → Capture output → Report result → Continue to next command
If error: Analyze → Fix source code → Retry → Continue
```

---

## 1. 🐳 DOCKER ARCHITECTURE (MANDATORY - READ FIRST)

### ⚠️ THE GOLDEN RULE
**Odoo runs INSIDE a Docker container. NEVER run Odoo commands directly on the host.**

### Container Reference
| Component | Container Name | Purpose |
|-----------|----------------|---------|
| **Odoo** | `gemini_odoo19` | Application server |
| **PostgreSQL** | `gemini_odoo19_db` | Database server |

### Path Mapping (Host ↔ Container)
| Host Path | Container Path |
|-----------|----------------|
| `/opt/gemini_odoo19/addons/` | `/mnt/extra-addons/` |
| `/opt/gemini_odoo19/config/odoo.conf` | `/etc/odoo/odoo.conf` |

### ❌ WRONG vs ✅ CORRECT Commands

**Installing/Updating Modules:**
```
❌ WRONG - Will fail with "odoo-bin: not found"
cd /opt/gemini_odoo19 && ./odoo-bin -d mz-db -i module_name
python3 odoo-bin -c odoo.conf -d mz-db -u module_name

✅ CORRECT - Use docker exec
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i module_name --stop-after-init
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u module_name --stop-after-init
```

**Viewing Logs:**
```
❌ WRONG
tail -f /var/log/odoo/odoo.log

✅ CORRECT
docker logs gemini_odoo19 --tail 100
docker logs gemini_odoo19 -f
```

**Restarting Odoo:**
```
✅ CORRECT
cd /opt/gemini_odoo19 && docker compose restart gemini_odoo19
docker restart gemini_odoo19
```

**Shell Access (for debugging):**
```
✅ CORRECT
docker exec -it gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db
```

**Database Operations:**
```
✅ CORRECT - Use gemini_odoo19_db container
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ops_%';"
```

### 📋 Quick Command Reference

| Task | Command |
|------|---------|
| Install module | `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i MODULE --stop-after-init` |
| Update module | `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE --stop-after-init` |
| Update multiple | `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u mod1,mod2,mod3 --stop-after-init` |
| View logs | `docker logs gemini_odoo19 --tail 100` |
| Follow logs | `docker logs gemini_odoo19 -f` |
| Restart Odoo | `docker restart gemini_odoo19` |
| Check status | `docker ps \| grep gemini` |
| Odoo shell | `docker exec -it gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db` |
| Python syntax check | `python3 -m py_compile /opt/gemini_odoo19/addons/MODULE/models/*.py` |
| XML validation | `python3 -c "import xml.etree.ElementTree as ET; ET.parse('/opt/gemini_odoo19/addons/MODULE/views/FILE.xml')"` |

---

## 2. 📍 ENVIRONMENT CONTEXT

| Property | Value |
|----------|-------|
| **Instance Name** | gemini_odoo19 |
| **Odoo Version** | 19.0 Community Edition |
| **Database** | mz-db |
| **Web Port** | 8089 |
| **Longpoll Port** | 8082 |
| **UI URL** | https://dev.mz-im.com/ |
| **Admin Password** | admin |
| **Project Root** | /opt/gemini_odoo19/ |
| **Addons Path (Host)** | /opt/gemini_odoo19/addons/ |

---

## 3. 🛡️ SAFETY & SCOPE RULES

### Workspace Scope
- Your scope is **strictly limited** to the `gemini_odoo19` service and `/opt/gemini_odoo19/` directory.
- **NEVER** affect other Docker containers, networks, or volumes.

### Forbidden Actions
| Action | Reason |
|--------|--------|
| `docker system prune` | Destroys unrelated containers |
| `docker network prune` | Breaks other services |
| `docker volume prune` | Data loss risk |
| `rm -rf /` or `rm -rf /*` | System destruction |
| Direct `psql` data fixes | Violates Source Code Sovereignty |

### Require Explicit Confirmation
Before running these, **ASK USER FIRST**:
- `docker rm` (any container)
- `docker volume rm`
- `docker kill`
- Deleting any file

---

## 4. 🏆 SOURCE CODE SOVEREIGNTY (GOLDEN RULE)

### ABSOLUTELY NO MANUAL DATABASE FIXES
1. **No SQL shortcuts**: Forbidden from using `psql` or `cr.execute` to fix errors directly.
2. **Source of Truth**: `.py` and `.xml` files are the ONLY source of truth.
3. **Clean Install**: Module must work from fresh install - no manual DB hacks.

### Fix Protocol
If Odoo upgrade fails due to database constraint:
- ✅ Modify Python model (change field, remove constraint)
- ✅ Modify XML view
- ✅ Write Python migration script if data cleanup needed
- ❌ NEVER touch database directly to bypass errors

---

## 5. 📜 ODOO 19 CODING STANDARDS

### Python Standards
```python
# Use fields.Command (NOT tuple syntax):
from odoo import Command
line_ids = [Command.create({'name': 'New'})]
tag_ids = [Command.link(tag_id)]
tag_ids = [Command.set([id1, id2])]

# Type hints required:
def action_confirm(self) -> bool:
    self.ensure_one()
    return True

# Use @api.model_create_multi:
@api.model_create_multi
def create(self, vals_list: List[Dict[str, Any]]) -> models.Model:
    return super().create(vals_list)
```

### Forbidden Patterns
| ❌ Forbidden | ✅ Use Instead |
|-------------|---------------|
| `@api.multi` | (removed - self is always recordset) |
| `@api.one` | (removed) |
| `(4, id)` tuple | `Command.link(id)` |
| `(0, 0, {})` tuple | `Command.create({})` |
| `view_type` in actions | `view_mode` only |

### XML Standards
- IDs: `view_{model_name}_{type}` (e.g., `view_ops_branch_form`)
- Form structure: `<header>` → `<sheet>` → `<div class="oe_chatter">`
- Always include `sample="1"` in tree views for empty state

### Manifest Requirements
```python
{
    'name': 'Module Name',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',  # MANDATORY
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',  # Load order: Security first
        'data/...',                       # Then data
        'views/...',                      # Then views
    ],
}
```

### Security
- Every model **MUST** have `ir.model.access.csv` entry
- Include admin bypass (`base.group_system`) in record rules

---

## 6. 🏗️ MODULE ARCHITECTURE

### Hierarchy (Load Order)
```
ops_matrix_core          # Base - Branches, Personas, Rules
    ↓
ops_matrix_accounting    # Depends on core
    ↓
ops_matrix_reporting     # Depends on accounting
    ↓
ops_matrix_asset_management  # Depends on core
```

### Module Purposes
| Module | Dependencies | Purpose |
|--------|--------------|---------|
| `ops_matrix_core` | base, mail | Branches, Business Units, Personas, Governance Rules |
| `ops_matrix_accounting` | account, ops_matrix_core | Budgets, PDC, Financial Controls |
| `ops_matrix_reporting` | ops_matrix_accounting | Reports, Analytics |
| `ops_matrix_asset_management` | ops_matrix_core | Asset tracking |

---

## 7. 🐛 DEBUGGING & ERROR HANDLING

### NO FEATURE DELETION AS FIX
- ❌ **PROHIBITED**: Removing a field to fix validation errors
- ❌ **PROHIBITED**: Commenting out methods that raise exceptions
- ✅ **REQUIRED**: Fix underlying logic while preserving functionality

### Root Cause Mandate
For every bug:
1. Identify the actual root cause
2. Propose fix that maintains feature integrity
3. If removal genuinely needed, document WHY with evidence

### Trial Limit
- **5 consecutive failed attempts** → STOP and report error details
- Ask for human intervention with full context

### Standard Debug Workflow
1. Check current logs: `docker logs gemini_odoo19 --tail 100`
2. Validate Python syntax: `python3 -m py_compile /opt/gemini_odoo19/addons/MODULE/models/*.py`
3. Validate XML files
4. Attempt upgrade: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE --stop-after-init`
5. Check result: `docker logs gemini_odoo19 --tail 50`

---

## 8. 🔄 WORKFLOW & TOOLING

### After Code Changes
- **Python changes only**: `docker restart gemini_odoo19`
- **XML/Data changes**: Run upgrade command
- **New module**: Run install command

### Pre-Refactor Checklist
Check git status before major changes:
```bash
cd /opt/gemini_odoo19 && git status
```
If dirty, ask user to commit first

### Success Criteria
- Module installs via CLI without Traceback
- No manual SQL intervention required
- All features preserved after fixes

---

## 9. 📱 UI/UX STANDARDS

### Form View Template
```xml
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm" class="oe_highlight"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <div name="button_box" class="oe_button_box"/>
        <group>
            <field name="name"/>
        </group>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

### Mobile Responsiveness
- Approve/Reject buttons visible in header (no horizontal scroll)
- Use `class="oe_highlight"` for primary actions
- Test badge/ribbon widgets for SLA status

---

## 10. 📚 QUICK REFERENCE CARD

### Install Modules
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init
```

### Update All OPS Modules
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management --stop-after-init
```

### Full Restart Cycle
```bash
cd /opt/gemini_odoo19 && docker compose restart && docker logs gemini_odoo19 -f
```

### Check Module States
```bash
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ops_%' ORDER BY name;"
```
