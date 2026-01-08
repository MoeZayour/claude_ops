-- OPS Framework Comprehensive Seed Data
-- Run via: docker exec gemini_odoo19_db psql -U odoo -d mz-db -f /tmp/seed_data.sql

-- Get company ID
DO $$
DECLARE
    v_company_id INTEGER;
    v_user_id INTEGER;
BEGIN
    SELECT id INTO v_company_id FROM res_company LIMIT 1;

    -- =============================================
    -- 1. CREATE PERSONAS FOR ALL USERS
    -- =============================================
    RAISE NOTICE 'Creating Personas...';

    -- Admin/CEO Persona
    INSERT INTO ops_persona (name, code, user_id, company_id, is_approver, approval_limit,
        is_branch_manager, is_bu_leader, is_matrix_administrator, job_level, active, create_uid, create_date, write_uid, write_date)
    SELECT 'CEO - Executive', 'PRS-CEO-001', id, v_company_id, true, 1000000, true, true, true, 'executive', true, 1, now(), 1, now()
    FROM res_users WHERE login = 'admin'
    ON CONFLICT DO NOTHING;

    -- Get user IDs for other personas
    FOR v_user_id IN SELECT id FROM res_users WHERE login != 'admin' LOOP
        -- Branch Manager Persona
        INSERT INTO ops_persona (name, code, user_id, company_id, is_approver, approval_limit,
            is_branch_manager, is_bu_leader, job_level, active, create_uid, create_date, write_uid, write_date)
        VALUES (
            'Branch Manager', 'PRS-BM-' || v_user_id, v_user_id, v_company_id,
            true, 50000, true, false, 'manager', true, 1, now(), 1, now()
        ) ON CONFLICT DO NOTHING;

        -- Finance Persona (if user email contains 'account' or 'finance')
        INSERT INTO ops_persona (name, code, user_id, company_id, is_approver, approval_limit,
            can_validate_invoices, can_access_cost_prices, job_level, active, create_uid, create_date, write_uid, write_date)
        VALUES (
            'Finance - Accountant', 'PRS-FIN-' || v_user_id, v_user_id, v_company_id,
            true, 250000, true, true, 'senior', true, 1, now(), 1, now()
        ) ON CONFLICT DO NOTHING;

        -- Sales Persona
        INSERT INTO ops_persona (name, code, user_id, company_id,
            can_access_cost_prices, max_discount_percent, job_level, active, create_uid, create_date, write_uid, write_date)
        VALUES (
            'Sales Representative', 'PRS-SALES-' || v_user_id, v_user_id, v_company_id,
            false, 5.0, 'mid', true, 1, now(), 1, now()
        ) ON CONFLICT DO NOTHING;

        -- Warehouse Persona
        INSERT INTO ops_persona (name, code, user_id, company_id,
            can_adjust_inventory, can_access_cost_prices, job_level, active, create_uid, create_date, write_uid, write_date)
        VALUES (
            'Warehouse Manager', 'PRS-WH-' || v_user_id, v_user_id, v_company_id,
            true, true, 'manager', true, 1, now(), 1, now()
        ) ON CONFLICT DO NOTHING;
    END LOOP;

    RAISE NOTICE 'Personas created successfully';
END $$;

-- =============================================
-- 2. CREATE SEGREGATION OF DUTIES RULES
-- =============================================
DO $$
DECLARE
    v_model_id INTEGER;
BEGIN
    RAISE NOTICE 'Creating SoD Rules...';

    -- Get model IDs
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'account.payment' LIMIT 1;

    -- SoD: No Approve & Record Payments
    INSERT INTO ops_segregation_of_duties (name, description, model_id, action_1, action_2, severity, active, create_uid, create_date, write_uid, write_date)
    VALUES (
        'No Approve & Record Payments',
        'Prevents users from approving and recording the same payment',
        v_model_id, 'approve', 'create', 'high', true, 1, now(), 1, now()
    ) ON CONFLICT DO NOTHING;

    -- SoD: No Create & Approve Invoices
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'account.move' LIMIT 1;
    INSERT INTO ops_segregation_of_duties (name, description, model_id, action_1, action_2, severity, active, create_uid, create_date, write_uid, write_date)
    VALUES (
        'No Create & Approve Invoices',
        'Prevents users from creating and approving their own invoices',
        v_model_id, 'create', 'approve', 'critical', true, 1, now(), 1, now()
    ) ON CONFLICT DO NOTHING;

    -- SoD: Cost Modification Restriction
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'product.product' LIMIT 1;
    INSERT INTO ops_segregation_of_duties (name, description, model_id, action_1, action_2, severity, active, create_uid, create_date, write_uid, write_date)
    VALUES (
        'No Cost Modification',
        'Prevents unauthorized modification of product cost prices',
        v_model_id, 'write', 'read', 'medium', true, 1, now(), 1, now()
    ) ON CONFLICT DO NOTHING;

    RAISE NOTICE 'SoD Rules created successfully';
