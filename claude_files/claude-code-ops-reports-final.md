# Claude Code Implementation Prompt
## OPS Framework Financial Reports — Build on Existing Meridian Native Engine

---

## CRITICAL: YOUR EXISTING INFRASTRUCTURE

Your project already has a mature reporting engine. **DO NOT recreate what exists.**

### Existing Architecture Summary

```
addons/ops_matrix_accounting/
├── report/
│   ├── ops_report_layout.xml          ← MERIDIAN NATIVE ENGINE (Master CSS)
│   ├── ops_financial_report_template.xml  ← P&L, BS, TB, CF templates
│   ├── ops_asset_report_templates.xml
│   ├── ops_consolidated_report_templates.xml
│   └── ops_general_ledger_template.xml
├── wizard/
│   ├── ops_base_report_wizard.py      ← BASE CLASS (inherit from this!)
│   ├── ops_financial_report_wizard.py
│   ├── ops_asset_report_wizard.py
│   ├── ops_treasury_report_wizard.py
│   └── ops_inventory_report_wizard.py
├── data/
│   ├── ops_paperformat.xml            ← A4 paper format
│   └── report_templates.xml
└── static/src/css/
    ├── ops_accounting.css
    └── ops_report.css
```

### Your Design System: MERIDIAN NATIVE

**Color Tokens (Already Defined):**
```css
/* DO NOT REDEFINE - Use these existing classes */
GOLD: #C9A962      /* Executive Gold - Brand accent */
BLACK: #1A1A1A     /* Primary Black - Text/headers */
RED: #DA291C       /* Corporate Red - Negatives */
MUTED: #FAFAFA     /* Light Grey - Backgrounds */
ZERO: #cccccc      /* Zero values display */
GREEN: #059669     /* Revenue/Profit */
BLUE: #2563eb      /* Assets */
ORANGE: #d97706    /* Liabilities/Warning */
```

**Typography (Already Set):**
- Headers: Arial, Helvetica, sans-serif
- Numbers: Georgia, 'Times New Roman', serif
- Body: 10pt default

**Existing CSS Classes (USE THESE):**
```css
/* Tables */
.ops-native-table, .ops-meridian-table, .ops-table-consulting

/* Row Types */
tr.section-header    /* Section title row */
tr.subtotal-row      /* Subtotal with gray bg */
tr.total-row         /* Single top, DOUBLE bottom border */
tr.grand-total-row   /* Black background, white text */

/* Indentation */
.indent-0, .indent-1, .indent-2, .indent-3
.level-0, .level-1, .level-2, .level-3

/* Values */
.ops-value-zero      /* color: #cccccc */
.ops-value-negative  /* color: #DA291C with parentheses */
.ops-value-positive  /* color: #000000 */

/* Section Headers (Colored) */
.ops-section-header.revenue   /* Green #059669 */
.ops-section-header.expense   /* Red #DA291C */
.ops-section-header.asset     /* Blue #2563eb */
.ops-section-header.liability /* Orange #d97706 */
.ops-section-header.neutral   /* Black #1A1A1A */
.ops-section-header.gold      /* Gold #C9A962 */

/* KPI Cards */
.ops-kpi-strip, .ops-kpi-card

/* Aging Buckets */
.ops-aging-current, .ops-aging-30, .ops-aging-60, .ops-aging-90, .ops-aging-over
```

**Existing Helper Templates (USE THESE):**
```xml
ops_matrix_accounting.ops_report_styles          <!-- Master CSS -->
ops_matrix_accounting.ops_meridian_header_template
ops_matrix_accounting.ops_equation_bar_template  <!-- Balance Sheet equation -->
ops_matrix_accounting.ops_meta_bar_template
ops_matrix_accounting.ops_format_amount          <!-- Number formatting -->
ops_matrix_accounting.ops_report_footer_template
ops_matrix_accounting.ops_notes_template
ops_matrix_accounting.ops_component_signature_block (if exists)
```

---

## PHASE 1: INVESTIGATE FIRST

Before implementing, examine these files:

```bash
# 1. Understand the base wizard pattern
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_base_report_wizard.py

# 2. See how financial wizard extends it
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_financial_report_wizard.py

# 3. Check existing report actions
grep -r "ir.actions.report" /opt/gemini_odoo19/addons/ops_matrix_accounting --include="*.xml" | head -20

# 4. See what reports are already implemented
grep -r "report_type" /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/*.py
```

---

## PHASE 2: REPORTS TO IMPLEMENT

Based on OPS_FRAMEWORK_FEATURES_MASTER.md, implement these missing reports:

### Already Exists (DO NOT RECREATE):
- ✅ Balance Sheet (bs)
- ✅ Profit & Loss (pl)
- ✅ Trial Balance (tb)
- ✅ Cash Flow (cf)
- ✅ General Ledger (basic)

