# -*- coding: utf-8 -*-
"""Security and Audit Tests"""

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install', 'ops_security')
class TestSecurityAudit(TransactionCase):
    """Test security and audit logging functionality."""

    def setUp(self):
        super().setUp()
        self.company = self.env['res.company'].create({'name': 'Test Company'})

    def test_security_rules_exist(self):
        """Test that critical security rules are defined."""
        # Check if branch access rules exist
        branch_rules = self.env['ir.rule'].search([
            ('model_id.model', '=', 'ops.branch')
        ])
        self.assertGreater(len(branch_rules), 0,
            "Branch security rules should exist")

    def test_user_dimension_fields_exist(self):
        """Test that users have matrix dimension fields."""
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@example.com',
        })

        # Check if user has matrix permission fields
        self.assertTrue(hasattr(user, 'ops_allowed_branch_ids'),
            "Users should have ops_allowed_branch_ids field")
        self.assertTrue(hasattr(user, 'ops_allowed_business_unit_ids'),
            "Users should have ops_allowed_business_unit_ids field")
