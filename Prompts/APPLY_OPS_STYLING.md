# Apply Consistent UI Styling Across OPS Matrix Framework

## Objective
Apply professional, consistent styling (colors, icons, decorations) across all OPS Framework forms following the established style guide. Enhance usability without compromising the professional appearance of an enterprise-grade accounting framework.

## Working Directory
`/opt/gemini_odoo19/addons/`

## Target Modules
- ops_matrix_core
- ops_matrix_accounting
- ops_matrix_reporting

---

## PHASE 1: Create Shared CSS Theme File

### File: `ops_matrix_core/static/src/css/ops_theme.css`

```css
/*
 * OPS Matrix Framework - UI Theme
 * Version: 1.0
 * Odoo 19 CE Compatible
 */

/* ============================================
   STATUS BAR COLORS
   ============================================ */

/* Draft State - Gray */
.o_statusbar_status .o_arrow_button[data-value="draft"],
.o_statusbar_status .o_arrow_button[data-value="new"] {
    --StatusBar-arrow-bg: #6c757d !important;
}

/* Confirmed/Validated State - Blue */
.o_statusbar_status .o_arrow_button[data-value="confirmed"],
.o_statusbar_status .o_arrow_button[data-value="validated"],
.o_statusbar_status .o_arrow_button[data-value="open"] {
    --StatusBar-arrow-bg: #007bff !important;
}

/* Approved State - Teal */
.o_statusbar_status .o_arrow_button[data-value="approved"],
.o_statusbar_status .o_arrow_button[data-value="running"] {
    --StatusBar-arrow-bg: #17a2b8 !important;
}

/* Posted/Done State - Green */
.o_statusbar_status .o_arrow_button[data-value="posted"],
.o_statusbar_status .o_arrow_button[data-value="done"],
.o_statusbar_status .o_arrow_button[data-value="collected"],
.o_statusbar_status .o_arrow_button[data-value="completed"],
.o_statusbar_status .o_arrow_button[data-value="closed"] {
    --StatusBar-arrow-bg: #28a745 !important;
}

/* Cancelled/Rejected State - Red */
.o_statusbar_status .o_arrow_button[data-value="cancelled"],
.o_statusbar_status .o_arrow_button[data-value="rejected"],
.o_statusbar_status .o_arrow_button[data-value="bounced"] {
    --StatusBar-arrow-bg: #dc3545 !important;
}

/* Pending/Hold State - Yellow */
.o_statusbar_status .o_arrow_button[data-value="pending"],
.o_statusbar_status .o_arrow_button[data-value="hold"],
.o_statusbar_status .o_arrow_button[data-value="deposited"] {
    --StatusBar-arrow-bg: #ffc107 !important;
}

/* ============================================
   FORM ALERTS - OPS BRANDED
   ============================================ */

.o_form_view .alert.ops-alert-info {
    background-color: #e7f3ff;
    border-color: #b8daff;
    color: #004085;
}

.o_form_view .alert.ops-alert-warning {
    background-color: #fff3cd;
    border-color: #ffeaa7;
    color: #856404;
}

.o_form_view .alert.ops-alert-danger {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}

.o_form_view .alert.ops-alert-success {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}

/* ============================================
   BUTTON ENHANCEMENTS
   ============================================ */

/* Primary button subtle shadow */
.o_form_view .o_form_statusbar .btn-primary {
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.25);
}

/* Danger button confirmation highlight */
.o_form_view .o_form_statusbar .btn-danger {
    box-shadow: 0 2px 4px rgba(220, 53, 69, 0.25);
}

/* ============================================
   NOTEBOOK TAB ICONS
   ============================================ */

.o_notebook .nav-link .fa {
    margin-right: 6px;
    opacity: 0.8;
}

/* ============================================
   MONETARY FIELD COLORS
   ============================================ */

.o_field_monetary.text-danger,
.o_list_table .text-danger {
    color: #dc3545 !important;
}

.o_field_monetary.text-success,
.o_list_table .text-success {
    color: #28a745 !important;
}

/* ============================================
   KANBAN CARD STATES
   ============================================ */

.o_kanban_record.oe_kanban_color_0 { border-left: 3px solid #6c757d; }  /* Draft */
.o_kanban_record.oe_kanban_color_1 { border-left: 3px solid #007bff; }  /* Confirmed */
.o_kanban_record.oe_kanban_color_2 { border-left: 3px solid #28a745; }  /* Done */
.o_kanban_record.oe_kanban_color_3 { border-left: 3px solid #dc3545; }  /* Cancelled */
.o_kanban_record.oe_kanban_color_4 { border-left: 3px solid #ffc107; }  /* Warning */
```

