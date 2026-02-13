# PHASE 4: Refactor Remaining Wizards (Daily + Treasury + Assets + Inventory + Consolidation + Budget)
# Run with: claude -p "$(cat PHASE_4_REMAINING_WIZARDS.md)"
# Prerequisite: Phases 0-3 completed
# Estimated: ~30 minutes

## CONTEXT
You are refactoring the remaining report wizards to use the v2 data contracts.
These wizards ALREADY EXIST — you're refactoring them, not creating from scratch.

Read FIRST:
1. Data contracts: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_report_contracts.py`
2. A completed Phase 3 wizard for reference: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_gl_wizard.py`

Then read each existing wizard before refactoring it:
```bash
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_daily_reports_wizard.py
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_treasury_report_wizard.py
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_asset_report_wizard.py
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_inventory_report_wizard.py
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_consolidation_intelligence_wizard.py
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_budget_vs_actual_wizard.py
```

## REFACTORING PATTERN

For each existing wizard:
1. **Keep** the `_name`, class name, and all unique fields
2. **Add** `_inherit = 'ops.base.report.wizard'` if not already present
3. **Rewrite** `_get_report_data()` to return the correct data contract dict
4. **Rewrite** `_return_report_action()` to use the new ir.actions.report XML IDs from Phase 2
5. **Add** `_get_engine_name()` and `_get_report_shape()` methods
6. **Remove** any inline Excel generation code (will be handled by generic renderer in Phase 5)
7. **Remove** any inline HTML generation code (will be handled by controller in Phase 5)
8. **Keep** all domain-building logic — just ensure it includes branch isolation

### Pattern:
```python
def _get_report_data(self):
    self.ensure_one()
    self._check_intelligence_access(self._get_engine_name())
    
    meta = build_report_meta(self, self.report_type, self._get_report_titles()[self.report_type], self._get_report_shape())
    colors = build_report_colors(self.company_id)
    
    # ... existing query logic, adapted to return contract dict ...
    
    return to_dict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))
```

## YOUR TASK

### File 1: Refactor `wizard/ops_daily_reports_wizard.py`

Contains 3 wizards: `ops.cash.book.wizard`, `ops.day.book.wizard`, `ops.bank.book.wizard`
All are Shape A (line-based) reports.

For each:
- `_get_report_shape()` → `'lines'`
- `_get_engine_name()` → `'Financial'`
- Rewrite `_get_report_data()` to return ShapeAReport dict
- Cash Book: group by date or account, show cash journal lines only
- Day Book: group by journal, show all journal entries
- Bank Book: group by bank journal, show bank transactions with running balance per bank
- Remove inline Excel `action_export_to_excel()` method body (keep method, raise "use Phase 5")
- Remove inline HTML view logic
- Keep the domain building, keep the sort logic

### File 2: Refactor `wizard/ops_treasury_report_wizard.py`

Contains report_type selection: registry, maturity, on_hand
Shape C (matrix) report.

