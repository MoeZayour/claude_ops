# Priority #7: Three-Way Match Enforcement - Technical Specifications

**Priority**: #7 - HIGH  
**Estimated Effort**: 2 sessions (4-6 hours)  
**Status**: READY FOR DEVELOPMENT  
**Phase-Based Implementation**: Yes (2 phases)

---

## Overview

Implement three-way matching between Purchase Order, Receipt, and Vendor Bill to ensure:
- Only received goods are paid for
- Quantities on invoices match what was actually received
- Discrepancies are flagged and require approval
- Complete audit trail for all matches and overrides

---

## Business Context

### Problem Statement

Without three-way matching:
- ❌ Vendors can invoice for goods not yet delivered
- ❌ Companies pay for quantities never received
- ❌ No systematic check between PO → Receipt → Invoice
- ❌ Manual verification prone to errors
- ❌ Disputes with vendors common

### Solution

**Three-Way Match**:
1. **PO ↔ Receipt**: Validate received quantity ≤ ordered quantity
2. **Receipt ↔ Bill**: Validate billed quantity ≤ received quantity
3. **Tolerance**: Allow small variances (configurable %)
4. **Override**: Authorized users can override with reason

### User Stories

**As a** Purchase Manager  
**I want** the system to block invoices that don't match receipts  
**So that** we only pay for what we actually received

**As an** AP Clerk  
**I want** to see matching status before processing payments  
**So that** I can verify invoices are legitimate

**As a** CFO  
**I want** an audit trail of all overrides  
**So that** I can review exceptions and identify issues

---

## Core Concepts

### Three-Way Match Flow

```
┌─────────────────┐
│ Purchase Order  │
│ Qty: 100 units  │
└────────┬────────┘
         │ Creates
         ↓
┌─────────────────┐
│ Receipt         │  ← Match #1: Received ≤ Ordered?
│ Qty: 95 units   │
└────────┬────────┘
         │ Creates
         ↓
┌─────────────────┐
│ Vendor Bill     │  ← Match #2: Billed ≤ Received?
│ Qty: 95 units   │
└─────────────────┘
         │
         ↓
    ✅ MATCHED - Can Pay
```

### Match States

1. **MATCHED** ✅
   - Billed qty = Received qty (within tolerance)
   - Can proceed with payment
   - No approval needed

2. **UNDER_BILLED** ⚠️
   - Billed qty < Received qty
   - Warning only (vendor may send correction)
   - Can proceed with payment

3. **OVER_BILLED** ❌
   - Billed qty > Received qty
   - **BLOCK** invoice validation
   - Requires override approval

4. **NO_RECEIPT** ❌
   - No receipt found for PO line
   - **BLOCK** invoice validation  
   - Requires override approval

5. **PARTIAL_RECEIPT** ⚠️
   - Received qty < Ordered qty
   - Warning only (normal for partial deliveries)
   - Track remaining qty to receive

---

## PHASE 1: Core Matching Engine (Session 1)

### Objectives

1. Create matching engine model
2. Track quantities (ordered, received, billed)
3. Implement match validation logic
4. Add tolerance configuration
5. Block invoice validation on mismatch
6. Basic UI indicators

### Files to Create

#### 1. `models/ops_three_way_match.py`

**Purpose**: Core matching engine

**Model**: `ops.three.way.match`

**Key Fields**:
```python
class OpsThreeWayMatch(models.Model):
    _name = 'ops.three.way.match'
    _description = 'Three-Way Match Record'
    
    # References
    purchase_order_id = fields.Many2one('purchase.order', required=True)
    purchase_line_id = fields.Many2one('purchase.order.line', required=True)
    
    # Quantities
    ordered_qty = fields.Float('Ordered Quantity', required=True)
    received_qty = fields.Float('Received Quantity', compute='_compute_received_qty', store=True)
    billed_qty = fields.Float('Billed Quantity', compute='_compute_billed_qty', store=True)
    
    # Match Status
    match_state = fields.Selection([
        ('matched', 'Matched'),
        ('under_billed', 'Under Billed'),
        ('over_billed', 'Over Billed'),
        ('no_receipt', 'No Receipt'),
        ('partial_receipt', 'Partial Receipt'),
    ], compute='_compute_match_state', store=True)
    
    # Variance
    qty_variance = fields.Float('Quantity Variance', compute='_compute_variance')
    qty_variance_percent = fields.Float('Variance %', compute='_compute_variance')
    
    # Status
    is_blocked = fields.Boolean('Blocked', compute='_compute_match_state', store=True)
    blocking_reason = fields.Text('Blocking Reason')
```

