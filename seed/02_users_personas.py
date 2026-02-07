# -*- coding: utf-8 -*-
"""
02_users_personas.py - Create demo users and assign personas with matrix dimensions.

Run via:
    cat seed/02_users_personas.py | docker exec -i gemini_odoo19 odoo shell \
        -c /etc/odoo/odoo.conf -d mz-db --no-http

Idempotent: checks login before creating users, checks persona code before assigning.
Uses ONLY Odoo ORM (no raw SQL).
"""
import sys

def log(msg):
    """Print progress to stderr (stdout is swallowed by Odoo shell)."""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def main(env):
    log("=" * 70)
    log("  02_USERS_PERSONAS - Create Users & Assign Personas")
    log("=" * 70)

    User = env['res.users']
    Persona = env['ops.persona']
    Branch = env['ops.branch']
    BU = env['ops.business.unit']

    COMPANY_ID = 1
    PASSWORD = "Demo@2026"

    # ------------------------------------------------------------------
    # STEP 1: Discover branches by name pattern
    # ------------------------------------------------------------------
    log("\n[1/4] Discovering branches...")

    all_branches = Branch.search([('company_id', '=', COMPANY_ID), ('active', '=', True)])
    log(f"  Found {len(all_branches)} active branches in company {COMPANY_ID}:")
    for b in all_branches:
        log(f"    - [{b.code}] {b.name} (ID: {b.id})")

    def find_branch(pattern):
        """Find a branch whose name contains the pattern (case-insensitive)."""
        pattern_lower = pattern.lower()
        for b in all_branches:
            if pattern_lower in b.name.lower():
                return b
        log(f"  WARNING: No branch matching '{pattern}'")
        return None

    br_dubai = find_branch('Dubai')
    br_abudhabi = find_branch('Abu Dhabi')
    br_sharjah = find_branch('Sharjah')
    br_riyadh = find_branch('Riyadh')
    br_doha = find_branch('Doha')

    # Collect all found branches (filter out None)
    all_found = [b for b in [br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha] if b]
    log(f"  Matched {len(all_found)} of 5 expected branches")

    # Helper to build branch ID list from branch references (filters None)
    def branch_ids(*branches):
        return [b.id for b in branches if b]

    # ------------------------------------------------------------------
    # STEP 2: Discover business units by name pattern
    # ------------------------------------------------------------------
    log("\n[2/4] Discovering business units...")

    all_bus = BU.search([('active', '=', True)])
    log(f"  Found {len(all_bus)} active business units:")
    for bu in all_bus:
        log(f"    - [{bu.code}] {bu.name} (ID: {bu.id})")

    def find_bu(pattern):
        """Find a BU whose name contains the pattern (case-insensitive)."""
        pattern_lower = pattern.lower()
        for bu in all_bus:
            if pattern_lower in bu.name.lower():
                return bu
        log(f"  WARNING: No BU matching '{pattern}'")
        return None

    bu_electronics = find_bu('Electronics')
    bu_luxury = find_bu('Luxury')
    bu_fb = find_bu('F&B') or find_bu('Food') or find_bu('Beverage')
    bu_it = find_bu('IT Solutions') or find_bu('IT')

    all_found_bus = [bu for bu in [bu_electronics, bu_luxury, bu_fb, bu_it] if bu]
    log(f"  Matched {len(all_found_bus)} of 4 expected BUs")

    def bu_ids(*bus):
        return [bu.id for bu in bus if bu]

    # ------------------------------------------------------------------
    # STEP 3: Create users
    # ------------------------------------------------------------------
    log("\n[3/4] Creating users...")

    # User definitions: (login, name, persona_code)
    USER_DEFS = [
        ('ceo@mztrading.com', 'Ahmed Al Mansouri', 'CEO'),
        ('cfo@mztrading.com', 'Sarah Al Hashimi', 'CFO'),
        ('fin.ctrl@mztrading.com', 'Mohammad Khalil', 'FIN_CTRL'),
        ('sales.director@mztrading.com', 'Khalid Al Rashid', 'SALES_LEADER'),
        ('sales.mgr@mztrading.com', 'Fatima Al Zahra', 'SALES_MGR'),
        ('purchase.mgr@mztrading.com', 'Omar Hassan', 'PURCHASE_MGR'),
        ('chief.acct@mztrading.com', 'Layla Ibrahim', 'CHIEF_ACCT'),
        ('treasury@mztrading.com', 'Yousef Al Nasser', 'TREASURY_OFF'),
        ('logistics@mztrading.com', 'Rashid Al Maktoum', 'LOG_MGR'),
        ('hr.mgr@mztrading.com', 'Aisha Mahmoud', 'HR_MGR'),
        ('sales.rep1@mztrading.com', 'Ali Al Farsi', 'SALES_REP'),
        ('sales.rep2@mztrading.com', 'Hassan Al Mutairi', 'SALES_REP'),
        ('purchase.off@mztrading.com', 'Nora Al Dosari', 'PURCHASE_OFF'),
        ('log.clerk@mztrading.com', 'Saeed Al Shamsi', 'LOG_CLERK'),
        ('accountant@mztrading.com', 'Huda Al Qasimi', 'ACCOUNTANT'),
        ('ar.clerk@mztrading.com', 'Mariam Khalaf', 'AR_CLERK'),
        ('ap.clerk@mztrading.com', 'Tariq Al Sayed', 'AP_CLERK'),
        ('it.admin@mztrading.com', 'Rami Saleh', 'SYS_ADMIN'),
    ]

    created_users = {}  # login -> user record

    for login, name, persona_code in USER_DEFS:
        existing = User.with_context(skip_ops_validation=True).search(
            [('login', '=', login)], limit=1
        )
        if existing:
            log(f"  EXISTS: {login} ({existing.name}, ID: {existing.id})")
            created_users[login] = existing
            # Ensure company assignment is correct
            if existing.company_id.id != COMPANY_ID:
                existing.with_context(skip_ops_validation=True).write({
                    'company_id': COMPANY_ID,
                })
            if COMPANY_ID not in existing.company_ids.ids:
                existing.with_context(skip_ops_validation=True).write({
                    'company_ids': [(4, COMPANY_ID)],
                })
            continue

        try:
            user = User.with_context(skip_ops_validation=True).create({
                'name': name,
                'login': login,
                'password': PASSWORD,
                'company_id': COMPANY_ID,
                'company_ids': [(4, COMPANY_ID)],
            })
            created_users[login] = user
            log(f"  CREATED: {login} -> {name} (ID: {user.id})")
        except Exception as e:
            log(f"  ERROR creating {login}: {e}")

    log(f"  Total users ready: {len(created_users)}")

    # ------------------------------------------------------------------
    # STEP 4: Assign personas with branch/BU dimensions
    # ------------------------------------------------------------------
    log("\n[4/4] Assigning personas...")

    # Persona assignment configuration
    # Format: persona_code -> {
    #   'login': user login,
    #   'branches': list of branch records,
    #   'bus': list of BU records,
    #   'default_branch': branch record,
    #   'default_bu': BU record or None,
    #   'extra_flags': dict of extra persona fields,
    # }

    # Build the full assignment map.
    # Note: SALES_REP persona is used by two users. We handle this by creating
    # a unique persona per user when the code is shared (sales reps).

    # For all personas EXCEPT SALES_REP, the mapping is 1:1 persona_code -> user.
    PERSONA_ASSIGNMENTS = {
        'CEO': {
            'login': 'ceo@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_luxury, bu_fb, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {'is_matrix_administrator': True},
        },
        'CFO': {
            'login': 'cfo@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_luxury, bu_fb, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'FIN_CTRL': {
            'login': 'fin.ctrl@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_luxury, bu_fb, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'SALES_LEADER': {
            'login': 'sales.director@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_luxury, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'SALES_MGR': {
            'login': 'sales.mgr@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi),
            'bus': bu_ids(bu_electronics, bu_luxury),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'PURCHASE_MGR': {
            'login': 'purchase.mgr@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_fb, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'CHIEF_ACCT': {
            'login': 'chief.acct@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_luxury, bu_fb, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'TREASURY_OFF': {
            'login': 'treasury@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi),
            'bus': bu_ids(bu_electronics, bu_luxury, bu_fb, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'LOG_MGR': {
            'login': 'logistics@mztrading.com',
            'branches': branch_ids(br_dubai, br_sharjah, br_riyadh),
            'bus': bu_ids(bu_electronics, bu_fb),
            'default_branch': br_sharjah,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'HR_MGR': {
            'login': 'hr.mgr@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': [],  # No BU assignment for HR
            'default_branch': br_dubai,
            'default_bu': None,
            'extra_flags': {},
        },
        'PURCHASE_OFF': {
            'login': 'purchase.off@mztrading.com',
            'branches': branch_ids(br_dubai, br_sharjah),
            'bus': bu_ids(bu_fb, bu_electronics),
            'default_branch': br_dubai,
            'default_bu': bu_fb,
            'extra_flags': {},
        },
        'LOG_CLERK': {
            'login': 'log.clerk@mztrading.com',
            'branches': branch_ids(br_sharjah),
            'bus': bu_ids(bu_fb),
            'default_branch': br_sharjah,
            'default_bu': bu_fb,
            'extra_flags': {},
        },
        'ACCOUNTANT': {
            'login': 'accountant@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi),
            'bus': bu_ids(bu_electronics, bu_it),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'AR_CLERK': {
            'login': 'ar.clerk@mztrading.com',
            'branches': branch_ids(br_dubai),
            'bus': bu_ids(bu_electronics, bu_luxury),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
            'extra_flags': {},
        },
        'AP_CLERK': {
            'login': 'ap.clerk@mztrading.com',
            'branches': branch_ids(br_dubai, br_sharjah),
            'bus': bu_ids(bu_fb, bu_electronics),
            'default_branch': br_dubai,
            'default_bu': bu_fb,
            'extra_flags': {},
        },
        'SYS_ADMIN': {
            'login': 'it.admin@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi, br_sharjah, br_riyadh, br_doha),
            'bus': [],  # IT Admin should NOT see business data
            'default_branch': br_dubai,
            'default_bu': None,
            'extra_flags': {},
        },
    }

    # Sales reps are special: two users share the SALES_REP persona code.
    # We need the *same* persona record for Sales Rep (template). Odoo persona
    # has a Many2one user_id, so only one user can be the primary. However, the
    # ops_persona_ids on res.users is Many2many, so both users can reference the
    # same persona. Since the persona model only has user_id (Many2one), we will:
    #  - Find the persona by code
    #  - Assign the FIRST sales rep as the persona's user_id
    #  - Add the persona to both users' ops_persona_ids
    #  - Configure branch/BU on the USERS directly (since persona is shared)

    SALES_REP_USERS = [
        {
            'login': 'sales.rep1@mztrading.com',
            'branches': branch_ids(br_dubai, br_abudhabi),
            'bus': bu_ids(bu_electronics),
            'default_branch': br_dubai,
            'default_bu': bu_electronics,
        },
        {
            'login': 'sales.rep2@mztrading.com',
            'branches': branch_ids(br_riyadh, br_doha),
            'bus': bu_ids(bu_electronics, bu_luxury),
            'default_branch': br_riyadh,
            'default_bu': bu_electronics,
        },
    ]

    # ----- Process non-shared personas (1:1 mapping) -----
    assigned_count = 0
    for persona_code, config in PERSONA_ASSIGNMENTS.items():
        login = config['login']
        user = created_users.get(login)
        if not user:
            log(f"  SKIP {persona_code}: user {login} not found")
            continue

        persona = Persona.search([('code', '=', persona_code)], limit=1)
        if not persona:
            log(f"  SKIP {persona_code}: persona not found in database")
            continue

        # Build persona write values
        persona_vals = {
            'user_id': user.id,
            'company_id': COMPANY_ID,
        }

        # Branch assignment
        if config['branches']:
            persona_vals['branch_ids'] = [(6, 0, config['branches'])]
        else:
            # Even personas without BU need at least some branches for the constraint
            # HR Manager and SYS_ADMIN still have branches assigned
            persona_vals['branch_ids'] = [(6, 0, config['branches'])] if config['branches'] else [(5, 0, 0)]

        # BU assignment
        if config['bus']:
            persona_vals['business_unit_ids'] = [(6, 0, config['bus'])]
        else:
            # Clear BUs if none specified
            persona_vals['business_unit_ids'] = [(5, 0, 0)]

        # Default branch
        if config['default_branch']:
            persona_vals['default_branch_id'] = config['default_branch'].id

        # Default BU
        if config['default_bu']:
            persona_vals['default_business_unit_id'] = config['default_bu'].id
        else:
            persona_vals['default_business_unit_id'] = False

        # Extra flags
        for flag_key, flag_val in config.get('extra_flags', {}).items():
            persona_vals[flag_key] = flag_val

        try:
            persona.write(persona_vals)
            log(f"  ASSIGNED: {persona_code} -> {login} "
                f"({len(config['branches'])} branches, {len(config['bus'])} BUs)")
        except Exception as e:
            log(f"  ERROR assigning {persona_code} to {login}: {e}")
            continue

        # Also ensure user has the persona in ops_persona_ids and correct matrix settings
        try:
            user_vals = {
                'ops_persona_ids': [(4, persona.id)],
                'company_id': COMPANY_ID,
                'company_ids': [(4, COMPANY_ID)],
            }
            # Set allowed branches/BUs on the user to match persona
            if config['branches']:
                user_vals['ops_allowed_branch_ids'] = [(6, 0, config['branches'])]
                user_vals['primary_branch_id'] = config['default_branch'].id if config['default_branch'] else config['branches'][0]
            if config['bus']:
                user_vals['ops_allowed_business_unit_ids'] = [(6, 0, config['bus'])]

            if config['default_branch']:
                user_vals['ops_default_branch_id'] = config['default_branch'].id
            if config['default_bu']:
                user_vals['ops_default_business_unit_id'] = config['default_bu'].id

            user.with_context(skip_ops_validation=True).write(user_vals)
            assigned_count += 1
        except Exception as e:
            log(f"  ERROR updating user {login} matrix fields: {e}")

    # ----- Process Sales Rep users (shared persona) -----
    sales_rep_persona = Persona.search([('code', '=', 'SALES_REP')], limit=1)
    if sales_rep_persona:
        first_rep = True
        for rep_config in SALES_REP_USERS:
            login = rep_config['login']
            user = created_users.get(login)
            if not user:
                log(f"  SKIP SALES_REP: user {login} not found")
                continue

            # Assign persona user_id to first rep only (Many2one constraint)
            if first_rep:
                try:
                    persona_vals = {
                        'user_id': user.id,
                        'company_id': COMPANY_ID,
                    }
                    # For the persona record itself, use the union of all rep branches/BUs
                    all_rep_branches = []
                    all_rep_bus = []
                    for rc in SALES_REP_USERS:
                        all_rep_branches.extend(rc['branches'])
                        all_rep_bus.extend(rc['bus'])
                    all_rep_branches = list(set(all_rep_branches))
                    all_rep_bus = list(set(all_rep_bus))

                    persona_vals['branch_ids'] = [(6, 0, all_rep_branches)]
                    persona_vals['business_unit_ids'] = [(6, 0, all_rep_bus)]
                    if rep_config['default_branch']:
                        persona_vals['default_branch_id'] = rep_config['default_branch'].id
                    if rep_config['default_bu']:
                        persona_vals['default_business_unit_id'] = rep_config['default_bu'].id

                    sales_rep_persona.write(persona_vals)
                    log(f"  ASSIGNED: SALES_REP persona -> {login} (primary user_id)")
                except Exception as e:
                    log(f"  ERROR assigning SALES_REP persona: {e}")
                first_rep = False

            # Add persona to user and set user-level matrix fields
            try:
                user_vals = {
                    'ops_persona_ids': [(4, sales_rep_persona.id)],
                    'company_id': COMPANY_ID,
                    'company_ids': [(4, COMPANY_ID)],
                }
                if rep_config['branches']:
                    user_vals['ops_allowed_branch_ids'] = [(6, 0, rep_config['branches'])]
                    user_vals['primary_branch_id'] = rep_config['default_branch'].id if rep_config['default_branch'] else rep_config['branches'][0]
                if rep_config['bus']:
                    user_vals['ops_allowed_business_unit_ids'] = [(6, 0, rep_config['bus'])]
                if rep_config['default_branch']:
                    user_vals['ops_default_branch_id'] = rep_config['default_branch'].id
                if rep_config['default_bu']:
                    user_vals['ops_default_business_unit_id'] = rep_config['default_bu'].id

                user.with_context(skip_ops_validation=True).write(user_vals)
                assigned_count += 1
                log(f"  ASSIGNED: SALES_REP (user matrix) -> {login} "
                    f"({len(rep_config['branches'])} branches, {len(rep_config['bus'])} BUs)")
            except Exception as e:
                log(f"  ERROR updating sales rep user {login}: {e}")
    else:
        log("  SKIP: SALES_REP persona not found in database")

    # ------------------------------------------------------------------
    # STEP 4b: IT Admin special group assignment
    # ------------------------------------------------------------------
    log("\n  Assigning IT Admin security group...")
    it_admin_user = created_users.get('it.admin@mztrading.com')
    if it_admin_user:
        try:
            it_admin_group = env.ref('ops_matrix_core.group_ops_it_admin', raise_if_not_found=False)
            if it_admin_group:
                it_admin_user.with_context(skip_ops_validation=True).write({
                    'groups_id': [(4, it_admin_group.id)],
                })
                log(f"  ADDED: IT Admin group (ID: {it_admin_group.id}) -> {it_admin_user.login}")
            else:
                log("  WARNING: group_ops_it_admin not found via env.ref")
        except Exception as e:
            log(f"  ERROR assigning IT Admin group: {e}")
    else:
        log("  SKIP: IT Admin user not found")

    # ------------------------------------------------------------------
    # STEP 4c: TECH_SUPPORT persona (no user assignment needed per spec,
    #          but included for completeness if needed later)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # STEP 5: Assign standard Odoo groups for functional access
    # ------------------------------------------------------------------
    log("\n[5/5] Assigning standard Odoo groups...")

    def ref(xml_id):
        try:
            return env.ref(xml_id)
        except Exception:
            return False

    GROUP_ASSIGNMENTS = {
        'ceo@mztrading.com': [
            'account.group_account_manager',
            'sales_team.group_sale_manager',
            'purchase.group_purchase_manager',
            'stock.group_stock_manager',
        ],
        'cfo@mztrading.com': [
            'account.group_account_manager',
            'sales_team.group_sale_manager',
            'purchase.group_purchase_manager',
            'stock.group_stock_manager',
        ],
        'fin.ctrl@mztrading.com': [
            'account.group_account_manager',
            'purchase.group_purchase_user',
        ],
        'chief.acct@mztrading.com': [
            'account.group_account_manager',
        ],
        'treasury@mztrading.com': [
            'account.group_account_user',
            'account.group_account_invoice',
        ],
        'sales.director@mztrading.com': [
            'sales_team.group_sale_manager',
            'account.group_account_invoice',
            'stock.group_stock_user',
        ],
        'sales.mgr@mztrading.com': [
            'sales_team.group_sale_manager',
            'account.group_account_invoice',
            'stock.group_stock_user',
        ],
        'sales.rep1@mztrading.com': [
            'sales_team.group_sale_salesman',
            'stock.group_stock_user',
        ],
        'sales.rep2@mztrading.com': [
            'sales_team.group_sale_salesman',
            'stock.group_stock_user',
        ],
        'purchase.mgr@mztrading.com': [
            'purchase.group_purchase_manager',
            'account.group_account_invoice',
            'stock.group_stock_user',
        ],
        'purchase.off@mztrading.com': [
            'purchase.group_purchase_user',
            'stock.group_stock_user',
        ],
        'accountant@mztrading.com': [
            'account.group_account_user',
            'account.group_account_invoice',
        ],
        'ar.clerk@mztrading.com': [
            'account.group_account_invoice',
        ],
        'ap.clerk@mztrading.com': [
            'account.group_account_invoice',
        ],
        'logistics@mztrading.com': [
            'stock.group_stock_manager',
        ],
        'log.clerk@mztrading.com': [
            'stock.group_stock_user',
        ],
        'hr.mgr@mztrading.com': [],
    }

    groups_assigned = 0
    for login, group_refs in GROUP_ASSIGNMENTS.items():
        user = created_users.get(login)
        if not user:
            continue
        if not group_refs:
            continue
        group_cmds = []
        group_names = []
        for xml_id in group_refs:
            g = ref(xml_id)
            if g:
                group_cmds.append((4, g.id))
                group_names.append(g.full_name)
        if group_cmds:
            try:
                user.sudo().write({'group_ids': group_cmds})
                log(f"  GROUPS: {login} -> {', '.join(group_names)}")
                groups_assigned += 1
            except Exception as e:
                log(f"  ERROR groups {login}: {e}")
    log(f"  Assigned Odoo groups to {groups_assigned} users")

    # ------------------------------------------------------------------
    # STEP 6: Commit
    # ------------------------------------------------------------------
    log("\n" + "=" * 70)
    log("  Committing to database...")
    env.cr.commit()
    log("  COMMITTED successfully.")

    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------
    log("\n" + "=" * 70)
    log("  SEED COMPLETE - SUMMARY")
    log("=" * 70)
    log(f"  Users created/verified: {len(created_users)}")
    log(f"  Personas assigned:      {assigned_count}")
    log("")
    log("  USER CREDENTIALS (password for all: Demo@2026)")
    log("  " + "-" * 50)
    for login, name, persona_code in USER_DEFS:
        status = "OK" if login in created_users else "MISSING"
        log(f"  {login:<35s} {name:<25s} [{persona_code}] {status}")
    log("")
    log("  Access URL: http://localhost:8089 or https://dev.mz-im.com")
    log("=" * 70)


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
try:
    main(env)  # noqa: F821 - 'env' is provided by Odoo shell
except Exception as exc:
    sys.stderr.write(f"\nFATAL ERROR: {exc}\n")
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
