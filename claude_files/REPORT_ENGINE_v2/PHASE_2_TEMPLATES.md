# PHASE 2: Base Templates + Report Actions
# Run with: claude -p "$(cat PHASE_2_TEMPLATES.md)"
# Prerequisite: Phase 1 completed
# Estimated: ~20 minutes

## CONTEXT
You are building QWeb templates for OPS Framework report engine v2 in `/opt/gemini_odoo19/addons/ops_matrix_accounting/`.
Read the master spec: `cat /opt/gemini_odoo19/addons/claude_files/REPORT_ENGINE_REWRITE_MASTER.md` — Sections 7 and 8.
Also read the existing corporate layout: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_corporate_report_layout.xml`
And the helpers model: `grep -n "def " /opt/gemini_odoo19/addons/ops_matrix_accounting/models/ops_report_helpers.py`

The data contracts are in: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_report_contracts.py`

## DESIGN PRINCIPLES
1. wkhtmltopdf renders these — NO CSS variables, NO flexbox, NO grid. Use tables and inline styles.
2. Colors come from `colors` dict passed by bridge parser. NEVER hardcode hex values.
3. The `helpers` object provides: `format_amount()`, `format_percentage()`, `get_value_color()`, `amount_to_words()`, etc.
4. Templates must work for ALL reports of that shape — no report-specific logic in shape templates.
5. Column visibility is driven by `data['visible_columns']` (Shape A) or `data['columns']` (Shape C).
6. Portrait for hierarchy reports (P&L, BS). Landscape for line/matrix reports (GL, TB, Aged).

## YOUR TASK

### File 1: `report/ops_report_base.xml`

Master layout template used by ALL reports. Contains:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- ============================================================ -->
    <!-- OPS REPORT BASE LAYOUT                                        -->
    <!-- Master template for all OPS corporate reports.                -->
    <!-- Contains: header, filter bar, content slot, notes, footer.    -->
    <!-- ============================================================ -->

    <!-- wkhtmltopdf external layout with OPS badge footer -->
    <template id="ops_report_external_layout">
        <div class="header" style="border:none !important; padding:0; margin:0; max-height:0; overflow:hidden;"/>
        <t t-out="0"/>
        <div class="footer" style="border:none !important; padding:0 12mm;">
            <span style="font-size:7pt; color:#94a3b8;">Powered by OPS Framework</span>
            <span style="float:right; font-size:8pt; color:#94a3b8;">
                Page <span class="page"/> of <span class="topage"/>
            </span>
        </div>
    </template>

    <!-- Main report body template -->
    <template id="ops_report_base">
        <t t-call="ops_matrix_accounting.ops_report_external_layout">
            <div t-attf-style="font-family: Arial, Helvetica, sans-serif; color: #{colors.get('body_text', '#1a1a1a')}; font-size: 9pt; padding: 0 4mm;">

                <!-- ==================== HEADER ==================== -->
                <div t-attf-style="border-bottom: 3px solid #{colors.get('primary', '#5B6BBB')}; padding-bottom: 10px; margin-bottom: 14px;">
                    <table style="width:100%; border-collapse:collapse;">
                        <tr>
                            <td style="width:60%; vertical-align:top;">
                                <div style="font-size:16pt; font-weight:bold;">
                                    <t t-out="meta.get('company_name', '')"/>
                                </div>
                                <div t-if="meta.get('company_vat')" style="font-size:8pt; color:#6b7280;">
                                    VAT: <t t-out="meta.get('company_vat', '')"/>
                                </div>
                            </td>
                            <td style="width:40%; text-align:right; vertical-align:top;">
                                <div t-attf-style="font-size:13pt; font-weight:bold; color:#{colors.get('primary', '#5B6BBB')};">
                                    <t t-out="meta.get('report_title', 'Report')"/>
                                </div>
                                <div style="font-size:8pt; color:#6b7280;">
                                    <t t-if="meta.get('date_from') and meta.get('date_to')">
                                        <t t-out="meta['date_from']"/> to <t t-out="meta['date_to']"/>
                                    </t>
                                    <t t-elif="meta.get('as_of_date')">
                                        As of <t t-out="meta['as_of_date']"/>
                                    </t>
                                </div>
                                <div style="font-size:7pt; color:#94a3b8; margin-top:2px;">
                                    Generated: <t t-out="meta.get('generated_at', '')"/>
                                </div>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- ==================== FILTER BAR ==================== -->
                <t t-set="filters" t-value="meta.get('filters', {})"/>
                <div t-if="filters"
                     t-attf-style="background:#{colors.get('primary_light', '#edeef5')}; padding:6px 10px; margin-bottom:14px; border-radius:3px; font-size:8pt;">
                    <t t-foreach="filters.items()" t-as="f">
                        <span style="margin-right:12px;">
                            <strong style="text-transform:capitalize;"><t t-out="f[0].replace('_', ' ')"/>: </strong>
                            <t t-if="isinstance(f[1], list)">
                                <t t-out="', '.join(str(v) for v in f[1])"/>
                            </t>
                            <t t-else="">
                                <t t-out="f[1]"/>
                            </t>
                        </span>
                    </t>
                </div>

                <!-- ==================== CONTENT SLOT ==================== -->
                <t t-out="0"/>

                <!-- ==================== NOTES ==================== -->
                <div style="margin-top:16px; font-size:7pt; color:#94a3b8; border-top:1px solid #e5e7eb; padding-top:6px;">
                    <span>All amounts in <t t-out="meta.get('currency_name', '')"/> unless otherwise stated.</span>
                    <span style="float:right;">
                        Prepared by <t t-out="meta.get('generated_by', '')"/>
                    </span>
                </div>
            </div>
        </t>
    </template>
