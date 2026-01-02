# Data Factory Script - Setup & Execution Report

## 📋 Overview

Created a comprehensive data factory script [`utils/generate_demo_company.py`](utils/generate_demo_company.py) that populates the `mz-db` database with high-volume demo data covering ALL OPS Framework scenarios for General Manager demonstrations.

## ✅ Script Capabilities

### Phase 0: Module Installation
- Auto-detects and installs required Odoo modules
- OPS Framework modules: `ops_matrix_core`, `ops_matrix_accounting`, `ops_matrix_reporting`
- Standard modules: `product`, `sale_management`, `purchase`, `stock`, `account`, `contacts`

### Phase 1: Branch Hierarchy
- Creates multi-level branch structure:
  - **Main Branch** (root)
  - **North Region** (child)
  - **South Region** (child)

### Phase 2: User Personas
- Creates 5 role-based users (Password: `123` for all):
  - `user_sales` - Sales Manager
  - `user_logistics` - Warehouse Manager
  - `user_accountant` - Senior Accountant
  - `user_purchaser` - Purchasing Officer
  - `user_approver` - Operations Approver
- Creates corresponding OPS Personas for each user

### Phase 3: Master Products
- 7 diverse products covering all scenarios:
  - **Laptop Pro X1** ($2,500) - Stockable, high-value IT equipment
  - **Wireless Mouse** ($25) - Consumable peripheral
  - **IT Support Contract** ($1,200) - Service product
  - **Office Desk Premium** ($650) - Furniture inventory
  - **Consulting Hour** ($150) - Professional services
  - **Network Router** ($450) - Network equipment
  - **Software License** ($300) - Software service

### Phase 4: Business Partners
- **3 Vendors** across different branches:
  - Tech Supplies Global (Main)
  - Office Furniture Direct (North)
  - IT Equipment Corp (South)
- **5 Customers** with varied profiles:
  - Acme Corporation Ltd (Main, Company)
  - Global Industries Inc (North, Company)
  - Tech Innovators LLC (South, Person)
  - Enterprise Solutions Co (Main, Company)
  - Digital Services Group (North, Person)

### Phase 5: Purchase-to-Pay Cycle
- **PO #1**: 50 Laptops - Fully received & billed ($75,000 expense)
- **PO #2**: 25 Office Desks - Partial receipt (15 received, 10 backorder)
- Demonstrates:
  - Full procurement cycle
  - Partial receipts with backorders
  - Stock valuation scenarios
  - Vendor bill processing

### Phase 6: Order-to-Cash Cycle
- **15 Sales Orders** with varied scenarios:
  - 12 fully delivered and invoiced
  - 7 with payments received (demonstrates cash flow)
  - 5 unpaid invoices (for Aged Receivables report)
  - 3 pending deliveries (for logistics dashboard)
- Revenue generation: $50,000+ across multiple products
- Demonstrates:
  - Complete sales cycle
  - Payment processing
  - Partial delivery scenarios
  - Accounts receivable management

### Phase 7: Financial Padding
- **Journal Entries**:
  - Office Rent: $5,000
  - Utilities & Internet: $1,200
  - Office Supplies: $800
- **Vendor Bills**:
  - Electricity: $950
  - Maintenance Services: $1,500
- Total Operating Expenses: $9,450
- **Purpose**: Ensures realistic P&L with operating expenses

## 📊 Expected Results

### Financial Reports Ready
- **Profit & Loss**: ~$50k Revenue vs ~$85k Expenses (including COGS)
- **Balance Sheet**: Assets (inventory), Liabilities, Equity
- **Aged Receivables**: 5+ unpaid invoices across customers
- **Cash Flow**: Payment transactions recorded

### Logistics Reports Ready
- **Stock Valuation**: Laptops, Desks, Routers in inventory
- **Stock Moves**: 65+ movements (receipts + deliveries)
- **Backorders**: 10 Office Desks pending
- **Pending Deliveries**: 3 Sales Orders awaiting shipment

### OPS Framework Coverage
✅ **Branch Hierarchy**: Multi-level structure (Main → North/South)  
✅ **User Personas**: 5 role-based users with OPS personas  
✅ **Product Management**: 7 products (stockable, consumable, service)  
✅ **Partner Management**: Vendors & customers by branch  
✅ **Purchase-to-Pay**: Full cycle with partial receipts  
✅ **Order-to-Cash**: Full cycle with pending items  
✅ **Financial Accounting**: P&L ready with complete transactions  
✅ **Inventory Management**: Stock moves, valuations, backorders  
✅ **Approval Workflows**: User setup for approval scenarios  
✅ **Multi-Branch Operations**: Data distributed across branches  

## 🚨 Current Status: Database Initialization Required

### Issue Encountered
The `mz-db` database is **not initialized** with base Odoo modules. The script requires:
1. Base Odoo installation
2. Standard modules: product, sale, purchase, stock, account
3. OPS Framework modules installed