**Key Methods**:

```python
@api.depends('purchase_line_id')
def _compute_received_qty(self):
    """Calculate total received quantity from stock moves."""
    for record in self:
        moves = self.env['stock.move'].search([
            ('purchase_line_id', '=', record.purchase_line_id.id),
            ('state', '=', 'done')
        ])
        record.received_qty = sum(moves.mapped('product_uom_qty'))

@api.depends('purchase_line_id')
def _compute_billed_qty(self):
    """Calculate total billed quantity from invoice lines."""
    for record in self:
        invoice_lines = self.env['account.move.line'].search([
            ('purchase_line_id', '=', record.purchase_line_id.id),
            ('move_id.move_type', '=', 'in_invoice'),
            ('move_id.state', '!=', 'cancel')
        ])
        record.billed_qty = sum(invoice_lines.mapped('quantity'))

@api.depends('ordered_qty', 'received_qty', 'billed_qty')
def _compute_match_state(self):
    """Determine match state and blocking status."""
    for record in self:
        tolerance_pct = record.purchase_order_id.company_id.three_way_match_tolerance or 0.0
        tolerance = record.received_qty * (tolerance_pct / 100.0)
        
        if record.received_qty == 0:
            record.match_state = 'no_receipt'
            record.is_blocked = True
            record.blocking_reason = 'No goods have been received for this purchase order line.'
        
        elif record.billed_qty > (record.received_qty + tolerance):
            record.match_state = 'over_billed'
            record.is_blocked = True
            record.blocking_reason = f'Billed quantity ({record.billed_qty}) exceeds received quantity ({record.received_qty}) by more than tolerance ({tolerance_pct}%).'
        
        elif record.billed_qty < (record.received_qty - tolerance):
            record.match_state = 'under_billed'
            record.is_blocked = False
            record.blocking_reason = False
        
        elif record.received_qty < record.ordered_qty:
            record.match_state = 'partial_receipt'
            record.is_blocked = False
            record.blocking_reason = False
        
        else:
            record.match_state = 'matched'
            record.is_blocked = False
            record.blocking_reason = False

@api.depends('received_qty', 'billed_qty')
def _compute_variance(self):
    """Calculate quantity variance."""
    for record in self:
        record.qty_variance = record.billed_qty - record.received_qty
        if record.received_qty > 0:
            record.qty_variance_percent = (record.qty_variance / record.received_qty) * 100
        else:
            record.qty_variance_percent = 0.0
```

#### 2. `models/res_company.py` (Extend)

**Add Configuration Fields**:
```python
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Three-Way Match Settings
    enable_three_way_match = fields.Boolean(
        'Enable Three-Way Match',
        default=True,
        help='Enforce matching between PO, Receipt, and Invoice'
    )
    
    three_way_match_tolerance = fields.Float(
        'Match Tolerance (%)',
        default=5.0,
        help='Allow variance up to this percentage (e.g., 5% means billed qty can be 5% more than received qty)'
    )
    
    three_way_match_block_validation = fields.Boolean(
        'Block Invoice Validation',
        default=True,
        help='Prevent validating invoices with mismatched quantities'
    )
```

#### 3. `models/account_move.py` (Extend)

