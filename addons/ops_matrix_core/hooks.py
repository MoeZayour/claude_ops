from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def _auto_configure_matrix(env):
    """
    EMERGENCY FIX: Minimal auto-configuration to prevent demo data creation.
    All setup should be done manually via Setup Wizards by users.
    """
    _logger.info("=== OPS Matrix Core: Minimal Auto-Configuration Started ===")
    
    # Step 1: Ensure existing company has OPS fields populated (REQUIRED)
    main_company = env.company
    if main_company and not main_company.ops_code:
        _logger.info(f"Setting OPS code for existing company: {main_company.name}")
        main_company.ops_code = env['ir.sequence'].next_by_code('res.company.ops') or 'HQ'
        _logger.info(f"✓ Company OPS code set: {main_company.ops_code}")
    else:
        _logger.info(f"✓ Company already configured: {main_company.name} ({main_company.ops_code})")
    
    # Step 2: REMOVED - Do NOT create demo Business Units
    # Users must create their own BUs via the Setup Wizard
    _logger.info("✓ Skipping demo data creation (clean install)")
    
    # Step 3: Link warehouses to company if not set (if field exists)
    Warehouse = env['stock.warehouse']
    try:
        if 'ops_branch_id' in Warehouse._fields:
            warehouses = Warehouse.search([('ops_branch_id', '=', False)])
            if warehouses:
                _logger.info(f"Found {len(warehouses)} warehouse(s) without branch. Linking to main company...")
                warehouses.write({'ops_branch_id': main_company.id})
                for wh in warehouses:
                    _logger.info(f"✓ Warehouse '{wh.name}' linked to {main_company.name}")
            else:
                _logger.info("✓ All warehouses already have branches assigned")
        else:
            _logger.info("Note: ops_branch_id field not found on stock.warehouse (may not be installed yet)")
    except Exception as e:
        _logger.warning(f"Could not link warehouses to branches: {e}")
    
    _logger.info("=== OPS Matrix Core: Minimal Auto-Configuration Complete ===")


def _ensure_generic_coa(env):
    """Load a minimal generic chart of accounts if none is installed.

    This is needed for downstream seeds (sale/purchase journals, default accounts).
    """
    Company = env.company
    AccountAccount = env['account.account']

    # Safety: some registries may not have company_id yet (during early boot)
    if 'company_id' not in AccountAccount._fields:
        _logger.warning("account.account.company_id not available yet; skipping generic COA load this pass")
        return

    existing_accounts = AccountAccount.search_count([('company_id', '=', Company.id)])

    if existing_accounts:
        _logger.info("✓ Chart of accounts already present; skipping generic load")
        return

    # Fallback: use the built-in minimal chart loader
    try:
        _logger.info("Loading generic chart of accounts for company %s", Company.name)
        env.ref('base.generic_coa').with_user(SUPERUSER_ID)._load(CoA=None)  # type: ignore[attr-defined]
        _logger.info("✓ Generic chart of accounts loaded")
    except Exception as e:
        _logger.warning("Generic COA load failed or not available: %s", e)


