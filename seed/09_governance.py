import sys

def log(msg):
    sys.stderr.write(f"{msg}\n")

log("=" * 50)
log("SEED 09: Governance, SoD, SLA Rules")
log("=" * 50)

try:
    # 1. Enable ALL existing governance rules
    log("\n--- Governance Rules ---")
    GovRule = env['ops.governance.rule']
    rules = GovRule.search([])
    for rule in rules:
        updates = {}
        if not rule.active:
            updates['active'] = True
        if hasattr(rule, 'enabled') and not rule.enabled:
            updates['enabled'] = True
        if updates:
            rule.write(updates)
            log(f"+ Enabled: {rule.name}")
        else:
            log(f"= Already active: {rule.name}")

    # 2. Enable ALL SoD rules
    log("\n--- Segregation of Duties Rules ---")
    SoD = env['ops.segregation.of.duties']
    sod_rules = SoD.search([])
    for rule in sod_rules:
        updates = {}
        if not rule.active:
            updates['active'] = True
        if hasattr(rule, 'enabled') and not rule.enabled:
            updates['enabled'] = True
        if hasattr(rule, 'block_violation'):
            # Block violations for payment and invoice rules
            if rule.model_name in ('account.move', 'payment') and not rule.block_violation:
                updates['block_violation'] = True
        if updates:
            rule.write(updates)
            log(f"+ Enabled: {rule.name} (block={rule.block_violation if hasattr(rule, 'block_violation') else 'N/A'})")
        else:
            log(f"= Already active: {rule.name}")

    # 3. Enable ALL SLA templates
    log("\n--- SLA Templates ---")
    SLA = env['ops.sla.template']
    sla_templates = SLA.search([])
    for tmpl in sla_templates:
        updates = {}
        if not tmpl.active:
            updates['active'] = True
        if hasattr(tmpl, 'enabled') and not tmpl.enabled:
            updates['enabled'] = True
        if updates:
            tmpl.write(updates)
            log(f"+ Enabled: {tmpl.name}")
        else:
            log(f"= Already active: {tmpl.name}")

    # 4. Create Product Requests if model exists
    log("\n--- Product Requests ---")
    if 'ops.product.request' in env:
        PR = env['ops.product.request']
        User = env['res.users']

        requests_data = [
            {
                'name': 'New Laptop Model - Dell XPS 15',
                'description': 'Customer demand for Dell XPS 15 laptops. Multiple inquiries from corporate clients.',
                'requested_by_login': 'sales.rep1@mztrading.com',
            },
            {
                'name': 'Organic Coffee Beans (Premium)',
                'description': 'Premium organic coffee beans from Ethiopian highlands. Growing market demand.',
                'requested_by_login': 'purchase.mgr@mztrading.com',
            },
            {
                'name': 'Smart Watch Collection',
                'description': 'Apple Watch and Samsung Galaxy Watch series. High margin potential.',
                'requested_by_login': 'sales.mgr@mztrading.com',
            },
        ]

        for data in requests_data:
            existing = PR.search([('name', '=', data['name'])], limit=1)
            if existing:
                log(f"= Exists: {data['name']}")
                continue

            user = User.search([('login', '=', data['requested_by_login'])], limit=1)
            vals = {
                'name': data['name'],
                'description': data['description'],
                'company_id': 1,
            }
            if user and 'requested_by' in PR._fields:
                vals['requested_by'] = user.id
            elif user and 'user_id' in PR._fields:
                vals['user_id'] = user.id

            try:
                pr = PR.create(vals)
                log(f"+ Created: {data['name']}")
            except Exception as e:
                log(f"! Failed to create {data['name']}: {e}")
    else:
        log("Model ops.product.request not found, skipping")

    # 5. Create Archive Policies if model exists
    log("\n--- Archive Policies ---")
    if 'ops.archive.policy' in env:
        AP = env['ops.archive.policy']

        policies = [
            {
                'name': 'Archive Cancelled Sales Orders',
                'model_name': 'sale.order',
                'retention_days': 365,
            },
            {
                'name': 'Archive Old Journal Entries',
                'model_name': 'account.move',
                'retention_days': 730,
            },
        ]

        for data in policies:
            existing = AP.search([('name', '=', data['name'])], limit=1)
            if existing:
                log(f"= Exists: {data['name']}")
                continue
            try:
                # Try with available fields
                vals = {'name': data['name']}
                if 'model_id' in AP._fields:
                    model = env['ir.model'].search([('model', '=', data['model_name'])], limit=1)
                    if model:
                        vals['model_id'] = model.id
                elif 'model_name' in AP._fields:
                    vals['model_name'] = data['model_name']
                if 'retention_days' in AP._fields:
                    vals['retention_days'] = data['retention_days']
                if 'company_id' in AP._fields:
                    vals['company_id'] = 1

                ap = AP.create(vals)
                log(f"+ Created: {data['name']}")
            except Exception as e:
                log(f"! Failed: {data['name']}: {e}")
    else:
        log("Model ops.archive.policy not found, skipping")

    # 6. Enable field visibility rules
    log("\n--- Field Visibility Rules ---")
    if 'ops.field.visibility.rule' in env:
        FV = env['ops.field.visibility.rule']
        fv_rules = FV.search([])
        enabled_count = 0
        for rule in fv_rules:
            if hasattr(rule, 'active') and not rule.active:
                rule.write({'active': True})
                enabled_count += 1
        log(f"Enabled {enabled_count} field visibility rules (total: {len(fv_rules)})")
    else:
        log("Model ops.field.visibility.rule not found")

    env.cr.commit()
    log("\nSEED 09 COMPLETE - Governance and security rules configured")

except Exception as e:
    env.cr.rollback()
    log(f"ERROR: {e}")
    import traceback
    sys.stderr.write(traceback.format_exc())
