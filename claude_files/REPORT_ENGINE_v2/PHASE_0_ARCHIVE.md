# PHASE 0: Archive Old Report Code & Prepare Clean Slate
# Run with: claude -p "$(cat PHASE_0_ARCHIVE.md)"
# Estimated: ~5 minutes

## CONTEXT
You are rewriting the OPS Framework report engine in `/opt/gemini_odoo19/addons/ops_matrix_accounting/`.
This phase archives all old report code to `_archived_reports/v1/` without deleting anything.
The master spec is at `/opt/gemini_odoo19/addons/claude_files/REPORT_ENGINE_REWRITE_MASTER.md` — read it first.

## YOUR TASK

### Step 1: Create archive directory
```bash
mkdir -p /opt/gemini_odoo19/addons/ops_matrix_accounting/_archived_reports/v1/report
mkdir -p /opt/gemini_odoo19/addons/ops_matrix_accounting/_archived_reports/v1/wizard
mkdir -p /opt/gemini_odoo19/addons/ops_matrix_accounting/_archived_reports/v1/controllers
mkdir -p /opt/gemini_odoo19/addons/ops_matrix_accounting/_archived_reports/v1/views
```

### Step 2: Move THESE EXACT FILES to `_archived_reports/v1/report/`:
- `report/ops_financial_report_parser.py`
- `report/ops_general_ledger_report.py`
- `report/ops_financial_matrix_report.py`
- `report/ops_asset_register_report.py`
- `report/ops_corporate_report_parsers.py`
- `report/ops_xlsx_abstract.py`
- `report/ops_excel_report_builders.py`
- `report/ops_asset_register_xlsx.py`
- `report/ops_general_ledger_xlsx.py`
- `report/ops_financial_matrix_xlsx.py`
- `report/ops_treasury_report_xlsx.py`
- `report/ops_financial_report_template.xml`
- `report/ops_general_ledger_template.xml`
- `report/ops_consolidated_report_templates.xml`
- `report/ops_daily_report_templates.xml`
- `report/ops_inventory_report_templates.xml`
- `report/ops_treasury_report_templates.xml`
- `report/ops_asset_report_templates.xml`
- `report/ops_partner_ledger_corporate.xml`
- `report/ops_budget_vs_actual_corporate.xml`
- `report/components/ops_corporate_report_components.xml`

### Step 3: Move THESE EXACT FILES to `_archived_reports/v1/wizard/`:
- `wizard/ops_general_ledger_wizard_enhanced.py`

### Step 4: Move THESE EXACT FILES to `_archived_reports/v1/views/`:
- `views/ops_general_ledger_wizard_enhanced_views.xml`

### Step 5: Move THESE EXACT FILES to `_archived_reports/v1/controllers/`:
- `controllers/ops_report_controller.py`

### Step 6: Create `_archived_reports/v1/README.md`:
```markdown
# Archived Report Engine v1
**Archived:** 2026-02-09
**Reason:** Clean rewrite to contracted pipeline architecture (v2)
**Total lines archived:** ~25,000

## Archived Files
### Parsers (replaced by single bridge parser)
- ops_financial_report_parser.py (1,420 lines)
- ops_general_ledger_report.py (549 lines)
- ops_financial_matrix_report.py (299 lines)
- ops_asset_register_report.py (68 lines)
- ops_corporate_report_parsers.py (783 lines)

### Excel (replaced by generic renderer)
- ops_xlsx_abstract.py, ops_excel_report_builders.py
- ops_asset_register_xlsx.py, ops_general_ledger_xlsx.py
- ops_financial_matrix_xlsx.py, ops_treasury_report_xlsx.py

### Templates (replaced by shape-based system)
- 11 XML template files totaling ~7,300 lines

### God Wizard (replaced by focused wizards)
- ops_general_ledger_wizard_enhanced.py (2,053 lines)

### Controller (replaced)
- ops_report_controller.py (381 lines)

## Recovery
All code preserved here. Original functionality in git history.
```

### Step 7: Update `report/__init__.py` to ONLY import what's kept:
```python
# OPS Matrix Accounting - Report Engine v2

# Bridge Parser (universal)
from . import ops_report_bridge

# Data Contracts
from . import ops_report_contracts

# Excel Renderer
from . import ops_excel_renderer

# Legacy kept:
from . import excel_styles
```

Note: `ops_report_bridge.py`, `ops_report_contracts.py`, and `ops_excel_renderer.py` don't exist yet.
Create them as empty placeholder files so the import doesn't break:

```python
# report/ops_report_bridge.py
# Placeholder — implemented in Phase 1

# report/ops_report_contracts.py
# Placeholder — implemented in Phase 1

# report/ops_excel_renderer.py
# Placeholder — implemented in Phase 5
```

### Step 8: Update `wizard/__init__.py`:
Remove the import of `ops_general_ledger_wizard_enhanced`. Keep all other imports.
Add placeholder comments for new wizards (Phase 3-5).

### Step 9: Update `controllers/__init__.py`:
Comment out the old controller import. Leave placeholder for new one.

### Step 10: Update `__manifest__.py`:
Remove ALL archived XML files from `data` list. Comment them out with `# ARCHIVED v1:` prefix.
Do NOT add new files yet — they don't exist.
Keep: `report/ops_corporate_report_layout.xml`, `report/ops_report_invoice.xml`, `report/ops_report_payment.xml`, `data/ops_paperformat.xml`.

### Step 11: DO NOT update or restart the module yet.
Just verify all files moved correctly:
```bash
echo "=== Archived files ===" && ls -la _archived_reports/v1/report/ && ls -la _archived_reports/v1/wizard/ && ls -la _archived_reports/v1/controllers/ && ls -la _archived_reports/v1/views/
echo "=== Remaining report files ===" && ls -la report/
echo "=== Remaining wizard files ===" && ls -la wizard/
```

## RULES
- Use `mv` not `cp` — we want files MOVED, not copied
- Do NOT modify any Python model code (only __init__.py and __manifest__.py)
- Do NOT delete any files
- Do NOT run odoo update command
- Verify each move completed before proceeding