**Add Validation Hook**:
```python
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    three_way_match_status = fields.Selection([
        ('not_applicable', 'N/A'),
        ('matched', 'Matched'),
        ('blocked', 'Blocked - Mismatch'),
        ('override_approved', 'Override Approved'),
    ], compute='_compute_three_way_match_status', store=True, string='Match Status')
    
    three_way_match_issues = fields.Text('Match Issues', compute='_compute_three_way_match_status')
    
    @api.depends('invoice_line_ids', 'invoice_line_ids.purchase_line_id')
    def _compute_three_way_match_status(self):
        """Check three-way match status for vendor bills."""
        for move in self:
            if move.move_type != 'in_invoice' or not move.company_id.enable_three_way_match:
                move.three_way_match_status = 'not_applicable'
                move.three_way_match_issues = False
                continue
            
            issues = []
            has_blocked = False
            
            for line in move.invoice_line_ids.filtered('purchase_line_id'):
                match = self.env['ops.three.way.match'].search([
                    ('purchase_line_id', '=', line.purchase_line_id.id)
                ], limit=1)
                
                if not match:
                    # Create match record
                    match = self.env['ops.three.way.match'].create({
                        'purchase_order_id': line.purchase_line_id.order_id.id,
                        'purchase_line_id': line.purchase_line_id.id,
                        'ordered_qty': line.purchase_line_id.product_qty,
                    })
                
                if match.is_blocked:
                    has_blocked = True
                    issues.append(f"Line {line.name}: {match.blocking_reason}")
            
            if has_blocked:
                move.three_way_match_status = 'blocked'
                move.three_way_match_issues = '\n'.join(issues)
            elif issues:
                move.three_way_match_status = 'matched'
                move.three_way_match_issues = False
            else:
                move.three_way_match_status = 'not_applicable'
                move.three_way_match_issues = False
    
    def action_post(self):
        """Block posting if three-way match fails."""
        for move in self:
            if move.three_way_match_status == 'blocked' and move.company_id.three_way_match_block_validation:
                raise UserError(
                    _("Cannot validate this invoice due to three-way match issues:\n\n%s\n\n"
                      "Please verify quantities with your Purchase Manager or request an override approval.") 
                    % move.three_way_match_issues
                )
        return super().action_post()
```

### Views to Create

#### 1. Company Settings View

**File**: `views/res_company_views.xml`

```xml
<record id="view_company_form_three_way_match" model="ir.ui.view">
    <field name="name">res.company.form.three.way.match</field>
    <field name="model">res.company</field>
    <field name="inherit_id" ref="base.view_company_form"/>
    <field name="arch" type="xml">
        <xpath expr="//page[@name='account']" position="after">
            <page name="three_way_match" string="Three-Way Match">
                <group>
                    <group string="Settings">
                        <field name="enable_three_way_match"/>
                        <field name="three_way_match_tolerance" 
                               attrs="{'invisible': [('enable_three_way_match', '=', False)]}"/>
                        <field name="three_way_match_block_validation"
                               attrs="{'invisible': [('enable_three_way_match', '=', False)]}"/>
                    </group>
                    <group string="Information">
                        <div class="alert alert-info" role="alert">
                            <strong>Three-Way Match</strong>
                            <p>Ensures invoices match received quantities:</p>
                            <ul>
                                <li>Validates Purchase Order ↔ Receipt ↔ Invoice</li>
                                <li>Blocks overpayment for undelivered goods</li>
                                <li>Tolerance allows small variances</li>
                                <li>Overrides require approval and justification</li>
                            </ul>
                        </div>
                    </group>
                </group>
            </page>
        </xpath>
    </field>
</record>
```

#### 2. Invoice Form View Enhancement

**File**: `views/account_move_views.xml`

```xml
<record id="view_invoice_form_three_way_match" model="ir.ui.view">
    <field name="name">account.move.form.three.way.match</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account.view_move_form"/>
    <field name="arch" type="xml">
        <!-- Add warning banner -->
        <xpath expr="//sheet" position="before">
            <div class="alert alert-danger" role="alert" 
                 attrs="{'invisible': [('three_way_match_status', '!=', 'blocked')]}">
                <strong>⚠️ Three-Way Match Blocked</strong>
                <p><field name="three_way_match_issues" readonly="1"/></p>
                <p>This invoice cannot be validated until quantities are corrected or an override is approved.</p>
            </div>
            <div class="alert alert-warning" role="alert"
                 attrs="{'invisible': [('three_way_match_status', '!=', 'under_billed')]}">
                <strong>ℹ️ Under-Billed</strong>
                <p>Invoice quantity is less than received quantity. Vendor may send a correction invoice.</p>
            </div>
        </xpath>
        
        <!-- Add match status field -->
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="three_way_match_status" 
                   widget="badge"
                   decoration-success="three_way_match_status == 'matched'"
                   decoration-danger="three_way_match_status == 'blocked'"
                   decoration-warning="three_way_match_status == 'override_approved'"
                   attrs="{'invisible': [('move_type', '!=', 'in_invoice')]}"/>
        </xpath>
    </field>
</record>
```

