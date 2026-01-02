from odoo import _, models, fields, api
from odoo.exceptions import ValidationError

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # Note: branch_id now points to res.company (which IS the branch)
    # Most warehouses will use company_id directly, but branch_id allows
    # a warehouse to belong to a different company/branch than its main company
    branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        required=False,  # Will default to company_id
        ondelete='restrict',
        help="Branch/Company this warehouse belongs to. Defaults to warehouse's company."
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure branch_id defaults to company_id."""
        for vals in vals_list:
            if not vals.get('branch_id'):
                # Default branch_id to company_id (company IS the branch now)
                vals['branch_id'] = vals.get('company_id', self.env.company.id)
        
        return super().create(vals_list)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """When company changes, update branch_id to match."""
        if self.company_id and not self.branch_id:
            self.branch_id = self.company_id

    @api.constrains('branch_id', 'company_id')
    def _check_branch_company(self):
        """
        Ensure branch belongs to a valid company.
        Note: With the new architecture, branch_id IS a company,
        so we just verify it exists and is accessible.
        """
        for warehouse in self:
            if warehouse.branch_id and not warehouse.branch_id.active:
                raise ValidationError(_("Warehouse's branch/company must be active."))
