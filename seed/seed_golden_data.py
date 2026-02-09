#!/usr/bin/env python3
"""Golden Data Seeding Script for OPS Framework."""

def seed_data(env):
    """Seed golden data for dashboard testing."""
    print("🚀 Starting Golden Data Seeding...")

    # Get existing Branch (use MAIN if exists)
    hq = env['ops.branch'].search([('code', '=', 'MAIN')], limit=1)
    if not hq:
        hq = env['ops.branch'].search([], limit=1)
    if not hq:
        hq = env['ops.branch'].create({'name': 'Headquarters', 'code': 'BR-HQ', 'active': True})
        print(f"✅ Created Branch: {hq.name}")
    else:
        print(f"ℹ️ Using Branch: {hq.name} ({hq.code})")

    # Get existing BU
    bu = env['ops.business.unit'].search([('code', '=', 'GBU')], limit=1)
    if not bu:
        bu = env['ops.business.unit'].search([], limit=1)
    if not bu:
        bu = env['ops.business.unit'].create({'name': 'Consumer Goods', 'code': 'BU-CONS', 'active': True})
        print(f"✅ Created BU: {bu.name}")
    else:
        print(f"ℹ️ Using BU: {bu.name} ({bu.code})")

    # Get or Create Product
    prod = env['product.product'].search([('default_code', '=', 'OPS-RACK')], limit=1)
    if not prod:
        prod = env['product.product'].create({
            'name': 'OPS Server Rack',
            'default_code': 'OPS-RACK',
            'list_price': 1000.0,
            'standard_price': 600.0,
            'type': 'consu',
            'sale_ok': True,
        })
        print(f"✅ Created Product: {prod.name} @ $1,000")
    else:
        print(f"ℹ️ Product exists: {prod.name}")

    # Get partner
    partner = env['res.partner'].search([('is_company', '=', True)], limit=1)
    if not partner:
        partner = env['res.partner'].search([], limit=1)
    print(f"ℹ️ Using Partner: {partner.name}")

    # Get admin
    admin = env['res.users'].search([('login', '=', 'admin')], limit=1)
    print(f"ℹ️ Admin: {admin.login}")

    # Check existing confirmed sales
    existing = env['sale.order'].search([('state', 'in', ['sale', 'done'])])
    existing_total = sum(existing.mapped('amount_total'))
    print(f"📊 Existing confirmed sales: {len(existing)}, Total: ${existing_total:,.2f}")

    # Create order if needed
    if existing_total < 5000:
        needed = 5000 - existing_total
        qty = max(5, int(needed / 1000))

        order_vals = {
            'partner_id': partner.id,
            'user_id': admin.id,
            'order_line': [(0, 0, {
                'product_id': prod.id,
                'product_uom_qty': qty,
                'price_unit': 1000.0,
            })]
        }

        # Add OPS fields if available
        so_model = env['sale.order']
        if 'ops_branch_id' in so_model._fields:
            order_vals['ops_branch_id'] = hq.id
        if 'ops_business_unit_id' in so_model._fields:
            order_vals['ops_business_unit_id'] = bu.id

        order = env['sale.order'].create(order_vals)
        order.action_confirm()
        env.cr.commit()
        print(f"✅ Created & Confirmed: {order.name} (${order.amount_total:,.2f})")
    else:
        print(f"ℹ️ Sales target already met: ${existing_total:,.2f}")

    # Final verification
    final = env['sale.order'].search([('state', 'in', ['sale', 'done'])])
    final_total = sum(final.mapped('amount_total'))
    print(f"🎉 FINAL: {len(final)} confirmed orders, Total Sales: ${final_total:,.2f}")

    return final_total


if __name__ == '__main__':
    # This will be called from odoo shell
    pass
