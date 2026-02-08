# Wave 2 — Aging Reports: Aged Receivables + Aged Payables

## BEFORE YOU START
Read `00_MANDATORY_RULES.md` in this folder. Those rules override any conflicting patterns below.

## MISSION
Redesign the Aged Receivables and Aged Payables report templates to match OPS corporate branding standard (established by GL report redesign). Existing wizards and Python data layers exist — focus is on template rewrite + data layer enhancement.

**Duration**: 2.5 hours | **Mode**: Autonomous — fix errors, don't stop
**Branch**: `git checkout -b wave-2-aging-reports`
**DO NOT EDIT**: `__manifest__.py`, `__init__.py`, any GL or Wave 1 files

---

## PHASE 1: DISCOVERY (15 min)

```bash
echo "========================================"
echo "PHASE 1: DISCOVERY"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

# Find existing aged partner files
echo "=== Finding existing files ==="
find . -name "*aged*" -type f
find . -name "*aging*" -type f
grep -rl "aged.partner" --include="*.py" --include="*.xml" .
grep -rl "aged_partner" --include="*.py" --include="*.xml" .

# Check wizard
echo "=== Wizard model ==="
cat wizard/ops_aged_partner_wizard.py | head -50

# Check report class
echo "=== Report class ==="
find . -path "*/report/*aged*" -type f
find . -path "*/report/*" -name "*.py" | xargs grep -l "aged" 2>/dev/null

# Check existing template
echo "=== Existing template ==="
find . -name "*aged*" -path "*.xml" -type f

# Check report action
grep -rl "aged" data/ --include="*.xml" 2>/dev/null

echo "✅ Discovery complete — note all file paths"
```

**Record file paths found. Adapt subsequent phases to actual locations.**

---

## PHASE 2: AGED RECEIVABLES REPORT (60 min)

### 2.1 Report Specifications

| Attribute | Value |
|-----------|-------|
| **Orientation** | Portrait A4 |
| **Report ID Prefix** | `AR-` |
| **Grouping** | Flat — one row per partner |
| **Sort** | By total outstanding descending |

**Columns (7):**

| # | Column | Width | Align | Content |
|---|--------|-------|-------|---------|
| 1 | Partner | 28% | left | Partner name |
| 2 | Current | 12% | right | Not yet due |
| 3 | 1-30 | 12% | right | 1-30 days overdue |
| 4 | 31-60 | 12% | right | 31-60 days overdue |
| 5 | 61-90 | 12% | right | 61-90 days overdue |
| 6 | 90+ | 12% | right | Over 90 days overdue |
| 7 | Total | 12% | right | Sum of all buckets |

**Summary Row (3 metrics):**
- TOTAL OUTSTANDING: sum of all partner totals
- TOTAL OVERDUE: sum of 1-30 + 31-60 + 61-90 + 90+ buckets
- OVERDUE %: (Total Overdue / Total Outstanding) × 100

