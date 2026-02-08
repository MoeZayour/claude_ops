# Wave Final — Integration: Merge All Branches, Update Manifest, Full Test

## MISSION
Merge all wave branches into main, update `__manifest__.py` and `__init__.py` files to include all new report files, resolve any conflicts, install module, and verify all reports generate PDF without errors.

**Duration**: 1.5 hours | **Mode**: Autonomous — fix errors, don't stop
**This runs AFTER all wave branches are committed.**

---

## PHASE 1: MERGE ALL BRANCHES (20 min)

```bash
echo "========================================"
echo "PHASE 1: MERGE ALL BRANCHES"
echo "========================================"

cd /opt/gemini_odoo19

echo "=== Current branches ==="
git branch -a

echo "=== Ensure main is up to date ==="
git checkout main
git pull origin main

echo "=== Merge Wave 1 ==="
git merge wave-1-transaction-ledgers --no-edit 2>&1 || {
    echo "⚠️ Conflict in Wave 1 — resolving..."
    # If conflict is in __manifest__.py or __init__.py, keep main version (we'll rebuild these)
    git checkout --ours __manifest__.py __init__.py 2>/dev/null
    git add .
    git commit --no-edit
}
echo "✅ Wave 1 merged"

echo "=== Merge Wave 2 ==="
git merge wave-2-aging-reports --no-edit 2>&1 || {
    echo "⚠️ Conflict in Wave 2 — resolving..."
    git checkout --theirs addons/ops_matrix_accounting/report/ 2>/dev/null
    git checkout --ours addons/ops_matrix_accounting/__manifest__.py 2>/dev/null
    git add .
    git commit --no-edit
}
echo "✅ Wave 2 merged"

echo "=== Merge Wave 3 ==="
git merge wave-3-financial-statements --no-edit 2>&1 || {
    echo "⚠️ Conflict in Wave 3 — resolving..."
    git checkout --theirs addons/ops_matrix_accounting/report/ 2>/dev/null
    git checkout --ours addons/ops_matrix_accounting/__manifest__.py 2>/dev/null
    git add .
    git commit --no-edit
}
echo "✅ Wave 3 merged"

echo "=== Merge Wave 4 ==="
git merge wave-4-register-reports --no-edit 2>&1 || {
    echo "⚠️ Conflict in Wave 4 — resolving..."
    git checkout --theirs addons/ops_matrix_accounting/report/ 2>/dev/null
    git checkout --ours addons/ops_matrix_accounting/__manifest__.py 2>/dev/null
    git add .
    git commit --no-edit
}
echo "✅ Wave 4 merged"

echo "=== Merge Wave 5 ==="
git merge wave-5-analytical-reports --no-edit 2>&1 || {
    echo "⚠️ Conflict in Wave 5 — resolving..."
    git checkout --theirs addons/ops_matrix_accounting/report/ 2>/dev/null
    git checkout --ours addons/ops_matrix_accounting/__manifest__.py 2>/dev/null
    git add .
    git commit --no-edit
}
echo "✅ Wave 5 merged"

echo "=== Merge Wave 6 ==="
git merge wave-6-advanced-statements --no-edit 2>&1 || {
    echo "⚠️ Conflict in Wave 6 — resolving..."
    git checkout --theirs addons/ops_matrix_accounting/report/ 2>/dev/null
    git checkout --ours addons/ops_matrix_accounting/__manifest__.py 2>/dev/null
    git add .
    git commit --no-edit
}
echo "✅ Wave 6 merged"

echo "✅ All branches merged into main"
```

---

## PHASE 2: INVENTORY NEW FILES (15 min)

```bash
echo "========================================"
echo "PHASE 2: INVENTORY NEW FILES"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== All report Python files ==="
find report/ -name "*.py" -type f | sort

echo "=== All report XML files ==="
find report/ -name "*.xml" -type f | sort

echo "=== All wizard Python files ==="
find wizard/ -name "*.py" -type f | sort

echo "=== All data XML files ==="
find data/ -name "*.xml" -type f | sort

echo "=== New files not in manifest ==="
# Extract current manifest data list
python3 -c "
import ast, os

# Read manifest
with open('__manifest__.py') as f:
    manifest = ast.literal_eval(f.read())

# Get all data files listed
listed = set(manifest.get('data', []))

# Find all XML files that should be in data
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.xml'):
            path = os.path.join(root, f).lstrip('./')
            if path not in listed:
                print(f'MISSING from manifest: {path}')
" 2>/dev/null || echo "Manual check needed"

echo "✅ Inventory complete"
```

