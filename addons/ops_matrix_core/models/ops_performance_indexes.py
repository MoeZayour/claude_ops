# -*- coding: utf-8 -*-
"""
Performance Optimization: Database Indexes
This module adds critical indexes to improve query performance for the OPS Matrix framework.
"""
from odoo import models, tools, _
import logging

_logger = logging.getLogger(__name__)


class OpsPerformanceIndexes(models.AbstractModel):
    """Add performance indexes to critical OPS Matrix fields."""
    _name = 'ops.performance.indexes'
    _description = 'OPS Performance Index Management'
    
    def _auto_init(self):
        """Create indexes on critical fields for performance optimization."""
        res = super()._auto_init()
        
        # Define indexes to create
        # Format: (table_name, column_name, index_name)
        indexes = [
            # Sale Order indexes
            ('sale_order', 'ops_branch_id', 'idx_sale_order_ops_branch'),
            ('sale_order', 'ops_business_unit_id', 'idx_sale_order_ops_bu'),
            ('sale_order', 'date_order', 'idx_sale_order_date'),
            ('sale_order', 'state', 'idx_sale_order_state'),
            
            # Sale Order Line indexes
            ('sale_order_line', 'ops_branch_id', 'idx_sol_ops_branch'),
            ('sale_order_line', 'ops_business_unit_id', 'idx_sol_ops_bu'),
            ('sale_order_line', 'product_id', 'idx_sol_product'),
            
            # Purchase Order indexes
            ('purchase_order', 'ops_branch_id', 'idx_po_ops_branch'),
            ('purchase_order', 'ops_business_unit_id', 'idx_po_ops_bu'),
            ('purchase_order', 'date_order', 'idx_po_date_order'),
            ('purchase_order', 'state', 'idx_po_state'),
            
            # Account Move (Invoice) indexes
            ('account_move', 'ops_branch_id', 'idx_account_move_ops_branch'),
            ('account_move', 'ops_business_unit_id', 'idx_account_move_ops_bu'),
            ('account_move', 'date', 'idx_account_move_date'),
            ('account_move', 'invoice_date', 'idx_account_move_invoice_date'),
            ('account_move', 'move_type', 'idx_account_move_type'),
            ('account_move', 'state', 'idx_account_move_state'),
            
            # Account Move Line indexes
            ('account_move_line', 'ops_branch_id', 'idx_aml_ops_branch'),
            ('account_move_line', 'ops_business_unit_id', 'idx_aml_ops_bu'),
            ('account_move_line', 'date', 'idx_aml_date'),
            ('account_move_line', 'account_id', 'idx_aml_account'),
            ('account_move_line', 'product_id', 'idx_aml_product'),
            
            # Stock Picking indexes
            ('stock_picking', 'ops_branch_id', 'idx_stock_picking_ops_branch'),
            ('stock_picking', 'scheduled_date', 'idx_stock_picking_scheduled_date'),
            ('stock_picking', 'state', 'idx_stock_picking_state'),
            ('stock_picking', 'picking_type_id', 'idx_stock_picking_type'),
            
            # Stock Move indexes
            ('stock_move', 'ops_branch_id', 'idx_stock_move_ops_branch'),
            ('stock_move', 'product_id', 'idx_stock_move_product'),
            ('stock_move', 'location_id', 'idx_stock_move_location'),
            ('stock_move', 'location_dest_id', 'idx_stock_move_location_dest'),
            ('stock_move', 'state', 'idx_stock_move_state'),
            
            # Stock Quant indexes
            ('stock_quant', 'location_id', 'idx_stock_quant_location'),
            ('stock_quant', 'product_id', 'idx_stock_quant_product'),
            ('stock_quant', 'ops_business_unit_id', 'idx_stock_quant_ops_bu'),
            
            # Product Template indexes
            ('product_template', 'business_unit_id', 'idx_product_template_bu'),
            ('product_template', 'categ_id', 'idx_product_template_categ'),
            
            # Product Product indexes
            ('product_product', 'default_code', 'idx_product_product_default_code'),
            
            # OPS Branch indexes
            ('ops_branch', 'code', 'idx_ops_branch_code'),
            ('ops_branch', 'active', 'idx_ops_branch_active'),
            
            # OPS Business Unit indexes
            ('ops_business_unit', 'code', 'idx_ops_bu_code'),
            ('ops_business_unit', 'active', 'idx_ops_bu_active'),
            
            # OPS Approval Request indexes
            ('ops_approval_request', 'branch_id', 'idx_approval_branch'),
            ('ops_approval_request', 'business_unit_id', 'idx_approval_bu'),
            ('ops_approval_request', 'state', 'idx_approval_state'),
            ('ops_approval_request', 'requested_date', 'idx_approval_date'),
            
            # OPS Governance Rule indexes
            ('ops_governance_rule', 'ops_branch_id', 'idx_gov_rule_branch'),
            ('ops_governance_rule', 'ops_business_unit_id', 'idx_gov_rule_bu'),
            ('ops_governance_rule', 'active', 'idx_gov_rule_active'),
            
            # OPS Persona indexes
            ('ops_persona', 'user_id', 'idx_persona_user'),
            ('ops_persona', 'active', 'idx_persona_active'),
            
            # Composite indexes disabled - create manually after installation if needed
            # ('sale_order', 'ops_branch_id, ops_business_unit_id', 'idx_so_branch_bu_composite'),
            # ('sale_order', 'date_order, state', 'idx_so_date_state_composite'),
            # ('purchase_order', 'ops_branch_id, ops_business_unit_id', 'idx_po_branch_bu_composite'),
            # ('account_move', 'ops_branch_id, ops_business_unit_id', 'idx_am_branch_bu_composite'),
            # ('account_move', 'date, state', 'idx_am_date_state_composite'),
        ]
        
        cr = self.env.cr
        
        for table, column, index_name in indexes:
            try:
                # Check if table exists
                cr.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                if not cr.fetchone()[0]:
                    _logger.debug(f"Table {table} does not exist, skipping index {index_name}")
                    continue
                
                # Check if column exists (for composite indexes, skip this check)
                if ',' not in column:
                    cr.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = %s 
                            AND column_name = %s
                        );
                    """, (table, column))
                    
                    if not cr.fetchone()[0]:
                        _logger.debug(f"Column {column} does not exist in table {table}, skipping index {index_name}")
                        continue
                
                # Check if index already exists
                cr.execute("""
                    SELECT EXISTS (
                        SELECT FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND tablename = %s 
                        AND indexname = %s
                    );
                """, (table, index_name))
                
                if cr.fetchone()[0]:
                    _logger.debug(f"Index {index_name} already exists on {table}.{column}")
                    continue
                
                # Create index
                query = f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} ON {table} ({column})"
                _logger.info(f"Creating index: {query}")
                
                # Note: CONCURRENTLY requires being outside a transaction block
                # In module installation, we can't use CONCURRENTLY, so we use regular CREATE INDEX
                query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({column})"
                cr.execute(query)
                _logger.info(f"Successfully created index {index_name} on {table}.{column}")
                
            except Exception as e:
                _logger.warning(f"Failed to create index {index_name} on {table}.{column}: {e}")
                # Continue with other indexes even if one fails
                continue
        
        return res


class SaleOrder(models.Model):
    """Add index hints to sale.order model."""
    _inherit = 'sale.order'
    
    def init(self):
        """Ensure indexes exist on sale.order."""
        super().init()
        # Indexes are created by OpsPerformanceIndexes


class PurchaseOrder(models.Model):
    """Add index hints to purchase.order model."""
    _inherit = 'purchase.order'
    
    def init(self):
        """Ensure indexes exist on purchase.order."""
        super().init()
        # Indexes are created by OpsPerformanceIndexes


class AccountMove(models.Model):
    """Add index hints to account.move model."""
    _inherit = 'account.move'
    
    def init(self):
        """Ensure indexes exist on account.move."""
        super().init()
        # Indexes are created by OpsPerformanceIndexes


class StockPicking(models.Model):
    """Add index hints to stock.picking model."""
    _inherit = 'stock.picking'
    
    def init(self):
        """Ensure indexes exist on stock.picking."""
        super().init()
        # Indexes are created by OpsPerformanceIndexes
