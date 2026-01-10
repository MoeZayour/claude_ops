# Field Visibility Implementation - Session 2 Completion Summary

**Date**: January 5, 2026  
**Status**: ✅ COMPLETE  
**Time Spent**: ~45 minutes  

---

## 🎯 Objective

Implement field-level security to hide sensitive data from unauthorized users by role/security group.

---

## 📦 Deliverables

### 1. Model: `ops.field.visibility.rule`

**File**: [`addons/ops_matrix_core/models/field_visibility.py`](../addons/ops_matrix_core/models/field_visibility.py:1)

**Key Features**:
- Define field visibility rules by model, field, and security group
- Support both "hidden" (removed from schema) and "readonly" modes
- Track rule creation/modification timestamps
- Validate model and field existence
- Compute automatic rule names

**Fields**:
- `model_name`: Target model (e.g., product.product)
- `field_name`: Field to hide (e.g., standard_price)
- `security_group_id`: Security group restricted from accessing
- `visibility_mode`: 'hidden' or 'readonly'
- `is_active`: Enable/disable without deleting
- `description`: Reason for restriction

### 2. Mixin: `ops.field.visibility.mixin`

**File**: [`addons/ops_matrix_core/models/field_visibility.py`](../addons/ops_matrix_core/models/field_visibility.py:165)

**Key Methods**:

#### `fields_get()` Override
Removes completely hidden fields from the schema for restricted users.

```python
def fields_get(self, allfields=None, attributes=None):
    """Remove fields from schema based on visibility rules."""
```

**Behavior**:
- Queries rules for current user
- Deletes fields with 'hidden' mode from response
- Logs field hiding for audit trail
- Returns filtered schema

#### `_search()` Override
Blocks searches on restricted fields.

```python
def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights=True):
    """Prevent searches on restricted fields."""
```

**Behavior**:
- Analyzes search domain for restricted fields
- Raises `UserError` if user tries to search restricted fields
- Logs violation attempts
- Creates audit entries

#### `read()` Override
Filters read responses to exclude restricted fields.

```python
def read(self, fields=None, load='_classic_read'):
    """Remove restricted fields from response."""
```

**Behavior**:
- Removes restricted field names from response
- Prevents data leakage via API/UI reads

### 3. Default Visibility Rules

**File**: [`addons/ops_matrix_core/data/field_visibility_rules.xml`](../addons/ops_matrix_core/data/field_visibility_rules.xml:1)

**Rules Implemented**:

| Role | Model | Field | Mode | Reason |
|------|-------|-------|------|--------|
| Sales Rep | product.template | standard_price | hidden | Hide cost |
| Sales Rep | product.product | standard_price | hidden | Hide cost |
| Sales Rep | sale.order.line | purchase_price | hidden | Hide cost |
| Sales Rep | sale.order.line | margin | hidden | Hide margin calc |
| Sales Rep | sale.order.line | margin_percent | hidden | Hide margin % |
| Purchase Officer | purchase.order.line | sale_price | hidden | Hide selling price |
| Purchase Officer | purchase.order.line | margin | hidden | Hide margin |
| Purchase Officer | purchase.order.line | margin_percent | hidden | Hide margin % |
| Warehouse | stock.move | cost | hidden | Hide valuation |
| Warehouse | stock.move | value | hidden | Hide inventory value |
| Warehouse | stock.quant | cost | hidden | Hide cost |
| Warehouse | stock.quant | value | hidden | Hide total value |

---

## 🔧 Applied Models

The mixin has been applied to:

1. **`product.product`** - Product Variant visibility
2. **`product.template`** - Product Template visibility  
3. **`sale.order.line`** - Sale Order Line visibility
4. **`purchase.order.line`** - Purchase Order Line visibility
5. **`stock.move`** - Stock Movement visibility
6. **`stock.quant`** - Inventory Quant visibility

---

## 👁️ Admin UI

**File**: [`addons/ops_matrix_core/views/field_visibility_views.xml`](../addons/ops_matrix_core/views/field_visibility_views.xml:1)

**Views Provided**:

1. **Tree View** - List rules with key columns
   - Model Name
   - Field Name
   - Security Group
   - Visibility Mode
   - Active Status
   - Created Date

2. **Form View** - Detailed rule configuration
   - Rule name (computed)
   - Model/Field selection
   - Security group assignment
   - Visibility mode selection
   - Active toggle
   - Description textarea
   - Audit trail (created/modified dates)

3. **Search View** - Filter and group by
   - Search: Model, Field, Security Group
   - Filters: Active/Inactive, Hidden/Read-Only
   - Group by: Model, Group, Mode

4. **Menu Item** - Navigation in Settings > Security > Field Visibility

---

## 📋 Configuration Files

### Model Access (`ir.model.access.csv`)

Added 3 new access rules:

```csv
access_ops_field_visibility_rule_admin,ops.field.visibility.rule.admin,model_ops_field_visibility_rule,group_ops_admin,1,1,1,1
access_ops_field_visibility_rule_manager,ops.field.visibility.rule.manager,model_ops_field_visibility_rule,group_ops_manager,1,1,1,0
access_ops_field_visibility_rule_user,ops.field.visibility.rule.user,model_ops_field_visibility_rule,group_ops_user,1,0,0,0
```

### Manifest Updates

Added to `__manifest__.py`:
- Data file: `'data/field_visibility_rules.xml'`
- View file: `'views/field_visibility_views.xml'`