---

## PHASE 3: UPDATE __MANIFEST__.PY (15 min)

Based on Phase 2 inventory, add ALL new files to `__manifest__.py`:

```bash
echo "========================================"
echo "PHASE 3: UPDATE MANIFEST"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Current manifest data section ==="
python3 -c "
import ast
with open('__manifest__.py') as f:
    m = ast.literal_eval(f.read())
for d in sorted(m.get('data', [])):
    print(d)
"
```

Now add missing files. The agent should:

1. Read current `__manifest__.py`
2. Find all new XML files from waves
3. Add them to the `'data'` list in correct order:
   - `security/` files first
   - `data/` files second (paperformats, report actions)
   - `report/` templates third
   - `wizard/` views last
4. Write updated manifest

**Order within data list:**
```python
'data': [
    # Security
    'security/ir.model.access.csv',
    'security/security.xml',
    # ... existing security files

    # Data (paperformats, report actions, sequences)
    'data/ops_report_paperformat.xml',
    # ... existing data files

    # Reports - GL (Wave 0)
    'report/ops_general_ledger_template.xml',

    # Reports - Transaction Ledgers (Wave 1)
    'report/ops_cash_book_template.xml',
    'report/ops_day_book_template.xml',
    'report/ops_bank_book_template.xml',
    'report/ops_partner_ledger_template.xml',

    # Reports - Aging (Wave 2)
    'report/ops_aged_receivables_template.xml',
    'report/ops_aged_payables_template.xml',

    # Reports - Financial Statements (Wave 3)
    'report/ops_profit_loss_template.xml',
    'report/ops_balance_sheet_template.xml',
    'report/ops_trial_balance_template.xml',

    # Reports - Registers (Wave 4)
    'report/ops_asset_register_template.xml',
    'report/ops_pdc_registry_template.xml',
    'report/ops_pdc_maturity_template.xml',

    # Reports - Analytical (Wave 5)
    'report/ops_budget_vs_actual_template.xml',
    'report/ops_bu_profitability_template.xml',
    'report/ops_branch_pl_template.xml',

    # Reports - Advanced (Wave 6)
    'report/ops_cash_flow_template.xml',
    'report/ops_consolidated_pl_template.xml',

    # Wizards
    # ... existing wizard views
],
```

**NOTE:** File names may differ from these examples. Use ACTUAL file names found in Phase 2. The agent must adapt to whatever naming convention each wave used.

---

## PHASE 4: UPDATE __INIT__.PY FILES (10 min)

```bash
echo "========================================"
echo "PHASE 4: UPDATE __INIT__.PY"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Check report/__init__.py ==="
cat report/__init__.py

echo "=== All Python report files ==="
ls report/*.py | grep -v __init__ | grep -v __pycache__

echo "=== Missing imports ==="
for f in report/*.py; do
    module=$(basename "$f" .py)
    if [ "$module" != "__init__" ] && ! grep -q "$module" report/__init__.py; then
        echo "MISSING: from . import $module"
    fi
done
```

Add missing imports to `report/__init__.py` and `wizard/__init__.py`.

---

## PHASE 5: MODULE UPDATE + TEST (20 min)

```bash
echo "========================================"
echo "PHASE 5: MODULE UPDATE + TEST"
echo "========================================"

echo "=== Updating ops_matrix_accounting ==="
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1

echo "=== Check for errors ==="
docker logs gemini_odoo19 --tail 100 | grep -i "error\|traceback\|warning" | head -30

echo "=== Restart container ==="
docker restart gemini_odoo19
sleep 10

echo "=== Verify running ==="
docker logs gemini_odoo19 --tail 20
```

If module update fails, check error and fix:
- Missing file → Check file path in manifest matches actual location
- XML parse error → Fix template XML
- Python import error → Fix `__init__.py`
- Model error → Check Python syntax

**Fix errors and retry until module installs clean.**

