# -*- coding: utf-8 -*-
"""Branch Model Tests"""

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'ops_core')
class TestBranchModel(TransactionCase):
    """Test ops.branch model functionality."""

    def setUp(self):
        super().setUp()
        self.company = self.env['res.company'].create({'name': 'Test Company'})

    def test_branch_name_required(self):
        """Test that branch name is required."""
        with self.assertRaises(Exception):
            self.env['ops.branch'].create({'code': 'TEST'})

    def test_branch_code_required(self):
        """Test that branch code is required."""
        with self.assertRaises(Exception):
            self.env['ops.branch'].create({'name': 'Test Branch'})

    def test_branch_active_default(self):
        """Test that branches are active by default."""
        branch = self.env['ops.branch'].create({
            'name': 'Test Branch',
            'code': 'TEST',
            'company_id': self.company.id,
        })
        self.assertTrue(branch.active)
