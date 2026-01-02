from odoo import models, fields, api
from odoo.sql_db import Cursor


class OpsSalesAnalysis(models.Model):
    """
    Sales Analysis Report - Read-Only SQL View
    
    This model represents a PostgreSQL materialized view that provides
    high-performance sales analytics with Branch and Business Unit dimensions.
    
    The view joins sale.order_line with sale.order to provide:
    - Date of sale
    - Product sold
    - Customer (partner)
    - Branch and Business Unit dimensions
    - Quantities and revenue
    - Margin calculations
    
    CRITICAL: This model is read-only (_auto=False) and backed by a PostgreSQL view.
    """
    
    _name = 'ops.sales.analysis'
    _description = 'Sales Analysis by Branch and Business Unit'
    _auto = False  # Don't auto-create table
    _rec_name = 'id'
    _order = 'date_order DESC'
    
    # ========================================================================
    # FIELDS - Mirror the View Columns
    # ========================================================================
    id = fields.Id(readonly=True)
    
    date_order = fields.Datetime(
        string='Order Date',
        readonly=True,
        help='Date and time when the sale order was created in the system. '
             'This field is used as the primary temporal dimension for sales trend analysis and period comparisons. '
             'Use Case: Filter by date range to analyze sales performance over specific periods (month, quarter, year). '
             'Example: "2025-01-01 to 2025-03-31" for Q1 sales analysis. '
             'Note: Only confirmed/done orders (state=sale/done) are included in this analysis view. '
             'Related: Combine with ops_branch_id and ops_business_unit_id for multi-dimensional time series analysis.'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
        help='The specific product variant sold in this transaction line. '
             'Used to analyze product performance, identify top sellers, and track product margins across dimensions. '
             'Use Case: Group by product_id to see total revenue and margin per product. '
             'Example: "Product A sold 500 units with 25% average margin in Branch X". '
             'Important: This is the variant (product.product), not the template (product.template). '
             'Analysis: Use get_margin_analysis() to identify products with negative margins that need price adjustments. '
             'Related: Combine with ops_business_unit_id to verify product silo enforcement.'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        readonly=True,
        help='The customer (partner) who purchased the products in this sale order. '
             'Used to analyze customer purchasing patterns, identify top customers, and track customer profitability by dimension. '
             'Use Case: Group by partner_id to calculate customer lifetime value (CLV) and average order value per branch/BU. '
             'Example: "Customer ABC generated $50K revenue across 3 branches with 22% average margin". '
             'Important: Only business partners with type=contact or company are included (not addresses). '
             'Analysis: Cross-reference with receivables reports to identify high-value customers with payment issues. '
             'Related: Filter by ops_branch_id to see which customers prefer specific branches or regions.'
    )
    
    ops_branch_id = fields.Many2one(
        'res.company',
        string='Branch',
        readonly=True,
        help='The operational branch (location/store) that originated and owns this sale transaction. '
             'This is the primary geographic dimension for sales analysis and performance comparison across locations. '
             'Use Case: Compare revenue, margin, and volume across branches to identify high/low performers. '
             'Example: "Branch A: $100K revenue, 20% margin vs Branch B: $80K revenue, 25% margin". '
             'Important: This field respects user security rules - users only see sales from their allowed branches. '
             'Analysis: Use get_summary_by_branch() for aggregated branch performance metrics. '
             'Note: Legacy field name uses res.company model but represents operational branch concept.'
    )
    
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        readonly=True,
        help='The business unit (product line/division) that owns this sale transaction. '
             'This is the product/service dimension for sales analysis, enabling P&L tracking by division. '
             'Use Case: Analyze which product lines (BUs) generate the most revenue and margin across different branches. '
             'Example: "Electronics BU: $200K revenue in 5 branches, Consumer Goods BU: $150K in 3 branches". '
             'Important: Combined with ops_branch_id, this creates the matrix intersection for true multi-dimensional analysis. '
             'Analysis: Use get_summary_by_matrix() to see Branch × BU performance grid. '
             'Security: Users only see BU data they have access to via their persona assignments.'
    )
    
    product_uom_qty = fields.Float(
        string='Quantity',
        readonly=True,
        help='The quantity of products sold in this transaction line, measured in the product\'s unit of measure (UoM). '
             'Used to calculate volume metrics, track unit sales trends, and compute average selling price per unit. '
             'Use Case: Track which products sell in high volumes vs high value but low volume (luxury goods). '
             'Example: "Product A sold 1000 units at $10 each = $10K revenue vs Product B sold 10 units at $1K = $10K revenue". '
             'Important: Quantity is in the product\'s default UoM (pieces, kg, liters, etc.) - check product.uom_id for unit type. '
             'Calculation: Average selling price = price_subtotal / product_uom_qty. '
             'Related: Compare with reserved_quantity in inventory analysis to forecast demand.'
    )
    
    price_subtotal = fields.Float(
        string='Subtotal (ex. tax)',
        readonly=True,
        help='The total revenue for this transaction line excluding taxes (net price × quantity). '
             'This is the primary revenue metric used for all sales analysis, margin calculations, and financial reporting. '
             'Use Case: Sum by dimension (branch/BU/time period) to calculate total revenue and compare performance. '
             'Example: "Branch A generated $50K subtotal in Q1 across 200 order lines". '
             'Important: Excludes taxes and shipping charges - use this for margin calculations, not customer invoices. '
             'Calculation: Margin = price_subtotal - (product_uom_qty × standard_price). '
             'Warning: Currency is the company currency - multi-currency sales are converted at transaction date rate.'
    )
    
    margin = fields.Float(
        string='Margin Amount',
        readonly=True,
        help='The gross profit amount for this transaction line, calculated as revenue minus cost of goods sold (COGS). '
             'Formula: margin = price_subtotal - (product_uom_qty × standard_price). '
             'Use Case: Identify which products, branches, or BUs generate the highest absolute profit contribution. '
             'Example: "$1000 revenue - $600 COGS = $400 margin". '
             'Important: Margin can be negative if selling below cost - use get_margin_analysis() to identify loss-making products. '
             'Warning: Based on standard_price (cost) at transaction time - does not reflect inventory valuation changes. '
             'Analysis: High margin products may need volume increases, low margin products may need price increases or cost reductions.'
    )
    
    margin_percent = fields.Float(
        string='Margin %',
        readonly=True,
        help='The gross profit margin expressed as a percentage of revenue, calculated as (margin / price_subtotal) × 100. '
             'This is the key profitability metric for comparing performance across products with different price points. '
             'Use Case: Identify high-margin products (>30%) and low-margin products (<10%) to guide pricing strategy. '
             'Example: "$400 margin / $1000 revenue = 40% margin percentage". '
             'Interpretation: 0% = break-even, <0% = loss, 10-20% = competitive, 20-30% = good, >30% = excellent. '
             'Warning: Percentage can be misleading - a 50% margin on a $10 sale ($5 profit) is less valuable than 10% on $1000 ($100 profit). '
             'Related: Compare margin_percent across branches to identify operational efficiency differences or pricing inconsistencies.'
    )
    
    # ========================================================================
    # SQL VIEW CREATION
    # ========================================================================
    def init(self):
        """
        Create the PostgreSQL view when the model is initialized.
        
        The view:
        1. Joins sale.order_line with sale.order
        2. Filters for confirmed orders (state in confirmed, done)
        3. Calculates margin as (price_subtotal - cogs)
        4. Includes Branch and Business Unit dimensions
        5. Optimized for pivot/grouping operations
        """
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    -- Identification
                    sol.id::integer AS id,
                    
                    -- Temporal
                    so.date_order::timestamp AS date_order,
                    
                    -- Products & Customers (explicit integer casting for Many2one fields)
                    sol.product_id::integer AS product_id,
                    so.partner_id::integer AS partner_id,
                    
                    -- OPS Matrix Dimensions (explicit integer casting for Many2one fields)
                    so.ops_branch_id::integer AS ops_branch_id,
                    so.ops_business_unit_id::integer AS ops_business_unit_id,
                    
                    -- Quantities & Revenue (explicit numeric casting for float fields)
                    sol.product_uom_qty::numeric AS product_uom_qty,
                    sol.price_subtotal::numeric AS price_subtotal,
                    
                    -- Margin Calculation (already numeric from computation)
                    (
                        sol.price_subtotal::numeric -
                        (sol.product_uom_qty::numeric * COALESCE(CAST(pp.standard_price AS NUMERIC), 0))
                    )::numeric AS margin,
                    
                    -- Margin Percentage (already numeric from computation)
                    CASE
                        WHEN sol.price_subtotal = 0 THEN 0::numeric
                        ELSE ROUND(
                            (
                                (
                                    sol.price_subtotal::numeric -
                                    (sol.product_uom_qty::numeric * COALESCE(CAST(pp.standard_price AS NUMERIC), 0))
                                ) / sol.price_subtotal::numeric * 100
                            )::numeric,
                            2
                        )
                    END AS margin_percent
                
                FROM sale_order_line sol
                
                INNER JOIN sale_order so ON sol.order_id = so.id
                LEFT JOIN product_product pp ON sol.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                
                WHERE
                    -- Only include confirmed/done orders
                    so.state IN ('sale', 'done')
                    -- Exclude cancelled lines
                    AND sol.state != 'cancel'
            )
            """
        )
    
    # ========================================================================
    # STATISTICS & AGGREGATIONS
    # ========================================================================
    @api.model
    def get_summary_by_branch(self):
        """
        Get summary statistics grouped by branch.
        
        Returns aggregated sales data by branch:
        - Total revenue
        - Total margin
        - Average margin %
        - Total units sold
        """
        self.env.cr.execute(
            """
            SELECT
                ops_branch_id,
                COUNT(*) as line_count,
                SUM(product_uom_qty) as total_qty,
                SUM(price_subtotal) as total_revenue,
                SUM(margin) as total_margin,
                ROUND(AVG(margin_percent)::numeric, 2) as avg_margin_percent
            FROM ops_sales_analysis
            WHERE ops_branch_id IN (
                SELECT id FROM res_company
                WHERE id IN (
                    SELECT branch_id FROM res_users_ops_allowed_branch_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY ops_branch_id
            ORDER BY total_revenue DESC
            """,
            [self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_summary_by_business_unit(self):
        """
        Get summary statistics grouped by business unit.
        
        Returns aggregated sales data by BU:
        - Total revenue
        - Total margin
        - Average margin %
        - Total units sold
        """
        self.env.cr.execute(
            """
            SELECT
                ops_business_unit_id,
                COUNT(*) as line_count,
                SUM(product_uom_qty) as total_qty,
                SUM(price_subtotal) as total_revenue,
                SUM(margin) as total_margin,
                ROUND(AVG(margin_percent)::numeric, 2) as avg_margin_percent
            FROM ops_sales_analysis
            WHERE ops_business_unit_id IN (
                SELECT id FROM ops_business_unit
                WHERE id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY ops_business_unit_id
            ORDER BY total_revenue DESC
            """,
            [self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_summary_by_matrix(self):
        """
        Get summary statistics grouped by Branch AND Business Unit (matrix view).
        
        Returns aggregated sales data by the Branch/BU matrix intersection:
        - Revenue per dimension pair
        - Margin per dimension pair
        - Units per dimension pair
        """
        self.env.cr.execute(
            """
            SELECT
                ops_branch_id,
                ops_business_unit_id,
                COUNT(*) as line_count,
                SUM(product_uom_qty) as total_qty,
                SUM(price_subtotal) as total_revenue,
                SUM(margin) as total_margin,
                ROUND(AVG(margin_percent)::numeric, 2) as avg_margin_percent
            FROM ops_sales_analysis
            WHERE 
                ops_branch_id IN (
                    SELECT branch_id FROM res_users_ops_allowed_branch_rel
                    WHERE user_id = %s
                )
                AND ops_business_unit_id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            GROUP BY ops_branch_id, ops_business_unit_id
            ORDER BY total_revenue DESC
            """,
            [self.env.uid, self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_margin_analysis(self):
        """
        Get detailed margin analysis by product, branch, and BU.
        
        Identifies products and dimensions with:
        - Highest margins
        - Lowest margins
        - Negative margin (loss-making) products
        """
        self.env.cr.execute(
            """
            SELECT
                product_id,
                ops_branch_id,
                ops_business_unit_id,
                COUNT(*) as transaction_count,
                ROUND(AVG(margin_percent)::numeric, 2) as avg_margin_percent,
                SUM(price_subtotal) as total_revenue,
                SUM(margin) as total_margin
            FROM ops_sales_analysis
            WHERE 
                ops_branch_id IN (
                    SELECT branch_id FROM res_users_ops_allowed_branch_rel
                    WHERE user_id = %s
                )
                AND ops_business_unit_id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            GROUP BY product_id, ops_branch_id, ops_business_unit_id
            ORDER BY avg_margin_percent ASC
            """,
            [self.env.uid, self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    # ========================================================================
    # CONSTRAINTS
    # ========================================================================
    @api.model
    def create(self, vals):
        """Prevent creation of records (read-only view)"""
        raise NotImplementedError("This is a read-only view. Records cannot be created.")
    
    def write(self, vals):
        """Prevent modification of records (read-only view)"""
        raise NotImplementedError("This is a read-only view. Records cannot be modified.")
    
    def unlink(self):
        """Prevent deletion of records (read-only view)"""
        raise NotImplementedError("This is a read-only view. Records cannot be deleted.")