#### 3. Three-Way Match Report View

**File**: `views/ops_three_way_match_views.xml`

```xml
<record id="view_three_way_match_tree" model="ir.ui.view">
    <field name="name">ops.three.way.match.tree</field>
    <field name="model">ops.three.way.match</field>
    <field name="arch" type="xml">
        <tree decoration-danger="is_blocked" decoration-warning="match_state == 'under_billed'">
            <field name="purchase_order_id"/>
            <field name="purchase_line_id" string="PO Line"/>
            <field name="ordered_qty" sum="Total Ordered"/>
            <field name="received_qty" sum="Total Received"/>
            <field name="billed_qty" sum="Total Billed"/>
            <field name="qty_variance" sum="Total Variance"/>
            <field name="qty_variance_percent" widget="percentage"/>
            <field name="match_state" widget="badge"
                   decoration-success="match_state == 'matched'"
                   decoration-danger="match_state == 'over_billed'"
                   decoration-warning="match_state in ('under_billed', 'partial_receipt')"
                   decoration-muted="match_state == 'no_receipt'"/>
            <field name="is_blocked" invisible="1"/>
        </tree>
    </field>
</record>

<record id="view_three_way_match_form" model="ir.ui.view">
    <field name="name">ops.three.way.match.form</field>
    <field name="model">ops.three.way.match</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <field name="match_state" widget="statusbar"/>
            </header>
            <sheet>
                <div class="alert alert-danger" role="alert" attrs="{'invisible': [('is_blocked', '=', False)]}">
                    <strong>⚠️ Blocked</strong>
                    <p><field name="blocking_reason" readonly="1"/></p>
                </div>
                
                <group>
                    <group string="Purchase Order">
                        <field name="purchase_order_id"/>
                        <field name="purchase_line_id"/>
                        <field name="ordered_qty"/>
                    </group>
                    <group string="Quantities">
                        <field name="received_qty"/>
                        <field name="billed_qty"/>
                        <field name="qty_variance" 
                               decoration-danger="qty_variance > 0"
                               decoration-success="qty_variance == 0"/>
                        <field name="qty_variance_percent" widget="percentage"/>
                    </group>
                </group>
            </sheet>
        </form>
    </field>
</record>

<record id="action_three_way_match" model="ir.actions.act_window">
    <field name="name">Three-Way Match Report</field>
    <field name="res_model">ops.three.way.match</field>
    <field name="view_mode">tree,form</field>
    <field name="context">{'search_default_blocked': 1}</field>
</record>

<!-- Search view with filters -->
<record id="view_three_way_match_search" model="ir.ui.view">
    <field name="name">ops.three.way.match.search</field>
    <field name="model">ops.three.way.match</field>
    <field name="arch" type="xml">
        <search>
            <field name="purchase_order_id"/>
            <field name="purchase_line_id"/>
            <filter name="blocked" string="Blocked" domain="[('is_blocked', '=', True)]"/>
            <filter name="over_billed" string="Over Billed" domain="[('match_state', '=', 'over_billed')]"/>
            <filter name="no_receipt" string="No Receipt" domain="[('match_state', '=', 'no_receipt')]"/>
            <filter name="matched" string="Matched" domain="[('match_state', '=', 'matched')]"/>
            <group expand="0" string="Group By">
                <filter name="group_po" string="Purchase Order" context="{'group_by': 'purchase_order_id'}"/>
                <filter name="group_state" string="Match State" context="{'group_by': 'match_state'}"/>
            </group>
        </search>
    </field>
</record>
```

### Testing Checklist (Phase 1)

**Match Calculations**:
- [ ] Ordered 100, Received 100, Billed 100 → MATCHED ✅
- [ ] Ordered 100, Received 95, Billed 95 → MATCHED ✅
- [ ] Ordered 100, Received 95, Billed 100 → OVER_BILLED ❌
- [ ] Ordered 100, Received 0, Billed 50 → NO_RECEIPT ❌
- [ ] Ordered 100, Received 95, Billed 90 → UNDER_BILLED ⚠️

**Tolerance**:
- [ ] Tolerance 5%, Received 100, Billed 105 → MATCHED (within tolerance)
- [ ] Tolerance 5%, Received 100, Billed 106 → OVER_BILLED (exceeds tolerance)
- [ ] Tolerance 0%, Received 100, Billed 101 → OVER_BILLED (no tolerance)

