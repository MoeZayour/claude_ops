# Wave 5 — Analytical Reports: Budget vs Actual, BU Profitability, Branch P&L

## BEFORE YOU START
Read `00_MANDATORY_RULES.md` in this folder. Those rules override any conflicting patterns below.

## MISSION
Redesign the Budget vs Actual, BU Profitability, and Branch P&L report templates. These are ANALYTICAL reports — they slice financial data across organizational dimensions (budgets, business units, branches). All use landscape orientation due to multiple data columns.

**Duration**: 4 hours | **Mode**: Autonomous — fix errors, don't stop
**Branch**: `git checkout -b wave-5-analytical-reports`
**DO NOT EDIT**: `__manifest__.py`, `__init__.py`, any other wave files

---

## PHASE 1: DISCOVERY (15 min)

```bash
echo "========================================"
echo "PHASE 1: DISCOVERY"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Budget report files ==="
find . -name "*budget*" -type f | grep -v __pycache__
grep -rl "budget.wizard\|budget_report\|budget_vs" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== BU Profitability files ==="
find . -name "*bu_profit*" -o -name "*business_unit*report*" | grep -v __pycache__
grep -rl "bu_profitability\|bu_profit" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== Branch P&L files ==="
find . -name "*branch*pnl*" -o -name "*branch*profit*" -o -name "*branch_pl*" | grep -v __pycache__
grep -rl "branch_pl\|branch_pnl\|branch_profit" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== Wizards ==="
cat wizard/ops_budget_wizard.py 2>/dev/null | head -50

echo "=== Report classes ==="
find . -path "*/report/*" -name "*.py" | xargs grep -l "budget\|bu_profit\|branch_p" 2>/dev/null

echo "✅ Discovery complete"
```

---

## PHASE 2: BUDGET VS ACTUAL REPORT (75 min)

### 2.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Landscape A4 |
| **Report ID Prefix** | `BVA-` |
| **Structure** | Grouped by account group/type |
| **Sort** | By account code within group |

**Columns (8):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Code | 7% | left | Account code |
| 2 | Account | 21% | left | Account name |
| 3 | Budget | 12% | right | Planned amount |
| 4 | Actual | 12% | right | Actual spent |
| 5 | Committed | 12% | right | Open POs/committed |
| 6 | Available | 12% | right | Budget - Actual - Committed |
| 7 | Used % | 10% | right | (Actual + Committed) / Budget × 100 |
| 8 | Status | 14% | center | Visual indicator |

**Status Column — Budget Utilization Indicator:**

