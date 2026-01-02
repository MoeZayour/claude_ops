from odoo import models, fields, api


class OpsInventoryAnalysis(models.Model):
    """
    Inventory Analysis Report - Read-Only SQL View
    
    This model represents a PostgreSQL materialized view that provides
    high-performance inventory analytics with Business Unit segregation.
    
    The view queries stock_quant to provide:
    - Product inventory levels
    - Location information
    - Business Unit dimension (from product via quant)
    - Quantity on hand
    - Stock value (quantity * standard cost)
    
    CRITICAL: This model is read-only (_auto=False) and backed by a PostgreSQL view.
    Ensures accurate inventory visibility respecting BU boundaries.
    """
    
    _name = 'ops.inventory.analysis'
    _description = 'Inventory Health and BU Segregation Analysis'
    _auto = False  # Don't auto-create table
    _rec_name = 'id'
    _order = 'product_id'
    
    # ========================================================================
    # FIELDS - Mirror the View Columns
    # ========================================================================
    id = fields.Id(readonly=True)
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
        help='The specific product variant held in inventory at this location. '
             'Used to track stock levels, valuation, and availability across the warehouse network. '
             'Use Case: Analyze inventory turnover rates, identify slow-moving stock, and plan replenishment by BU. '
             'Example: "Product SKU-001 has 500 units on-hand across 3 locations worth $25K". '
             'Important: This is the variant (product.product), not the template - tracking is at SKU level. '
             'Analysis: Use get_low_stock_alerts() to identify products below reorder points, get_overstocked_items() for excess inventory. '
             'Related: Product belongs to a Business Unit (ops_business_unit_id) - inventory respects BU silo boundaries.'
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        readonly=True,
        help='The specific warehouse location (bin, shelf, zone) where this product quantity is physically stored. '
             'Locations are organized hierarchically: Warehouse → Zone → Bin, enabling precise inventory tracking. '
             'Use Case: Track which locations hold specific products for picking optimization and space utilization analysis. '
             'Example: "WH/Stock/Shelf-A/Bin-3 contains 50 units of Product X". '
             'Important: Only internal storage and transit locations are included (usage=internal/transit) - customer/vendor locations excluded. '
             'Analysis: Use get_inventory_by_location() to see total inventory value and diversity per physical location. '
             'Related: Each location typically belongs to a warehouse (stock.warehouse) which may be assigned to a branch.'
    )
    
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        readonly=True,
        help='The business unit (division/product line) that owns and manages this inventory based on product assignment. '
             'This enables BU-level inventory silos ensuring each division controls its own stock independently. '
             'Use Case: Generate separate inventory reports per BU for P&L accuracy and divisional performance measurement. '
             'Example: "Electronics BU has $500K inventory value across 200 SKUs, Clothing BU has $300K across 150 SKUs". '
             'Important: Inherited from product.template.business_unit_id - product BU assignment determines inventory ownership. '
             'Security: Users only see inventory from BUs they have access to via persona assignments. '
             'Analysis: Use verify_bu_segregation() to identify products incorrectly assigned to multiple BUs (data integrity check).'
    )
    
    quantity = fields.Float(
        string='Quantity On Hand',
        readonly=True,
        help='The total physical quantity of this product currently present in this location, regardless of reservations. '
             'This is the actual stock-on-hand including both available and reserved units. '
             'Use Case: Calculate total inventory investment, track stock movements over time, identify excess or shortage situations. '
             'Example: "100 units on-hand: 70 available for sale + 30 reserved for existing orders". '
             'Important: Measured in product\'s unit of measure (UoM) - pieces, kg, liters, etc. Check product.uom_id for unit. '
             'Calculation: Available Quantity = Quantity - Reserved Quantity. '
             'Warning: Zero or negative quantities indicate stock discrepancies requiring physical inventory count.'
    )
    
    standard_price = fields.Float(
        string='Unit Cost',
        readonly=True,
        help='The standard cost per unit for this product, used for inventory valuation and margin calculations. '
             'This represents the acquisition cost (for purchased goods) or production cost (for manufactured goods). '
             'Use Case: Calculate total inventory value (quantity × standard_price) and cost of goods sold (COGS) for margin analysis. '
             'Example: "Product cost $50/unit × 100 units = $5,000 inventory value". '
             'Important: This is the cost at the time of snapshot - does not reflect current purchase price if costs have changed. '
             'Warning: Standard price should be updated periodically to reflect actual costs - outdated costs distort profitability reports. '
             'Related: Compare with sale price to calculate potential margin before selling (sale_price - standard_price).'
    )
    
    stock_value = fields.Float(
        string='Stock Value',
        readonly=True,
        help='The total inventory value for this product at this location, calculated as (quantity × standard_price). '
             'This represents the total capital investment tied up in inventory at cost basis. '
             'Use Case: Track total inventory investment by location, product, and BU to manage working capital and inventory turns. '
             'Example: "100 units × $50/unit = $5,000 stock value in Location A". '
             'Important: Sum across all locations and products to get total inventory asset value for balance sheet. '
             'Analysis: High stock value + low turnover = excess inventory tying up cash. Target: minimize value while maintaining availability. '
             'Related: Compare total stock_value to monthly sales to calculate inventory turnover ratio (Days Inventory Outstanding).'
    )
    
    reserved_quantity = fields.Float(
        string='Reserved Qty',
        readonly=True,
        help='The quantity of this product already reserved/allocated for confirmed sales orders awaiting delivery. '
             'Reserved stock is physically on-hand but committed to customers - not available for new orders. '
             'Use Case: Calculate true available-to-promise (ATP) inventory for sales quotations and order fulfillment planning. '
             'Example: "100 units on-hand: 30 reserved for Order #123, 70 available for new orders". '
             'Important: Reservations are created when sales orders are confirmed, released when shipment is completed. '
             'Warning: High reserved_quantity relative to total quantity indicates pending fulfillment backlog - may need expedited shipping. '
             'Related: Available Quantity = Quantity - Reserved Quantity shows true sellable inventory.'
    )
    
    available_quantity = fields.Float(
        string='Available Qty',
        readonly=True,
        help='The quantity of this product available for new sales orders, calculated as (quantity - reserved_quantity). '
             'This is the true "sellable" inventory that can be promised to new customers without overselling. '
             'Use Case: Check available_quantity before accepting new orders to avoid stockouts and backorders. '
             'Example: "100 on-hand - 30 reserved = 70 available for new orders". '
             'Important: This is the Available-to-Promise (ATP) metric used by sales teams and e-commerce systems. '
             'Warning: Negative available_quantity indicates oversold situation - more reserved than on-hand (requires urgent replenishment). '
             'Analysis: Low available_quantity triggers reorder points - use with minimum stock rules to prevent stockouts. '
             'Related: Compare with demand forecast to ensure sufficient stock for upcoming sales without excess inventory.'
    )
    
    # ========================================================================
    # SQL VIEW CREATION
    # ========================================================================
    def init(self):
        """
        Create the PostgreSQL view when the model is initialized.
        
        The view:
        1. Queries stock_quant for all stock quantities
        2. Joins with product_product and product_template for BU
        3. Includes location information
        4. Calculates stock value
        5. Optimized for BU-aware inventory analysis
        """
        self.env.cr.execute(
            f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    -- Identification
                    sq.id,
                    sq.product_id,
                    sq.location_id,
                    
                    -- OPS Matrix Dimension (from product)
                    pt.business_unit_id AS ops_business_unit_id,
                    
                    -- Inventory quantities
                    sq.quantity,
                    CAST(pp.standard_price AS NUMERIC) AS standard_price,
                    sq.reserved_quantity,
                    
                    -- Calculated fields
                    (sq.quantity * CAST(pp.standard_price AS NUMERIC)) AS stock_value,
                    (sq.quantity - sq.reserved_quantity) AS available_quantity
                
                FROM stock_quant sq
                
                INNER JOIN product_product pp ON sq.product_id = pp.id
                INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
                
                WHERE
                    -- Only include locations that are actual warehouses/storage
                    sq.location_id IN (
                        SELECT id FROM stock_location 
                        WHERE usage IN ('internal', 'transit')
                    )
                    -- Only non-zero quantities (filter out ghost records)
                    AND (sq.quantity != 0 OR sq.reserved_quantity != 0)
            )
            """
        )
    
    # ========================================================================
    # STATISTICS & AGGREGATIONS
    # ========================================================================
    @api.model
    def get_summary_by_business_unit(self):
        """
        Get inventory summary grouped by business unit.
        
        Returns aggregated inventory data by BU:
        - Total on-hand quantity
        - Total reserved quantity
        - Total available quantity
        - Total stock value
        - Item count
        """
        self.env.cr.execute(
            """
            SELECT
                ops_business_unit_id,
                COUNT(DISTINCT product_id) as product_count,
                COUNT(*) as location_product_count,
                SUM(quantity) as total_on_hand,
                SUM(reserved_quantity) as total_reserved,
                SUM(available_quantity) as total_available,
                SUM(stock_value) as total_value
            FROM ops_inventory_analysis
            WHERE ops_business_unit_id IN (
                SELECT id FROM ops_business_unit
                WHERE id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY ops_business_unit_id
            ORDER BY total_value DESC
            """,
            [self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_inventory_by_location(self):
        """
        Get inventory summary grouped by location and business unit.
        
        Shows warehouse-level inventory positions:
        - Inventory by warehouse
        - Shows BU ownership
        - Identifies stock segregation
        """
        self.env.cr.execute(
            """
            SELECT
                location_id,
                ops_business_unit_id,
                COUNT(DISTINCT product_id) as product_count,
                SUM(quantity) as total_on_hand,
                SUM(reserved_quantity) as total_reserved,
                SUM(available_quantity) as total_available,
                SUM(stock_value) as location_bu_value
            FROM ops_inventory_analysis
            WHERE ops_business_unit_id IN (
                SELECT id FROM ops_business_unit
                WHERE id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY location_id, ops_business_unit_id
            ORDER BY location_bu_value DESC
            """,
            [self.env.uid]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_low_stock_alerts(self, threshold_value=1000):
        """
        Get inventory items with low stock value (potential issue).
        
        :param threshold_value: Value threshold to flag as "low stock"
        :return: Products below value threshold by BU
        """
        self.env.cr.execute(
            """
            SELECT
                product_id,
                ops_business_unit_id,
                location_id,
                COUNT(*) as location_count,
                SUM(quantity) as total_quantity,
                SUM(stock_value) as total_value
            FROM ops_inventory_analysis
            WHERE 
                ops_business_unit_id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            GROUP BY product_id, ops_business_unit_id, location_id
            HAVING SUM(stock_value) > 0 AND SUM(stock_value) < %s
            ORDER BY total_value ASC
            """,
            [self.env.uid, threshold_value]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def get_overstocked_items(self, threshold_qty=100):
        """
        Get inventory items with excess/overstock condition.
        
        Helps identify potentially slow-moving or obsolete stock:
        - High quantity
        - Low recent movement
        - By BU
        
        :param threshold_qty: Quantity threshold to flag as "overstocked"
        :return: Products above quantity threshold by BU
        """
        self.env.cr.execute(
            """
            SELECT
                product_id,
                ops_business_unit_id,
                COUNT(*) as location_count,
                SUM(quantity) as total_quantity,
                SUM(available_quantity) as total_available,
                SUM(stock_value) as total_value,
                ROUND((SUM(quantity) / NULLIF(SUM(reserved_quantity), 0))::numeric, 2) as qty_to_reserved_ratio
            FROM ops_inventory_analysis
            WHERE 
                ops_business_unit_id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            GROUP BY product_id, ops_business_unit_id
            HAVING SUM(quantity) > %s
            ORDER BY total_value DESC
            """,
            [self.env.uid, threshold_qty]
        )
        return self.env.cr.dictfetchall()
    
    @api.model
    def verify_bu_segregation(self):
        """
        Verify that inventory is properly segregated by Business Unit.
        
        Returns products where:
        - Quantities exist in multiple BU assignments (possible data integrity issue)
        - Used for BU-aware inventory audits
        """
        self.env.cr.execute(
            """
            SELECT
                product_id,
                COUNT(DISTINCT ops_business_unit_id) as bu_count,
                ARRAY_AGG(DISTINCT ops_business_unit_id) as bu_ids,
                SUM(quantity) as total_qty,
                SUM(stock_value) as total_value
            FROM ops_inventory_analysis
            WHERE ops_business_unit_id IN (
                SELECT id FROM ops_business_unit
                WHERE id IN (
                    SELECT business_unit_id FROM res_users_ops_allowed_business_unit_rel
                    WHERE user_id = %s
                )
            )
            GROUP BY product_id
            HAVING COUNT(DISTINCT ops_business_unit_id) > 1
            ORDER BY total_value DESC
            """,
            [self.env.uid]
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
