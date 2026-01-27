# OPS Matrix Architect

Apply the OPS Matrix Framework standards when creating or modifying code, reports, or modules.

---

## Iron Laws (MUST FOLLOW)

### 1. PDF Compatibility (wkhtmltopdf)

| FORBIDDEN | REQUIRED |
|-----------|----------|
| `display: flex` | `<table>`, `<tr>`, `<td>` |
| `display: grid` | Table-based layouts |
| `var(--color)` | Direct hex codes (#DA291C) |
| `gap:`, `flex-direction:` | Table cell spacing |
| External fonts | System fonts only |

**Always on colored elements:**
```css
-webkit-print-color-adjust: exact !important;
print-color-adjust: exact !important;
```

### 2. Security (Branch Isolation)

```python
# FORBIDDEN
records = self.env['model'].sudo().search([])

# REQUIRED - Always filter by branch
domain = self._apply_branch_filter([('state', '=', 'posted')])
records = self.env['model'].search(domain)

# New models MUST inherit mixin
class MyModel(models.Model):
    _name = 'ops.my.model'
    _inherit = ['ops.matrix.mixin']  # MANDATORY
```

### 3. Performance (Use _read_group)

```python
# FORBIDDEN - No loops for aggregation
total = 0
for rec in records:
    total += rec.amount

# REQUIRED - Use _read_group
results = self.env['account.move.line']._read_group(
    domain=[('company_id', '=', company.id)],
    groupby=['account_id'],
    aggregates=['debit:sum', 'credit:sum'],
)
```

---

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Primary Dark | `#0a1628` | Cover backgrounds, headers |
| Primary | `#1a2744` | Section headers |
| Secondary | `#3b82f6` | Highlights, badges |
| Success | `#059669` | Revenue, profit, positive |
| Danger | `#dc2626` | Expenses, loss, negative |
| Warning | `#d97706` | Caution, liabilities |
| Muted | `#94a3b8` | Zero values |
| Text Dark | `#1e293b` | Body text |
| Border | `#e2e8f0` | Dividers |

---

## Typography

```css
/* Body */
font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;

/* Headings */
font-family: Georgia, 'Times New Roman', serif;

/* Numbers */
font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
```

---

## Layout Patterns

```xml
<!-- Two Column -->
<table style="width: 100%;">
    <tr>
        <td style="width: 50%; vertical-align: top;">Left</td>
        <td style="width: 50%; vertical-align: top;">Right</td>
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
```

---

## Module Structure

```
ops_matrix_[name]/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── [model_name].py
├── views/
│   └── [model_name]_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security_rules.xml
├── report/
│   └── report_templates.xml
└── static/description/icon.png
```

---

## Model Template

```python
from odoo import models, fields, api

class OpsMyModel(models.Model):
    _name = 'ops.my.model'
    _description = 'OPS My Model'
    _inherit = ['ops.matrix.mixin']  # MANDATORY
    _order = 'create_date desc'

    name = fields.Char(string='Name', required=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)
```

---

## QWeb Report Template

```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="ops_matrix_accounting.ops_external_layout">
                <div class="page" style="background: #ffffff !important;">
                    <!-- TABLE-BASED content only -->
                </div>
            </t>
        </t>
    </t>
</template>
```

---

## Validation Checklist

### Python
- [ ] PEP 8 style
- [ ] Models inherit `ops.matrix.mixin`
- [ ] No `sudo()` without authorization
- [ ] Uses `_read_group` for aggregations

### XML/QWeb
- [ ] No Flexbox or Grid
- [ ] Table-based layouts
- [ ] Hex color codes (no CSS vars)
- [ ] `-webkit-print-color-adjust: exact` on colors
- [ ] System fonts only

### Security
- [ ] ir.model.access.csv defined
- [ ] Record rules for branch isolation
- [ ] Branch filter in search domains

---

## References

Full documentation available at:
- Architecture: `ops-matrix-architect/references/ops_architecture.md`
- Style Guide: `ops-matrix-architect/references/ops_style_guide.md`
- CSS Template: `ops-matrix-architect/assets/ops_executive_css.xml`
- Scaffold Script: `ops-matrix-architect/scripts/ops_scaffold.py`
