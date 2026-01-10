# OPS Framework - Development Workflow & Agent Responsibilities

**Last Updated**: January 4, 2026  
**Repository**: https://github.com/MoeZayour/claude_ops.git  
**VPS Path**: `/opt/gemini_odoo19/`

---

## Development Environment Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GITHUB REPOSITORY                        │
│              github.com/MoeZayour/claude_ops                 │
│                                                              │
│  ┌──────────────┐              ┌─────────────────────┐      │
│  │   addons/    │              │  claude_files/      │      │
│  │  (Code)      │              │  (Documentation)    │      │
│  └──────────────┘              └─────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
    (MCP Access)                         (MCP Access)
         │                                    │
         │                                    │
┌────────┴────────┐                  ┌───────┴──────────┐
│   RooCode       │                  │ Claude Desktop   │
│   (VSCode)      │                  │   (MCP Client)   │
│                 │                  │                  │
│ Location:       │                  │ Location:        │
│ VPS Host        │                  │ Your Computer    │
│ /opt/gemini_    │                  │                  │
│ odoo19/         │                  │ Reads: Repo      │
│                 │                  │ Writes: Docs     │
│ Does: Code      │                  │ Updates: TODOs   │
│ Tests: Direct   │                  │                  │
│ Commits: Yes    │                  │ Commits: Yes     │
└─────────────────┘                  └──────────────────┘
```

---

## Agent Roles & Responsibilities

### 🤖 RooCode (VSCode on VPS)

**Location**: VPS Host at `/opt/gemini_odoo19/`  
**Access**: Direct filesystem + Git via MCP  
**Primary Role**: Code Development & Testing

**What RooCode Does**:
- ✅ Develops Odoo modules in `/addons/`
- ✅ Tests code directly on running Odoo instance
- ✅ Fixes bugs and installation errors
- ✅ Validates Python/XML syntax
- ✅ Installs/upgrades modules via Odoo CLI
- ✅ Commits working code to GitHub

**RooCode Works On**:
```
addons/
├── ops_matrix_core/
│   ├── models/*.py          ← RooCode edits
│   ├── views/*.xml          ← RooCode edits
│   ├── data/*.xml           ← RooCode edits
│   ├── security/            ← RooCode edits
│   └── __manifest__.py      ← RooCode edits
├── ops_matrix_accounting/
├── ops_matrix_asset_management/
└── ops_matrix_reporting/
```

**RooCode Commits**:
- Bug fixes
- New features
- Model changes
- View updates
- Data file modifications
- Security rules

**Commit Message Pattern**:
```
feat(module): Add new feature X
fix(module): Fix installation error Y
refactor(module): Improve code Z
```

---

### 📋 Claude Desktop (MCP Client)

**Location**: Your local computer  
**Access**: GitHub repo via MCP (read/write)  
**Primary Role**: Documentation & Project Management

**What Claude Desktop Does**:
- ✅ Reads repository state via MCP
- ✅ Updates `TODO_MASTER.md` with progress
- ✅ Creates session reports in `claude_files/`
- ✅ Maintains `PROJECT_STRUCTURE.md`
- ✅ Tracks features and priorities
- ✅ Documents decisions and changes
- ✅ Commits documentation to GitHub

**Claude Desktop Works On**:
```
claude_files/
├── TODO_MASTER.md                    ← Claude updates
├── PROJECT_STRUCTURE.md              ← Claude maintains
├── AGENT_RULES.md                    ← Claude maintains
├── CODE_AUDIT_REPORT_*.md            ← Claude creates
├── INSTALLATION_SUCCESS_*.md         ← Claude creates
├── SESSION_SUMMARY_*.md              ← Claude creates
└── QUICK_WIN_*.md                    ← Claude creates
```

**Claude Desktop Commits**:
- TODO updates
- Session summaries
- Audit reports
- Architecture decisions
- Feature documentation
- Progress tracking

**Commit Message Pattern**:
```
docs: Update TODO with completed features
docs: Add session summary for Jan 4
docs: Code audit report - installation fixes
```

---

## File Ownership Matrix

| Directory/File | Owner | Purpose | Commit By |
|---------------|-------|---------|-----------||
| `addons/**/*.py` | RooCode | Python code | RooCode |
| `addons/**/*.xml` | RooCode | Views/Data/Security | RooCode |
| `addons/**/__manifest__.py` | RooCode | Module config | RooCode |
| `claude_files/TODO_MASTER.md` | Claude Desktop | Progress tracking | Claude Desktop |
| `claude_files/PROJECT_STRUCTURE.md` | Claude Desktop | Architecture | Claude Desktop |
| `claude_files/*_REPORT_*.md` | Claude Desktop | Documentation | Claude Desktop |
| `config/` | Manual | Odoo config | Manual/Admin |
| `docker-compose.yml` | Manual | Container config | Manual/Admin |
| `.gitignore` | Manual | Git exclusions | Manual/Admin |

---

## Development Workflow

### Standard Development Cycle

```
1. USER gives task to Claude Desktop
   ↓
2. Claude Desktop reads repo via MCP
   ↓
3. Claude Desktop analyzes current state
   ↓
4. Claude Desktop updates TODO_MASTER.md
   ↓
5. Claude Desktop commits documentation
   ↓
6. USER gives refined instructions to RooCode
   ↓
7. RooCode works on VPS at /opt/gemini_odoo19/
   ↓
8. RooCode develops code in addons/
   ↓
9. RooCode tests on Odoo instance
   ↓
10. RooCode fixes any errors (up to 5 retries)
    ↓
11. RooCode commits working code to GitHub
    ↓
12. USER informs Claude Desktop of completion
    ↓
13. Claude Desktop reads updated repo via MCP
    ↓
14. Claude Desktop updates TODO (marks DONE)
    ↓
15. Claude Desktop creates session report
    ↓
16. Claude Desktop commits documentation
    ↓
17. CYCLE COMPLETE
```

---

## Typical Session Flow

### Example: Adding a New Feature

**Step 1**: User → Claude Desktop
```
User: "We need to add IT Admin Blindness feature - 
       create 20 record rules to block IT Admin from 
       seeing business transactions"
```

**Step 2**: Claude Desktop Actions
```bash
# Claude reads repo via MCP
# Claude updates TODO_MASTER.md:
#   - Priority #6: IT Admin Blindness [IN PROGRESS]
#   - Add 20 record rules needed
# Claude commits to GitHub
```

**Step 3**: User → RooCode (on VPS)
```
User: "Create 20 record rules in 
       ops_matrix_core/security/ir_rule_it_admin.xml
       to exclude group_ops_it_admin from:
       - sale.order
       - purchase.order
       - account.move
       ... (detailed specs)"
```

**Step 4**: RooCode Actions
```bash
# RooCode creates: security/ir_rule_it_admin.xml
# RooCode updates: __manifest__.py (adds file to data list)
# RooCode tests: docker exec ... -u ops_matrix_core
# RooCode verifies: Rules loaded, IT Admin blocked
# RooCode commits: "feat(core): Add IT Admin blindness rules"
```

**Step 5**: User → Claude Desktop
```
User: "RooCode completed IT Admin Blindness feature.
       All 20 rules created and tested successfully."
```

**Step 6**: Claude Desktop Actions
```bash
# Claude reads repo via MCP (sees new commit)
# Claude updates TODO_MASTER.md:
#   - Priority #6: IT Admin Blindness [DONE] ✓
# Claude creates: SESSION_SUMMARY_2026-01-04.md
# Claude commits: "docs: IT Admin Blindness completed"
```

---

## Git Workflow

### Branch Strategy

**Main Branch**: `main`
- Production-ready code
- All commits are tested
- Direct commits allowed (single developer)

**No Feature Branches**: Not needed for single developer workflow

### Commit Frequency

**RooCode Commits**:
- After each successful feature/fix
- After module installation succeeds
- After bug fix is verified
- Frequency: Multiple times per session

**Claude Desktop Commits**:
- After TODO updates
- After creating session reports
- After major documentation changes
- Frequency: 1-3 times per session

### Pulling Changes

**When to Pull**:

RooCode should pull BEFORE starting work:
```bash
cd /opt/gemini_odoo19
git pull origin main
```

Claude Desktop auto-syncs via MCP (no manual pull needed)

---

## Communication Protocol

### RooCode → User

**Format**: Action-oriented updates
```
✓ Created security/ir_rule_it_admin.xml
✓ Added 20 record rules
✓ Updated manifest
✓ Testing installation...
✓ SUCCESS - Module upgraded
✓ Committed to GitHub
```

### Claude Desktop → User

**Format**: Documentation-oriented updates
```
📋 Updated TODO_MASTER.md
   - Marked Priority #6 as [DONE]
   - Updated completion stats: 6/10 priorities complete
   
📄 Created SESSION_SUMMARY_2026-01-04.md
   - IT Admin Blindness: Complete
   - 20 record rules implemented
   - Next: Document Lock feature
   
✓ Committed documentation to GitHub
```

### User → Agents

**To RooCode** (Development Tasks):
```
"Create a new model ops.something in ops_matrix_core with 
 these fields: X, Y, Z. Add views and security."
```

**To Claude Desktop** (Documentation Tasks):
```
"Update TODO to reflect that we completed IT Admin 
 Blindness. Create a summary of what was accomplished 
 this week."
```

---

## Directory Structure (Reference)

```
/opt/gemini_odoo19/  (VPS Host)
├── addons/                     ← RooCode workspace
│   ├── ops_matrix_core/
│   │   ├── models/            ← Python models
│   │   ├── views/             ← XML views
│   │   ├── data/              ← Data files
│   │   ├── security/          ← Access rules
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ops_matrix_accounting/
│   ├── ops_matrix_asset_management/
│   └── ops_matrix_reporting/
│
├── claude_files/               ← Claude Desktop workspace
│   ├── TODO_MASTER.md         ← Master tracking
│   ├── PROJECT_STRUCTURE.md   ← Architecture docs
│   ├── AGENT_RULES.md         ← Workflow rules
│   └── *_REPORT_*.md          ← Session reports
│
├── config/                     ← Admin only
│   └── odoo.conf
│
├── docker-compose.yml          ← Admin only
├── .gitignore                  ← Admin only
└── README.md                   ← Shared docs
```

---

## MCP Access Details

### What MCP Provides

Both agents access GitHub via MCP server with these capabilities:

**Read Operations**:
- `github:get_file_contents` - Read any file
- `github:list_commits` - View commit history
- `github:get_pull_request` - Check PRs
- `github:search_code` - Search codebase

**Write Operations**:
- `github:push_files` - Commit files
- `github:create_or_update_file` - Modify files
- `github:create_branch` - Make branches (not used)

**Both Agents Use Same MCP**:
- RooCode: VSCode MCP client
- Claude Desktop: Desktop app MCP client
- Both connect to: `github.com/MoeZayour/claude_ops`

---

## Conflict Resolution

### If Both Agents Modify Same File

**Unlikely Scenario** (different workspaces):
- RooCode works in `addons/`
- Claude Desktop works in `claude_files/`

**If It Happens**:
1. Git will show merge conflict
2. Agent who pulled later resolves
3. Keep both changes if possible
4. User decides if conflict is real

**Prevention**:
- Clear separation of responsibilities
- RooCode = Code
- Claude Desktop = Docs

---

## Testing & Verification

### RooCode Testing Checklist

Before committing code:
```bash
# 1. Syntax check
python3 -m py_compile models/*.py
xmllint --noout data/*.xml views/*.xml

# 2. Installation test
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf \
  -d test-db -u ops_matrix_core --stop-after-init

# 3. Verify in logs
docker logs gemini_odoo19 --tail 100 | grep -i error

# 4. If all pass → Commit
git add -A
git commit -m "feat(core): Description"
git push origin main
```

### Claude Desktop Verification Checklist

Before committing docs:
```markdown
# 1. Check TODO accuracy
- [ ] All [DONE] items are actually complete
- [ ] All [IN PROGRESS] items are being worked on
- [ ] Priorities are correct

# 2. Verify session report
- [ ] Lists actual work completed
- [ ] Links to relevant commits
- [ ] Next steps are clear

# 3. Commit
Commits via MCP automatically
```

---

## Quick Reference Commands

### For RooCode (on VPS)

```bash
# Pull latest
cd /opt/gemini_odoo19 && git pull origin main

# Check status
git status

# Test module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf \
  -d mz-db -u ops_matrix_core --stop-after-init

# Commit changes
git add addons/ops_matrix_core/
git commit -m "feat(core): Added new feature"
git push origin main

# View logs
docker logs gemini_odoo19 --tail 100
```

### For Claude Desktop (via MCP)

```markdown
# Read repo state
Use: github:get_file_contents on TODO_MASTER.md

# Update documentation
Use: github:push_files with updated docs

# Check recent changes
Use: github:list_commits

# Create session report
Use: github:push_files with new report file
```

---

## Success Indicators

### You Know It's Working When:

✅ **RooCode**:
- Code commits appear on GitHub after development
- Modules install successfully
- Tests pass on VPS
- No merge conflicts

✅ **Claude Desktop**:
- TODO stays synchronized with actual progress
- Session reports document all work
- Documentation commits appear on GitHub
- Accurate tracking of completed features

✅ **Overall Workflow**:
- Clear separation: Code vs Docs
- No duplicate work
- Both agents stay synchronized via Git
- User has visibility into all progress

---

## Common Questions

**Q: Can RooCode and Claude Desktop work simultaneously?**  
A: Yes! They work on different files (code vs docs), so no conflicts.

**Q: What if I want to make manual changes?**  
A: Pull latest, make changes, commit. Tell both agents about the change.

**Q: How do agents know about each other's work?**  
A: They read the shared Git repository via MCP.

**Q: Can I give tasks to both agents at once?**  
A: Yes, but be clear about who does what. Generally:
- Technical tasks → RooCode
- Documentation tasks → Claude Desktop

**Q: What if a commit fails?**  
A: Agent will report error. Usually means:
- Need to pull latest first
- Syntax error in commit message
- Network issue

---

## Emergency Procedures

### If Git Gets Messy

```bash
# On VPS (RooCode's side)
cd /opt/gemini_odoo19
git fetch origin
git reset --hard origin/main  # CAUTION: Loses local changes
```

### If Odoo Module Breaks

```bash
# Uninstall broken module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf \
  -d mz-db --uninstall ops_matrix_core

# Fix code
# Reinstall
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf \
  -d mz-db -i ops_matrix_core --stop-after-init
```

### If Agents Get Confused

1. Tell Claude Desktop: "Read TODO_MASTER.md and summarize current state"
2. Tell RooCode: "Check what modules are installed and their status"
3. Sync both with latest main branch

---

## Summary

**Simple Version**:

1. **RooCode** = Writes code on VPS, commits to GitHub
2. **Claude Desktop** = Writes docs, updates TODO, commits to GitHub
3. **Both** = Use MCP to access same GitHub repository
4. **User** = Orchestrates both agents, reviews progress
5. **Git** = Single source of truth for everyone

**File Separation**:
- `addons/` = RooCode's territory
- `claude_files/` = Claude Desktop's territory
- No overlap = No conflicts

**Workflow**:
- User → Claude Desktop → Plans & Documents
- User → RooCode → Codes & Tests
- Both → GitHub → Single source of truth
- User → Reviews both → Happy! 🎉

---

**Last Updated**: January 4, 2026  
**Status**: Active Development  
**Next Review**: As needed when workflow changes
