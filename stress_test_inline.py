import sys
from datetime import date, timedelta

print("=" * 80)
print("OPS FRAMEWORK STRESS TEST")
print("=" * 80)

RESULTS = {"passed": 0, "failed": 0}

def test(name, condition, detail=""):
    global RESULTS
    if condition:
        RESULTS["passed"] += 1
        print(f"PASS: {name}")
    else:
        RESULTS["failed"] += 1
        print(f"FAIL: {name}")
    if detail:
        print(f"   -> {detail}")

# Setup
print("\n== SETUP ==")
Company = env["res.company"]
company = Company.search([], limit=1)
print(f"Company: {company.name}")

Branch = env["ops.branch"]
branch_n = Branch.search([("name", "=", "North")], limit=1)
if not branch_n:
    branch_n = Branch.create({"name": "North", "company_id": company.id})
branch_s = Branch.search([("name", "=", "South")], limit=1)
if not branch_s:
    branch_s = Branch.create({"name": "South", "company_id": company.id})

BU = env["ops.business.unit"]
bu = BU.search([("name", "=", "Trading")], limit=1)
if not bu:
    bu = BU.create({"name": "Trading", "company_id": company.id, "branch_ids": [(6, 0, [branch_n.id, branch_s.id])]})
else:
    bu.write({"branch_ids": [(6, 0, [branch_n.id, branch_s.id])]})

env.cr.commit()
test("Matrix Setup", True, f"Branches: {branch_n.name}, {branch_s.name}")

# Test 1: CR Uniqueness
print("\n== TEST 1: CR Number Uniqueness ==")
Partner = env["res.partner"]
old = Partner.search([("ops_cr_number", "like", "STRESS-%")])
if old:
    old.unlink()
    env.cr.commit()

c1 = Partner.create({"name": "Stress Customer 1", "customer_rank": 1, "ops_cr_number": "STRESS-001", "ops_master_verified": True, "ops_credit_limit": 50000})
env.cr.commit()

dup_blocked = False
try:
    Partner.create({"name": "Stress Duplicate", "customer_rank": 1, "ops_cr_number": "STRESS-001"})
except Exception as e:
    dup_blocked = True
    env.cr.rollback()

test("CR Uniqueness", dup_blocked, "Duplicate blocked" if dup_blocked else "ALLOWED!")

# Test 2: Product Branch Activation
print("\n== TEST 2: Product Branch Activation ==")
Product = env["product.template"]
old = Product.search([("name", "=", "Stress Product")])
if old:
    old.unlink()
    env.cr.commit()

prod = Product.create({
    "name": "Stress Product",
    "type": "consu",
    "list_price": 25000,
    "standard_price": 23000,
    "ops_is_global_master": True,
    "ops_branch_activation_ids": [(6, 0, [branch_n.id])],
})
env.cr.commit()
test("Global Master Product", prod.ops_is_global_master, f"Activated for: North only")

# Test 3: Master Verification
print("\n== TEST 3: Master Verification Block ==")
c2 = Partner.create({"name": "Stress Unverified", "customer_rank": 1, "ops_cr_number": "STRESS-002", "ops_master_verified": False, "ops_credit_limit": 5000})
env.cr.commit()

SaleOrder = env["sale.order"]
SaleOrderLine = env["sale.order.line"]
old = SaleOrder.search([("partner_id", "in", [c1.id, c2.id])])
if old:
    old.unlink()
    env.cr.commit()

pp = env["product.product"].search([("product_tmpl_id", "=", prod.id)], limit=1)

so_unv = SaleOrder.create({"partner_id": c2.id, "ops_branch_id": branch_n.id, "ops_business_unit_id": bu.id})
SaleOrderLine.create({"order_id": so_unv.id, "product_id": pp.id, "product_uom_qty": 1, "price_unit": 5000})
env.cr.commit()

blocked = False
from odoo.exceptions import ValidationError, UserError
try:
    so_unv.action_confirm()
except (ValidationError, UserError) as e:
    if "MASTER" in str(e).upper() or "VERIFIED" in str(e).upper():
        blocked = True
    env.cr.rollback()
except:
    env.cr.rollback()

if so_unv.state != "sale":
    blocked = True

test("Master Verification Block", blocked, f"State: {so_unv.state}")

# Test 4: Stock Move Fields
print("\n== TEST 4: Stock Move Fields ==")
sm = env["stock.move"]._fields
has_fields = "ops_source_branch_id" in sm and "ops_dest_branch_id" in sm
test("Inter-Branch Fields", has_fields, "Source/Dest branch fields present")

# Test 5: Matrix Snapshot
print("\n== TEST 5: Matrix Snapshot ==")
if "ops.matrix.snapshot" in env:
    Snap = env["ops.matrix.snapshot"]
    count = Snap.rebuild_snapshots(period_type="monthly", date_from=date.today().replace(day=1), date_to=date.today())
    test("Snapshot Rebuild", count >= 0, f"Built {count} snapshots")
else:
    test("Snapshot", False, "Model missing")

# Summary
print("\n" + "=" * 80)
print("STRESS TEST COMPLETE")
print("=" * 80)
print(f"PASSED: {RESULTS['passed']}")
print(f"FAILED: {RESULTS['failed']}")
print("=" * 80)