### Need to Implement:

#### Ledger Intelligence Engine
1. **Aged Receivables** — `ops_matrix_accounting.ops_aged_receivables_report`
2. **Aged Payables** — `ops_matrix_accounting.ops_aged_payables_report`
3. **Partner Ledger** — `ops_matrix_accounting.ops_partner_ledger_report`

#### Asset Intelligence Engine (Check ops_asset_report_templates.xml first)
4. **Fixed Asset Register** — Likely exists, may need enhancement
5. **Depreciation Schedule** — Projection view
6. **CAPEX Analysis** — Budget vs Actual

#### Inventory Intelligence Engine
7. **Stock Valuation** — By location/category
8. **Dead Stock Analysis** — Items >180 days no movement
9. **Movement Analysis (ABC)** — Velocity classification

#### Treasury Intelligence Engine
10. **Cash Outflow Forecast** — Weekly projection
11. **PDC Registry** — Inbound/Outbound checks

#### Consolidated Intelligence
12. **Consolidated Statements** — Multi-company with eliminations

---

## PHASE 3: IMPLEMENTATION PATTERN

### Step 1: Extend Base Wizard

```python
# In wizard/ops_ledger_report_wizard.py

from odoo import models, fields, api
from .ops_base_report_wizard import OPSBaseReportWizard

class OPSLedgerReportWizard(models.TransientModel):
    _name = 'ops.ledger.report.wizard'
    _inherit = 'ops.base.report.wizard'  # CRITICAL: Inherit base!
    _description = 'Ledger Reports Wizard'

    # Ledger-specific fields
    report_type = fields.Selection([
        ('aged_ar', 'Aged Receivables'),
        ('aged_ap', 'Aged Payables'),
        ('partner_ledger', 'Partner Ledger'),
    ], string='Report Type', required=True, default='aged_ar')
    
    partner_ids = fields.Many2many('res.partner', string='Partners')
    aging_method = fields.Selection([
        ('due_date', 'By Due Date'),
        ('invoice_date', 'By Invoice Date'),
    ], default='due_date')
    
    def _get_engine_name(self):
        return 'ledger'
    
    def _get_report_titles(self):
        return {
            'aged_ar': 'Aged Receivables',
            'aged_ap': 'Aged Payables',
            'partner_ledger': 'Partner Ledger',
        }
    
    def _compute_report_data(self):
        """Override to compute ledger-specific data."""
        if self.report_type == 'aged_ar':
            return self._compute_aged_receivables()
        elif self.report_type == 'aged_ap':
            return self._compute_aged_payables()
        elif self.report_type == 'partner_ledger':
            return self._compute_partner_ledger()
    
    def _compute_aged_receivables(self):
        """Compute aged receivables buckets."""
        # Implementation here
        return {
            'partners': [...],
            'totals': {...},
            'buckets': ['Current', '1-30', '31-60', '61-90', '90+'],
        }
```

### Step 2: Create QWeb Template