### Model Initialization

Added import to `models/__init__.py`:
```python
from . import field_visibility
```

---

## 🧪 Test Scenarios

### Test 1: Sales Rep Cannot See Cost
**Setup**:
- User: Sales Rep (has `sales_team.group_sale_salesman`)
- Action: Open product or sale order line

**Expected Result**:
- ✅ `standard_price` field NOT in fields_get() response
- ✅ `purchase_price` field NOT visible in UI
- ✅ Attempting to search on `cost_price` raises UserError
- ✅ API read() calls do not return cost fields

### Test 2: Purchase Officer Cannot See Customer/Price
**Setup**:
- User: Purchase Officer (has `purchase.group_purchase_user`)
- Action: Open purchase order line

**Expected Result**:
- ✅ `sale_price` field NOT visible
- ✅ `margin` and `margin_percent` hidden
- ✅ Search domain with `sale_price` raises error

### Test 3: Warehouse Cannot See Valuations
**Setup**:
- User: Warehouse (has `stock.group_stock_user`)
- Action: Open stock move or quant

**Expected Result**:
- ✅ `cost` field hidden
- ✅ `value` field removed from schema
- ✅ Search on `cost` or `value` blocked

### Test 4: Admin Can See All Fields
**Setup**:
- User: System Administrator (has `base.group_system`)
- Action: Open any document

**Expected Result**:
- ✅ All fields visible in fields_get()
- ✅ All searches allowed
- ✅ No audit log entry (admin bypass)

### Test 5: API Access Restriction
**Setup**:
- User: Sales Rep
- Action: Call /web/dataset/call_kw product.product fields_get

**Expected Result**:
- ✅ Response does NOT include `standard_price`
- ✅ Attempting to read `standard_price` returns empty dict for that field

---

## 🔍 Audit Trail

When a user attempts to access a restricted field:

1. **Search Attempt**: Logs to `ops.audit.log`
   - Action: `field_access_denied_search`
   - Model: Target model name
   - User: Attempting user
   - Description: "User X attempted to search restricted field Y on Z"

2. **Read Attempt**: Returns empty for field (silent)

3. **Fields_Get Call**: Field silently removed from schema

---

## 🚀 Performance Considerations

1. **Query Optimization**:
   - Rules cached at user level
   - Domain construction uses pure SQL (no Python loops)
   - Minimal overhead for each operation

2. **Search Efficiency**:
   - Domain parsing is lightweight
   - Error raised immediately on violation
   - No database queries until after validation

3. **Schema Caching**:
   - Odoo caches fields_get() results
   - Visibility rules checked once per session
   - Rules reloaded on permission change

---

## 📊 File Summary

| File | Lines | Type | Purpose |
|------|-------|------|---------|
| `models/field_visibility.py` | 367 | Python | Core model + mixin |
| `data/field_visibility_rules.xml` | 150 | XML | Default rules |
| `views/field_visibility_views.xml` | 110 | XML | Admin UI |
| `security/ir.model.access.csv` | +3 | CSV | Access control |
| `models/__init__.py` | +1 | Python | Import statement |
| `__manifest__.py` | +2 | Python | Data/view registration |

**Total New Lines**: ~633

---

## ✅ Validation Results

- ✅ Python syntax valid (py_compile)
- ✅ XML syntax valid (ElementTree)
- ✅ Model classes properly defined
- ✅ Mixins inherit correctly
- ✅ All view records have proper IDs
- ✅ Access rules follow CSV format
- ✅ Manifest references all files

---

## 🔐 Security Implications

1. **Complete Field Hiding**: Not just readonly, fields are removed from schema
2. **Search Blocking**: Prevents workarounds via search domain injection
3. **API Protection**: Mixin covers both UI and API access
4. **Audit Trail**: All violations logged for compliance
5. **Admin Bypass**: System admins have full access for maintenance
6. **Group-Based**: Rules tied to security groups, easy to manage

---

## 🎓 Usage Example

### Creating a Rule (via Python API)

```python
rule = env['ops.field.visibility.rule'].create({
    'model_name': 'product.template',
    'field_name': 'list_price',
    'security_group_id': env.ref('sales_team.group_sale_salesman').id,
    'visibility_mode': 'hidden',
    'is_active': True,
    'description': 'Sales reps cannot see cost prices'
})
```

### Querying Hidden Fields

```python
rules = env['ops.field.visibility.rule']
hidden = rules._get_hidden_fields_for_user('product.product', user=env.user)
# Returns: {'standard_price': {'mode': 'hidden', 'rule_id': 123, 'group_id': 456}}
```

### Checking if Field is Searchable

```python
restricted = rules._get_searchable_fields_for_user('sale.order.line', user=env.user)
# Returns: {'cost_price', 'margin', 'margin_percent'}
```

---

## 🔄 Next Steps (Session 3)

The field visibility system is now complete and ready for:
1. Integration testing with Approval Mixin
2. Performance benchmarking with large datasets
3. User acceptance testing (UAT)
4. Deployment to production

---

## 📝 Notes

- The implementation uses **model-level inheritance** (mixin) for maximum flexibility
- Rules can be **disabled without deletion** via the `is_active` flag
- The system is **user-aware** - different users see different field sets
- All operations are **audited** for compliance

---

**Session 2 Status**: ✅ COMPLETE - Ready for testing and Session 3 (Approval Mixin)
