# OPS Framework - Go-Live Autonomous Execution Prompt

**Mission:** Install, fix, seed, and validate the entire OPS Framework for production readiness  
**Mode:** Fully autonomous - no approvals needed until complete  
**Duration:** Estimated 4-6 hours  
**Date:** 2026-01-31

---

## EXECUTIVE DIRECTIVE

You are Claude Code executing an autonomous go-live sequence for OPS Framework on Odoo 19 CE. You have **full authority** to:

1. Install modules in sequence
2. Fix ANY code errors in source files
3. Create comprehensive seed data via Odoo ORM
4. Test every feature thoroughly
5. Commit progress at phase boundaries
6. Generate detailed reports

**CONSTRAINTS:**
- NO direct database manipulation (no SQL INSERT/UPDATE/DELETE)
- ALL data operations through Odoo ORM/API only
- Fix errors in SOURCE CODE only
- Work as if you are a human user interacting with the system

**AUTONOMY LEVEL:** Execute all phases without stopping for approval. Only stop if:
- A critical error cannot be resolved after 3 attempts
- A security vulnerability is discovered
- Data loss would occur

---

## ENVIRONMENT

```
VPS Path: /opt/gemini_odoo19/
Database: mz-db
Container: gemini_odoo19
Dev URL: https://dev.mz-im.com/
Git Branch: main

Modules to Install (IN ORDER):
1. ops_matrix_core
2. ops_matrix_accounting  
3. ops_theme
4. ops_dashboard

Report Output: /opt/gemini_odoo19/claude_files/go_live_audit/
```

---

## PHASE OVERVIEW

| Phase | Name | Duration | Deliverable |
|-------|------|----------|-------------|
| 0 | Environment Verification | 15 min | Environment ready |
| 1 | Module Installation | 60 min | All 4 modules installed |
| 2 | Error Resolution | 90 min | Zero errors in logs |
| 3 | Seed Data Creation | 60 min | Complete test dataset |
| 4 | Functional Testing | 90 min | All features verified |
| 5 | UI/UX Validation | 45 min | All views working |
| 6 | Security Testing | 45 min | Security rules verified |
| 7 | Final Report | 30 min | Complete documentation |

---

## GIT COMMIT STRATEGY

Commit at these checkpoints:
1. After Phase 1 (modules installed)
2. After Phase 2 (errors fixed) - may have multiple commits per major fix
3. After Phase 3 (seed data created)
4. After Phase 6 (all testing complete)
5. Final commit with reports

**Commit Message Format:**
```
[GO-LIVE] Phase X: Description

- Detail 1
- Detail 2
- Detail 3

Tested: Yes/No
Errors Fixed: X
```

---

## REPORT STRUCTURE

Create these files in `/opt/gemini_odoo19/claude_files/go_live_audit/`:

```
go_live_audit/
├── 00_EXECUTION_LOG.md       # Real-time progress log
├── 01_INSTALLATION_REPORT.md # Module installation details
├── 02_ERROR_FIX_REPORT.md    # All errors found and fixed
├── 03_SEED_DATA_REPORT.md    # Seed data created
├── 04_FUNCTIONAL_TEST.md     # Feature test results
├── 05_UI_TEST_REPORT.md      # UI validation results
├── 06_SECURITY_TEST.md       # Security test results
├── 07_FINAL_SUMMARY.md       # Go/No-Go recommendation
└── 08_KNOWN_ISSUES.md        # Issues deferred to future
```

---

## BEGIN EXECUTION

Read the phase files in order:
1. `01_PHASE_ENVIRONMENT.md`
2. `02_PHASE_INSTALLATION.md`
3. `03_PHASE_ERROR_RESOLUTION.md`
4. `04_PHASE_SEED_DATA.md`
5. `05_PHASE_FUNCTIONAL_TEST.md`
6. `06_PHASE_UI_VALIDATION.md`
7. `07_PHASE_SECURITY_TEST.md`
8. `08_PHASE_FINAL_REPORT.md`

**START NOW. Execute autonomously until complete.**
