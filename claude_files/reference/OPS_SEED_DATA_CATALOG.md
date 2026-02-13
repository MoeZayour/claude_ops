# OPS Seed Data Catalog

> Auto-loaded on every module install. Survives container wipes and volume resets.

---

## Loading Architecture

```
Module Install / Update
        │
        ▼
__manifest__.py 'data' section
        │  (XML files with noupdate="1")
        │
        ├── ops_seed_structure.xml    ← Companies, Branches, BUs
        ├── ops_seed_products.xml     ← Categories + 50 products
        ├── ops_seed_partners.xml     ← 20 customers + 15 vendors
        ├── ops_seed_users.xml        ← 36 users (18 personas × 2)
        ├── ops_seed_governance.xml   ← Approval rules, SLA, archive
        └── ops_seed_fiscal.xml       ← 12 monthly fiscal periods
                │
                ▼
        post_init_hook (runs ONCE on install)
                │
                ├── _auto_configure_matrix()
                ├── _ensure_generic_coa()
                ├── _set_not_null_constraints()
                ├── _setup_analytic_structure()
                └── seed_transactions()  ← SOs, POs, invoices, PDC, budgets
                    (idempotent via ir.config_parameter sentinel)
```

**Key guarantee:** XML data files with `noupdate="1"` are loaded on **every fresh install** but never overwritten on module upgrade. The Python `seed_transactions()` function uses an `ir.config_parameter` sentinel (`ops_seed_transactions_loaded`) to ensure it runs only once.

---

## File Inventory

### ops_matrix_core

| File | Records | Model(s) | Load Order |
|------|---------|----------|------------|
| `data/ops_seed_structure.xml` | 14 | res.company (1), ops.branch (5), ops.business.unit (8) | Before default data |
| `data/ops_seed_products.xml` | 58 | product.category (8), product.template (50) | After product_rules |
| `data/ops_seed_partners.xml` | 35 | res.partner (35: 20 cust, 15 vendor, 3 dual) | After default data |
| `data/ops_seed_users.xml` | 36 | res.users (36: 18 personas × 2 branches) | After partners |
| `data/ops_seed_governance.xml` | 17 | ops.approval.rule (6), ops.sla.template (4), ops.archive.policy (3), ops.dashboard.widget (4) | After users |
| `data/ops_seed_transactions.py` | — | Python (called from post_init_hook) | Post-install |

### ops_matrix_accounting

| File | Records | Model(s) | Load Order |
|------|---------|----------|------------|
| `data/ops_seed_fiscal.xml` | 12 | ops.fiscal.period (12 monthly) | After SoD bank rules |

---

## Detailed Record Counts

### Structure (14 records)

| Entity | Count | Details |
|--------|-------|---------|
| Companies | 1 | OPS International LLC (2nd company) |
| Branches | 5 | HQ (Abu Dhabi), Dubai, Abu Dhabi, Riyadh, Doha |
| Business Units | 8 | Trading, Contracting, Building Materials, HVAC, MEP, Interiors, IT Solutions, E-Commerce |

### Products (58 records)

| Entity | Count | Details |
|--------|-------|---------|
| Product Categories | 8 | Building Materials, HVAC, Electrical, MEP, Safety, Tools, Office, IT |
| Products | 50 | 13 consumable, 32 storable, 5 service |

Price range: $5.25 – $500,000. Margin range: 25%–35%.

### Partners (35 records)

| Entity | Count | Details |
|--------|-------|---------|
| Customers | 20 | GCC-based (UAE, KSA, Qatar, Kuwait, Oman, Bahrain) |
| Vendors | 15 | International suppliers + GCC local |
| Dual-role | 3 | Both customer_rank and supplier_rank > 0 |

### Users (36 records)

All 18 personas covered with 2 users each (one at HQ, one at branch):

| # | Persona Code | HQ User | Branch User | Branch |
|---|-------------|---------|-------------|--------|
| 1 | CEO | Ahmad Al Mansouri | Nasser Al Thani | Doha |
| 2 | CFO | Fatima Al Hashimi | Omar Al Ghamdi | Riyadh |
| 3 | FIN_CTRL | Khalid Al Mazrouei | Maryam Al Suwaidi | Dubai |
| 4 | SALES_LEADER | Mohammed Al Farsi | Huda Al Balushi | Dubai |
| 5 | SALES_MGR | Youssef Al Khatib | Layla Al Rashid | Abu Dhabi |
| 6 | PURCHASE_MGR | Ali Al Mulla | Noura Al Shamsi | Dubai |
| 7 | LOG_MGR | Hassan Al Jaber | Amira Al Dosari | Riyadh |
| 8 | TREASURY_OFF | Saeed Al Nuaimi | Dalal Al Hajri | Dubai |
| 9 | HR_MGR | Rashed Al Kaabi | Salma Al Ketbi | Abu Dhabi |
| 10 | CHIEF_ACCT | Ibrahim Al Wahaibi | Aisha Al Marzouqi | Dubai |
| 11 | SYS_ADMIN | Tariq Al Hamadi | Reem Al Falasi | Dubai |
| 12 | SALES_REP | Khaled Al Zaabi | Sara Al Dhaheri | Dubai |
| 13 | PURCHASE_OFF | Majed Al Naqbi | Hessa Al Qassimi | Abu Dhabi |
| 14 | LOG_CLERK | Faisal Al Marri | Shamma Al Blooshi | Riyadh |
| 15 | ACCOUNTANT | Abdulla Al Hosani | Moza Al Rumaithi | Dubai |
| 16 | AR_CLERK | Sultan Al Mheiri | Latifa Al Ameri | Doha |
| 17 | AP_CLERK | Hamdan Al Tayer | Maitha Al Maktoum | Abu Dhabi |
| 18 | TECH_SUPPORT | Younus Al Qubaisi | Sheikha Al Nahyan | Riyadh |

