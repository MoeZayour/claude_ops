# -*- coding: utf-8 -*-
"""
Trend Analysis Tests
Tests the trend analysis and variance reporting functionality
"""

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'ops_trends')
class TestTrendAnalysis(TransactionCase):
    """Test trend analysis wizard."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test data
        cls.company = cls.env['res.company'].create({'name': 'Trend Test Co'})

        cls.branch1 = cls.env['ops.branch'].create({
            'name': 'Branch A',
            'code': 'BRA',
            'company_id': cls.company.id,
        })

        cls.branch2 = cls.env['ops.branch'].create({
            'name': 'Branch B',
            'code': 'BRB',
            'company_id': cls.company.id,
        })

        cls.bu1 = cls.env['ops.business.unit'].create({
            'name': 'BU Alpha',
            'code': 'BU-A',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch1.id, cls.branch2.id])],
        })

        cls.bu2 = cls.env['ops.business.unit'].create({
            'name': 'BU Beta',
            'code': 'BU-B',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch1.id])],
        })

        # Create test snapshots for current month
        cls.current_month_start = date.today().replace(day=1)
        cls.current_month_end = date.today()

        cls.Snapshot = cls.env['ops.matrix.snapshot']

        # Current period snapshots
        cls.snapshot_current_1 = cls.Snapshot.create({
            'company_id': cls.company.id,
            'branch_id': cls.branch1.id,
            'business_unit_id': cls.bu1.id,
            'period_type': 'monthly',
            'snapshot_date': cls.current_month_end,
            'period_start': cls.current_month_start,
            'period_end': cls.current_month_end,
            'revenue': 100000.0,
            'cogs': 40000.0,
            'operating_expense': 30000.0,
            'transaction_count': 100,
        })

        cls.snapshot_current_2 = cls.Snapshot.create({
            'company_id': cls.company.id,
            'branch_id': cls.branch2.id,
            'business_unit_id': cls.bu1.id,
            'period_type': 'monthly',
            'snapshot_date': cls.current_month_end,
            'period_start': cls.current_month_start,
            'period_end': cls.current_month_end,
            'revenue': 80000.0,
            'cogs': 32000.0,
            'operating_expense': 24000.0,
            'transaction_count': 80,
        })

        # Previous month snapshots (MoM comparison)
        cls.prev_month_end = cls.current_month_start - timedelta(days=1)
        cls.prev_month_start = cls.prev_month_end.replace(day=1)

        cls.snapshot_prev_1 = cls.Snapshot.create({
            'company_id': cls.company.id,
            'branch_id': cls.branch1.id,
            'business_unit_id': cls.bu1.id,
            'period_type': 'monthly',
            'snapshot_date': cls.prev_month_end,
            'period_start': cls.prev_month_start,
            'period_end': cls.prev_month_end,
            'revenue': 90000.0,
            'cogs': 36000.0,
            'operating_expense': 27000.0,
            'transaction_count': 90,
        })

        cls.snapshot_prev_2 = cls.Snapshot.create({
            'company_id': cls.company.id,
            'branch_id': cls.branch2.id,
            'business_unit_id': cls.bu1.id,
            'period_type': 'monthly',
            'snapshot_date': cls.prev_month_end,
            'period_start': cls.prev_month_start,
            'period_end': cls.prev_month_end,
            'revenue': 75000.0,
            'cogs': 30000.0,
            'operating_expense': 22500.0,
            'transaction_count': 75,
        })

        # Last year snapshots (YoY comparison)
        cls.yoy_start = cls.current_month_start - relativedelta(years=1)
        cls.yoy_end = cls.current_month_end - relativedelta(years=1)

        cls.snapshot_yoy_1 = cls.Snapshot.create({
            'company_id': cls.company.id,
            'branch_id': cls.branch1.id,
            'business_unit_id': cls.bu1.id,
            'period_type': 'monthly',
            'snapshot_date': cls.yoy_end,
            'period_start': cls.yoy_start,
            'period_end': cls.yoy_end,
            'revenue': 80000.0,
            'cogs': 32000.0,
            'operating_expense': 24000.0,
            'transaction_count': 80,
        })

    def test_wizard_creation(self):
        """Test basic wizard creation."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
        })

        self.assertTrue(wizard.id, "Wizard should be created")
        self.assertEqual(wizard.comparison_type, 'mom')

    def test_comparison_dates_mom(self):
        """Test automatic MoM comparison date calculation."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
        })

        # Should auto-calculate previous month
        self.assertEqual(
            wizard.auto_comparison_start,
            self.prev_month_start,
            "Should calculate previous month start"
        )
        self.assertEqual(
            wizard.auto_comparison_end,
            self.prev_month_end,
            "Should calculate previous month end"
        )

    def test_comparison_dates_yoy(self):
        """Test automatic YoY comparison date calculation."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'yoy',
        })

        # Should auto-calculate same period last year
        self.assertEqual(
            wizard.auto_comparison_start,
            self.yoy_start,
            "Should calculate same period last year start"
        )
        self.assertEqual(
            wizard.auto_comparison_end,
            self.yoy_end,
            "Should calculate same period last year end"
        )

    def test_comparison_dates_qoq(self):
        """Test automatic QoQ comparison date calculation."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': date(2024, 7, 1),
            'current_period_end': date(2024, 9, 30),
            'comparison_type': 'qoq',
        })

        # Should calculate previous quarter (April-June)
        expected_start = date(2024, 4, 1)
        self.assertEqual(
            wizard.auto_comparison_start,
            expected_start,
            "Should calculate previous quarter start"
        )

    def test_trend_data_with_snapshots_total(self):
        """Test trend analysis with snapshots (total grouping)."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        # Trigger computation
        trend_data = wizard.trend_data

        self.assertTrue(trend_data, "Should have trend data")
        self.assertEqual(wizard.data_source, 'snapshot', "Should use snapshots")
        self.assertIn('items', trend_data, "Should have items")
        self.assertIn('summary', trend_data, "Should have summary")

    def test_trend_data_by_branch(self):
        """Test trend analysis grouped by branch."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'branch',
        })

        trend_data = wizard.trend_data

        self.assertTrue(trend_data, "Should have trend data")
        self.assertGreaterEqual(len(trend_data.get('items', [])), 1, "Should have branch items")

        # Check that items have dimension info
        for item in trend_data['items']:
            if 'dimension' in item:
                self.assertEqual(item['dimension'], 'branch', "Should be branch dimension")

    def test_trend_data_by_bu(self):
        """Test trend analysis grouped by business unit."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'bu',
        })

        trend_data = wizard.trend_data

        self.assertTrue(trend_data, "Should have trend data")
        items = trend_data.get('items', [])

        # Check for BU dimension
        for item in items:
            if 'dimension' in item:
                self.assertEqual(item['dimension'], 'bu', "Should be BU dimension")

    def test_variance_calculation(self):
        """Test variance calculation logic."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        trend_data = wizard.trend_data

        # Check summary contains growth metrics
        summary = trend_data.get('summary', {})
        self.assertIn('revenue_growth_pct', summary, "Should have revenue growth %")
        self.assertIn('net_income_growth_pct', summary, "Should have net income growth %")

        # Since current period has higher revenue than previous,
        # revenue growth should be positive
        self.assertGreater(
            summary['revenue_growth_pct'],
            0,
            "Revenue should have positive growth"
        )

    def test_variance_items_structure(self):
        """Test structure of variance items."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        trend_data = wizard.trend_data
        items = trend_data.get('items', [])

        self.assertGreater(len(items), 0, "Should have at least one item")

        item = items[0]
        self.assertIn('current', item, "Should have current period data")
        self.assertIn('comparison', item, "Should have comparison period data")
        self.assertIn('variance', item, "Should have variance data")

        # Check variance structure
        variance = item['variance']
        if 'revenue' in variance:
            self.assertIn('absolute', variance['revenue'], "Should have absolute variance")
            self.assertIn('percentage', variance['revenue'], "Should have percentage variance")
            self.assertIn('direction', variance['revenue'], "Should have direction indicator")

    def test_metric_filtering(self):
        """Test that only selected metrics are included."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'total',
            'show_revenue': True,
            'show_cogs': False,
            'show_gross_profit': False,
            'show_operating_expense': False,
            'show_ebitda': False,
            'show_net_income': True,
            'show_margins': False,
        })

        trend_data = wizard.trend_data
        items = trend_data.get('items', [])

        if items:
            item = items[0]
            current = item.get('current', {})

            # Should have revenue (enabled)
            self.assertIn('revenue', current, "Should include revenue")

            # Should have net_income (enabled)
            self.assertIn('net_income', current, "Should include net_income")

            # Should NOT have COGS (disabled)
            self.assertNotIn('cogs', current, "Should NOT include COGS")

    def test_yoy_trend_analysis(self):
        """Test Year-over-Year trend analysis."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'yoy',
            'group_by': 'total',
        })

        trend_data = wizard.trend_data

        self.assertTrue(trend_data, "Should have YoY trend data")
        self.assertEqual(wizard.data_source, 'snapshot', "Should use snapshots for YoY")

        # YoY should show significant growth (100K vs 80K revenue)
        summary = trend_data.get('summary', {})
        if summary:
            self.assertGreater(
                summary.get('revenue_growth_pct', 0),
                0,
                "Should show positive YoY growth"
            )

    def test_custom_period_comparison(self):
        """Test custom period comparison."""
        custom_start = date(2024, 1, 1)
        custom_end = date(2024, 1, 31)

        # Create snapshot for custom period
        self.Snapshot.create({
            'company_id': self.company.id,
            'branch_id': self.branch1.id,
            'business_unit_id': self.bu1.id,
            'period_type': 'monthly',
            'snapshot_date': custom_end,
            'period_start': custom_start,
            'period_end': custom_end,
            'revenue': 70000.0,
            'cogs': 28000.0,
            'operating_expense': 21000.0,
            'transaction_count': 70,
        })

        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'custom',
            'comparison_period_start': custom_start,
            'comparison_period_end': custom_end,
            'group_by': 'total',
        })

        trend_data = wizard.trend_data

        self.assertTrue(trend_data, "Should have custom period trend data")

    def test_branch_filter(self):
        """Test filtering by specific branches."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'branch',
            'branch_ids': [(6, 0, [self.branch1.id])],
        })

        trend_data = wizard.trend_data
        items = trend_data.get('items', [])

        # Should only have branch1 data
        self.assertEqual(len(items), 1, "Should only have one branch")

    def test_empty_metrics_handling(self):
        """Test handling of empty/zero metrics."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': date.today() + timedelta(days=365),
            'current_period_end': date.today() + timedelta(days=395),
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        # Should not crash even with no data
        trend_data = wizard.trend_data

        # May fall back to realtime (which has no data)
        # or return empty structure
        self.assertIsNotNone(trend_data)

    def test_action_generate_report(self):
        """Test report generation action."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        action = wizard.action_generate_report()

        self.assertEqual(action['type'], 'ir.actions.client', "Should return client action")
        self.assertIn('params', action, "Should have params")

    def test_realtime_fallback(self):
        """Test fallback to real-time when snapshots unavailable."""
        # Create wizard with future dates (no snapshots)
        future_date = date.today() + timedelta(days=365)

        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': future_date.replace(day=1),
            'current_period_end': future_date,
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        # Should fall back to realtime (even if no data)
        # Just verify it doesn't crash
        trend_data = wizard.trend_data
        self.assertIsNotNone(trend_data)

    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'branch',
        })

        trend_data = wizard.trend_data
        summary = trend_data.get('summary', {})

        # Should have aggregated totals
        self.assertIn('total_current_revenue', summary)
        self.assertIn('total_comparison_revenue', summary)
        self.assertIn('item_count', summary)

        # Should identify best/worst performers
        if summary.get('item_count', 0) > 0:
            self.assertIn('best_performer', summary)
            self.assertIn('worst_performer', summary)

    def test_direction_indicators(self):
        """Test that direction indicators are correctly set."""
        wizard = self.env['ops.trend.analysis'].create({
            'company_id': self.company.id,
            'current_period_start': self.current_month_start,
            'current_period_end': self.current_month_end,
            'comparison_type': 'mom',
            'group_by': 'total',
        })

        trend_data = wizard.trend_data
        items = trend_data.get('items', [])

        if items:
            item = items[0]
            variance = item.get('variance', {})

            if 'revenue' in variance:
                direction = variance['revenue']['direction']
                self.assertIn(direction, ['up', 'down', 'flat'], "Direction should be valid")

                # Check consistency
                if variance['revenue']['absolute'] > 0:
                    self.assertEqual(direction, 'up', "Positive variance should be 'up'")
                elif variance['revenue']['absolute'] < 0:
                    self.assertEqual(direction, 'down', "Negative variance should be 'down'")
                else:
                    self.assertEqual(direction, 'flat', "Zero variance should be 'flat'")
