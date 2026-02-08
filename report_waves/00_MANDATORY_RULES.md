# MANDATORY RULES — Read BEFORE Executing Wave 1

## APPLY THESE RULES TO EVERY REPORT TEMPLATE

These override anything in the Wave 1 prompt that conflicts. Learned from GL implementation and wkhtmltopdf testing.

---

### Rule 1: ALL CSS MUST BE INLINE

wkhtmltopdf does NOT reliably load external CSS files via `<link>`. 

**DO NOT USE:**
```xml
<link rel="stylesheet" href="/ops_matrix_accounting/static/src/css/ops_internal_report.css"/>
```

**USE INSTEAD:** Embed a complete `<style>` block inside each template, right after `<div class="page ops-report">`:

```xml
<div class="page ops-report cashbook">
    <style type="text/css">
        /* All report CSS goes here — inline */
    </style>
    <!-- rest of report -->
</div>
```

Copy the relevant CSS from `ops_internal_report.css` into each template's inline `<style>` block. Yes, this means duplication — but it's the only way wkhtmltopdf renders it.

---

### Rule 2: NO FLEXBOX — Use Tables

wkhtmltopdf's QtWebKit (~2011) does NOT support modern flexbox or `gap`.

**DO NOT USE:**
```css
display: flex; gap: 48px; justify-content: flex-start;
```

**USE INSTEAD for summary row:**
```html
<table style="width: 100%; border-collapse: collapse;">
    <tr>
        <td style="padding: 12px 16px; width: 33%;">
            <div style="font-size: 8pt; text-transform: uppercase;">LABEL</div>
            <div style="font-size: 13pt; font-weight: 700;">VALUE</div>
        </td>
        <td style="padding: 12px 16px; width: 33%;">...</td>
        <td style="padding: 12px 16px; width: 34%;">...</td>
    </tr>
</table>
```

**USE INSTEAD for signature block:**
```html
<table style="width: 100%; border-collapse: collapse; margin-top: 30px;">
    <tr>
        <td style="width: 32%; padding: 0 15px 0 0; vertical-align: top;">
            <div style="text-transform: uppercase; font-size: 7.5pt; font-weight: 600; color: #64748b;">PREPARED BY</div>
            <div style="border-bottom: 1px solid #cbd5e1; margin: 40px 0 6px;"></div>
            <div style="font-size: 7pt; color: #94a3b8;">Name / Date</div>
        </td>
        <td style="width: 2%; border-left: 1px solid #e2e8f0;"></td>
        <td style="width: 32%; padding: 0 15px; vertical-align: top;">
            <!-- REVIEWED BY - same structure -->
        </td>
        <td style="width: 2%; border-left: 1px solid #e2e8f0;"></td>
        <td style="width: 32%; padding: 0 0 0 15px; vertical-align: top;">
            <!-- APPROVED BY - same structure -->
        </td>
    </tr>
</table>
```

Apply this to ALL horizontal layouts: summary row, signature block, header (company left / date right), footer.

---

### Rule 3: NO VERIFICATION BLOCK

Do NOT include any "Balance Verified" section. Remove all references to:
- `report_verification_block`
- `is_balanced` variable
- Any green/red verification indicator

Not needed on any report.

---

### Rule 4: FIXED FOOTER — Not In-Page

The confidentiality notice and "Powered by OPS Framework" badge use `position: fixed; bottom: 0` — NOT placed inline after the data.

**DO NOT USE:**
```xml
<t t-call="ops_matrix_accounting.report_corporate_in_page_footer"/>
<t t-call="ops_matrix_accounting.report_confidentiality_notice"/>
```

**USE INSTEAD** — place this INSIDE `<div class="page">` as the LAST element:

```xml
<!-- FIXED FOOTER — bottom of every page -->
<div style="position: fixed; bottom: 0; left: 0; right: 0; padding: 6px 12mm; border-top: 1px solid #e2e8f0;">
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="width: 50%; text-align: left; vertical-align: middle; padding: 4px 0;">
                <span style="font-size: 8pt; color: #666666;">Powered by</span>
                <img src="/ops_matrix_accounting/static/src/img/ops_badge_footer.png"
                     style="height: 16px; vertical-align: middle; margin-left: 4px;"
                     alt="OPS Framework"/>
            </td>
            <td style="width: 50%; text-align: right; vertical-align: middle; padding: 4px 0;">
                <span style="font-size: 6.5pt; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                    Confidential &#x2014; For authorized personnel only
                </span>
            </td>
        </tr>
    </table>
</div>
```

---

### Rule 5: HTML ENTITIES — No Literal Special Characters