```xml
<!-- In report/ops_ledger_report_templates.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Include master styles -->
    <template id="ops_ledger_report_document" name="OPS Ledger Reports">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="ops_matrix_accounting.ops_report_styles"/>
                
                <div class="ops-meridian-page">
                    <!-- Gold Accent Bar -->
                    <div style="height: 4px; background-color: #C9A962; margin-bottom: 20px;"></div>
                    
                    <!-- Use existing header template -->
                    <t t-call="ops_matrix_accounting.ops_meridian_header_template">
                        <t t-set="report_title" t-value="doc.report_title"/>
                        <t t-set="company_name" t-value="doc.company_id.name"/>
                        <t t-set="date_from" t-value="doc.date_from"/>
                        <t t-set="date_to" t-value="doc.date_to"/>
                    </t>
                    
                    <!-- Report-specific content -->
                    <t t-if="doc.report_type == 'aged_ar'">
                        <t t-call="ops_matrix_accounting.ops_aged_receivables_content"/>
                    </t>
                    <t t-elif="doc.report_type == 'aged_ap'">
                        <t t-call="ops_matrix_accounting.ops_aged_payables_content"/>
                    </t>
                </div>
            </t>
        </t>
    </template>

    <!-- Aged Receivables Content -->
    <template id="ops_aged_receivables_content">
        <t t-set="report_data" t-value="doc._compute_report_data()"/>
        
        <!-- KPI Summary Strip (use existing pattern) -->
        <table width="100%" style="border-collapse: separate; border-spacing: 12px 0; margin-bottom: 25px;">
            <tr>
                <td style="background-color: #ffffff; border: 1px solid #e5e7eb; border-left: 4px solid #C9A962; padding: 16px 18px; width: 25%;">
                    <div style="font-size: 8pt; font-weight: 600; color: #6b7280; text-transform: uppercase;">Total Receivable</div>
                    <div style="font-family: Georgia, serif; font-size: 18pt; font-weight: 700; color: #1A1A1A; margin-top: 6px;">
                        <t t-esc="'{:,.0f}'.format(report_data.get('total_receivable', 0))"/>
                    </div>
                </td>
                <td style="background-color: #ffffff; border: 1px solid #e5e7eb; border-left: 4px solid #2563eb; padding: 16px 18px; width: 25%;">
                    <div style="font-size: 8pt; font-weight: 600; color: #6b7280; text-transform: uppercase;">DSO</div>
                    <div style="font-family: Georgia, serif; font-size: 18pt; font-weight: 700; color: #1A1A1A; margin-top: 6px;">
                        <t t-esc="report_data.get('dso', 0)"/> Days
                    </div>
                </td>
                <td style="background-color: #ffffff; border: 1px solid #e5e7eb; border-left: 4px solid #DA291C; padding: 16px 18px; width: 25%;">
                    <div style="font-size: 8pt; font-weight: 600; color: #6b7280; text-transform: uppercase;">Overdue</div>
                    <div style="font-family: Georgia, serif; font-size: 18pt; font-weight: 700; color: #DA291C; margin-top: 6px;">
                        <t t-esc="'{:.1f}%'.format(report_data.get('overdue_pct', 0))"/>
                    </div>
                </td>
                <td style="background-color: #ffffff; border: 1px solid #e5e7eb; border-left: 4px solid #059669; padding: 16px 18px; width: 25%;">
                    <div style="font-size: 8pt; font-weight: 600; color: #6b7280; text-transform: uppercase;">Risk Level</div>
                    <div t-attf-style="font-family: Georgia, serif; font-size: 14pt; font-weight: 700; color: #{report_data.get('risk_color', '#1A1A1A')}; margin-top: 6px;">
                        <t t-esc="report_data.get('risk_level', 'Normal')"/>
                    </div>
                </td>
            </tr>
        </table>
        
        <!-- Aging Table - Use existing table classes -->
        <div style="padding: 10px 14px; background-color: #1A1A1A !important; color: #ffffff; font-weight: 700; font-size: 11pt; text-transform: uppercase; letter-spacing: 0.5px;">
            <table width="100%"><tr>
                <td>Aged Receivables by Customer</td>
                <td style="text-align: right; font-family: Georgia, serif;"><t t-esc="len(report_data.get('partners', []))"/> Customers</td>
            </tr></table>
        </div>
        
        <table class="ops-native-table" width="100%">
            <thead>
                <tr>
                    <th style="background-color: #f8f9fa; padding: 12px 10px; text-align: left; font-size: 8pt; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #000000;">Customer</th>
                    <th class="ops-aging-current" style="padding: 12px 10px; text-align: right; font-size: 8pt; font-weight: 600; border-bottom: 2px solid #000000; width: 90px;">Current</th>
                    <th class="ops-aging-30" style="padding: 12px 10px; text-align: right; font-size: 8pt; font-weight: 600; border-bottom: 2px solid #000000; width: 90px;">1-30</th>
                    <th class="ops-aging-60" style="padding: 12px 10px; text-align: right; font-size: 8pt; font-weight: 600; border-bottom: 2px solid #000000; width: 90px;">31-60</th>
                    <th class="ops-aging-90" style="padding: 12px 10px; text-align: right; font-size: 8pt; font-weight: 600; border-bottom: 2px solid #000000; width: 90px;">61-90</th>
                    <th class="ops-aging-over" style="padding: 12px 10px; text-align: right; font-size: 8pt; font-weight: 600; border-bottom: 2px solid #000000; width: 90px;">90+</th>
                    <th style="background-color: #f8f9fa; padding: 12px 10px; text-align: right; font-size: 8pt; font-weight: 600; border-bottom: 2px solid #000000; width: 100px;">Total</th>
                </tr>
            </thead>
            <tbody>
                <t t-foreach="report_data.get('partners', [])" t-as="partner">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">
                            <t t-esc="partner.get('name', '')"/>
                        </td>
                        <t t-foreach="['current', 'bucket_30', 'bucket_60', 'bucket_90', 'bucket_over']" t-as="bucket">
                            <t t-set="val" t-value="partner.get(bucket, 0)"/>
                            <td style="padding: 10px; text-align: right; font-family: Georgia, serif; border-bottom: 1px solid #e5e7eb;">
                                <t t-if="val == 0"><span style="color: #cccccc;">—</span></t>
                                <t t-else=""><t t-esc="'{:,.0f}'.format(val)"/></t>
                            </td>
                        </t>
                        <td style="padding: 10px; text-align: right; font-family: Georgia, serif; font-weight: 600; border-bottom: 1px solid #e5e7eb; background-color: #f8f9fa;">
                            <t t-esc="'{:,.0f}'.format(partner.get('total', 0))"/>
                        </td>
                    </tr>
                </t>
            </tbody>
            <!-- Grand Total Row -->
            <tfoot>
                <tr class="grand-total-row">
                    <td style="padding: 14px 10px; font-weight: 700; background-color: #1A1A1A !important; color: #ffffff !important;">TOTAL</td>
                    <t t-foreach="['total_current', 'total_30', 'total_60', 'total_90', 'total_over']" t-as="total_key">
                        <td style="padding: 14px 10px; text-align: right; font-family: Georgia, serif; font-weight: 700; background-color: #1A1A1A !important; color: #ffffff !important;">
                            <t t-esc="'{:,.0f}'.format(report_data.get(total_key, 0))"/>
                        </td>
                    </t>
                    <td style="padding: 14px 10px; text-align: right; font-family: Georgia, serif; font-weight: 700; font-size: 12pt; background-color: #1A1A1A !important; color: #ffffff !important;">
                        <t t-esc="'{:,.0f}'.format(report_data.get('total_receivable', 0))"/>
                    </td>
                </tr>
            </tfoot>
        </table>
        
        <!-- Notes -->
        <t t-call="ops_matrix_accounting.ops_notes_template">
            <t t-set="target_move" t-value="doc.target_move"/>
        </t>
    </template>
</odoo>
```

