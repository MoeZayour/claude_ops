# How-To: Create a New Financial Report

**Audience:** Developers

This guide demonstrates how to create a new, professionally styled financial report by leveraging the OPS Framework's existing "Meridian Native" reporting engine.

**Goal:** We will create a new "Aged Receivables" report.

---

## Guiding Principles

- **Inherit, Don't Recreate:** The framework provides a base wizard (`ops.base.report.wizard`) and QWeb templates. Always extend them.
- **Use Existing Styles:** The Meridian Native design system provides CSS classes for tables, colors, and typography. Use them for a consistent look and feel.
- **Separate Logic and Presentation:** The Python wizard should handle data computation, and the QWeb template should handle rendering.

---

## Step 1: Create the Report Wizard

The wizard defines the user-facing options and contains the logic to fetch and process the report data.

**File: `my_ops_extensions/wizard/aged_receivables_wizard.py`**
```python
from odoo import models, fields

class AgedReceivablesWizard(models.TransientModel):
    _name = 'my.aged.receivables.wizard'
    _inherit = 'ops.base.report.wizard' # Inherit the base wizard
    _description = 'Aged Receivables Report Wizard'

    partner_ids = fields.Many2many('res.partner', string='Partners', domain="[('customer_rank', '>', 0)]")

    def _get_report_name(self):
        # This must match the report action name in Step 3
        return 'my_ops_extensions.action_aged_receivables_report'

    def _get_report_data(self):
        # This is where your report logic goes.
        # It should return a dictionary of data for the QWeb template.
        # For simplicity, we'll use dummy data here.
        # In a real scenario, you would query account.move.line.
        
        data = {
            'partners': [
                {'name': 'Customer A', 'bucket_30': 5000, 'bucket_60': 2000, 'total': 7000},
                {'name': 'Customer B', 'current': 10000, 'total': 10000},
            ],
            'totals': {
                'current': 10000, 'bucket_30': 5000, 'bucket_60': 2000, 'grand_total': 17000
            },
            'buckets': ['Current', '1-30', '31-60', '61-90', '90+'],
        }
        return data
```

## Step 2: Create the QWeb Report Template

This XML file defines the visual layout of your PDF report. It calls the `_get_report_data` method from the wizard to get its data.

**File: `my_ops_extensions/report/aged_receivables_template.xml`**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="report_aged_receivables_document">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <!-- This calls the base template with header, footer, and styles -->
                <t t-call="ops_matrix_accounting.ops_report_layout">
                    <div class="page">
                        <t t-set="report_data" t-value="doc._get_report_data()"/>
                        <h3>Aged Receivables</h3>
                        
                        <!-- Use existing Meridian Native CSS classes -->
                        <table class="ops-native-table" width="100%">
                            <thead>
                                <tr class="section-header">
                                    <th>Customer</th>
                                    <th class="text-right">Current</th>
                                    <th class="text-right">1-30 Days</th>
                                    <th class="text-right">31-60 Days</th>
                                    <th class="text-right">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-foreach="report_data['partners']" t-as="partner">
                                    <tr>
                                        <td><t t-esc="partner['name']"/></td>
                                        <td class="text-right"><span t-field="partner['current']" t-options='{"widget": "monetary", "display_currency": doc.company_id.currency_id}'/></td>
                                        <td class="text-right"><span t-field="partner['bucket_30']" t-options='{"widget": "monetary", "display_currency": doc.company_id.currency_id}'/></td>
                                        <td class="text-right"><span t-field="partner['bucket_60']" t-options='{"widget": "monetary", "display_currency": doc.company_id.currency_id}'/></td>
                                        <td class="text-right"><strong><span t-field="partner['total']" t-options='{"widget": "monetary", "display_currency": doc.company_id.currency_id}'/></strong></td>
                                    </tr>
                                </t>
                            </tbody>
                        </table>
                    </div>
                </t>
            </t>
        </t>
    </template>
</odoo>
```

## Step 3: Create the Report Action and Menu Item

This XML file registers your report with Odoo and adds a menu item so users can access it.

**File: `my_ops_extensions/report/report_actions.xml`**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Report Action -->
    <record id="action_aged_receivables_report" model="ir.actions.report">
        <field name="name">Aged Receivables</field>
        <field name="model">my.aged.receivables.wizard</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_ops_extensions.report_aged_receivables_document</field>
        <field name="report_file">my_ops_extensions.report_aged_receivables_document</field>
        <field name="paperformat_id" ref="ops_matrix_accounting.ops_paperformat_a4"/>
        <field name="binding_model_id" eval="False"/>
        <field name="binding_type">report</field>
    </record>

    <!-- Wizard View -->
    <record id="view_aged_receivables_wizard" model="ir.ui.view">
        <field name="name">Aged Receivables Wizard</field>
        <field name="model">my.aged.receivables.wizard</field>
        <field name="arch" type="xml">
            <form>
                <group>
                    <field name="partner_ids" widget="many2many_tags"/>
                </group>
                <footer>
                    <button name="action_print_report" string="Print" type="object" class="btn-primary"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Menu Item -->
    <record id="menu_aged_receivables_report" model="ir.actions.act_window">
        <field name="name">Aged Receivables Report</field>
        <field name="res_model">my.aged.receivables.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>

    <menuitem id="menu_item_aged_receivables"
              name="Aged Receivables"
              parent="account.menu_finance_reports"
              action="menu_aged_receivables_report"
              sequence="100"/>
</odoo>
```

## Step 4: Update Manifest and Install

1.  Add the new Python and XML files to your `__manifest__.py`.
2.  Install or upgrade your module.
3.  Navigate to **Invoicing → Reports → Aged Receivables** to launch your new report wizard.