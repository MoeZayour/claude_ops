# -*- coding: utf-8 -*-
"""
OPS Matrix Core - User Segregation of Duties (SoD) Conflict Detection
========================================================================

Provides SoD conflict detection methods for res.users, checking for
incompatible security group memberships.

Author: OPS Matrix Framework
"""

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ResUsersSoD(models.Model):
    _inherit = 'res.users'

    # ========================================================================
    # SOD CONFLICT DETECTION METHODS
    # ========================================================================

    # Define conflicting group pairs at class level for reuse
    SOD_CONFLICT_PAIRS = [
        ('ops_matrix_core.group_ops_it_admin', 'ops_matrix_core.group_ops_admin_power',
         'IT Admin cannot have OPS Admin Power rights'),
        ('ops_matrix_core.group_ops_it_admin', 'ops_matrix_core.group_ops_see_cost',
         'IT Admin cannot see cost data'),
        ('ops_matrix_core.group_ops_it_admin', 'account.group_account_manager',
         'IT Admin cannot be Account Manager'),
        ('ops_matrix_core.group_ops_it_admin', 'purchase.group_purchase_manager',
         'IT Admin cannot be Purchase Manager'),
        ('ops_matrix_core.group_ops_it_admin', 'sales_team.group_sale_manager',
         'IT Admin cannot be Sales Manager'),
        ('ops_matrix_core.group_ops_it_admin', 'stock.group_stock_manager',
         'IT Admin cannot be Stock Manager'),
    ]

    def _compute_sod_conflicts(self):
        """
        Detect conflicting group memberships that violate Segregation of Duties.
        
        Note: No @api.depends decorator to avoid Odoo 19 dependency resolution issues
        during model loading. Field recomputation triggered manually when needed.
        """
        for user in self:
            conflicts = []
            user_groups = user.group_ids

            for group1_ref, group2_ref, conflict_desc in self.SOD_CONFLICT_PAIRS:
                try:
                    group1 = self.env.ref(group1_ref, raise_if_not_found=False)
                    group2 = self.env.ref(group2_ref, raise_if_not_found=False)

                    if group1 and group2 and user_groups:
                        if group1 in user_groups and group2 in user_groups:
                            conflicts.append(conflict_desc)
                except Exception:
                    _logger.debug('Failed to check SoD conflict pair %s / %s', group1_ref, group2_ref, exc_info=True)
                    # Skip if groups don't exist (module not installed)
                    pass

            user.has_sod_conflict = bool(conflicts)
            user.sod_conflict_count = len(conflicts)
            user.sod_conflicts = '\n'.join(conflicts) if conflicts else ''

    def check_and_log_sod_conflicts(self):
        """
        Check and log SoD conflicts for the user.

        Call this method after modifying group memberships to log conflicts.
        """
        for user in self:
            # Force recomputation
            user._compute_sod_conflicts()

            if user.has_sod_conflict and user.sod_conflicts:
                # Log to SoD violation log if the model exists
                try:
                    self.env['ops.segregation.of.duties.log'].sudo().create({
                        'user_id': user.id,
                        'violation_type': 'group_conflict',
                        'description': f"SoD Conflict Detected:\n{user.sod_conflicts}",
                        'detected_by_id': self.env.user.id,
                        'action_taken': 'logged',
                    })
                    _logger.warning(
                        "SoD conflict detected for user %s: %s",
                        user.login,
                        user.sod_conflicts.replace('\n', '; ')
                    )
                except Exception as e:
                    # Model might not exist or have different fields
                    _logger.warning(
                        "Could not log SoD conflict for user %s: %s",
                        user.login, str(e)
                    )