**Color Coding for Aging Buckets:**
- Current: green (#16a34a)
- 1-30: default text color
- 31-60: amber (#d97706)
- 61-90: orange (#ea580c)
- 90+: red (#dc2626)
- These colors apply to the COLUMN HEADER background, not cell text
- Cell text uses standard positive/negative/zero rules from mandatory rules

**Grand Total Row:**
- Primary color background, white text
- Shows: total for each bucket column + grand total

### 2.2 Python Data Layer Enhancement

In the existing report class (likely `report/ops_aged_partner_report.py` or similar), add:

```python
import random, string
from datetime import datetime

def _get_report_id(self, prefix='AR'):
    """Generate unique report ID: AR-YYYYMMDD-HHMMSS-XXXX"""
    now = datetime.now()
    rand = ''.join(random.choices(string.hexdigits[:16].upper(), k=4))
    return f"{prefix}-{now.strftime('%Y%m%d-%H%M%S')}-{rand}"

def _get_report_colors(self, company):
    """Get report color dict with fallbacks"""
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

Add these to the data dict passed to the template:
- `report_id`: generated report ID
- `colors`: color dict
- `print_date`: formatted current date (DD MMM YYYY)
- `total_outstanding`, `total_overdue`, `overdue_pct`: summary metrics

### 2.3 Template Rewrite

Create new template file. Follow the template skeleton from mandatory rules exactly:

1. `<style>` block (inline CSS — full report styles)
2. `<meta charset="UTF-8">`
3. Header (table: company info left | print date + report ID right)
4. Title: "Aged Receivables Report"
5. Subtitle: "As of [date] | Currency: [currency] | Branch: [branch or All]"
6. Summary row (table: 3 metrics)
7. Data table: column headers with aging bucket colors, one row per partner
8. Grand total row
9. Signature block (table: 3 columns)
10. Fixed footer (position: fixed)

**Bucket header color implementation:**
```html
<th style="text-align: right; padding: 8px 10px; font-size: 7.5pt; text-transform: uppercase; background: #dcfce7; color: #166534;">CURRENT</th>
<th style="text-align: right; padding: 8px 10px; font-size: 7.5pt; text-transform: uppercase;">1-30</th>
<th style="text-align: right; padding: 8px 10px; font-size: 7.5pt; text-transform: uppercase; background: #fef3c7; color: #92400e;">31-60</th>
<th style="text-align: right; padding: 8px 10px; font-size: 7.5pt; text-transform: uppercase; background: #fed7aa; color: #9a3412;">61-90</th>
<th style="text-align: right; padding: 8px 10px; font-size: 7.5pt; text-transform: uppercase; background: #fecaca; color: #991b1b;">90+</th>
```

---

## PHASE 3: AGED PAYABLES REPORT (45 min)

### 3.1 Report Specifications

Identical structure to Aged Receivables with these differences:

| Attribute | Value |
|-----------|-------|
| **Report ID Prefix** | `AP-` |
| **Title** | "Aged Payables Report" |
| **Data Source** | Payable accounts instead of receivable |

**Summary Row (3 metrics):**
- TOTAL PAYABLE: sum of all vendor totals
- TOTAL OVERDUE: sum of overdue buckets
- OVERDUE %: percentage

Everything else (columns, colors, template structure) is identical. Clone the AR template, change:
- Template ID
- Title string
- Report ID prefix
- Data source (payable accounts)

---

## PHASE 4: REPORT ACTIONS + PAPERFORMAT (15 min)

### 4.1 Create/Update Report Actions

For each report, ensure `ir.actions.report` record exists:

```xml
<record id="action_report_aged_receivables_redesign" model="ir.actions.report">
    <field name="name">Aged Receivables</field>
    <field name="model">ops.aged.partner.wizard</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">ops_matrix_accounting.report_aged_receivables_redesign</field>
    <field name="report_file">ops_matrix_accounting.report_aged_receivables_redesign</field>
    <field name="paperformat_id" ref="paperformat_ops_portrait"/>
    <field name="binding_type">report</field>
</record>
```

If `paperformat_ops_portrait` doesn't exist yet, create it per mandatory rules Rule 8.

### 4.2 Wire Wizard to New Template

Update the wizard's `action_generate` method to use the new report name. If wizard uses a `report_type` field to switch between AR/AP, preserve that logic.

---

## PHASE 5: VERIFY & COMMIT (15 min)

```bash
echo "========================================"
echo "PHASE 5: VERIFY & COMMIT"
echo "========================================"

# DO NOT update module — just verify syntax
echo "=== Checking Python syntax ==="
cd /opt/gemini_odoo19/addons/ops_matrix_accounting
python3 -m py_compile report/ops_aged_receivables_report.py 2>&1 || true
python3 -m py_compile report/ops_aged_payables_report.py 2>&1 || true

echo "=== Checking XML syntax ==="
python3 -c "
import xml.etree.ElementTree as ET
for f in ['report/ops_aged_receivables_template.xml', 'report/ops_aged_payables_template.xml']:
    try:
        ET.parse(f)
        print(f'✅ {f} — valid XML')
    except Exception as e:
        print(f'❌ {f} — {e}')
"

echo "=== Git commit ==="
cd /opt/gemini_odoo19
git add -A
git status
git commit -m "feat(accounting): Wave 2 — Aged Receivables + Aged Payables redesign

- Corporate branding template for Aged Receivables
- Corporate branding template for Aged Payables
- Color-coded aging bucket headers (green→red progression)
- Report ID generation (AR-/AP- prefix)
- Summary row with overdue percentage
- All CSS inline per wkhtmltopdf rules
- Fixed footer with OPS badge
- Table-based layouts (no flexbox)"

git push origin wave-2-aging-reports

echo "✅ Wave 2 committed to branch wave-2-aging-reports"
```

---

## FILES CREATED/MODIFIED

| File | Action |
|------|--------|
| `report/ops_aged_receivables_report.py` | Enhanced (report_id, colors, summary metrics) |
| `report/ops_aged_receivables_template.xml` | Rewritten (corporate branding) |
| `report/ops_aged_payables_report.py` | Enhanced (or same file if shared) |
| `report/ops_aged_payables_template.xml` | Rewritten (corporate branding) |
| `data/ops_report_paperformat.xml` | Created IF not exists |

**DO NOT EDIT:** `__manifest__.py`, `__init__.py`, any GL/Wave1 files

---

## SUCCESS CRITERIA

- [ ] AR template has 7 columns with colored bucket headers
- [ ] AP template mirrors AR with payable data
- [ ] Summary row shows Total, Overdue, Overdue %
- [ ] All CSS is inline (no external stylesheet links)
- [ ] No flexbox in any layout (tables only)
- [ ] Fixed footer with OPS badge on every page
- [ ] Report IDs: AR-YYYYMMDD-HHMMSS-XXXX / AP-YYYYMMDD-HHMMSS-XXXX
- [ ] HTML entities for special characters (no literal em dashes)
- [ ] Python syntax valid
- [ ] XML syntax valid
- [ ] Committed to wave-2-aging-reports branch

**BEGIN AUTONOMOUS EXECUTION NOW.**
