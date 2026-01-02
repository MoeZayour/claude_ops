# OPS Matrix Comprehensive Testing – Resumable Plan (Phases 0–6)

## Phase 0 – Prerequisites & Environment
- Objective: Confirm container, DB, addons path, credentials ready.
- Checkpoints:
  - Verify `gemini_odoo19` running and reachable at `http://localhost:8089`.
  - Confirm DB `mz-db` accessible with Odoo shell.
  - Snapshot current logs (baseline) and note active modules.
- Error-handling: If container unreachable, restart then re-verify; if DB auth fails, validate `odoo.conf` creds; if module list incomplete, re-run manifest scan.

## Phase 1 – Module Discovery & Analysis
- Objective: Enumerate OPS Matrix modules and surface models, fields, rules, groups, wizards, reports.
- Checkpoints:
  - Run manifest discovery (`__manifest__.py` under `/mnt/extra-addons/ops_matrix_*`).
  - Extract models/fields/methods, security groups/record rules, wizards/reports per module.
  - Capture outputs into matrix notes for later coverage mapping.
- Error-handling: If grep/shell commands fail, verify paths and permissions; if models missing, flag for follow-up in error log.

## Phase 2 – Test Data Architecture & Seeding
- Objective: Define minimal-complete test data covering branches, BUs, personas, users, products, partners, and seed via script.
- Checkpoints:
  - Validate hierarchy matches prompt (branches HQ/DXB/AUH; BUs SALES/FIN/OPS/RETAIL/WHOLESALE; personas per spec).
  - Ensure test user mappings to branches/BUs/personas set; products/partners prepared.
  - Execute `test_data_seed.py` in Odoo shell; confirm commit and summary counts.
- Error-handling: On create conflicts, prefer idempotent search-or-create; log exceptions per user/record; if persona model missing, skip with warning and record.

## Phase 3 – Test Scenario Execution (Governance & Workflows)
- Objective: Run governance matrix and workflow validations using provided test functions.
- Checkpoints:
  - Execute governance search_count per user/model (sales orders, invoices, partners, leads).
  - Run workflow tests: sales rep create, cross-branch access denial, branch manager visibility, admin visibility.
  - Capture counts/pass/fail per scenario.
- Error-handling: If model absent, mark skipped with reason; on AccessError, confirm expected vs unexpected and log; rerun after fixes.

## Phase 4 – Error Fixing Protocol
- Objective: Triage and fix defects only in source; re-run affected tests.
- Checkpoints:
  - Log each error with file/line/type/message/root-cause/fix/result.
  - Apply common fixes (missing fields, record rule domains, groups, method signatures) then update modules if required.
  - Re-execute targeted tests until pass.
- Error-handling: If module upgrade needed, run Odoo upgrade command; if fix impacts data, avoid direct DB edits—adjust code/migrations.

## Phase 5 – Reporting
- Objective: Generate comprehensive test report per prompt template.
- Checkpoints:
  - Fill metrics (executed, passed, failed, errors fixed, pass rate).
  - Document module coverage, governance outcomes, workflow results, errors fixed, data created, recommendations.
  - Timestamped report saved to `/mnt/extra-addons/TEST_REPORT_*.md`.
- Error-handling: If data missing, backfill from logs and rerun specific tests; ensure markdown table integrity.

## Phase 6 – Finalization & Access Verification
- Objective: Ensure system ready and artifacts accessible.
- Checkpoints:
  - Restart container; wait and health-check login page.
  - Tail logs for errors; confirm none blocking.
  - Publish access info (URL, DB, test accounts) and report path.
- Error-handling: If restart fails, inspect docker logs; if health check fails, iterate until web responds; document any residual blockers.
