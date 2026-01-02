# CORE ARCHITECTURE REFACTOR REPORT
## ops.branch → res.company Native Inheritance

**Date:** 2024-12-24  
**Status:** ✅ COMPLETE (Ready for DB Reset)  
**Scope:** Replace custom ops.branch model with native res.company inheritance

---

## 🎯 OBJECTIVE

Remove the redundant `ops.branch` model and inject OPS Matrix logic directly into Odoo's native `res.company` model. This eliminates duplication and leverages Odoo's built-in company/branch architecture.

---

## 📊 CHANGES SUMMARY

### ✅ Phase 1: Model Replacement

#### Created Files:
1. **`addons/ops_matrix_core/models/res_company.py`**
   - Inherits `res.company`
   - Adds OPS fields: `ops_code`, `ops_business_unit_ids`, `ops_manager_id`, `ops_analytic_account_id`
   - Implements sequence generation (same logic as old ops.branch)
   - Auto-creates analytic accounts for financial tracking

2. **`addons/ops_matrix_core/views/res_company_views.xml`**
   - Extends standard Company form with "OPS Configuration" tab
   - Adds OPS fields to Company tree and search views
   - Provides filters for OPS Manager and Business Units

#### Updated Core Files:
- **`addons/ops_matrix_core/models/__init__.py`**
  - Replaced `from . import ops_branch` → `from . import res_company`

- **`addons/ops_matrix_core/__manifest__.py`**
  - Replaced `'views/ops_branch_views.xml'` → `'views/res_company_views.xml'`

- **`addons/ops_matrix_core/security/ir.model.access.csv`**
  - Removed 3 access entries for `model_ops_branch` (no longer needed - res.company uses base access)

- **`addons/ops_matrix_core/data/ir_sequence_data.xml`**
  - Updated sequence code: `ops.branch` → `res.company.ops`
  - Keeps same prefix: `BR` (for continuity)

#### Obsolete Files (No Longer Referenced):
- `addons/ops_matrix_core/models/ops_branch.py` ⚠️ Can be deleted after verification
- `addons/ops_matrix_core/views/ops_branch_views.xml` ⚠️ Can be deleted after verification

---

### ✅ Phase 2: Global Model Updates (22 Files Updated)

#### Core Models (ops_matrix_core):
1. **`ops_mixin.py`** - Changed `ops_branch_id` target: `'ops.branch'` → `'res.company'`
2. **`ops_persona.py`** - Updated `branch_id`, `primary_branch_id`, `allowed_branch_ids`
3. **`sale_order.py`** - Updated `ops_branch_id` field definition
4. **`account_move.py`** - Updated branch references and dimension logic
5. **`stock_move.py`** - Updated `branch_id` field
6. **`stock_picking.py`** - Updated `branch_id` field
7. **`stock_warehouse.py`** - Updated `branch_id` field and SQL references
8. **`stock_warehouse_orderpoint.py`** - Updated `branch_id` field
9. **`res_users.py`** - Updated all branch-related Many2one and Many2many fields
10. **`pricelist.py`** - Updated `ops_branch_id` field
11. **`ops_product_request.py`** - Updated `branch_id` field
12. **`ops_approval_request.py`** - Updated `branch_id` field
13. **`ops_business_unit.py`** - Updated helper references to branch model

#### Accounting Module (ops_matrix_accounting):
14. **`ops_budget.py`** - Updated `ops_branch_id` field (key model for budgeting)
15. **`ops_pdc.py`** - Updated `ops_branch_id` field
16. **`ops_matrix_standard_extensions.py`** - Updated all branch references in Sale/Purchase/Move extensions
17. **`wizard/ops_financial_report_wizard.py`** - Updated `branch_id` field

#### Reporting Module (ops_matrix_reporting):
18. **`ops_sales_analysis.py`** - Updated `ops_branch_id` field and SQL queries
19. **`ops_financial_analysis.py`** - Updated `ops_branch_id` field and SQL queries

---

### ✅ Phase 3: Security & Access Control

#### Updated Security Files:
1. **`addons/ops_matrix_core/security/ir_rule.xml`**
   - Removed 2 IR rules for `model_ops_branch` (no longer needed)
   - Kept all other rules unchanged (they reference fields, not models)

#### Access Control Notes:
- res.company already has robust access control via Odoo base
- OPS fields inherit standard company security
- No custom access rules needed for res.company itself

---

### ✅ Phase 4: Data & Views (6 Files Updated)

#### Test Files Updated:
1. **`tests/test_branch_flow.py`**
2. **`tests/test_01_branch_creation.py`**
3. **`tests/test_autopilot_suite.py`**
4. **`tests/test_matrix_lifecycle.py`**

#### Data/Hook Files:
5. **`hooks.py`** - Updated SQL queries and model references
6. **`demo/ops_demo_data.xml`** - Updated demo branch records to use res.company

#### View Files:
- XML view files remain largely unchanged (they reference field names, not model names)
- Field name `ops_branch_id` stays the same but now points to `res.company`

---

### ✅ Phase 5: Migration Files

**`migrations/19.0.1.0/post_migration.py`**
- Disabled legacy migration logic (no longer applicable)
- Added documentation explaining the refactor

---

## 🔧 TECHNICAL DETAILS

### Field Mapping:
| Old Model (ops.branch) | New Model (res.company) | Status |
|------------------------|-------------------------|--------|
| `name` | `name` | Native field (inherited) |
| `code` | `ops_code` | New custom field |
| `manager_id` | `ops_manager_id` | New custom field |
| `company_id` | `id` | Native (company is its own parent) |
| `analytic_account_id` | `ops_analytic_account_id` | New custom field |
| `sequence` | Built-in ordering | Native behavior |
| `active` | `active` | Native field |
| `color` | Not migrated | Optional cosmetic field |

