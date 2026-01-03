# OPS Framework - Issues & Blockers Log

**Purpose**: Track current issues, blockers, and technical debt  
**Status**: ACTIVE - Continuously updated  
**Format**: Active issues on top, resolved issues at bottom  

---

## ACTIVE ISSUES

### Currently: NONE

All known blockers have been resolved.

---

## RESOLVED ISSUES

### Issue #004 - Unreadable Characters in Documentation
- **Reported**: 2026-01-03
- **Severity**: MEDIUM
- **Description**: Box-drawing characters (â”œâ”€â”€, â””â”€â”€) and emojis not rendering in all environments
- **Impact**: Documentation hard to read
- **Solution**: Converted all documentation to ASCII-only characters
- **Resolved**: 2026-01-03
- **Files Fixed**: All .md files - using standard tree format and [STATUS] markers

### Issue #003 - Multiple TODO Files
- **Reported**: 2026-01-03
- **Severity**: MEDIUM
- **Description**: Three TODO files (TODO.md, TODO_v1.1.md, TODO_MASTER.md) causing confusion
- **Impact**: Unclear which file is source of truth
- **Solution**: Consolidated to single TODO_MASTER.md, archived old versions
- **Resolved**: 2026-01-03
- **Files Affected**: OPS_FRAMEWORK_TODO.md, OPS_FRAMEWORK_TODO_v1_1.md (archived)

### Issue #002 - Missing Data Files Referenced in Manifests
- **Reported**: 2026-01-02
- **Severity**: CRITICAL
- **Description**: Module manifest referenced data files that didn't exist
- **Impact**: Module installation blocked
- **Solution**: Created all 11 missing data XML files
- **Resolved**: 2026-01-02
- **Files Created**: ir_module_category.xml, res_groups.xml, ir_sequence_data.xml, ir_cron_data.xml, ops_asset_data.xml, etc.

### Issue #001 - Enterprise Dependency Incompatible with Community
- **Reported**: 2026-01-02
- **Severity**: CRITICAL
- **Description**: Module depended on spreadsheet_dashboard (Enterprise-only feature)
- **Impact**: Cannot install on Community Edition
- **Solution**: Removed Enterprise dependency from manifest
- **Resolved**: 2026-01-02
- **Files Modified**: __manifest__.py in ops_matrix_core

---

## TECHNICAL DEBT

### None Currently

All architectural decisions have been implemented cleanly.

---

## KNOWN LIMITATIONS

### Limitation #001 - Persona Combination UI
- **Description**: While personas can be combined, there's no user-friendly UI for it yet
- **Impact**: LOW - Can be done manually by assigning multiple personas
- **Planned Fix**: Priority #LOW in TODO_MASTER.md
- **Workaround**: Manually assign multiple personas to user

### Limitation #002 - Data Export Security Not Implemented
- **Description**: Export security hooks not yet created
- **Impact**: MEDIUM - Data can be exported in bulk
- **Planned Fix**: Priority #CRITICAL in TODO_MASTER.md
- **Workaround**: None - manual policy enforcement

---

## ENHANCEMENT REQUESTS

### None Currently

Will be tracked here as they come up during development/testing.

---

## ISSUE TEMPLATE

When adding new issues, use this format:

```
### Issue #XXX - [Short Title]
- **Reported**: YYYY-MM-DD
- **Severity**: CRITICAL | HIGH | MEDIUM | LOW
- **Description**: [What is the issue?]
- **Impact**: [How does it affect the system?]
- **Solution**: [How was it resolved?]
- **Resolved**: YYYY-MM-DD (or "OPEN" if not resolved)
- **Files Affected**: [List of files]
```

---

## SEVERITY DEFINITIONS

| Severity | Definition | Response Time |
|----------|------------|---------------|
| **CRITICAL** | Blocks installation/usage | Immediate (same session) |
| **HIGH** | Breaks core functionality | Within 1 session |
| **MEDIUM** | Degrades user experience | Within 1-2 sessions |
| **LOW** | Minor inconvenience | When convenient |

---

## CHANGE LOG

| Date | Change | Notes |
|------|--------|-------|
| 2026-01-03 | Created ISSUES_LOG.md | Initial issue tracking system |

---

**END OF ISSUES LOG**

Update when issues are discovered or resolved.