**Login pattern:** `persona.branch@ops-demo.com` (e.g., `ceo.hq@ops-demo.com`)
**Password:** `Demo@2026` (all users)

**Branch access tiers:**
- Executives (CEO, CFO, FIN_CTRL): All 5 branches, all 8 BUs
- Directors (SALES_LEADER): 3–4 branches, 3 BUs
- Managers: 1–2 branches, 2 BUs
- Clerks/Users: 1 branch, 1 BU
- System (SYS_ADMIN, TECH_SUPPORT): All 5 branches, all 8 BUs (IT Admin blinded)

### Governance (17 records)

| Entity | Count | Details |
|--------|-------|---------|
| Approval Rules | 6 | SO >50k, PO >25k, Payment >10k, SO >100k (2-level), PO >75k (2-level), Invoice >50k |
| SLA Templates | 4 | SO Processing (48h), PO Approval (24h), Invoice Processing (72h), Customer Complaint (24h) |
| Archive Policies | 3 | Sale Orders >1yr, Purchase Orders >1yr, Invoices >2yr |
| Dashboard Widgets | 4 | Pending Approvals, SLA Compliance, Budget Utilization, Revenue Trend |

### Fiscal Periods (12 records)

| Period | State | Notes |
|--------|-------|-------|
| January 2026 | hard_lock | Locked for testing period-lock enforcement |
| February–December 2026 | open | Available for transactions |

### Transactional (Python seed — post_init_hook)

| Entity | Target Count | Details |
|--------|-------------|---------|
| Sale Orders | 30 | 20 confirmed, 10 draft; multi-branch |
| Purchase Orders | 25 | 15 confirmed, 10 draft; multi-branch |
| Customer Invoices | 25 | 15 posted, 10 draft |
| Vendor Bills | 15 | 8 posted, 7 draft |
| Budgets | 5 | 1 per branch, with budget lines per expense account |
| PDC Receivable | 10 | Mix: draft, deposited, cleared, bounced, cancelled |
| PDC Payable | 8 | Mix: draft, issued, cleared, bounced, cancelled |

---

## Testing Scenarios Enabled

### 1. Branch Isolation
- Users at different branches see only their branch's data
- Cross-branch users (executives) see all data

### 2. IT Admin Blindness
- TECH_SUPPORT users (group_ops_it_admin) cannot see business transactions
- 25 record rules enforce blindness across 24 models

### 3. Persona-Based Access
- Each persona gets specific Odoo security groups via explicit group_ids
- No reliance on onchange (which doesn't fire during XML data load)

### 4. Budget Control
- 5 budgets with lines enable budget availability checks on POs
- Over-budget scenarios testable by creating POs exceeding planned amounts

### 5. PDC Lifecycle
- Records in every PDC state enable testing of state transitions
- Receivable: draft → deposited → cleared/bounced
- Payable: draft → issued → cleared/bounced

### 6. Fiscal Period Locking
- January hard-locked: posting invoices to Jan should fail
- Other months open: normal transaction flow

### 7. Approval Workflows
- 6 rules with different thresholds enable multi-level approval testing
- SO >$50k triggers 1-level, SO >$100k triggers 2-level

### 8. SLA Tracking
- 4 SLA templates with different deadlines
- SLA instances auto-created when matching documents are created

---

## Validation

Run the validation script after install:

```bash
docker exec gemini_odoo19 odoo shell -d mz-db < seed/validate_seed_coverage.py
docker exec gemini_odoo19 cat /tmp/seed_validation.json
```

Expected output: All checks PASS, 0 failures.

---

## XML ID Prefix Convention

All seed data uses the `seed_` prefix for easy identification:

- `seed_company_*` — Companies
- `seed_branch_*` — Branches
- `seed_bu_*` — Business Units
- `seed_partner_*` — Partners (customers/vendors)
- `seed_categ_*` — Product categories
- `seed_product_*` — Products
- `seed_user_*` — Users
- `seed_approval_*` — Approval rules
- `seed_sla_*` — SLA templates
- `seed_archive_*` — Archive policies
- `seed_widget_*` — Dashboard widgets
- `seed_fiscal_*` — Fiscal periods

Total XML IDs: **172 records** across 6 files.

---

*Generated: 2026-02-13 | OPS Framework v19.0*