END $$;

-- =============================================
-- 3. CREATE FIELD VISIBILITY RULES
-- =============================================
DO $$
DECLARE
    v_group_id INTEGER;
    v_model_id INTEGER;
BEGIN
    RAISE NOTICE 'Creating Field Visibility Rules...';

    -- Get sales group
    SELECT id INTO v_group_id FROM res_groups WHERE name = 'User: All Users' AND category_id IN (SELECT id FROM ir_module_category WHERE name = 'Sales') LIMIT 1;
    IF v_group_id IS NULL THEN
        SELECT id INTO v_group_id FROM res_groups WHERE name = 'User: All Users' LIMIT 1;
    END IF;

    -- Get product model
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'product.product' LIMIT 1;

    -- Rule: Hide cost from non-admin users
    INSERT INTO ops_field_visibility_rule (model_name, field_name, field_label, security_group_id, visibility_mode, description, is_active, create_uid, create_date, write_uid, write_date)
    VALUES (
        'product.product', 'standard_price', 'Cost Price',
        v_group_id, 'hidden',
        'Hide product cost from unauthorized users to protect margins',
        true, 1, now(), 1, now()
    ) ON CONFLICT DO NOTHING;

    -- Rule: Hide vendor info from sales
    INSERT INTO ops_field_visibility_rule (model_name, field_name, field_label, security_group_id, visibility_mode, description, is_active, create_uid, create_date, write_uid, write_date)
    VALUES (
        'product.product', 'seller_ids', 'Vendor Information',
        v_group_id, 'hidden',
        'Hide vendor/supplier information from sales team',
        true, 1, now(), 1, now()
    ) ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Field Visibility Rules created successfully';
END $$;

-- =============================================
-- 4. CREATE SLA TEMPLATES
-- =============================================
DO $$
DECLARE
    v_model_id INTEGER;
BEGIN
    RAISE NOTICE 'Creating SLA Templates...';

    -- Get sale order model
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'sale.order' LIMIT 1;
    INSERT INTO ops_sla_template (name, model_id, target_hours, priority, active, create_uid, create_date, write_uid, write_date)
    VALUES ('Sales Order Approval', v_model_id, 4, 'standard', true, 1, now(), 1, now())
    ON CONFLICT DO NOTHING;

    -- Get invoice model
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'account.move' LIMIT 1;
    INSERT INTO ops_sla_template (name, model_id, target_hours, priority, active, create_uid, create_date, write_uid, write_date)
    VALUES ('Invoice Validation', v_model_id, 24, 'high', true, 1, now(), 1, now())
    ON CONFLICT DO NOTHING;

    -- Get payment model
    SELECT id INTO v_model_id FROM ir_model WHERE model = 'account.payment' LIMIT 1;
    INSERT INTO ops_sla_template (name, model_id, target_hours, priority, active, create_uid, create_date, write_uid, write_date)
    VALUES ('Vendor Payment Processing', v_model_id, 48, 'standard', true, 1, now(), 1, now())
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'SLA Templates created successfully';
END $$;

-- =============================================
-- 5. CREATE SAMPLE GOVERNANCE RULES
-- =============================================
DO $$
BEGIN
    RAISE NOTICE 'Creating Governance Rules...';

    -- Discount Limit Rule
    INSERT INTO ops_governance_rule (name, description, model_id, rule_type, severity, active, create_uid, create_date, write_uid, write_date)
    SELECT 'Max Discount 20%', 'Orders exceeding 20% discount require approval',
        id, 'discount_limit', 'high', true, 1, now(), 1, now()
    FROM ir_model WHERE model = 'sale.order' LIMIT 1
    ON CONFLICT DO NOTHING;

    -- Credit Limit Rule
    INSERT INTO ops_governance_rule (name, description, model_id, rule_type, severity, active, create_uid, create_date, write_uid, write_date)
    SELECT 'Credit Limit Check', 'Orders exceeding customer credit limit require approval',
        id, 'credit_limit', 'critical', true, 1, now(), 1, now()
    FROM ir_model WHERE model = 'sale.order' LIMIT 1
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Governance Rules created successfully';
END $$;

-- =============================================
-- 6. VERIFY CREATED DATA
-- =============================================
SELECT 'Personas' as entity, COUNT(*) as count FROM ops_persona
UNION ALL SELECT 'SoD Rules', COUNT(*) FROM ops_segregation_of_duties
UNION ALL SELECT 'Field Visibility Rules', COUNT(*) FROM ops_field_visibility_rule
UNION ALL SELECT 'SLA Templates', COUNT(*) FROM ops_sla_template
UNION ALL SELECT 'Governance Rules', COUNT(*) FROM ops_governance_rule;
