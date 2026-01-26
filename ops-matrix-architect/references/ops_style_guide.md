# OPS Matrix Style Guide

> PDF Rendering Rules, Color System & Executive Design Standards

## Critical: wkhtmltopdf Compatibility

wkhtmltopdf uses an older WebKit engine with limited CSS support. **All styles must comply with these restrictions.**

### FORBIDDEN CSS

```css
/* DO NOT USE THESE - WILL BREAK PDF RENDERING */

display: flex;           /* No Flexbox */
display: grid;           /* No CSS Grid */
flex-direction: *;       /* Flex properties */
justify-content: *;      /* Flex alignment */
align-items: *;          /* Flex alignment */
gap: *;                  /* Flex/Grid gap */
grid-template-*: *;      /* Grid properties */

var(--color);            /* CSS Variables */
--custom-property: *;    /* CSS Custom Properties */

@import url('...');      /* External fonts */
font-family: 'CustomFont'; /* Web fonts */
```

### REQUIRED CSS

```css
/* ALWAYS USE THESE PATTERNS */

/* Table-based layout (replaces flex/grid) */
display: table;
display: table-cell;
display: inline-block;

/* Direct color values (no variables) */
background-color: #DA291C;
color: #000000;
border-color: #e2e8f0;

/* Force print colors (CRITICAL) */
-webkit-print-color-adjust: exact !important;
print-color-adjust: exact !important;

/* System fonts only */
font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;
font-family: Georgia, 'Times New Roman', serif;
font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
```

---

## Color System

### Primary Palette

| Name | Hex Code | RGB | Usage |
|------|----------|-----|-------|
| **Primary Dark** | `#0a1628` | rgb(10, 22, 40) | Cover backgrounds, dark headers |
| **Primary** | `#1a2744` | rgb(26, 39, 68) | Section headers, navigation |
| **Secondary** | `#3b82f6` | rgb(59, 130, 246) | Highlights, links, badges |

### Semantic Colors

| Name | Hex Code | RGB | Usage |
|------|----------|-----|-------|
| **Success** | `#059669` | rgb(5, 150, 105) | Revenue, profit, positive values |
| **Danger** | `#dc2626` | rgb(220, 38, 38) | Expenses, loss, negative values |
| **Warning** | `#d97706` | rgb(217, 119, 6) | Caution, liabilities, alerts |
| **Info** | `#2563eb` | rgb(37, 99, 235) | Assets, neutral highlights |

### Grayscale

| Name | Hex Code | Usage |
|------|----------|-------|
| **Text Dark** | `#1e293b` | Primary text |
| **Text Medium** | `#64748b` | Labels, secondary text |
| **Text Light** | `#94a3b8` | Muted, zero values |
| **Border** | `#e2e8f0` | Table borders, dividers |
| **Background** | `#f8fafc` | Subtle backgrounds |
| **White** | `#ffffff` | Page background |

### Color Application Rules

```xml
<!-- Revenue/Income: Always success green -->
<td style="color: #059669 !important;">+500.00</td>

<!-- Expenses/Costs: Always danger red -->
<td style="color: #dc2626 !important;">-350.00</td>

<!-- Zero values: Always muted -->
<td style="color: #94a3b8 !important;">0.00</td>

<!-- Neutral/informational: Use primary -->
<td style="color: #1e293b;">Item Name</td>

<!-- Colored backgrounds require print-color-adjust -->
<div style="background-color: #059669 !important; -webkit-print-color-adjust: exact !important;">
    <span style="color: #ffffff;">Content</span>
</div>
```

---

## Typography

### Font Families

```css
/* Body text - sans-serif */
.ops-body {
    font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1e293b;
}

/* Headings - serif for elegance */
.ops-heading {
    font-family: Georgia, 'Times New Roman', serif;
    font-weight: bold;
}

/* Numbers/Currency - monospace for alignment */
.ops-number {
    font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
}
```

### Font Sizes

| Element | Size | Weight |
|---------|------|--------|
| Cover Title | 32px | Bold |
| Section Header | 18px | Bold |
| Page Title | 22px | Bold |
| Table Header | 9pt | 600 |
| Body Text | 10pt | 400 |
| Small Text | 8pt | 400 |
| Labels | 9px | 600 |
| KPI Value | 22px | Bold |
| Summary Value | 24pt | 700 |

### Text Utilities

```css
.ops-uppercase {
    text-transform: uppercase;
    letter-spacing: 1px;
}

.ops-small-caps {
    font-variant: small-caps;
    letter-spacing: 0.5px;
}

.text-end { text-align: right !important; }
.text-center { text-align: center !important; }
.text-left { text-align: left !important; }
.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }
```

