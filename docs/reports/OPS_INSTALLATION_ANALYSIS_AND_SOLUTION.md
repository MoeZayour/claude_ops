# OPS Framework Installation Analysis & Complete Solution

**Date**: January 5, 2026  
**Analysis By**: Claude  
**Status**: COMPREHENSIVE REVIEW COMPLETE

---

## 📋 EXECUTIVE SUMMARY

The agent disabled **16 data files** from the manifest to allow module installation without circular dependencies. This was the correct approach to get the models installed. Now we need to:

1. ✅ Install modules (creates database tables)
2. ✅ Load data files in correct order (after models exist)
3. ✅ Seed comprehensive test data

---

## 🔍 WHAT THE AGENT DISABLED

### Files Commented Out in `__manifest__.py`:

```python
# Temporarily disabled - require personas to be created first
# 'data/ops_default_data.xml',
# 'data/ops_default_data_clean.xml',
# 'data/ops_governance_rule_templates.xml',
# 'data/ops_governance_templates.xml',
# 'data/ops_governance_templates_extended.xml',
# 'data/ops_persona_templates.xml',
# 'data/ops_product_templates.xml',
# 'data/ops_sla_templates.xml',
# 'data/product_rules.xml',
# 'data/ops_sod_default_rules.xml',
# 'data/field_visibility_rules.xml',
# 'data/templates/ops_persona_templates.xml',
# 'data/templates/ops_governance_rule_templates.xml',
# 'data/templates/ops_user_templates.xml',
# 'data/ops_governance_rule_three_way_match.xml',
# 'data/templates/ops_sla_templates.xml',
```

### Files Modified:

1. **ops_account_templates.xml** - Stripped down to basic account structure only
   - Removed: Tax records (need tax_group_id)
   - Removed: Payment terms (invalid field names)
   - Kept: Basic account groups and 4 core accounts

---

## ⚠️ WHY THESE WERE DISABLED

### 1. Circular Dependencies

**Problem**: Data files reference models that haven't been created yet

```
ops_persona_templates.xml → Needs ops.persona model
ops_governance_rule_templates.xml → Needs ops.governance.rule + ops.persona
ops_sod_default_rules.xml → Needs ops.segregation.of.duties model
field_visibility_rules.xml → Needs ops.field.visibility.rule model
```

**Solution**: Install models first, then load data

### 2. Missing Required Fields

**Problem**: Odoo 19 has stricter validation

```
Tax records → require tax_group_id (NOT NULL constraint)
Payment terms → use invalid 'value' field (should be 'value_amount')
```

**Solution**: Fix field names or create required dependencies first

### 3. Data Dependencies

**Problem**: Some data files depend on others being loaded first

```
ops_governance_rule_templates.xml → Needs personas to exist
ops_user_templates.xml → Needs personas + branches + BUs
```

**Solution**: Load in specific order

---

## ✅ WHAT'S CURRENTLY WORKING

### Files Still in Manifest (These Load Fine):

1. **Core Structure**:
   - `ir_module_category.xml` ✅
   - `res_groups.xml` ✅ (21 security groups)
   - `ir_sequence_data.xml` ✅
   - `ops_account_templates.xml` ✅ (simplified version)

2. **Security**:
   - `security/ir.model.access.csv` ✅
   - `security/ir_rule.xml` ✅

3. **All View Files** (69 files) ✅

4. **Cron Jobs**:
   - `ir_cron_data.xml` ✅
   - `ir_cron_archiver.xml` ✅
   - `ir_cron_escalation.xml` ✅

5. **Templates**:
   - `email_templates.xml` ✅
   - `ops_report_templates.xml` ✅
   - `ops_archive_templates.xml` ✅

---

## 🎯 COMPLETE INSTALLATION STRATEGY

### Phase 1: Install Modules (Creates Tables)

```bash
# This creates all database tables
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db \
  -i ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting,ops_matrix_asset_management \
  --stop-after-init
```

**Expected Result**: 50-70 OPS tables created

### Phase 2: Load Data in Correct Order

After modules install, load disabled data files via Python script (not XML):