def _set_not_null_constraints(env):
    """
    Helper function to ensure analytic accounts for companies.
    Note: We're no longer setting NOT NULL on ops_analytic_account_id
    since it's auto-created by the res.company create method.
    """
    _logger.info("Checking companies for missing analytic accounts...")
    
    # Check if the column exists first
    env.cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='res_company'
        AND column_name='ops_analytic_account_id'
    """)
    if not env.cr.fetchone():
        _logger.info("ops_analytic_account_id column does not exist yet, skipping check")
        return
    
    # Ensure an analytic plan exists (required for account.analytic.account.plan_id)
    plan = env['account.analytic.plan'].search([('name', '=', 'Matrix Branch')], limit=1)
    if not plan:
        _logger.warning("No analytic plan found (Matrix Branch). Skipping analytic account creation to avoid install-time sync errors.")
        return

    # Find companies without analytic accounts
    env.cr.execute("""
        SELECT id, name, ops_code, id as company_id
        FROM res_company
        WHERE ops_analytic_account_id IS NULL;
    """)
    companies = env.cr.fetchall()
    
    if companies:
        _logger.info(f"Found {len(companies)} companies without analytic accounts. Creating...")
        for company_id, name, ops_code, comp_id in companies:
            analytic = env['account.analytic.account'].create({
                'name': f"{name} - OPS",
                'code': ops_code or 'OPS',
                'company_id': comp_id,
                'plan_id': plan.id,
            })
            env.cr.execute("""
                UPDATE res_company
                SET ops_analytic_account_id = %s
                WHERE id = %s
            """, (analytic.id, company_id))
            _logger.info(f"✓ Created analytic account for company: {name}")
    else:
        _logger.info("✓ All companies have analytic accounts")


def post_init_hook(env):
    """
    Post-init hook for ops_matrix_core module.
    Executes auto-configuration.
    
    NOTE: In Odoo 19, post_init_hook receives 'env' as single argument, not (cr, registry).
    """
    _logger.info("Running post_init_hook for ops_matrix_core...")
    
    # Run auto-configuration
    _auto_configure_matrix(env)

    # Ensure we have a chart of accounts
    _ensure_generic_coa(env)
    
    # Ensure analytic accounts exist
    _set_not_null_constraints(env)
    
    # Setup analytic structure for Matrix dimensions
    _setup_analytic_structure(env)
    
    _logger.info("post_init_hook completed successfully")


def _setup_analytic_structure(env):
    """
    Auto-setup analytic structure on module installation.
    Creates Matrix Branch and Matrix Business Unit analytic plans.
    
    NOTE: On fresh installations, branches/BUs may not exist yet.
    In that case, we only create the analytic plans. The branches/BUs
    will auto-create their analytic accounts when they are created.
    """
    _logger.info("Setting up Matrix analytic structure...")
    
    # Check if analytic plans exist
    branch_plan = env['account.analytic.plan'].search([('name', '=', 'Matrix Branch')], limit=1)
    bu_plan = env['account.analytic.plan'].search([('name', '=', 'Matrix Business Unit')], limit=1)
    
    if not branch_plan or not bu_plan:
        _logger.info("Creating Matrix analytic plans...")
        
        # Create Branch analytic plan
        if not branch_plan:
            branch_plan = env['account.analytic.plan'].create({
                'name': 'Matrix Branch',
                'description': 'Operational Branch tracking for Matrix reporting',
            })
            _logger.info(f"✓ Created Matrix Branch analytic plan (ID: {branch_plan.id})")
        
        # Create Business Unit analytic plan
        if not bu_plan:
            bu_plan = env['account.analytic.plan'].create({
                'name': 'Matrix Business Unit',
                'description': 'Business Unit profit center tracking',
            })
            _logger.info(f"✓ Created Matrix Business Unit analytic plan (ID: {bu_plan.id})")
    else:
        _logger.info("✓ Analytic plans already exist")
    
    # Check if branches and BUs exist before trying to sync
    branch_count = env['ops.branch'].search_count([('active', '=', True)])
    bu_count = env['ops.business.unit'].search_count([('active', '=', True)])
    
    if branch_count == 0 and bu_count == 0:
        _logger.info("ℹ Fresh installation detected: No branches or business units yet.")
        _logger.info("  Analytic accounts will be auto-created when branches/BUs are created.")
        _logger.info("✓ Analytic structure setup complete (plans only)")
        return
    
    # If branches/BUs exist, sync their analytic accounts
    if branch_count > 0 or bu_count > 0:
        _logger.info(f"Syncing analytic accounts for {branch_count} branches and {bu_count} BUs...")
        try:
            setup_wizard = env['ops.analytic.setup'].create({})
            
            # Sync branches if they exist
            if branch_count > 0:
                try:
                    branch_created = setup_wizard._sync_branch_analytic_accounts()
                    _logger.info(f"✓ Synced {branch_created} branch analytic accounts")
                except Exception as e:
                    _logger.warning(f"Could not sync branch analytic accounts: {e}")
            
            # Sync BUs if they exist
            if bu_count > 0:
                try:
                    bu_created = setup_wizard._sync_bu_analytic_accounts()
                    _logger.info(f"✓ Synced {bu_created} BU analytic accounts")
                except Exception as e:
                    _logger.warning(f"Could not sync BU analytic accounts: {e}")
                    
        except Exception as e:
            _logger.warning(f"Analytic account sync encountered issues (non-fatal): {e}")
    
    _logger.info("✓ Analytic structure setup complete")


def post_load():
    """Post-load hook to set NOT NULL constraints."""
    def wrapped(cr, registry):
        env = api.Environment(cr, SUPERUSER_ID, {})
        _set_not_null_constraints(env)
    return wrapped
