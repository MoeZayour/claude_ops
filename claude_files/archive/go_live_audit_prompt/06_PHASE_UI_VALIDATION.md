# Phase 5: UI/UX Validation

**Duration:** 45 minutes  
**Objective:** Verify all views render correctly and UI is functional

---

## UI TESTING APPROACH

Test each view type:
1. **List/Tree Views** - Render, columns, sorting, filtering
2. **Form Views** - Fields, buttons, tabs, chatter
3. **Kanban Views** - Cards, stages, drag-drop
4. **Search Views** - Filters, groupings
5. **Menu Structure** - All menus accessible
6. **Buttons** - State transitions work

---

## Task 5.1: Verify Menu Structure

```bash
echo "========================================"
echo "PHASE 5: UI/UX VALIDATION"
echo "========================================"

echo "=== Checking menu items ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT 
    m.name,
    m.complete_name,
    a.name as action_name
FROM ir_ui_menu m
LEFT JOIN ir_act_window a ON m.action::text LIKE '%,' || a.id::text
WHERE m.complete_name LIKE '%OPS%' OR m.complete_name LIKE '%Matrix%'
ORDER BY m.complete_name
LIMIT 50;
"

echo "✅ Menu structure retrieved"
```

---

## Task 5.2: Verify Views Load Without Errors

```python
# ============================================================
# VIEW LOADING TESTS
# ============================================================

print("Testing View Loading...")

# List of OPS models to test
ops_models = [
    'ops.branch',
    'ops.business.unit',
    'ops.persona',
    'ops.governance.rule',
    'ops.approval.request',
    'ops.sla.template',
    'ops.pdc.receivable',
    'ops.pdc.payable',
    'ops.asset',
    'ops.asset.category',
    'ops.budget',
    'ops.kpi',
    'ops.dashboard',
]

view_errors = []

for model_name in ops_models:
    try:
        model = env[model_name]
        
        # Test tree view
        try:
            tree_view = model.get_view(view_type='tree')
            print(f"✅ {model_name} - Tree view OK")
        except Exception as e:
            view_errors.append(f"{model_name} tree: {e}")
            print(f"❌ {model_name} - Tree view ERROR: {e}")
        
        # Test form view
        try:
            form_view = model.get_view(view_type='form')
            print(f"✅ {model_name} - Form view OK")
        except Exception as e:
            view_errors.append(f"{model_name} form: {e}")
            print(f"❌ {model_name} - Form view ERROR: {e}")
        
        # Test search view
        try:
            search_view = model.get_view(view_type='search')
            print(f"✅ {model_name} - Search view OK")
        except Exception as e:
            # Search view optional
            print(f"⚠️ {model_name} - No search view")
            
    except KeyError:
        print(f"⚠️ Model {model_name} not found - skipping")
    except Exception as e:
        view_errors.append(f"{model_name}: {e}")
        print(f"❌ {model_name} - ERROR: {e}")

print(f"\n{'='*50}")
print(f"View Errors: {len(view_errors)}")
for err in view_errors:
    print(f"  - {err}")
```

---

## Task 5.3: Test Extended Standard Model Views

```python
# ============================================================
# EXTENDED MODEL VIEWS
# ============================================================

print("\nTesting Extended Standard Model Views...")

extended_models = [
    'sale.order',
    'purchase.order',
    'account.move',
    'account.payment',
    'stock.picking',
    'res.users',
    'res.partner',
    'product.template',
]

for model_name in extended_models:
    try:
        model = env[model_name]
        
        # Check if OPS fields exist in form view
        form_view = model.get_view(view_type='form')
        arch = form_view.get('arch', '')
        
        has_branch = 'ops_branch_id' in arch
        has_bu = 'ops_business_unit_id' in arch
        
        if has_branch or has_bu:
            print(f"✅ {model_name} - OPS fields in view (branch: {has_branch}, BU: {has_bu})")
        else:
            print(f"⚠️ {model_name} - OPS fields may not be in form view")
            
    except Exception as e:
        print(f"❌ {model_name} - ERROR: {e}")
```

---

## Task 5.4: Test Button Actions

```python
# ============================================================
# BUTTON ACTION TESTS
# ============================================================

print("\nTesting Button Actions...")

# Test PDC Receivable buttons
try:
    pdc = env['ops.pdc.receivable'].search([], limit=1)
    if pdc:
        print(f"Testing PDC: {pdc.name}, State: {pdc.state}")
        
        # Check action methods exist
        actions = ['action_register', 'action_deposit', 'action_clear', 
                   'action_bounce', 'action_cancel']
        for action in actions:
            if hasattr(pdc, action):
                print(f"  ✅ Button method exists: {action}")
            else:
                print(f"  ⚠️ Button method missing: {action}")
except Exception as e:
    print(f"⚠️ PDC button test error: {e}")

# Test Sale Order buttons
try:
    so = env['sale.order'].search([], limit=1)
    if so:
        print(f"\nTesting Sale Order: {so.name}, State: {so.state}")
        
        # Check approval-related buttons
        approval_actions = ['action_submit_approval', 'action_recall_approval']
        for action in approval_actions:
            if hasattr(so, action):
                print(f"  ✅ Approval method exists: {action}")
            else:
                print(f"  ⚠️ Approval method not found: {action}")
except Exception as e:
    print(f"⚠️ SO button test error: {e}")
```

---

## Task 5.5: Test Theme Elements (if ops_theme installed)