wkhtmltopdf has UTF-8 encoding issues. Use HTML entities for special characters.

| Character | DO NOT USE | USE INSTEAD |
|-----------|-----------|-------------|
| Em dash | `—` | `&#x2014;` |
| Checkmark | `✓` | `&#x2713;` |
| En dash | `–` | `&#x2013;` |
| Bullet | `•` | `&#x2022;` |

**Also**: Every template MUST have this inside `<head>` (or at the very top if using `web.html_container`):
```xml
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
```

---

### Rule 6: NO `font-variant-numeric`

wkhtmltopdf does not support `font-variant-numeric: tabular-nums`. Remove it from all CSS. Number alignment comes from right-aligned `text-align: right` cells only.

---

### Rule 7: PAPERFORMAT RECORDS

Every report needs a paperformat record. Create ONE shared record per orientation:

**Portrait** (for Cash Book, Day Book, Bank Book):
```xml
<record id="paperformat_ops_portrait" model="report.paperformat">
    <field name="name">OPS Financial Report (Portrait)</field>
    <field name="default">False</field>
    <field name="format">A4</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">15</field>
    <field name="margin_bottom">25</field>
    <field name="margin_left">12</field>
    <field name="margin_right">12</field>
    <field name="header_line">False</field>
    <field name="header_spacing">0</field>
    <field name="disable_shrinking">True</field>
</record>
```

**Landscape** (for Partner Ledger):
```xml
<record id="paperformat_ops_landscape" model="report.paperformat">
    <field name="name">OPS Financial Report (Landscape)</field>
    <field name="default">False</field>
    <field name="format">A4</field>
    <field name="orientation">Landscape</field>
    <field name="margin_top">15</field>
    <field name="margin_bottom">25</field>
    <field name="margin_left">12</field>
    <field name="margin_right">12</field>
    <field name="header_line">False</field>
    <field name="header_spacing">0</field>
    <field name="disable_shrinking">True</field>
</record>
```

**Bottom margin is 25mm** to reserve space for the `position: fixed` footer.

Link each report action to the appropriate paperformat:
```xml
<field name="paperformat_id" ref="paperformat_ops_portrait"/>
```

Also set `@page` in the inline CSS to match:
```css
@page { size: A4; margin: 15mm 12mm 25mm 12mm; }
/* OR for landscape: */
@page { size: A4 landscape; margin: 15mm 12mm 25mm 12mm; }
```

---

### Rule 8: ZERO VALUES IN TRANSACTIONS

- Transaction rows with zero debit or credit: show `&#x2014;` (em dash), NOT `0.00`
- Total rows with zero: show `0.00` with gray color (`color: #bbbbbb`)
- Use HTML entity, not literal character

---

### Rule 9: TEMPLATE SKELETON ORDER

Every report template follows this exact element order inside `<div class="page">`:

```
1. <style> block (inline CSS)
2. <meta charset>
3. HEADER (company info | print date + report ID)
4. TITLE + SUBTITLE
5. SUMMARY ROW (3 metrics in a table)
6. DATA SECTIONS (account/date/partner groups)
7. GRAND TOTAL
8. SIGNATURE BLOCK (table-based, 3 columns)
9. FIXED FOOTER (position: fixed, confidentiality + badge)
```

**No verification block. No notes section. No in-page footer call.**

---

### Rule 10: COLOR FALLBACKS

The GL prompt may or may not have created `ops_report_primary_color` fields yet. Always use fallbacks:

```python
primary_color = getattr(company, 'ops_report_primary_color', None) or '#5B6BBB'
text_on_primary = getattr(company, 'ops_report_text_on_primary', None) or '#FFFFFF'
body_text_color = getattr(company, 'ops_report_body_text_color', None) or '#1a1a1a'
```

For light/dark variants, compute inline if helper methods don't exist:
```python
def _fallback_primary_light(hex_color):
    h = (hex_color or '#5B6BBB').lstrip('#')
    r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    return '#{:02x}{:02x}{:02x}'.format(int(r*0.15+255*0.85), int(g*0.15+255*0.85), int(b*0.15+255*0.85))

def _fallback_primary_dark(hex_color):
    h = (hex_color or '#5B6BBB').lstrip('#')
    r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    return '#{:02x}{:02x}{:02x}'.format(int(r*0.75), int(g*0.75), int(b*0.75))
```

---

## EXECUTION ORDER

1. Read this addendum FIRST
2. Then execute the Wave 1 prompt (WAVE1_TRANSACTION_LEDGERS.md)
3. Wherever the Wave 1 prompt conflicts with these rules, **these rules win**
