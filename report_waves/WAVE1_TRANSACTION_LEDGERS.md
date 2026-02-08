# Wave 1 — Transaction Ledger Reports: BS Corporate Theme

## MISSION
Apply the BS corporate design system to all 4 remaining transaction ledger reports: Cash Book, Day Book, Bank Book, and Partner Ledger. These reuse the CSS and shared components deployed by the GL redesign prompt. Each report gets a full template rewrite + Python data layer update.

**Duration**: 5 hours | **Mode**: Autonomous — fix errors, don't stop

---

## MULTI-AGENT STRATEGY

> **NOTE TO CLAUDE CODE**: This prompt contains 4 independent report rewrites (Phases 2–5). Each touches DIFFERENT Python files and DIFFERENT XML template files. Use **multiple sub-agents in parallel** for maximum speed:
>
> - **Agent A**: Cash Book (Phase 2) then Bank Book (Phase 4) — these share journal-based patterns
> - **Agent B**: Day Book (Phase 3) then Partner Ledger (Phase 5) — these are structurally different
> - **Main Agent**: Phase 1 (pre-flight + shared CSS), Phase 6 (wizard cleanup), Phase 7 (manifest + test + commit)
>
> All agents share the same design system and CSS classes. Coordinate on `ops_internal_report.css` additions (Phase 1 must complete before agents start).

---

## ARCHITECTURE CONTEXT

### What Already Exists (from GL Redesign)
The GL prompt (running separately) creates these shared resources:

| Resource | Location | Status |
|----------|----------|--------|
| Badge PNG | `ops_matrix_accounting/static/src/img/ops_badge_footer.png` | Created by GL prompt |
| Report CSS | `ops_matrix_accounting/static/src/css/ops_internal_report.css` | Created by GL prompt |
| Company fields | `ops_report_primary_color`, `ops_report_text_on_primary`, `ops_report_body_text_color` | Created by GL prompt |
| Helper methods | `get_report_primary_light()`, `get_report_primary_dark()` | Created by GL prompt |
| In-page footer | `ops_matrix_accounting.report_corporate_in_page_footer` template | Created by GL prompt |
| Account type badges | CSS classes `.badge-asset`, `.badge-liability`, etc. | In report CSS |

### What This Prompt Creates
4 complete report template rewrites + Python data layer updates. NO new CSS files — we ADD report-specific column widths to the existing `ops_internal_report.css`.

### Design System (Identical to GL)
- Colors: Dynamic from `company.ops_report_primary_color` (default `#5B6BBB`)
- Font: Inter, 8.5pt body, 16pt title, 9pt section headers, 7pt table headers
- Value formatting: Green positive (`#16a34a`), Red negative (`#dc2626`), Gray zero (`#bbbbbb`)
- Negative values: Parentheses `(1,234.56)`
- Zero in transaction rows: Em dash `—`
- Zero in total rows: `0.00` with `.zero` class
- Tables: No borders, alternating rows (`#f8fafc`), tabular-nums
- Sections: Primary-light bg + 4px primary left border
- Footer: In-page badge + wkhtmltopdf page numbers only
- Signature block + verification indicator + confidentiality notice on all reports

---

## REPORT SPECIFICATIONS

### Report 1: Cash Book
| Property | Value |
|----------|-------|
| **Orientation** | Portrait A4 |
| **Grouped by** | Cash/Bank Account |
| **Filter** | Cash + Bank type journals only |
| **Opening balance** | Yes — per account |
| **Running balance** | Yes — per account |
| **Summary metrics** | Total Receipts, Total Payments, Net Cash Movement |
| **Report ID prefix** | `CB-` |

**Columns (7 — portrait fits):**

| Column | Width | Align | Content |
|--------|-------|-------|---------|
| Date | 10% | left | Transaction date, DD Mon YYYY |
| Reference | 15% | left | Move reference (INV/2026/0001) |
| Partner | 18% | left | Partner name, truncate |
| Description | 25% | left | Move line name, deduped |
| Receipts | 11% | right | Debit amount (money in) |
| Payments | 11% | right | Credit amount (money out) |
| Balance | 10% | right | Running balance, color-coded |

**Section header**: Account code + name (e.g. "101001 — Cash on Hand"). No type badge (all are asset/cash type).

**Account total label**: `Total 101001 (N transactions)`

---

### Report 2: Day Book
| Property | Value |
|----------|-------|
| **Orientation** | Portrait A4 |
| **Grouped by** | Date (primary), then Journal within date |
| **Filter** | All journals, date range |
| **Opening balance** | No — it's a daily transaction register |
| **Running balance** | No — shows daily totals only |
| **Summary metrics** | Total Debit, Total Credit, Transaction Count |
| **Report ID prefix** | `DB-` |

**Columns (7 — portrait fits):**

| Column | Width | Align | Content |
|--------|-------|-------|---------|
| Journal | 8% | left | Journal code (INV, BNK, etc.) |
| Account | 12% | left | Account code + short name |
| Partner | 16% | left | Partner name, truncate |
| Reference | 14% | left | Move reference |
| Description | 24% | left | Line description |
| Debit | 13% | right | Debit amount |
| Credit | 13% | right | Credit amount |

**Section header**: Date formatted as "Wednesday, 15 January 2026" with transaction count badge.

**Date total label**: `Total 15 Jan 2026 (N entries)`

**Key difference**: No Balance column. No opening balance rows. Grouped by date, not account.

---

### Report 3: Bank Book
| Property | Value |
|----------|-------|
| **Orientation** | Portrait A4 |
| **Grouped by** | Bank Account |
| **Filter** | Bank type journals only |
| **Opening balance** | Yes — per bank account |
| **Running balance** | Yes — per bank account |
| **Summary metrics** | Total Deposits, Total Withdrawals, Net Bank Movement |
| **Report ID prefix** | `BK-` |

**Columns (7 — portrait fits):**

| Column | Width | Align | Content |
|--------|-------|-------|---------|
| Date | 10% | left | Transaction date |
| Reference | 15% | left | Move reference |
| Partner | 18% | left | Partner name |
| Description | 25% | left | Line description |
| Deposits | 11% | right | Debit amount (money in) |
| Withdrawals | 11% | right | Credit amount (money out) |
| Balance | 10% | right | Running balance |

**Virtually identical to Cash Book** but filtered to bank journals only. Section headers show bank name and account number.

**Section header**: "101002 — National Bank USD" with bank icon (if available) or just the code+name.

---

### Report 4: Partner Ledger
| Property | Value |
|----------|-------|
| **Orientation** | Landscape A4 |
| **Grouped by** | Partner |
| **Filter** | Receivable + Payable accounts (configurable) |
| **Opening balance** | Yes — per partner |
| **Running balance** | Yes — per partner |
| **Summary metrics** | Total Debit, Total Credit, Net Balance |
| **Report ID prefix** | `PL-` |

**Columns (8 — landscape needed):**

| Column | Width | Align | Content |
|--------|-------|-------|---------|
| Date | 8% | left | Transaction date |
| Journal | 7% | left | Journal code |
| Account | 12% | left | Account code |
| Reference | 13% | left | Move reference |
| Description | 24% | left | Line description |
| Debit | 12% | right | Debit amount |
| Credit | 12% | right | Credit amount |
| Balance | 12% | right | Running balance |

