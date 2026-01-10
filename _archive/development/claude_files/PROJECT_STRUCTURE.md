# OPS Framework - Project Structure & Organization

**Version**: 1.0  
**Last Updated**: January 3, 2026  
**Purpose**: Master organizational document for all development activities  
**Status**: ACTIVE - All agents must follow this structure  

---

## TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [File Naming Conventions](#file-naming-conventions)
4. [Documentation Hierarchy](#documentation-hierarchy)
5. [Version Control Strategy](#version-control-strategy)
6. [Development Workflow](#development-workflow)
7. [Agent Roles & Responsibilities](#agent-roles--responsibilities)
8. [Communication Protocols](#communication-protocols)

---

## PROJECT OVERVIEW

### Project Identity
- **Name**: OPS Matrix Framework
- **Platform**: Odoo 19 Community Edition
- **Target**: Multi-branch, multi-business-unit companies with zero technical knowledge
- **Current Version**: 19.0.1.3 (next: 19.0.1.4)
- **Status**: Active Development - Phase 1

### Core Principles
1. **LITE** - Zero configuration, works out of the box
2. **DYNAMIC** - Personas can be combined
3. **PLUG-AND-PLAY** - Preloaded data, archived templates
4. **ZERO-TECH** - No technical knowledge required
5. **SECURITY-FIRST** - Lock by default, grant access explicitly

---

## DIRECTORY STRUCTURE

### Documentation Location Strategy

**CRITICAL DECISION**: 
- **Code Repository**: `/home/claude/ops-framework-dev-main/` (HOST SERVER)
- **Documentation Repository**: Claude.ai Project (for easy reference in all chats)
- **Reason**: Direct code access for development, docs in chat for quick lookup

### Claude.ai Project Files (Documentation Only)

```
Claude.ai Project/
|
+-- 00_MASTER/
|   |-- PROJECT_STRUCTURE.md           (THIS FILE - master organization)
|   |-- AGENT_RULES.md                 (Rules for all AI assistants)
|   |-- DEVELOPMENT_WORKFLOW.md        (Step-by-step development process)
|   +-- SESSION_TEMPLATE.md            (Template for starting sessions)
|
+-- 01_SPECIFICATIONS/
|   |-- OPS_FRAMEWORK_ENVIRONMENT.md   (Master context/environment)
|   |-- OPS_FRAMEWORK_USER_EXPERIENCE_v1_2.md (Complete UX spec - 18 personas)
|   |-- OPS_MATRIX_CORE_TECHNICAL_SPEC.md (Core module technical spec)
|   |-- OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md (Accounting module spec)
|   |-- OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md (Reporting module spec)
|   +-- README_TECHNICAL_SPECS.md      (Index for all technical specs)
|
+-- 02_TRACKING/
|   |-- OPS_FRAMEWORK_TODO_MASTER.md   (SINGLE source of truth for tasks)
|   |-- COMPLETED_LOG.md               (Completed items with dates)
|   +-- ISSUES_LOG.md                  (Known issues and blockers)
|
+-- 03_ARCHITECTURE/
|   |-- Comprehensive_Review           (Marketing-style overview)
|   |-- SECURITY_ARCHITECTURE.md       (Security model deep-dive)
|   |-- DATA_MODEL.md                  (ERD and relationships)
|   +-- API_DOCUMENTATION.md           (API endpoints and usage)
|
+-- 04_HANDOFFS/
|   |-- HANDOFF_TEMPLATE.md            (Template for session handoffs)
|   +-- Handoffs/
|       |-- HANDOFF_2026-01-03.md     (Session-specific handoffs)
|       +-- HANDOFF_2026-01-04.md
|
+-- 05_REFERENCES/
|   |-- ODOO19_STANDARDS.md            (Odoo 19 coding standards)
|   |-- DOCKER_COMMANDS.md             (Docker quick reference)
|   +-- TROUBLESHOOTING.md             (Common issues & solutions)
|
+-- 06_ARCHIVES/
    +-- old_versions/                  (Deprecated docs)
```

### Host Server Files (Code Repository)

```
/home/claude/ops-framework-dev-main/
|
+-- addons/
|   |-- ops_matrix_core/
|   |-- ops_matrix_accounting/
|   |-- ops_matrix_reporting/
|   +-- ops_matrix_asset_management/
|
+-- config/
|   +-- odoo.conf
|
+-- docker-compose.yml
+-- README.md
+-- CHANGELOG.md
```

---

## FILE NAMING CONVENTIONS

### Documentation Files

**Pattern**: `COMPONENT_TYPE_VERSION.md`

| Component | Examples |
|-----------|----------|
| OPS_FRAMEWORK | OPS_FRAMEWORK_TODO_MASTER.md |
| OPS_MATRIX_CORE | OPS_MATRIX_CORE_TECHNICAL_SPEC.md |
| OPS_MATRIX_ACCOUNTING | OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md |

**Version Suffix Rules**:
- No suffix = Living document (continuously updated)
- `_vX.Y` = Versioned document (e.g., `_v1.2`)
- `_MASTER` = Single source of truth (no duplicates allowed)

### Code Files

**Pattern**: Follow Odoo standards

| Type | Pattern | Example |
|------|---------|---------|
| Models | `ops_{model_name}.py` | `ops_branch.py` |
| Views | `{model_name}_views.xml` | `ops_branch_views.xml` |
| Security | `ir_rule_{purpose}.xml` | `ir_rule_it_admin.xml` |
| Data | `{model_name}_data.xml` | `ops_asset_data.xml` |
| Templates | `ops_{entity}_templates.xml` | `ops_persona_templates.xml` |

### Session Handoff Files

**Pattern**: `HANDOFF_YYYY-MM-DD.md`

Example: `HANDOFF_2026-01-03.md`

---

## DOCUMENTATION HIERARCHY

### Level 0: Master Documents (READ FIRST)
1. **PROJECT_STRUCTURE.md** (THIS FILE) - How everything is organized
2. **AGENT_RULES.md** - Rules all agents must follow
3. **OPS_FRAMEWORK_ENVIRONMENT.md** - Project context and current state

### Level 1: Specifications (READ BEFORE CODING)
1. **OPS_FRAMEWORK_USER_EXPERIENCE_vX.X.md** - UX requirements for all 18 personas
2. **OPS_MATRIX_CORE_TECHNICAL_SPEC.md** - Core module architecture
3. **OPS_MATRIX_ACCOUNTING_TECHNICAL_SPEC.md** - Accounting module architecture
4. **OPS_MATRIX_REPORTING_TECHNICAL_SPEC.md** - Reporting module architecture

### Level 2: Tracking (CHECK DAILY)
1. **OPS_FRAMEWORK_TODO_MASTER.md** - What's done, what's next
2. **COMPLETED_LOG.md** - Historical record
3. **ISSUES_LOG.md** - Current blockers

### Level 3: References (AS NEEDED)
- ODOO19_STANDARDS.md
- DOCKER_COMMANDS.md
- TROUBLESHOOTING.md

### Level 4: Archives (HISTORICAL)
- Old versions of documents
- Deprecated specs

---

## VERSION CONTROL STRATEGY

### Documentation Versioning

**Living Documents** (No version suffix):
- Updated continuously in place
- Examples: PROJECT_STRUCTURE.md, AGENT_RULES.md, TODO_MASTER.md

**Versioned Documents** (With _vX.Y suffix):
- Create new version for major changes
- Keep previous version in archives
- Examples: OPS_FRAMEWORK_USER_EXPERIENCE_v1.2.md

**Version Bump Rules**:
- **Major (X.0)**: Architectural changes, complete rewrites
- **Minor (X.Y)**: New sections, significant additions
- **No bump**: Typo fixes, clarifications

### Code Versioning

Follow Odoo standards: `19.0.MAJOR.MINOR.PATCH`

Current: `19.0.1.3`
- **19.0** = Odoo version
- **1** = Major module version
- **3** = Minor/patch number

**When to bump**:
- New model = Major bump (1.3.0 -> 2.0.0)
- New field/method = Minor bump (1.3.0 -> 1.4.0)
- Bug fix = Patch bump (1.3.0 -> 1.3.1)

---

## DEVELOPMENT WORKFLOW

### Phase 1: Planning (Current)
1. Define all 18 personas (DONE)
2. Define all governance rules (DONE)
3. Define security architecture (DONE)
4. **NEXT**: Complete document lock during approval

### Standard Development Cycle

```
1. Check TODO_MASTER.md
   |
   v
2. Read relevant TECHNICAL_SPEC.md
   |
   v
3. Code on HOST SERVER (/home/claude/ops-framework-dev-main/)
   |
   v
4. Test using Docker commands
   |
   v
5. Update TODO_MASTER.md (mark as DONE)
   |
   v
6. Create HANDOFF if ending session
   |
   v
7. Commit code changes (git)
```

### Multi-Session Projects

For features spanning multiple sessions:

1. **Session N**: 
   - Work on feature
   - Create `HANDOFF_YYYY-MM-DD.md` with:
     - What was completed
     - What's in progress
     - Next steps
     - Files modified
     - Commands to continue

2. **Session N+1**:
   - Read `HANDOFF_YYYY-MM-DD.md` from previous session
   - Read `TODO_MASTER.md` for current priority
   - Continue work

---

## AGENT ROLES & RESPONSIBILITIES

### Primary Agent (You - Currently Active)
- **Role**: Development Manager & Implementer
- **Responsibilities**:
  - Organize project structure
  - Create/update documentation
  - Implement features
  - Update TODO tracking
  - Create handoffs
- **Authority**: Full control over project organization

### Future Agents (Other AI Assistants)
- **Role**: Feature Implementers
- **Responsibilities**:
  - Read PROJECT_STRUCTURE.md first
  - Read AGENT_RULES.md second
  - Check TODO_MASTER.md for assignments
  - Follow coding standards
  - Update tracking documents
- **Authority**: Limited to assigned features

### Human Developer (Moe)
- **Role**: Product Owner & Reviewer
- **Responsibilities**:
  - Define requirements
  - Review implementations
  - Approve major architectural changes
  - Deploy to production
- **Authority**: Final decision on all matters

---

## COMMUNICATION PROTOCOLS

### Starting a New Session

**MANDATORY OPENING**:
```
I'm continuing work on the OPS Framework.

Current state: [brief summary from TODO_MASTER.md]
Working on: [specific task from TODO_MASTER.md]

Read:
1. PROJECT_STRUCTURE.md (this file)
2. AGENT_RULES.md
3. OPS_FRAMEWORK_ENVIRONMENT.md
4. Last HANDOFF file (if multi-session)
```

### Ending a Session

**MANDATORY CLOSING** (if work is incomplete):
1. Update TODO_MASTER.md (mark progress)
2. Create HANDOFF_YYYY-MM-DD.md with:
   - What was completed
   - What's in progress  
   - Files modified
   - Commands to resume
   - Next steps

### Between Sessions

**Human Developer Actions**:
- Review changes
- Test on dev environment
- Update TODO_MASTER.md if priorities change
- Add new requirements to appropriate spec

---

## CRITICAL RULES FOR ALL AGENTS

### RULE 1: Single Source of Truth
- **TODO_MASTER.md** is the ONLY TODO list (no duplicates)
- **OPS_FRAMEWORK_ENVIRONMENT.md** is the ONLY environment doc
- Never create competing documents

### RULE 2: Read Before Act
- ALWAYS read PROJECT_STRUCTURE.md first
- ALWAYS read AGENT_RULES.md second
- ALWAYS check TODO_MASTER.md before starting work

### RULE 3: Update Tracking
- Mark tasks as DONE in TODO_MASTER.md immediately
- Add completed items to COMPLETED_LOG.md with date
- Log blockers in ISSUES_LOG.md

### RULE 4: No Guessing
- If something is unclear, ask before proceeding
- Don't assume - read the spec
- Don't delete features to fix bugs

### RULE 5: Standard Characters Only
- Use ASCII characters in all documents
- NO box-drawing characters (â”œâ”€â”€, â””â”€â”€)
- Use standard tree format:
  ```
  |-- item
  |   |-- subitem
  |   +-- subitem
  +-- item
  ```

---

## FILE CREATION CHECKLIST

Before creating ANY new document:

- [ ] Does it duplicate existing content? (Check structure above)
- [ ] Does it follow naming convention? (Check conventions section)
- [ ] Does it fit in the hierarchy? (Check documentation hierarchy)
- [ ] Is version suffix needed? (Check versioning rules)
- [ ] Will it be updated frequently? (Living vs versioned)

---

## DOCUMENT TYPES REFERENCE

### Master Documents
- **Purpose**: Define how project works
- **Update Frequency**: As needed (when process changes)
- **Versioning**: Living (no version suffix)
- **Examples**: PROJECT_STRUCTURE.md, AGENT_RULES.md

### Specification Documents
- **Purpose**: Define what to build
- **Update Frequency**: When requirements change
- **Versioning**: Versioned (_vX.Y)
- **Examples**: USER_EXPERIENCE_v1.2.md, TECHNICAL_SPEC.md

### Tracking Documents
- **Purpose**: Track progress and issues
- **Update Frequency**: Daily/per session
- **Versioning**: Living (continuous updates)
- **Examples**: TODO_MASTER.md, COMPLETED_LOG.md

### Handoff Documents
- **Purpose**: Transfer context between sessions
- **Update Frequency**: End of each incomplete session
- **Versioning**: Dated (YYYY-MM-DD)
- **Examples**: HANDOFF_2026-01-03.md

### Reference Documents
- **Purpose**: Quick lookup information
- **Update Frequency**: When standards change
- **Versioning**: Living or versioned (depends on content)
- **Examples**: DOCKER_COMMANDS.md, ODOO19_STANDARDS.md

---

## NEXT STEPS FOR THIS PROJECT

### Immediate Actions (This Session)
1. [x] Create PROJECT_STRUCTURE.md (this file)
2. [ ] Create AGENT_RULES.md (comprehensive rules for all agents)
3. [ ] Create TODO_MASTER.md (consolidate all TODO files)
4. [ ] Create DEVELOPMENT_WORKFLOW.md (detailed process)
5. [ ] Create SESSION_TEMPLATE.md (template for starting sessions)
6. [ ] Fix all unreadable characters in existing files
7. [ ] Move all files to Claude.ai project in correct folders

### Subsequent Sessions
1. Follow the established structure
2. Update TODO_MASTER.md as work progresses
3. Create handoffs as needed
4. Maintain organization

---

## CHANGE LOG

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-01-03 | 1.0 | Initial project structure document | Claude (Project Manager) |

---

**END OF PROJECT STRUCTURE**

This document is the foundation of all project organization. All agents must read and follow it.
