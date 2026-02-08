# Wave 6 — Advanced Statements: Cash Flow Statement, Consolidated P&L

## BEFORE YOU START
Read `00_MANDATORY_RULES.md` in this folder. Those rules override any conflicting patterns below.

## MISSION
Redesign the Cash Flow Statement and Consolidated P&L report templates. These are the most complex financial reports — Cash Flow uses the indirect method with account mapping, Consolidated P&L aggregates across multiple companies with elimination entries.

**Duration**: 3.5 hours | **Mode**: Autonomous — fix errors, don't stop
**Branch**: `git checkout -b wave-6-advanced-statements`
**DO NOT EDIT**: `__manifest__.py`, `__init__.py`, any other wave files

---

## PHASE 1: DISCOVERY (15 min)

```bash
echo "========================================"
echo "PHASE 1: DISCOVERY"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Cash Flow files ==="
find . -name "*cash_flow*" -o -name "*cashflow*" | grep -v __pycache__
grep -rl "cash.flow\|cash_flow" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== Consolidated P&L files ==="
find . -name "*consolidat*" -type f | grep -v __pycache__
grep -rl "consolidat" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== Financial report wizard (handles CF) ==="
grep -n "cash_flow\|cash.flow\|cf_\|cashflow" wizard/ops_financial_report_wizard.py 2>/dev/null

echo "=== Consolidation wizard ==="
cat wizard/ops_consolidation_wizard.py 2>/dev/null | head -60

echo "=== Report classes ==="
find . -path "*/report/*" -name "*.py" | xargs grep -l "cash_flow\|consolidat" 2>/dev/null

echo "✅ Discovery complete"
```

---

## PHASE 2: CASH FLOW STATEMENT (90 min)

### 2.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Portrait A4 |
| **Report ID Prefix** | `CF-` |
| **Method** | Indirect (start from Net Income) |
| **Structure** | 3 sections: Operating, Investing, Financing |

**Columns — Single Period (2):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Description | 65% | left | Line item (indented by level) |
| 2 | Amount | 35% | right | Cash flow amount |

**Columns — Comparative (4):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Description | 40% | left | Line item |
| 2 | Current | 20% | right | Current period |
| 3 | Prior | 20% | right | Prior period |
| 4 | Change | 20% | right | Variance |

**Report Structure:**

```
CASH FLOWS FROM OPERATING ACTIVITIES          ← Section header (primary bg, white)
  Net Income                        15,000    ← Starting point (bold)
  
  Adjustments for Non-Cash Items:             ← Subsection header (primary-light bg)
    Depreciation & Amortization      5,000    ← Line item (regular)
    Provision for Bad Debts          1,000
    (Gain)/Loss on Asset Disposal     (500)
  Total Adjustments                  5,500    ← Subsection total (semibold)
  
  Changes in Working Capital:                 ← Subsection header
    (Increase)/Decrease in Receivables (3,000)
    (Increase)/Decrease in Inventory   (2,000)
    Increase/(Decrease) in Payables     4,000
    Increase/(Decrease) in Accruals     1,000
  Total Working Capital Changes        0      ← Subsection total
  
NET CASH FROM OPERATING ACTIVITIES   20,500   ← Section total (bold, primary bg)

═══════════════════════════════════════════

CASH FLOWS FROM INVESTING ACTIVITIES          ← Section header
  Purchase of Equipment            (10,000)
  Proceeds from Asset Sale           2,000
  Purchase of Investments           (5,000)
NET CASH FROM INVESTING ACTIVITIES  (13,000)  ← Section total

═══════════════════════════════════════════

CASH FLOWS FROM FINANCING ACTIVITIES          ← Section header
  Proceeds from Borrowings          15,000
  Repayment of Loans               (8,000)
  Dividends Paid                   (5,000)
NET CASH FROM FINANCING ACTIVITIES    2,000   ← Section total

═══════════════════════════════════════════

NET INCREASE/(DECREASE) IN CASH      9,500    ← Grand total line 1 (bold, large)
CASH AT BEGINNING OF PERIOD         25,000    ← Reference line
CASH AT END OF PERIOD               34,500    ← Grand total line 2 (primary bg, white)

═══════════════════════════════════════════
```

**Styling Rules:**

| Element | Style |
|---------|-------|
| Section header (Operating/Investing/Financing) | Primary bg, white text, 9pt bold uppercase |
| Subsection header (Adjustments/Working Capital) | Primary-light bg, 8.5pt semibold |
| Net Income (starting point) | Bold, no background |
| Line items | Regular 8.5pt, alternating rows, indent 30px |
| Subsection totals | Semibold, primary-light bg, indent 20px |
| Section totals | Bold, primary bg, white text |
| Separator lines | 2px solid primary color, 16px margin |
| Final summary | Net Change (bold 10pt), Opening (regular), Closing (primary bg) |

