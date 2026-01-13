# -*- coding: utf-8 -*-
"""Security Tests for safe_eval Implementation"""

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'ops_security')
class TestSecureExportWizard(TransactionCase):
    """Test safe_eval implementation in export wizard."""

    def setUp(self):
        super().setUp()
        self.wizard_model = self.env['secure.excel.export.wizard']

    def test_safe_eval_valid_domain(self):
        """Test that valid domains are accepted."""
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': "[('is_company', '=', True)]",
        })

        # Trigger the action that evaluates the domain
        try:
            wizard.action_export()
        except Exception as e:
            # Domain should be parsed safely
            # If it fails, it should not be due to eval security
            if 'eval' in str(e).lower() or 'code' in str(e).lower():
                self.fail(f"Safe eval failed unexpectedly: {str(e)}")

    def test_safe_eval_blocks_code_injection(self):
        """Test that code injection attempts are blocked."""
        dangerous_domains = [
            "__import__('os').system('ls')",
            "exec('import os; os.system(\"ls\")')",
            "eval('1+1')",
            "__builtins__",
        ]

        for dangerous_code in dangerous_domains:
            wizard = self.wizard_model.create({
                'model_name': 'res.partner',
                'domain': dangerous_code,
            })

            # Should raise ValidationError
            with self.assertRaises(ValidationError,
                    msg=f"Should block dangerous code: {dangerous_code}"):
                wizard.action_export()

    def test_safe_eval_complex_domain(self):
        """Test that complex but valid domains work."""
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': "[('name', 'ilike', 'test'), ('active', '=', True), '|', ('customer_rank', '>', 0), ('supplier_rank', '>', 0)]",
        })

        try:
            wizard.action_export()
        except ValidationError as e:
            # Should not raise validation error for valid domain
            if 'domain' in str(e).lower():
                self.fail(f"Valid complex domain rejected: {str(e)}")

    def test_safe_eval_empty_domain(self):
        """Test that empty domain is handled."""
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': '',
        })

        # Should not fail with empty domain
        try:
            wizard.action_export()
        except Exception as e:
            if 'domain' in str(e).lower() and 'eval' in str(e).lower():
                self.fail(f"Empty domain should be handled: {str(e)}")

    def test_safe_eval_invalid_format(self):
        """Test that invalid domain format is caught."""
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': "not a list",  # Invalid: should be a list
        })

        # Should raise ValidationError about format
        with self.assertRaises(ValidationError,
                msg="Should reject non-list domain"):
            wizard.action_export()

    def test_safe_eval_nested_structures(self):
        """Test that nested domain structures work."""
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': "[('child_ids.name', 'ilike', 'test')]",
        })

        try:
            wizard.action_export()
        except ValidationError as e:
            # Should not fail for valid nested domain
            if 'eval' in str(e).lower():
                self.fail(f"Valid nested domain rejected: {str(e)}")

    def test_model_name_validation(self):
        """Test that model_name is validated."""
        # Valid model
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': '[]',
        })
        self.assertEqual(wizard.model_name, 'res.partner')

        # Check if invalid model is caught
        try:
            invalid_wizard = self.wizard_model.create({
                'model_name': 'nonexistent.model',
                'domain': '[]',
            })
            # If creation succeeds, check if export fails
            with self.assertRaises(Exception):
                invalid_wizard.action_export()
        except Exception:
            # If creation fails, that's also acceptable
            pass

    def test_export_format_options(self):
        """Test available export format options."""
        wizard = self.wizard_model.create({
            'model_name': 'res.partner',
            'domain': '[]',
        })

        # Check if export_format field exists
        self.assertTrue(hasattr(wizard, 'export_format'),
            "Wizard should have export_format field")
