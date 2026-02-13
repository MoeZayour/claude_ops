# -*- coding: utf-8 -*-
"""Business Unit Model Tests"""

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'ops_core')
class TestBusinessUnitModel(TransactionCase):
    """Test ops.business.unit model functionality."""

    def setUp(self):
        super().setUp()
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        self.branch = self.env['ops.branch'].create({
            'name': 'Test Branch',
            'code': 'TEST',
            'company_id': self.company.id,
        })

    def test_bu_name_required(self):
        """Test that BU name is required."""
        with self.assertRaises(Exception):
            self.env['ops.business.unit'].create({'code': 'TEST'})

    def test_bu_code_required(self):
        """Test that BU code is required."""
        with self.assertRaises(Exception):
            self.env['ops.business.unit'].create({'name': 'Test BU'})

    def test_bu_active_default(self):
        """Test that BUs are active by default."""
        bu = self.env['ops.business.unit'].create({
            'name': 'Test BU',
            'code': 'TEST',
            'company_ids': [(6, 0, [self.company.id])],
            'branch_ids': [(6, 0, [self.branch.id])],
        })
        self.assertTrue(bu.active)

    def test_bu_branch_relationship(self):
        """Test BU can be linked to branches."""
        bu = self.env['ops.business.unit'].create({
            'name': 'Test BU',
            'code': 'TEST',
            'company_ids': [(6, 0, [self.company.id])],
            'branch_ids': [(6, 0, [self.branch.id])],
        })
        self.assertIn(self.branch, bu.branch_ids)
