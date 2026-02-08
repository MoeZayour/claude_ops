# Wave 4 — Register Reports: Asset Register, PDC Registry, PDC Maturity

## BEFORE YOU START
Read `00_MANDATORY_RULES.md` in this folder. Those rules override any conflicting patterns below.

## MISSION
Redesign the Asset Register, PDC Registry, and PDC Maturity report templates to match OPS corporate branding standard. These are FLAT LIST reports (no hierarchical nesting) — simpler template structure than financial statements.

**Duration**: 3 hours | **Mode**: Autonomous — fix errors, don't stop
**Branch**: `git checkout -b wave-4-register-reports`
**DO NOT EDIT**: `__manifest__.py`, `__init__.py`, any GL or other wave files

---

## PHASE 1: DISCOVERY (15 min)

```bash
echo "========================================"
echo "PHASE 1: DISCOVERY"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Finding asset report files ==="
find . -name "*asset*register*" -o -name "*asset*report*" | grep -v __pycache__
grep -rl "asset.register" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== Finding PDC report files ==="
find . -name "*pdc*report*" -o -name "*pdc*registry*" -o -name "*pdc*maturity*" | grep -v __pycache__
grep -rl "pdc.report\|pdc_report\|pdc_registry\|pdc_maturity" --include="*.py" --include="*.xml" . 2>/dev/null

echo "=== Wizards ==="
cat wizard/ops_asset_register_wizard.py 2>/dev/null | head -50
cat wizard/ops_pdc_report_wizard.py 2>/dev/null | head -50

echo "=== Report classes ==="
find . -path "*/report/*" -name "*.py" | xargs grep -l "asset\|pdc" 2>/dev/null

echo "=== Templates ==="
find . -name "*.xml" | xargs grep -l "asset_register\|pdc_registry\|pdc_maturity" 2>/dev/null

echo "✅ Discovery complete"
```

---

## PHASE 2: ASSET REGISTER REPORT (60 min)

### 2.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Landscape A4 |
| **Report ID Prefix** | `AST-` |
| **Grouping** | Grouped by Asset Category |
| **Sort** | By asset name within category |

**Columns (9):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Code | 7% | left | Asset reference |
| 2 | Asset Name | 18% | left | Asset description |
| 3 | Category | 10% | left | Asset category |
| 4 | Purchase Date | 9% | center | DD MMM YYYY |
| 5 | Original Cost | 12% | right | Purchase value |
| 6 | Accum. Depreciation | 12% | right | Total depreciation to date |
| 7 | Book Value | 12% | right | Cost - Accum. Dep |
| 8 | Method | 8% | center | SL / DB / DL |
| 9 | Status | 12% | center | Badge: Running/Paused/Sold/Disposed |

