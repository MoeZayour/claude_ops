from odoo import models, fields, api

class OpsProductCategory(models.Model):
    _inherit = 'product.category'

    # Override inventory valuation fields to enforce defaults
    property_cost_method = fields.Selection(
        default='fifo',
        readonly=True,
        help="FIFO costing method enforced by Matrix Operations"
    )
    
    property_valuation = fields.Selection(
        default='real_time',
        readonly=True,
        help="Real-time valuation enforced by Matrix Operations"
    )

    @api.constrains('property_cost_method', 'property_valuation')
    def _check_accounting_fields_not_empty(self):
        """Ensure costing and valuation methods are always set."""
        for record in self:
            if not record.property_cost_method:
                record.property_cost_method = 'fifo'
            if not record.property_valuation:
                record.property_valuation = 'real_time'

    @api.model
    def default_get(self, fields_list):
        """Override to auto-populate accounting fields with smart defaults."""
        defaults = super().default_get(fields_list)
        
        try:
            company = self.env.company
            account_obj = self.env['account.account']

            # Helper function to find accounts - simplified for Odoo 19 compatibility
            def find_account(fallback_type=None):
                if fallback_type:
                    try:
                        account = account_obj.search([
                            ('account_type', '=', fallback_type)
                        ], limit=1)
                        return account.id if account else False
                    except Exception:
                        pass
                return False

            # 1. Income Account (Sales)
            if 'property_account_income_categ_id' in fields_list:
                income_account = find_account(fallback_type='income')
                defaults['property_account_income_categ_id'] = income_account

            # 2. Expense Account (COGS)
            if 'property_account_expense_categ_id' in fields_list:
                expense_account = find_account(fallback_type='expense')
                defaults['property_account_expense_categ_id'] = expense_account

            # 3. Stock Valuation Account
            if 'property_stock_valuation_account_id' in fields_list:
                valuation_account = find_account(fallback_type='asset_current')
                defaults['property_stock_valuation_account_id'] = valuation_account

            # 4. Stock Input Account
            if 'property_stock_account_input_categ_id' in fields_list:
                input_account = find_account(fallback_type='asset_current')
                defaults['property_stock_account_input_categ_id'] = input_account

            # 5. Stock Output Account
            if 'property_stock_account_output_categ_id' in fields_list:
                output_account = find_account(fallback_type='asset_current')
                defaults['property_stock_account_output_categ_id'] = output_account

        except Exception:
            # Gracefully fall back if account lookup fails
            pass

        return defaults


class OpsProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields_list):
        """Ensure products inherit category defaults properly."""
        defaults = super().default_get(fields_list)
        
        # If no category specified, find or create the default category
        if not defaults.get('categ_id'):
            default_category = self.env['product.category'].search([
                ('name', '=', 'All'),
                ('parent_id', '=', False)
            ], limit=1)
            
            if not default_category:
                default_category = self.env['product.category'].create({
                    'name': 'All'
                })
            
            defaults['categ_id'] = default_category.id
        
        return defaults

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        """Ensure accounting fields are properly inherited from category."""
        if self.categ_id:
            self.property_account_income_id = False  # Force inherit from category
            self.property_account_expense_id = False  # Force inherit from category