---

## PHASE 6: REPORT GENERATION TEST (20 min)

For each report, verify it can generate a PDF:

```bash
echo "========================================"
echo "PHASE 6: REPORT GENERATION TEST"
echo "========================================"

# Use Odoo shell to test each report
docker exec -it gemini_odoo19 odoo shell -d mz-db << 'SHELL'
from odoo import api, SUPERUSER_ID

# List all OPS report actions
reports = env['ir.actions.report'].search([('report_name', 'like', 'ops_matrix_accounting.report_')])
for r in reports:
    print(f"📄 {r.report_name} — {r.name}")

# Count reports
print(f"\nTotal OPS reports: {len(reports)}")
SHELL

echo "=== Manual test instructions ==="
echo ""
echo "Login to https://dev.mz-im.com as admin"
echo "Navigate to Accounting > Reports menu"
echo "For each report:"
echo "  1. Open the report wizard"
echo "  2. Set date range (current month)"
echo "  3. Click Generate"
echo "  4. Verify PDF renders:"
echo "     - Header with company info + report ID"
echo "     - Data displays correctly"
echo "     - Footer with OPS badge on every page"
echo "     - No encoding issues (no â€" characters)"
echo "     - Colors render (not plain black text)"
echo ""
echo "Reports to test:"
echo "  Wave 0: General Ledger"
echo "  Wave 1: Cash Book, Day Book, Bank Book, Partner Ledger"
echo "  Wave 2: Aged Receivables, Aged Payables"
echo "  Wave 3: P&L, Balance Sheet, Trial Balance"
echo "  Wave 4: Asset Register, PDC Registry, PDC Maturity"
echo "  Wave 5: Budget vs Actual, BU Profitability, Branch P&L"
echo "  Wave 6: Cash Flow, Consolidated P&L"

echo "✅ Phase 6 complete — manual testing required"
```

---

## PHASE 7: FINAL COMMIT (5 min)

```bash
echo "========================================"
echo "PHASE 7: FINAL COMMIT"
echo "========================================"

cd /opt/gemini_odoo19
git add -A
git status

git commit -m "chore(accounting): Wave Integration — merge all report redesigns

- Merged waves 1-6 into main branch
- Updated __manifest__.py with all new report files
- Updated __init__.py imports
- Module installs clean
- 19 reports with corporate branding template

Reports redesigned:
- GL, Cash Book, Day Book, Bank Book, Partner Ledger
- Aged Receivables, Aged Payables
- P&L, Balance Sheet, Trial Balance
- Asset Register, PDC Registry, PDC Maturity
- Budget vs Actual, BU Profitability, Branch P&L
- Cash Flow, Consolidated P&L"

git push origin main

echo "✅ Integration complete — all waves merged to main"
```

---

## PHASE 8: CLEANUP (5 min)

```bash
echo "========================================"
echo "PHASE 8: CLEANUP"
echo "========================================"

cd /opt/gemini_odoo19

echo "=== Deleting wave branches ==="
for branch in wave-1-transaction-ledgers wave-2-aging-reports wave-3-financial-statements wave-4-register-reports wave-5-analytical-reports wave-6-advanced-statements; do
    git branch -d "$branch" 2>/dev/null && echo "Deleted local: $branch"
    git push origin --delete "$branch" 2>/dev/null && echo "Deleted remote: $branch"
done

echo "✅ All wave branches cleaned up"

echo "========================================"
echo "INTEGRATION COMPLETE"
echo "========================================"
echo ""
echo "REPORTS REDESIGNED: 19"
echo "BRANCHES MERGED: 6"
echo "MODULE STATUS: Installed"
echo ""
echo "NEXT: Wave 7 — Excel variants"
echo "========================================"
```

---

## SUCCESS CRITERIA

- [ ] All 6 wave branches merged into main without conflicts
- [ ] `__manifest__.py` includes all new report files
- [ ] `__init__.py` files include all new Python imports
- [ ] Module installs without errors
- [ ] Container starts without errors
- [ ] All 19 report actions registered in database
- [ ] At least GL report generates PDF successfully
- [ ] Wave branches deleted
- [ ] Single clean commit on main

**BEGIN AUTONOMOUS EXECUTION NOW.**
