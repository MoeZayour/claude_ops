# OPS Matrix - Administrator Configuration Guide

**Version:** 1.0
**Last Updated:** 2026-01-18
**Target Audience:** IT Administrators, System Managers

---

## 1. Creating the Organizational Matrix

The OPS Framework relies on a strict hierarchy of Branches and Business Units (BUs). This structure forms the foundation for all data isolation, approval workflows, and governance rules.

### Step 1: Define Branches

Navigate to **Settings > OPS Configuration > Branches** (or **OPS Matrix > Branches**).

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Descriptive branch name | `Dubai Main Office` |
| **Code** | Unique identifier (3-5 chars) | `DXB`, `US-NY`, `UK-LON` |
| **Currency** | Functional currency for the branch | `AED`, `USD`, `GBP` |
| **Company** | Parent company (multi-company setups) | `Antigravity AI LLC` |
| **Active** | Enable/disable the branch | `True` |

**Best Practices:**
- Use ISO-style codes: `COUNTRY-CITY` (e.g., `US-NY`, `AE-DXB`)
- Set the functional currency to match local operations
- Always link a branch to exactly one company

### Step 2: Define Business Units

Navigate to **Settings > OPS Configuration > Business Units** (or **OPS Matrix > Business Units**).

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Business unit name | `Retail Division` |
| **Code** | Unique identifier | `RETAIL`, `GOV`, `B2B` |
| **Branches** | Where this BU operates (Many2many) | `DXB`, `AUH`, `US-NY` |
| **Leader** | BU Head (user reference) | `Sarah Chen` |

**Critical Rule:** A Business Unit MUST be linked to one or more Branches.

**Example Configuration:**
- `Retail` operates in: `US-NY`, `UK-LON`, `AE-DXB`
- `Government` operates in: `US-NY` only (restricted)
- `Wholesale` operates in: `AE-DXB`, `AE-AUH`

---

## 2. User Onboarding (The "Persona" Model)

**WARNING:** In the OPS Framework, you cannot create a standard internal user without completing the Matrix Access tab. The system enforces strict governance.

### Understanding the "OPS Matrix Access" Tab

When creating or editing a user, navigate to the **OPS Matrix Access** tab:

```
┌─────────────────────────────────────────────────────────────┐
│ OPS Matrix Access                                           │
├─────────────────────────────────────────────────────────────┤
│ OPS Personas:        [Sales Manager] [+]                    │
│ Primary Branch:      [Dubai Main Office ▼]                  │
│ Default Branch:      [Dubai Main Office ▼]                  │
│ Allowed Branches:    [Dubai] [Abu Dhabi] [+]                │
│ Allowed BUs:         [Retail] [Wholesale] [+]               │
│ Default BU:          [Retail ▼]                             │
│ ☐ Cross-Branch BU Leader                                    │
│ ☐ Matrix Administrator                                      │
└─────────────────────────────────────────────────────────────┘
```

### Field Definitions

| Field | Purpose | Required? |
|-------|---------|-----------|
| **OPS Personas** | Role(s) assigned to user. Determines authorities (can_validate_invoices, etc.) | **YES** |
| **Primary Branch** | User's "Home" location. Appears on their profile. | **YES** |
| **Default Branch** | Pre-selected branch for new transactions | No (auto-set to Primary if empty) |
| **Allowed Branches** | ALL branches the user can see/transact in | **YES** (at least 1) |
| **Allowed BUs** | Business lines the user can access | **YES** (at least 1) |
| **Default BU** | Pre-selected BU for new transactions | No |
| **Cross-Branch BU Leader** | Can see BU data across ALL branches | No (checkbox) |
| **Matrix Administrator** | Can configure matrix structure | No (checkbox) |

### User Creation Workflow

1. Go to **Settings > Users & Companies > Users**
2. Click **Create**
3. Fill in basic info: Name, Email, Login
4. Navigate to **OPS Matrix Access** tab
5. **Select Persona FIRST** - the system will auto-populate branches/BUs
6. Verify/adjust:
   - Primary Branch (required)
   - Allowed Branches (at least one)
   - Allowed Business Units (at least one)
7. **Save** the user

**Tip:** Assigning a Persona first triggers auto-population logic that sets sensible defaults.

### Validation Errors

If you see this error when saving a user:

```
User 'John Doe' cannot be saved due to missing OPS Matrix requirements:

• OPS Persona: At least one persona must be assigned.
• Primary Branch: A primary branch must be assigned.
• Business Units: At least one business unit must be assigned.

Please go to the 'OPS Matrix Access' tab and complete the required fields.
```

**Solution:** Complete all three required fields in the OPS Matrix Access tab.

---

## 3. Primary Branch vs Allowed Branches

This is a common point of confusion. Here's the difference:

| Concept | Primary Branch | Allowed Branches |
|---------|----------------|------------------|
| **Purpose** | User's "Home" location | Data visibility scope |
| **Cardinality** | Exactly ONE | One or MORE |
| **Usage** | Profile display, defaults | Record-level security rules |
| **Required** | Yes | Yes (at least 1) |

### Practical Example

**Scenario:** Sarah is a Regional Sales Manager overseeing Dubai and Abu Dhabi.

```
Primary Branch:    Dubai Main Office (her desk is here)
Allowed Branches:  Dubai Main Office, Abu Dhabi Branch
Allowed BUs:       Retail, Wholesale
```

**Result:**
- Sarah's profile shows "Dubai Main Office"
- New sales orders default to Dubai
- Sarah can VIEW and CREATE records in both Dubai and Abu Dhabi
- Sarah can only access Retail and Wholesale data (not Government BU)