### Update Manifest to Include CSS

**File: `ops_matrix_core/__manifest__.py`**

Add to assets section:
```python
'assets': {
    'web.assets_backend': [
        'ops_matrix_core/static/src/css/ops_theme.css',
    ],
},
```

---

## PHASE 2: Apply Button Styling Standards

### Standard Button Patterns by Action Type

```xml
<!-- PRIMARY: Main workflow action (only ONE per form) -->
<button name="action_confirm" type="object" string="Confirm"
        class="btn-primary" icon="fa-check"
        invisible="state != 'draft'"
        data-hotkey="v"/>

<!-- SECONDARY: Alternative/supporting actions -->
<button name="action_compute" type="object" string="Compute"
        class="btn-secondary" icon="fa-calculator"/>

<!-- SUCCESS: Positive completion actions -->
<button name="action_approve" type="object" string="Approve"
        class="btn-success" icon="fa-thumbs-up"
        groups="ops_matrix_core.group_ops_manager"/>

<button name="action_post" type="object" string="Post"
        class="btn-success" icon="fa-save"/>

<!-- WARNING: Actions requiring attention -->
<button name="action_hold" type="object" string="Put on Hold"
        class="btn-warning" icon="fa-pause"/>

<!-- DANGER: Destructive actions (always with confirm) -->
<button name="action_cancel" type="object" string="Cancel"
        class="btn-danger" icon="fa-times"
        confirm="Are you sure you want to cancel this record?"/>

<button name="action_reject" type="object" string="Reject"
        class="btn-danger" icon="fa-ban"
        confirm="Are you sure you want to reject?"/>

<!-- LINK: Utility/subtle actions -->
<button name="action_print" type="object" string="Print"
        class="btn-link" icon="fa-print"/>

<button name="action_reset_draft" type="object" string="Reset to Draft"
        class="btn-link" icon="fa-undo"
        groups="ops_matrix_core.group_ops_manager"/>
```

### Apply to Files:

#### ops_matrix_accounting/views/ops_asset_views.xml
```xml
<header>
    <button name="action_confirm" type="object" string="Confirm"
            class="btn-primary" icon="fa-check"
            invisible="state != 'draft'"/>
    <button name="action_start_depreciation" type="object" string="Start Depreciation"
            class="btn-success" icon="fa-play"
            invisible="state != 'confirmed'"/>
    <button name="action_compute_depreciation" type="object" string="Compute Depreciation"
            class="btn-secondary" icon="fa-calculator"
            invisible="state not in ('running', 'confirmed')"/>
    <button name="action_dispose" type="object" string="Dispose"
            class="btn-warning" icon="fa-archive"
            invisible="state not in ('running', 'confirmed')"
            confirm="Are you sure you want to dispose this asset?"/>
    <button name="action_cancel" type="object" string="Cancel"
            class="btn-danger" icon="fa-times"
            invisible="state in ('disposed', 'cancelled')"
            confirm="Are you sure you want to cancel this asset?"/>
    <button name="action_reset_draft" type="object" string="Reset to Draft"
            class="btn-link" icon="fa-undo"
            invisible="state != 'cancelled'"
            groups="ops_matrix_core.group_ops_manager"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,running,closed"/>
</header>
```

