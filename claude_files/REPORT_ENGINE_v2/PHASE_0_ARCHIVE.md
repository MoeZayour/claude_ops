# PHASE 0: Archive Old Report Code & Prepare Clean Slate
# Run with: claude -p "$(cat /opt/gemini_odoo19/claude_files/REPORT_ENGINE_v2/PHASE_0_ARCHIVE.md)"

## CONTEXT
You are rewriting the OPS Framework report engine in `/opt/gemini_odoo19/addons/ops_matrix_accounting/`.
Read the master spec first: `cat /opt/gemini_odoo19/claude_files/REPORT_ENGINE_v2/REPORT_ENGINE_REWRITE_MASTER.md`

## TASK

### Step 1: Create archive directory
```bash
mkdir -p /opt/gemini_odoo19/addons/ops_matrix_accounting/_archived_reports/v1/{report,wizard,controllers,views,report/components}
```

### Step 2: Move parsers to archive
```bash
cd /opt/gemini_odoo19/addons/ops_matrix_accounting
for f in report/ops_financial_report_parser.py report/ops_general_ledger_report.py report/ops_financial_matrix_report.py report/ops_asset_register_report.py report/ops_corporate_report_parsers.py; do
    [ -f "$f" ] && mv "$f" "_archived_reports/v1/$f" && echo "Moved: $f"
done
```

### Step 3: Move Excel files to archive
```bash
for f in report/ops_xlsx_abstract.py report/ops_excel_report_builders.py report/ops_asset_register_xlsx.py report/ops_general_ledger_xlsx.py report/ops_financial_matrix_xlsx.py report/ops_treasury_report_xlsx.py; do
    [ -f "$f" ] && mv "$f" "_archived_reports/v1/$f" && echo "Moved: $f"
done
```

### Step 4: Move templates to archive
```bash
for f in report/ops_financial_report_template.xml report/ops_general_ledger_template.xml report/ops_consolidated_report_templates.xml report/ops_daily_report_templates.xml report/ops_inventory_report_templates.xml report/ops_treasury_report_templates.xml report/ops_asset_report_templates.xml report/ops_partner_ledger_corporate.xml report/ops_budget_vs_actual_corporate.xml; do
    [ -f "$f" ] && mv "$f" "_archived_reports/v1/$f" && echo "Moved: $f"
done
[ -f "report/components/ops_corporate_report_components.xml" ] && mv "report/components/ops_corporate_report_components.xml" "_archived_reports/v1/report/components/" && echo "Moved: components"
```

### Step 5: Move God wizard + views + controller
```bash
[ -f "wizard/ops_general_ledger_wizard_enhanced.py" ] && mv "wizard/ops_general_ledger_wizard_enhanced.py" "_archived_reports/v1/wizard/"
[ -f "views/ops_general_ledger_wizard_enhanced_views.xml" ] && mv "views/ops_general_ledger_wizard_enhanced_views.xml" "_archived_reports/v1/views/"
[ -f "controllers/ops_report_controller.py" ] && mv "controllers/ops_report_controller.py" "_archived_reports/v1/controllers/"
```

### Step 6: Create archive README
Create `_archived_reports/v1/README.md` with:
- Date: 2026-02-09
- Reason: Clean rewrite to contracted pipeline architecture (v2)
- Total: ~25,000 lines archived
- List all archived files with line counts

### Step 7: Update report/__init__.py
Remove ALL imports of archived files. Create placeholder imports:
```python
# OPS Matrix Accounting - Report Engine v2
from . import ops_report_contracts  # placeholder
from . import ops_report_bridge     # placeholder
from . import excel_styles
```
Create empty placeholder files: `report/ops_report_contracts.py` and `report/ops_report_bridge.py`

### Step 8: Update wizard/__init__.py
Remove import of `ops_general_ledger_wizard_enhanced`. Keep all other imports.

### Step 9: Update controllers/__init__.py
Comment out old controller import. Create empty `controllers/ops_report_controller.py` placeholder.

### Step 10: Update __manifest__.py
Comment out ALL archived XML files with `# ARCHIVED v1:` prefix.
Keep: ops_corporate_report_layout.xml, ops_report_invoice.xml, ops_report_payment.xml, ops_paperformat.xml

### Step 11: Verify (DO NOT update module)
```bash
echo "=== Archived ===" && find _archived_reports/v1 -type f | wc -l
echo "=== Remaining report/ ===" && ls report/*.py report/*.xml 2>/dev/null
echo "=== Remaining wizard/ ===" && ls wizard/*.py 2>/dev/null
```

## RULES
- Use `mv` not `cp`
- Do NOT modify Python model code (only __init__.py and __manifest__.py)
- Do NOT delete files
- Do NOT run odoo update