---

## 4. Troubleshooting "Blind Admin" Issues

### Symptom
Administrator or Manager user logs in but sees NO records (empty lists, blank dashboards).

### Root Cause
The admin user lacks proper Matrix Access configuration. Odoo's record rules filter data based on `user.ops_allowed_branch_ids`.

### Diagnosis

1. **Check User's Matrix Access:**
   ```
   Go to: Settings > Users > [Admin User] > OPS Matrix Access tab
   ```

   Verify:
   - ☑ At least one Persona assigned
   - ☑ Primary Branch is set
   - ☑ Allowed Branches contains entries
   - ☑ Allowed BUs contains entries

2. **Check Security Groups:**

   The admin user should have one of these groups:
   - `base.group_system` (Settings/Administrator) - bypasses all rules
   - `ops_matrix_core.group_ops_matrix_administrator` - Matrix Admin

3. **Check Record Rules:**
   ```
   Go to: Settings > Technical > Security > Record Rules
   Search for: ops_matrix
   ```

   Look for rules like:
   - `ops_matrix_core.rule_branch_isolation`
   - `ops_matrix_core.rule_ops_user_branch`

### Quick Fix: Grant Full Access

For a true system administrator who should see EVERYTHING:

**Option A: Add to Settings Group**
```
User > Access Rights tab > Check "Administration: Settings"
```
This bypasses all record rules (use sparingly).

**Option B: Assign All Branches/BUs**
```
OPS Matrix Access tab:
  Allowed Branches: [Select ALL branches]
  Allowed BUs: [Select ALL business units]
  ☑ Matrix Administrator checkbox
```

### Shell Diagnosis

```bash
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
# Check user's matrix access
user = self.env['res.users'].browse(2)  # Admin user ID
print(f"User: {user.name}")
print(f"Personas: {user.ops_persona_ids.mapped('name')}")
print(f"Primary Branch: {user.primary_branch_id.name}")
print(f"Allowed Branches: {user.ops_allowed_branch_ids.mapped('name')}")
print(f"Allowed BUs: {user.ops_allowed_business_unit_ids.mapped('name')}")
print(f"Is System Admin: {user.has_group('base.group_system')}")
PYTHON
```

---

## 5. Security Record Rules

The OPS Framework uses Odoo's record rules to enforce data isolation:

| Rule | Model | Effect |
|------|-------|--------|
| `rule_branch_user` | `ops.branch` | Users see only allowed branches |
| `rule_sale_order_branch` | `sale.order` | Sales orders filtered by branch |
| `rule_invoice_branch` | `account.move` | Invoices filtered by branch |
| `rule_stock_move_branch` | `stock.move` | Inventory moves filtered by branch |

### How Rules Work

```python
# Example rule domain (from ir_rule.xml)
[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]
```

**Translation:** "Show this record only if its branch is in the user's allowed branches list."

### Bypassing Rules (Emergency Only)

For system administrators, the `base.group_system` group bypasses ALL record rules.

```python
# Programmatically (in code)
self.env['sale.order'].sudo().search([])  # sudo() bypasses rules
```

---

## 6. Common Configuration Scenarios

### Scenario 1: Single-Branch User (Sales Rep)
```
Persona:           Sales Representative
Primary Branch:    Dubai
Allowed Branches:  Dubai (only)
Allowed BUs:       Retail
```

### Scenario 2: Multi-Branch Manager
```
Persona:           Sales Manager
Primary Branch:    Dubai
Allowed Branches:  Dubai, Abu Dhabi, Sharjah
Allowed BUs:       Retail, Wholesale
☑ Cross-Branch BU Leader
```

### Scenario 3: Regional Executive
```
Personas:          CFO, Executive
Primary Branch:    HQ
Allowed Branches:  ALL branches
Allowed BUs:       ALL business units
☑ Matrix Administrator
```

### Scenario 4: IT Administrator
```
Persona:           System Admin
Primary Branch:    HQ
Allowed Branches:  ALL branches
Allowed BUs:       ALL business units
☑ Matrix Administrator
+ Access Rights: Administration: Settings
```

---

## 7. Audit and Compliance

### Tracking Matrix Changes

All changes to user matrix access are logged:
1. Audit trail on partner record (message history)
2. Python logging for security events
3. Odoo chatter messages

### Reviewing User Access

```bash
# Generate user access report
docker exec gemini_odoo19 odoo shell -c /etc/odoo/odoo.conf -d mz-db --no-http << 'PYTHON'
users = self.env['res.users'].search([('share', '=', False)])
for u in users:
    branches = u.ops_allowed_branch_ids.mapped('code')
    bus = u.ops_allowed_business_unit_ids.mapped('code')
    print(f"{u.name}: Branches={branches}, BUs={bus}")
PYTHON
```

---

## 8. Quick Reference

### Required Fields for New Users
- [x] Name
- [x] Email/Login
- [x] OPS Persona (at least one)
- [x] Primary Branch
- [x] Allowed Branches (at least one)
- [x] Allowed Business Units (at least one)

### Admin Checklist
- [ ] Branches created with proper codes
- [ ] Business Units linked to branches
- [ ] Personas defined with authorities
- [ ] Users have complete Matrix Access configuration
- [ ] Administrators have full branch/BU access
- [ ] Record rules are active

### Emergency Contacts
- System Administrator: Check `base.group_system` membership
- Matrix Configuration: `Settings > OPS Configuration`
- Record Rules: `Settings > Technical > Security > Record Rules`

---

**Document Version:** 1.0
**Applies to:** OPS Framework v1.3.0+, Odoo 19.0