**Section header**: Partner name with partner type badge:
- Customer (receivable): Blue badge
- Vendor (payable): Amber badge  
- Both: Purple badge

**Partner total label**: `Total Azure Interior (N transactions)`

---

## PHASE 1: PRE-FLIGHT + SHARED CSS (15 min)

### Task 1.1: Verify GL Dependencies Exist

```bash
echo "========================================"
echo "PHASE 1: PRE-FLIGHT + SHARED CSS"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Checking GL prerequisites ==="

# Badge
if [ -f static/src/img/ops_badge_footer.png ]; then
    echo "✅ Badge PNG exists"
else
    echo "❌ Badge PNG MISSING — run GL prompt first or generate now"
    # Fallback: generate badge
    mkdir -p static/src/img
    python3 << 'PYEOF'
from PIL import Image, ImageDraw, ImageFont

width, height, radius = 240, 40, 8
r1, g1, b1 = 0x3b, 0x82, 0xf6
r2, g2, b2 = 0x1e, 0x40, 0xaf

gradient = Image.new('RGBA', (width, height), (0,0,0,0))
for x in range(width):
    t = x / (width - 1)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    for y in range(height):
        gradient.putpixel((x, y), (r, g, b, 255))

mask = Image.new('L', (width, height), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, width-1, height-1], radius=radius, fill=255)
img = Image.composite(gradient, Image.new('RGBA', (width, height), (0,0,0,0)), mask)

draw = ImageDraw.Draw(img)
font = None
for fp in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
           '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']:
    try:
        font = ImageFont.truetype(fp, 16)
        break
    except: pass
if not font:
    font = ImageFont.load_default()

text = "OPS FRAMEWORK"
bbox = draw.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
x = (width - tw) // 2
y = (height - th) // 2 - 2
draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

img.save('static/src/img/ops_badge_footer.png')
print("✅ Badge generated")
PYEOF
fi

# CSS
if [ -f static/src/css/ops_internal_report.css ]; then
    echo "✅ Report CSS exists"
    wc -l static/src/css/ops_internal_report.css
else
    echo "❌ Report CSS MISSING — this is critical"
    echo "The GL prompt must run first to create the base CSS."
    echo "We will create a minimal version and the GL prompt will overwrite it."
fi

# Company fields
docker exec gemini_odoo19 python3 -c "
import xmlrpc.client
db, uid, pwd = 'mz-db', 2, 'admin'
models = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
fields = models.execute_kw(db, uid, pwd, 'res.company', 'fields_get', [], {'attributes': ['string'], 'filter': [['name', 'like', 'ops_report_']]})
if fields:
    print('✅ Report color fields exist:', list(fields.keys()))
else:
    print('⚠️ Report color fields not yet created — GL prompt will add them')
" 2>/dev/null || echo "⚠️ Could not check fields via RPC"

# In-page footer template
grep -l "report_corporate_in_page_footer" report/*.xml 2>/dev/null && echo "✅ In-page footer template exists" || echo "⚠️ In-page footer template not found — will create fallback"

echo "✅ Task 1.1 complete"
```

### Task 1.2: Add Report-Specific Column Width CSS

Append column width classes for all 4 reports to `ops_internal_report.css`. These are additive — do NOT replace existing content.

```bash
echo "=== Adding report-specific CSS ==="

cat >> static/src/css/ops_internal_report.css << 'CSSEOF'

/* ================================================================
   CASH BOOK — Portrait, 7 columns
   ================================================================ */
.ops-report.cashbook .col-date { width: 10%; }
.ops-report.cashbook .col-ref { width: 15%; }
.ops-report.cashbook .col-partner { width: 18%; }
.ops-report.cashbook .col-desc { width: 25%; }
.ops-report.cashbook .col-receipts { width: 11%; }
.ops-report.cashbook .col-payments { width: 11%; }
.ops-report.cashbook .col-balance { width: 10%; }

/* ================================================================
   DAY BOOK — Portrait, 7 columns, no balance
   ================================================================ */
.ops-report.daybook .col-jrnl { width: 8%; }
.ops-report.daybook .col-account { width: 12%; }
.ops-report.daybook .col-partner { width: 16%; }
.ops-report.daybook .col-ref { width: 14%; }
.ops-report.daybook .col-desc { width: 24%; }
.ops-report.daybook .col-debit { width: 13%; }
.ops-report.daybook .col-credit { width: 13%; }

/* Day Book date section header */
.ops-report.daybook .date-section-header {
    font-size: 10pt;
    font-weight: 700;
    padding: 10px 12px 6px;
    margin-top: 18px;
    color: #1e293b;
}

.ops-report.daybook .date-section-header .day-name {
    font-weight: 400;
    color: #64748b;
}

.ops-report.daybook .date-section-header .txn-count {
    font-size: 7.5pt;
    font-weight: 500;
    color: #94a3b8;
    margin-left: 8px;
}

/* ================================================================
   BANK BOOK — Portrait, 7 columns (same as Cash Book structure)
   ================================================================ */
.ops-report.bankbook .col-date { width: 10%; }
.ops-report.bankbook .col-ref { width: 15%; }
.ops-report.bankbook .col-partner { width: 18%; }
.ops-report.bankbook .col-desc { width: 25%; }
.ops-report.bankbook .col-deposits { width: 11%; }
.ops-report.bankbook .col-withdrawals { width: 11%; }
.ops-report.bankbook .col-balance { width: 10%; }

/* ================================================================
   PARTNER LEDGER — Landscape, 8 columns
   ================================================================ */
.ops-report.partner-ledger .col-date { width: 8%; }
.ops-report.partner-ledger .col-jrnl { width: 7%; }
.ops-report.partner-ledger .col-account { width: 12%; }
.ops-report.partner-ledger .col-ref { width: 13%; }
.ops-report.partner-ledger .col-desc { width: 24%; }
.ops-report.partner-ledger .col-debit { width: 12%; }
.ops-report.partner-ledger .col-credit { width: 12%; }
.ops-report.partner-ledger .col-balance { width: 12%; }

/* Partner type badges */
.ops-report .badge-customer { background: #dbeafe; color: #1e40af; }
.ops-report .badge-vendor { background: #fef3c7; color: #92400e; }
.ops-report .badge-both { background: #f3e8ff; color: #6b21a8; }

CSSEOF

echo "✅ Task 1.2 complete"
```

### Task 1.3: Create Shared In-Page Footer (if not yet created by GL prompt)

Check if the shared footer template exists. If not, create it so all reports can use it.