---

## Layout System

### Table-Based Grid (Replaces Flexbox)

```xml
<!-- Two Column Layout -->
<table style="width: 100%;">
    <tr>
        <td style="width: 50%; vertical-align: top;">
            <!-- Left column -->
        </td>
        <td style="width: 50%; vertical-align: top;">
            <!-- Right column -->
        </td>
    </tr>
</table>

<!-- Three Column with Spacing -->
<table style="width: 100%; border-collapse: separate; border-spacing: 12px 0;">
    <tr>
        <td style="width: 33.33%; vertical-align: top;">Card 1</td>
        <td style="width: 33.33%; vertical-align: top;">Card 2</td>
        <td style="width: 33.33%; vertical-align: top;">Card 3</td>
    </tr>
</table>

<!-- Sidebar Layout (25% / 75%) -->
<table style="width: 100%;">
    <tr>
        <td style="width: 25%; vertical-align: top;">
            <!-- Sidebar -->
        </td>
        <td style="width: 75%; vertical-align: top; padding-left: 20px;">
            <!-- Main content -->
        </td>
    </tr>
</table>
```

### Column System

```css
.row { display: table; width: 100%; }
.row:after { content: ""; display: table; clear: both; }
.col-6 { display: table-cell; width: 50%; vertical-align: top; }
.col-4 { display: table-cell; width: 33.33%; vertical-align: top; }
.col-3 { display: table-cell; width: 25%; vertical-align: top; }
.col-12 { display: block; width: 100%; }
```

---

## Component Library

### KPI Cards

```xml
<div class="ops-kpi-card success" style="
    background: #ffffff !important;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #059669 !important;
    padding: 18px;
    -webkit-print-color-adjust: exact !important;
">
    <div style="font-size: 9px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">
        Total Revenue
    </div>
    <div style="font-size: 22px; font-weight: bold; color: #059669 !important; margin-top: 4px; font-family: 'DejaVu Sans Mono', monospace;">
        1,250,000.00
    </div>
    <div style="font-size: 10px; font-weight: 600; color: #64748b; margin-top: 4px;">
        +12.5% vs Last Year
    </div>
</div>
```