**Correct Loading Order**:
1. SoD Rules (4 rules)
2. Field Visibility Rules (12 rules)
3. SLA Templates
4. Persona Templates (18 personas)
5. Governance Rule Templates (25 rules)
6. Product Templates
7. Default Data

### Phase 3: Seed Test Data

Create comprehensive test data for UAT

---

## 📦 COMPREHENSIVE SEED DATA SOLUTION

I'm creating a **single Python seeding script** that:
- ✅ Loads all disabled data files in correct order
- ✅ Creates comprehensive test data
- ✅ Handles dependencies properly
- ✅ Provides cleanup before seeding
- ✅ Includes verification steps

---

## 🗂️ WHAT NEEDS TO BE IN SEED DATA

### 1. Security Framework (Tier 1)

**Segregation of Duties** (4 rules):
- SO Create + Confirm (threshold: $5,000)
- PO Create + Confirm (threshold: $5,000)
- Invoice Create + Post (threshold: $0 - always)
- Payment Create + Post (threshold: $2,000)

**Field Visibility** (12 rules):
- Hide cost_price from Sales Reps
- Hide margin from Sales Reps
- Hide customer from Purchase Officers
- Hide sale_price from Purchase Officers
- Hide cost/value from Warehouse
- (7 more rules)

### 2. Organizational Structure

**Business Units** (2):
- Retail Division (RET)
- Wholesale Division (WHO)

**Branches** (2):
- Dubai Main Branch (DXB-01) → Business Unit: Retail
- Abu Dhabi Branch (AUH-01) → Business Unit: Wholesale

### 3. Master Data

**Customers** (3):
- Emirates Electronics LLC
  - Credit Limit: 50,000 AED
  - Payment Terms: Net 30
  - Branch: DXB-01
  
- Gulf Retail Trading
  - Credit Limit: 75,000 AED
  - Payment Terms: Net 45
  - Branch: DXB-01
  
- Abu Dhabi Wholesalers
  - Credit Limit: 100,000 AED
  - Payment Terms: Net 60
  - Branch: AUH-01

**Vendors** (2):
- Global Tech Supplies (China)
  - Payment Terms: Net 45
  - Products: Laptops, Monitors
  
- Regional Electronics Distributor (UAE)
  - Payment Terms: Net 30
  - Products: Accessories

**Products** (5):
- LAP-BUS-001: Business Laptop Pro
  - Sale Price: 3,500 AED
  - Cost: 2,100 AED
  - Margin: 40%
  
- MSE-WRL-001: Wireless Mouse
  - Sale Price: 85 AED
  - Cost: 45 AED
  - Margin: 47%
  
- CBL-USC-002: USB-C Cable 2m
  - Sale Price: 25 AED
  - Cost: 10 AED
  - Margin: 60%
  
- MON-27K-001: 27" 4K Monitor
  - Sale Price: 1,200 AED
  - Cost: 750 AED
  - Margin: 38%
  
- KBD-MEC-RGB: Mechanical Keyboard RGB
  - Sale Price: 350 AED
  - Cost: 180 AED
  - Margin: 49%

### 4. Test Transactions

**Sales Orders** (3):

1. **S00001** (Small Order - No Approval Needed)
   - Customer: Emirates Electronics
   - Products:
     - 2x Wireless Mouse @ 85 = 170
     - 3x USB-C Cable @ 25 = 75
   - Total: 245 AED
   - Status: Draft
   
2. **S00002** (Large Order - Requires Approval)
   - Customer: Gulf Retail Trading
   - Products:
     - 50x Business Laptop @ 3,500 = 175,000
     - 50x Wireless Mouse @ 85 = 4,250
     - 100x USB-C Cable @ 25 = 2,500
   - Total: 181,750 AED
   - Status: Requires Approval (>$5K triggers SoD)
   
3. **S00003** (Draft for Excel Import Testing)
   - Customer: Abu Dhabi Wholesalers
   - Products: None (empty for testing Excel import)
   - Total: 0 AED
   - Status: Draft

**Purchase Orders** (3):