**Blocking**:
- [ ] Invoice with OVER_BILLED status → Cannot validate
- [ ] Invoice with NO_RECEIPT status → Cannot validate
- [ ] Invoice with MATCHED status → Can validate
- [ ] Invoice with UNDER_BILLED status → Can validate (warning only)

**UI**:
- [ ] Company settings visible and working
- [ ] Invoice shows match status badge
- [ ] Blocked invoice shows danger banner
- [ ] Three-way match report accessible
- [ ] Filters work correctly

---

## PHASE 2: Override Approval (Session 2)

### Objectives

1. Create override approval wizard
2. Integrate with existing approval system
3. Track override history
4. Update governance rules
5. Dashboard widgets
6. Complete testing

### Files to Create

#### 1. `wizard/three_way_match_override_wizard.py`

**Purpose**: Request override approval for blocked invoices

```python
class ThreeWayMatchOverrideWizard(models.TransientModel):
    _name = 'three.way.match.override.wizard'
    _description = 'Three-Way Match Override Request'
    
    invoice_id = fields.Many2one('account.move', required=True)
    override_reason = fields.Text('Override Reason', required=True)
    match_issues = fields.Text('Match Issues', readonly=True)
    approver_id = fields.Many2one('res.users', 'Approver', required=True,
                                   domain="[('groups_id', 'in', %(group_ops_manager)d)]")
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        invoice_id = self.env.context.get('active_id')
        if invoice_id:
            invoice = self.env['account.move'].browse(invoice_id)
            res['invoice_id'] = invoice_id
            res['match_issues'] = invoice.three_way_match_issues
        return res
    
    def action_request_override(self):
        """Create approval request for override."""
        if len(self.override_reason) < 20:
            raise UserError('Override reason must be at least 20 characters.')
        
        # Create approval request
        approval = self.env['ops.approval.request'].create({
            'document_model': 'account.move',
            'document_id': self.invoice_id.id,
            'document_ref': self.invoice_id.name,
            'reason': f'Three-Way Match Override:\n{self.override_reason}\n\nMatch Issues:\n{self.match_issues}',
            'approver_id': self.approver_id.id,
            'request_type': 'three_way_match_override',
        })
        
        # Post to chatter
        self.invoice_id.message_post(
            body=_('<p><strong>Three-Way Match Override Requested</strong></p>'
                   '<p>Reason: %s</p>'
                   '<p>Approver: %s</p>') % (self.override_reason, self.approver_id.name),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Override approval requested from %s' % self.approver_id.name,
                'type': 'success',
                'sticky': False,
            }
        }
```

#### 2. Extend `models/account_move.py`

**Add Override Tracking**:
```python
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    three_way_match_override_approved = fields.Boolean('Override Approved', default=False)
    three_way_match_override_by = fields.Many2one('res.users', 'Override Approved By')
    three_way_match_override_date = fields.Datetime('Override Approval Date')
    three_way_match_override_reason = fields.Text('Override Reason')
    
    def action_request_three_way_override(self):
        """Open override request wizard."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request Three-Way Match Override',
            'res_model': 'three.way.match.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
    
    def action_approve_three_way_override(self):
        """Approve override (called from approval system)."""
        self.write({
            'three_way_match_override_approved': True,
            'three_way_match_override_by': self.env.user.id,
            'three_way_match_override_date': fields.Datetime.now(),
            'three_way_match_status': 'override_approved',
        })
        
        self.message_post(
            body=_('<p><strong>Three-Way Match Override APPROVED</strong></p>'
                   '<p>Approved by: %s</p>') % self.env.user.name,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_post(self):
        """Updated to allow override-approved invoices."""
        for move in self:
            if move.three_way_match_status == 'blocked':
                if not move.three_way_match_override_approved and move.company_id.three_way_match_block_validation:
                    raise UserError(
                        _("Cannot validate this invoice due to three-way match issues.\n\n"
                          "Use 'Request Override' button to request approval from a manager.")
                    )
        return super().action_post()
```

#### 3. Governance Rule Template

**File**: `data/ops_governance_rule_three_way_match.xml`

