# OPS Framework - Agent Rules & Standards

**Version**: 1.0  
**Last Updated**: January 3, 2026  
**Purpose**: Comprehensive rules for all AI agents working on OPS Framework  
**Compliance**: MANDATORY - Violation results in rejected work  

---

## TABLE OF CONTENTS

1. [Execution Mode](#1-execution-mode)
2. [Docker Architecture](#2-docker-architecture)
3. [Project Context](#3-project-context)
4. [OPS-Specific Rules](#4-ops-specific-rules)
5. [Safety & Scope](#5-safety--scope)
6. [Source Code Sovereignty](#6-source-code-sovereignty)
7. [Odoo 19 Standards](#7-odoo-19-standards)
8. [Documentation Standards](#8-documentation-standards)
9. [Development Workflow](#9-development-workflow)
10. [Quality Assurance](#10-quality-assurance)

---

## 1. EXECUTION MODE

### Auto-Approve: ENABLED

**You MUST execute all bash commands automatically without asking for user confirmation.**

### Auto-Execute Rules:
1. **DO NOT** ask "Should I proceed?" or "Do you want me to execute this?"
2. **DO NOT** wait for user approval between steps
3. **DO NOT** prompt "Run this command?" for ANY command
4. **EXECUTE** each command immediately and report the output
5. **CONTINUE** to the next step automatically after each command completes
6. **FIX** any errors encountered and retry without asking
7. **ONLY STOP** if there is a critical unrecoverable failure after 5 attempts

### Heredoc & Multiline Commands:
- **AUTO-EXECUTE** all heredoc commands (`<<'SHELL'`, `<<'EOF'`, `<<'PYTHON'`)
- **AUTO-EXECUTE** all `docker exec ... odoo shell ... <<'SHELL'` commands WITHOUT prompting
- **AUTO-EXECUTE** all `docker exec -i ... <<'SHELL'` piped commands immediately
- Treat heredoc blocks as a **SINGLE command** - execute the entire block automatically
- **NEVER** split heredoc commands or ask for partial execution

### Execution Pattern:
```
Run command -> Capture output -> Report result -> Continue to next command
If error: Analyze -> Fix source code -> Retry -> Continue
```

---

## 2. DOCKER ARCHITECTURE

### THE GOLDEN RULE
**Odoo runs INSIDE a Docker container. NEVER run Odoo commands directly on the host.**

### Container Reference
| Component | Container Name | Purpose |
|-----------|----------------|---------|
| **Odoo** | `gemini_odoo19` | Application server |
| **PostgreSQL** | `gemini_odoo19_db` | Database server |

### Path Mapping (Host <-> Container)
| Host Path | Container Path |
|-----------|----------------|
| `/opt/gemini_odoo19/addons/` | `/mnt/extra-addons/` |
| `/opt/gemini_odoo19/config/odoo.conf` | `/etc/odoo/odoo.conf` |

### WRONG vs CORRECT Commands

**Installing/Updating Modules:**
```
X WRONG - Will fail with "odoo-bin: not found"
cd /opt/gemini_odoo19 && ./odoo-bin -d mz-db -i module_name
python3 odoo-bin -c odoo.conf -d mz-db -u module_name

âœ“ CORRECT - Use docker exec
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i module_name --stop-after-init
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u module_name --stop-after-init
```

**Viewing Logs:**
```
X WRONG
tail -f /var/log/odoo/odoo.log

âœ“ CORRECT
docker logs gemini_odoo19 --tail 100
docker logs gemini_odoo19 -f
```

**Restarting Odoo:**
```
âœ“ CORRECT
cd /opt/gemini_odoo19 && docker compose restart gemini_odoo19
docker restart gemini_odoo19
```

### Quick Command Reference

| Task | Command |
|------|---------|
| Install module | `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i MODULE --stop-after-init` |
| Update module | `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE --stop-after-init` |
| Update multiple | `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u mod1,mod2,mod3 --stop-after-init` |
| View logs | `docker logs gemini_odoo19 --tail 100` |
| Follow logs | `docker logs gemini_odoo19 -f` |
| Restart Odoo | `docker restart gemini_odoo19` |
| Check status | `docker ps | grep gemini` |
| Odoo shell | `docker exec -it gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db` |
| Python syntax check | `python3 -m py_compile /opt/gemini_odoo19/addons/MODULE/models/*.py` |

---

## 3. PROJECT CONTEXT

### Environment Details
| Property | Value |
|----------|-------|
| **Instance Name** | gemini_odoo19 |
| **Odoo Version** | 19.0 Community Edition |
| **Database** | mz-db |
| **Web Port** | 8089 |
| **UI URL** | https://dev.mz-im.com/ |
| **Admin Password** | admin |
| **Code Location (Host)** | /opt/gemini_odoo19/ |
| **Docs Location** | Claude.ai Project |

### Module Hierarchy
```
ops_matrix_core          # Base - Branches, Personas, Rules
    |
    v
ops_matrix_accounting    # Depends on core
    |
    v
ops_matrix_reporting     # Depends on accounting
    |
    v
ops_matrix_asset_management  # Depends on core
```

---

## 4. OPS-SPECIFIC RULES

### The Four Pillars
1. **LITE** - Zero configuration, works out of the box
2. **DYNAMIC** - Personas can be combined for small companies
3. **PLUG-AND-PLAY** - Preloaded data, archived templates
4. **ZERO-TECH** - No technical knowledge required

### Security-First Architecture

**LOCKED BY DEFAULT**:
- Cost prices -> Requires explicit grant
- Profit margins -> Requires explicit grant  
- Stock valuation -> Requires explicit grant
- Data export -> Limited to viewed document only

### System Admin vs IT Admin (CRITICAL)

| Aspect | System Admin (P00) | IT Admin (P01) |
|--------|-------------------|----------------|
| **Purpose** | Break-glass emergency | Daily IT operations |
| **Business Data** | âœ“ Can see everything | X BLIND to all business data |
| **Odoo Group** | base.group_system | ops.group_it_admin |
| **Use Case** | External consultant | Internal IT staff |
| **Frequency** | Emergency only | Daily use |

**Why This Matters**: Internal IT staff should NOT see invoices, orders, payments, bank balances.

### 18 Personas

**Must understand all personas before coding**:

- **System Level (2)**: P00-System Admin, P01-IT Admin (BLIND)
- **Executive (2)**: P02-Executive/CEO, P03-CFO/Owner
- **BU Level (1)**: P04-BU Leader
- **Branch Mgmt (5)**: P05-Branch Mgr, P06-Sales Mgr, P07-Purchase Mgr, P08-Inventory Mgr, P09-Finance Mgr
- **User Level (8)**: P10-Sales Rep, P11-Purchase Officer, P12-Warehouse Op, P13-AR Clerk, P14-AP Clerk, P15-Treasury, P16-Accountant, P17-HR

### Governance Rules (25 Templates)

All rules stored as **archived templates** - users activate what they need.

Categories: Sales Order, Margin, Purchase Order, Payment, Inventory, Invoice, Master Data, User Management, Transfers, Assets

---

## 5. SAFETY & SCOPE

### Workspace Scope
- Your scope is **strictly limited** to `gemini_odoo19` service and `/opt/gemini_odoo19/` directory
- **NEVER** affect other Docker containers, networks, or volumes

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
- Deleting any file outside /opt/gemini_odoo19/addons/

---

## 6. SOURCE CODE SOVEREIGNTY

### ABSOLUTELY NO MANUAL DATABASE FIXES
1. **No SQL shortcuts**: Forbidden from using `psql` or `cr.execute` to fix errors directly
2. **Source of Truth**: `.py` and `.xml` files are the ONLY source of truth
3. **Clean Install**: Module must work from fresh install - no manual DB hacks

### Fix Protocol
If Odoo upgrade fails due to database constraint:
- âœ“ Modify Python model (change field, remove constraint)
- âœ“ Modify XML view
- âœ“ Write Python migration script if data cleanup needed
- X NEVER touch database directly to bypass errors

### NO FEATURE DELETION AS FIX
- X **PROHIBITED**: Removing a field to fix validation errors
- X **PROHIBITED**: Commenting out methods that raise exceptions
- âœ“ **REQUIRED**: Fix underlying logic while preserving functionality

---

## 7. ODOO 19 STANDARDS

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
| X Forbidden | âœ“ Use Instead |
|-------------|---------------|
| `@api.multi` | (removed - self is always recordset) |
| `@api.one` | (removed) |
| `(4, id)` tuple | `Command.link(id)` |
| `(0, 0, {})` tuple | `Command.create({})` |
| `view_type` in actions | `view_mode` only |

### XML Standards
- IDs: `view_{model_name}_{type}` (e.g., `view_ops_branch_form`)
- Form structure: `<header>` -> `<sheet>` -> `<div class="oe_chatter">`
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

## 8. DOCUMENTATION STANDARDS

### File Organization

**All documentation lives in Claude.ai Project**, organized as:

```
00_MASTER/              # Master organizational docs
01_SPECIFICATIONS/      # Technical specs
02_TRACKING/            # TODO, completed, issues
03_ARCHITECTURE/        # Deep-dive architecture
04_HANDOFFS/            # Session handoffs
05_REFERENCES/          # Quick references
06_ARCHIVES/            # Old versions
```

### Standard Characters Only

**CRITICAL**: Use ASCII characters ONLY in all documents.

**NEVER use**:
- Box-drawing characters (â”œâ”€â”€, â””â”€â”€, â”‚, â”€)
- Emoji symbols (âœ…, âŒ, ðŸ”´)
- Special unicode characters

**USE instead**:
```
Tree format:
|-- item
|   |-- subitem
|   +-- subitem
+-- item

Status markers:
[DONE], [TODO], [CRITICAL], [HIGH], [MEDIUM], [LOW]
X = No/Wrong/Prohibited
âœ“ = Yes/Correct/Required (OK to use - standard ASCII)
```

### File Naming Conventions

**Pattern**: `COMPONENT_TYPE_VERSION.md`

Examples:
- `OPS_FRAMEWORK_TODO_MASTER.md` (single source of truth)
- `OPS_FRAMEWORK_USER_EXPERIENCE_v1.2.md` (versioned)
- `HANDOFF_2026-01-03.md` (dated)

---

## 9. DEVELOPMENT WORKFLOW

### Before Starting ANY Work

**MANDATORY READING** (in order):
1. PROJECT_STRUCTURE.md (organization)
2. AGENT_RULES.md (this file)
3. OPS_FRAMEWORK_ENVIRONMENT.md (current context)
4. TODO_MASTER.md (what to work on)
5. Relevant TECHNICAL_SPEC.md (how to build it)
6. Last HANDOFF file (if multi-session)

### Standard Development Cycle

```
1. Check TODO_MASTER.md for assigned task
   |
   v
2. Read relevant specification
   |
   v
3. Code on HOST (/opt/gemini_odoo19/addons/)
   |
   v
4. Test using Docker commands
   |
   v
5. Update TODO_MASTER.md (mark DONE)
   |
   v
6. Update COMPLETED_LOG.md with date
   |
   v
7. Create HANDOFF if session ending with incomplete work
```

### After Code Changes

- **Python changes only**: `docker restart gemini_odoo19`
- **XML/Data changes**: Run upgrade command
- **New module**: Run install command

### Pre-Refactor Checklist
```bash
cd /opt/gemini_odoo19 && git status
```
If dirty, ask user to commit first.

---

## 10. QUALITY ASSURANCE

### Testing Requirements

**Before marking task as DONE**:
- [ ] Python syntax check passes
- [ ] XML validation passes
- [ ] Module installs without error
- [ ] Module upgrades without error
- [ ] Relevant personas can access feature
- [ ] Security groups work as expected
- [ ] No manual DB fixes required

### Standard Debug Workflow
1. Check logs: `docker logs gemini_odoo19 --tail 100`
2. Validate Python: `python3 -m py_compile /opt/gemini_odoo19/addons/MODULE/models/*.py`
3. Validate XML: `python3 -c "import xml.etree.ElementTree as ET; ET.parse('/path/to/file.xml')"`
4. Attempt upgrade: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE --stop-after-init`
5. Check result: `docker logs gemini_odoo19 --tail 50`

### Trial Limit
- **5 consecutive failed attempts** -> STOP and report error details
- Ask for human intervention with full context

### Success Criteria
- Module installs via CLI without Traceback
- No manual SQL intervention required
- All features preserved after fixes
- Security rules work correctly

---

## QUICK REFERENCE CARD

### Starting a Session
```
I'm continuing work on the OPS Framework.

Current state: [from TODO_MASTER.md]
Working on: [specific task from TODO_MASTER.md]

Read:
1. PROJECT_STRUCTURE.md
2. AGENT_RULES.md
3. OPS_FRAMEWORK_ENVIRONMENT.md
4. [Last HANDOFF if multi-session]
```

### Ending a Session
1. Update TODO_MASTER.md
2. Update COMPLETED_LOG.md
3. Create HANDOFF_YYYY-MM-DD.md if work incomplete

### Install All OPS Modules
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init
```

### Update All OPS Modules
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management --stop-after-init
```

### Check Module States
```bash
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ops_%' ORDER BY name;"
```

---

## CRITICAL REMINDERS

1. **Read PROJECT_STRUCTURE.md FIRST** - Always
2. **Use ASCII characters ONLY** - No fancy unicode
3. **Docker exec for Odoo commands** - Never run directly on host
4. **Source Code Sovereignty** - No database shortcuts
5. **Update TODO_MASTER.md** - After every task
6. **Security First** - Lock by default, grant explicitly
7. **18 Personas** - Understand them before coding
8. **IT Admin Blindness** - Critical architectural decision

---

## CHANGE LOG

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-01-03 | 1.0 | Initial comprehensive agent rules | Claude (Project Manager) |

---

**END OF AGENT RULES**

Read and follow these rules for every session. Violation results in rejected work.