#### ops_matrix_accounting/views/ops_pdc_views.xml
```xml
<header>
    <button name="action_confirm" type="object" string="Confirm"
            class="btn-primary" icon="fa-check"
            invisible="state != 'draft'"/>
    <button name="action_deposit" type="object" string="Deposit"
            class="btn-secondary" icon="fa-university"
            invisible="state != 'confirmed'"/>
    <button name="action_collect" type="object" string="Mark Collected"
            class="btn-success" icon="fa-check-circle"
            invisible="state != 'deposited'"/>
    <button name="action_bounce" type="object" string="Mark Bounced"
            class="btn-danger" icon="fa-exclamation-circle"
            invisible="state not in ('deposited', 'confirmed')"
            confirm="Mark this check as bounced?"/>
    <button name="action_cancel" type="object" string="Cancel"
            class="btn-danger" icon="fa-times"
            invisible="state in ('collected', 'cancelled')"
            confirm="Cancel this PDC?"/>
    <button name="action_reset_draft" type="object" string="Reset to Draft"
            class="btn-link" icon="fa-undo"
            invisible="state != 'cancelled'"
            groups="ops_matrix_core.group_ops_manager"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,deposited,collected"/>
</header>
```

#### ops_matrix_accounting/views/ops_budget_views.xml
```xml
<header>
    <button name="action_confirm" type="object" string="Confirm"
            class="btn-primary" icon="fa-check"
            invisible="state != 'draft'"/>
    <button name="action_approve" type="object" string="Approve"
            class="btn-success" icon="fa-thumbs-up"
            invisible="state != 'confirmed'"
            groups="ops_matrix_core.group_ops_manager"/>
    <button name="action_revise" type="object" string="Revise"
            class="btn-secondary" icon="fa-edit"
            invisible="state != 'approved'"/>
    <button name="action_close" type="object" string="Close"
            class="btn-warning" icon="fa-lock"
            invisible="state != 'approved'"
            confirm="Close this budget period?"/>
    <button name="action_cancel" type="object" string="Cancel"
            class="btn-danger" icon="fa-times"
            invisible="state in ('closed', 'cancelled')"
            confirm="Cancel this budget?"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,approved,closed"/>
</header>
```

#### ops_matrix_core/views/ops_inter_branch_transfer_views.xml
```xml
<header>
    <button name="action_confirm" type="object" string="Confirm"
            class="btn-primary" icon="fa-check"
            invisible="state != 'draft'"/>
    <button name="action_approve" type="object" string="Approve"
            class="btn-success" icon="fa-thumbs-up"
            invisible="state != 'confirmed'"
            groups="ops_matrix_core.group_ops_manager"/>
    <button name="action_transfer" type="object" string="Execute Transfer"
            class="btn-success" icon="fa-exchange"
            invisible="state != 'approved'"/>
    <button name="action_receive" type="object" string="Mark Received"
            class="btn-success" icon="fa-check-circle"
            invisible="state != 'transferred'"/>
    <button name="action_cancel" type="object" string="Cancel"
            class="btn-danger" icon="fa-times"
            invisible="state in ('done', 'cancelled')"
            confirm="Cancel this transfer?"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,confirmed,approved,transferred,done"/>
</header>
```

#### ops_matrix_core/views/ops_product_request_views.xml
```xml
<header>
    <button name="action_submit" type="object" string="Submit"
            class="btn-primary" icon="fa-paper-plane"
            invisible="state != 'draft'"/>
    <button name="action_approve" type="object" string="Approve"
            class="btn-success" icon="fa-thumbs-up"
            invisible="state != 'submitted'"
            groups="ops_matrix_core.group_ops_manager"/>
    <button name="action_reject" type="object" string="Reject"
            class="btn-danger" icon="fa-thumbs-down"
            invisible="state != 'submitted'"
            groups="ops_matrix_core.group_ops_manager"
            confirm="Reject this request?"/>
    <button name="action_fulfill" type="object" string="Mark Fulfilled"
            class="btn-success" icon="fa-check-circle"
            invisible="state != 'approved'"/>
    <button name="action_cancel" type="object" string="Cancel"
            class="btn-danger" icon="fa-times"
            invisible="state in ('fulfilled', 'cancelled', 'rejected')"
            confirm="Cancel this request?"/>
    <field name="state" widget="statusbar"
           statusbar_visible="draft,submitted,approved,fulfilled"/>
</header>
```