**Status Badges:**
- Running: green bg (#dcfce7), green text (#166534)
- Paused: amber bg (#fef3c7), amber text (#92400e)
- Sold: blue bg (#dbeafe), blue text (#1e40af)
- Disposed: gray bg (#f1f5f9), gray text (#64748b)
- Draft: light gray bg (#f8fafc), gray text (#94a3b8)

Badge implementation (inline styles, no external CSS):
```html
<span style="padding: 2px 8px; border-radius: 4px; font-size: 7pt; font-weight: 600;
             background: #dcfce7; color: #166534; text-transform: uppercase;">RUNNING</span>
```

**Category Group Header:**
Same as GL account header — primary-light bg, 4px left border in primary color. Shows:
- Category name
- Count of assets in category

**Category Subtotal Row:**
Primary-light bg, shows: Total Cost, Total Accum. Dep, Total Book Value for that category.

**Summary Row (3 metrics):**
- TOTAL ASSETS: count of all assets
- TOTAL COST: sum of original cost
- NET BOOK VALUE: sum of book values

**Grand Total Row:**
Primary bg, white text — totals for Cost, Accum. Dep, Book Value columns.

### 2.2 Depreciation Method Labels

| Value in DB | Display |
|-------------|---------|
| straight_line | SL |
| declining_balance | DB |
| degressive_then_linear | DL |

---

## PHASE 3: PDC REGISTRY REPORT (50 min)

### 3.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Portrait A4 |
| **Report ID Prefix** | `PDC-` |
| **Grouping** | Grouped by Status |
| **Data Source** | Both receivable and payable PDCs (wizard selects) |

**Columns (8):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | PDC No | 10% | left | PDC reference number |
| 2 | Type | 6% | center | R (Receivable) / P (Payable) |
| 3 | Date | 10% | center | Issue date (DD MMM YYYY) |
| 4 | Partner | 20% | left | Customer/Vendor name |
| 5 | Check No | 10% | left | Check number |
| 6 | Bank | 12% | left | Bank name |
| 7 | Amount | 14% | right | PDC amount |
| 8 | Due Date | 10% | center | Maturity date |

**Wizard should provide status filter option:**
- All statuses
- Specific status (draft/registered/deposited/cleared/bounced/cancelled)

**Status Group Headers:**
Same style as account headers — primary-light bg, left border. Status name + count.

Status colors for group header left border:
- Draft: gray (#94a3b8)
- Registered: blue (#3b82f6)
- Deposited: amber (#d97706)
- Cleared: green (#16a34a)
- Bounced: red (#dc2626)
- Cancelled: gray (#cbd5e1)

**Status Subtotal:** Count + total amount per status.

**Summary Row (3 metrics):**
- TOTAL PDCs: total count
- TOTAL AMOUNT: sum of all amounts
- ACTIVE: count of non-cancelled/non-cleared

**Grand Total Row:**
Primary bg, white text. Total count + total amount.

---

## PHASE 4: PDC MATURITY REPORT (40 min)

### 4.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Portrait A4 |
| **Report ID Prefix** | `PDCM-` |
| **Grouping** | Grouped by Month (of due date) |
| **Sort** | By due date ascending |
| **Data Filter** | Only active PDCs (not cancelled/cleared) |

**Columns (6):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | PDC No | 12% | left | Reference number |
| 2 | Type | 8% | center | Receivable / Payable |
| 3 | Partner | 25% | left | Customer/Vendor |
| 4 | Amount | 20% | right | PDC amount |
| 5 | Due Date | 15% | center | DD MMM YYYY |
| 6 | Days | 10% | center | Days until maturity (or overdue) |

**Days Column Color Coding:**
- Overdue (negative): red (#dc2626), show as "X days overdue"
- Due this week (0-7): amber (#d97706)
- Due this month (8-30): default text color
- Future (31+): green (#16a34a)

**Month Group Headers:**
Show month name + year (e.g., "February 2026"). Subtotal shows count + amount.

Overdue PDCs grouped under "OVERDUE" header at the top with red left border.

**Summary Row (4 metrics):**
- TOTAL MATURING: total count
- TOTAL AMOUNT: sum
- THIS MONTH: amount maturing this month
- OVERDUE: amount already past due (red if > 0)

---

## PHASE 5: PYTHON DATA LAYER (20 min)

Add to each report class:

```python
def _get_report_id(self, prefix):
    import random, string
    from datetime import datetime
    now = datetime.now()
    rand = ''.join(random.choices(string.hexdigits[:16].upper(), k=4))
    return f"{prefix}-{now.strftime('%Y%m%d-%H%M%S')}-{rand}"

def _get_report_colors(self, company):
    primary = getattr(company, 'ops_report_primary_color', None) or '#5B6BBB'
    h = primary.lstrip('#')
    r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    return {
        'primary': primary,
        'primary_light': '#{:02x}{:02x}{:02x}'.format(int(r*0.15+255*0.85), int(g*0.15+255*0.85), int(b*0.15+255*0.85)),
        'primary_dark': '#{:02x}{:02x}{:02x}'.format(int(r*0.75), int(g*0.75), int(b*0.75)),
        'text_on_primary': getattr(company, 'ops_report_text_on_primary', None) or '#FFFFFF',
        'body_text': getattr(company, 'ops_report_body_text_color', None) or '#1a1a1a',
    }
```

For PDC Maturity, compute `days_to_maturity` in Python:
```python
from datetime import date
days = (pdc.due_date - date.today()).days  # negative = overdue
```

---

## PHASE 6: REPORT ACTIONS + PAPERFORMAT (10 min)

- Asset Register → `paperformat_ops_landscape`
- PDC Registry → `paperformat_ops_portrait`
- PDC Maturity → `paperformat_ops_portrait`

Create paperformat records if they don't exist yet (check first).

---

## PHASE 7: VERIFY & COMMIT (15 min)

```bash
echo "========================================"
echo "PHASE 7: VERIFY & COMMIT"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Syntax checks ==="
for f in $(find report/ -name "*asset_register*" -o -name "*pdc_registry*" -o -name "*pdc_maturity*" | grep "\.py$"); do
    python3 -m py_compile "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"
done

for f in $(find report/ -name "*asset_register*" -o -name "*pdc_registry*" -o -name "*pdc_maturity*" | grep "\.xml$"); do
    python3 -c "import xml.etree.ElementTree as ET; ET.parse('$f'); print('✅ ' + '$f')" 2>&1 || echo "❌ $f"
done

echo "=== Git commit ==="
cd /opt/gemini_odoo19
git add -A
git commit -m "feat(accounting): Wave 4 — Asset Register, PDC Registry, PDC Maturity redesign

- Asset Register: landscape, grouped by category, status badges
- PDC Registry: grouped by status with colored left borders
- PDC Maturity: grouped by month, days-to-maturity color coding
- Report ID generation (AST-/PDC-/PDCM- prefixes)
- All CSS inline, table-based layouts
- Fixed footer with OPS badge"

git push origin wave-4-register-reports

echo "✅ Wave 4 committed to branch wave-4-register-reports"
```

---

## FILES CREATED/MODIFIED

| File | Action |
|------|--------|
| `report/ops_asset_register_template.xml` | Rewritten |
| `report/ops_asset_register_report.py` | Enhanced |
| `report/ops_pdc_registry_template.xml` | Rewritten |
| `report/ops_pdc_maturity_template.xml` | Rewritten |
| `report/ops_pdc_report.py` | Enhanced |

**DO NOT EDIT:** `__manifest__.py`, `__init__.py`, any other wave files

---

## SUCCESS CRITERIA

- [ ] Asset Register: 9 columns, landscape, status badges with colored backgrounds
- [ ] PDC Registry: 8 columns, grouped by status, colored left borders per status
- [ ] PDC Maturity: 6 columns, grouped by month, days color coding
- [ ] Overdue PDCs highlighted at top of maturity report
- [ ] All CSS inline, no flexbox
- [ ] Fixed footer on every page
- [ ] Report IDs with correct prefixes
- [ ] HTML entities for special characters
- [ ] Committed to wave-4-register-reports branch

**BEGIN AUTONOMOUS EXECUTION NOW.**
