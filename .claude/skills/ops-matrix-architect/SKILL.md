---
name: ops-matrix-architect
version: 1.0.0
description: The official development guide for the OPS Matrix Odoo 19 Framework. Enforces strict Security, Performance, and Legacy-PDF compatibility rules.
author: Antigravity AI
framework: Odoo 19.0
---

# OPS Matrix Architect

Use this skill for **ANY** code modification, report generation, or module creation within the OPS Framework.

## Quick Reference

| Aspect | Rule |
|--------|------|
| **Layout** | HTML Tables only (NO Flexbox, NO Grid) |
| **Colors** | Hex codes only (NO CSS variables) |
| **Print** | Always add `-webkit-print-color-adjust: exact` |
| **Security** | Always filter by `ops_branch_ids` |
| **Models** | Always inherit `ops.matrix.mixin` |
| **Performance** | Use `_read_group` for aggregation |

---

## CRITICAL RULES (The "Iron Laws")

### 1. PDF COMPATIBILITY (wkhtmltopdf)

The OPS Framework generates financial reports using wkhtmltopdf, which has limited CSS support.

| FORBIDDEN | REQUIRED |
|-----------|----------|
| `display: flex` | `<table>`, `<tr>`, `<td>` |
| `display: grid` | Table-based layouts |
| `var(--color)` | Direct hex codes (#DA291C) |
| `gap:`, `flex-direction:` | Table cell spacing |
| External fonts | System fonts only |

**Always include in colored elements:**
```css
-webkit-print-color-adjust: exact !important;
print-color-adjust: exact !important;
```

**Allowed CSS Properties:**
- `background-color`, `color`, `border`
- `padding`, `margin`
- `font-family` (system fonts only)
- `font-size`, `font-weight`
- `text-align`, `vertical-align`
- `width` (percentage or fixed)
- `display: inline-block`, `display: table`
- `float: left/right` (with clear)

### 2. SECURITY (The Iron Lock)

```python
# FORBIDDEN - Never bypass security
records = self.env['model'].sudo().search([])  # NO!

# REQUIRED - Always filter by branch
domain = self._apply_branch_filter([('state', '=', 'posted')])
records = self.env['model'].search(domain)

# REQUIRED - New models must inherit the mixin
class MyModel(models.Model):
    _name = 'ops.my.model'
    _inherit = ['ops.matrix.mixin']  # MANDATORY
```

**Security Checklist:**
- [ ] New model inherits `ops.matrix.mixin`
- [ ] Search domains include branch filter
- [ ] No `sudo()` without explicit authorization
- [ ] Access control CSV defined in security/
- [ ] Record rules defined for branch isolation

### 3. PERFORMANCE

```python
# FORBIDDEN - No loops for aggregation
total = 0
for rec in records:  # NO!
    total += rec.amount

# REQUIRED - Use _read_group
results = self.env['account.move.line']._read_group(
    domain=[('company_id', '=', company.id)],
    groupby=['account_id'],
    aggregates=['debit:sum', 'credit:sum'],
)
```

**Performance Checklist:**
- [ ] Use `_read_group` for sums/counts
- [ ] Limit recordset iterations
- [ ] Pre-fetch related records with `mapped()`
- [ ] Use `@api.depends` correctly to avoid recomputation
- [ ] Batch operations where possible

---

## DESIGN SYSTEM (Executive Theme)

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| **Primary Dark** | `#0a1628` | Cover backgrounds, headers |
| **Primary** | `#1a2744` | Section headers |
| **Secondary** | `#3b82f6` | Highlights, badges |
| **Success** | `#059669` | Revenue, positive values, profit |
| **Danger** | `#dc2626` | Expenses, negative values, loss |
| **Warning** | `#d97706` | Caution, liabilities |
| **Muted** | `#94a3b8` | Zero values, secondary text |
| **Text Dark** | `#1e293b` | Body text |
| **Text Light** | `#64748b` | Subtle text, labels |
| **Border** | `#e2e8f0` | Dividers, table borders |

### Typography

```css
/* Body Text */
font-family: 'DejaVu Sans', Helvetica, Arial, sans-serif;
font-size: 10pt;

/* Headings */
font-family: Georgia, 'Times New Roman', serif;

/* Monospace (numbers) */
font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
```

### Layout Pattern (Table-Based)

```xml
<!-- Sidebar + Content Layout -->
<table style="width: 100%;">
    <tr>
        <td style="width: 25%; vertical-align: top;">
            <!-- Sidebar content -->
        </td>
        <td style="width: 75%; vertical-align: top; padding-left: 20px;">
            <!-- Main content -->
        </td>
    </tr>
</table>

<!-- Multi-column Cards -->
<table style="width: 100%; border-collapse: separate; border-spacing: 12px 0;">
    <tr>
        <td style="width: 33%; vertical-align: top;">
            <!-- Card 1 -->
        </td>
        <td style="width: 33%; vertical-align: top;">
            <!-- Card 2 -->
        </td>
        <td style="width: 33%; vertical-align: top;">
            <!-- Card 3 -->
        </td>
    </tr>
</table>
```

---

## MODULE STRUCTURE

### Standard Layout

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
├── wizards/
│   ├── __init__.py
│   └── [wizard_name].py
├── report/
│   └── report_templates.xml
├── data/
│   └── default_data.xml
└── static/
    └── description/
        └── icon.png
```

### Manifest Template

```python
{
    'name': 'OPS Matrix - Module Name',
    'version': '19.0.1.0.0',
    'category': 'OPS Framework',
    'summary': 'Brief description of module purpose',
    'description': """
        OPS Matrix Module Name
        ======================
        Detailed description of functionality.
    """,
    'author': 'Antigravity AI',
    'website': 'https://github.com/MoeZayour/claude_ops',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'ops_matrix_core',  # REQUIRED - always include
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/model_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### Model Template

```python
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OpsMyModel(models.Model):
    """
    OPS Matrix Model

    Purpose: [Describe model purpose]
    Inherits: ops.matrix.mixin for branch/BU tracking
    """
    _name = 'ops.my.model'
    _description = 'OPS My Model'
    _inherit = ['ops.matrix.mixin']  # MANDATORY
    _order = 'create_date desc'

    # =========================================================================
    # Fields
    # =========================================================================

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    # =========================================================================
    # Compute Methods
    # =========================================================================

    # =========================================================================
    # CRUD Methods
    # =========================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add custom logic."""
        return super().create(vals_list)

    # =========================================================================
    # Business Methods
    # =========================================================================
```

---

## REPORT TEMPLATES

### QWeb Report Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Report Action -->
    <record id="action_report_my_document" model="ir.actions.report">
        <field name="name">My Report</field>
        <field name="model">ops.my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">ops_matrix_module.report_my_document</field>
        <field name="print_report_name">'Report_%s' % object.name</field>
        <field name="paperformat_id" ref="ops_matrix_accounting.paperformat_ops_a4_financial"/>
    </record>

    <!-- QWeb Template -->
    <template id="report_my_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="ops_matrix_accounting.ops_external_layout">
                    <div class="page" style="background: #ffffff !important;">
                        <!-- Report content using TABLE-BASED layouts -->
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

---

## VALIDATION CHECKLIST

Before committing any code, verify:

### Python Files
- [ ] Follows PEP 8 style
- [ ] 4-space indentation
- [ ] Max 120 characters per line
- [ ] Models inherit `ops.matrix.mixin`
- [ ] No `sudo()` usage
- [ ] Uses `_read_group` for aggregations
- [ ] Proper docstrings

### XML/QWeb Files
- [ ] 2-space indentation
- [ ] No Flexbox or Grid
- [ ] Table-based layouts
- [ ] Hex color codes (no CSS variables)
- [ ] `-webkit-print-color-adjust: exact` on colored elements
- [ ] System fonts only

### Security
- [ ] ir.model.access.csv defined
- [ ] Record rules for branch isolation
- [ ] Branch filter in search domains

### Testing
- [ ] Tested in Odoo shell
- [ ] Module update successful
- [ ] No errors in logs
- [ ] PDF generation works

---

## REFERENCES

- **Architecture Guide:** `references/ops_architecture.md`
- **Style Guide:** `references/ops_style_guide.md`
- **Golden CSS Template:** `assets/ops_executive_css.xml`
- **Module Scaffold Script:** `scripts/ops_scaffold.py`

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01 | Initial release - Phase 20 |
