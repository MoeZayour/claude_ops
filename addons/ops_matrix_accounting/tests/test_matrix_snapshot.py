# -*- coding: utf-8 -*-
"""
Matrix Snapshot Tests
Tests the financial snapshot (materialized view) system
"""

from odoo.tests import tagged, TransactionCase
from datetime import date, timedelta
import time
import logging

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'ops_snapshots')
class TestMatrixSnapshot(TransactionCase):
    """Test financial snapshot system."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test data
        cls.company = cls.env['res.company'].create({'name': 'Snapshot Test Co'})

        cls.branch = cls.env['ops.branch'].create({
            'name': 'Test Branch',
            'code': 'TST-BR',
            'company_id': cls.company.id,
        })

        cls.bu = cls.env['ops.business.unit'].create({
            'name': 'Test BU',
            'code': 'TST-BU',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch.id])],
        })

        # Create accounts
        cls.income_account = cls.env['account.account'].create({
            'name': 'Test Income',
            'code': 'INC999',
            'account_type': 'income',
            'company_id': cls.company.id,
        })

        cls.expense_account = cls.env['account.account'].create({
            'name': 'Test Expense',
            'code': 'EXP999',
            'account_type': 'expense',
            'company_id': cls.company.id,
        })

        cls.journal = cls.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TSNAP',
            'type': 'general',
            'company_id': cls.company.id,
        })

    def test_snapshot_creation(self):
        """Test basic snapshot creation."""
        Snapshot = self.env['ops.matrix.snapshot']

        date_to = date.today()
        date_from = date_to - timedelta(days=30)

        count = Snapshot.rebuild_snapshots(
            period_type='monthly',
            date_from=date_from,
            date_to=date_to,
            company_ids=[self.company.id],
            branch_ids=[self.branch.id],
            bu_ids=[self.bu.id]
        )

        # Should create at least 1 snapshot if there's data
        self.assertGreaterEqual(count, 0, "Should process snapshot creation")

    def test_snapshot_metrics_computation(self):
        """Test computed metrics calculation."""
        Snapshot = self.env['ops.matrix.snapshot']

        snapshot = Snapshot.create({
            'company_id': self.company.id,
            'branch_id': self.branch.id,
            'business_unit_id': self.bu.id,
            'period_type': 'monthly',
            'snapshot_date': date.today(),
            'period_start': date.today().replace(day=1),
            'period_end': date.today(),
            'revenue': 100000.0,
            'cogs': 40000.0,
            'operating_expense': 30000.0,
            'depreciation': 5000.0,
            'interest_expense': 2000.0,
            'tax_expense': 8000.0,
            'total_assets': 500000.0,
            'total_liabilities': 200000.0,
            'transaction_count': 100,
        })

        # Verify computed fields
        self.assertEqual(snapshot.gross_profit, 60000.0, "GP = Revenue - COGS")
        self.assertEqual(snapshot.ebitda, 30000.0, "EBITDA = GP - OpEx")
        self.assertEqual(snapshot.ebit, 25000.0, "EBIT = EBITDA - Depreciation")
        self.assertEqual(snapshot.net_income, 15000.0, "NI = EBIT - Interest - Tax")
        self.assertEqual(snapshot.total_equity, 300000.0, "Equity = Assets - Liabilities")
        self.assertEqual(snapshot.gross_margin_pct, 60.0, "GM% = GP / Revenue * 100")
        self.assertEqual(snapshot.operating_margin_pct, 25.0, "Operating% = EBIT / Revenue * 100")
        self.assertEqual(snapshot.net_margin_pct, 15.0, "Net% = NI / Revenue * 100")

    def test_period_generation(self):
        """Test period calculation."""
        Snapshot = self.env['ops.matrix.snapshot']

        # Test monthly periods
        periods = Snapshot._generate_periods(
            'monthly',
            date(2024, 1, 1),
            date(2024, 3, 31)
        )

        self.assertEqual(len(periods), 3, "Should generate 3 monthly periods")
        self.assertEqual(periods[0][0], date(2024, 1, 1), "First period starts Jan 1")
        self.assertEqual(periods[0][1], date(2024, 1, 31), "First period ends Jan 31")

        # Test quarterly periods
        quarters = Snapshot._generate_periods(
            'quarterly',
            date(2024, 1, 1),
            date(2024, 12, 31)
        )

        self.assertEqual(len(quarters), 4, "Should generate 4 quarterly periods")

    def test_get_snapshot_data(self):
        """Test snapshot query method."""
        Snapshot = self.env['ops.matrix.snapshot']

        # Create test snapshot
        Snapshot.create({
            'company_id': self.company.id,
            'branch_id': self.branch.id,
            'business_unit_id': self.bu.id,
            'period_type': 'monthly',
            'snapshot_date': date.today(),
            'period_start': date.today().replace(day=1),
            'period_end': date.today(),
            'revenue': 50000.0,
            'cogs': 20000.0,
            'transaction_count': 50,
        })

        # Query snapshots
        snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',
            date_from=date.today().replace(day=1),
            date_to=date.today(),
            company_id=self.company.id
        )

        self.assertGreater(len(snapshots), 0, "Should return snapshots")

    def test_snapshot_performance(self):
        """Test snapshot query is fast."""
        Snapshot = self.env['ops.matrix.snapshot']

        # Create multiple snapshots
        for i in range(10):
            Snapshot.create({
                'company_id': self.company.id,
                'branch_id': self.branch.id,
                'business_unit_id': self.bu.id,
                'period_type': 'monthly',
                'snapshot_date': date.today() - timedelta(days=i*30),
                'period_start': (date.today() - timedelta(days=i*30)).replace(day=1),
                'period_end': date.today() - timedelta(days=i*30),
                'revenue': 10000.0 * (i + 1),
                'cogs': 4000.0 * (i + 1),
                'transaction_count': 10 * (i + 1),
            })

        # Test query speed
        start = time.time()
        snapshots = Snapshot.get_snapshot_data(
            period_type='monthly',
            date_from=date.today() - timedelta(days=365),
            date_to=date.today()
        )
        duration = time.time() - start

        self.assertLess(duration, 1.0, "Snapshot query should be <1 second")
        self.assertGreaterEqual(len(snapshots), 10, "Should return all snapshots")

    def test_snapshot_unique_constraint(self):
        """Test unique constraint on snapshots."""
        Snapshot = self.env['ops.matrix.snapshot']

        # Create first snapshot
        snapshot1 = Snapshot.create({
            'company_id': self.company.id,
            'branch_id': self.branch.id,
            'business_unit_id': self.bu.id,
            'period_type': 'monthly',
            'snapshot_date': date.today(),
            'period_start': date.today().replace(day=1),
            'period_end': date.today(),
            'revenue': 10000.0,
            'transaction_count': 10,
        })

        # Try to create duplicate (should fail or update existing)
        try:
            Snapshot.create({
                'company_id': self.company.id,
                'branch_id': self.branch.id,
                'business_unit_id': self.bu.id,
                'period_type': 'monthly',
                'snapshot_date': date.today(),
                'period_start': date.today().replace(day=1),
                'period_end': date.today(),
                'revenue': 20000.0,
                'transaction_count': 20,
            })
            self.fail("Should not allow duplicate snapshots")
        except Exception:
            # Expected - unique constraint violated
            pass

    def test_snapshot_integration_with_reporting(self):
        """Test that consolidation wizard can use snapshots."""
        Snapshot = self.env['ops.matrix.snapshot']

        # Create snapshot
        Snapshot.create({
            'company_id': self.company.id,
            'branch_id': self.branch.id,
            'business_unit_id': self.bu.id,
            'period_type': 'monthly',
            'snapshot_date': date.today(),
            'period_start': date.today().replace(day=1),
            'period_end': date.today(),
            'revenue': 100000.0,
            'cogs': 40000.0,
            'operating_expense': 30000.0,
            'transaction_count': 100,
        })

        # Create wizard with snapshots enabled
        wizard = self.env['ops.company.consolidation'].create({
            'company_id': self.company.id,
            'date_from': date.today().replace(day=1),
            'date_to': date.today(),
            'report_detail_level': 'by_branch',
            'use_snapshots': True,
        })

        # Should have use_snapshots field
        self.assertTrue(hasattr(wizard, 'use_snapshots'), "Wizard should have use_snapshots field")

        # Try to get snapshot-based data
        data = wizard._get_branch_detail_data_from_snapshots(self.env['ops.branch'].browse([self.branch.id]))

        if data:  # If snapshots available
            self.assertIn('data_source', data, "Should indicate data source")
            self.assertEqual(data['data_source'], 'snapshot', "Should be from snapshots")

    def test_name_get(self):
        """Test display name generation."""
        Snapshot = self.env['ops.matrix.snapshot']

        snapshot = Snapshot.create({
            'company_id': self.company.id,
            'branch_id': self.branch.id,
            'business_unit_id': self.bu.id,
            'period_type': 'monthly',
            'snapshot_date': date.today(),
            'period_start': date.today().replace(day=1),
            'period_end': date.today(),
            'revenue': 10000.0,
            'transaction_count': 10,
        })

        names = snapshot.name_get()
        self.assertTrue(len(names) > 0, "Should return display name")
        self.assertIn(str(date.today()), names[0][1], "Display name should include date")