```xml
<odoo>
    <data noupdate="1">
        <!-- Three-Way Match Override Approval -->
        <record id="governance_three_way_match_override" model="ops.governance.rule">
            <field name="name">Three-Way Match Override - Purchase Manager Approval</field>
            <field name="rule_type">approval</field>
            <field name="document_model">account.move</field>
            <field name="condition_type">python</field>
            <field name="condition_value">record.three_way_match_status == 'blocked'</field>
            <field name="approval_level">1</field>
            <field name="approver_persona_id" ref="ops_matrix_core.persona_purchase_manager"/>
            <field name="description">Vendor invoices with three-way match discrepancies require Purchase Manager approval to override.</field>
            <field name="active" eval="False"/>
            <field name="sequence">60</field>
        </record>
    </data>
</odoo>
```

### Views to Create/Modify

#### 1. Override Wizard View

**File**: `wizard/three_way_match_override_wizard_views.xml`

```xml
<record id="view_three_way_match_override_wizard" model="ir.ui.view">
    <field name="name">three.way.match.override.wizard.form</field>
    <field name="model">three.way.match.override.wizard</field>
    <field name="arch" type="xml">
        <form string="Request Three-Way Match Override">
            <group>
                <div class="alert alert-danger" role="alert">
                    <h4>⚠️ Three-Way Match Issues Detected</h4>
                    <field name="match_issues" readonly="1" nolabel="1"/>
                </div>
                
                <field name="invoice_id" invisible="1"/>
                
                <group string="Override Request">
                    <field name="approver_id" placeholder="Select manager to approve override..."/>
                    <field name="override_reason" 
                           placeholder="Explain why this invoice should be approved despite the mismatch (min 20 characters)..."
                           nolabel="1"/>
                </group>
                
                <div class="alert alert-warning" role="alert">
                    <strong>Important:</strong> Override approvals are logged and auditable. 
                    Provide clear justification for why this mismatch is acceptable.
                </div>
            </group>
            
            <footer>
                <button name="action_request_override" type="object" string="Request Override" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

#### 2. Invoice Form - Add Override Button

**File**: `views/account_move_views.xml` (extend)

```xml
<xpath expr="//form/header/button[@name='action_post']" position="before">
    <button name="action_request_three_way_override"
            type="object"
            string="Request Override"
            class="btn-warning"
            attrs="{'invisible': [('three_way_match_status', '!=', 'blocked')]}"/>
</xpath>

<!-- Add override info -->
<xpath expr="//field[@name='three_way_match_status']" position="after">
    <field name="three_way_match_override_approved" 
           attrs="{'invisible': [('three_way_match_override_approved', '=', False)]}"/>
    <field name="three_way_match_override_by"
           attrs="{'invisible': [('three_way_match_override_approved', '=', False)]}"/>
    <field name="three_way_match_override_date"
           attrs="{'invisible': [('three_way_match_override_approved', '=', False)]}"/>
</xpath>
```

### Testing Checklist (Phase 2)

**Override Request**:
- [ ] Blocked invoice shows "Request Override" button
- [ ] Wizard opens with match issues pre-filled
- [ ] Approver selection limited to Purchase Managers
- [ ] Reason validation (min 20 chars)
- [ ] Approval request created
- [ ] Chatter post on invoice

**Override Approval**:
- [ ] Approver receives notification
- [ ] Approver can approve/reject
- [ ] Approval unlocks invoice
- [ ] Override fields populated correctly
- [ ] Chatter updated
- [ ] Invoice can now be validated

**Override Rejection**:
- [ ] Rejection blocks invoice validation
- [ ] User notified of rejection
- [ ] Can request new override

**Audit Trail**:
- [ ] All overrides logged
- [ ] Override reason recorded
- [ ] Approver recorded
- [ ] Timestamp recorded
- [ ] Chatter shows full history

---

## Integration Points

### With Existing Systems

1. **Purchase Orders**
   - Track ordered quantities
   - Link to match records

2. **Stock Moves**
   - Track received quantities
   - Update match records on receipt

3. **Vendor Bills**
   - Validate against match records
   - Block if mismatch
   - Track billed quantities

4. **Approval System**
   - Request override approval
   - Track approval status
   - Unlock on approval

5. **Chatter**
   - Post match issues
   - Post override requests
   - Post approval decisions

### Data Flow

```
PO Created → Match Record Created (ordered_qty)
    ↓