**Variants:**
- `success` - Green accent (border-left-color: #059669)
- `danger` - Red accent (border-left-color: #dc2626)
- `warning` - Orange accent (border-left-color: #d97706)
- `neutral` - Blue accent (border-left-color: #2563eb)

### Section Headers

```xml
<div class="ops-section-header-bar" style="
    background: #059669 !important;
    padding: 10px 14px;
    border-radius: 4px 4px 0 0;
    -webkit-print-color-adjust: exact !important;
">
    <table style="width: 100%;">
        <tr>
            <td style="font-size: 11pt; font-weight: 700; color: #ffffff !important; text-transform: uppercase; letter-spacing: 0.5px;">
                Revenue
            </td>
            <td style="font-family: 'DejaVu Sans Mono', monospace; font-size: 12pt; font-weight: 700; color: #ffffff !important; text-align: right;">
                1,250,000.00
            </td>
        </tr>
    </table>
</div>
```

### Data Tables

```xml
<table class="ops-data-table" style="width: 100%; border-collapse: collapse; background: #ffffff; font-size: 10pt;">
    <thead>
        <tr>
            <th style="padding: 10px 8px; text-align: left; font-size: 9pt; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 2px solid #1e293b;">
                Account
            </th>
            <th style="padding: 10px 8px; text-align: right; font-size: 9pt; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 2px solid #1e293b;">
                Amount
            </th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="padding: 8px; font-size: 10pt; color: #1e293b; border-bottom: 1px solid #f1f5f9;">
                Sales Revenue
            </td>
            <td style="padding: 8px; text-align: right; font-family: 'DejaVu Sans Mono', monospace; font-size: 9pt; color: #059669 !important; border-bottom: 1px solid #f1f5f9;">
                500,000.00
            </td>
        </tr>
        <!-- Total Row -->
        <tr style="background: #fafafa !important; -webkit-print-color-adjust: exact !important;">
            <td style="padding: 8px; font-weight: 600; border-top: 1px solid #94a3b8;">
                Total
            </td>
            <td style="padding: 8px; text-align: right; font-weight: 700; font-family: 'DejaVu Sans Mono', monospace; border-top: 1px solid #94a3b8;">
                500,000.00
            </td>
        </tr>
    </tbody>
</table>
```

### Summary Box

```xml
<div class="ops-summary-box" style="
    margin-top: 20px;
    border-radius: 6px;
    padding: 18px 22px;
    background: #047857 !important;
    -webkit-print-color-adjust: exact !important;
">
    <table style="width: 100%;">
        <tr>
            <td style="width: 35%; vertical-align: middle;">
                <div style="font-size: 9pt; font-weight: 600; color: rgba(255, 255, 255, 0.65); text-transform: uppercase; letter-spacing: 0.5px;">
                    Net Profit
                </div>
                <div style="font-size: 10pt; color: rgba(255, 255, 255, 0.8); margin-top: 2px;">
                    Revenue - Expenses
                </div>
            </td>
            <td style="width: 40%; text-align: center; vertical-align: middle;">
                <div style="font-family: 'DejaVu Sans Mono', monospace; font-size: 24pt; font-weight: 700; color: #ffffff !important;">
                    150,000.00
                </div>
            </td>
            <td style="width: 25%; text-align: right; vertical-align: middle;">
                <div style="background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.2); padding: 8px 14px; border-radius: 5px; text-align: center;">
                    <div style="font-size: 10pt; font-weight: 600; color: #ffffff; margin-top: 3px;">
                        12.5% Margin
                    </div>
                </div>
            </td>
        </tr>
    </table>
</div>
```

**Variants:**
- `.success` - background: #047857
- `.loss` - background: #991b1b
- `.neutral` - background: #0a1628

### Status Pills

```xml
<span style="
    display: inline-block;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 10pt;
    font-weight: 600;
    background: #dcfce7 !important;
    color: #059669 !important;
    -webkit-print-color-adjust: exact !important;
">Excellent</span>
```

**Variants:**
- `excellent` - bg: #dcfce7, color: #059669
- `healthy` - bg: #dbeafe, color: #2563eb
- `acceptable` - bg: #f1f5f9, color: #64748b
- `warning` - bg: #fef3c7, color: #d97706
- `loss` - bg: #fee2e2, color: #dc2626

### Alert Banners

```xml
<div style="
    padding: 12px 14px;
    border-radius: 4px;
    margin: 14px 0;
    border-left: 4px solid #059669 !important;
    background-color: rgba(5, 150, 105, 0.1) !important;
    color: #065f46;
    -webkit-print-color-adjust: exact !important;
">
    <strong>Success:</strong> Operation completed successfully.
</div>
```

**Variants:**
- `success` - border: #059669, bg: rgba(5,150,105,0.1), text: #065f46
- `warning` - border: #d97706, bg: rgba(217,119,6,0.1), text: #92400e
- `danger` - border: #dc2626, bg: rgba(220,38,38,0.1), text: #991b1b
- `info` - border: #2563eb, bg: rgba(37,99,235,0.1), text: #1e40af

---

## Cover Page Design

### Executive Cover Structure

```xml
<div class="page ops-cover-page" style="min-height: 100%; background: #ffffff !important; page-break-after: always;">

    <!-- Header Band -->
    <div style="padding: 35px 45px; background: #0a1628 !important; -webkit-print-color-adjust: exact !important;">
        <table style="width: 100%;">
            <tr>
                <td style="vertical-align: middle;">
                    <!-- Logo + Company Name -->
                    <span style="
                        display: inline-block;
                        width: 48px;
                        height: 48px;
                        border-radius: 8px;
                        background: linear-gradient(135deg, #1a2744 0%, #3b82f6 100%);
                        text-align: center;
                        line-height: 48px;
                        font-family: Georgia, serif;
                        font-size: 24px;
                        font-weight: bold;
                        color: #ffffff;
                        -webkit-print-color-adjust: exact !important;
                    ">O</span>
                    <span style="display: inline-block; vertical-align: middle; margin-left: 12px;">
                        <span style="font-size: 18px; font-weight: bold; color: #ffffff;">Company Name</span><br/>
                        <span style="font-size: 10px; color: rgba(255,255,255,0.6);">Financial Intelligence</span>
                    </span>
                </td>
                <td style="text-align: right; vertical-align: middle;">
                    <!-- Period Badge -->
                </td>
            </tr>
        </table>
    </div>

    <!-- Accent Bar -->
    <div style="height: 5px; background: linear-gradient(90deg, #1a2744 0%, #3b82f6 50%, #059669 100%); -webkit-print-color-adjust: exact !important;"></div>

    <!-- Title Area -->
    <div style="padding: 50px 45px 35px 45px; background: #0a1628 !important; -webkit-print-color-adjust: exact !important;">
        <div style="font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; color: #3b82f6;">
            Financial Statement
        </div>
        <h1 style="font-family: Georgia, serif; font-size: 32px; font-weight: bold; color: #ffffff; line-height: 1.2; margin: 0;">
            Profit &amp; Loss Statement
        </h1>
    </div>

    <!-- KPI Cards Section -->
    <div style="padding: 40px 45px;">
        <!-- Table-based KPI cards -->
    </div>

    <!-- Footer Meta -->
    <div style="padding-top: 25px; border-top: 1px solid #e2e8f0; margin-top: 35px;">
        <!-- Period, Prepared By, etc. -->
    </div>
</div>
```

---

## Page Structure

### Report Page Layout

```xml
<div class="page" style="background: #ffffff !important; -webkit-print-color-adjust: exact !important;">

    <!-- Page Header -->
    <table style="width: 100%; padding-bottom: 10px; border-bottom: 2px solid #1a2744; margin-bottom: 20px;">
        <tr>
            <td style="vertical-align: middle; width: 65%;">
                <!-- Logo + Company -->
            </td>
            <td style="vertical-align: middle; text-align: right; width: 35%;">
                <!-- Page info -->
            </td>
        </tr>
    </table>

    <!-- Statement Title -->
    <div style="margin-bottom: 20px; text-align: center;">
        <h2 style="font-family: Georgia, serif; font-size: 22px; font-weight: bold; color: #1a2744; margin: 0 0 4px 0;">
            Report Title
        </h2>
        <span style="display: inline-block; margin-top: 8px; padding: 4px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 10px; font-weight: 500; color: #64748b;">
            For Period: 2024-01-01 to 2024-12-31
        </span>
    </div>

    <!-- Report Content -->
    <!-- ... section blocks, tables, etc. ... -->

    <!-- Notes Section -->
    <div style="margin-top: 20px; padding: 14px 18px; background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 0 5px 5px 0; -webkit-print-color-adjust: exact !important;">
        <div style="font-size: 9pt; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 6px;">
            Notes
        </div>
        <ul style="list-style: none; margin: 0; padding: 0;">
            <li style="font-size: 9pt; color: #64748b; padding: 2px 0;">Note item</li>
        </ul>
    </div>

    <!-- Page Footer -->
    <div style="margin-top: 25px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
        <table style="width: 100%;">
            <tr>
                <td style="font-size: 8pt; color: #94a3b8;">
                    Prepared by: User | Generated: 2024-01-01 12:00
                </td>
                <td style="text-align: right;">
                    <span style="font-size: 7pt; font-weight: 600; color: #94a3b8; text-transform: uppercase; padding: 3px 8px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 3px;">
                        Confidential
                    </span>
                </td>
            </tr>
        </table>
    </div>

</div>
```

---

## Value Formatting

### Currency Display

```python
# Python formatting
"{:,.2f}".format(1234567.89)  # "1,234,567.89"

# With currency symbol
f"{currency_symbol} {:,.2f}".format(amount)  # "AED 1,234,567.89"
```

### QWeb Value Classes

```xml
<!-- Positive value -->
<td class="ops-value-positive" style="color: #059669 !important;">
    1,234.56
</td>

<!-- Negative value -->
<td class="ops-value-negative" style="color: #dc2626 !important;">
    -567.89
</td>

<!-- Zero value -->
<td class="ops-value-zero" style="color: #94a3b8 !important;">
    0.00
</td>

<!-- Dynamic coloring in QWeb -->
<td t-attf-class="text-end #{value > 0 and 'ops-value-positive' or (value &lt; 0 and 'ops-value-negative' or 'ops-value-zero')}">
    <t t-esc="'{:,.2f}'.format(value)"/>
</td>
```

---

## Print Considerations

### Page Breaks

```css
/* Force page break after element */
page-break-after: always;

/* Prevent page break inside element */
page-break-inside: avoid;

/* Class for cover page */
.ops-cover-page {
    min-height: 100%;
    page-break-after: always;
}
```

### Paper Format

```xml
<record id="paperformat_ops_a4_financial" model="report.paperformat">
    <field name="name">OPS A4 Financial</field>
    <field name="format">A4</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">15</field>
    <field name="margin_bottom">15</field>
    <field name="margin_left">15</field>
    <field name="margin_right">15</field>
    <field name="header_spacing">5</field>
    <field name="dpi">96</field>
</record>
```

---

## Checklist

Before finalizing any PDF template:

- [ ] All layouts use `<table>` (no flex/grid)
- [ ] All colors are hex codes (no CSS variables)
- [ ] Colored backgrounds have `-webkit-print-color-adjust: exact`
- [ ] System fonts only (DejaVu Sans, Georgia, Courier)
- [ ] Cover page has `page-break-after: always`
- [ ] Tables prevent break inside (`page-break-inside: avoid`)
- [ ] Currency values use monospace font
- [ ] Positive=green, Negative=red, Zero=muted
- [ ] Headers have proper contrast (white on dark bg)
