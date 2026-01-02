from odoo import models, api, fields

class OpsAnalyticMixin(models.AbstractModel):
    _name = 'ops.analytic.mixin'
    _description = 'Operations Analytic Account Mixin'

    analytic_account_id = fields.Many2one('account.analytic.account', 
        string='Analytic Account', 
        ondelete='restrict',
        help='Analytic account associated with this record')

    @api.model
    def _get_analytic_name_prefix(self):
        """Override in child models to set specific prefix."""
        return ""

    def write(self, vals):
        """Override to sync analytic account state and name."""
        res = super().write(vals)
        
        for record in self:
            if not record.analytic_account_id:
                continue

            analytic_vals = {}
            
            # Sync active state
            if 'active' in vals:
                analytic_vals['active'] = vals['active']
            
            # Sync name with prefix
            if 'name' in vals:
                prefix = record._get_analytic_name_prefix()
                analytic_vals['name'] = f"{prefix}{vals['name']}"
            
            if analytic_vals:
                record.analytic_account_id.write(analytic_vals)
        
        return res

    def _create_analytic_account(self, name, code, company_id=None, group_id=None):
        """Create analytic account with proper grouping.
        
        Args:
            name: Record name to use for analytic account
            code: Record code to use for analytic account
            company_id: Optional company ID
            group_id: Analytic group ID for proper hierarchy
        
        Returns:
            Created analytic account record
        """
        self.ensure_one()
        
        # Get default plan
        default_plan = self.env['account.analytic.plan'].search(
            [('parent_id', '=', False)], limit=1)
        
        if not default_plan:
            default_plan = self.env['account.analytic.plan'].create({
                'name': 'OPS Structure',
                'parent_id': False,
            })

        prefix = self._get_analytic_name_prefix()
        
        vals = {
            'name': f"{prefix}{name}",
            'code': code,
            'plan_id': default_plan.id,
            'company_id': company_id or self.env.company.id,
        }
        
        if group_id:
            vals['group_id'] = group_id

        return self.env['account.analytic.account'].create(vals)