Receipt Done → Match Record Updated (received_qty)
    ↓
Bill Created → Match Record Updated (billed_qty)
    ↓
Match State Computed
    ↓
If BLOCKED → Prevent Validation
    ↓
Request Override → Create Approval
    ↓
Approval Granted → Unlock Invoice
    ↓
Invoice Validated → Payment Allowed
```

---

## Security

### Access Control

**Three-Way Match Records**:
- View: Purchase User, Purchase Manager, AP Clerk
- Create/Write: System only (automatic)
- Delete: System Admin only

**Override Requests**:
- Create: AP Clerk, Purchase User
- Approve: Purchase Manager, CFO
- View: All involved parties

### Record Rules

```python
# Purchase users see their branch's matches only
<record id="rule_three_way_match_branch" model="ir.rule">
    <field name="name">Three-Way Match: Branch Access</field>
    <field name="model_id" ref="model_ops_three_way_match"/>
    <field name="domain_force">[
        ('purchase_order_id.ops_branch_id', 'in', user.ops_branch_ids.ids)
    ]</field>
    <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_purchase_user'))]"/>
</record>

# Managers see all
<record id="rule_three_way_match_manager" model="ir.rule">
    <field name="name">Three-Way Match: Manager All Access</field>
    <field name="model_id" ref="model_ops_three_way_match"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('ops_matrix_core.group_ops_manager'))]"/>
</record>
```

---

## Performance Considerations

### Optimization Strategies

1. **Computed Field Storage**
   - Store `received_qty`, `billed_qty`, `match_state`
   - Recompute only when dependencies change

2. **Bulk Match Creation**
   - Create match records in batch
   - When PO is confirmed, create all line matches

3. **Indexing**
   - Index `purchase_line_id` for fast lookups
   - Index `match_state` for filtering

4. **Caching**
   - Cache tolerance settings per company
   - Reduce repeated database queries

### Expected Performance

- **Match Calculation**: <100ms per line
- **Invoice Validation**: <500ms (includes match check)
- **Report Loading**: <2s for 1,000 matches

---

## User Documentation Needed

### Quick Start Guide

1. **Setup** (5 minutes)
   - Enable three-way match in Company settings
   - Set tolerance percentage (default 5%)
   - Assign Purchase Manager personas

2. **Daily Operations** (AP Clerk)
   - Receive vendor bill
   - System auto-checks match
   - If blocked: Request override
   - If matched: Validate normally

3. **Override Approval** (Purchase Manager)
   - Receive override request
   - Review match issues
   - Check with receiving department
   - Approve or reject with reason

4. **Monitoring** (CFO/Controller)
   - Open Three-Way Match Report
   - Filter: Blocked items
   - Review frequent overrides
   - Investigate patterns

### FAQ

**Q: What if we receive partial deliveries?**  
A: System tracks cumulative received quantity. Invoice can match total received so far.

**Q: What if vendor splits invoice?**  
A: System tracks cumulative billed quantity. Multiple invoices can total to received qty.

**Q: Can I bypass three-way match?**  
A: Only with override approval from Purchase Manager. All bypasses are logged.

**Q: What tolerance should I use?**  
A: Start with 5%. Adjust based on your vendor reliability and industry norms.

---

## Success Metrics

**Feature Success If**:
- ✅ 95%+ of invoices pass match automatically
- ✅ Override requests <5% of total invoices
- ✅ No overpayments for unreceived goods
- ✅ Vendor disputes reduced by 50%+
- ✅ AP processing time unchanged

---

## Future Enhancements (Out of Scope)

1. **Price Matching**
   - Validate invoice price = PO price
   - Flag variances

2. **Return Handling**
   - Account for returned goods
   - Adjust match records

3. **Advance Shipping Notice**
   - Pre-validate based on ASN
   - Faster receipt processing

4. **Machine Learning**
   - Predict approval likelihood
   - Auto-approve low-risk variances

5. **Vendor Scorecard**
   - Track match compliance per vendor
   - Identify problematic vendors

---

## READY FOR DEVELOPMENT

**Phase 1**: Core matching engine (Session 1)  
**Phase 2**: Override approval (Session 2)  
**Total Effort**: 4-6 hours over 2 sessions  

**All requirements defined. Ready for RooCode!** 🚀
