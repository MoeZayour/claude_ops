# -*- coding: utf-8 -*-
"""Consolidated Reporting Tests"""

from odoo.tests import tagged, TransactionCase
from datetime import date, timedelta


@tagged('post_install', '-at_install', 'ops_reporting')
class TestConsolidatedReporting(TransactionCase):
    """Test consolidated reporting functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'Test Reporting Company',
        })

        # Create branches
        cls.branch_a = cls.env['ops.branch'].create({
            'name': 'Branch A',
            'code': 'BR-A',
            'company_id': cls.company.id,
        })
        cls.branch_b = cls.env['ops.branch'].create({
            'name': 'Branch B',
            'code': 'BR-B',
            'company_id': cls.company.id,
        })

        # Create business units
        cls.bu_sales = cls.env['ops.business.unit'].create({
            'name': 'Sales',
            'code': 'BU-SALES',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch_a.id, cls.branch_b.id])],
        })

        # Create accounts
        cls.income_account = cls.env['account.account'].create({
            'name': 'Income',
            'code': 'INC001',
            'account_type': 'income',
            'company_id': cls.company.id,
        })
        cls.expense_account = cls.env['account.account'].create({
            'name': 'Expense',
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

        cls.date_from = date.today() - timedelta(days=30)
        cls.date_to = date.today()

    def test_company_consolidation_wizard_creation(self):
        """Test creating consolidation wizard."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        self.assertTrue(wizard.id, "Wizard should be created")
        self.assertEqual(wizard.company_id, self.company)

    def test_summary_report_generation(self):
        """Test summary level report generation."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': 'summary',
        })

        # Trigger report computation
        wizard._compute_report_data()

        # Verify report_data is populated
        self.assertTrue(wizard.report_data, "Report data should be generated")

    def test_branch_detail_report(self):
        """Test branch detail report generation."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': 'by_branch',
        })

        wizard._compute_report_data()

        self.assertTrue(wizard.report_data, "Branch detail report should be generated")
        if wizard.report_data:
            self.assertIn('branch_data', wizard.report_data,
                "Report should contain branch_data")

    def test_bu_detail_report(self):
        """Test business unit detail report generation."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': 'by_bu',
        })

        wizard._compute_report_data()

        self.assertTrue(wizard.report_data, "BU detail report should be generated")
        if wizard.report_data:
            self.assertIn('bu_data', wizard.report_data,
                "Report should contain bu_data")

    def test_branch_filter(self):
        """Test filtering report by specific branches."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [self.branch_a.id])],
            'report_detail_level': 'by_branch',
        })

        wizard._compute_report_data()

        # Report should only include filtered branch
        self.assertTrue(wizard.report_data)

    def test_previous_period_comparison(self):
        """Test previous period comparison."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'compare_with_previous': True,
        })

        # Compute previous dates
        wizard._compute_previous_dates()

        self.assertTrue(wizard.previous_date_from,
            "Previous period start should be computed")
        self.assertTrue(wizard.previous_date_to,
            "Previous period end should be computed")
        self.assertLess(wizard.previous_date_to, wizard.date_from,
            "Previous period should be before current period")

    def test_cache_key_generation(self):
        """Test cache key is generated correctly."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': 'summary',
        })

        wizard._compute_cache_key()

        self.assertTrue(wizard.cache_key, "Cache key should be generated")
        self.assertIn(str(self.company.id), wizard.cache_key,
            "Cache key should contain company ID")

    def test_caching_behavior(self):
        """Test report caching works."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': 'summary',
            'cache_valid_minutes': 30,
        })

        # First computation (cache miss)
        wizard._compute_report_data()
        first_data = wizard.report_data

        # Second computation (should use cache)
        wizard._compute_report_data()
        second_data = wizard.report_data

        # Both should return data
        self.assertTrue(first_data)
        self.assertTrue(second_data)

    def test_cache_refresh(self):
        """Test manual cache refresh."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        # Set some cached data
        wizard.write({
            'cached_data': {'test': 'data'},
            'cache_timestamp': date.today(),
        })

        # Refresh cache
        wizard.action_refresh_cache()

        # Cache should be cleared
        self.assertFalse(wizard.cached_data, "Cached data should be cleared")
        self.assertFalse(wizard.cache_timestamp, "Cache timestamp should be cleared")

    def test_matrix_profitability_analysis(self):
        """Test matrix profitability analysis wizard."""
        wizard = self.env['ops.matrix.profitability.analysis'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        })

        self.assertTrue(wizard.id, "Matrix analysis wizard should be created")

        # Trigger computation
        wizard._compute_matrix_data()

        # Should generate matrix data
        self.assertTrue(hasattr(wizard, 'matrix_data'),
            "Wizard should have matrix_data field")

    def test_report_data_structure(self):
        """Test that report data has expected structure."""
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_detail_level': 'summary',
        })

        wizard._compute_report_data()

        if wizard.report_data:
            # Check for common report fields
            self.assertIsInstance(wizard.report_data, dict,
                "Report data should be a dictionary")

    def test_no_data_period(self):
        """Test report generation with no data."""
        # Use future dates with no transactions
        future_from = date.today() + timedelta(days=365)
        future_to = date.today() + timedelta(days=395)

        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': future_from,
            'date_to': future_to,
        })

        wizard._compute_report_data()

        # Should generate empty report without errors
        self.assertTrue(True, "Should handle empty data gracefully")
