from odoo import api, SUPERUSER_ID, fields


def _get_company(env):
    return env.company


def _get_or_create(env, model, search_domain, create_vals):
    record = env[model].search(search_domain, limit=1)
    if record:
        record.write(create_vals)
        return record
    return env[model].create(create_vals)


def create_branches(env):
    """Create OPS branches - MUST RUN FIRST"""
    Branch = env['ops.branch'].sudo()
    branches_data = [
        # is_headquarters removed (field not present on ops.branch)
        {'name': 'Headquarters', 'code': 'HQ', 'active': True},
        {'name': 'Dubai Marina Branch', 'code': 'DXB', 'active': True},
        {'name': 'Abu Dhabi Central', 'code': 'AUH', 'active': True},
        {'name': 'Sharjah Branch', 'code': 'SHJ', 'active': True},
    ]

    created = {}
    for data in branches_data:
        existing = Branch.search([('code', '=', data['code'])], limit=1)
        if existing:
            created[data['code']] = existing
            print(f"  Branch exists: {data['code']}")
        else:
            branch = Branch.create(data)
            created[data['code']] = branch
            print(f"  Created branch: {data['code']} (ID: {branch.id})")

    return created


def seed_test_data(env):
    """Idempotent test data seed for branches, business units, personas, users, partners, products, and transactions."""
    company = _get_company(env)

    # Branches
    branches = create_branches(env)

    # Business Units
    bu_matrix = {
        "SALES": ["HQ", "DXB", "AUH"],
        "FIN": ["HQ"],
        "OPS": ["HQ", "DXB", "AUH"],
        "RETAIL": ["DXB"],
        "WHOLESALE": ["AUH"],
    }
    business_units = {}
    for bu_name, branch_keys in bu_matrix.items():
        branch_ids = [branches[bk].id for bk in branch_keys]
        vals = {
            "name": bu_name,
            "company_ids": [(6, 0, [company.id])],
            "branch_ids": [(6, 0, branch_ids)],
            "active": True,
        }
        bu = _get_or_create(env, "ops.business.unit", [("name", "=", bu_name)], vals)
        # ensure branches set (write does 6 replace)
        bu.write({"branch_ids": [(6, 0, branch_ids)]})
        business_units[bu_name] = bu

    # Personas
    persona_specs = [
        {
            "code": "SALES_REP",
            "name": "Sales Representative",
            "flags": {"is_approver": False},
            "limits": {"approval_limit": 5000, "max_discount": 10},
        },
        {
            "code": "SALES_MGR",
            "name": "Sales Manager",
            "flags": {"is_approver": True},
            "limits": {"approval_limit": 50000, "max_discount": 25},
        },
        {
            "code": "ACCOUNTANT",
            "name": "Accountant",
            "flags": {"can_post_journal_entries": True},
        },
        {
            "code": "FIN_MGR",
            "name": "Finance Manager",
            "flags": {"can_execute_payments": True, "is_approver": True},
            "limits": {"approval_limit": 100000},
        },
        {
            "code": "BRANCH_MGR",
            "name": "Branch Manager",
            "flags": {"is_branch_manager": True, "is_approver": True, "is_cross_branch": True, "is_bu_leader": True},
        },
        {
            "code": "ADMIN",
            "name": "System Administrator",
            "flags": {"is_matrix_administrator": True, "is_cross_branch": True, "is_bu_leader": True, "is_approver": True},
        },
    ]
    personas = {}
    for spec in persona_specs:
        vals = {
            "name": spec["name"],
            "code": spec["code"],
            "company_id": company.id,
            "active": True,
        }
        flags = spec.get("flags", {})
        vals.update(flags)
        limits = spec.get("limits", {})
        if "approval_limit" in limits:
            vals["approval_limit"] = limits["approval_limit"]
        persona = _get_or_create(env, "ops.persona", [("code", "=", spec["code"])], vals)
        personas[spec["code"]] = persona

    # Users
    user_specs = [
        {"login": "sales_rep_dxb", "name": "Sarah Sales", "branch": "DXB", "bu": "SALES", "persona": "SALES_REP", "password": "test123"},
        {"login": "sales_mgr_dxb", "name": "Mike Manager", "branch": "DXB", "bu": "SALES", "persona": "SALES_MGR", "password": "test123"},
        {"login": "sales_rep_auh", "name": "Ahmed Sales", "branch": "AUH", "bu": "SALES", "persona": "SALES_REP", "password": "test123"},
        {"login": "accountant_hq", "name": "Fatima Finance", "branch": "HQ", "bu": "FIN", "persona": "ACCOUNTANT", "password": "test123"},
        {"login": "fin_mgr_hq", "name": "Omar Finance Manager", "branch": "HQ", "bu": "FIN", "persona": "FIN_MGR", "password": "test123"},
        {"login": "branch_mgr_dxb", "name": "Khalid Branch Manager", "branch": "DXB", "bu": None, "persona": "BRANCH_MGR", "password": "test123"},
        {"login": "ops_admin", "name": "System Administrator", "branch": None, "bu": None, "persona": "ADMIN", "password": "admin123"},
    ]
    users = {}
    for spec in user_specs:
        branch = branches.get(spec["branch"]) if spec.get("branch") else False
        bu = business_units.get(spec["bu"]) if spec.get("bu") else False
        persona = personas[spec["persona"]]
        user_vals = {
            "name": spec["name"],
            "login": spec["login"],
            "company_ids": [(6, 0, [company.id])],
            "company_id": company.id,
            "persona_id": persona.id,
            "ops_persona_ids": [(6, 0, [persona.id])],
            "ops_allowed_branch_ids": [(6, 0, [b.id for b in branches.values()])] if spec["persona"] == "ADMIN" else ([(6, 0, [branch.id])] if branch else [(6, 0, [b.id for b in branches.values()])]),
            "ops_allowed_business_unit_ids": [(6, 0, [bu.id for bu in business_units.values()])] if spec["persona"] == "ADMIN" or spec["persona"] == "BRANCH_MGR" else ([(6, 0, [bu.id])] if bu else [(6, 0, [bu.id for bu in business_units.values()])]),
            "ops_default_branch_id": branch.id if branch else False,
            "ops_default_business_unit_id": bu.id if bu else False,
        }
        user = env["res.users"].sudo().search([("login", "=", spec["login"])], limit=1)
        if user:
            user.sudo().write(user_vals)
        else:
            user = env["res.users"].sudo().create(user_vals)
        user.sudo().write({"password": spec["password"]})
        users[spec["login"]] = user

    # Partners
    partner_names = [
        "Acme Corporation",
        "Global Supplies Ltd",
        "Tech Solutions Inc",
        "Quick Vendors LLC",
    ]
    partners = {}
    for name in partner_names:
        partner = _get_or_create(env, "res.partner", [("name", "=", name)], {"name": name, "company_id": company.id})
        partners[name] = partner

    # Products (templates)
    product_names = ["Standard Widget", "Premium Widget", "Basic Service"]
    products = {}
    for pname in product_names:
        tmpl = _get_or_create(env, "product.template", [("name", "=", pname), ("company_id", "=", company.id)], {
            "name": pname,
            "type": "consu" if "Service" not in pname else "service",
            "list_price": 100.0,
            "company_id": company.id,
        })
        product = tmpl.product_variant_id
        products[pname] = product

    # Sales Orders (DXB and AUH)
    so_specs = [
        {"name": "SO-DXB-TEST", "branch": "DXB", "bu": "SALES", "partner": "Acme Corporation"},
        {"name": "SO-AUH-TEST", "branch": "AUH", "bu": "SALES", "partner": "Global Supplies Ltd"},
    ]
    for spec in so_specs:
        branch = branches[spec["branch"]]
        bu = business_units[spec["bu"]]
        partner = partners[spec["partner"]]
        so_vals = {
            "name": spec["name"],
            "partner_id": partner.id,
            "company_id": company.id,
            "ops_branch_id": branch.id,
            "ops_business_unit_id": bu.id,
            "order_line": [(0, 0, {
                "product_id": products["Standard Widget"].id,
                "product_uom_qty": 1,
                "price_unit": 100,
                "ops_branch_id": branch.id,
                "ops_business_unit_id": bu.id,
            })],
        }
        sale = env["sale.order"].search([("name", "=", spec["name"]), ("company_id", "=", company.id)], limit=1)
        if sale:
            sale.write(so_vals)
        else:
            sale = env["sale.order"].create(so_vals)
        if sale.state == "draft":
            sale.action_confirm()

    # Ensure journals exist
    sale_journal = env["account.journal"].search([
        ("type", "=", "sale"),
        ("company_id", "=", company.id),
    ], limit=1)
    if not sale_journal:
        sale_journal = env["account.journal"].create({
            "name": "Sales Journal",
            "code": "SAL",
            "type": "sale",
            "company_id": company.id,
        })

    purchase_journal = env["account.journal"].search([
        ("type", "=", "purchase"),
        ("company_id", "=", company.id),
    ], limit=1)
    if not purchase_journal:
        purchase_journal = env["account.journal"].create({
            "name": "Purchase Journal",
            "code": "PUR",
            "type": "purchase",
            "company_id": company.id,
        })

    # Invoices
    invoice_specs = [
        {"name": "INV-TEST-CUST", "move_type": "out_invoice", "partner": "Acme Corporation", "branch": "DXB", "bu": "SALES", "journal_id": sale_journal.id},
        {"name": "BILL-TEST-VEND", "move_type": "in_invoice", "partner": "Quick Vendors LLC", "branch": "AUH", "bu": "SALES", "journal_id": purchase_journal.id},
    ]
    for spec in invoice_specs:
        branch = branches[spec["branch"]]
        bu = business_units[spec["bu"]]
        partner = partners[spec["partner"]]
        product = products["Standard Widget"]
        income_acc = product.property_account_income_id or product.categ_id.property_account_income_categ_id
        expense_acc = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id
        line_account = income_acc if spec["move_type"] == "out_invoice" else expense_acc

        # Fallback search if product does not carry accounts
        if not line_account:
            account_domain = [
                ("company_id", "=", company.id),
                ("account_type", "=", "income" if spec["move_type"] == "out_invoice" else "expense"),
            ]
            line_account = env["account.account"].search(account_domain, limit=1)

        inv_vals = {
            "name": spec["name"],
            "move_type": spec["move_type"],
            "partner_id": partner.id,
            "company_id": company.id,
            "journal_id": spec["journal_id"],
            "invoice_date": fields.Date.context_today(env.user),
            "ops_branch_id": branch.id,
            "ops_business_unit_id": bu.id,
            "invoice_line_ids": [(0, 0, {
                "product_id": product.id,
                "account_id": line_account.id if line_account else False,
                "quantity": 1,
                "price_unit": 100,
                "ops_branch_id": branch.id,
                "ops_business_unit_id": bu.id,
            })],
        }
        inv = env["account.move"].search([("name", "=", spec["name"]), ("company_id", "=", company.id)], limit=1)
        if inv:
            inv.write(inv_vals)
        else:
            inv = env["account.move"].create(inv_vals)
        if inv.state == "draft":
            inv.action_post()

    # Commit to persist seed data when running from odoo shell
    env.cr.commit()
    print("Seed commit complete.")
