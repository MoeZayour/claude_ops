# -*- coding: utf-8 -*-
"""
OPS Matrix Core - User Authority & Access Control
====================================================

Provides matrix access control methods, persona-based authority checking,
and delegation integration for res.users.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResUsersAuthority(models.Model):
    _inherit = 'res.users'

    # ========================================================================
    # ACCESS CONTROL METHODS
    # ========================================================================

    def get_effective_matrix_access(self):
        """
        Returns computed access based on user's direct assignments and personas.
        Consolidated view of all access rights.
        """
        self.ensure_one()

        # If system administrator, grant all access
        if self.has_group('base.group_system'):
            return {
                'companies': self.env['res.company'].search([]),
                'branches': self.env['ops.branch'].search([]),
                'business_units': self.env['ops.business.unit'].search([]),
            }

        # Start with direct assignments
        companies = self.company_ids
        branches = self.ops_allowed_branch_ids
        business_units = self.ops_allowed_business_unit_ids

        # Add access from personas (if persona module exists and is installed)
        if hasattr(self, 'persona_ids'):
            for persona in self.persona_ids.filtered(lambda p: p.active):
                # Add persona's allowed branches
                if hasattr(persona, 'branch_ids'):
                    branches |= persona.branch_ids

                # Add persona's allowed business units
                if hasattr(persona, 'business_unit_ids'):
                    business_units |= persona.business_unit_ids

        # For cross-branch BU leaders, get all branches where their BUs operate
        if self.is_cross_branch_bu_leader and business_units:
            # Get all branches where allowed BUs operate
            bu_branches = business_units.mapped('branch_ids')
            branches |= bu_branches

        # Derive companies from branches (if not already set)
        if branches and not companies:
            companies = branches.mapped('company_id')

        return {
            'companies': companies,
            'branches': branches,
            'business_units': business_units,
        }

    def can_access_branch(self, branch_id):
        """Check if user can access specific branch."""
        self.ensure_one()

        # System administrators can access everything
        if self.has_group('base.group_system'):
            return True

        # Get effective access
        effective_access = self.get_effective_matrix_access()

        # Check if branch is in allowed branches
        branch = self.env['ops.branch'].browse(branch_id)
        if not branch.exists():
            return False

        # Company-level access: if user has company access, they can see all branches in that company
        if branch.company_id.id in effective_access['companies'].ids:
            return True

        # Branch-level access
        return branch_id in effective_access['branches'].ids

    def can_access_business_unit(self, bu_id):
        """Check if user can access specific business unit."""
        self.ensure_one()

        # System administrators can access everything
        if self.has_group('base.group_system'):
            return True

        # Get effective access
        effective_access = self.get_effective_matrix_access()

        # Check if BU is in allowed BUs
        bu = self.env['ops.business.unit'].browse(bu_id)
        if not bu.exists():
            return False

        # Company-level access: if user has company access, they can see all BUs in that company
        bu_companies = bu.branch_ids.mapped('company_id')
        if any(company.id in effective_access['companies'].ids for company in bu_companies):
            return True

        # BU-level access
        return bu_id in effective_access['business_units'].ids

    def can_access_matrix_combination(self, branch_id, bu_id):
        """
        Check if user can access specific branch-BU combination.
        Useful for transaction validation.
        """
        self.ensure_one()

        # System administrators can access everything
        if self.has_group('base.group_system'):
            return True

        # Check individual access
        if not self.can_access_branch(branch_id):
            return False

        if not self.can_access_business_unit(bu_id):
            return False

        # For cross-branch BU leaders: special handling
        if self.is_cross_branch_bu_leader:
            # Cross-branch BU leaders can access their BUs in any branch
            allowed_bus = self.get_effective_matrix_access()['business_units']
            return bu_id in allowed_bus.ids

        # Regular users: BU must operate in the branch
        bu = self.env['ops.business.unit'].browse(bu_id)
        branch = self.env['ops.branch'].browse(branch_id)

        return branch in bu.branch_ids

    # ========================================================================
    # SEGREGATION OF DUTIES (SoD) AUTHORITY CHECKING
    # ========================================================================

    def has_authority(self, authority_field):
        """
        Check if user has specific authority based on ANY of their effective personas.
        Returns True if ANY active persona has the authority flag set to True.
        Includes both own personas and delegated personas.

        :param authority_field: Name of the authority field (e.g., 'can_validate_invoices')
        :return: Boolean
        """
        self.ensure_one()

        # System administrators bypass all checks
        if self.has_group('base.group_system'):
            return True

        # Get all effective personas (own + delegated) using the central method
        effective_personas = self.get_effective_personas()

        if not effective_personas:
            return False

        for persona in effective_personas:
            if hasattr(persona, authority_field) and getattr(persona, authority_field):
                return True

        return False

    def get_effective_personas(self):
        """
        Get all personas effective for this user, including:
        - User's own active personas
        - Personas from active delegations TO this user

        This is the central method for determining what authorities a user has,
        considering both direct persona assignments and delegations.

        Returns: recordset of ops.persona records
        """
        self.ensure_one()
        now = fields.Datetime.now()

        # Start with user's own active personas
        effective_personas = self.ops_persona_ids.filtered(
            lambda p: p.active and getattr(p, 'is_active_today', True)
        )

        # Find active delegations TO this user
        Delegation = self.env['ops.persona.delegation']
        try:
            active_delegations = Delegation.sudo().search([
                ('delegate_id', '=', self.id),
                ('active', '=', True),
                ('start_date', '<=', now),
                '|',
                ('end_date', '=', False),
                ('end_date', '>=', now),
            ])

            if active_delegations:
                _logger.debug(
                    f"User {self.name} (ID: {self.id}) has {len(active_delegations)} active delegations"
                )
                # Get the specific delegated personas (not all delegator personas)
                for delegation in active_delegations:
                    if delegation.persona_id and delegation.persona_id.active:
                        effective_personas |= delegation.persona_id
                        _logger.debug(
                            f"User {self.name} inherited persona '{delegation.persona_id.name}' "
                            f"via delegation from {delegation.delegator_id.name}"
                        )

        except Exception as e:
            _logger.warning(f"Could not check delegations for user {self.name}: {e}")

        return effective_personas

    def has_ops_authority(self, field_name):
        """
        Cumulative Authority Logic Helper: Check if ANY of the user's effective personas
        grants a specific authority. Includes both own personas AND delegated personas.

        :param field_name: Name of the boolean authority field on ops.persona model
        :return: Boolean
        """
        self.ensure_one()

        # System administrators bypass all authority checks
        if self.has_group('base.group_system'):
            return True

        # Get all effective personas (own + delegated)
        effective_personas = self.get_effective_personas()

        # Handle case: No effective personas
        if not effective_personas:
            _logger.debug(
                f"User {self.name} (ID: {self.id}) has no effective personas. "
                f"Authority check for '{field_name}' returns False."
            )
            return False

        # Defensive check: Verify field exists on persona model
        persona_model = self.env['ops.persona']
        if field_name not in persona_model._fields:
            _logger.warning(
                f"Authority field '{field_name}' does not exist on ops.persona model. "
                f"Authority check for user {self.name} (ID: {self.id}) returns False."
            )
            return False

        # Use any() for efficient cumulative authority check
        try:
            has_authority = any(
                getattr(persona, field_name, False)
                for persona in effective_personas
            )

            if has_authority:
                _logger.debug(
                    f"User {self.name} (ID: {self.id}) has authority '{field_name}' "
                    f"via one or more effective personas."
                )

            return has_authority

        except Exception as e:
            _logger.error(
                f"Error checking authority '{field_name}' for user {self.name} (ID: {self.id}): {e}"
            )
            return False

    def can_modify_product_master(self):
        """Check if user can modify product master data (cost, suppliers)."""
        return self.has_authority('can_modify_product_master')

    def can_access_cost_prices(self):
        """Check if user can access/view product cost prices."""
        return self.has_authority('can_access_cost_prices')

    def can_validate_invoices(self):
        """Check if user can validate and post invoices."""
        return self.has_authority('can_validate_invoices')

    def can_post_journal_entries(self):
        """Check if user can post accounting journal entries."""
        return self.has_authority('can_post_journal_entries')

    def can_execute_payments(self):
        """Check if user can execute vendor payments."""
        return self.has_authority('can_execute_payments')

    def can_adjust_inventory(self):
        """Check if user can post inventory adjustments."""
        return self.has_authority('can_adjust_inventory')

    def can_manage_pdc(self):
        """Check if user can manage Post Dated Checks."""
        return self.has_authority('can_manage_pdc')

    # ========================================================================
    # PERSONA INTEGRATION & DELEGATION
    # ========================================================================

    def _get_effective_persona(self):
        """Get the effective persona considering delegations."""
        self.ensure_one()
        now = fields.Datetime.now()

        # Check if there's an active delegation TO this user
        delegation = self.env['ops.persona.delegation'].search([
            ('delegate_id', '=', self.id),
            ('active', '=', True),
            ('start_date', '<=', now),
            '|',
            ('end_date', '=', False),
            ('end_date', '>=', now),
        ], limit=1)

        if delegation:
            return delegation.persona_id

        # Return user's own persona
        return self.persona_id

    def get_delegation_info_for_authority(self, authority_field):
        """
        Check if user has authority via delegation and return delegation info.

        :param authority_field: Name of the authority field on ops.persona
        :return: dict with delegation info or None if authority is direct
        """
        self.ensure_one()

        # System admins don't need delegation
        if self.has_group('base.group_system'):
            return None

        # Check if user has this authority directly
        direct_personas = self.ops_persona_ids.filtered(
            lambda p: p.active and getattr(p, 'is_active_today', True)
        )
        for persona in direct_personas:
            if hasattr(persona, authority_field) and getattr(persona, authority_field):
                return None  # Direct authority, not delegation

        # Check if user has this authority via delegation
        now = fields.Datetime.now()
        Delegation = self.env['ops.persona.delegation']

        try:
            active_delegations = Delegation.sudo().search([
                ('delegate_id', '=', self.id),
                ('active', '=', True),
                ('start_date', '<=', now),
                '|',
                ('end_date', '=', False),
                ('end_date', '>=', now),
            ])

            for delegation in active_delegations:
                persona = delegation.persona_id
                if persona and persona.active:
                    if hasattr(persona, authority_field) and getattr(persona, authority_field):
                        return {
                            'delegation': delegation,
                            'delegator': delegation.delegator_id,
                            'persona': persona,
                        }

        except Exception as e:
            _logger.warning(f"Could not check delegation authority for user {self.name}: {e}")

        return None

    def check_authority_with_delegation_audit(self, authority_field):
        """
        Check if user has authority and return info about how (direct or delegated).

        :param authority_field: Name of the authority field on ops.persona
        :return: dict with keys: has_authority, is_delegated, delegation_info, persona
        """
        self.ensure_one()

        # System admins bypass all checks
        if self.has_group('base.group_system'):
            return {
                'has_authority': True,
                'is_delegated': False,
                'delegation_info': None,
                'persona': None,
            }

        # First check direct authority
        direct_personas = self.ops_persona_ids.filtered(
            lambda p: p.active and getattr(p, 'is_active_today', True)
        )
        for persona in direct_personas:
            if hasattr(persona, authority_field) and getattr(persona, authority_field):
                return {
                    'has_authority': True,
                    'is_delegated': False,
                    'delegation_info': None,
                    'persona': persona,
                }

        # Then check delegated authority
        delegation_info = self.get_delegation_info_for_authority(authority_field)
        if delegation_info:
            return {
                'has_authority': True,
                'is_delegated': True,
                'delegation_info': delegation_info,
                'persona': delegation_info['persona'],
            }

        return {
            'has_authority': False,
            'is_delegated': False,
            'delegation_info': None,
            'persona': None,
        }