</odoo>
```

### File 2: `report/ops_report_shape_lines.xml`

Shape A template — line-based reports (GL, Partner Ledger, Cash/Day/Bank Book).

Key requirements:
- Receives `data` dict matching ShapeAReport contract
- `data['visible_columns']` controls which columns render — loop dynamically
- Each group renders: group header → opening balance row → line rows → group total row
- Running balance is pre-computed in data (per-group, starting from opening)
- Color positive/negative balances using `colors['success']` / `colors['danger']`
- Grand totals row at the bottom
- Column headers use `colors['primary']` background with `colors['text_on_primary']` text
- Group header uses `colors['primary_light']` background
- Total rows use bold + top border
- Zebra striping on detail rows (every other row slightly shaded)

Column display mapping (template must handle all of these):
```
'date'         → Date
'entry'        → Entry / Ref#
'journal'      → Journal
'account_code' → Account Code
'account_name' → Account Name  
'label'        → Description
'ref'          → Reference
'partner'      → Partner
'branch'       → Branch
'bu'           → Business Unit
'debit'        → Debit (right-aligned, currency formatted)
'credit'       → Credit (right-aligned, currency formatted)
'balance'      → Balance (right-aligned, colored by sign)
'currency'     → Currency
'amount_currency' → Amount in Currency
```

The template iterates `data['visible_columns']` for headers and for each line. This makes it fully dynamic — adding a column to visible_columns automatically renders it.

Define a helper mapping inside the template:
```xml
<t t-set="col_labels" t-value="{'date':'Date','entry':'Entry','journal':'Jnl','account_code':'Code','account_name':'Account','label':'Description','ref':'Reference','partner':'Partner','branch':'Branch','bu':'BU','debit':'Debit','credit':'Credit','balance':'Balance','currency':'Curr','amount_currency':'FCY Amount'}"/>
<t t-set="col_align" t-value="{'debit':'right','credit':'right','balance':'right','amount_currency':'right'}"/>
<t t-set="col_type" t-value="{'debit':'number','credit':'number','balance':'number','amount_currency':'number'}"/>
```

### File 3: `report/ops_report_shape_hierarchy.xml`

Shape B template — hierarchy reports (P&L, BS, CF, Budget vs Actual).

Key requirements:
- Receives `data` dict matching ShapeBReport contract
- `data['value_columns']` defines the numeric columns: e.g. [{'key':'current','label':'Current Period'}, {'key':'previous','label':'Previous Period'}]
- Recursive rendering of `data['sections']` — each node can have children
- Indentation based on `node['level']` (10px per level)
- Row styling based on `node['style']`:
  - `section`: bold, primary_light background, font-size slightly larger
  - `group`: bold, slight indent
  - `detail`: normal, indented
  - `total`: bold, top border, primary background (or primary_light)
  - `grand_total`: bold, double top border, larger font
- `data['net_result']` renders at the very bottom as grand_total style
- Value formatting: use helpers.format_amount(), negative values in red

Create a recursive sub-template `ops_hierarchy_node` that calls itself for children.

### File 4: `report/ops_report_shape_matrix.xml`

Shape C template — matrix/table reports (TB, Aged, Inventory, Assets, Treasury).

Key requirements:
- Receives `data` dict matching ShapeCReport contract
- `data['columns']` defines ALL columns dynamically: key, label, col_type, align
- `data['rows']` contains all data rows with `values` dict keyed by column keys
- Row styling based on `row['style']`: header, detail, subtotal, total, grand_total
- Indentation on first column based on `row['level']`
- Column alignment from `col['align']`
- Number formatting based on `col['col_type']`: 'currency' → format_amount, 'percentage' → format_percentage
- `data['totals']` renders as final row
- Auto-width columns: numbers get smaller width, descriptions get larger

### File 5: `report/ops_report_actions.xml`

All `ir.actions.report` records. ONE per report type. All use the bridge parser.

Pattern for each:
```xml
<record id="action_report_gl" model="ir.actions.report">
    <field name="name">General Ledger</field>
    <field name="model">ops.gl.report.wizard</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">ops_matrix_accounting.report_general_ledger</field>
    <field name="report_file">ops_matrix_accounting.report_general_ledger</field>
    <field name="paperformat_id" ref="ops_matrix_accounting.ops_landscape_paperformat"/>
    <field name="binding_model_id" eval="False"/>
