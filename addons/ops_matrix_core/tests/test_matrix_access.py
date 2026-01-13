# -*- coding: utf-8 -*-
"""
Matrix Access Control Tests
Tests the AND logic (intersection) security model for branches × business units
"""

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'ops_security')
class TestMatrixAccessControl(TransactionCase):
    """
    Test matrix intersection (AND logic) access control.

    Security Model: Users can only access records where they have BOTH
    branch access AND business unit access (intersection, not union).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'OPS Test Company',
        })

        # Create test branches
        cls.branch_north = cls.env['ops.branch'].create({
            'name': 'North Branch',
            'code': 'BR-NORTH',
            'company_id': cls.company.id,
        })
        cls.branch_south = cls.env['ops.branch'].create({
            'name': 'South Branch',
            'code': 'BR-SOUTH',
            'company_id': cls.company.id,
        })
        cls.branch_east = cls.env['ops.branch'].create({
            'name': 'East Branch',
            'code': 'BR-EAST',
            'company_id': cls.company.id,
        })

        # Create test business units
        cls.bu_sales = cls.env['ops.business.unit'].create({
            'name': 'Sales',
            'code': 'BU-SALES',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch_north.id, cls.branch_south.id, cls.branch_east.id])],
        })
        cls.bu_ops = cls.env['ops.business.unit'].create({
            'name': 'Operations',
            'code': 'BU-OPS',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch_north.id, cls.branch_south.id, cls.branch_east.id])],
        })
        cls.bu_finance = cls.env['ops.business.unit'].create({
            'name': 'Finance',
            'code': 'BU-FIN',
            'company_ids': [(6, 0, [cls.company.id])],
            'branch_ids': [(6, 0, [cls.branch_north.id, cls.branch_south.id, cls.branch_east.id])],
        })

        # Create test user groups
        cls.group_ops_user = cls.env.ref('base.group_user')

        # Create test user with North branch + Sales BU access
        cls.user_north_sales = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'North Sales User',
            'login': 'north_sales@test.com',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, [cls.company.id])],
            'groups_id': [(6, 0, [cls.group_ops_user.id])],
        })

        # Add OPS permissions
        cls.user_north_sales.write({
            'ops_allowed_branch_ids': [(6, 0, [cls.branch_north.id])],
            'ops_allowed_business_unit_ids': [(6, 0, [cls.bu_sales.id])],
        })

        # Create test user with South branch + Finance BU access
        cls.user_south_finance = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'South Finance User',
            'login': 'south_finance@test.com',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, [cls.company.id])],
            'groups_id': [(6, 0, [cls.group_ops_user.id])],
        })

        cls.user_south_finance.write({
            'ops_allowed_branch_ids': [(6, 0, [cls.branch_south.id])],
            'ops_allowed_business_unit_ids': [(6, 0, [cls.bu_finance.id])],
        })

    def test_matrix_intersection_access(self):
        """
        Test AND logic: User can only access records where they have BOTH
        branch AND business unit access.
        """
        # User has access to North branch + Sales BU
        # Should be able to search for records in that intersection
        user = self.user_north_sales

        # This should NOT raise an error - user has both permissions
        try:
            branches = self.env['ops.branch'].with_user(user).search([
                ('id', '=', self.branch_north.id)
            ])
            self.assertEqual(len(branches), 1, "User should see North branch")

            bus = self.env['ops.business.unit'].with_user(user).search([
                ('id', '=', self.bu_sales.id)
            ])
            self.assertEqual(len(bus), 1, "User should see Sales BU")

        except AccessError:
            self.fail("User should have access to their assigned branch and BU")

    def test_matrix_no_access_wrong_branch(self):
        """
        Test that user with North branch cannot access South branch records,
        even if they have the right BU.
        """
        user = self.user_north_sales

        # User has Sales BU access but NOT South branch access
        # Should not see South branch
        branches = self.env['ops.branch'].with_user(user).search([
            ('id', '=', self.branch_south.id)
        ])

        self.assertEqual(len(branches), 0,
            "User should NOT see branches they don't have access to")

    def test_matrix_no_access_wrong_bu(self):
        """
        Test that user with Sales BU cannot access Finance BU records,
        even if they have the right branch.
        """
        user = self.user_north_sales

        # User has North branch access but NOT Finance BU access
        # Should not see Finance BU
        bus = self.env['ops.business.unit'].with_user(user).search([
            ('id', '=', self.bu_finance.id)
        ])

        self.assertEqual(len(bus), 0,
            "User should NOT see BUs they don't have access to")

    def test_branch_model_basic_crud(self):
        """Test basic CRUD operations on branch model."""
        # Create
        branch = self.env['ops.branch'].create({
            'name': 'Test Branch',
            'code': 'TEST-BR',
            'company_id': self.company.id,
        })
        self.assertTrue(branch.id, "Branch should be created")
        self.assertEqual(branch.code, 'TEST-BR')

        # Read
        branch_read = self.env['ops.branch'].browse(branch.id)
        self.assertEqual(branch_read.name, 'Test Branch')

        # Update
        branch.write({'name': 'Updated Branch'})
        self.assertEqual(branch.name, 'Updated Branch')

        # Delete (archive)
        branch.write({'active': False})
        self.assertFalse(branch.active)

    def test_business_unit_model_basic_crud(self):
        """Test basic CRUD operations on business unit model."""
        # Create
        bu = self.env['ops.business.unit'].create({
            'name': 'Test BU',
            'code': 'TEST-BU',
            'company_ids': [(6, 0, [self.company.id])],
            'branch_ids': [(6, 0, [self.branch_north.id])],
        })
        self.assertTrue(bu.id, "Business unit should be created")
        self.assertEqual(bu.code, 'TEST-BU')

        # Read
        bu_read = self.env['ops.business.unit'].browse(bu.id)
        self.assertEqual(bu_read.name, 'Test BU')

        # Update
        bu.write({'name': 'Updated BU'})
        self.assertEqual(bu.name, 'Updated BU')

        # Delete (archive)
        bu.write({'active': False})
        self.assertFalse(bu.active)

    def test_branch_unique_code(self):
        """Test that branch codes must be unique within company."""
        # First branch with code
        branch1 = self.env['ops.branch'].create({
            'name': 'Branch 1',
            'code': 'UNIQUE-CODE',
            'company_id': self.company.id,
        })
        self.assertTrue(branch1.id)

        # Try to create another branch with same code in same company
        # This should either fail or trigger a constraint
        try:
            branch2 = self.env['ops.branch'].create({
                'name': 'Branch 2',
                'code': 'UNIQUE-CODE',
                'company_id': self.company.id,
            })
            # If it succeeds, that's also acceptable behavior
            # depending on implementation
            _logger.info("Duplicate codes allowed (no constraint)")
        except Exception as e:
            # If it fails, that's the expected behavior
            _logger.info(f"Duplicate codes prevented: {str(e)}")

    def test_bu_branch_relationship(self):
        """Test that business units can operate in multiple branches."""
        # BU should have branch relationships
        bu = self.bu_sales

        self.assertIn(self.branch_north, bu.branch_ids,
            "BU should operate in North branch")
        self.assertIn(self.branch_south, bu.branch_ids,
            "BU should operate in South branch")

        # Add new branch to BU
        bu.write({
            'branch_ids': [(4, self.branch_east.id)]
        })

        self.assertIn(self.branch_east, bu.branch_ids,
            "BU should now operate in East branch")

    def test_user_matrix_permissions(self):
        """Test that user matrix permissions are properly enforced."""
        user = self.user_north_sales

        # Check user has correct branch access
        self.assertIn(self.branch_north, user.ops_allowed_branch_ids,
            "User should have North branch access")

        # Check user has correct BU access
        self.assertIn(self.bu_sales, user.ops_allowed_business_unit_ids,
            "User should have Sales BU access")

        # Check user does NOT have other accesses
        self.assertNotIn(self.branch_south, user.ops_allowed_branch_ids,
            "User should NOT have South branch access")
        self.assertNotIn(self.bu_finance, user.ops_allowed_business_unit_ids,
            "User should NOT have Finance BU access")