- `_get_report_shape()` → `'matrix'`
- `_get_engine_name()` → `'Treasury'`
- Registry: All PDCs with columns [PDC#, Type, Partner, Bank, Amount, Issue Date, Due Date, Status]
- Maturity: Buckets by due date [Partner, Current, 30d, 60d, 90d, 90+, Total]
- On Hand: Currently held PDCs [PDC#, Partner, Bank, Amount, Due Date, Days Held]
- Return ShapeCReport with dynamic ColumnDef list per report_type

### File 3: Refactor `wizard/ops_asset_report_wizard.py`

Contains report_type selection: register, schedule, disposal, forecast, movement
Shape C (matrix) report.

- `_get_report_shape()` → `'matrix'`
- `_get_engine_name()` → `'Asset'`
- Register: [Asset Name, Category, Purchase Date, Cost, Accum Depreciation, NBV, Status]
- Schedule: [Asset, Period, Depreciation Amount, Accum, NBV]
- Disposal: [Asset, Disposal Date, Cost, Accum Dep, NBV at Disposal, Sale Price, Gain/Loss]
- Forecast: [Asset, Next 12 months depreciation amounts]
- Movement: [Category, Opening NBV, Additions, Disposals, Depreciation, Closing NBV]
- IMPORTANT: Check cost visibility — only show Cost/NBV columns if user has `group_ops_see_cost`

### File 4: Refactor `wizard/ops_inventory_report_wizard.py`

Contains report_type selection: valuation, aging, movement, negative
Shape C (matrix) report.

- `_get_report_shape()` → `'matrix'`
- `_get_engine_name()` → `'Inventory'`
- Valuation: [Product, Category, Qty On Hand, Unit Cost, Total Value, Warehouse]
- Aging: [Product, Qty, Value, Current, 30d, 60d, 90d, 90+]
- Movement: [Product, Opening Qty, IN, OUT, Closing Qty, Value]
- Negative: [Product, Warehouse, Qty (negative), Last Movement Date]
- CRITICAL: Check `group_ops_see_cost` before including cost columns, `group_ops_see_valuation` before valuation columns

### File 5: Refactor `wizard/ops_consolidation_intelligence_wizard.py`

Contains report types for multi-company/branch/BU consolidation.
Shape B (hierarchy) report.

- `_get_report_shape()` → `'hierarchy'`
- `_get_engine_name()` → `'Financial'`
- Company Consolidation: P&L hierarchy with columns per company
- Branch P&L: P&L hierarchy with columns per branch
- BU Report: P&L hierarchy with columns per BU
- Consolidated BS: BS hierarchy with columns per entity
- value_columns should be dynamic: one column per branch/BU/company selected

### File 6: Refactor `wizard/ops_budget_vs_actual_wizard.py`

Shape B (hierarchy) report.

- `_get_report_shape()` → `'hierarchy'`
- `_get_engine_name()` → `'Financial'`
- Hierarchy: account groups → accounts
- value_columns: [Budget, Actual, Variance, Variance %]
- Favorable/unfavorable variance coloring (revenue: actual > budget = green, expense: actual > budget = red)

### File 7: Update wizard views

For each refactored wizard, ensure views are updated to include the `output_format` field.
Check each existing view XML file and add if missing:
```xml
<field name="output_format"/>
```

### File 8: Update `wizard/__init__.py`

Ensure all wizard imports are correct. Remove any commented-out or dead imports.

### File 9: Update `security/ir.model.access.csv`

Add ACL entries for any NEW wizard _name values. If _name stayed the same (which it should for refactored wizards), existing ACLs should work.

Verify:
```bash
grep "cash.book.wizard\|day.book.wizard\|bank.book.wizard\|treasury.report.wizard\|asset.report.wizard\|inventory.report.wizard\|consolidation.intelligence\|budget.vs.actual" /opt/gemini_odoo19/addons/ops_matrix_accounting/security/ir.model.access.csv
```

If any are missing, add them following the Phase 3 pattern.

## VERIFICATION

```bash
cd /opt/gemini_odoo19/addons/ops_matrix_accounting
echo "=== Syntax checks ===" 
for f in wizard/ops_daily_reports_wizard.py wizard/ops_treasury_report_wizard.py wizard/ops_asset_report_wizard.py wizard/ops_inventory_report_wizard.py wizard/ops_consolidation_intelligence_wizard.py wizard/ops_budget_vs_actual_wizard.py; do
    python3 -m py_compile "$f" && echo "OK: $f" || echo "FAIL: $f"
done
echo "=== Check all wizards have _get_report_data ==="
grep -l "_get_report_data" wizard/ops_*.py | wc -l
echo "=== Check all wizards have _get_report_shape ==="
grep -l "_get_report_shape" wizard/ops_*.py | wc -l
```

## RULES
- Keep existing `_name` values — do NOT rename models (would break DB records)
- Keep existing `report_type` Selection field values — do NOT rename selection keys
- Each wizard must call `self._check_intelligence_access()` first in `_get_report_data()`
- Cost/margin/valuation columns must check group membership before including
- Branch isolation is non-negotiable on every query
- Remove inline Excel/HTML code, keep method stubs that delegate to base
- Do NOT run odoo update yet