```bash
echo "=== Checking/creating shared footer component ==="

if grep -q "report_corporate_in_page_footer" report/*.xml 2>/dev/null; then
    echo "✅ Shared footer already exists"
else
    echo "Creating shared footer component..."
    # This will be created/appended to ops_corporate_report_components.xml
    # or whichever file the GL prompt uses for shared components.
    # Find the right file:
    ls report/ops_corporate* 2>/dev/null || echo "No corporate components file yet"
    
    # Create it if missing
    if [ ! -f report/ops_corporate_report_components.xml ]; then
        cat > report/ops_corporate_report_components.xml << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Shared in-page branded footer — all internal reports call this -->
    <template id="report_corporate_in_page_footer" name="OPS In-Page Branded Footer">
        <div class="report-footer">
            <div class="footer-branding">
                <span class="powered-by">Powered by</span>
                <img src="/ops_matrix_accounting/static/src/img/ops_badge_footer.png"
                     width="120" height="20"
                     alt="OPS Framework"
                     style="vertical-align: middle;"/>
            </div>
        </div>
    </template>
    
    <!-- Shared verification indicator -->
    <template id="report_verification_block" name="OPS Report Verification Block">
        <t t-set="is_balanced" t-value="abs(net_balance) &lt; 0.01"/>
        <div t-attf-class="verification-block #{is_balanced and 'balanced' or 'unbalanced'}"
             t-attf-style="border-left: 4px solid #{is_balanced and '#16a34a' or '#dc2626'}; background: #{is_balanced and '#f0fdf4' or '#fef2f2'};">
            <div class="verification-inner">
                <span t-if="is_balanced" class="verification-icon" style="color: #16a34a;">✓</span>
                <span t-else="" class="verification-icon" style="color: #dc2626;">✗</span>
                <div class="verification-text">
                    <div class="verification-title" t-attf-style="color: #{is_balanced and '#166534' or '#991b1b'};">
                        <t t-if="is_balanced">Report Balanced</t>
                        <t t-else="">Balance Discrepancy</t>
                    </div>
                    <div class="verification-detail" style="color: #64748b; font-size: 7pt;">
                        <t t-if="is_balanced">Total debits equal total credits. Net difference: 0.00</t>
                        <t t-else="">
                            Net difference: <t t-esc="'%.2f' % abs(net_balance)"/>
                            — Requires investigation
                        </t>
                    </div>
                </div>
            </div>
        </div>
    </template>
    
    <!-- Shared signature block -->
    <template id="report_signature_block" name="OPS Report Signature Block">
        <div class="signature-block">
            <div class="sig-col">
                <div class="sig-line"></div>
                <div class="sig-label">Prepared by</div>
                <div class="sig-sublabel">Date: _______________</div>
            </div>
            <div class="sig-divider"></div>
            <div class="sig-col">
                <div class="sig-line"></div>
                <div class="sig-label">Reviewed by</div>
                <div class="sig-sublabel">Date: _______________</div>
            </div>
            <div class="sig-divider"></div>
            <div class="sig-col">
                <div class="sig-line"></div>
                <div class="sig-label">Approved by</div>
                <div class="sig-sublabel">Date: _______________</div>
            </div>
        </div>
    </template>
    
    <!-- Shared confidentiality notice -->
    <template id="report_confidentiality_notice" name="OPS Report Confidentiality">
        <div class="confidentiality-notice">
            CONFIDENTIAL — This document contains proprietary financial information.
            Unauthorized distribution is strictly prohibited.
        </div>
    </template>
</odoo>
XMLEOF
        echo "✅ Created ops_corporate_report_components.xml"
        
        # Add to manifest data if not present
        if ! grep -q "ops_corporate_report_components.xml" __manifest__.py; then
            echo "Adding components file to manifest..."
            # This needs careful insertion — add to the 'data' list
        fi
    fi
fi

echo "✅ Task 1.3 complete"
```

**Verify Phase 1:**
```bash
wc -l static/src/css/ops_internal_report.css
ls -la static/src/img/ops_badge_footer.png
grep "report_corporate_in_page_footer" report/*.xml | head -3
echo "✅ PHASE 1 COMPLETE — Agents can now proceed in parallel"
```

---

## PHASE 2: CASH BOOK — Template + Python (60 min)

> **Can run in parallel** with Phases 3–5. Touches: `wizard/ops_cash_book_wizard*.py`, `report/ops_cash_book*`

### Task 2.1: Audit Current Cash Book Structure

```bash
echo "========================================"
echo "PHASE 2: CASH BOOK REDESIGN"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Cash Book files ==="
find . -name "*cash_book*" -o -name "*cashbook*" | sort

echo "=== Wizard structure ==="
grep -n "class \|def \|_name\|_description" wizard/ops_cash_book_wizard*.py 2>/dev/null | head -30

echo "=== Report Python ==="
find . -path "*/report/*" -name "*cash*" | sort
grep -n "class \|def \|_name\|_description" report/ops_cash_book*.py 2>/dev/null | head -30

echo "=== Template structure ==="
wc -l report/ops_cash_book*.xml 2>/dev/null
grep -n "template id\|t-call\|t-foreach" report/ops_cash_book*.xml 2>/dev/null | head -20

echo "=== Data dict passed to template ==="
grep -A 40 "def _get_report_values\|def get_report_data\|def _prepare_report_data\|def action_print\|return {" report/ops_cash_book*.py wizard/ops_cash_book_wizard*.py 2>/dev/null | head -60

echo "✅ Task 2.1 complete — structure audited"
```

### Task 2.2: Update Cash Book Python Data Layer

The Python report/wizard must pass ALL required variables. Audit the current data dict and ADD any missing:

**Required data dict for Cash Book template:**
```python
{
    'company': company_record,
    'currency': company.currency_id,
    'date_from': date_object,
    'date_to': date_object,
    'target_move': 'posted' or 'all',
    'include_initial_balance': True,
    'accounts': [
        {
            'code': '101001',
            'name': 'Cash on Hand',
            'initial_debit': float,
            'initial_credit': float, 
            'initial_balance': float,
            'total_debit': float,      # Total receipts
            'total_credit': float,     # Total payments
            'balance': float,          # Closing balance
            'line_count': int,
            'lines': [
                {
                    'date': date,
                    'ref': 'PAY/2026/0001',
                    'partner': 'Partner Name',
                    'name': 'Description',
                    'debit': float,    # Receipt
                    'credit': float,   # Payment
                    'balance': float,  # Running balance
                },
            ],
        },
    ],
    'total_debit': float,              # Grand total receipts
    'total_credit': float,             # Grand total payments
    'net_balance': float,              # Net cash movement
    'account_count': int,
    'report_id': 'CB-YYYYMMDD-HHMMSS-XXXX',
    'report_name': 'Cash Book',
    'filter_display': 'Period: ...',
    'branch_names': 'All' or comma-separated,
    'bu_names': 'All' or comma-separated,
    # Colors
    'primary_color': company.ops_report_primary_color or '#5B6BBB',
    'text_on_primary': company.ops_report_text_on_primary or '#FFFFFF',
    'body_text_color': company.ops_report_body_text_color or '#1a1a1a',
    'primary_light': company._get_report_primary_light(),
    'primary_dark': company._get_report_primary_dark(),
}
```

**For report_id generation:**
```python
import hashlib, time
report_id = 'CB-%s-%s' % (
    fields.Datetime.now().strftime('%Y%m%d-%H%M%S'),
    hashlib.md5(str(time.time()).encode()).hexdigest()[:4].upper()
)
```

