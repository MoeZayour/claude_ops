# Wave 3 — Financial Statements: P&L, Balance Sheet, Trial Balance

## BEFORE YOU START
Read `00_MANDATORY_RULES.md` in this folder. Those rules override any conflicting patterns below.

## MISSION
Redesign the three core financial statement templates (Profit & Loss, Balance Sheet, Trial Balance) to match OPS corporate branding standard. These are HIERARCHICAL reports — account groups nest under parent categories. Existing wizard (`ops.financial.report.wizard`) handles all three.

**Duration**: 4 hours | **Mode**: Autonomous — fix errors, don't stop
**Branch**: `git checkout -b wave-3-financial-statements`
**DO NOT EDIT**: `__manifest__.py`, `__init__.py`, any GL or other wave files

---

## PHASE 1: DISCOVERY (15 min)

```bash
echo "========================================"
echo "PHASE 1: DISCOVERY"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Finding financial report files ==="
find . -name "*financial*" -type f
find . -name "*profit*" -o -name "*pnl*" -o -name "*loss*" | grep -v __pycache__
find . -name "*balance_sheet*" -o -name "*bs_*" | grep -v __pycache__
find . -name "*trial_balance*" -o -name "*tb_*" | grep -v __pycache__
grep -rl "financial.report.wizard" --include="*.py" --include="*.xml" .

echo "=== Wizard model ==="
find . -name "*financial*wizard*" -path "*/wizard/*" | head -5
# Read first 80 lines of wizard
find . -name "*financial*wizard*" -path "*/wizard/*" -exec head -80 {} \;

echo "=== Report classes ==="
find . -path "*/report/*" -name "*.py" | xargs grep -l "financial\|profit\|balance.sheet\|trial.balance" 2>/dev/null

echo "=== Existing templates ==="
find . -name "*.xml" | xargs grep -l "financial_report\|profit_loss\|balance_sheet\|trial_balance" 2>/dev/null

echo "=== Report actions ==="
grep -rl "ir.actions.report" data/ --include="*.xml" | xargs grep -l "financial\|profit\|balance\|trial" 2>/dev/null

echo "✅ Discovery complete"
```

---

## PHASE 2: PROFIT & LOSS REPORT (75 min)

### 2.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Portrait A4 |
| **Report ID Prefix** | `PL-` |
| **Structure** | Hierarchical — account groups with subtotals |
| **Comparative** | Optional — current period vs prior period |

**Columns — Single Period (4):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Account | 55% | left | Account name (indented by level) |
| 2 | Code | 10% | left | Account code (leaf accounts only) |
| 3 | Amount | 20% | right | Period amount |
| 4 | % | 15% | right | % of Revenue |

**Columns — Comparative (6):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Account | 35% | left | Account name (indented by level) |
| 2 | Code | 8% | left | Account code |
| 3 | Current | 17% | right | Current period |
| 4 | Prior | 17% | right | Prior period |
| 5 | Variance | 13% | right | Current - Prior |
| 6 | Var % | 10% | right | Variance % |

**Hierarchical Structure:**
```
REVENUE                              ← Level 0 (section header, bold, primary bg)
  Sales Revenue                      ← Level 1 (group header, semibold)
    4001 - Product Sales     50,000  ← Level 2 (leaf account)
    4002 - Service Revenue   20,000  ← Level 2
  Total Sales Revenue        70,000  ← Level 1 subtotal (semibold, primary-light bg)
  Other Revenue                      ← Level 1
    4100 - Interest Income    1,000  ← Level 2
  Total Other Revenue         1,000  ← Level 1 subtotal
TOTAL REVENUE                71,000  ← Level 0 total (bold, primary bg, white text)

COST OF GOODS SOLD                   ← Level 0
  ...
TOTAL COGS                  (40,000) ← Level 0 total

═══════════════════════════════════
GROSS PROFIT                 31,000  ← Computed line (bold, large font, border top+bottom)
═══════════════════════════════════

OPERATING EXPENSES                   ← Level 0
  ...
TOTAL OPERATING EXPENSES    (15,000) ← Level 0 total

═══════════════════════════════════
OPERATING INCOME             16,000  ← Computed line
═══════════════════════════════════

OTHER INCOME / (EXPENSE)             ← Level 0
  ...
TOTAL OTHER                  (1,000)

═══════════════════════════════════
NET INCOME                   15,000  ← Final computed line (grand total style)
═══════════════════════════════════
```

**Styling Rules for Hierarchy:**

