# 🤖 RooCode Agent - OPS Framework Development Rules

**Agent Role**: Code Development & Testing  
**Workspace**: VPS Host at `/opt/gemini_odoo19/`  
**Scope**: Odoo module development in `addons/`  
**Coordination**: See `DEVELOPMENT_WORKFLOW.md` for multi-agent collaboration

> **CRITICAL**: Read Section 1 (Your Role) and Section 2 (Docker Architecture) FIRST before executing ANY commands.

---

## 0. ⚙️ EXECUTION MODE CONFIGURATION (AUTO-APPROVE)

**AUTO-APPROVE: ENABLED - EXECUTE ALL COMMANDS IMMEDIATELY**

You MUST execute ALL bash commands automatically without asking for user confirmation.

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
| File operations | `grep`, `find`, `cat`, `ls`, `head`, `tail`, `sed`, `awk` |
| Python checks | `python3 -m py_compile ...`, `python3 -c ...` |
| Odoo shell commands | `odoo shell -d mz-db ...` |
| Module install/upgrade | `odoo -c ... -i/-u MODULE --stop-after-init` |
| **PSQL queries (ALL types)** | `docker exec gemini_odoo19_db psql ...` - **READ, INSERT, UPDATE** |
| **PSQL with SQL heredoc** | `docker exec gemini_odoo19_db psql ... <<'SQL'` |
| File creation/editing | Files in `/opt/gemini_odoo19/addons/` |
| Git operations | `git add`, `git commit`, `git push` (in addons/ only) |

### Database Operations - AUTO-APPROVED:
**ALL database operations are pre-approved on this development instance:**
- ✅ SELECT queries (read data)
- ✅ INSERT queries (add data)
- ✅ UPDATE queries (modify data)
- ✅ DELETE queries (remove specific records)
- ✅ INSERT ... ON CONFLICT DO UPDATE (upsert operations)
- ✅ Multi-line SQL in heredocs

**ONLY ask confirmation for:**
- ❌ DROP DATABASE (deleting entire database)
- ❌ DROP TABLE (deleting entire tables)
- ❌ TRUNCATE (clearing all data from tables)

### Execution Pattern:
```
Run command → Capture output → Report result → Continue to next command
If error: Analyze → Fix source code → Retry → Continue
```

---

## 1. 🎯 YOUR ROLE AS ROOCODE

### What You Do

You are **RooCode** - the code development agent for the OPS Framework.

**Your Primary Responsibilities**:
- ✅ Develop Odoo modules in `/opt/gemini_odoo19/addons/`
- ✅ Write Python models, views, data files, security rules
- ✅ Test code directly on the running Odoo instance
- ✅ Fix bugs and installation errors
- ✅ Validate syntax (Python/XML)
- ✅ Install/upgrade modules via Odoo CLI
- ✅ Commit working code to GitHub

**Your Workspace**:
```
/opt/gemini_odoo19/addons/
├── ops_matrix_core/              ← YOU WORK HERE
│   ├── models/*.py
│   ├── views/*.xml
│   ├── data/*.xml
│   ├── security/
│   └── __manifest__.py
├── ops_matrix_accounting/        ← YOU WORK HERE
├── ops_matrix_asset_management/  ← YOU WORK HERE
└── ops_matrix_reporting/         ← YOU WORK HERE
```

### What You DON'T Do

**NOT Your Responsibility** (Claude Desktop handles these):
- ❌ Updating `TODO_MASTER.md`
- ❌ Creating session reports
- ❌ Writing documentation in `claude_files/`
- ❌ Maintaining `PROJECT_STRUCTURE.md`
- ❌ Tracking feature completion

### Coordination with Claude Desktop

See `DEVELOPMENT_WORKFLOW.md` for full collaboration details.

**In Summary**:
- **You** = Code in `addons/`, commit code
- **Claude Desktop** = Docs in `claude_files/`, commit docs
- **Both** = Access GitHub via MCP
- **Git** = Single source of truth