| Utilization | Color | Badge Text |
|-------------|-------|------------|
| 0-50% | green bg (#dcfce7) | ON TRACK |
| 51-80% | blue bg (#dbeafe) | MODERATE |
| 81-100% | amber bg (#fef3c7) | CAUTION |
| > 100% | red bg (#fecaca) | OVER BUDGET |

Badge implementation: same inline style as Asset Register status badges.

**Progress bar alternative (optional but recommended):**
Instead of badge, use a simple inline progress bar:
```html
<div style="width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
    <div style="width: 75%; height: 100%; background: #3b82f6; border-radius: 4px;"></div>
</div>
<span style="font-size: 7pt; color: #64748b;">75%</span>
```
Color the bar: green (0-50%), blue (51-80%), amber (81-100%), red (>100%, clamp width to 100%).

**Group Headers:**
Account type groups (Revenue, COGS, Operating Expenses, etc.) as section headers with primary-light bg.

**Group Subtotals:**
Sum of Budget, Actual, Committed, Available for each group. Show group Used % and Status.

**Summary Row (4 metrics):**
- TOTAL BUDGET
- TOTAL ACTUAL
- TOTAL AVAILABLE
- OVERALL UTILIZATION % (with color)

**Grand Total Row:**
Primary bg, white text. Sums for Budget, Actual, Committed, Available columns.

**Special Rules:**
- Available negative (over budget) → show in red with parentheses
- Budget = 0 → show "N/A" for Used % (avoid division by zero)
- Committed = 0 → show "&#x2014;" dash

---

## PHASE 3: BU PROFITABILITY REPORT (60 min)

### 3.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Landscape A4 |
| **Report ID Prefix** | `BUP-` |
| **Structure** | P&L hierarchy with BU columns |
| **Dynamic Columns** | One column per Business Unit + Total |

**Column Structure:**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Account | 25% | left | Account name (hierarchical, indented) |
| 2..N | BU 1..N | dynamic | right | Amount for each BU |
| N+1 | Total | 12% | right | Sum across all BUs |

Width for BU columns: `(75% - 12%) / number_of_BUs`

**Row Structure — Follows P&L Pattern:**
```
REVENUE                    BU-Alpha  BU-Beta  BU-Gamma  Total
  Sales Revenue             50,000   30,000    20,000  100,000
  Service Revenue           10,000    5,000     8,000   23,000
TOTAL REVENUE               60,000   35,000    28,000  123,000

COST OF GOODS SOLD
  ...
TOTAL COGS                 (30,000) (18,000)  (12,000) (60,000)

GROSS PROFIT                30,000   17,000    16,000   63,000

OPERATING EXPENSES
  ...
TOTAL OPERATING            (15,000)  (8,000)   (9,000) (32,000)

NET INCOME                  15,000    9,000     7,000   31,000
```

**Styling Rules:**
- Use same hierarchy styling as P&L (Phase 2 of Wave 3)
- Section headers: primary bg, white text, spans all columns
- Subtotals: primary-light bg
- Computed lines (Gross Profit, Net Income): border-top 2px primary
- BU column headers: show BU name, rotated if > 4 BUs

**Summary Row (1 metric per BU + Total):**
NET INCOME for each BU. Color-code: green positive, red negative.

**Handling Variable BU Count:**
- If 1-3 BUs: comfortable width
- If 4-6 BUs: narrower columns, smaller font (7.5pt for data)
- If 7+: consider grouping into 2 pages or reducing to top N BUs

Use QWeb `t-foreach` to generate BU columns dynamically.

---

## PHASE 4: BRANCH P&L REPORT (45 min)

### 4.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Landscape A4 |
| **Report ID Prefix** | `BPL-` |
| **Structure** | P&L hierarchy with Branch columns |
| **Dynamic Columns** | One column per Branch + Total |

**Identical structure to BU Profitability** with these differences:
- Column headers show Branch names instead of BU names
- Data filtered by `ops_branch_id` instead of `ops_business_unit_id`
- Report title: "Branch Profit & Loss"
- Report ID prefix: `BPL-`

Clone BU Profitability template, change:
- Template ID
- Title
- Data source (branch dimension)
- Report ID prefix

---

## PHASE 5: PYTHON DATA LAYER (30 min)

### 5.1 Budget vs Actual

Ensure data dict includes:
```python
{
    'groups': [
        {
            'name': 'Operating Expenses',
            'lines': [
                {
                    'code': '6100',
                    'name': 'Salaries',
                    'budget': 50000,
                    'actual': 35000,
                    'committed': 5000,
                    'available': 10000,
                    'used_pct': 80.0,
                    'status': 'caution',  # on_track/moderate/caution/over_budget
                },
                ...
            ],
            'subtotal': { 'budget': ..., 'actual': ..., ... },
        },
        ...
    ],
    'totals': { 'budget': ..., 'actual': ..., 'committed': ..., 'available': ..., 'used_pct': ... },
    'report_id': 'BVA-...',
    'colors': { ... },
}
```

### 5.2 BU Profitability / Branch P&L

Ensure data dict includes:
```python
{
    'dimensions': ['BU Alpha', 'BU Beta', 'BU Gamma'],  # or branch names
    'dimension_count': 3,
    'lines': [
        {
            'name': 'Sales Revenue',
            'level': 2,         # 0=section, 1=group, 2=leaf
            'type': 'account',  # section/group/account/subtotal/total/computed
            'values': [50000, 30000, 20000],  # one per dimension
            'total': 100000,
        },
        ...
    ],
    'net_income_by_dimension': [15000, 9000, 7000],
    'net_income_total': 31000,
}
```

---

## PHASE 6: VERIFY & COMMIT (15 min)

```bash
echo "========================================"
echo "PHASE 6: VERIFY & COMMIT"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Syntax checks ==="
for f in $(find report/ -name "*budget*" -o -name "*bu_profit*" -o -name "*branch_pl*" | grep "\.py$"); do
    python3 -m py_compile "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"
done

for f in $(find report/ -name "*budget*" -o -name "*bu_profit*" -o -name "*branch_pl*" | grep "\.xml$"); do
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('$f'); print('✅ ' + '$f')" 2>&1 || echo "❌ $f"
done

cd /opt/gemini_odoo19
git add -A
git commit -m "feat(accounting): Wave 5 — Budget vs Actual, BU Profitability, Branch P&L

- Budget vs Actual: utilization badges/progress bars, 8 columns
- BU Profitability: dynamic BU columns, P&L hierarchy
- Branch P&L: dynamic Branch columns, P&L hierarchy
- Color-coded budget utilization (green→red)
- Report ID generation (BVA-/BUP-/BPL- prefixes)
- All landscape orientation
- All CSS inline, table-based layouts"

git push origin wave-5-analytical-reports

echo "✅ Wave 5 committed to branch wave-5-analytical-reports"
```

---

## FILES CREATED/MODIFIED

| File | Action |
|------|--------|
| `report/ops_budget_vs_actual_template.xml` | Rewritten |
| `report/ops_budget_vs_actual_report.py` | Enhanced |
| `report/ops_bu_profitability_template.xml` | Rewritten |
| `report/ops_bu_profitability_report.py` | Enhanced |
| `report/ops_branch_pl_template.xml` | Rewritten |
| `report/ops_branch_pl_report.py` | Enhanced (may share with BU) |

**DO NOT EDIT:** `__manifest__.py`, `__init__.py`, any other wave files

---

## SUCCESS CRITERIA

- [ ] Budget vs Actual: 8 columns with utilization badges
- [ ] Progress bars render in wkhtmltopdf (basic div-in-div)
- [ ] BU Profitability: dynamic columns, P&L hierarchy
- [ ] Branch P&L: dynamic columns, mirrors BU structure
- [ ] Negative availables in red with parentheses
- [ ] Division by zero handled (N/A for 0 budget)
- [ ] All landscape with correct paperformat
- [ ] All CSS inline, no flexbox
- [ ] Fixed footer on every page
- [ ] Committed to wave-5-analytical-reports branch

**BEGIN AUTONOMOUS EXECUTION NOW.**
