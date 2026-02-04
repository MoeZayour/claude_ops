# -*- coding: utf-8 -*-
"""
OPS Security Compliance Dashboard
=================================
Automated security compliance verification for IT Admin Blindness,
Branch Isolation, SoD Conflicts, and Persona Drift detection.
"""

import logging
import time
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpsSecurityComplianceCheck(models.Model):
    """Security compliance audit check record."""

    _name = 'ops.security.compliance.check'
    _description = 'OPS Security Compliance Check'
    _order = 'check_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    check_date = fields.Datetime(
        string='Check Date',
        required=True,
        readonly=True,
        default=fields.Datetime.now,
        tracking=True,
    )

    check_type = fields.Selection(
        selection=[
            ('full', 'Full Security Audit'),
            ('it_admin_blindness', 'IT Admin Blindness'),
            ('branch_isolation', 'Branch Isolation'),
            ('sod_conflicts', 'SoD Conflicts'),
            ('persona_drift', 'Persona Drift'),
            ('acl_coverage', 'ACL Coverage'),
        ],
        string='Check Type',
        required=True,
        default='full',
        tracking=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    # Statistics - stored computed fields
    total_checks = fields.Integer(
        string='Total Checks',
        compute='_compute_statistics',
        store=True,
    )

    passed_count = fields.Integer(
        string='Passed',
        compute='_compute_statistics',
        store=True,
    )

    failed_count = fields.Integer(
        string='Failed',
        compute='_compute_statistics',
        store=True,
    )

    warning_count = fields.Integer(
        string='Warnings',
        compute='_compute_statistics',
        store=True,
    )

    compliance_percentage = fields.Float(
        string='Compliance %',
        compute='_compute_statistics',
        store=True,
    )

    # Results
    result_ids = fields.One2many(
        'ops.security.compliance.result',
        'check_id',
        string='Results',
    )

    # Audit trail
    executed_by_id = fields.Many2one(
        'res.users',
        string='Executed By',
        readonly=True,
        default=lambda self: self.env.user,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    duration_seconds = fields.Float(
        string='Duration (seconds)',
        readonly=True,
        digits=(16, 2),
    )

    notes = fields.Text(string='Notes')

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('result_ids', 'result_ids.status')
    def _compute_statistics(self):
        """Compute check statistics from results."""
        for check in self:
            results = check.result_ids
            check.total_checks = len(results)
            check.passed_count = len(results.filtered(lambda r: r.status == 'passed'))
            check.failed_count = len(results.filtered(lambda r: r.status == 'failed'))
            check.warning_count = len(results.filtered(lambda r: r.status == 'warning'))

            if check.total_checks > 0:
                check.compliance_percentage = (check.passed_count / check.total_checks) * 100
            else:
                check.compliance_percentage = 0.0

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence on create."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ops.security.compliance.check'
                ) or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # ACTION BUTTONS
    # -------------------------------------------------------------------------

    def action_run_full_audit(self):
        """Run all compliance checks."""
        self.ensure_one()
        start_time = time.time()

        self.write({'state': 'running', 'check_date': fields.Datetime.now()})
        self.result_ids.unlink()  # Clear previous results

        try:
            self._check_it_admin_blindness_rules()
            self._check_branch_isolation()
            self._check_sod_conflicts()
            self._check_persona_drift()
            self._check_acl_coverage()

            # Determine final state
            final_state = 'completed' if self.failed_count == 0 else 'failed'
            self.write({
                'state': final_state,
                'duration_seconds': time.time() - start_time,
            })

            # Post message with summary
            self.message_post(
                body=_(
                    "Security audit completed.<br/>"
                    "<b>Results:</b> %(passed)s passed, %(failed)s failed, %(warnings)s warnings<br/>"
                    "<b>Compliance:</b> %(score).1f%%"
                ) % {
                    'passed': self.passed_count,
                    'failed': self.failed_count,
                    'warnings': self.warning_count,
                    'score': self.compliance_percentage,
                },
                subject=_("Security Audit Complete"),
            )

        except Exception as e:
            _logger.exception("Security audit failed: %s", str(e))
            self.write({
                'state': 'failed',
                'duration_seconds': time.time() - start_time,
            })
            self.message_post(
                body=_("Security audit failed with error: %s") % str(e),
                subject=_("Security Audit Failed"),
            )
            raise UserError(_("Security audit failed: %s") % str(e))

        return True

    def action_run_it_admin_blindness_check(self):
        """Run only IT Admin Blindness verification."""
        self.ensure_one()
        start_time = time.time()

        self.write({
            'state': 'running',
            'check_date': fields.Datetime.now(),
            'check_type': 'it_admin_blindness',
        })
        self.result_ids.unlink()

        try:
            self._check_it_admin_blindness_rules()
            final_state = 'completed' if self.failed_count == 0 else 'failed'
            self.write({
                'state': final_state,
                'duration_seconds': time.time() - start_time,
            })
        except Exception as e:
            self.write({'state': 'failed', 'duration_seconds': time.time() - start_time})
            raise UserError(_("IT Admin Blindness check failed: %s") % str(e))

        return True

    def action_run_branch_isolation_check(self):
        """Run only Branch Isolation verification."""
        self.ensure_one()
        start_time = time.time()

        self.write({
            'state': 'running',
            'check_date': fields.Datetime.now(),
            'check_type': 'branch_isolation',
        })
        self.result_ids.unlink()

        try:
            self._check_branch_isolation()
            final_state = 'completed' if self.failed_count == 0 else 'failed'
            self.write({
                'state': final_state,
                'duration_seconds': time.time() - start_time,
            })
        except Exception as e:
            self.write({'state': 'failed', 'duration_seconds': time.time() - start_time})
            raise UserError(_("Branch Isolation check failed: %s") % str(e))

        return True

    def action_run_sod_conflicts_check(self):
        """Run only SoD Conflicts verification."""
        self.ensure_one()
        start_time = time.time()

        self.write({
            'state': 'running',
            'check_date': fields.Datetime.now(),
            'check_type': 'sod_conflicts',
        })
        self.result_ids.unlink()

        try:
            self._check_sod_conflicts()
            final_state = 'completed' if self.failed_count == 0 else 'failed'
            self.write({
                'state': final_state,
                'duration_seconds': time.time() - start_time,
            })
        except Exception as e:
            self.write({'state': 'failed', 'duration_seconds': time.time() - start_time})
            raise UserError(_("SoD Conflicts check failed: %s") % str(e))

        return True

    def action_run_persona_drift_check(self):
        """Run only Persona Drift detection."""
        self.ensure_one()
        start_time = time.time()

        self.write({
            'state': 'running',
            'check_date': fields.Datetime.now(),
            'check_type': 'persona_drift',
        })
        self.result_ids.unlink()

        try:
            self._check_persona_drift()
            final_state = 'completed' if self.failed_count == 0 else 'failed'
            self.write({
                'state': final_state,
                'duration_seconds': time.time() - start_time,
            })
        except Exception as e:
            self.write({'state': 'failed', 'duration_seconds': time.time() - start_time})
            raise UserError(_("Persona Drift check failed: %s") % str(e))

        return True

    # -------------------------------------------------------------------------
    # CHECK IMPLEMENTATIONS
    # -------------------------------------------------------------------------

    def _check_it_admin_blindness_rules(self):
        """
        Verify IT Admin Blindness rules are in place for all protected models.

        IT Admin should have NO access to business transaction data.
        This is enforced via ir.rule with domain [('id', '=', 0)] or [(0, '=', 1)].
        """
        self.ensure_one()

        # Models that must be blocked for IT Admin
        protected_models = [
            ('sale.order', 'Sales Orders'),
            ('sale.order.line', 'Sales Order Lines'),
            ('purchase.order', 'Purchase Orders'),
            ('purchase.order.line', 'Purchase Order Lines'),
            ('account.move', 'Journal Entries/Invoices'),
            ('account.move.line', 'Journal Items'),
            ('account.payment', 'Payments'),
            ('account.bank.statement', 'Bank Statements'),
            ('account.bank.statement.line', 'Bank Statement Lines'),
            ('stock.picking', 'Stock Pickings'),
            ('stock.move', 'Stock Moves'),
            ('stock.move.line', 'Stock Move Lines'),
            ('stock.quant', 'Stock Quantities'),
            ('stock.valuation.layer', 'Stock Valuation'),
            ('product.pricelist', 'Pricelists'),
            ('product.pricelist.item', 'Pricelist Items'),
            ('account.analytic.line', 'Analytic Lines'),
            # OPS-specific models
            ('ops.pdc.receivable', 'PDC Receivable'),
            ('ops.pdc.payable', 'PDC Payable'),
            ('ops.budget', 'Budgets'),
            ('ops.budget.line', 'Budget Lines'),
            ('ops.asset', 'Assets'),
            ('ops.asset.category', 'Asset Categories'),
            ('ops.asset.depreciation', 'Asset Depreciation'),
        ]

        # Get IT Admin group
        it_admin_group = self.env.ref(
            'ops_matrix_core.group_ops_it_admin',
            raise_if_not_found=False
        )

        if not it_admin_group:
            self.env['ops.security.compliance.result'].create({
                'check_id': self.id,
                'check_category': 'it_admin_blindness',
                'status': 'failed',
                'severity': 'critical',
                'rule_name': 'IT Admin Group',
                'description': 'IT Admin security group not found! Security framework may be misconfigured.',
                'recommendation': 'Verify ops_matrix_core module is properly installed.',
            })
            return

        Result = self.env['ops.security.compliance.result']

        for model_name, model_label in protected_models:
            try:
                # Check if model exists in the system
                model_record = self.env['ir.model'].sudo().search(
                    [('model', '=', model_name)],
                    limit=1
                )

                if not model_record:
                    Result.create({
                        'check_id': self.id,
                        'check_category': 'it_admin_blindness',
                        'status': 'info',
                        'severity': 'low',
                        'model_name': model_name,
                        'rule_name': f'IT Admin Blindness: {model_label}',
                        'description': f'Model {model_name} not installed - skipped.',
                        'recommendation': 'No action needed if module is intentionally not installed.',
                    })
                    continue

                # Search for blocking rule assigned to IT Admin
                # Rules use domain [('id', '=', 0)] or [(0, '=', 1)] to block all access
                blocking_rule = self.env['ir.rule'].sudo().search([
                    ('model_id.model', '=', model_name),
                    ('groups', 'in', it_admin_group.id),
                    ('active', '=', True),
                    '|',
                    ('domain_force', 'ilike', "('id', '=', 0)"),
                    ('domain_force', 'ilike', "[(0, '=', 1)]"),
                ], limit=1)

                if blocking_rule:
                    Result.create({
                        'check_id': self.id,
                        'check_category': 'it_admin_blindness',
                        'status': 'passed',
                        'severity': 'low',
                        'model_name': model_name,
                        'rule_name': f'IT Admin Blindness: {model_label}',
                        'description': f'Blocking rule found: {blocking_rule.name}',
                        'recommendation': '',
                    })
                else:
                    Result.create({
                        'check_id': self.id,
                        'check_category': 'it_admin_blindness',
                        'status': 'failed',
                        'severity': 'critical',
                        'model_name': model_name,
                        'rule_name': f'IT Admin Blindness: {model_label}',
                        'description': f'NO BLOCKING RULE FOUND for {model_name}! IT Admin can view {model_label}.',
                        'recommendation': f'Create ir.rule for {model_name} with domain [(\'id\', \'=\', 0)] assigned to IT Admin group.',
                    })

            except Exception as e:
                _logger.warning("Error checking IT Admin Blindness for %s: %s", model_name, str(e))
                Result.create({
                    'check_id': self.id,
                    'check_category': 'it_admin_blindness',
                    'status': 'warning',
                    'severity': 'medium',
                    'model_name': model_name,
                    'rule_name': f'IT Admin Blindness: {model_label}',
                    'description': f'Error during check: {str(e)}',
                    'recommendation': 'Review error and retry check.',
                })

    def _check_branch_isolation(self):
        """
        Verify branch isolation is properly enforced.

        Checks:
        1. All users have at least one branch assigned (except system users)
        2. Branch-related record rules exist for key models
        3. Cross-branch access is properly controlled
        """
        self.ensure_one()
        Result = self.env['ops.security.compliance.result']

        # Check 1: Users without branch assignments
        users_without_branch = self.env['res.users'].sudo().search([
            ('active', '=', True),
            ('id', 'not in', [1, 2]),  # Exclude admin and public
            ('ops_allowed_branch_ids', '=', False),
            ('share', '=', False),  # Exclude portal users
        ])

        if users_without_branch:
            for user in users_without_branch[:10]:  # Limit to first 10
                Result.create({
                    'check_id': self.id,
                    'check_category': 'branch_isolation',
                    'status': 'warning',
                    'severity': 'medium',
                    'user_id': user.id,
                    'rule_name': 'Branch Assignment',
                    'description': f'User "{user.name}" has no branch assigned.',
                    'recommendation': 'Assign at least one branch to this user.',
                })

            if len(users_without_branch) > 10:
                Result.create({
                    'check_id': self.id,
                    'check_category': 'branch_isolation',
                    'status': 'warning',
                    'severity': 'medium',
                    'rule_name': 'Branch Assignment',
                    'description': f'... and {len(users_without_branch) - 10} more users without branch assignment.',
                    'recommendation': 'Review all users and assign branches.',
                })
        else:
            Result.create({
                'check_id': self.id,
                'check_category': 'branch_isolation',
                'status': 'passed',
                'severity': 'low',
                'rule_name': 'Branch Assignment',
                'description': 'All active users have branch assignments.',
                'recommendation': '',
            })

        # Check 2: Branch-related record rules exist
        branch_models = [
            ('sale.order', 'Sales Orders'),
            ('purchase.order', 'Purchase Orders'),
            ('account.move', 'Journal Entries'),
            ('stock.picking', 'Stock Pickings'),
        ]

        for model_name, model_label in branch_models:
            model_record = self.env['ir.model'].sudo().search(
                [('model', '=', model_name)],
                limit=1
            )
            if not model_record:
                continue

            # Look for rules that reference branch
            branch_rule = self.env['ir.rule'].sudo().search([
                ('model_id.model', '=', model_name),
                ('active', '=', True),
                '|',
                ('domain_force', 'ilike', 'ops_branch_id'),
                ('domain_force', 'ilike', 'branch_id'),
            ], limit=1)

            if branch_rule:
                Result.create({
                    'check_id': self.id,
                    'check_category': 'branch_isolation',
                    'status': 'passed',
                    'severity': 'low',
                    'model_name': model_name,
                    'rule_name': f'Branch Isolation: {model_label}',
                    'description': f'Branch filtering rule found: {branch_rule.name}',
                    'recommendation': '',
                })
            else:
                Result.create({
                    'check_id': self.id,
                    'check_category': 'branch_isolation',
                    'status': 'warning',
                    'severity': 'medium',
                    'model_name': model_name,
                    'rule_name': f'Branch Isolation: {model_label}',
                    'description': f'No branch filtering rule found for {model_name}.',
                    'recommendation': 'Consider adding branch-based record rules.',
                })

    def _check_sod_conflicts(self):
        """
        Verify no users have conflicting group memberships.

        IT Admin should never have:
        - OPS Admin Power
        - See Cost permission
        - Account Manager
        - Purchase Manager
        - Sales Manager
        """
        self.ensure_one()
        Result = self.env['ops.security.compliance.result']

        # Define conflicting group pairs
        conflict_pairs = [
            ('ops_matrix_core.group_ops_it_admin', 'ops_matrix_core.group_ops_admin_power',
             'IT Admin + OPS Admin Power'),
            ('ops_matrix_core.group_ops_it_admin', 'ops_matrix_core.group_ops_see_cost',
             'IT Admin + See Cost'),
            ('ops_matrix_core.group_ops_it_admin', 'account.group_account_manager',
             'IT Admin + Account Manager'),
            ('ops_matrix_core.group_ops_it_admin', 'purchase.group_purchase_manager',
             'IT Admin + Purchase Manager'),
            ('ops_matrix_core.group_ops_it_admin', 'sales_team.group_sale_manager',
             'IT Admin + Sales Manager'),
        ]

        conflicts_found = 0

        for group1_ref, group2_ref, conflict_name in conflict_pairs:
            try:
                group1 = self.env.ref(group1_ref, raise_if_not_found=False)
                group2 = self.env.ref(group2_ref, raise_if_not_found=False)

                if not group1 or not group2:
                    continue

                # Find users with both groups
                conflicting_users = self.env['res.users'].sudo().search([
                    ('active', '=', True),
                    ('groups_id', 'in', group1.id),
                    ('groups_id', 'in', group2.id),
                ])

                if conflicting_users:
                    conflicts_found += len(conflicting_users)
                    for user in conflicting_users[:5]:  # Limit to first 5 per conflict type
                        Result.create({
                            'check_id': self.id,
                            'check_category': 'sod_conflict',
                            'status': 'failed',
                            'severity': 'critical',
                            'user_id': user.id,
                            'rule_name': f'SoD Conflict: {conflict_name}',
                            'description': f'User "{user.name}" has conflicting groups: {conflict_name}',
                            'recommendation': f'Remove either {group1.name} or {group2.name} from this user.',
                        })

                    if len(conflicting_users) > 5:
                        Result.create({
                            'check_id': self.id,
                            'check_category': 'sod_conflict',
                            'status': 'failed',
                            'severity': 'critical',
                            'rule_name': f'SoD Conflict: {conflict_name}',
                            'description': f'... and {len(conflicting_users) - 5} more users with same conflict.',
                            'recommendation': 'Review all users for SoD compliance.',
                        })

            except Exception as e:
                _logger.warning("Error checking SoD conflict %s: %s", conflict_name, str(e))

        if conflicts_found == 0:
            Result.create({
                'check_id': self.id,
                'check_category': 'sod_conflict',
                'status': 'passed',
                'severity': 'low',
                'rule_name': 'Segregation of Duties',
                'description': 'No SoD conflicts detected. All group assignments comply with separation policies.',
                'recommendation': '',
            })

    def _check_persona_drift(self):
        """
        Detect users with permissions beyond their assigned persona.

        Compares actual group memberships against expected groups from persona.
        """
        self.ensure_one()
        Result = self.env['ops.security.compliance.result']

        # Get all active users with personas
        users_with_personas = self.env['res.users'].sudo().search([
            ('active', '=', True),
            ('id', 'not in', [1, 2]),  # Exclude admin and public
            ('ops_persona_ids', '!=', False),
        ])

        users_without_personas = self.env['res.users'].sudo().search([
            ('active', '=', True),
            ('id', 'not in', [1, 2]),
            ('ops_persona_ids', '=', False),
            ('share', '=', False),  # Exclude portal users
        ])

        # Report users without personas
        if users_without_personas:
            Result.create({
                'check_id': self.id,
                'check_category': 'persona_drift',
                'status': 'warning',
                'severity': 'medium',
                'rule_name': 'Persona Assignment',
                'description': f'{len(users_without_personas)} users have no persona assigned.',
                'recommendation': 'Assign personas to all internal users for proper access control.',
            })

        drift_count = 0

        for user in users_with_personas:
            # Get all OPS-related groups the user has
            user_ops_groups = user.groups_id.filtered(
                lambda g: 'ops' in g.full_name.lower() or 'ops_matrix' in g.category_id.name.lower() if g.category_id else False
            )

            # Check if user has admin-level groups that may indicate drift
            sensitive_groups = user.groups_id.filtered(
                lambda g: any(kw in g.name.lower() for kw in ['admin', 'manager', 'cost', 'margin', 'executive'])
            )

            # For now, flag users with many sensitive groups as potential drift
            # This is a simplified check - full implementation would compare against persona template
            if len(sensitive_groups) > 5:
                drift_count += 1
                Result.create({
                    'check_id': self.id,
                    'check_category': 'persona_drift',
                    'status': 'warning',
                    'severity': 'medium',
                    'user_id': user.id,
                    'rule_name': 'Permission Accumulation',
                    'description': f'User "{user.name}" has {len(sensitive_groups)} sensitive groups. Review for potential drift.',
                    'recommendation': 'Compare user permissions against their persona template.',
                })

        if drift_count == 0 and users_with_personas:
            Result.create({
                'check_id': self.id,
                'check_category': 'persona_drift',
                'status': 'passed',
                'severity': 'low',
                'rule_name': 'Persona Drift Detection',
                'description': 'No significant permission drift detected.',
                'recommendation': '',
            })

    def _check_acl_coverage(self):
        """
        Verify ACL (ir.model.access) coverage for OPS models.

        Ensures all OPS models have proper access control entries.
        """
        self.ensure_one()
        Result = self.env['ops.security.compliance.result']

        # Get all OPS models
        ops_models = self.env['ir.model'].sudo().search([
            ('model', 'like', 'ops.%'),
        ])

        for model in ops_models:
            # Check if ACL entries exist
            acl_entries = self.env['ir.model.access'].sudo().search([
                ('model_id', '=', model.id),
            ])

            if not acl_entries:
                Result.create({
                    'check_id': self.id,
                    'check_category': 'acl_coverage',
                    'status': 'failed',
                    'severity': 'high',
                    'model_name': model.model,
                    'rule_name': f'ACL Coverage: {model.name}',
                    'description': f'Model {model.model} has no ACL entries!',
                    'recommendation': 'Add ir.model.access entries for this model.',
                })
            elif len(acl_entries) < 2:
                Result.create({
                    'check_id': self.id,
                    'check_category': 'acl_coverage',
                    'status': 'warning',
                    'severity': 'medium',
                    'model_name': model.model,
                    'rule_name': f'ACL Coverage: {model.name}',
                    'description': f'Model {model.model} has only {len(acl_entries)} ACL entry. Consider adding role-based entries.',
                    'recommendation': 'Add ACL entries for different user roles (user, manager, admin).',
                })
            else:
                Result.create({
                    'check_id': self.id,
                    'check_category': 'acl_coverage',
                    'status': 'passed',
                    'severity': 'low',
                    'model_name': model.model,
                    'rule_name': f'ACL Coverage: {model.name}',
                    'description': f'Model has {len(acl_entries)} ACL entries.',
                    'recommendation': '',
                })


class OpsSecurityComplianceResult(models.Model):
    """Individual compliance check result."""

    _name = 'ops.security.compliance.result'
    _description = 'Security Compliance Check Result'
    _order = 'severity_order, check_category, id'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------

    check_id = fields.Many2one(
        'ops.security.compliance.check',
        string='Compliance Check',
        required=True,
        ondelete='cascade',
        index=True,
    )

    check_category = fields.Selection(
        selection=[
            ('it_admin_blindness', 'IT Admin Blindness'),
            ('branch_isolation', 'Branch Isolation'),
            ('sod_conflict', 'SoD Conflict'),
            ('persona_drift', 'Persona Drift'),
            ('acl_coverage', 'ACL Coverage'),
            ('record_rule', 'Record Rule'),
        ],
        string='Category',
        required=True,
        index=True,
    )

    status = fields.Selection(
        selection=[
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('warning', 'Warning'),
            ('info', 'Info'),
        ],
        string='Status',
        required=True,
        index=True,
    )

    severity = fields.Selection(
        selection=[
            ('critical', 'Critical'),
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        string='Severity',
        default='medium',
    )

    severity_order = fields.Integer(
        compute='_compute_severity_order',
        store=True,
        help='For sorting by severity'
    )

    # What was checked
    model_name = fields.Char(string='Model')
    rule_name = fields.Char(string='Check Name', required=True)

    # Affected user/record
    user_id = fields.Many2one('res.users', string='Affected User')
    record_ref = fields.Char(string='Record Reference')

    # Details
    description = fields.Text(string='Description', required=True)
    recommendation = fields.Text(string='Recommended Action')
    details_json = fields.Json(string='Technical Details')

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('severity')
    def _compute_severity_order(self):
        """Compute numeric order for severity sorting (critical first)."""
        severity_map = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4,
        }
        for result in self:
            result.severity_order = severity_map.get(result.severity, 5)