---

## PHASE 3: Add Alert Banners to Forms

### Pattern for Contextual Alerts

```xml
<sheet>
    <!-- Warning Alert - Cancelled/Bounced -->
    <div class="alert alert-danger mb-3" role="alert"
         invisible="state != 'cancelled'">
        <i class="fa fa-ban me-2"/>
        <strong>Cancelled:</strong> This record has been cancelled.
    </div>
    
    <!-- Warning Alert - Bounced Check -->
    <div class="alert alert-danger mb-3" role="alert"
         invisible="state != 'bounced'">
        <i class="fa fa-exclamation-triangle me-2"/>
        <strong>Bounced:</strong> This check has been returned unpaid.
    </div>
    
    <!-- Info Alert - Pending Approval -->
    <div class="alert alert-info mb-3" role="alert"
         invisible="state != 'confirmed'">
        <i class="fa fa-clock-o me-2"/>
        <strong>Pending Approval:</strong> This record is awaiting manager approval.
    </div>
    
    <!-- Success Alert - Completed -->
    <div class="alert alert-success mb-3" role="alert"
         invisible="state not in ('done', 'posted', 'collected')">
        <i class="fa fa-check-circle me-2"/>
        <strong>Completed:</strong> This record has been fully processed.
    </div>
    
    <!-- Warning Alert - Near Due Date (for PDC) -->
    <div class="alert alert-warning mb-3" role="alert"
         invisible="days_to_maturity > 7 or days_to_maturity &lt; 0 or state != 'confirmed'">
        <i class="fa fa-calendar me-2"/>
        <strong>Maturing Soon:</strong> This check matures in 
        <field name="days_to_maturity" nolabel="1" class="fw-bold"/> days.
    </div>
    
    <!-- Rest of sheet content -->
    <div class="oe_title">
        ...
    </div>
</sheet>
```

### Apply Alerts to Specific Forms:

**ops_asset_views.xml** - Add after `<sheet>`:
```xml
<div class="alert alert-warning mb-3" role="alert"
     invisible="state != 'disposed'">
    <i class="fa fa-archive me-2"/>
    <strong>Disposed:</strong> This asset has been disposed on 
    <field name="disposal_date" nolabel="1"/>.
</div>
<div class="alert alert-info mb-3" role="alert"
     invisible="not (fully_depreciated and state == 'running')">
    <i class="fa fa-info-circle me-2"/>
    <strong>Fully Depreciated:</strong> This asset has been fully depreciated.
</div>
```

**ops_pdc_views.xml** - Add after `<sheet>`:
```xml
<div class="alert alert-danger mb-3" role="alert"
     invisible="state != 'bounced'">
    <i class="fa fa-exclamation-triangle me-2"/>
    <strong>Bounced:</strong> This check has been returned by the bank.
</div>
<div class="alert alert-warning mb-3" role="alert"
     invisible="days_to_maturity > 7 or days_to_maturity &lt; 0 or state not in ('draft', 'confirmed')">
    <i class="fa fa-calendar me-2"/>
    <strong>Maturing Soon:</strong> Check matures in 
    <field name="days_to_maturity" nolabel="1" class="fw-bold"/> days.
</div>
```

