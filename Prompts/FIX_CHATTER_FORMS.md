
# Fix Chatter/Layout Issues in OPS Framework Forms

## Reference
Based on audit performed on 2025-01-XX

## Phase 1: Fix Wizard Forms (Remove <sheet>, Add <footer>)

### Pattern to Apply:
```xml
<!-- BEFORE (Wrong) -->
<form string="Wizard Name">
    <sheet>
        <group>
            <field name="field1"/>
        </group>
    </sheet>
</form>

<!-- AFTER (Correct) -->
<form string="Wizard Name">
    <group>
        <field name="field1"/>
    </group>
    <footer>
        <button string="Generate" type="object" name="action_generate" class="btn-primary"/>
        <button string="Cancel" special="cancel" class="btn-secondary"/>
    </footer>
</form>
```

### Files to Fix:
1. `ops_matrix_accounting/views/ops_financial_report_wizard_views.xml`
2. `ops_matrix_accounting/views/ops_general_ledger_wizard_enhanced_views.xml`
3. `ops_matrix_accounting/views/ops_general_ledger_wizard_views.xml`
4. `ops_matrix_accounting/views/ops_reporting_views.xml`
5. `ops_matrix_core/views/ops_governance_violation_report_views.xml`
6. `ops_matrix_reporting/views/ops_excel_export_wizard_views.xml`

---

## Phase 2: Add Full Chatter to Transactional Models

### Step 2A: Update Python Models
Add `mail.thread` and `mail.activity.mixin` inheritance:

**Files to modify:**
- `ops_matrix_accounting/models/ops_asset.py`
- `ops_matrix_accounting/models/ops_asset_depreciation.py`
- `ops_matrix_accounting/models/ops_budget.py`
- `ops_matrix_accounting/models/ops_pdc.py`
- `ops_matrix_core/models/ops_inter_branch_transfer.py`
- `ops_matrix_core/models/ops_product_request.py`
- `ops_matrix_core/models/ops_sla_instance.py`

**Pattern:**
```python
class OpsAsset(models.Model):
    _name = 'ops.asset'
    _description = 'OPS Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ADD THIS
    
    name = fields.Char(required=True, tracking=True)  # ADD tracking=True
    state = fields.Selection([...], tracking=True)
```

### Step 2B: Update XML Views
Add `<chatter/>` after `</sheet>`:

**Files to modify:**
- `ops_matrix_accounting/views/ops_asset_views.xml`
- `ops_matrix_accounting/views/ops_asset_depreciation_views.xml`
- `ops_matrix_accounting/views/ops_budget_views.xml`
- `ops_matrix_accounting/views/ops_pdc_views.xml`
- `ops_matrix_core/views/ops_inter_branch_transfer_views.xml`
- `ops_matrix_core/views/ops_product_request_views.xml`
- `ops_matrix_core/views/ops_sla_instance_views.xml`

**Pattern:**
```xml
<form string="Asset">
    <header>
        <!-- buttons/status -->
    </header>
    <sheet>
        <!-- form content -->
    </sheet>
    <chatter/>  <!-- ADD THIS LINE -->
</form>
```

---

## Phase 3: Fix Configuration Forms

### Option A: Add Simple Chatter (for auditable configs)
Apply to:
- `ops_matrix_accounting/views/ops_asset_category_views.xml`
- `ops_matrix_core/views/ops_api_key_views.xml`

### Option B: Use o_form_nosheet (for simple lookups)
Apply to:
- `ops_matrix_core/views/ops_analytic_views.xml`
- `ops_matrix_core/views/ops_dashboard_config_views.xml`
- `ops_matrix_core/views/ops_audit_log_views.xml`

**Pattern:**
```xml
<form string="Config" class="o_form_nosheet">
    <group>
        <field name="name"/>
    </group>
</form>
```

---

## Phase 4: Special Handling - res_company_views.xml

This extends Odoo's base company form. The base already has chatter.
Check if your extension is using `<xpath>` correctly:

```xml
<record id="view_company_form_ops" model="ir.ui.view">
    <field name="name">res.company.form.ops</field>
    <field name="model">res.company</field>
    <field name="inherit_id" ref="base.view_company_form"/>
    <field name="arch" type="xml">
        <xpath expr="//sheet" position="inside">
            <notebook position="inside">
                <page string="OPS Settings">
                    <!-- Your fields -->
                </page>
            </notebook>
        </xpath>
    </field>
</record>
```

---

## Validation Checklist

After fixes, verify:
- [ ] All wizard forms open as modal dialogs (no sheet)
- [ ] All transactional forms show chatter on right side
- [ ] All config forms are centered properly
- [ ] No forms pushed to extreme left
- [ ] Module upgrades without errors
```

---
