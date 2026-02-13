from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
    MIGRATION DISABLED - Model refactoring from ops.branch to res.company.
    
    This migration is no longer applicable as ops.branch model has been removed.
    Branch functionality is now inherited directly into res.company.
    
    After DB reset, res.company records will automatically have OPS fields.
    """
    pass
    
    # LEGACY CODE (for reference):
    # Previously, this migration:
    # 1. Ensured all branches had analytic accounts
    # 2. Ensured all warehouses had branches
    # 3. Set NOT NULL constraints on these fields
    #
    # New approach:
    # - res.company will auto-generate OPS codes and analytic accounts
    # - Warehouses will link to res.company via company_id
    # - No special migration needed as it's native Odoo behavior