**ops_budget_views.xml** - Add after `<sheet>`:
```xml
<div class="alert alert-danger mb-3" role="alert"
     invisible="not is_over_budget">
    <i class="fa fa-exclamation-circle me-2"/>
    <strong>Over Budget:</strong> Actual spending has exceeded the budgeted amount.
</div>
<div class="alert alert-success mb-3" role="alert"
     invisible="budget_utilization &lt; 0.9 or is_over_budget">
    <i class="fa fa-check me-2"/>
    <strong>On Track:</strong> Budget utilization is within acceptable limits.
</div>
```

---

## PHASE 4: Apply Tree View Decorations

### Standard Decoration Pattern

```xml
<tree decoration-danger="state in ('cancelled', 'bounced', 'rejected')"
      decoration-warning="state in ('pending', 'hold', 'overdue')"
      decoration-success="state in ('done', 'posted', 'collected', 'approved')"
      decoration-muted="active == False"
      decoration-info="is_priority == True or is_urgent == True">
```

### Apply to Tree Views:

**ops_asset_views.xml** - Tree view:
```xml
<tree decoration-danger="state == 'cancelled'"
      decoration-warning="state == 'disposed'"
      decoration-success="state == 'closed'"
      decoration-muted="active == False"
      decoration-info="fully_depreciated == True">
    <field name="name"/>
    <field name="code"/>
    <field name="category_id"/>
    <field name="acquisition_date"/>
    <field name="acquisition_value" sum="Total Value"/>
    <field name="book_value" sum="Total Book Value"/>
    <field name="state" widget="badge"
           decoration-success="state in ('running', 'closed')"
           decoration-warning="state == 'disposed'"
           decoration-danger="state == 'cancelled'"
           decoration-info="state in ('draft', 'confirmed')"/>
    <field name="active" column_invisible="1"/>
    <field name="fully_depreciated" column_invisible="1"/>
</tree>
```

**ops_pdc_views.xml** - Tree view:
```xml
<tree decoration-danger="state in ('cancelled', 'bounced')"
      decoration-warning="days_to_maturity &lt;= 7 and days_to_maturity >= 0 and state == 'confirmed'"
      decoration-success="state == 'collected'"
      decoration-muted="active == False">
    <field name="name"/>
    <field name="partner_id"/>
    <field name="check_number"/>
    <field name="check_date"/>
    <field name="amount" sum="Total Amount"/>
    <field name="days_to_maturity" string="Days to Maturity"
           decoration-danger="days_to_maturity &lt; 0"
           decoration-warning="days_to_maturity &lt;= 7 and days_to_maturity >= 0"/>
    <field name="state" widget="badge"
           decoration-success="state == 'collected'"
           decoration-warning="state == 'deposited'"
           decoration-danger="state in ('cancelled', 'bounced')"
           decoration-info="state in ('draft', 'confirmed')"/>
    <field name="active" column_invisible="1"/>
</tree>
```

**ops_budget_views.xml** - Tree view:
```xml
<tree decoration-danger="is_over_budget == True"
      decoration-warning="budget_utilization >= 0.9 and not is_over_budget"
      decoration-success="state == 'closed'"
      decoration-muted="active == False">
    <field name="name"/>
    <field name="fiscal_year_id"/>
    <field name="department_id"/>
    <field name="planned_amount" sum="Total Planned"/>
    <field name="actual_amount" sum="Total Actual"/>
    <field name="variance" sum="Total Variance"
           decoration-danger="variance &lt; 0"
           decoration-success="variance >= 0"/>
    <field name="budget_utilization" widget="progressbar"/>
    <field name="state" widget="badge"
           decoration-success="state in ('approved', 'closed')"
           decoration-warning="state == 'confirmed'"
           decoration-danger="state == 'cancelled'"
           decoration-info="state == 'draft'"/>
    <field name="is_over_budget" column_invisible="1"/>
    <field name="active" column_invisible="1"/>
</tree>
```

