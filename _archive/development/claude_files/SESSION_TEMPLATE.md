# Session Start Template

**Use this template at the beginning of EVERY development session.**

---

## SESSION OPENER (Copy & Paste This)

```
I'm continuing work on the OPS Framework.

Session Date: [YYYY-MM-DD]
Session Goal: [Brief description of what you're working on]

MANDATORY READING (in order):
1. PROJECT_STRUCTURE.md - How project is organized
2. AGENT_RULES.md - Rules I must follow
3. OPS_FRAMEWORK_ENVIRONMENT.md - Current project context
4. TODO_MASTER.md - Tasks and priorities
5. [If multi-session work] HANDOFF_[last-date].md

Current State (from TODO_MASTER.md):
- Phase: [Phase 1, 2, 3, etc.]
- Version: [19.0.x.x]
- Last Completed: [Brief summary]

Working On (from TODO_MASTER.md):
- Priority: [CRITICAL | HIGH | MEDIUM | LOW]
- Task: [Specific task name]
- Files: [List of files to modify]
- Estimated Effort: [X sessions]

Code Location: /opt/gemini_odoo19/addons/
Documentation: Claude.ai Project

Ready to proceed.
```

---

## PRE-WORK CHECKLIST

Before writing any code, verify:

- [ ] Read PROJECT_STRUCTURE.md
- [ ] Read AGENT_RULES.md  
- [ ] Read OPS_FRAMEWORK_ENVIRONMENT.md
- [ ] Checked TODO_MASTER.md for current priority
- [ ] Read relevant TECHNICAL_SPEC.md for the feature
- [ ] Read last HANDOFF file (if multi-session)
- [ ] Understand which personas are affected
- [ ] Know which security groups need updates

---

## DURING WORK CHECKLIST

While coding:

- [ ] Use ASCII characters only in documentation
- [ ] Use docker exec for all Odoo commands (never run directly on host)
- [ ] Follow Odoo 19 standards (fields.Command, type hints, etc.)
- [ ] No manual database fixes (Source Code Sovereignty)
- [ ] Test with multiple personas
- [ ] Update comments in code
- [ ] Keep security-first mindset (lock by default)

---

## SESSION CLOSER (Multi-Session Work Only)

If work is incomplete at session end, create handoff:

```
File: HANDOFF_YYYY-MM-DD.md

## Session Summary

**Date**: [YYYY-MM-DD]
**Working On**: [Task name from TODO_MASTER.md]
**Status**: IN PROGRESS

### Completed This Session
1. [Item 1]
2. [Item 2]
3. [Item 3]

### Still In Progress
- [What's not done yet]

### Files Modified
- [File 1] - [What was changed]
- [File 2] - [What was changed]

### Next Steps
1. [Immediate next action]
2. [Following action]
3. [After that]

### Commands to Resume Work
```bash
# Navigate to project
cd /opt/gemini_odoo19/

# Check current status
docker logs gemini_odoo19 --tail 50

# Continue testing module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE_NAME --stop-after-init
```

### Known Issues This Session
- [Issue 1] - [Solution attempted or needed]
- [Issue 2] - [Solution attempted or needed]

### Context for Next Session
[Any important context that the next agent needs to know]
```

---

## POST-WORK CHECKLIST

After completing ANY work:

- [ ] Update TODO_MASTER.md (mark as [DONE] or [IN PROGRESS])
- [ ] Add completed items to COMPLETED_LOG.md with date
- [ ] Log any new issues in ISSUES_LOG.md
- [ ] Test installation: `docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE --stop-after-init`
- [ ] Check logs: `docker logs gemini_odoo19 --tail 50`
- [ ] If session incomplete: Create HANDOFF_YYYY-MM-DD.md
- [ ] If session complete: Mark task [DONE] in TODO_MASTER.md

---

## QUICK REFERENCE COMMANDS

### Check What's Running
```bash
docker ps | grep gemini
```

### View Recent Logs
```bash
docker logs gemini_odoo19 --tail 100
```

### Install Module
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i MODULE_NAME --stop-after-init
```

### Update Module
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u MODULE_NAME --stop-after-init
```

### Update All OPS Modules
```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management --stop-after-init
```

### Restart Odoo
```bash
docker restart gemini_odoo19
```

### Check Module Status
```bash
docker exec gemini_odoo19_db psql -U odoo -d mz-db -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'ops_%' ORDER BY name;"
```

### Python Syntax Check
```bash
python3 -m py_compile /opt/gemini_odoo19/addons/MODULE/models/*.py
```

---

## COMMON MISTAKES TO AVOID

1. **Running Odoo directly on host** (always use docker exec)
2. **Using box-drawing characters** (use ASCII only)
3. **Manual database fixes** (edit source code instead)
4. **Deleting features to fix bugs** (fix the logic)
5. **Not reading specifications** (always read tech spec first)
6. **Not updating TODO_MASTER** (update after every task)
7. **Using unicode emojis** (use [STATUS] markers)
8. **Creating duplicate docs** (check PROJECT_STRUCTURE first)

---

## EXAMPLE SESSION

### Good Session Start
```
I'm continuing work on the OPS Framework.

Session Date: 2026-01-04
Session Goal: Complete document lock during approval

MANDATORY READING (in order):
1. PROJECT_STRUCTURE.md
2. AGENT_RULES.md
3. OPS_FRAMEWORK_ENVIRONMENT.md
4. TODO_MASTER.md
5. HANDOFF_2026-01-03.md

Current State:
- Phase: Phase 1 - Foundation & Security
- Version: 19.0.1.3
- Last Completed: IT Admin blindness, cost/margin lock

Working On:
- Priority: [CRITICAL]
- Task: Priority #5 - Complete Document Lock During Approval
- Files: models/ops_approval_request.py, models/sale_order.py, views/sale_order_views.xml
- Estimated Effort: 1-2 sessions

Code Location: /opt/gemini_odoo19/addons/
Documentation: Claude.ai Project

Ready to proceed.
```

### Bad Session Start (Don't Do This)
```
Hi, I'm here to help with Odoo development.
```
*(Missing all context - will waste time)*

---

**END OF SESSION TEMPLATE**

Use this every time you start a development session.