</record>
```

Create records for ALL 29 reports listed in master spec Section 5.
Use landscape paperformat for Shape A and C reports, portrait for Shape B.

Check which paperformat IDs exist: `grep "paperformat" /opt/gemini_odoo19/addons/ops_matrix_accounting/data/ops_paperformat.xml`

### File 6: `report/ops_report_configs.xml`

Per-report configuration templates. Each one:
1. Inherits the appropriate shape template
2. Sets report-specific variables (visible columns, display options)

Example for GL:
```xml
<template id="report_general_ledger">
    <t t-call="ops_matrix_accounting.ops_report_shape_lines"/>
</template>
```

For most reports, the template is just a t-call to the shape template because the wizard already controls visible_columns in the data contract. But some reports may need minor overrides.

Create configuration templates for all 29 reports.

### File 7: Update `__manifest__.py`

Add ALL new XML files to the data list (in correct order — base first, then shapes, then actions, then configs):
```python
# Report Engine v2 - Templates
"report/ops_report_base.xml",
"report/ops_report_shape_lines.xml",
"report/ops_report_shape_hierarchy.xml",
"report/ops_report_shape_matrix.xml",
"report/ops_report_actions.xml",
"report/ops_report_configs.xml",
# Keep existing
"report/ops_corporate_report_layout.xml",
"report/ops_report_invoice.xml",
"report/ops_report_payment.xml",
```

### Verification

```bash
cd /opt/gemini_odoo19/addons/ops_matrix_accounting
echo "=== New template files ===" && ls -la report/ops_report_*.xml
echo "=== Manifest check ===" && grep "ops_report_" __manifest__.py
echo "=== Template IDs ===" && grep 'template id=' report/ops_report_*.xml | head -40
echo "=== Report Actions ===" && grep 'record id=.*ir.actions.report' report/ops_report_actions.xml | wc -l
```

Expected: 29 ir.actions.report records, 29+ template IDs, 6 new XML files.

## RULES
- wkhtmltopdf compatible ONLY: no CSS variables, no flexbox, no grid, no modern CSS
- All colors via inline `t-attf-style` using `colors` dict — NEVER hardcode hex
- All amounts formatted via `helpers.format_amount()` or `helpers.format_percentage()`
- Negative values must show in `colors['danger']` color
- Zero values may show in `colors['zero']` color
- Tables use `border-collapse: collapse; width: 100%;`
- Font size: 9pt body, 8pt filters/notes, 7pt footer, 13pt title, 16pt company
- Do NOT include any report data logic — templates are PURE renderers
- Do NOT run odoo update yet