```python
# ============================================================
# THEME VALIDATION
# ============================================================

print("\nValidating Theme...")

try:
    # Check company theme settings
    company = env['res.company'].search([], limit=1)
    
    theme_fields = [
        'ops_theme_preset',
        'ops_primary_color',
        'ops_secondary_color',
        'ops_login_tagline',
    ]
    
    for field in theme_fields:
        if hasattr(company, field):
            value = getattr(company, field)
            print(f"✅ {field}: {value or '(not set)'}")
        else:
            print(f"⚠️ {field}: Field not found")
    
    # Check user preferences
    user = env['res.users'].browse(env.uid)
    user_fields = ['ops_chatter_position', 'ops_color_mode']
    
    for field in user_fields:
        if hasattr(user, field):
            value = getattr(user, field)
            print(f"✅ User {field}: {value or '(default)'}")
        else:
            print(f"⚠️ User {field}: Field not found")

except Exception as e:
    print(f"⚠️ Theme validation error: {e}")
```

---

## Task 5.6: Test Dashboard Views (if ops_dashboard installed)

```python
# ============================================================
# DASHBOARD VALIDATION
# ============================================================

print("\nValidating Dashboards...")

try:
    dashboards = env['ops.dashboard'].search([])
    print(f"Total dashboards: {len(dashboards)}")
    
    for dash in dashboards:
        print(f"\nDashboard: {dash.name} ({dash.code})")
        print(f"  Type: {dash.dashboard_type}")
        print(f"  Widgets: {len(dash.widget_ids)}")
        print(f"  Auto-refresh: {dash.auto_refresh}")
        
        # Check widget configuration
        for widget in dash.widget_ids[:3]:  # First 3 widgets
            print(f"    - Widget: {widget.name}, Type: {widget.widget_type}")
    
    # Test KPIs
    kpis = env['ops.kpi'].search([])
    print(f"\nTotal KPIs: {len(kpis)}")
    
    for kpi in kpis[:5]:  # First 5 KPIs
        print(f"  - {kpi.name} ({kpi.code}): {kpi.calculation_type}")

except Exception as e:
    print(f"⚠️ Dashboard validation error: {e}")
```

---

## Task 5.7: Check for JavaScript Errors

```bash
echo "=== Checking for JS asset compilation errors ==="
docker logs gemini_odoo19 --tail 500 | grep -E "(JavaScript|SCSS|asset|bundle)" | head -20

echo "=== Checking webclient assets ==="
docker exec gemini_odoo19 psql -U odoo -d mz-db -c "
SELECT name, create_date 
FROM ir_attachment 
WHERE name LIKE '%web.assets%' 
ORDER BY create_date DESC 
LIMIT 10;
"
```

---

## Task 5.8: Validate Report Templates

```python
# ============================================================
# REPORT TEMPLATE VALIDATION
# ============================================================

print("\nValidating Report Templates...")

try:
    # Check QWeb reports
    reports = env['ir.actions.report'].search([
        '|', 
        ('model', 'like', 'ops.%'),
        ('report_name', 'like', 'ops_%')
    ])
    
    print(f"Total OPS reports: {len(reports)}")
    
    for report in reports:
        print(f"  - {report.name}: {report.report_type} ({report.model})")
        
        # Try to get template
        try:
            template = env.ref(report.report_name.replace('.', '_'))
            print(f"    ✅ Template found")
        except:
            print(f"    ⚠️ Template not found by ref")

except Exception as e:
    print(f"⚠️ Report validation error: {e}")
```

---

## Task 5.9: Test Wizard Forms

```python
# ============================================================
# WIZARD FORM VALIDATION
# ============================================================

print("\nValidating Wizard Forms...")

wizards = [
    'ops.approval.recall.wizard',
    'ops.approval.reject.wizard',
    'ops.financial.report.wizard',
    'ops.general.ledger.wizard',
    'ops.pdc.report.wizard',
    'ops.asset.register.wizard',
]

for wizard_name in wizards:
    try:
        wizard = env[wizard_name]
        form_view = wizard.get_view(view_type='form')
        print(f"✅ {wizard_name} - Form view OK")
    except KeyError:
        print(f"⚠️ {wizard_name} - Model not found")
    except Exception as e:
        print(f"❌ {wizard_name} - ERROR: {e}")
```

---

## Task 5.10: Generate UI Test Report

Create `/opt/gemini_odoo19/claude_files/go_live_audit/05_UI_TEST_REPORT.md`:

```markdown
# UI/UX Test Report

**Date:** [DATE]
**Executor:** Claude Code

## View Test Summary

| Category | Views Tested | Passed | Failed |
|----------|--------------|--------|--------|
| OPS Model Tree Views | X | X | X |
| OPS Model Form Views | X | X | X |
| OPS Model Search Views | X | X | X |
| Extended Model Views | X | X | X |
| Wizard Forms | X | X | X |
| Dashboard Views | X | X | X |
| Reports | X | X | X |
| **TOTAL** | **X** | **X** | **X** |

## Menu Structure

[List all accessible OPS menus]

## Theme Validation

| Setting | Value | Status |
|---------|-------|--------|
| Primary Color | #XXXXX | ✅/⚠️ |
| Secondary Color | #XXXXX | ✅/⚠️ |
| ... | ... | ... |

## View Errors Found

| Model | View Type | Error | Resolution |
|-------|-----------|-------|------------|
| ... | ... | ... | ... |

## Button Tests

| Model | Button | Exists | Works |
|-------|--------|--------|-------|
| ops.pdc.receivable | action_register | ✅/❌ | ✅/❌ |
| ... | ... | ... | ... |

## JavaScript/Asset Issues

[List any JS or asset compilation errors]

## Recommendations

[UI/UX improvement recommendations]
```

---

## PROCEED TO PHASE 6