**ops_inter_branch_transfer_views.xml** - Tree view:
```xml
<tree decoration-danger="state == 'cancelled'"
      decoration-warning="state in ('confirmed', 'approved')"
      decoration-success="state == 'done'"
      decoration-muted="active == False">
    <field name="name"/>
    <field name="date"/>
    <field name="source_branch_id"/>
    <field name="dest_branch_id"/>
    <field name="transfer_type"/>
    <field name="total_amount" sum="Total Amount"/>
    <field name="state" widget="badge"
           decoration-success="state == 'done'"
           decoration-warning="state in ('transferred', 'approved')"
           decoration-info="state in ('draft', 'confirmed')"
           decoration-danger="state == 'cancelled'"/>
    <field name="active" column_invisible="1"/>
</tree>
```

---

## PHASE 5: Add Notebook Tab Icons

### Pattern for Notebook Pages

```xml
<notebook>
    <page string="General" name="general" icon="fa-info-circle">
        <!-- General information fields -->
    </page>
    <page string="Lines" name="lines" icon="fa-list">
        <!-- Line items -->
    </page>
    <page string="Accounting" name="accounting" icon="fa-book">
        <!-- Accounting details -->
    </page>
    <page string="Depreciation" name="depreciation" icon="fa-line-chart">
        <!-- Depreciation schedule -->
    </page>
    <page string="Notes" name="notes" icon="fa-sticky-note">
        <!-- Notes field -->
    </page>
    <page string="History" name="history" icon="fa-history"
          groups="ops_matrix_core.group_ops_manager">
        <!-- Audit history -->
    </page>
    <page string="Documents" name="documents" icon="fa-paperclip">
        <!-- Attachments -->
    </page>
    <page string="Settings" name="settings" icon="fa-cog"
          groups="base.group_no_one">
        <!-- Technical settings -->
    </page>
</notebook>
```

### Apply to Asset Form (ops_asset_views.xml):
```xml
<notebook>
    <page string="General Information" name="general" icon="fa-info-circle">
        <group>
            <group string="Asset Details">
                <field name="category_id"/>
                <field name="method"/>
                <field name="method_number"/>
                <field name="method_period"/>
            </group>
            <group string="Values">
                <field name="acquisition_value"/>
                <field name="salvage_value"/>
                <field name="book_value"/>
                <field name="depreciated_value"/>
            </group>
        </group>
    </page>
    <page string="Depreciation Schedule" name="depreciation" icon="fa-line-chart">
        <field name="depreciation_line_ids">
            <tree editable="bottom" decoration-muted="move_posted == True">
                <field name="depreciation_date"/>
                <field name="amount"/>
                <field name="depreciated_value"/>
                <field name="remaining_value"/>
                <field name="move_id"/>
                <field name="move_posted" column_invisible="1"/>
            </tree>
        </field>
    </page>
    <page string="Accounting" name="accounting" icon="fa-book">
        <group>
            <group>
                <field name="account_asset_id"/>
                <field name="account_depreciation_id"/>
                <field name="account_depreciation_expense_id"/>
            </group>
            <group>
                <field name="journal_id"/>
                <field name="analytic_account_id"/>
            </group>
        </group>
    </page>
    <page string="Notes" name="notes" icon="fa-sticky-note">
        <field name="notes" placeholder="Additional notes about this asset..."/>
    </page>
</notebook>
```

---

## PHASE 6: Smart Button Styling (Stat Buttons)

### Pattern for Stat Buttons with Icons

```xml
<div class="oe_button_box" name="button_box">
    <button name="action_view_depreciation_lines" type="object"
            class="oe_stat_button" icon="fa-line-chart"
            invisible="depreciation_line_count == 0">
        <field name="depreciation_line_count" widget="statinfo" string="Depreciation Lines"/>
    </button>
    <button name="action_view_journal_entries" type="object"
            class="oe_stat_button" icon="fa-book"
            invisible="move_count == 0">
        <field name="move_count" widget="statinfo" string="Journal Entries"/>
    </button>
    <button name="action_view_documents" type="object"
            class="oe_stat_button" icon="fa-paperclip"
            invisible="document_count == 0">
        <field name="document_count" widget="statinfo" string="Documents"/>
    </button>
    <button name="toggle_active" type="object" class="oe_stat_button" icon="fa-archive">
        <field name="active" widget="boolean_button"
               options='{"terminology": "archive"}'/>
    </button>
</div>
```

