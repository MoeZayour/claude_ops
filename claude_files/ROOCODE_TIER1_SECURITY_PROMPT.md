# RooCode Agent: Tier 1 Critical Security Implementation

**Date**: January 5, 2026  
**Target**: Complete Tier 1 Security implementation  
**Expected Duration**: 3 sessions, 8-12 hours total  
**Success Metric**: All 3 Tier 1 items production-ready

---

## 🥇 TIER 1: CRITICAL SECURITY - YOUR PRIORITY

This is the foundation. Everything else depends on getting security right.

### 1. SEGREGATION OF DUTIES (SoD) - PREVENT FRAUD
**Estimated Time**: 3-4 hours  
**Deliverable**: Block same user from creating AND confirming transactions

#### What This Does
- Sales Rep creates $5K SO → Cannot confirm it
- Purchase Officer creates $10K PO → Cannot confirm it
- AR Clerk creates invoice → Cannot post it
- **Violation logged with full audit trail for compliance**

#### Implementation
**File**: Create `addons/ops_matrix_core/models/segregation_of_duties.py`

Model: `ops.segregation.of.duties` - Define rules (SO create+confirm=blocked, etc)
Mixin: `ops.segregation.of.duties.mixin` - Apply to SO, PO, Invoice, Payment
Rules: Create 4 default rules in `data/default_sod_rules.xml`

Key methods:
- `_check_sod_rules()` - Enforce rule before action
- `_handle_sod_violation()` - Log violation, raise error if blocked

Test:
- [ ] User A creates SO → User B confirms (success)
- [ ] User A creates SO → User A confirms (blocked + error message)
- [ ] Violation appears in `ops.segregation.of.duties.log`

---

### 2. FIELD VISIBILITY - HIDE SENSITIVE DATA
**Estimated Time**: 2-3 hours  
**Deliverable**: Cost/margin hidden from Sales, Price hidden from Purchase

#### What This Does
- Sales Rep views SO → sees sale_price, NOT cost_price
- Purchase Officer views PO → sees cost_price, NOT sale_price
- Warehouse views Stock → sees quantity, NOT any prices
- **Fields completely hidden, not just readonly**

#### Implementation
**File**: Create `addons/ops_matrix_core/models/field_visibility.py`

Mixin: `ops.field.visibility.mixin` - Control field visibility by security group
Views: Create `views/field_visibility.xml` - Hide fields at UI level

Key methods:
- `fields_get()` - Remove fields from schema for unauthorized users
- `_search()` - Block searching on restricted fields

Apply to:
- Product Template/Variant
- Sale Order Line
- Purchase Order Line
- Stock Valuation

Test:
- [ ] Login as Sales Rep → Open Product → standard_price INVISIBLE
- [ ] Login as Purchase Officer → Open PO → customer/supplier HIDDEN
- [ ] Login as Warehouse → Open Stock → value/cost MISSING
- [ ] Search for cost_price as Sales Rep → ERROR

---

### 3. APPLY APPROVAL MIXIN - LOCK DOCUMENTS IN WORKFLOW
**Estimated Time**: 2-3 hours  
**Deliverable**: Document becomes read-only during approval

#### What This Does
- Create SO → Can edit
- Confirm SO → Becomes READ-ONLY
- Recall SO → Can edit again
- **No field editing possible while in approval workflow**

#### Implementation
Mixin already exists: `addons/ops_matrix_core/models/ops_approval_mixin.py`

Just apply to these models by adding `_inherit`:
1. sale.order
2. purchase.order
3. account.move (invoke action_post())
4. account.payment (invoke action_post())
5. stock.picking (invoke button_validate())

Verify mixin has:
- `is_locked` field
- `_check_approval_workflow()` method
- `write()` override that blocks edits if locked
- Recall wizard to unlock

Test:
- [ ] SO: edit before confirm → success
- [ ] SO: edit after confirm → blocked
- [ ] SO: recall → can edit again
- [ ] Same for PO, Invoice, Payment

---

## 📋 IMPLEMENTATION TIMELINE

### Session 1: SoD (3-4 hours)
1. Create segregation_of_duties.py (250 lines)
2. Create default_sod_rules.xml (50 lines)
3. Apply mixin to SO, PO, Invoice, Payment (10 lines each)
4. Test all 4 SoD rules
5. Verify audit log created

### Session 2: Field Visibility (2-3 hours)
1. Create field_visibility.py (200 lines)
2. Create field_visibility.xml (100 lines)
3. Apply to Products, SO Lines, PO Lines, Stock
4. Test visibility for each persona
5. Verify field schema changes

### Session 3: Approval Mixin (2-3 hours)
1. Verify mixin is complete
2. Apply to SO, PO, Invoice, Payment, Stock (5 models)
3. Test locking on each
4. Verify chatter integration
5. Test recall/reject workflow

---

## 🎯 SUCCESS CRITERIA

**SoD**:
- ✓ SO: User A creates, User A cannot confirm (blocked)
- ✓ PO: User A creates >$5K, User B must confirm
- ✓ Invoice: Creator cannot post it
- ✓ Payment: Creator cannot approve >$2K
- ✓ Log shows user, doc, action, timestamp

**Field Visibility**:
- ✓ Sales Rep: cost_price INVISIBLE everywhere
- ✓ Purchase Officer: customer HIDDEN in PO
- ✓ Warehouse: cost/value MISSING in Stock
- ✓ Fields not in schema (not just readonly)

**Approval Locking**:
- ✓ SO: locked after confirm, edit button gone
- ✓ Recall unlocks, edit button reappears
- ✓ Chatter logs: "Locked during approval", "Unlocked by [user]"
- ✓ Works on PO, Invoice, Payment, Stock

---

## 📊 DELIVERABLES

**Code** (500+ lines):
- segregation_of_duties.py (250 lines)
- field_visibility.py (200 lines)
- Model inheritance updates (50 lines)

**Data** (150+ lines):
- default_sod_rules.xml (50 lines)
- field_visibility.xml (100 lines)

**Testing**:
- SoD rules verified (4 tests)
- Field visibility verified (8 tests)
- Approval locking verified (5 tests)

**Documentation**:
- Implementation summary
- Test results
- Security checklist

---

## 🚨 CRITICAL NOTES

1. Security groups exist (created in Priority #3):
   - group_ops_see_cost
   - group_ops_see_margin
   - group_ops_see_valuation

2. Test with real users (not admin) - personas have different groups

3. Violations must be logged - compliance audit trail

4. All configurable - admin can enable/disable rules

5. No performance impact - use efficient queries

---

**This is Tier 1. Do this before anything else. Then all other features have solid security foundation.**
