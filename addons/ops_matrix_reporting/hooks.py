# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
from odoo.tools import sql


def post_init_hook(env):
    """
    Post-installation hook to create SQL views and indices.
    
    Creates:
    - PostgreSQL materialized views for analytics
    - Indices on frequently filtered columns for performance
    
    NOTE: In Odoo 19, post_init_hook receives 'env' as single argument, not (cr, registry).
    """
    # Create views by initializing the models
    # This triggers their init() methods which create the PostgreSQL views
    env['ops.sales.analysis'].init()
    env['ops.financial.analysis'].init()
    env['ops.inventory.analysis'].init()
    
    # Create indices on frequently-used filter columns for performance
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_sales_analysis_branch 
        ON ops_sales_analysis(ops_branch_id);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_sales_analysis_bu
        ON ops_sales_analysis(ops_business_unit_id);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_sales_analysis_date
        ON ops_sales_analysis(date_order);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_financial_analysis_branch
        ON ops_financial_analysis(ops_branch_id);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_financial_analysis_bu
        ON ops_financial_analysis(ops_business_unit_id);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_financial_analysis_date
        ON ops_financial_analysis(date);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_inventory_analysis_bu
        ON ops_inventory_analysis(ops_business_unit_id);
        """
    )
    
    env.cr.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_ops_inventory_analysis_location
        ON ops_inventory_analysis(location_id);
        """
    )
    
    env.cr.commit()


def uninstall_hook(cr, registry):
    """
    Uninstallation hook to clean up SQL views and indices.
    
    Removes:
    - PostgreSQL views
    - Associated indices
    """
    cr.execute(
        """
        DROP VIEW IF EXISTS ops_sales_analysis CASCADE;
        """
    )
    
    cr.execute(
        """
        DROP VIEW IF EXISTS ops_financial_analysis CASCADE;
        """
    )
    
    cr.execute(
        """
        DROP VIEW IF EXISTS ops_inventory_analysis CASCADE;
        """
    )
    
    # Drop indices (PostgreSQL will drop them automatically with CASCADE, but explicit is good)
    cr.execute(
        """
        DROP INDEX IF EXISTS idx_ops_sales_analysis_branch CASCADE;
        DROP INDEX IF EXISTS idx_ops_sales_analysis_bu CASCADE;
        DROP INDEX IF EXISTS idx_ops_sales_analysis_date CASCADE;
        DROP INDEX IF EXISTS idx_ops_financial_analysis_branch CASCADE;
        DROP INDEX IF EXISTS idx_ops_financial_analysis_bu CASCADE;
        DROP INDEX IF EXISTS idx_ops_financial_analysis_date CASCADE;
        DROP INDEX IF EXISTS idx_ops_inventory_analysis_bu CASCADE;
        DROP INDEX IF EXISTS idx_ops_inventory_analysis_location CASCADE;
        """
    )
    
    cr.commit()