**Value Formatting:**
- Cash inflows (positive): green (#16a34a) — no parentheses
- Cash outflows (negative): red (#dc2626) — with parentheses
- Zero: show "&#x2014;" for line items, "0.00" gray for totals

**Summary Row (3 metrics):**
- OPERATING: net cash from operating
- INVESTING: net cash from investing
- FINANCING: net cash from financing

### 2.2 Important Business Rules

- Parentheses convention: outflows always in parentheses
- Working capital changes: increase in asset = cash outflow (negative), increase in liability = cash inflow (positive)
- "Net Income" is pulled from P&L for the period
- Cash at beginning = bank/cash account balances at period start
- Cash at end MUST equal actual bank/cash balances at period end (validation check)

---

## PHASE 3: CONSOLIDATED P&L (75 min)

### 3.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Landscape A4 |
| **Report ID Prefix** | `CPL-` |
| **Structure** | P&L hierarchy with company columns |
| **Special Column** | Elimination entries |

**Column Structure:**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Account | 22% | left | Account name (hierarchical) |
| 2..N | Company 1..N | dynamic | right | Amount per company |
| N+1 | Eliminations | 12% | right | Intercompany elimination amounts |
| N+2 | Consolidated | 14% | right | Final consolidated total (bold) |

Width for company columns: `(66% - 12% - 14%) / number_of_companies` = `40% / N`

**Row Structure — P&L Hierarchy:**
Same as standard P&L (Wave 3) but with company columns:

```
                          Co. A    Co. B   Elim.  Consolidated
REVENUE
  Sales Revenue           100,000  80,000  (5,000)  175,000
  Service Revenue          20,000  10,000       -    30,000
TOTAL REVENUE             120,000  90,000  (5,000)  205,000

COGS
  ...
TOTAL COGS               (60,000) (45,000)  3,000  (102,000)

GROSS PROFIT               60,000  45,000  (2,000)  103,000

...

NET INCOME                 25,000  18,000  (2,000)   41,000
```

**Elimination Column:**
- Shows intercompany transaction eliminations
- Typically negative (removing double-counted revenue/expense)
- Red text for negative amounts
- Could be zero for many lines — show "&#x2014;" dash

**Consolidated Column:**
- Sum of all companies + eliminations
- Bold text
- This is the "true" figure

**Styling:**
- Company column headers: show company short name
- Elimination header: "Elim." with italic style
- Consolidated header: "Consolidated" with bold + primary-dark text
- Same hierarchy indentation as standard P&L
- Section headers span all columns

**Summary Row (metrics per company + consolidated):**
NET INCOME for each company + elimination + consolidated total.

**Handling Variable Company Count:**
- 1-2 companies: comfortable width
- 3-4 companies: narrower columns, smaller font (7.5pt)
- 5+: consider summary mode (only show section totals per company, not leaf accounts)

### 3.2 Elimination Rules

The elimination amounts should come from the existing consolidation engine. The template just renders what Python provides. Data dict should include:

```python
{
    'companies': ['Alpha Trading LLC', 'Beta Services Ltd'],
    'company_count': 2,
    'lines': [
        {
            'name': 'Sales Revenue',
            'level': 2,
            'type': 'account',
            'company_values': [100000, 80000],
            'elimination': -5000,
            'consolidated': 175000,
        },
        ...
    ],
    'net_income_by_company': [25000, 18000],
    'net_income_elimination': -2000,
    'net_income_consolidated': 41000,
}
```

---

## PHASE 4: PYTHON DATA LAYER (20 min)

Add standard helpers to both report classes:
- `_get_report_id(prefix)` — CF- or CPL-
- `_get_report_colors(company)` — with fallbacks
- `print_date` — DD MMM YYYY format

For Cash Flow, ensure the data dict validates:
```python
cash_at_end = cash_at_beginning + net_operating + net_investing + net_financing
# Include 'is_balanced' flag in data dict
```

---

## PHASE 5: REPORT ACTIONS + PAPERFORMAT (10 min)

- Cash Flow → `paperformat_ops_portrait`
- Consolidated P&L → `paperformat_ops_landscape`

---

## PHASE 6: VERIFY & COMMIT (15 min)

```bash
echo "========================================"
echo "PHASE 6: VERIFY & COMMIT"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Syntax checks ==="
for f in $(find report/ -name "*cash_flow*" -o -name "*consolidat*" | grep "\.py$"); do
    python3 -m py_compile "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"
done

for f in $(find report/ -name "*cash_flow*" -o -name "*consolidat*" | grep "\.xml$"); do
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('$f'); print('✅ ' + '$f')" 2>&1 || echo "❌ $f"
done

cd /opt/gemini_odoo19
git add -A
git commit -m "feat(accounting): Wave 6 — Cash Flow Statement, Consolidated P&L

- Cash Flow: indirect method, 3 activity sections
- Cash Flow: opening/closing cash validation
- Consolidated P&L: dynamic company columns + elimination
- Consolidated P&L: P&L hierarchy with consolidation
- Report ID generation (CF-/CPL- prefixes)
- All CSS inline, table-based layouts
- Fixed footer with OPS badge"

git push origin wave-6-advanced-statements

echo "✅ Wave 6 committed to branch wave-6-advanced-statements"
```

---

## FILES CREATED/MODIFIED

| File | Action |
|------|--------|
| `report/ops_cash_flow_template.xml` | Rewritten |
| `report/ops_cash_flow_report.py` | Enhanced |
| `report/ops_consolidated_pl_template.xml` | Rewritten |
| `report/ops_consolidated_pl_report.py` | Enhanced |

**DO NOT EDIT:** `__manifest__.py`, `__init__.py`, any other wave files

---

## SUCCESS CRITERIA

- [ ] Cash Flow: 3 sections (Operating/Investing/Financing)
- [ ] Cash Flow: Net Income as starting point, adjustments, working capital changes
- [ ] Cash Flow: Opening + Net Change = Closing validation
- [ ] Cash Flow: Outflows in parentheses, red
- [ ] Consolidated P&L: dynamic company columns
- [ ] Consolidated P&L: elimination column
- [ ] Consolidated P&L: consolidated total matches sum + eliminations
- [ ] All CSS inline, no flexbox
- [ ] Fixed footer on every page
- [ ] Committed to wave-6-advanced-statements branch

**BEGIN AUTONOMOUS EXECUTION NOW.**
