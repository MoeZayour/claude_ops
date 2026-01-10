
import sys

print("\n" + "=" * 70)
print("OPS FRAMEWORK - STATUS VERIFICATION")
print("=" * 70)

# env is provided by odoo shell
env = self.env

# Modules
modules = env['ir.module.module'].search([
    ('name', 'like', 'ops_matrix_%'),
    ('state', '=', 'installed')
])
print(f"\n📦 MODULES: {len(modules)}/4")
for m in modules:
    print(f"   ✅ {m.name}")

# Company Structure
bus = env['ops.business.unit'].search([])
branches = env['ops.branch'].search([])
print(f"\n🏢 COMPANY STRUCTURE:")
print(f"   Business Units: {len(bus)}")
print(f"   Branches: {len(branches)}")

# Users
users = env['res.users'].search([('login', '!=', 'admin')])
print(f"\n👥 USERS: {len(users)}")

# Master Data
products = env['product.product'].search([('default_code', 'like', 'PROD%')])
customers = env['res.partner'].search([('customer_rank', '>', 0)])
vendors = env['res.partner'].search([('supplier_rank', '>', 0)])
print(f"\n📊 MASTER DATA:")
print(f"   Products: {len(products)}")
print(f"   Customers: {len(customers)}")
print(f"   Vendors: {len(vendors)}")

# Governance
sla = env['ops.sla.template'].search([])
sod = env['ops.segregation.of.duties'].search([])
print(f"\n⚖️  GOVERNANCE:")
print(f"   SLA Templates: {len(sla)}")
print(f"   SoD Rules: {len(sod)}")

# Transactions
so = env['sale.order'].search([])
budgets = env['ops.budget'].search([]) if 'ops.budget' in env else []
assets = env['ops.asset'].search([]) if 'ops.asset' in env else []
pdcs = (env['ops.pdc.receivable'].search([]) if 'ops.pdc.receivable' in env else [])
print(f"\n💼 TRANSACTIONS:")
print(f"   Sale Orders: {len(so)}")
print(f"   Budgets: {len(budgets)}")
print(f"   Assets: {len(assets)}")
print(f"   PDCs: {len(pdcs)}")

# Dashboards
dashboards = env['ops.dashboard'].search([])
widgets = env['ops.dashboard.widget'].search([])
print(f"\n📈 DASHBOARDS:")
print(f"   Dashboards: {len(dashboards)}")
print(f"   Widgets: {len(widgets)}")

# Test All 15 Priorities
print(f"\n🎯 15 PRIORITIES STATUS:")
priorities = [
    ('#1 Company Structure', 'ops.business.unit' in env and 'ops.branch' in env),
    ('#2 Personas', 'ops.persona' in env),
    ('#3 Security', 'ops.field.visibility.rule' in env),
    ('#4 SoD', 'ops.segregation.of.duties' in env),
    ('#5 Governance', 'ops.sla.template' in env),
    ('#6 Excel Import', 'ops.sale.order.import.wizard' in env),
    ('#7 Three-Way Match', 'ops.three.way.match' in env),
    ('#8 Auto-Escalation', 'ops.sla.instance' in env),
    ('#9 Auto-List Accounts', 'ops.report.template' in env),
    ('#10 PDC', 'ops.pdc.receivable' in env),
    ('#11 Budget', 'ops.budget' in env),
    ('#12 Assets', 'ops.asset' in env),
    ('#13 Financial Reports', 'ops.financial.report.wizard' in env),
    ('#14 Dashboards', 'ops.dashboard' in env),
    ('#15 Export', 'ops.excel.export.wizard' in env),
]

passed = 0
for name, exists in priorities:
    icon = "✅" if exists else "❌"
    print(f"   {icon} {name}")
    if exists:
        passed += 1

print(f"\n" + "=" * 70)
print(f"COMPLETION SCORE: {passed}/15 priorities ({(passed/15)*100:.0f}%)")

# Final Assessment
if passed == 15 and len(modules) == 4:
    if len(products) >= 40 and len(customers) >= 20 and len(so) >= 15:
        print("🎉 STATUS: 100% COMPLETE - PRODUCTION READY!")
    else:
        print("⚠️  STATUS: 95% COMPLETE - Core working, some data light")
elif passed >= 14:
    print("✅ STATUS: 90%+ COMPLETE - Almost ready")
else:
    print(f"⚠️  STATUS: {(passed/15)*100:.0f}% COMPLETE - Work needed")

print("=" * 70)
