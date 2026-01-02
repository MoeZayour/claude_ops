# TASK: Implement Menu Reorganization

## Context
Read the full specification: `docs/MENU_REORGANIZATION_SPEC.md`

## Objective
Reorganize all OPS Matrix menus following modular architecture principles.

## Execution Phases

### Phase 1: Audit & Analysis (Architect Mode)
- [x] Run audit commands from spec
- [x] Document current menu inventory
- [x] Identify broken references
- [x] Update spec with findings

### Phase 2: Menu Refactoring (Code Mode)
- [x] **`ops_matrix_accounting` Refactor**
  - [x] Correct `__manifest__.py`
  - [x] Consolidate menus into `addons/ops_matrix_accounting/views/accounting_menus.xml`
  - [x] Clean up orphaned files in ops_matrix_accounting
  - [x] Correct parent attributes in `accounting_menus.xml`
  - [x] Validate manifest references the new file and not the old ones.
- [x] Refactor menus in ops_matrix_core
- [x] **`ops_matrix_reporting` Refactor**
  - [x] Refactor menus in `addons/ops_matrix_reporting/views/reporting_menu.xml`
  - [x] Correct invalid parent references
  - [x] Verify `__manifest__.py` entries

## Phase 3: Validation and Verification
- [-] Restart Odoo and upgrade modules

## Success Criteria
See Phase 4: Validation in the spec document.