### Error Messages
```
- "Object product.product doesn't exist"
- "Object ops.branch doesn't exist"  
- "Invalid field 'supplier_rank' in 'res.partner'"
```

These indicate the database needs to be properly initialized through the Odoo web interface first.

## 📝 Required Steps to Complete

### Step 1: Initialize Database via Web Interface
```bash
# Access Odoo web interface
http://localhost:8089

# Create/Initialize database 'mz-db':
- Database name: mz-db
- Email: admin@example.com
- Password: admin
- Language: English
- Country: United States (or appropriate)
- Demo data: No
```

### Step 2: Install Required Modules
Via Odoo Web Interface → Apps:
1. Update Apps List
2. Install in order:
   - **Contacts** (base partner management)
   - **Sales** (sales_management)
   - **Purchase** (purchase)
   - **Inventory** (stock)
   - **Accounting** (account)
   - **OPS Matrix Core** (ops_matrix_core)
   - **OPS Matrix Accounting** (ops_matrix_accounting)
   - **OPS Matrix Reporting** (ops_matrix_reporting)

### Step 3: Run Data Factory Script
```bash
python3 utils/generate_demo_company.py
```

### Alternative: Command Line Installation
```bash
# Stop the running Odoo instance first
docker stop gemini_odoo19

# Initialize database with modules
docker run --rm -it \
  --network=gemini_odoo19_default \
  -v $(pwd)/addons:/mnt/extra-addons \
  -v $(pwd)/config:/etc/odoo \
  odoo:19.0 \
  odoo -d mz-db \
  --db_host=gemini_odoo19_db \
  --db_user=odoo \
  --db_password=odoo \
  --init=base,web,product,sale_management,purchase,stock,account,contacts,ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting \
  --stop-after-init \
  --without-demo=True

# Restart the service
docker start gemini_odoo19

# Wait for startup (30 seconds)
sleep 30

# Run data factory
python3 utils/generate_demo_company.py
```

## 🎯 Script Features

### XML-RPC Based
- Persistent data (survives server restarts)
- Professional approach vs direct database manipulation
- Can be run as admin creating records on behalf of personas

### Error Handling
- Graceful degradation if OPS modules not available
- Automatic retry logic for module installation
- Detailed error reporting with truncated messages
- Continues execution even if some phases fail

### Progress Reporting
- Real-time phase progress with emoji indicators
- Detailed logging of each creation step
- Comprehensive final summary with statistics
- User credentials and login information

### Statistics Tracked
- Infrastructure: branches, users, personas
- Master data: products, partners
- Transactions: POs, SOs, invoices, payments
- Financial: revenue, expenses, net income
- Logistics: stock moves, backorders

## 📖 Usage After Initialization

```bash
# Run the data factory
python3 utils/generate_demo_company.py

# Expected output:
# ✅ 3 Branches created
# ✅ 5 Users created with passwords
# ✅ 7 Products created
# ✅ 8 Partners created
# ✅ 2 Purchase orders processed
# ✅ 15 Sales orders with varied scenarios
# ✅ Financial entries for realistic P&L

# Login credentials (all passwords: 123):
- admin / admin (System Administrator)
- user_accountant / 123 (View Financial Reports)
- user_sales / 123 (Sales Dashboard)
- user_logistics / 123 (Warehouse Operations)
- user_purchaser / 123 (Purchase Management)
- user_approver / 123 (Approval Workflows)
```

## 🎬 Demonstration Scenarios

Once executed, the GM can demonstrate:

1. **Financial Health**: 
   - P&L showing revenue vs expenses
   - Balance sheet with assets and liabilities
   - Aged receivables with unpaid invoices

2. **Sales Performance**:
   - 15 orders across 5 customers
   - $50k+ in revenue
   - Pipeline with pending deliveries

3. **Procurement Efficiency**:
   - Active purchase orders
   - Partial receipts management
   - Vendor performance tracking

4. **Inventory Management**:
   - Real-time stock levels
   - Stock valuation reports
   - Backorder management

5. **Multi-Branch Operations**:
   - Branch-specific data
   - Cross-branch visibility
   - Hierarchical reporting

6. **Role-Based Access**:
   - Different dashboards per user
   - Permission-based visibility
   - Workflow assignments

## 📁 Files Created

- **[`utils/generate_demo_company.py`](utils/generate_demo_company.py)**: Main data factory script (660 lines)
- **[`DATA_FACTORY_SETUP_REPORT.md`](DATA_FACTORY_SETUP_REPORT.md)**: This documentation

## ✨ Next Steps

1. ✅ Script created and ready
2. ⏳ Initialize mz-db database via web interface
3. ⏳ Install required modules
4. ⏳ Execute data factory script
5. ⏳ Verify all reports and dashboards
6. ⏳ Present to General Manager

## 🔗 Connection Details

- **URL**: http://localhost:8089
- **Database**: mz-db
- **Admin User**: admin
- **Admin Password**: admin
- **XML-RPC Endpoint**: http://localhost:8089/xmlrpc/2/

---

**Status**: Script ready, awaiting database initialization to proceed with data population.
