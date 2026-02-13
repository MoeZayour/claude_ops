# -*- coding: utf-8 -*-
"""
Performance Test Suite for OPS Matrix Accounting
Validates N+1 query optimizations and performance targets
"""

import time
import logging
from datetime import date, timedelta
from odoo.tests import TransactionCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'ops_performance')
class TestConsolidatedReportingPerformance(TransactionCase):
    """
    Performance tests for consolidated reporting queries.

    Target: Reports should complete in <2 seconds for 100 entities
    Success Criteria:
    - Branch detail report: <2s for 100 branches
    - BU detail report: <2s for 100 business units
    - Matrix report: <5s for 10×5 matrix
    - Query count: 1 per report (not N or N×M)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'OPS Performance Test Company',
        })

        # Create 50 test branches (realistic production size)
        cls.branches = cls.env['ops.branch'].create([
            {
                'name': f'Test Branch {i:03d}',
                'code': f'BR{i:03d}',
                'company_id': cls.company.id,
                'active': True,
            }
            for i in range(1, 51)
        ])
        _logger.info(f"Created {len(cls.branches)} test branches")

        # Create 10 test business units
        cls.business_units = cls.env['ops.business.unit'].create([
            {
                'name': f'Test BU {i}',
                'code': f'BU{i:02d}',
                'company_ids': [(6, 0, [cls.company.id])],
                'branch_ids': [(6, 0, cls.branches.ids)],  # All BUs operate in all branches
                'active': True,
            }
            for i in range(1, 11)
        ])
        _logger.info(f"Created {len(cls.business_units)} test business units")

        # Create chart of accounts
        cls.income_account = cls.env['account.account'].create({
            'name': 'Test Income',
            'code': 'INC001',
            'account_type': 'income',
            'company_id': cls.company.id,
        })

        cls.expense_account = cls.env['account.account'].create({
            'name': 'Test Expense',
            'code': 'EXP001',
            'account_type': 'expense',
            'company_id': cls.company.id,
        })

        # Create journal
        cls.journal = cls.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TEST',
            'type': 'general',
            'company_id': cls.company.id,
        })

        # Create test transactions (20 per branch-BU combination = 10,000 transactions)
        cls._create_test_transactions(cls)

        # Create test wizard for reports
        cls.date_from = date.today() - timedelta(days=30)
        cls.date_to = date.today()

    @classmethod
    def _create_test_transactions(cls, self):
        """Create realistic transaction volume for performance testing."""
        _logger.info("Creating test transactions...")

        MoveLine = self.env['account.move.line']
        transaction_count = 0

        # Create 20 transactions per branch-BU combination
        # 50 branches × 10 BUs × 20 transactions = 10,000 move lines
        for branch in cls.branches:
            for bu in cls.business_units:
                # Create 10 income transactions
                for i in range(10):
                    move = self.env['account.move'].create({
                        'journal_id': cls.journal.id,
                        'company_id': cls.company.id,
                        'date': cls.date_from + timedelta(days=i),
                        'state': 'draft',
                    })

                    # Income line
                    MoveLine.create({
                        'move_id': move.id,
                        'account_id': cls.income_account.id,
                        'name': f'Income {branch.code}-{bu.code}-{i}',
                        'credit': 1000.0 + (i * 10),
                        'debit': 0.0,
                        'date': move.date,
                        'ops_branch_id': branch.id,
                        'ops_business_unit_id': bu.id,
                    })

                    # Balancing line
                    MoveLine.create({
                        'move_id': move.id,
                        'account_id': cls.expense_account.id,
                        'name': f'Balance {branch.code}-{bu.code}-{i}',
                        'debit': 1000.0 + (i * 10),
                        'credit': 0.0,
                        'date': move.date,
                        'ops_branch_id': branch.id,
                        'ops_business_unit_id': bu.id,
                    })

                    move.action_post()
                    transaction_count += 2

                # Create 10 expense transactions
                for i in range(10):
                    move = self.env['account.move'].create({
                        'journal_id': cls.journal.id,
                        'company_id': cls.company.id,
                        'date': cls.date_from + timedelta(days=i + 10),
                        'state': 'draft',
                    })

                    # Expense line
                    MoveLine.create({
                        'move_id': move.id,
                        'account_id': cls.expense_account.id,
                        'name': f'Expense {branch.code}-{bu.code}-{i}',
                        'debit': 600.0 + (i * 5),
                        'credit': 0.0,
                        'date': move.date,
                        'ops_branch_id': branch.id,
                        'ops_business_unit_id': bu.id,
                    })

                    # Balancing line
                    MoveLine.create({
                        'move_id': move.id,
                        'account_id': cls.income_account.id,
                        'name': f'Balance {branch.code}-{bu.code}-{i}',
                        'credit': 600.0 + (i * 5),
                        'debit': 0.0,
                        'date': move.date,
                        'ops_branch_id': branch.id,
                        'ops_business_unit_id': bu.id,
                    })

                    move.action_post()
                    transaction_count += 2

        _logger.info(f"Created {transaction_count} test move lines across {len(cls.branches)} branches and {len(cls.business_units)} BUs")

    def test_branch_detail_performance(self):
        """Branch detail report should complete in <2 seconds for 50 branches."""
        _logger.info("\n" + "="*80)
        _logger.info("Testing Branch Detail Report Performance")
        _logger.info("="*80)

        # Create wizard
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        # Prepare domain
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company.id),
        ]

        # Measure performance
        start_time = time.time()
        result = wizard._get_branch_detail_data(domain, self.branches)
        duration = time.time() - start_time

        # Log results
        _logger.info(f"Branch count: {len(self.branches)}")
        _logger.info(f"Duration: {duration:.3f}s")
        _logger.info(f"Query count: {result.get('query_count', 'N/A')}")
        _logger.info(f"Results: {len(result.get('branch_data', []))} branches processed")

        # Performance assertions
        self.assertLess(duration, 2.0,
            f"Branch detail report took {duration:.2f}s, expected <2s for {len(self.branches)} branches")

        # Query count assertion (should be O(1))
        self.assertEqual(result.get('query_count'), 1,
            f"Expected 1 query (O(1)), got {result.get('query_count')}")

        # Correctness assertion
        self.assertEqual(len(result['branch_data']), len(self.branches),
            "Should return data for all branches")

        # Verify financial data makes sense
        for branch_info in result['branch_data']:
            self.assertGreater(branch_info['income'], 0, "Should have positive income")
            self.assertGreater(branch_info['expense'], 0, "Should have positive expense")

        _logger.info(f"✓ PASSED: Branch detail report completed in {duration:.3f}s with 1 query")
        _logger.info("="*80 + "\n")

    def test_bu_detail_performance(self):
        """BU detail report should complete in <2 seconds for 10 business units."""
        _logger.info("\n" + "="*80)
        _logger.info("Testing Business Unit Detail Report Performance")
        _logger.info("="*80)

        # Create wizard
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        # Prepare domain
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company.id),
        ]

        # Measure performance
        start_time = time.time()
        result = wizard._get_bu_detail_data(domain, self.branches)
        duration = time.time() - start_time

        # Log results
        _logger.info(f"Business unit count: {len(self.business_units)}")
        _logger.info(f"Duration: {duration:.3f}s")
        _logger.info(f"Query count: {result.get('query_count', 'N/A')}")
        _logger.info(f"Results: {len(result.get('bu_data', []))} BUs processed")

        # Performance assertions
        self.assertLess(duration, 2.0,
            f"BU detail report took {duration:.2f}s, expected <2s for {len(self.business_units)} BUs")

        # Query count assertion (should be O(1))
        self.assertEqual(result.get('query_count'), 1,
            f"Expected 1 query (O(1)), got {result.get('query_count')}")

        # Correctness assertion
        self.assertEqual(len(result['bu_data']), len(self.business_units),
            "Should return data for all business units")

        # Verify financial data makes sense
        for bu_info in result['bu_data']:
            self.assertGreater(bu_info['income'], 0, "Should have positive income")
            self.assertGreater(bu_info['expense'], 0, "Should have positive expense")

        _logger.info(f"✓ PASSED: BU detail report completed in {duration:.3f}s with 1 query")
        _logger.info("="*80 + "\n")

    def test_matrix_report_performance(self):
        """Matrix report should complete in <5 seconds for 50×10 matrix."""
        _logger.info("\n" + "="*80)
        _logger.info("Testing Cross-Dimensional Matrix Report Performance")
        _logger.info("="*80)

        # Create wizard
        wizard = self.env['ops.profitability.matrix.wizard'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        # Measure performance
        start_time = time.time()
        wizard._compute_matrix_data()
        duration = time.time() - start_time

        matrix_data = wizard.matrix_data

        # Log results
        _logger.info(f"Matrix size: {len(self.branches)} branches × {len(self.business_units)} BUs")
        _logger.info(f"Duration: {duration:.3f}s")
        _logger.info(f"Query count: {matrix_data.get('query_count', 'N/A')}")
        _logger.info(f"Results: {len(matrix_data.get('matrix', []))} combinations processed")
        _logger.info(f"Active combinations: {matrix_data.get('summary', {}).get('active_combinations', 0)}")

        # Performance assertions
        self.assertLess(duration, 5.0,
            f"Matrix report took {duration:.2f}s, expected <5s for {len(self.branches)}×{len(self.business_units)} matrix")

        # Query count assertion (should be O(1))
        self.assertEqual(matrix_data.get('query_count'), 1,
            f"Expected 1 query (O(1)), got {matrix_data.get('query_count')}")

        # Correctness assertions
        expected_combinations = len(self.branches) * len(self.business_units)
        self.assertEqual(len(matrix_data['matrix']), expected_combinations,
            f"Should return data for all {expected_combinations} combinations")

        # Verify matrix structure
        for cell in matrix_data['matrix']:
            self.assertIn('branch_id', cell)
            self.assertIn('bu_id', cell)
            self.assertIn('income', cell)
            self.assertIn('expense', cell)
            self.assertIn('net_profit', cell)
            self.assertGreater(cell['income'], 0, "Should have positive income")
            self.assertGreater(cell['expense'], 0, "Should have positive expense")

        _logger.info(f"✓ PASSED: Matrix report completed in {duration:.3f}s with 1 query")
        _logger.info("="*80 + "\n")

    def test_query_count_optimization(self):
        """Verify that query count is O(1) not O(N) or O(N×M)."""
        _logger.info("\n" + "="*80)
        _logger.info("Testing Query Count Optimization")
        _logger.info("="*80)

        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company.id),
        ]

        # Test with different sizes
        test_cases = [
            (10, "Small dataset"),
            (25, "Medium dataset"),
            (50, "Large dataset"),
        ]

        for branch_count, description in test_cases:
            branches_subset = self.branches[:branch_count]

            result = wizard._get_branch_detail_data(domain, branches_subset)
            query_count = result.get('query_count', 0)

            _logger.info(f"{description}: {branch_count} branches → {query_count} query")

            # Should always be 1 query regardless of size (O(1))
            self.assertEqual(query_count, 1,
                f"{description} should use 1 query, got {query_count}")

        _logger.info("✓ PASSED: Query count is O(1) for all dataset sizes")
        _logger.info("="*80 + "\n")

    def test_performance_regression(self):
        """Comprehensive performance regression test."""
        _logger.info("\n" + "="*80)
        _logger.info("Performance Regression Test Summary")
        _logger.info("="*80)

        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company.id),
        ]

        # Test all report types
        tests = []

        # Branch detail
        start = time.time()
        result1 = wizard._get_branch_detail_data(domain, self.branches)
        tests.append(("Branch Detail", time.time() - start, 2.0, result1.get('query_count', 0)))

        # BU detail
        start = time.time()
        result2 = wizard._get_bu_detail_data(domain, self.branches)
        tests.append(("BU Detail", time.time() - start, 2.0, result2.get('query_count', 0)))

        # Matrix
        matrix_wizard = self.env['ops.profitability.matrix.wizard'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        start = time.time()
        matrix_wizard._compute_matrix_data()
        tests.append(("Matrix Report", time.time() - start, 5.0, matrix_wizard.matrix_data.get('query_count', 0)))

        # Print summary table
        _logger.info("\nReport Type       | Duration  | Target | Status | Queries")
        _logger.info("-" * 65)

        all_passed = True
        for name, duration, target, queries in tests:
            status = "PASS ✓" if duration < target else "FAIL ✗"
            if duration >= target:
                all_passed = False
            _logger.info(f"{name:17} | {duration:6.3f}s  | {target:.1f}s  | {status:6} | {queries}")

        _logger.info("-" * 65)

        if all_passed:
            _logger.info("✓ ALL PERFORMANCE TESTS PASSED")
        else:
            _logger.warning("✗ SOME PERFORMANCE TESTS FAILED")

        _logger.info("="*80 + "\n")

        self.assertTrue(all_passed, "All performance tests should pass")