1. **P00001** (Perfect Match Scenario)
   - Vendor: Global Tech Supplies
   - Products:
     - 100x Business Laptop @ 2,100 = 210,000
   - Total: 210,000 AED
   - Receipt: 100 units received
   - Vendor Bill: 210,000 AED
   - Three-Way Match: PERFECT MATCH ✅
   
2. **P00002** (Partial Receipt Scenario)
   - Vendor: Regional Electronics
   - Products:
     - 50x Monitor @ 750 = 37,500
   - Total: 37,500 AED
   - Receipt: 30 units received (partial)
   - Vendor Bill: Not yet created
   - Three-Way Match: PENDING (partial receipt)
   
3. **P00003** (Over-Billing Test)
   - Vendor: Global Tech Supplies
   - Products:
     - 100x Keyboard @ 180 = 18,000
   - Total: 18,000 AED
   - Receipt: 100 units received
   - Vendor Bill: 20,000 AED (OVER-BILLED!)
   - Three-Way Match: BLOCKED ❌

### 5. Personas (18 Templates)

All 18 persona templates should be loaded but **archived by default**:
- P00: System Admin
- P01: IT Admin (BLIND)
- P02: Executive/CEO
- P03: CFO/Owner
- P04: BU Leader
- P05: Branch Manager
- P06: Sales Manager
- P07: Purchase Manager
- P08: Inventory Manager
- P09: Finance Manager
- P10: Sales Representative
- P11: Purchase Officer
- P12: Warehouse Operator
- P13: AR Clerk
- P14: AP Clerk
- P15: Treasury Officer
- P16: Accountant/Controller
- P17: HR/Payroll Specialist

### 6. Test Users (4 Users for UAT)

1. **admin** (System Admin)
   - Groups: All OPS groups
   - Can see: Everything
   - Purpose: System configuration

2. **sales_rep** (Sales Representative)
   - Persona: P10
   - Groups: Sales User, OPS User
   - CANNOT SEE: cost_price, margin
   - Purpose: Test Field Visibility

3. **purchase_mgr** (Purchase Manager)
   - Persona: P07
   - Groups: Purchase Manager, OPS Manager
   - Can see: cost, purchase prices
   - Purpose: Test SoD, Three-Way Match

4. **finance_mgr** (Finance Manager)
   - Persona: P09
   - Groups: Finance Manager, OPS Manager
   - Can see: All financial data
   - Purpose: Test Financial Reports

---

## 📝 NEXT STEPS

1. **I will create** a comprehensive Python seeding script
2. **You will run** the script after module installation
3. **System will be** 100% ready for UAT testing

---

## ✅ SUCCESS CRITERIA

After running the seed script, you should have:

**Database Tables**: 50-70 OPS tables ✅  
**Security Rules**: 4 SoD + 12 Field Visibility ✅  
**Organizational**: 2 BUs + 2 Branches ✅  
**Master Data**: 3 Customers + 2 Vendors + 5 Products ✅  
**Transactions**: 3 SOs + 3 POs ✅  
**Personas**: 18 templates (archived) ✅  
**Test Users**: 4 users ready for UAT ✅  

**Total Records**: ~100 test records ready for comprehensive UAT

---

## 🎯 WHAT THIS ENABLES FOR UAT

With this seed data, you can test:

1. ✅ **Financial Reports Wizard** - Generate P&L, Balance Sheet with real data
2. ✅ **Three-Way Match** - Test perfect match, partial, and over-billing scenarios
3. ✅ **Segregation of Duties** - Try to create+confirm SO as same user (should block)
4. ✅ **Field Visibility** - Login as sales_rep, try to see cost_price (should be hidden)
5. ✅ **Approval Locking** - Confirm SO, try to edit (should lock)
6. ✅ **Excel Import** - Use S00003 to test bulk line import
7. ✅ **Branch Isolation** - Test that users only see their branch data
8. ✅ **Credit Limits** - Try to exceed customer credit limits
9. ✅ **Personas** - Assign personas to users and test access
10. ✅ **Auto-Escalation** - Let approval timeout and test escalation

---

**Ready to create the comprehensive seed script!** 🚀