| Level | Font | Background | Left Padding |
|-------|------|------------|-------------|
| 0 — Section | 9pt, bold, uppercase | primary color, white text | 12px |
| 1 — Group | 8.5pt, semibold | none | 24px |
| 2 — Leaf | 8.5pt, regular | alternating (white/#f8fafc) | 36px |
| Subtotal (L1) | 8.5pt, semibold | primary-light | 24px |
| Total (L0) | 9pt, bold | primary, white text | 12px |
| Computed line (GP/OI/NI) | 10pt, bold | white, border-top 2px | 12px |

**Summary Row (3 metrics):**
- TOTAL REVENUE
- NET INCOME
- NET MARGIN % (Net Income / Revenue × 100)

**Value Colors:**
- Positive amounts: green (#16a34a)
- Negative amounts: red (#dc2626), shown in parentheses
- Zero: gray (#bbbbbb), show "&#x2014;"
- Variance positive: green
- Variance negative: red

### 2.2 Template Notes

- Account indentation via `padding-left` inline style based on level
- Section headers span full width (colspan)
- Computed lines (Gross Profit, Operating Income, Net Income) have `border-top: 2px solid` in primary color
- If comparative mode: show 6 columns; if single period: show 4 columns
- Use QWeb `t-if` for comparative toggle

---

## PHASE 3: BALANCE SHEET REPORT (60 min)

### 3.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Portrait A4 |
| **Report ID Prefix** | `BS-` |
| **Structure** | Hierarchical — same as P&L |
| **Validation** | Assets = Liabilities + Equity (must balance) |

**Columns — Single Period (3):**

| # | Column | Width | Align |
|---|--------|-------|-------|
| 1 | Account | 60% | left |
| 2 | Code | 10% | left |
| 3 | Balance | 30% | right |

**Columns — Comparative (5):**

| # | Column | Width | Align |
|---|--------|-------|-------|
| 1 | Account | 40% | left |
| 2 | Code | 8% | left |
| 3 | Current | 20% | right |
| 4 | Prior | 20% | right |
| 5 | Change % | 12% | right |

**Hierarchical Structure:**
```
ASSETS                               ← Level 0
  Current Assets                     ← Level 1
    1100 - Cash              50,000  ← Level 2
    1200 - Receivables       30,000
  Total Current Assets       80,000  ← Subtotal
  Non-Current Assets                 ← Level 1
    1500 - Equipment         40,000
    1510 - Accum. Depr.     (10,000)
  Total Non-Current Assets   30,000
TOTAL ASSETS                110,000  ← Level 0 total

═══════════════════════════════════

LIABILITIES                          ← Level 0
  Current Liabilities                ← Level 1
    2100 - Payables          20,000
  Total Current Liabilities  20,000
  Non-Current Liabilities            ← Level 1
    2500 - Long-term Debt    40,000
  Total Non-Current          40,000
TOTAL LIABILITIES            60,000

EQUITY                               ← Level 0
  3000 - Share Capital       30,000
  3100 - Retained Earnings   20,000
TOTAL EQUITY                 50,000

═══════════════════════════════════
TOTAL LIABILITIES + EQUITY  110,000  ← Must equal Total Assets
═══════════════════════════════════
```

**Balance Check:**
If Total Assets = Total L+E → show green "Balanced" indicator
If not → show red "UNBALANCED" warning with difference amount

**Summary Row (3 metrics):**
- TOTAL ASSETS
- TOTAL LIABILITIES
- TOTAL EQUITY

---

## PHASE 4: TRIAL BALANCE REPORT (45 min)

### 4.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Landscape A4 |
| **Report ID Prefix** | `TB-` |
| **Structure** | Flat — one row per account (NO hierarchy) |
| **Grouping** | Optional group by account type |

**Columns (8):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Code | 8% | left | Account code |
| 2 | Account | 24% | left | Account name |
| 3 | Opening Dr | 10% | right | Opening debit balance |
| 4 | Opening Cr | 10% | right | Opening credit balance |
| 5 | Period Dr | 12% | right | Debit movements in period |
| 6 | Period Cr | 12% | right | Credit movements in period |
| 7 | Closing Dr | 12% | right | Closing debit balance |
| 8 | Closing Cr | 12% | right | Closing credit balance |

**Summary Row (3 metrics):**
- TOTAL DEBIT: sum of closing debit column
- TOTAL CREDIT: sum of closing credit column
- DIFFERENCE: should be 0.00 (green if balanced, red if not)

**Grand Total Row:**
Each numeric column shows its sum. Opening Dr = Opening Cr, Period Dr = Period Cr, Closing Dr = Closing Cr.

**Special Rules:**
- Zero rows: optionally hidden (wizard checkbox "Include zero balances")
- Alternating row colors: white / #f8fafc
- Column headers span Opening/Period/Closing as grouped headers:

```
Code | Account | ← Opening →  | ← Period →   | ← Closing →
                | Debit | Credit | Debit | Credit | Debit | Credit
```

Use a two-row header: top row has merged cells for "Opening", "Period", "Closing". Bottom row has individual "Debit"/"Credit" labels.

### 4.2 Paperformat

Trial Balance uses landscape: reference `paperformat_ops_landscape`. If doesn't exist, create per mandatory rules.

---

## PHASE 5: PYTHON DATA LAYER (30 min)

### 5.1 Shared Report Helpers

Add to each report's `_get_report_values()` method:

```python
# Report metadata
report_id = self._get_report_id(prefix)  # PL-, BS-, TB-
colors = self._get_report_colors(wizard.company_id)
print_date = fields.Datetime.now().strftime('%d %b %Y')

# Add to values dict
values.update({
    'report_id': report_id,
    'colors': colors,
    'print_date': print_date,
    'company': wizard.company_id,
})
```

### 5.2 P&L Specific

Ensure data dict includes:
- `lines`: list of dicts with `name`, `code`, `level` (0/1/2), `type` ('section'/'group'/'account'/'subtotal'/'total'/'computed'), `amount`, `prior_amount` (if comparative), `variance`, `variance_pct`, `pct_of_revenue`
- `total_revenue`, `net_income`, `net_margin_pct`
- `is_comparative`: boolean

### 5.3 BS Specific

Ensure data dict includes:
- `lines`: same structure as P&L but for BS sections
- `total_assets`, `total_liabilities`, `total_equity`
- `is_balanced`: boolean (assets == liabilities + equity)
- `balance_diff`: difference amount if unbalanced

### 5.4 TB Specific

Ensure data dict includes:
- `accounts`: list of dicts with `code`, `name`, `opening_debit`, `opening_credit`, `period_debit`, `period_credit`, `closing_debit`, `closing_credit`
- `totals`: dict with sums for each column
- `is_balanced`: boolean (closing_debit == closing_credit)

---

## PHASE 6: VERIFY & COMMIT (15 min)

```bash
echo "========================================"
echo "PHASE 6: VERIFY & COMMIT"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Python syntax check ==="
find report/ -name "*financial*" -o -name "*profit*" -o -name "*balance*" -o -name "*trial*" | grep "\.py$" | while read f; do
    python3 -m py_compile "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"
done

echo "=== XML syntax check ==="
find report/ -name "*profit*" -o -name "*balance*" -o -name "*trial*" | grep "\.xml$" | while read f; do
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('$f'); print('✅ $f')" 2>&1 || echo "❌ $f"
done

echo "=== Git commit ==="
cd /opt/gemini_odoo19
git add -A
git status
git commit -m "feat(accounting): Wave 3 — P&L, Balance Sheet, Trial Balance redesign

- Hierarchical P&L with 4-level indentation and computed lines
- Balance Sheet with balance validation indicator
- Trial Balance with 8-column Opening/Period/Closing structure
- Two-row grouped column headers for TB
- Comparative mode support for P&L and BS
- Report ID generation (PL-/BS-/TB- prefixes)
- All CSS inline, table-based layouts
- Fixed footer with OPS badge"

git push origin wave-3-financial-statements

echo "✅ Wave 3 committed to branch wave-3-financial-statements"
```

---

## FILES CREATED/MODIFIED

| File | Action |
|------|--------|
| `report/ops_profit_loss_template.xml` | Rewritten |
| `report/ops_balance_sheet_template.xml` | Rewritten |
| `report/ops_trial_balance_template.xml` | Rewritten |
| `report/ops_financial_report.py` | Enhanced (report_id, colors, hierarchy processing) |

**DO NOT EDIT:** `__manifest__.py`, `__init__.py`, any other wave files

---

## SUCCESS CRITERIA

- [ ] P&L has 4-level hierarchy with proper indentation
- [ ] P&L computed lines (Gross Profit, Operating Income, Net Income) have border separators
- [ ] BS validates Assets = L + E and shows indicator
- [ ] TB has two-row grouped headers (Opening/Period/Closing × Debit/Credit)
- [ ] TB uses landscape orientation
- [ ] Comparative columns work when enabled
- [ ] All CSS inline, no flexbox, table-based layouts
- [ ] Fixed footer on every page
- [ ] Report IDs: PL-/BS-/TB- prefixes
- [ ] HTML entities for special characters
- [ ] Committed to wave-3-financial-statements branch

**BEGIN AUTONOMOUS EXECUTION NOW.**