**For color fallbacks** (in case GL prompt hasn't added fields yet):
```python
primary_color = getattr(company, 'ops_report_primary_color', None) or '#5B6BBB'
text_on_primary = getattr(company, 'ops_report_text_on_primary', None) or '#FFFFFF'
body_text_color = getattr(company, 'ops_report_body_text_color', None) or '#1a1a1a'

# Light variant (15% opacity blend with white)
def _get_primary_light_fallback(hex_color):
    hex_color = (hex_color or '#5B6BBB').lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    return '#{:02x}{:02x}{:02x}'.format(
        int(r * 0.15 + 255 * 0.85),
        int(g * 0.15 + 255 * 0.85),
        int(b * 0.15 + 255 * 0.85)
    )

# Dark variant (75% factor)
def _get_primary_dark_fallback(hex_color):
    hex_color = (hex_color or '#5B6BBB').lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    return '#{:02x}{:02x}{:02x}'.format(int(r*0.75), int(g*0.75), int(b*0.75))

primary_light = (hasattr(company, '_get_report_primary_light') and company._get_report_primary_light()) or _get_primary_light_fallback(primary_color)
primary_dark = (hasattr(company, '_get_report_primary_dark') and company._get_report_primary_dark()) or _get_primary_dark_fallback(primary_color)
```

Modify the existing Python report class to include ALL these variables. DO NOT delete any existing logic — extend it.

```bash
echo "=== Updating Cash Book Python data layer ==="
# Edit the report Python file to add missing variables
echo "✅ Task 2.2 complete"
```

### Task 2.3: Rewrite Cash Book QWeb Template

**REPLACE the entire template content.** The new template follows the exact BS corporate design system.

**Template structure:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="ops_cash_book_report_template" name="Cash Book Report">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <!-- Color variables -->
                <t t-set="primary_color" t-value="primary_color or '#5B6BBB'"/>
                <t t-set="text_on_primary" t-value="text_on_primary or '#FFFFFF'"/>
                <t t-set="primary_light" t-value="primary_light or '#E8EAF6'"/>
                <t t-set="primary_dark" t-value="primary_dark or '#4A5AA8'"/>
                
                <div class="page ops-report cashbook">
                    <!-- Link to shared CSS -->
                    <link rel="stylesheet" href="/ops_matrix_accounting/static/src/css/ops_internal_report.css"/>
                    
                    <!-- ═══ HEADER ═══ -->
                    <div class="report-header" t-attf-style="border-bottom: 2px solid {{primary_color}};">
                        <div class="company-block">
                            <t t-if="company.logo">
                                <img t-att-src="image_data_uri(company.logo)" class="company-logo" alt="Logo"/>
                            </t>
                            <div t-else="" class="company-logo-placeholder" t-attf-style="background: {{primary_color}};">
                                <t t-esc="company.name[:2].upper()"/>
                            </div>
                            <div>
                                <div class="company-name"><t t-esc="company.name"/></div>
                                <div class="company-location">
                                    <t t-if="company.city"><t t-esc="company.city"/>, </t>
                                    <t t-if="company.country_id"><t t-esc="company.country_id.name"/></t>
                                </div>
                            </div>
                        </div>
                        <div class="report-info">
                            <div class="print-date">
                                Printed: <t t-esc="context_timestamp(datetime.datetime.now()).strftime('%d %b %Y %H:%M')"/>
                            </div>
                            <div class="report-run-id">
                                <t t-esc="report_id"/>
                            </div>
                        </div>
                    </div>
                    
                    <!-- ═══ TITLE BLOCK ═══ -->
                    <div style="margin-bottom: 16px;">
                        <div class="report-title">Cash Book</div>
                        <div class="report-subtitle">
                            Period: <t t-esc="date_from" t-options='{"widget": "date", "format": "dd MMM yyyy"}'/> 
                            to <t t-esc="date_to" t-options='{"widget": "date", "format": "dd MMM yyyy"}'/>
                            <span class="sep"> | </span>
                            Currency: <t t-esc="currency.name"/> (<t t-esc="currency.symbol"/>)
                            <span class="sep"> | </span>
                            Entries: <t t-if="target_move == 'posted'">Posted Only</t><t t-else="">All Entries</t>
                            <t t-if="branch_names and branch_names != 'All'">
                                <span class="sep"> | </span>Branch: <t t-esc="branch_names"/>
                            </t>
                        </div>
                    </div>
                    
                    <!-- ═══ SUMMARY ROW ═══ -->
                    <div class="summary-row" t-attf-style="background: {{primary_light}};">
                        <div class="summary-item">
                            <div class="summary-label" t-attf-style="color: {{primary_dark}};">Total Receipts</div>
                            <div class="summary-value">
                                <t t-esc="currency.symbol"/> <t t-esc="'{:,.2f}'.format(total_debit)"/>
                            </div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label" t-attf-style="color: {{primary_dark}};">Total Payments</div>
                            <div class="summary-value">
                                <t t-esc="currency.symbol"/> <t t-esc="'{:,.2f}'.format(total_credit)"/>
                            </div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label" t-attf-style="color: {{primary_dark}};">Net Cash Movement</div>
                            <div t-attf-class="summary-value #{abs(net_balance) &lt; 0.01 and 'balanced' or ''}">
                                <t t-esc="currency.symbol"/>
                                <t t-if="net_balance &gt;= 0"> <t t-esc="'{:,.2f}'.format(net_balance)"/></t>
                                <t t-else=""> (<t t-esc="'{:,.2f}'.format(abs(net_balance))"/>)</t>
                            </div>
                        </div>
                    </div>
                    
                    <!-- ═══ ACCOUNT SECTIONS ═══ -->
                    <t t-foreach="accounts" t-as="account">
                        <!-- Account header -->
                        <div t-attf-class="account-header #{account_first and 'first' or ''}"
                             t-attf-style="background: {{primary_light}}; border-left: 4px solid {{primary_color}};">
                            <div class="account-header-left">
                                <span class="account-code-name" t-attf-style="color: {{primary_dark}};">
                                    <t t-esc="account['code']"/> — <t t-esc="account['name']"/>
                                </span>
                            </div>
                            <div class="account-header-right">
                                <t t-esc="account.get('line_count', 0)"/> transactions
                            </div>
                        </div>
                        
                        <!-- Data table -->
                        <table class="report-table">
                            <thead>
                                <tr>
                                    <th class="col-date">Date</th>
                                    <th class="col-ref">Reference</th>
                                    <th class="col-partner">Partner</th>
                                    <th class="col-desc">Description</th>
                                    <th class="col-receipts num">Receipts</th>
                                    <th class="col-payments num">Payments</th>
                                    <th class="col-balance num">Balance</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Opening balance row -->
                                <t t-if="account.get('initial_balance', 0) != 0 or include_initial_balance">
                                    <tr class="opening-balance-row">
                                        <td colspan="4" style="font-style: italic; font-weight: 500; background: #fefce8;">Opening Balance</td>
                                        <td class="num" style="background: #fefce8;">
                                            <t t-if="account.get('initial_debit', 0)"><t t-esc="'{:,.2f}'.format(account['initial_debit'])"/></t>
                                            <t t-else="">—</t>
                                        </td>
                                        <td class="num" style="background: #fefce8;">
                                            <t t-if="account.get('initial_credit', 0)"><t t-esc="'{:,.2f}'.format(account['initial_credit'])"/></t>
                                            <t t-else="">—</t>
                                        </td>
                                        <td class="num" style="background: #fefce8; font-weight: 500;">
                                            <t t-set="ib" t-value="account.get('initial_balance', 0)"/>
                                            <span t-attf-class="#{ib &gt; 0 and 'positive' or (ib &lt; 0 and 'negative' or 'zero')}">
                                                <t t-if="ib &gt;= 0"><t t-esc="'{:,.2f}'.format(ib)"/></t>
                                                <t t-else="">(<t t-esc="'{:,.2f}'.format(abs(ib))"/>)</t>
                                            </span>
                                        </td>
                                    </tr>
                                </t>
                                
                                <!-- Transaction rows -->
                                <t t-foreach="account.get('lines', [])" t-as="line">
                                    <tr>
                                        <td><t t-esc="line['date']" t-options='{"widget": "date", "format": "dd MMM yyyy"}'/></td>
                                        <td class="text-truncate"><t t-esc="line.get('ref', '')"/></td>
                                        <td class="text-truncate"><t t-esc="line.get('partner', '')"/></td>
                                        <td class="text-truncate"><t t-esc="line.get('name', '')"/></td>
                                        <td class="num">
                                            <t t-if="line['debit']"><t t-esc="'{:,.2f}'.format(line['debit'])"/></t>
                                            <t t-else="">—</t>
                                        </td>
                                        <td class="num">
                                            <t t-if="line['credit']"><t t-esc="'{:,.2f}'.format(line['credit'])"/></t>
                                            <t t-else="">—</t>
                                        </td>
                                        <td class="num">
                                            <t t-set="bal" t-value="line['balance']"/>
                                            <span t-attf-class="#{bal &gt; 0 and 'positive' or (bal &lt; 0 and 'negative' or 'zero')}">
                                                <t t-if="bal &gt;= 0"><t t-esc="'{:,.2f}'.format(bal)"/></t>
                                                <t t-else="">(<t t-esc="'{:,.2f}'.format(abs(bal))"/>)</t>
                                            </span>
                                        </td>
                                    </tr>
                                </t>
                                
                                <!-- Account total -->
                                <tr class="account-total" t-attf-style="background: {{primary_light}} !important;">
                                    <td colspan="4" t-attf-style="color: {{primary_dark}}; font-weight: 600;">
                                        Total <t t-esc="account['code']"/> (<t t-esc="account.get('line_count', 0)"/> transactions)
                                    </td>
                                    <td class="num" t-attf-style="color: {{primary_dark}}; font-weight: 600;">
                                        <t t-esc="'{:,.2f}'.format(account['total_debit'])"/>
                                    </td>
                                    <td class="num" t-attf-style="color: {{primary_dark}}; font-weight: 600;">
                                        <t t-esc="'{:,.2f}'.format(account['total_credit'])"/>
                                    </td>
                                    <td class="num" style="font-weight: 700;">
                                        <t t-set="abal" t-value="account['balance']"/>
                                        <span t-attf-class="#{abal &gt; 0 and 'positive' or (abal &lt; 0 and 'negative' or 'zero')}">
                                            <t t-if="abal &gt;= 0"><t t-esc="'{:,.2f}'.format(abal)"/></t>
                                            <t t-else="">(<t t-esc="'{:,.2f}'.format(abs(abal))"/>)</t>
                                        </span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </t>
                    
                    <!-- ═══ GRAND TOTAL ═══ -->
                    <div class="grand-total" t-attf-style="background: {{primary_color}}; color: {{text_on_primary}};">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="width: 68%; padding: 12px 14px; font-weight: 600; font-size: 9pt;">
                                    GRAND TOTAL (<t t-esc="account_count"/> Accounts)
                                </td>
                                <td class="num" style="width: 11%; padding: 12px 8px; font-weight: 700; font-size: 10pt; font-variant-numeric: tabular-nums;">
                                    <t t-esc="'{:,.2f}'.format(total_debit)"/>
                                </td>
                                <td class="num" style="width: 11%; padding: 12px 8px; font-weight: 700; font-size: 10pt; font-variant-numeric: tabular-nums;">
                                    <t t-esc="'{:,.2f}'.format(total_credit)"/>
                                </td>
                                <td style="width: 10%;"></td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- ═══ VERIFICATION ═══ -->
                    <t t-call="ops_matrix_accounting.report_verification_block"/>
                    
                    <!-- ═══ SIGNATURE BLOCK ═══ -->
                    <t t-call="ops_matrix_accounting.report_signature_block"/>
                    
                    <!-- ═══ CONFIDENTIALITY ═══ -->
                    <t t-call="ops_matrix_accounting.report_confidentiality_notice"/>
                    
                    <!-- ═══ IN-PAGE FOOTER ═══ -->
                    <t t-call="ops_matrix_accounting.report_corporate_in_page_footer"/>
                </div>
            </t>
        </t>
    </template>
</odoo>
```

**IMPORTANT**: Adapt the template ID to match whatever the CURRENT file uses. Audit the existing template ID first:
```bash
grep "template id=" report/ops_cash_book*.xml
```
Use the SAME template ID so Odoo replaces it cleanly.

```bash
echo "=== Rewriting Cash Book template ==="
echo "✅ Task 2.3 complete"
```

### Task 2.4: Verify Cash Book

```bash
echo "=== Verifying Cash Book ==="
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -5
docker logs gemini_odoo19 --tail 20 | grep -i "error\|traceback" | grep -v werkzeug || echo "No errors"
echo "✅ PHASE 2 COMPLETE"
```

---

## PHASE 3: DAY BOOK — Template + Python (60 min)

> **Can run in parallel** with Phases 2, 4, 5. Touches: `wizard/ops_day_book_wizard*.py`, `report/ops_day_book*`

### Task 3.1: Audit Current Day Book Structure

```bash
echo "========================================"
echo "PHASE 3: DAY BOOK REDESIGN"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Day Book files ==="
find . -name "*day_book*" -o -name "*daybook*" | sort

echo "=== Wizard ==="
grep -n "class \|def \|_name" wizard/ops_day_book_wizard*.py 2>/dev/null | head -20

echo "=== Report Python ==="
grep -n "class \|def \|_name" report/ops_day_book*.py 2>/dev/null | head -20

echo "=== Template ==="
wc -l report/ops_day_book*.xml 2>/dev/null
grep "template id=" report/ops_day_book*.xml 2>/dev/null

echo "=== Data dict ==="
grep -A 40 "def _get_report_values\|return {" report/ops_day_book*.py wizard/ops_day_book_wizard*.py 2>/dev/null | head -60

echo "✅ Task 3.1 complete"
```

### Task 3.2: Update Day Book Python Data Layer

**Required data dict for Day Book:**
```python
{
    'company': company_record,
    'currency': company.currency_id,
    'date_from': date_object,
    'date_to': date_object,
    'target_move': 'posted' or 'all',
    'dates': [
        {
            'date': date_object,             # The date
            'date_display': 'Wednesday, 15 January 2026',
            'total_debit': float,
            'total_credit': float,
            'entry_count': int,
            'lines': [
                {
                    'journal': 'INV',         # Journal code
                    'account_code': '121000',  # Account code
                    'account_name': 'Account Receivable',
                    'partner': 'Partner Name',
                    'ref': 'INV/2026/0001',
                    'name': 'Description',
                    'debit': float,
                    'credit': float,
                },
            ],
        },
    ],
    'total_debit': float,
    'total_credit': float,
    'net_balance': float,                    # Debit - Credit
    'total_entries': int,                    # Total lines across all dates
    'date_count': int,                       # Number of distinct dates
    'report_id': 'DB-YYYYMMDD-HHMMSS-XXXX',
    'report_name': 'Day Book',
    'filter_display': '...',
    'branch_names': '...',
    'bu_names': '...',
    # Colors (same pattern as Cash Book)
    'primary_color': '...', 'text_on_primary': '...', 'body_text_color': '...',
    'primary_light': '...', 'primary_dark': '...',
}
```

**Key difference from other reports**: Data is grouped by DATE, not by account. Each date has a list of journal entry lines for that day. No running balance. No opening balance.

```bash
echo "=== Updating Day Book Python data layer ==="
echo "✅ Task 3.2 complete"
```

### Task 3.3: Rewrite Day Book QWeb Template

**Key structural differences from Cash Book:**
1. **Portrait A4** (not landscape)
2. **Grouped by date** — section headers show formatted date ("Wednesday, 15 January 2026")
3. **No Balance column** — Day Book is a transaction register, not a running balance
4. **No opening balance rows**
5. **Account column replaces Balance column** — shows which account was hit
6. **Summary metrics**: Total Debit, Total Credit, Transaction Count (not Net Balance)

**Template skeleton (key sections only — fill in full details):**

```xml
<div class="page ops-report daybook">
    <!-- HEADER: Same as Cash Book -->
    <!-- TITLE: "Day Book" -->
    <!-- SUBTITLE: Period + Currency + Entries filter -->
    
    <!-- SUMMARY ROW: 3 metrics -->
    <!-- Total Debit | Total Credit | Transaction Count -->
    <!-- Note: 3rd metric is COUNT not balance -->
    <div class="summary-item">
        <div class="summary-label">Total Entries</div>
        <div class="summary-value"><t t-esc="total_entries"/></div>
    </div>
    
    <!-- DATE SECTIONS (loop over dates) -->
    <t t-foreach="dates" t-as="day">
        <!-- Date section header — styled differently from account headers -->
        <div class="date-section-header" t-if="not day_first" style="margin-top: 20px;"/>
        <div class="account-header" t-attf-style="background: {{primary_light}}; border-left: 4px solid {{primary_color}};">
            <div class="account-header-left">
                <span class="account-code-name" t-attf-style="color: {{primary_dark}};">
                    <t t-esc="day['date_display']"/>
                </span>
            </div>
            <div class="account-header-right">
                <t t-esc="day['entry_count']"/> entries
            </div>
        </div>
        
        <!-- Transaction table — NO balance column -->
        <table class="report-table">
            <thead>
                <tr>
                    <th class="col-jrnl">Journal</th>
                    <th class="col-account">Account</th>
                    <th class="col-partner">Partner</th>
                    <th class="col-ref">Reference</th>
                    <th class="col-desc">Description</th>
                    <th class="col-debit num">Debit</th>
                    <th class="col-credit num">Credit</th>
                </tr>
            </thead>
            <tbody>
                <t t-foreach="day['lines']" t-as="line">
                    <tr>
                        <td><t t-esc="line['journal']"/></td>
                        <td><t t-esc="line['account_code']"/></td>
                        <td class="text-truncate"><t t-esc="line.get('partner', '')"/></td>
                        <td class="text-truncate"><t t-esc="line.get('ref', '')"/></td>
                        <td class="text-truncate"><t t-esc="line.get('name', '')"/></td>
                        <td class="num">
                            <t t-if="line['debit']"><t t-esc="'{:,.2f}'.format(line['debit'])"/></t>
                            <t t-else="">—</t>
                        </td>
                        <td class="num">
                            <t t-if="line['credit']"><t t-esc="'{:,.2f}'.format(line['credit'])"/></t>
                            <t t-else="">—</t>
                        </td>
                    </tr>
                </t>
                
                <!-- Daily total -->
                <tr class="account-total" t-attf-style="background: {{primary_light}} !important;">
                    <td colspan="5" t-attf-style="color: {{primary_dark}}; font-weight: 600;">
                        Total <t t-esc="day['date']" t-options='{"widget": "date", "format": "dd MMM yyyy"}'/> (<t t-esc="day['entry_count']"/> entries)
                    </td>
                    <td class="num" t-attf-style="color: {{primary_dark}}; font-weight: 600;">
                        <t t-esc="'{:,.2f}'.format(day['total_debit'])"/>
                    </td>
                    <td class="num" t-attf-style="color: {{primary_dark}}; font-weight: 600;">
                        <t t-esc="'{:,.2f}'.format(day['total_credit'])"/>
                    </td>
                </tr>
            </tbody>
        </table>
    </t>
    
    <!-- GRAND TOTAL: 2 number columns (no balance) -->
    <!-- Grand total column widths: label 74%, debit 13%, credit 13% -->
    
    <!-- VERIFICATION, SIGNATURE, CONFIDENTIALITY, FOOTER: Same t-calls -->
</div>
```

```bash
echo "=== Rewriting Day Book template ==="
echo "✅ Task 3.3 complete"
```

### Task 3.4: Verify Day Book

```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -5
docker logs gemini_odoo19 --tail 20 | grep -i "error\|traceback" | grep -v werkzeug || echo "No errors"
echo "✅ PHASE 3 COMPLETE"
```

---

## PHASE 4: BANK BOOK — Template + Python (45 min)

> **Can run in parallel**. Touches: `wizard/ops_bank_book_wizard*.py`, `report/ops_bank_book*`

### Task 4.1: Audit Current Bank Book Structure

```bash
echo "========================================"
echo "PHASE 4: BANK BOOK REDESIGN"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Bank Book files ==="
find . -name "*bank_book*" -o -name "*bankbook*" | sort

echo "=== Wizard ==="
grep -n "class \|def \|_name" wizard/ops_bank_book_wizard*.py 2>/dev/null | head -20

echo "=== Report Python ==="
grep -n "class \|def \|_name" report/ops_bank_book*.py 2>/dev/null | head -20

echo "=== Template ==="
grep "template id=" report/ops_bank_book*.xml 2>/dev/null

echo "=== Data dict ==="
grep -A 40 "def _get_report_values\|return {" report/ops_bank_book*.py wizard/ops_bank_book_wizard*.py 2>/dev/null | head -60

echo "✅ Task 4.1 complete"
```

### Task 4.2: Update Bank Book Python Data Layer

**Same structure as Cash Book** with these differences:
- Filter: Bank-type journals only (not cash)
- Column labels: "Deposits" instead of "Receipts", "Withdrawals" instead of "Payments"
- Report ID prefix: `BK-`
- Report name: `'Bank Book'`
- Section headers may include bank account number if available

```python
# Same data dict as Cash Book, but:
'report_id': 'BK-YYYYMMDD-HHMMSS-XXXX',
'report_name': 'Bank Book',
# accounts[] filtered to bank journal accounts only
```

```bash
echo "=== Updating Bank Book Python data layer ==="
echo "✅ Task 4.2 complete"
```

### Task 4.3: Rewrite Bank Book QWeb Template

**The Bank Book template is nearly identical to Cash Book.** Key differences:
1. Report title: "Bank Book" instead of "Cash Book"
2. Summary labels: "Total Deposits" / "Total Withdrawals" / "Net Bank Movement"
3. Column headers: "Deposits" / "Withdrawals" instead of "Receipts" / "Payments"
4. CSS class: `bankbook` instead of `cashbook`
5. Column classes: `.col-deposits` / `.col-withdrawals` instead of `.col-receipts` / `.col-payments`

**Clone the Cash Book template from Phase 2 and make these substitutions:**
- `class="...cashbook"` → `class="...bankbook"`
- `Cash Book` → `Bank Book`
- `Total Receipts` → `Total Deposits`
- `Total Payments` → `Total Withdrawals`
- `Net Cash Movement` → `Net Bank Movement`
- `col-receipts` → `col-deposits`
- `col-payments` → `col-withdrawals`
- Column header text: `Receipts` → `Deposits`, `Payments` → `Withdrawals`

```bash
echo "=== Rewriting Bank Book template ==="
echo "✅ Task 4.3 complete"
```

### Task 4.4: Verify Bank Book

```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -5
docker logs gemini_odoo19 --tail 20 | grep -i "error\|traceback" | grep -v werkzeug || echo "No errors"
echo "✅ PHASE 4 COMPLETE"
```

---

## PHASE 5: PARTNER LEDGER — Template + Python (75 min)

> **Can run in parallel**. Touches: `report/ops_partner_ledger*` or equivalent files

### Task 5.1: Audit Current Partner Ledger Structure

```bash
echo "========================================"
echo "PHASE 5: PARTNER LEDGER REDESIGN"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Partner Ledger files ==="
find . -name "*partner*ledger*" -o -name "*aged_partner*" | sort
# Note: aged partner is a DIFFERENT report (Wave 2). We want partner LEDGER.

echo "=== All report files for reference ==="
ls report/*.py report/*.xml 2>/dev/null | sort

echo "=== Check if partner ledger exists or if we need to create it ==="
grep -rn "partner.ledger\|partner_ledger\|Partner Ledger" report/ wizard/ --include="*.py" --include="*.xml" | head -20

echo "=== If it doesn't exist, check what GL wizard fields we can reuse ==="
grep -n "partner\|account_type\|account_ids" wizard/ops_general_ledger_wizard*.py 2>/dev/null | head -20

echo "✅ Task 5.1 complete"
```

### Task 5.2: Update/Create Partner Ledger Python Data Layer

**Required data dict:**
```python
{
    'company': company_record,
    'currency': company.currency_id,
    'date_from': date_object,
    'date_to': date_object,
    'target_move': 'posted' or 'all',
    'include_initial_balance': True,
    'account_types': ['asset_receivable', 'liability_payable'],  # Filter
    'partners': [
        {
            'name': 'Azure Interior',
            'partner_type': 'customer',       # customer/vendor/both
            'partner_type_label': 'Customer',
            'partner_type_badge': 'badge-customer',
            'initial_debit': float,
            'initial_credit': float,
            'initial_balance': float,
            'total_debit': float,
            'total_credit': float,
            'balance': float,
            'line_count': int,
            'lines': [
                {
                    'date': date,
                    'journal': 'INV',
                    'account_code': '121000',
                    'ref': 'INV/2026/0001',
                    'name': 'Description',
                    'debit': float,
                    'credit': float,
                    'balance': float,         # Running balance per partner
                },
            ],
        },
    ],
    'total_debit': float,
    'total_credit': float,
    'net_balance': float,
    'partner_count': int,
    'report_id': 'PL-YYYYMMDD-HHMMSS-XXXX',
    'report_name': 'Partner Ledger',
    'filter_display': '...',
    'branch_names': '...', 'bu_names': '...',
    # Colors
    'primary_color': '...', 'text_on_primary': '...', 'body_text_color': '...',
    'primary_light': '...', 'primary_dark': '...',
}
```

**Partner type determination:**
```python
def _get_partner_type(self, partner_id, account_types_used):
    """Determine if partner is customer, vendor, or both based on accounts used"""
    has_receivable = any(t.startswith('asset_receivable') for t in account_types_used)
    has_payable = any(t.startswith('liability_payable') for t in account_types_used)
    if has_receivable and has_payable:
        return ('Both', 'badge-both')
    elif has_receivable:
        return ('Customer', 'badge-customer')
    else:
        return ('Vendor', 'badge-vendor')
```

**If no Partner Ledger report file exists**, create it based on the GL report pattern:
- Model: `ops.partner.ledger.report` (or similar)
- Wizard: Can reuse GL wizard with partner filter, OR create `ops.partner.ledger.wizard`
- Template: New XML file

```bash
echo "=== Updating/Creating Partner Ledger data layer ==="
echo "✅ Task 5.2 complete"
```

### Task 5.3: Rewrite/Create Partner Ledger QWeb Template

**Landscape A4** (8 columns like GL). Uses GL column widths from `partner-ledger` CSS class.

**Template structure mirrors GL** with these differences:
- Grouped by partner (not account)
- Section header: Partner name + type badge (Customer/Vendor/Both)
- Account column instead of Partner column (since we're already grouped by partner)
- Summary: Total Debit | Total Credit | Net Balance
- Report title: "Partner Ledger"

**Section header with partner type badge:**
```xml
<div class="account-header" t-attf-style="background: {{primary_light}}; border-left: 4px solid {{primary_color}};">
    <div class="account-header-left">
        <span class="account-code-name" t-attf-style="color: {{primary_dark}};">
            <t t-esc="partner['name']"/>
        </span>
        <span t-attf-class="account-type-badge {{partner['partner_type_badge']}}">
            <t t-esc="partner['partner_type_label']"/>
        </span>
    </div>
    <div class="account-header-right">
        <t t-esc="partner['line_count']"/> transactions
    </div>
</div>
```

**Table columns:**
```xml
<thead>
    <tr>
        <th class="col-date">Date</th>
        <th class="col-jrnl">Journal</th>
        <th class="col-account">Account</th>
        <th class="col-ref">Reference</th>
        <th class="col-desc">Description</th>
        <th class="col-debit num">Debit</th>
        <th class="col-credit num">Credit</th>
        <th class="col-balance num">Balance</th>
    </tr>
</thead>
```

**Grand total label**: `GRAND TOTAL (N Partners)`

```bash
echo "=== Rewriting Partner Ledger template ==="
echo "✅ Task 5.3 complete"
```

### Task 5.4: Verify Partner Ledger

```bash
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -5
docker logs gemini_odoo19 --tail 20 | grep -i "error\|traceback" | grep -v werkzeug || echo "No errors"
echo "✅ PHASE 5 COMPLETE"
```

---

## PHASE 6: WIZARD CLEANUP (20 min)

### Task 6.1: Remove Preview Buttons from All 4 Wizards

Each wizard may have a "Preview" button that opens a web preview. Remove it — keep only "Print PDF" (and later "Export Excel").

```bash
echo "========================================"
echo "PHASE 6: WIZARD CLEANUP"
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Finding Preview buttons in wizard views ==="
grep -rn "preview\|Preview\|action_preview\|web_preview" wizard/ views/ --include="*.xml" --include="*.py" | head -30

echo "=== Wizard view files ==="
find views/ wizard/ -name "*cash_book*" -o -name "*day_book*" -o -name "*bank_book*" -o -name "*partner_ledger*" | sort
```

For each wizard found, remove:
1. Any `action_preview` or `action_web_preview` Python methods (or leave them but remove the button)
2. The Preview button from the wizard form XML
3. Keep only: **Print PDF** button (primary) + **Cancel** button (secondary)

Target footer structure for all wizards:
```xml
<footer>
    <button name="action_print" type="object" string="Print PDF" class="btn-primary"/>
    <button string="Cancel" class="btn-secondary" special="cancel"/>
</footer>
```

```bash
echo "=== Cleaning wizard buttons ==="
# Remove Preview buttons from each wizard view
echo "✅ Task 6.1 complete"
```

### Task 6.2: Ensure Wizard Forms Follow Layout Standards

Quick layout audit for all 4 wizards:
- NO `<sheet>` wrapper (it's a dialog)
- Two-column `<group><group>...<group>` layout
- Branch/BU filters present
- Date range fields with proper inline layout
- `target_move` selection field present

```bash
echo "=== Auditing wizard layouts ==="
for f in wizard/ops_cash_book_wizard*.xml wizard/ops_day_book_wizard*.xml wizard/ops_bank_book_wizard*.xml; do
    if [ -f "$f" ]; then
        echo "--- $f ---"
        grep -c "<sheet>" "$f" && echo "⚠️ Has <sheet> — remove it" || echo "✅ No <sheet>"
        grep "footer" "$f" | head -3
    fi
done
echo "✅ Task 6.2 complete"
```

---

## PHASE 7: MANIFEST + TEST + COMMIT (20 min)

### Task 7.1: Update Manifest Data Files

Ensure ALL new/modified XML files are registered in `__manifest__.py`:

```bash
echo "========================================"
echo "PHASE 7: MANIFEST + TEST + COMMIT"  
echo "========================================"

cd /opt/gemini_odoo19/addons/ops_matrix_accounting

echo "=== Checking manifest for all report files ==="
for f in \
    "ops_corporate_report_components.xml" \
    "ops_cash_book" \
    "ops_day_book" \
    "ops_bank_book" \
    "ops_partner_ledger"; do
    grep -q "$f" __manifest__.py && echo "✅ $f in manifest" || echo "❌ $f MISSING from manifest"
done
```

Add any missing files to the `'data'` list in `__manifest__.py`.

### Task 7.2: Full Module Update

```bash
echo "=== Full module update ==="
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -20

echo "=== Check for errors ==="
docker logs gemini_odoo19 --tail 50 | grep -i "error\|traceback" | grep -v werkzeug || echo "No errors found"

echo "=== Restart for clean state ==="
docker restart gemini_odoo19
sleep 10
echo "✅ Task 7.2 complete"
```

### Task 7.3: Verify All Templates Load

```bash
echo "=== Verifying all report templates exist ==="
docker exec gemini_odoo19 python3 -c "
import xmlrpc.client
db, uid, pwd = 'mz-db', 2, 'admin'
models = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')

templates = ['ops_cash_book_report_template', 'ops_day_book_report_template', 
             'ops_bank_book_report_template']
for t in templates:
    try:
        result = models.execute_kw(db, uid, pwd, 'ir.ui.view', 'search_count', 
                                    [[('key', 'like', t)]])
        print(f'  {t}: {\"✅\" if result else \"❌\"}')
    except Exception as e:
        print(f'  {t}: ❌ {e}')
" 2>/dev/null || echo "RPC check skipped"

echo "=== Verifying shared components ==="
grep -c "template id=" report/ops_corporate_report_components.xml 2>/dev/null || echo "Components file check"

echo "=== CSS file size ==="
wc -l static/src/css/ops_internal_report.css

echo "✅ Task 7.3 complete"
```

### Task 7.4: Git Commit

```bash
echo "=== Committing to git ==="

cd /opt/gemini_odoo19
git add -A
git status

git commit -m "feat(accounting): Wave 1 — BS corporate theme for Cash/Day/Bank Book + Partner Ledger

- Cash Book: Portrait A4, 7 columns (Receipts/Payments/Balance), grouped by cash account
- Day Book: Portrait A4, 7 columns (no balance), grouped by date with daily totals
- Bank Book: Portrait A4, 7 columns (Deposits/Withdrawals/Balance), grouped by bank account
- Partner Ledger: Landscape A4, 8 columns, grouped by partner with type badges
- All reports: Dynamic colors from company settings, opening balances, verification block
- All reports: Signature block, confidentiality notice, in-page badge footer
- Shared components: footer, verification, signature, confidentiality (reusable templates)
- Added report-specific CSS column widths + partner type badge styles
- Wizard cleanup: removed Preview buttons, standardized layouts
- Report IDs: CB-/DB-/BK-/PL- prefixes for audit trail"

git push origin main

echo "✅ Committed successfully"
```

---

## FINAL SUMMARY

```bash
echo "========================================"
echo "WAVE 1 — TRANSACTION LEDGERS COMPLETE"
echo "========================================"
echo ""
echo "REPORTS REDESIGNED:"
echo "  ✅ Cash Book    — Portrait, grouped by cash account"
echo "  ✅ Day Book     — Portrait, grouped by date"
echo "  ✅ Bank Book    — Portrait, grouped by bank account"
echo "  ✅ Partner Ledger — Landscape, grouped by partner"
echo ""
echo "SHARED COMPONENTS CREATED:"
echo "  ✅ ops_corporate_report_components.xml (footer, verification, signature, confidentiality)"
echo "  ✅ Report-specific CSS appended to ops_internal_report.css"
echo "  ✅ Partner type badges (customer/vendor/both)"
echo ""
echo "DESIGN SYSTEM:"
echo "  ✅ All use BS corporate theme from GL redesign"
echo "  ✅ All colors dynamic from company.ops_report_* fields"
echo "  ✅ All use shared footer with static badge PNG"
echo "  ✅ No notes section on any report"
echo ""
echo "WAVE STATUS:"
echo "  Wave 1: ████████████████████ COMPLETE"
echo "  Wave 2: Aged Receivables/Payables — NEXT"
echo "  Wave 3: P&L, BS, Trial Balance — PENDING"
echo "  Wave 4: Asset/PDC Registers — PENDING"
echo "  Wave 5: Variance/Comparison — PENDING"
echo "  Wave 6: Cash Flow/Consolidated — PENDING"
echo "  Wave 7: Excel variants — PENDING"
echo "========================================"
```

---

## SUCCESS CRITERIA

- [ ] All 4 reports render PDF without errors
- [ ] Cash Book filters to cash journals only, shows opening balance + running balance
- [ ] Day Book groups by date, shows daily totals, NO balance column
- [ ] Bank Book filters to bank journals only, shows deposits/withdrawals
- [ ] Partner Ledger groups by partner with type badges (Customer/Vendor/Both)
- [ ] All reports use dynamic colors from company settings
- [ ] All reports show: header, summary row, data sections, grand total, verification, signature, confidentiality, footer badge
- [ ] No hardcoded images — badge via static file path
- [ ] No notes section on any report
- [ ] Preview buttons removed from all 4 wizards
- [ ] Shared components (footer, verification, signature, confidentiality) work as t-call templates
- [ ] CSS additions append to existing file (don't overwrite GL column widths)
- [ ] Module updates without errors
- [ ] Git committed

---

## EXECUTION

Execute all phases sequentially (Phase 1 first, then 2–5 can parallelize, then 6–7 sequential).
Fix any errors encountered — do not stop.
Report progress after each phase.
Generate completion summary.

**BEGIN AUTONOMOUS EXECUTION NOW.**
