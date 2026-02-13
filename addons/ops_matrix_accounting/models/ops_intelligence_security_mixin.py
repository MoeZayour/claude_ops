# -*- coding: utf-8 -*-
"""
OPS Matrix Intelligence Security Mixin
======================================

Security mixin for all Four Pillars Intelligence wizards.
Enforces IT Admin Blindness, Branch Isolation, and Audit Logging.

Key Security Features:
- IT Admin Blindness: Absolute block on accessing intelligence reports
- Branch Isolation: Users can only see data from their allowed branches
- Persona Validation: Role-based access control
- Audit Logging: Silent compliance tracking

Author: OPS Matrix Framework
Version: 1.0 (Four Pillars Enhancement)
"""

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsIntelligenceSecurityMixin(models.AbstractModel):
    """
    Security mixin for all Four Pillars Intelligence wizards.
    Enforces IT Admin Blindness, Branch Isolation, and Audit Logging.

    Usage:
        In wizard, call: self._check_intelligence_access('Financial')
        Before any data query or report generation.
    """
    _name = 'ops.intelligence.security.mixin'
    _description = 'Intelligence Report Security Mixin'

    def _check_intelligence_access(self, pillar_name='Report'):
        """
        Validate user can access intelligence reports.
        Must be called before ANY data query or report generation.

        Args:
            pillar_name: Name of the pillar for error messages
                         One of: 'Financial', 'Treasury', 'Asset', 'Inventory'

        Raises:
            AccessError: If user is blocked from accessing reports

        Returns:
            True if access is granted
        """
        user = self.env.user

        # =====================================================================
        # IT ADMIN BLINDNESS - ABSOLUTE BLOCK
        # =====================================================================
        # IT Administrators can manage users, configure system, view logs
        # but they CANNOT access any financial/intelligence data

        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            _logger.warning(
                f"IT Admin access BLOCKED for {pillar_name} Intelligence: "
                f"User {user.login} (ID: {user.id})"
            )
            raise AccessError(_(
                "Access Denied: IT Administrators cannot access %s Intelligence reports.\n\n"
                "This restriction is enforced by OPS Framework security policy.\n\n"
                "IT Administrators have full access to:\n"
                "• User Management\n"
                "• System Configuration\n"
                "• Technical Settings\n"
                "• Audit Logs\n\n"
                "But CANNOT access financial or operational data.\n"
                "Contact your CFO or System Administrator if you believe this is an error."
            ) % pillar_name)

        # =====================================================================
        # SYSTEM ADMIN / CFO BYPASS
        # =====================================================================
        # These roles have unrestricted access to all pillars

        if user.has_group('base.group_system'):
            return True

        if user.has_group('ops_matrix_core.group_ops_cfo'):
            return True

        # =====================================================================
        # PERSONA VALIDATION
        # =====================================================================
        # Define which personas can access each pillar
        # P00=System Admin, P01=IT Admin, P02=Executive, P03=CFO, P04=Controller, etc.

        pillar_access = {
            'Financial': [
                'P00',  # System Admin
                'P02',  # Executive
                'P03',  # CFO
                'P04',  # Controller
                'P05',  # Finance Manager
                'P06',  # Accountant
                'P07',  # AR/AP Clerk
                'P09',  # Branch Manager
                'P13',  # Auditor
                'P14',  # Board Member
                'P15',  # Partner
                'P16',  # Operations Manager
            ],
            'Treasury': [
                'P00',  # System Admin
                'P03',  # CFO
                'P04',  # Controller
                'P05',  # Finance Manager
                'P09',  # Branch Manager
                'P13',  # Auditor
                'P14',  # Board Member
                'P15',  # Partner
                'P16',  # Operations Manager
            ],
            'Asset': [
                'P00',  # System Admin
                'P03',  # CFO
                'P04',  # Controller
                'P05',  # Finance Manager
                'P08',  # Asset Manager
                'P09',  # Branch Manager
                'P16',  # Operations Manager
            ],
            'Inventory': [
                'P00',  # System Admin
                'P03',  # CFO
                'P04',  # Controller
                'P05',  # Finance Manager
                'P07',  # Clerk
                'P08',  # Warehouse Manager
                'P12',  # Inventory Manager
                'P16',  # Operations Manager
            ],
        }

        allowed_personas = pillar_access.get(pillar_name, [])
        user_persona = user.ops_persona_id.code if hasattr(user, 'ops_persona_id') and user.ops_persona_id else None

        # Executive group also has broad access
        if user.has_group('ops_matrix_core.group_ops_executive'):
            return True

        # Manager group has broad access
        if user.has_group('ops_matrix_core.group_ops_manager'):
            return True

        # Check persona-based access (if persona system is active)
        if user_persona and user_persona not in allowed_personas:
            _logger.warning(
                f"Persona access BLOCKED for {pillar_name} Intelligence: "
                f"User {user.login} with persona {user_persona}"
            )
            raise AccessError(_(
                "Access Denied: Your role (%s) does not permit access to %s Intelligence reports.\n\n"
                "Contact your administrator if you require access to this data."
            ) % (user_persona, pillar_name))

        return True

    def _get_branch_filter_domain(self, branch_field='ops_branch_id'):
        """
        Build branch isolation domain based on user access level.

        This ensures users only see data from branches they have access to.

        Args:
            branch_field: Name of the branch field to filter on

        Returns:
            list: Domain filter for branch isolation
        """
        user = self.env.user

        # =====================================================================
        # FULL ACCESS ROLES - No branch restriction
        # =====================================================================
        if user.has_group('base.group_system'):
            return []

        if user.has_group('ops_matrix_core.group_ops_cfo'):
            return []

        if user.has_group('ops_matrix_core.group_ops_executive'):
            return []

        # =====================================================================
        # BU LEADER - Access to all branches in their Business Units
        # =====================================================================
        if user.has_group('ops_matrix_core.group_ops_bu_leader'):
            if hasattr(user, 'ops_business_unit_ids') and user.ops_business_unit_ids:
                bu_branches = user.ops_business_unit_ids.mapped('branch_ids')
                if bu_branches:
                    return [(branch_field, 'in', bu_branches.ids)]
            # BU Leader with no BUs assigned = no access
            return [(branch_field, '=', False)]

        # =====================================================================
        # MANAGER - Full access to all branches
        # =====================================================================
        if user.has_group('ops_matrix_core.group_ops_manager'):
            return []

        # =====================================================================
        # STANDARD USER - Only allowed branches
        # =====================================================================
        if hasattr(user, 'ops_allowed_branch_ids') and user.ops_allowed_branch_ids:
            return [(branch_field, 'in', user.ops_allowed_branch_ids.ids)]

        # Fallback - no branch access means no data
        # This prevents accidental full access
        return [(branch_field, '=', False)]

    def _validate_branch_access(self, requested_branch_ids):
        """
        Validate user has access to all requested branches.

        Call this when user explicitly selects branches in the wizard
        to ensure they can't request data from branches they shouldn't see.

        Args:
            requested_branch_ids: Recordset of ops.branch

        Raises:
            AccessError: If user doesn't have access to any requested branch

        Returns:
            True if all branches are accessible
        """
        if not requested_branch_ids:
            return True

        user = self.env.user

        # Full access roles can access any branch
        if user.has_group('base.group_system'):
            return True
        if user.has_group('ops_matrix_core.group_ops_cfo'):
            return True
        if user.has_group('ops_matrix_core.group_ops_executive'):
            return True
        if user.has_group('ops_matrix_core.group_ops_manager'):
            return True

        # BU Leader - check BU branches
        if user.has_group('ops_matrix_core.group_ops_bu_leader'):
            if hasattr(user, 'ops_business_unit_ids') and user.ops_business_unit_ids:
                allowed = user.ops_business_unit_ids.mapped('branch_ids')
            else:
                allowed = self.env['ops.branch']
        else:
            # Standard user - use allowed_branch_ids
            if hasattr(user, 'ops_allowed_branch_ids'):
                allowed = user.ops_allowed_branch_ids
            else:
                allowed = self.env['ops.branch']

        # Find branches user requested but doesn't have access to
        invalid = requested_branch_ids - allowed
        if invalid:
            invalid_names = ', '.join(invalid.mapped('name'))
            _logger.warning(
                f"Branch access DENIED: User {user.login} requested unauthorized "
                f"branches: {invalid_names}"
            )
            raise AccessError(_(
                "Access Denied: You don't have access to the following branch(es):\n\n"
                "• %s\n\n"
                "Please select only branches you are authorized to access, "
                "or contact your administrator for expanded access."
            ) % invalid_names)

        return True

    def _log_intelligence_report(self, pillar, report_type, filters_dict, output_format='pdf'):
        """
        Create audit trail entry for intelligence report generation.

        This is "The Black Box" - silent compliance logging that tracks
        all reporting activity without blocking execution if logging fails.

        Args:
            pillar: Pillar name (Financial, Treasury, Asset, Inventory)
            report_type: Specific report type within the pillar
            filters_dict: Dictionary of filters applied
            output_format: Output format (pdf, excel, screen)
        """
        try:
            # Use the existing ops.report.audit model if available
            if 'ops.report.audit' in self.env:
                self.env['ops.report.audit'].sudo().log_report(
                    engine=pillar.lower(),
                    report_name=f"{pillar} Intelligence - {report_type}",
                    report_type=report_type,
                    parameters=filters_dict,
                    export_format=output_format,
                    wizard_model=self._name,
                    record_count=filters_dict.get('record_count', 0),
                )
            else:
                _logger.info(
                    f"Intelligence Report Generated: {pillar}/{report_type} "
                    f"by {self.env.user.login} - Format: {output_format}"
                )
        except Exception as e:
            # CRITICAL: Never fail report generation due to audit logging failure
            _logger.error(f"Audit logging failed (non-blocking): {e}")

    def _get_good_size_threshold(self, pillar_name='Report'):
        """
        Get the threshold for "Good size" indicator.

        Reports with fewer records than this threshold get a green "Good size" badge.
        Reports with more get an orange "Large dataset" warning.

        Args:
            pillar_name: Pillar name for context-specific thresholds

        Returns:
            int: Threshold count for "good size"
        """
        thresholds = {
            'Financial': 10000,  # Journal entries can be many
            'Treasury': 500,     # PDCs are typically fewer
            'Asset': 1000,       # Assets are typically fewer
            'Inventory': 5000,   # Stock items can be many
        }
        return thresholds.get(pillar_name, 5000)

    def _get_size_indicator(self, record_count, pillar_name='Report'):
        """
        Get size indicator for display in wizard.

        Returns a dict with:
        - label: Display text
        - css_class: CSS class for styling
        - is_good: Boolean for "good size" or not

        Args:
            record_count: Number of records matching filters
            pillar_name: Pillar name for threshold lookup

        Returns:
            dict: Size indicator info
        """
        threshold = self._get_good_size_threshold(pillar_name)

        if record_count == 0:
            return {
                'label': 'No records',
                'css_class': 'text-muted',
                'is_good': False,
                'is_warning': False,
            }
        elif record_count <= threshold:
            return {
                'label': 'Good size',
                'css_class': 'text-success',
                'is_good': True,
                'is_warning': False,
            }
        elif record_count <= threshold * 2:
            return {
                'label': 'Large dataset',
                'css_class': 'text-warning',
                'is_good': False,
                'is_warning': True,
            }
        else:
            return {
                'label': 'Very large',
                'css_class': 'text-danger',
                'is_good': False,
                'is_warning': True,
            }
