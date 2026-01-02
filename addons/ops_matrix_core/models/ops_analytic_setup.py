# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class OpsAnalyticSetup(models.TransientModel):
    _name = 'ops.analytic.setup'
    _description = 'OPS Analytic Accounting Setup Helper'
    
    def setup_analytic_structure(self):
        """Main method to ensure analytic plans and accounts are properly configured."""
        try:
            # Validate prerequisites
            self._validate_prerequisites()
            
            # Execute setup in controlled sequence with transaction safety
            with self.env.cr.savepoint():
                plans = self._ensure_analytic_plans()
                branch_count = self._sync_branch_analytic_accounts()
                bu_count = self._sync_bu_analytic_accounts()
                self._ensure_accounting_groups()
            
            # Prepare success message with details
            message_parts = [_('Analytic structure setup completed successfully.')]
            if branch_count > 0:
                message_parts.append(_('%s branch analytic accounts created.') % branch_count)
            if bu_count > 0:
                message_parts.append(_('%s business unit analytic accounts created.') % bu_count)
            
            _logger.info(f"Analytic setup completed: {branch_count} branches, {bu_count} BUs")
            
            # Return success message
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Setup Complete'),
                    'message': '\n'.join(message_parts),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except ValidationError as e:
            _logger.error(f"Validation error during analytic setup: {e}")
            raise UserError(_('Setup failed: %s') % str(e))
            
        except Exception as e:
            _logger.exception("Unexpected error during analytic setup")
            raise UserError(
                _('An unexpected error occurred during setup. Please check the logs or contact your administrator.\n\nError: %s') % str(e)
            )
    
    def _validate_prerequisites(self):
        """Validate system state before running setup."""
        # Check if user has sufficient permissions
        if not self.env.user.has_group('base.group_system'):
            if not self.env.user.has_group('ops_matrix_core.group_ops_matrix_administrator'):
                raise ValidationError(
                    _('You do not have sufficient permissions to run this setup. '
                      'Please contact a System Administrator or Matrix Administrator.')
                )
        
        # Check if accounting module is installed
        if 'account.analytic.plan' not in self.env:
            raise ValidationError(
                _('The Accounting module is not installed or not properly configured. '
                  'Please install the accounting module before running this setup.')
            )
        
        # Verify at least one company exists
        if not self.env['res.company'].search_count([]):
            raise ValidationError(_('No company found in the system. Please create at least one company.'))
        
        # Verify branches exist
        branch_count = self.env['ops.branch'].search_count([('active', '=', True)])
        if branch_count == 0:
            raise ValidationError(
                _('No active branches found. Please create at least one branch before running analytic setup.')
            )
        
        # Verify business units exist
        bu_count = self.env['ops.business.unit'].search_count([('active', '=', True)])
        if bu_count == 0:
            raise ValidationError(
                _('No active business units found. Please create at least one business unit before running analytic setup.')
            )
        
        _logger.info(f"Prerequisites validated: {branch_count} branches, {bu_count} business units")
        return True
    
    def _ensure_analytic_plans(self):
        """Create Matrix Branch and Matrix BU analytic plans if they don't exist."""
        try:
            AnalyticPlan = self.env['account.analytic.plan']
            
            # Branch Plan for tracking operational branches
            branch_plan = AnalyticPlan.search([('name', '=', 'Matrix Branch')], limit=1)
            if not branch_plan:
                branch_plan = AnalyticPlan.create({
                    'name': 'Matrix Branch',
                    'description': 'Operational Branch tracking for Matrix reporting',
                })
                _logger.info(f"Created analytic plan: Matrix Branch (ID: {branch_plan.id})")
            else:
                _logger.info(f"Using existing analytic plan: Matrix Branch (ID: {branch_plan.id})")
            
            # Business Unit Plan for tracking profit centers
            bu_plan = AnalyticPlan.search([('name', '=', 'Matrix Business Unit')], limit=1)
            if not bu_plan:
                bu_plan = AnalyticPlan.create({
                    'name': 'Matrix Business Unit',
                    'description': 'Business Unit profit center tracking',
                })
                _logger.info(f"Created analytic plan: Matrix Business Unit (ID: {bu_plan.id})")
            else:
                _logger.info(f"Using existing analytic plan: Matrix Business Unit (ID: {bu_plan.id})")
            
            # Validate plans were created/found successfully
            if not branch_plan or not bu_plan:
                raise ValidationError(
                    _('Failed to create or retrieve analytic plans. Please check system configuration.')
                )
            
            return {
                'branch_plan': branch_plan,
                'bu_plan': bu_plan,
            }
            
        except Exception as e:
            _logger.error(f"Error creating analytic plans: {e}")
            raise ValidationError(
                _('Failed to create analytic plans: %s') % str(e)
            )
    
    def _sync_branch_analytic_accounts(self):
        """Ensure all active branches have analytic accounts created."""
        try:
            Branch = self.env['ops.branch']
            AnalyticAccount = self.env['account.analytic.account']
            
            # Find branches without analytic accounts
            branches_without_analytic = Branch.search([
                ('active', '=', True),
                ('analytic_account_id', '=', False),
            ])
            
            if not branches_without_analytic:
                _logger.info("All active branches already have analytic accounts")
                return 0
            
            created_count = 0
            failed_branches = []
            
            for branch in branches_without_analytic:
                try:
                    # Validate branch data
                    if not branch.code:
                        raise ValidationError(_('Branch %s has no code defined.') % branch.name)
                    if not branch.company_id:
                        raise ValidationError(_('Branch %s has no company assigned.') % branch.name)
                    
                    # Get or create Branch analytic plan
                    branch_plan = self.env['account.analytic.plan'].search([
                        ('name', '=', 'Matrix Branch')
                    ], limit=1)
                    
                    if not branch_plan:
                        # Create plan if it doesn't exist (should not happen after _ensure_analytic_plans)
                        branch_plan = self._ensure_analytic_plans()['branch_plan']
                    
                    # Check for duplicate analytic account codes
                    existing_account = AnalyticAccount.search([
                        ('code', '=', branch.code),
                        ('plan_id', '=', branch_plan.id),
                    ], limit=1)
                    
                    if existing_account:
                        _logger.warning(
                            f"Analytic account with code {branch.code} already exists, linking to branch {branch.name}"
                        )
                        branch.analytic_account_id = existing_account.id
                        continue
                    
                    # Create analytic account for branch
                    analytic_account = AnalyticAccount.create({
                        'name': f"{branch.code} - {branch.name}",
                        'code': branch.code,
                        'plan_id': branch_plan.id,
                        'company_id': branch.company_id.id,
                        'active': True,
                    })
                    
                    # Link back to branch
                    branch.analytic_account_id = analytic_account.id
                    created_count += 1
                    _logger.info(f"Created analytic account for branch: {branch.name} (ID: {analytic_account.id})")
                    
                except Exception as e:
                    _logger.error(f"Failed to create analytic account for branch {branch.name}: {e}")
                    failed_branches.append(branch.name)
                    continue
            
            if failed_branches:
                raise ValidationError(
                    _('Failed to create analytic accounts for the following branches: %s') % ', '.join(failed_branches)
                )
            
            if created_count:
                _logger.info(f"Successfully created analytic accounts for {created_count} branches")
            
            return created_count
            
        except Exception as e:
            _logger.error(f"Error syncing branch analytic accounts: {e}")
            raise
    
    def _sync_bu_analytic_accounts(self):
        """Ensure all active business units have analytic accounts created."""
        try:
            BU = self.env['ops.business.unit']
            AnalyticAccount = self.env['account.analytic.account']
            
            # Find BUs without analytic accounts
            bus_without_analytic = BU.search([
                ('active', '=', True),
                ('analytic_account_id', '=', False),
            ])
            
            if not bus_without_analytic:
                _logger.info("All active business units already have analytic accounts")
                return 0
            
            created_count = 0
            failed_bus = []
            
            for bu in bus_without_analytic:
                try:
                    # Validate BU data
                    if not bu.code:
                        raise ValidationError(_('Business Unit %s has no code defined.') % bu.name)
                    
                    # Get primary branch for company reference
                    primary_branch = bu.primary_branch_id
                    company_id = None
                    
                    if primary_branch and primary_branch.company_id:
                        company_id = primary_branch.company_id.id
                    elif bu.branch_ids and bu.branch_ids[0].company_id:
                        company_id = bu.branch_ids[0].company_id.id
                    else:
                        company_id = self.env.company.id
                    
                    if not company_id:
                        raise ValidationError(
                            _('Business Unit %s has no associated company. '
                              'Please ensure it is linked to at least one branch with a company.') % bu.name
                        )
                    
                    # Get or create BU analytic plan
                    bu_plan = self.env['account.analytic.plan'].search([
                        ('name', '=', 'Matrix Business Unit')
                    ], limit=1)
                    
                    if not bu_plan:
                        # Create plan if it doesn't exist
                        bu_plan = self._ensure_analytic_plans()['bu_plan']
                    
                    # Check for duplicate analytic account codes
                    existing_account = AnalyticAccount.search([
                        ('code', '=', bu.code),
                        ('plan_id', '=', bu_plan.id),
                    ], limit=1)
                    
                    if existing_account:
                        _logger.warning(
                            f"Analytic account with code {bu.code} already exists, linking to BU {bu.name}"
                        )
                        bu.analytic_account_id = existing_account.id
                        continue
                    
                    # Create analytic account for BU
                    analytic_account = AnalyticAccount.create({
                        'name': f"{bu.code} - {bu.name}",
                        'code': bu.code,
                        'plan_id': bu_plan.id,
                        'company_id': company_id,
                        'active': True,
                    })
                    
                    # Link back to BU
                    bu.analytic_account_id = analytic_account.id
                    created_count += 1
                    _logger.info(f"Created analytic account for BU: {bu.name} (ID: {analytic_account.id})")
                    
                except Exception as e:
                    _logger.error(f"Failed to create analytic account for BU {bu.name}: {e}")
                    failed_bus.append(bu.name)
                    continue
            
            if failed_bus:
                raise ValidationError(
                    _('Failed to create analytic accounts for the following business units: %s') % ', '.join(failed_bus)
                )
            
            if created_count:
                _logger.info(f"Successfully created analytic accounts for {created_count} business units")
            
            return created_count
            
        except Exception as e:
            _logger.error(f"Error syncing BU analytic accounts: {e}")
            raise
    
    def _ensure_accounting_groups(self):
        """Create analytic account groups for Branch and BU if they don't exist."""
        try:
            AnalyticGroup = self.env['account.analytic.group']
            
            # Branch group
            branch_group = AnalyticGroup.search([('name', '=', 'Branches')], limit=1)
            if not branch_group:
                branch_group = AnalyticGroup.create({
                    'name': 'Branches',
                    'description': 'Operational Branches Group',
                })
            
            # Business Unit group
            bu_group = AnalyticGroup.search([('name', '=', 'Business Units')], limit=1)
            if not bu_group:
                bu_group = AnalyticGroup.create({
                    'name': 'Business Units',
                    'description': 'Business Units Profit Centers Group',
                })
            
            return {
                'branch_group': branch_group,
                'bu_group': bu_group,
            }
        except Exception as e:
            # Analytic groups may not exist in all Odoo versions
            _logger.warning(f"Could not create analytic groups: {e}")
            return {}


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    # Add fields to track linkage (optional but helpful)
    ops_branch_id = fields.Many2one('ops.branch', string='Linked Branch', readonly=True, copy=False)
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Linked Business Unit', readonly=True, copy=False)
    
    def unlink(self):
        """Prevent deletion if linked to active branch or BU."""
        Branch = self.env['ops.branch']
        BU = self.env['ops.business.unit']
        
        for account in self:
            # Check if linked to an active branch
            branch = Branch.search([
                ('analytic_account_id', '=', account.id),
                ('active', '=', True)
            ], limit=1)
            
            if branch:
                raise UserError(
                    _("Cannot delete analytic account '%(account_name)s' because it is linked to "
                      "active branch '%(branch_name)s'. Deactivate the branch first.") % {
                          'account_name': account.name,
                          'branch_name': branch.name
                      }
                )
            
            # Check if linked to an active BU
            bu = BU.search([
                ('analytic_account_id', '=', account.id),
                ('active', '=', True)
            ], limit=1)
            
            if bu:
                raise UserError(
                    _("Cannot delete analytic account '%(account_name)s' because it is linked to "
                      "active business unit '%(bu_name)s'. Deactivate the BU first.") % {
                          'account_name': account.name,
                          'bu_name': bu.name
                      }
                )
        
        return super().unlink()
