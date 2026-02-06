# -*- coding: utf-8 -*-
"""
OPS Matrix Core - Persona-to-Group Mapping & Auto-Sync
=========================================================

Provides automatic security group synchronization based on persona
assignments and role-based group mapping for res.users.

Author: OPS Matrix Framework
"""

from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class ResUsersGroupMapper(models.Model):
    _inherit = 'res.users'

    # ========================================================================
    # GROUP SYNCHRONIZATION
    # ========================================================================

    @api.depends('group_ids')
    def _compute_matrix_roles_from_groups(self):
        """Sync group membership with role boolean fields."""
        matrix_admin_group = self.env.ref('ops_matrix_core.group_ops_matrix_administrator', False)
        cross_branch_group = self.env.ref('ops_matrix_core.group_ops_cross_branch_bu_leader', False)

        for user in self:
            if matrix_admin_group:
                user.is_matrix_administrator = matrix_admin_group in user.group_ids
            if cross_branch_group:
                user.is_cross_branch_bu_leader = cross_branch_group in user.group_ids

    @api.onchange('is_matrix_administrator')
    def _onchange_is_matrix_administrator(self):
        """Update group membership when role changes."""
        # Skip if record not yet created (group_ids not available on new records in onchange)
        if not self.id:
            return
        matrix_admin_group = self.env.ref('ops_matrix_core.group_ops_matrix_administrator', False)
        if matrix_admin_group:
            if self.is_matrix_administrator:
                self.group_ids = [(4, matrix_admin_group.id)]
            else:
                self.group_ids = [(3, matrix_admin_group.id)]

    @api.onchange('is_cross_branch_bu_leader')
    def _onchange_is_cross_branch_bu_leader(self):
        """Update group membership when role changes."""
        # Skip if record not yet created (group_ids not available on new records in onchange)
        if not self.id:
            return
        cross_branch_group = self.env.ref('ops_matrix_core.group_ops_cross_branch_bu_leader', False)
        if cross_branch_group:
            if self.is_cross_branch_bu_leader:
                self.group_ids = [(4, cross_branch_group.id)]
            else:
                self.group_ids = [(3, cross_branch_group.id)]

    # ========================================================================
    # PERSONA AUTO-SYNC: ZERO-FRICTION SETUP
    # ========================================================================

    @api.onchange('persona_id')
    def _onchange_persona_id(self):
        """
        AUTO-SYNC LOGIC: When a persona is assigned:
        1. Auto-add persona to ops_persona_ids (prevents validation errors before save)
        2. Auto-populate Primary Branch (use company's first branch)
        3. Auto-map Odoo 19 security groups based on persona
        4. Prevent "Primary Branch is missing" error
        """
        for user in self:
            if not user.persona_id:
                continue

            # Step 1: AUTO-ADD persona to ops_persona_ids (CRITICAL for validation)
            if user.persona_id not in user.ops_persona_ids:
                user.ops_persona_ids = [(4, user.persona_id.id)]
                _logger.info(f"Auto-added persona '{user.persona_id.name}' to ops_persona_ids for user {user.name}")

            # Step 2: Auto-populate Primary Branch if empty
            if not user.primary_branch_id:
                # First try to use first allowed branch
                if user.ops_allowed_branch_ids:
                    user.primary_branch_id = user.ops_allowed_branch_ids[0]
                    _logger.info(f"Auto-populated Primary Branch from allowed branches for user {user.name}: {user.primary_branch_id.name}")
                else:
                    # Fallback: Find the first branch in the user's company
                    main_branch = self.env['ops.branch'].search([
                        ('company_id', '=', user.company_id.id),
                        ('active', '=', True)
                    ], limit=1, order='sequence, id')

                    if main_branch:
                        user.primary_branch_id = main_branch
                        _logger.info(f"Auto-populated Primary Branch for user {user.name}: {main_branch.name}")

            # Step 3: Auto-map security groups based on persona code
            user._map_persona_to_groups()

    def _map_persona_to_groups(self):
        """
        Map persona to Odoo 19 security groups automatically.
        This is the "Zero-Friction" setup logic.
        """
        self.ensure_one()

        if not self.persona_id:
            return

        persona_code = self.persona_id.code
        groups_to_add = []

        # Persona -> Group Mapping
        persona_group_map = {
            'CEO': [
                'base.group_erp_manager',  # Access Rights
                'sales_team.group_sale_manager',  # Sales Manager
                'account.group_account_manager',  # Billing Manager
                'stock.group_stock_manager',  # Inventory Manager
                'ops_matrix_core.group_ops_executive',  # OPS Executive
                'ops_matrix_core.group_ops_matrix_administrator',  # Matrix Admin
            ],
            'CFO': [
                'account.group_account_manager',  # Billing Manager
                'account.group_account_user',  # Billing
                'ops_matrix_core.group_ops_executive',  # OPS Executive
                'ops_matrix_core.group_ops_cost_controller',  # Cost Controller
            ],
            'SALES_LEADER': [
                'sales_team.group_sale_manager',  # Sales Manager
                'sale.group_sale_manager',  # Administrator
                'ops_matrix_core.group_ops_bu_leader',  # BU Leader
            ],
            'SALES_MGR': [
                'sales_team.group_sale_manager',  # Sales Manager
                'sale.group_sale_salesman_all_leads',  # See All Leads
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'SALES_REP': [
                'sales_team.group_sale_salesman',  # User: Own Documents Only
                'sale.group_sale_salesman',  # User: Own Documents Only
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'HR_MGR': [
                'hr.group_hr_manager',  # Officer (if HR installed)
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'CHIEF_ACCT': [
                'account.group_account_manager',  # Billing Manager
                'account.group_account_user',  # Billing
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'FIN_MGR': [
                'account.group_account_manager',  # Accounting Manager (full invoicing)
                'account.group_account_invoice',  # Invoicing access
                'account.group_account_user',  # Accounting features
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'ACCOUNTANT': [
                'account.group_account_user',  # Billing
                'account.group_account_invoice',  # Billing
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'LOG_MGR': [
                'stock.group_stock_manager',  # Inventory Manager
                'ops_matrix_core.group_ops_branch_manager',  # Branch Manager
                'ops_matrix_core.group_ops_manager',  # OPS Manager
            ],
            'LOG_CLERK': [
                'stock.group_stock_user',  # User
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'TECH_SUPPORT': [
                'base.group_user',  # Internal User
                'ops_matrix_core.group_ops_user',  # OPS User
            ],
            'SYS_ADMIN': [
                'base.group_system',  # Settings
                'ops_matrix_core.group_ops_matrix_administrator',  # Matrix Admin
            ],
        }

        # Get groups for this persona
        group_xmlids = persona_group_map.get(persona_code, [])

        for xmlid in group_xmlids:
            try:
                group = self.env.ref(xmlid, raise_if_not_found=False)
                if group:
                    groups_to_add.append(group.id)
            except Exception as e:
                _logger.warning(f"Could not find group {xmlid}: {e}")

        # Add groups to user
        if groups_to_add:
            self.group_ids = [(4, gid) for gid in groups_to_add]
            _logger.info(f"Auto-mapped {len(groups_to_add)} groups to user {self.name} based on persona {persona_code}")