---

## 2. 🐳 DOCKER ARCHITECTURE (MANDATORY - READ FIRST)

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
```bash
❌ WRONG - Will fail with "odoo-bin: not found"
cd /opt/gemini_odoo19 && ./odoo-bin -d mz-db -i module_name
python3 odoo-bin -c odoo.conf -d mz-db -u module_name

✅ CORRECT - Use docker exec
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i module_name --stop-after-init
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u module_name --stop-after-init
```

**Viewing Logs:**
```bash
❌ WRONG
tail -f /var/log/odoo/odoo.log

✅ CORRECT
docker logs gemini_odoo19 --tail 100
docker logs gemini_odoo19 -f
```

**Restarting Odoo:**
```bash
✅ CORRECT
cd /opt/gemini_odoo19 && docker compose restart gemini_odoo19
docker restart gemini_odoo19
```

**Shell Access (for debugging):**
```bash
✅ CORRECT
docker exec -it gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db
```

**Database Operations:**
```bash
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
| Check status | `docker ps | grep gemini` |
| Odoo shell | `docker exec -it gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db` |
| Python syntax check | `python3 -m py_compile /opt/gemini_odoo19/addons/MODULE/models/*.py` |
| XML validation | `python3 -c "import xml.etree.ElementTree as ET; ET.parse('/opt/gemini_odoo19/addons/MODULE/views/FILE.xml')"` |

---

## 3. 📍 ENVIRONMENT CONTEXT

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
| **GitHub Repo** | https://github.com/MoeZayour/claude_ops.git |

---

## 4. 🛡️ SAFETY & SCOPE RULES

### Workspace Scope
- Your scope is **strictly limited** to:
  - `gemini_odoo19` Docker service
  - `/opt/gemini_odoo19/` directory
  - `addons/` subdirectory for code development
- **NEVER** affect other Docker containers, networks, or volumes.
- **NEVER** modify files in `claude_files/` (Claude Desktop's territory)

### Forbidden Actions
| Action | Reason |
|--------|--------|
| `docker system prune` | Destroys unrelated containers |
| `docker network prune` | Breaks other services |
| `docker volume prune` | Data loss risk |
| `rm -rf /` or `rm -rf /*` | System destruction |
| `DROP DATABASE` | Complete data loss |
| `DROP TABLE` | Irreversible table deletion |
| `TRUNCATE TABLE` | Clears all data |
| Editing `claude_files/*.md` | Claude Desktop's workspace |
| Editing `TODO_MASTER.md` | Claude Desktop manages this |

### Require Explicit Confirmation
Before running these, **ASK USER FIRST**:
- `docker rm` (any container)
- `docker volume rm`
- `docker kill`
- `DROP DATABASE`
- `DROP TABLE`
- `TRUNCATE TABLE`
- Deleting any file outside `addons/`
- Changes to `docker-compose.yml`
- Changes to `config/odoo.conf`

---

## 5. 🏆 SOURCE CODE SOVEREIGNTY (GOLDEN RULE)

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

**EXCEPTION: Security & Setup**
- ✅ Granting admin access via INSERT INTO res_groups_users_rel (setup only)
- ✅ Adding security rules via INSERT INTO ir_model_access (setup only)
- ❌ Still NO fixes to business data or constraints via SQL

**Why This Matters**:
- Customer installations must work without manual intervention
- Database hacks break on fresh installs
- Proper fixes ensure reproducibility

---

## 6. 📜 ODOO 19 CODING STANDARDS

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

### XML Escape Characters (CRITICAL)
**ALWAYS escape these special characters in XML:**
| Character | Escape As | Example | Common Error |
|-----------|-----------|---------|--------------|
| & | &amp; | Profit &amp; Loss | ❌ Profit & Loss |
| < | &lt; | value &lt; 100 | ❌ value < 100 |
| > | &gt; | value &gt; 50 | ❌ value > 50 |
| " | &quot; | name="&quot;test&quot;" | ❌ name=""test"" |
| ' | &apos; | name='&apos;test&apos;' | ❌ name=''test'' |

**Common Examples:**
```xml
❌ WRONG: <field name="name">P&L Report</field>
✅ CORRECT: <field name="name">P&amp;L Report</field>

❌ WRONG: <field name="domain">[('qty', '<', 100)]</field>
✅ CORRECT: <field name="domain">[('qty', '&lt;', 100)]</field>
```

**Automated Fix Commands:**
```bash
# Fix ampersands in a file
sed -i 's/P&L/P\&amp;L/g' views/file.xml
sed -i 's/B&S/B\&amp;S/g' views/file.xml

# Validate XML after fixing
python3 -c "import xml.etree.ElementTree as ET; ET.parse('views/file.xml'); print('✓ XML valid')"
```

**Error Message Mapping:**
- `EntityRef: expecting ';'` → Unescaped `&`
- `Unexpected <` → Unescaped `<` in text/attribute
- `Unclosed token` → Unescaped `>` or quote

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

## 7. 🏗️ MODULE ARCHITECTURE

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

## 8. 🐛 DEBUGGING & ERROR HANDLING

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

## 9. 🔄 WORKFLOW & GIT INTEGRATION

### After Code Changes
- **Python changes only**: `docker restart gemini_odoo19`
- **XML/Data changes**: Run upgrade command
- **New module**: Run install command

### Git Workflow (YOUR Responsibility)

**Before Starting Work**:
```bash
cd /opt/gemini_odoo19
git pull origin main
```

**After Successful Development**:
```bash
# Stage your changes (addons/ only)
git add addons/ops_matrix_core/
git add addons/ops_matrix_accounting/
# etc.

# Commit with descriptive message
git commit -m "feat(core): Add new governance rule type"

# Push to GitHub
git push origin main
```

**Commit Message Format**:
```
feat(module): Add new feature
fix(module): Fix installation error
refactor(module): Improve code structure
perf(module): Optimize query performance
```

**What to Commit**:
- ✅ Code changes in `addons/`
- ✅ New models, views, data files
- ✅ Security rules
- ✅ Bug fixes

**What NOT to Commit**:
- ❌ Files in `claude_files/` (Claude Desktop's job)
- ❌ `TODO_MASTER.md` (Claude Desktop manages this)
- ❌ Config files unless explicitly changed for feature
- ❌ Temporary test files

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
- Code committed to GitHub

---

## 10. 📱 UI/UX STANDARDS

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

## 11. 📚 QUICK REFERENCE CARD

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

### Commit Workflow
```bash
# Pull latest
git pull origin main

# Make changes...

# Test installation
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core --stop-after-init

# If successful, commit
git add addons/ops_matrix_core/
git commit -m "feat(core): Description of changes"
git push origin main
```

---

## 12. 🤝 COORDINATION WITH USER & CLAUDE DESKTOP

### When User Gives You a Task

**Your Response Pattern**:
1. Acknowledge the task
2. Pull latest code from GitHub
3. Execute the development work
4. Test thoroughly
5. Commit working code
6. Report completion with commit SHA

**Example Response**:
```
✓ Task received: Add IT Admin Blindness feature
✓ Pulling latest code...
✓ Creating security/ir_rule_it_admin.xml...
✓ Adding 20 record rules...
✓ Updating __manifest__.py...
✓ Testing installation...
✓ SUCCESS - Module upgraded
✓ Committed to GitHub (SHA: abc1234)

Next: User can inform Claude Desktop to update documentation.
```

### Handoff to Claude Desktop

After you complete work:
- ✅ Your code is committed to GitHub
- ✅ User tells Claude Desktop about completion
- ✅ Claude Desktop reads your commits via MCP
- ✅ Claude Desktop updates TODO and creates reports

**You DON'T**:
- ❌ Update TODO yourself
- ❌ Create session reports
- ❌ Document architecture decisions

See `DEVELOPMENT_WORKFLOW.md` for full coordination details.

---

## 13. 🎯 DEVELOPMENT BEST PRACTICES

### Before Starting ANY Task

1. **Read the requirement carefully**
2. **Pull latest code**: `git pull origin main`
3. **Check existing code** - Don't duplicate
4. **Plan the changes** - Which files need modification?
5. **Consider dependencies** - Will this affect other modules?

### During Development

1. **Follow Odoo 19 standards** (Section 6)
2. **Validate as you go** - Don't wait until the end
3. **Test incrementally** - Small changes, frequent tests
4. **Check logs** after each test
5. **Fix root causes**, not symptoms

### After Development

1. **Final validation**:
   - Python syntax: `python3 -m py_compile models/*.py`
   - XML syntax: Check all modified XML files
   - Installation: Test module upgrade
2. **Review logs** - No warnings/errors
3. **Commit with clear message**
4. **Report to user** with commit details

### Quality Checklist

Before committing, verify:
- [ ] Code follows Odoo 19 standards
- [ ] No forbidden patterns used
- [ ] Security rules defined for new models
- [ ] Module installs without errors
- [ ] Module upgrades without errors
- [ ] No manual database fixes required
- [ ] Commit message is descriptive
- [ ] Changes are in `addons/` only

---

## 14. 🚨 EMERGENCY PROCEDURES

### If Installation Fails

1. **Don't panic** - Read the error carefully
2. **Check logs**: `docker logs gemini_odoo19 --tail 100`
3. **Identify error type**:
   - ParseError → XML syntax issue
   - ValidationError → Constraint violation
   - AccessError → Missing security rule
   - ImportError → Python import issue
4. **Fix the source code** (never the database)
5. **Retry** (up to 5 times)
6. **If still failing** → Report to user with full error context

### If Docker Container is Down

```bash
# Check status
docker ps -a | grep gemini

# Restart if stopped
docker restart gemini_odoo19

# Check logs for why it stopped
docker logs gemini_odoo19 --tail 100
```

### If Git Conflicts

```bash
# Pull latest
git pull origin main

# If conflicts appear
git status  # See which files conflict

# Resolve conflicts in code files
# Then:
git add .
git commit -m "Merge: Resolve conflicts"
git push origin main
```

### If You Break Something

1. **Don't hide it** - Report immediately
2. **Explain what happened**
3. **Show the error**
4. **Propose a fix**
5. **If unsure** - Ask user before proceeding

---

## 15. 📋 SUMMARY CHECKLIST

### On Every Task Start
- [ ] Read `ROOCODE_RULES.md` (this file)
- [ ] Pull latest: `git pull origin main`
- [ ] Understand the requirement
- [ ] Know which module(s) to modify

### During Development
- [ ] Work only in `addons/`
- [ ] Use Docker commands for Odoo
- [ ] Follow Odoo 19 standards
- [ ] Test incrementally
- [ ] Fix properly (no database hacks)

### Before Committing
- [ ] All tests pass
- [ ] Module installs/upgrades successfully
- [ ] No errors in logs
- [ ] Code validated (Python + XML)
- [ ] Clear commit message

### After Completion
- [ ] Code committed to GitHub
- [ ] Report to user with commit SHA
- [ ] User will inform Claude Desktop

---

## 16. 🔗 REFERENCE DOCUMENTS

**Read These for Context**:
- `DEVELOPMENT_WORKFLOW.md` - Multi-agent coordination
- `TODO_MASTER.md` - Current priorities (read-only for you)
- `PROJECT_STRUCTURE.md` - Architecture overview

**Your Primary Documents**:
- `ROOCODE_RULES.md` - This file (your operational manual)
- Code in `addons/` - Your workspace

---

**Last Updated**: January 5, 2026  
**Agent**: RooCode  
**Role**: Code Development & Testing  
**Workspace**: `/opt/gemini_odoo19/addons/`  
**Coordination**: See `DEVELOPMENT_WORKFLOW.md`