---

## PHASE 7: Icon Reference Table

Use these icons consistently across all modules:

| Action/Concept | Icon | Usage |
|----------------|------|-------|
| Confirm/Validate | `fa-check` | Primary workflow action |
| Approve | `fa-thumbs-up` | Manager approval |
| Reject | `fa-thumbs-down` | Rejection action |
| Cancel | `fa-times` | Cancel action |
| Reset/Undo | `fa-undo` | Reset to draft |
| Submit/Send | `fa-paper-plane` | Submit for approval |
| Post | `fa-save` | Post to accounting |
| Compute/Calculate | `fa-calculator` | Computation actions |
| Print | `fa-print` | Print reports |
| Export | `fa-download` | Export data |
| Excel | `fa-file-excel-o` | Excel export |
| PDF | `fa-file-pdf-o` | PDF export |
| Email | `fa-envelope` | Send email |
| View/Preview | `fa-eye` | Preview action |
| Edit | `fa-edit` | Edit mode |
| Delete | `fa-trash` | Delete action |
| Archive | `fa-archive` | Archive record |
| Lock | `fa-lock` | Lock/finalize |
| Unlock | `fa-unlock` | Unlock/reopen |
| Settings | `fa-cog` | Configuration |
| History | `fa-history` | Audit trail |
| Calendar | `fa-calendar` | Date related |
| Money | `fa-money` | Payment |
| Bank | `fa-university` | Banking |
| Transfer | `fa-exchange` | Transfer action |
| Warning | `fa-exclamation-triangle` | Warning state |
| Info | `fa-info-circle` | Information |
| Success | `fa-check-circle` | Completed |
| Error | `fa-times-circle` | Failed/Error |
| Play/Start | `fa-play` | Start process |
| Pause/Hold | `fa-pause` | Hold action |
| Stop | `fa-stop` | Stop process |

---

## Validation Checklist

After applying all changes:

- [ ] CSS file created and registered in manifest
- [ ] All header buttons have appropriate class and icon
- [ ] Only ONE `btn-primary` button per form header
- [ ] All `btn-danger` buttons have `confirm` attribute
- [ ] Status bars use `statusbar_visible` attribute
- [ ] Tree views have appropriate `decoration-*` attributes
- [ ] State fields use `widget="badge"` with decorations
- [ ] Notebook pages have icons
- [ ] Alert banners show contextually based on state
- [ ] Stat buttons have appropriate icons
- [ ] All modules upgraded successfully
- [ ] UI renders correctly in browser

---

## Test Commands

```bash
# Upgrade all OPS modules
cd /opt/gemini_odoo19
./odoo-bin -c odoo.conf -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init

# Check for XML errors
grep -r "class=\"btn-" addons/ops_matrix_*/views/*.xml | grep -v "btn-primary\|btn-secondary\|btn-success\|btn-warning\|btn-danger\|btn-link"

# Verify all forms have consistent styling
grep -l "<header>" addons/ops_matrix_*/views/*.xml | xargs grep -L "icon="
```

---

## Output Required

For each file modified, provide:
1. File path
2. Summary of changes made
3. Any issues encountered

Report completion status for each phase.
```

---

## 📋 Summary

This comprehensive prompt will:

| Phase | Action | Files Affected |
|-------|--------|----------------|
| 1 | Create shared CSS theme | 1 new file |
| 2 | Apply button styling | ~10 view files |
| 3 | Add alert banners | ~7 form views |
| 4 | Apply tree decorations | ~7 tree views |
| 5 | Add notebook tab icons | ~5 forms |
| 6 | Style stat buttons | ~5 forms |
| 7 | Reference documentation | Style guide |

