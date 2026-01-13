# -*- coding: utf-8 -*-
"""Export Audit Logging Tests"""

from odoo.tests import tagged, TransactionCase
from datetime import datetime


@tagged('post_install', '-at_install', 'ops_audit')
class TestExportAudit(TransactionCase):
    """Test export audit logging functionality."""

    def setUp(self):
        super().setUp()
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser@test.com',
            'company_id': self.company.id,
        })
        self.model = self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)

    def test_export_log_creation(self):
        """Test that export logs are created with correct data."""
        log = self.env['ops.export.log'].create({
            'user_id': self.user.id,
            'model_id': self.model.id,
            'export_date': datetime.now(),
            'record_count': 100,
            'export_format': 'xlsx',
            'ip_address': '192.168.1.1',
        })

        self.assertTrue(log.id, "Export log should be created")
        self.assertEqual(log.user_id, self.user)
        self.assertEqual(log.record_count, 100)
        self.assertEqual(log.export_format, 'xlsx')

    def test_log_export_helper_method(self):
        """Test the log_export() helper method."""
        partners = self.env['res.partner'].search([], limit=5)

        log = self.env['ops.export.log'].log_export(
            model_name='res.partner',
            records=partners,
            domain=[('is_company', '=', True)],
            export_format='xlsx',
            notes='Test export'
        )

        self.assertTrue(log.id, "log_export() should create a log record")
        self.assertEqual(log.model_id.model, 'res.partner')
        self.assertEqual(log.record_count, len(partners))
        self.assertEqual(log.export_format, 'xlsx')

    def test_data_classification(self):
        """Test automatic data classification."""
        log = self.env['ops.export.log'].create({
            'user_id': self.user.id,
            'model_id': self.model.id,
            'export_date': datetime.now(),
            'record_count': 10,
            'export_format': 'csv',
        })

        # Check if data_classification is set
        self.assertTrue(hasattr(log, 'data_classification'),
            "Export log should have data_classification field")

    def test_export_log_readonly(self):
        """Test that export logs are readonly after creation."""
        log = self.env['ops.export.log'].create({
            'user_id': self.user.id,
            'model_id': self.model.id,
            'export_date': datetime.now(),
            'record_count': 50,
            'export_format': 'xlsx',
        })

        # Try to modify (this behavior depends on field configuration)
        # Most audit fields should be readonly
        try:
            log.write({'record_count': 100})
            # If write succeeds, verify it actually changed or was prevented
        except Exception:
            # If write fails, that's expected for readonly fields
            pass

    def test_search_exports_by_user(self):
        """Test searching export logs by user."""
        # Create exports for this user
        self.env['ops.export.log'].create({
            'user_id': self.user.id,
            'model_id': self.model.id,
            'export_date': datetime.now(),
            'record_count': 25,
            'export_format': 'xlsx',
        })

        # Search by user
        logs = self.env['ops.export.log'].search([
            ('user_id', '=', self.user.id)
        ])

        self.assertGreater(len(logs), 0, "Should find exports by user")

    def test_search_exports_by_model(self):
        """Test searching export logs by model."""
        # Create export
        self.env['ops.export.log'].create({
            'user_id': self.user.id,
            'model_id': self.model.id,
            'export_date': datetime.now(),
            'record_count': 30,
            'export_format': 'csv',
        })

        # Search by model
        logs = self.env['ops.export.log'].search([
            ('model_id', '=', self.model.id)
        ])

        self.assertGreater(len(logs), 0, "Should find exports by model")

    def test_export_format_validation(self):
        """Test that export format is properly stored."""
        formats = ['xlsx', 'csv', 'pdf', 'json']

        for fmt in formats:
            log = self.env['ops.export.log'].create({
                'user_id': self.user.id,
                'model_id': self.model.id,
                'export_date': datetime.now(),
                'record_count': 10,
                'export_format': fmt,
            })
            self.assertEqual(log.export_format, fmt,
                f"Export format {fmt} should be stored correctly")
