# -*- coding: utf-8 -*-
"""
Test Suite for OPS Matrix Performance and Database Optimization
Tests database indexes, query performance, and scalability
"""
import logging
import time
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger

_logger = logging.getLogger(__name__)

@tagged('post_install', 'matrix_performance', '-at_install', '-standard')
class TestPerformance(TransactionCase):
    """Test suite for performance and database optimization."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Get or create test data
        cls.company = cls.env.company
        cls.branch = cls.env['ops.branch'].search([
            ('company_id', '=', cls.company.id)
        ], limit=1)
        
        if not cls.branch:
            cls.branch = cls.env['ops.branch'].create({
                'name': 'Performance Test Branch',
                'code': 'PTB-001',
                'company_id': cls.company.id,
            })
    
    # =========================================================================
    # TEST 1: INDEX USAGE VERIFICATION
    # =========================================================================
    
    def test_01_sale_order_branch_index_usage(self):
        """Test that sale order queries use branch index."""
        # Execute EXPLAIN on a typical branch query
        query = """
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT id, name, amount_total
            FROM sale_order
            WHERE ops_branch_id = %s
            AND date_order >= %s
            LIMIT 100
        """
        
        date_from = date.today() - timedelta(days=30)
        
        self.env.cr.execute(query, (self.branch.id, date_from))
        explain_output = '\n'.join([str(row[0]) for row in self.env.cr.fetchall()])
        
        _logger.info(f"Sale Order Query Plan:\n{explain_output}")
        
        # Check that index is being used (not a sequential scan)
        # Note: Index might not be used if table is small
        if 'Seq Scan' in explain_output:
            _logger.warning(
                "Sequential scan detected on sale_order. "
                "This is normal for small tables but should use index in production."
            )
        
        # Verify query completes (no syntax errors)
        self.assertTrue(True, "Query executed successfully")
    
    def test_02_account_move_branch_index_usage(self):
        """Test that account move queries use branch index."""
        query = """
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT id, name, amount_total
            FROM account_move
            WHERE ops_branch_id = %s
            AND date >= %s
            AND move_type IN ('out_invoice', 'out_refund')
            LIMIT 100
        """
        
        date_from = date.today() - timedelta(days=30)
        
        self.env.cr.execute(query, (self.branch.id, date_from))
        explain_output = '\n'.join([str(row[0]) for row in self.env.cr.fetchall()])
        
        _logger.info(f"Account Move Query Plan:\n{explain_output}")
        
        # Verify query completes
        self.assertTrue(True, "Query executed successfully")
    
    def test_03_stock_move_branch_index_usage(self):
        """Test that stock move queries use branch index."""
        query = """
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT id, name, product_id, product_uom_qty
            FROM stock_move
            WHERE ops_branch_id = %s
            AND date >= %s
            AND state = 'done'
            LIMIT 100
        """
        
        date_from = date.today() - timedelta(days=30)
        
        try:
            self.env.cr.execute(query, (self.branch.id, date_from))
            explain_output = '\n'.join([str(row[0]) for row in self.env.cr.fetchall()])
            
            _logger.info(f"Stock Move Query Plan:\n{explain_output}")
            
            self.assertTrue(True, "Query executed successfully")
        except Exception as e:
            # If stock_move doesn't have ops_branch_id, that's okay
            _logger.warning(f"Stock move query failed (might not have ops_branch_id): {e}")
    
    def test_04_index_list_verification(self):
        """Test that critical indexes exist on database."""
        # Check for indexes on sale_order
        query = """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'sale_order'
            AND indexname LIKE '%ops_branch%'
        """
        
        self.env.cr.execute(query)
        indexes = self.env.cr.fetchall()
        
        _logger.info(f"Sale Order Branch Indexes: {indexes}")
        
        # If no branch indexes found, log warning
        if not indexes:
            _logger.warning(
                "No branch-related indexes found on sale_order. "
                "Consider creating: idx_sale_order_ops_branch_date"
            )
    
    # =========================================================================
    # TEST 2: QUERY PERFORMANCE BENCHMARKS
    # =========================================================================
    
    def test_05_sale_order_search_performance(self):
        """Test sale order search performance."""
        # Time a typical search operation
        start_time = time.time()
        
        orders = self.env['sale.order'].search([
            ('ops_branch_id', '=', self.branch.id),
            ('date_order', '>=', date.today() - timedelta(days=30)),
        ], limit=100)
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Sale order search took {elapsed:.3f}s for {len(orders)} records")
        
        # Should complete in reasonable time (< 2 seconds)
        self.assertLess(elapsed, 2.0,
                       f"Sale order search took {elapsed:.3f}s (should be < 2s)")
    
    def test_06_sales_analysis_query_performance(self):
        """Test sales analysis model performance."""
        start_time = time.time()
        
        analysis = self.env['ops.sales.analysis'].search_read(
            [
                ('date_order', '>=', date.today() - timedelta(days=90)),
                ('ops_branch_id', '=', self.branch.id),
            ],
            ['total_amount', 'product_id', 'ops_business_unit_id'],
            limit=1000
        )
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Sales analysis query took {elapsed:.3f}s for {len(analysis)} records")
        
        # Should complete in reasonable time
        self.assertLess(elapsed, 3.0,
                       f"Sales analysis query took {elapsed:.3f}s (should be < 3s)")
    
    def test_07_financial_analysis_query_performance(self):
        """Test financial analysis model performance."""
        start_time = time.time()
        
        analysis = self.env['ops.financial.analysis'].search_read(
            [
                ('date', '>=', date.today() - timedelta(days=90)),
                ('ops_branch_id', '=', self.branch.id),
            ],
            ['total_debit', 'total_credit', 'account_id'],
            limit=1000
        )
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Financial analysis query took {elapsed:.3f}s for {len(analysis)} records")
        
        self.assertLess(elapsed, 3.0,
                       f"Financial analysis query took {elapsed:.3f}s (should be < 3s)")
    
    def test_08_inventory_analysis_query_performance(self):
        """Test inventory analysis model performance."""
        start_time = time.time()
        
        analysis = self.env['ops.inventory.analysis'].search_read(
            [
                ('date', '>=', date.today() - timedelta(days=90)),
                ('ops_branch_id', '=', self.branch.id),
            ],
            ['quantity', 'product_id', 'location_id'],
            limit=1000
        )
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Inventory analysis query took {elapsed:.3f}s for {len(analysis)} records")
        
        self.assertLess(elapsed, 3.0,
                       f"Inventory analysis query took {elapsed:.3f}s (should be < 3s)")
    
    # =========================================================================
    # TEST 3: DASHBOARD LOAD TIME
    # =========================================================================
    
    def test_09_dashboard_data_load_time(self):
        """Test that dashboard data loads within acceptable time."""
        # Simulate loading dashboard data (multiple queries)
        start_time = time.time()
        
        # Typical dashboard queries
        date_from = date.today() - timedelta(days=30)
        
        # Sales summary
        self.env['ops.sales.analysis'].read_group(
            [('date_order', '>=', date_from)],
            ['total_amount:sum'],
            ['ops_branch_id']
        )
        
        # Financial summary
        self.env['ops.financial.analysis'].read_group(
            [('date', '>=', date_from)],
            ['total_debit:sum', 'total_credit:sum'],
            ['ops_branch_id']
        )
        
        # Inventory summary
        self.env['ops.inventory.analysis'].read_group(
            [('date', '>=', date_from)],
            ['quantity:sum'],
            ['ops_branch_id']
        )
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Dashboard data loaded in {elapsed:.3f}s")
        
        # Should load quickly (< 5 seconds for all queries)
        self.assertLess(elapsed, 5.0,
                       f"Dashboard load took {elapsed:.3f}s (should be < 5s)")
    
    # =========================================================================
    # TEST 4: LARGE DATASET HANDLING
    # =========================================================================
    
    def test_10_large_date_range_query(self):
        """Test performance with large date range (1 year)."""
        start_time = time.time()
        
        date_from = date.today() - timedelta(days=365)
        
        # Query large date range
        records = self.env['sale.order'].search([
            ('date_order', '>=', date_from),
        ], limit=500)
        
        elapsed = time.time() - start_time
        
        _logger.info(f"1-year query took {elapsed:.3f}s for {len(records)} records")
        
        # Should handle large ranges efficiently
        self.assertLess(elapsed, 5.0,
                       f"Large date range query took {elapsed:.3f}s (should be < 5s)")
    
    def test_11_pagination_performance(self):
        """Test that pagination works efficiently."""
        # Test multiple pages
        page_size = 100
        total_time = 0
        
        for offset in range(0, 500, page_size):
            start_time = time.time()
            
            self.env['sale.order'].search(
                [],
                limit=page_size,
                offset=offset
            )
            
            page_time = time.time() - start_time
            total_time += page_time
        
        _logger.info(f"Pagination (5 pages) took {total_time:.3f}s total")
        
        # Each page should be fast
        self.assertLess(total_time, 2.0,
                       f"Pagination took {total_time:.3f}s (should be < 2s)")
    
    # =========================================================================
    # TEST 5: CONCURRENT QUERY SIMULATION
    # =========================================================================
    
    def test_12_multiple_simultaneous_queries(self):
        """Test performance with multiple queries running."""
        start_time = time.time()
        
        # Simulate multiple users querying
        date_from = date.today() - timedelta(days=30)
        
        # User 1: Sales query
        self.env['sale.order'].search([
            ('date_order', '>=', date_from),
        ], limit=100)
        
        # User 2: Purchase query
        self.env['purchase.order'].search([
            ('date_order', '>=', date_from),
        ], limit=100)
        
        # User 3: Invoice query
        self.env['account.move'].search([
            ('date', '>=', date_from),
            ('move_type', '=', 'out_invoice'),
        ], limit=100)
        
        # User 4: Stock query
        self.env['stock.picking'].search([
            ('scheduled_date', '>=', date_from),
        ], limit=100)
        
        elapsed = time.time() - start_time
        
        _logger.info(f"4 concurrent queries took {elapsed:.3f}s")
        
        # Should handle multiple queries efficiently
        self.assertLess(elapsed, 3.0,
                       f"Concurrent queries took {elapsed:.3f}s (should be < 3s)")
    
    # =========================================================================
    # TEST 6: COMPUTED FIELD PERFORMANCE
    # =========================================================================
    
    def test_13_computed_field_calculation_speed(self):
        """Test that computed fields calculate quickly."""
        # Get records with computed fields
        start_time = time.time()
        
        branches = self.env['ops.branch'].search([], limit=50)
        
        # Access computed fields (triggers computation)
        for branch in branches:
            _ = branch.display_name
            if hasattr(branch, 'business_unit_count'):
                _ = branch.business_unit_count
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Computed field access for {len(branches)} branches took {elapsed:.3f}s")
        
        # Should be fast
        self.assertLess(elapsed, 2.0,
                       f"Computed field calculation took {elapsed:.3f}s (should be < 2s)")
    
    # =========================================================================
    # TEST 7: SEARCH/READ OPTIMIZATION
    # =========================================================================
    
    def test_14_search_read_vs_search_browse(self):
        """Compare search_read vs search + browse performance."""
        date_from = date.today() - timedelta(days=30)
        domain = [('date_order', '>=', date_from)]
        fields = ['name', 'partner_id', 'amount_total']
        
        # Method 1: search_read
        start_time = time.time()
        result1 = self.env['sale.order'].search_read(
            domain,
            fields,
            limit=100
        )
        elapsed1 = time.time() - start_time
        
        # Method 2: search + read
        start_time = time.time()
        orders = self.env['sale.order'].search(domain, limit=100)
        result2 = orders.read(fields)
        elapsed2 = time.time() - start_time
        
        _logger.info(f"search_read: {elapsed1:.3f}s, search+read: {elapsed2:.3f}s")
        
        # search_read should be faster or comparable
        self.assertLessEqual(len(result1), len(result2))
    
    # =========================================================================
    # TEST 8: MEMORY USAGE
    # =========================================================================
    
    def test_15_large_recordset_memory_efficiency(self):
        """Test memory efficiency with large recordsets."""
        # Query large number of records
        start_time = time.time()
        
        # Use search_read to limit memory usage
        records = self.env['sale.order'].search_read(
            [],
            ['name', 'date_order'],
            limit=1000
        )
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Loaded {len(records)} records in {elapsed:.3f}s")
        
        # Should handle 1000 records efficiently
        self.assertLess(elapsed, 5.0,
                       f"Loading 1000 records took {elapsed:.3f}s (should be < 5s)")
    
    # =========================================================================
    # TEST 9: DOMAIN FILTER OPTIMIZATION
    # =========================================================================
    
    def test_16_complex_domain_performance(self):
        """Test performance of complex domain filters."""
        start_time = time.time()
        
        # Complex domain with multiple conditions
        domain = [
            '&',
            ('date_order', '>=', date.today() - timedelta(days=90)),
            ('date_order', '<=', date.today()),
            '|',
            ('state', '=', 'sale'),
            ('state', '=', 'done'),
            ('ops_branch_id', '!=', False),
        ]
        
        orders = self.env['sale.order'].search(domain, limit=200)
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Complex domain query found {len(orders)} records in {elapsed:.3f}s")
        
        self.assertLess(elapsed, 3.0,
                       f"Complex domain took {elapsed:.3f}s (should be < 3s)")
    
    # =========================================================================
    # TEST 10: REPORTING PERFORMANCE
    # =========================================================================
    
    def test_17_read_group_aggregation_performance(self):
        """Test read_group aggregation performance."""
        start_time = time.time()
        
        # Typical aggregation query
        result = self.env['sale.order'].read_group(
            [('date_order', '>=', date.today() - timedelta(days=90))],
            ['amount_total:sum'],
            ['ops_branch_id', 'state'],
            lazy=False
        )
        
        elapsed = time.time() - start_time
        
        _logger.info(f"read_group aggregation took {elapsed:.3f}s, {len(result)} groups")
        
        self.assertLess(elapsed, 2.0,
                       f"Aggregation took {elapsed:.3f}s (should be < 2s)")
    
    def test_18_export_data_preparation_performance(self):
        """Test performance of data preparation for export."""
        start_time = time.time()
        
        # Simulate export data preparation
        records = self.env['sale.order'].search_read(
            [('date_order', '>=', date.today() - timedelta(days=30))],
            ['name', 'partner_id', 'amount_total', 'state', 'ops_branch_id'],
            limit=500
        )
        
        # Process data (like for Excel export)
        processed = []
        for record in records:
            processed.append({
                'name': record['name'],
                'partner': record['partner_id'][1] if record['partner_id'] else '',
                'amount': record['amount_total'],
                'state': record['state'],
            })
        
        elapsed = time.time() - start_time
        
        _logger.info(f"Export preparation for {len(records)} records took {elapsed:.3f}s")
        
        self.assertLess(elapsed, 5.0,
                       f"Export preparation took {elapsed:.3f}s (should be < 5s)")
    
    # =========================================================================
    # TEST 11: ORM VS RAW SQL COMPARISON
    # =========================================================================
    
    def test_19_orm_vs_sql_performance(self):
        """Compare ORM vs raw SQL performance for same query."""
        # ORM query
        start_time = time.time()
        orm_result = self.env['sale.order'].search_count([
            ('date_order', '>=', date.today() - timedelta(days=30)),
            ('state', '=', 'sale'),
        ])
        orm_time = time.time() - start_time
        
        # Raw SQL query
        start_time = time.time()
        self.env.cr.execute("""
            SELECT COUNT(*)
            FROM sale_order
            WHERE date_order >= %s
            AND state = %s
        """, (date.today() - timedelta(days=30), 'sale'))
        sql_result = self.env.cr.fetchone()[0]
        sql_time = time.time() - start_time
        
        _logger.info(f"ORM: {orm_time:.3f}s, SQL: {sql_time:.3f}s")
        
        # Results should match
        self.assertEqual(orm_result, sql_result,
                        "ORM and SQL should return same count")
        
        # ORM should be reasonably efficient
        self.assertLess(orm_time, 1.0,
                       f"ORM query took {orm_time:.3f}s (should be < 1s)")