### Step 3: Register Report Action

```xml
<!-- In data/report_templates.xml or separate file -->
<record id="action_ops_aged_receivables_report" model="ir.actions.report">
    <field name="name">Aged Receivables</field>
    <field name="model">ops.ledger.report.wizard</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">ops_matrix_accounting.ops_ledger_report_document</field>
    <field name="report_file">ops_matrix_accounting.ops_ledger_report_document</field>
    <field name="paperformat_id" ref="ops_paperformat_a4"/>
    <field name="binding_type">report</field>
</record>
```

---

## DESIGN SPECS REFERENCE FILES

Read these files for detailed layout specifications:

1. **`01-design-system-and-balance-sheet.md`** — Design tokens, components, Balance Sheet
2. **`02-pnl-cashflow-trialbalance-aging.md`** — Aging reports with risk highlighting
3. **`03-assets-inventory-treasury-consolidated.md`** — Asset, Inventory, Treasury, Consolidated

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Ledger Reports
- [ ] Examine existing `ops_base_report_wizard.py` structure
- [ ] Create `ops_ledger_report_wizard.py` extending base
- [ ] Create `ops_ledger_report_templates.xml`
- [ ] Implement Aged Receivables (with risk color coding)
- [ ] Implement Aged Payables (with payment priority)
- [ ] Implement Partner Ledger (with running balance)
- [ ] Add wizard views and menu items

### Phase 2: Inventory Reports
- [ ] Create `ops_inventory_report_wizard.py` (check if exists)
- [ ] Implement Stock Valuation by location
- [ ] Implement Dead Stock Analysis (>180 days)
- [ ] Implement Movement Analysis (ABC classification)

### Phase 3: Treasury Reports
- [ ] Enhance `ops_treasury_report_wizard.py`
- [ ] Implement Cash Outflow Forecast (weekly view)
- [ ] Implement PDC Registry (dual inbound/outbound)

### Phase 4: Integration
- [ ] Add menu items under Accounting → Reports → OPS Intelligence
- [ ] Test PDF generation with wkhtmltopdf
- [ ] Verify aging bucket colors render correctly
- [ ] Test with actual data

---

## CRITICAL REMINDERS

1. **INHERIT from `ops.base.report.wizard`** — Don't recreate base functionality
2. **USE existing CSS classes** — `.ops-native-table`, `.ops-value-zero`, etc.
3. **USE existing templates** — `ops_meridian_header_template`, `ops_format_amount`
4. **TABLE-BASED layouts only** — NO flexbox, NO grid (wkhtmltopdf limitation)
5. **Inline styles for reliability** — wkhtmltopdf can be finicky with external CSS
6. **ZEROS as "0.00" in gray** — Not blank, not dash (per Meridian standard)
7. **NEGATIVES in RED with parentheses** — `(1,234.56)` format
8. **Georgia serif for ALL numbers** — Brand standard

---

## QUICK START COMMAND

```bash
# Start by understanding the base wizard
cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_base_report_wizard.py | head -200

# Then implement ledger reports following the pattern
```