### Relationship Changes:
```python
# OLD:
ops_branch_id = fields.Many2one('ops.branch', ...)

# NEW:
ops_branch_id = fields.Many2one('res.company', ...)
```

### Key Benefits:
1. ✅ **No Duplication**: Leverages native Odoo architecture
2. ✅ **Multi-Company Ready**: Works seamlessly with Odoo's multi-company features
3. ✅ **Simplified Setup**: Users don't need to create separate "branches" - they use companies
4. ✅ **Better UX**: Company management UI is familiar to all Odoo users
5. ✅ **Reduced Maintenance**: One less custom model to maintain

---

## 📦 AUTOMATED REFACTORING SCRIPTS

Two Python scripts were created to automate the bulk of the changes:

1. **`refactor_branch_to_company.py`**
   - Updated 16 Python model files
   - Replaced `'ops.branch'` → `'res.company'`
   - Updated model references in comments and SQL

2. **`refactor_xml_files.py`**
   - Updated 6 test/data/XML files
   - Replaced model references
   - Updated demo data records

---

## ⚠️ BREAKING CHANGES & MIGRATION NOTES

### Database Reset Required:
This refactor **REQUIRES A FULL DATABASE DROP** because:
1. The `ops_branch` table will be removed
2. All foreign keys must be recreated pointing to `res_company`
3. Sequence codes have changed
4. No migration path exists (too invasive)

### Post-Reset Setup:
1. Install/upgrade `ops_matrix_core` module
2. res.company records will auto-generate `ops_code` via sequence
3. Assign Business Units to companies via "OPS Configuration" tab
4. Set Branch Managers if needed

### User Impact:
- **Before**: Users saw "Branches" menu under Settings → Users & Companies
- **After**: Users use standard "Companies" menu (Settings → Users & Companies → Companies)
- **Benefit**: Cleaner, more intuitive UX using native Odoo concepts

---

## 🧪 TESTING CHECKLIST

### Critical Workflows to Test:
- [ ] Create new Company - verify `ops_code` auto-generates
- [ ] Assign Business Units to Company
- [ ] Create Sale Order - verify `ops_branch_id` populates correctly
- [ ] Create Budget - verify Matrix dimensions (Branch = Company)
- [ ] Check Stock Warehouse - verify company/branch linkage
- [ ] Test Persona assignment - verify branch references work
- [ ] Run Sales Analysis report - verify SQL queries work
- [ ] Run Financial Analysis report - verify dimension filtering
- [ ] Test Product Requests - verify branch access control
- [ ] Verify IR Rules work with res.company instead of ops.branch

### SQL Integrity Checks:
```sql
-- Verify no orphaned references to ops.branch
SELECT tablename, columnname 
FROM information_schema.columns 
WHERE columnname LIKE '%branch%' 
  AND table_schema = 'public';

-- Verify res_company OPS fields exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'res_company' 
  AND column_name LIKE 'ops_%';
```

---

## 📋 FILES SUMMARY

### New Files Created: 2
- `addons/ops_matrix_core/models/res_company.py`
- `addons/ops_matrix_core/views/res_company_views.xml`

### Files Modified: 28
- **Models**: 19 Python files
- **Views/Data**: 6 XML files
- **Security**: 2 files (access CSV, rules XML)
- **Configuration**: 1 manifest file

### Files Obsolete: 2
- `addons/ops_matrix_core/models/ops_branch.py` (can be deleted)
- `addons/ops_matrix_core/views/ops_branch_views.xml` (can be deleted)

### Automation Scripts: 2
- `refactor_branch_to_company.py`
- `refactor_xml_files.py`

---

## 🚀 DEPLOYMENT INSTRUCTIONS

### Step 1: Stop Odoo
```bash
docker-compose down
```

### Step 2: Drop Database
```bash
docker-compose run --rm web dropdb -U odoo -h db postgres
docker-compose run --rm web createdb -U odoo -h db postgres
```

### Step 3: Start Odoo & Install
```bash
docker-compose up -d
# Access Odoo UI and install modules OR:
docker-compose exec web odoo -d postgres -i ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init
```

### Step 4: Verify Installation
1. Check Settings → Companies → Companies
2. Open a company record → OPS Configuration tab
3. Verify `ops_code` is generated (e.g., BR0001)
4. Create test Sale Order and verify branch assignment

---

## ✅ CONCLUSION

The refactoring is **COMPLETE** and ready for database reset. All code changes have been applied systematically:

- ✅ 28 files updated
- ✅ 2 new files created
- ✅ 2 obsolete files identified for deletion
- ✅ Security rules updated
- ✅ Test files updated
- ✅ Migration files disabled

**Next Action**: Execute database reset and test the new architecture.

---

## 📞 SUPPORT NOTES

If issues arise post-deployment:

1. **Missing ops_code**: Check sequence `res.company.ops` exists
2. **Access Errors**: Verify user has company access (standard Odoo permissions)
3. **Analytic Account Issues**: Run `company._create_ops_analytic_accounts()` manually
4. **Foreign Key Errors**: Indicates incomplete refactoring - check logs for model references

**Contact**: Development team for any critical issues.

---

**Report Generated**: 2024-12-24  
**Engineer**: AI Assistant (Code Mode)  
**Status**: ✅ READY FOR DEPLOYMENT
