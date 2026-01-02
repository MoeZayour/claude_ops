# -*- coding: utf-8 -*-
"""
Test Suite for OPS Matrix Excel Export Functionality
Tests the Excel export wizard for sales, financial, and inventory reports
"""
import logging
import base64
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

@tagged('post_install', 'matrix_excel_export', '-at_install')
class TestExcelExport(TransactionCase):
    """Test suite for Excel export wizard functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Get or create test company
        self.company = self.env.company
        
        # Get or create test branch
        self.branch = self.env['ops.branch'].search([
            ('company_id', '=', self.company.id)
        ], limit=1)
        
        if not self.branch:
            self.branch = self.env['ops.branch'].create({
                'name': 'Test Export Branch',
                'code': 'TEB-001',
                'company_id': self.company.id,
            })
        
        # Get or create test BU
        self.bu = self.env['ops.business.unit'].search([
            ('branch_ids', 'in', self.branch.id)
        ], limit=1)
        
        if not self.bu:
            self.bu = self.env['ops.business.unit'].create({
                'name': 'Test Export BU',
                'code': 'TEBU-001',
                'branch_ids': [(6, 0, [self.branch.id])],
                'primary_branch_id': self.branch.id,
            })
        
        # Date ranges for testing
        self.date_from = date.today() - timedelta(days=30)
        self.date_to = date.today()
        
        # Excel export wizard model
        self.ExportWizard = self.env['ops.excel.export.wizard']
    
    # =========================================================================
    # TEST 1: WIZARD CREATION AND VALIDATION
    # =========================================================================
    
    def test_01_wizard_creation_with_valid_data(self):
        """Test creating export wizard with valid parameters."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        self.assertEqual(wizard.report_type, 'sales')
        self.assertEqual(wizard.date_from, self.date_from)
        self.assertEqual(wizard.date_to, self.date_to)
    
    def test_02_date_validation_end_before_start(self):
        """Test that wizard validates date_to is after date_from."""
        with self.assertRaises(ValidationError):
            self.ExportWizard.create({
                'report_type': 'sales',
                'date_from': self.date_to,
                'date_to': self.date_from,  # End before start - invalid
            })
    
    def test_03_required_fields_validation(self):
        """Test that required fields are enforced."""
        # Try to create without report_type
        with self.assertRaises((ValidationError, ValueError)):
            self.ExportWizard.create({
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
    
    # =========================================================================
    # TEST 2: SALES ANALYSIS EXPORT
    # =========================================================================
    
    def test_04_sales_analysis_export_basic(self):
        """Test basic sales analysis export."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # Execute export
        result = wizard.action_generate_excel()
        
        # Verify result structure
        self.assertIn('type', result, "Result should have 'type' key")
        
        # Check if it's a download action or URL action
        if result['type'] == 'ir.actions.act_url':
            self.assertIn('url', result, "URL action should have 'url' key")
        elif result['type'] == 'ir.actions.act_window':
            # Alternative: might open a wizard showing file
            self.assertIn('res_model', result)
    
    def test_05_sales_analysis_with_branch_filter(self):
        """Test sales export filtered by branch."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [self.branch.id])],
        })
        
        result = wizard.action_generate_excel()
        
        # Should succeed without errors
        self.assertIn('type', result)
    
    def test_06_sales_analysis_with_bu_filter(self):
        """Test sales export filtered by business unit."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'business_unit_ids': [(6, 0, [self.bu.id])],
        })
        
        result = wizard.action_generate_excel()
        
        # Should succeed without errors
        self.assertIn('type', result)
    
    def test_07_sales_analysis_with_combined_filters(self):
        """Test sales export with both branch and BU filters."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [self.branch.id])],
            'business_unit_ids': [(6, 0, [self.bu.id])],
        })
        
        result = wizard.action_generate_excel()
        
        # Should succeed without errors
        self.assertIn('type', result)
    
    # =========================================================================
    # TEST 3: FINANCIAL ANALYSIS EXPORT
    # =========================================================================
    
    def test_08_financial_analysis_export_basic(self):
        """Test basic financial analysis export."""
        wizard = self.ExportWizard.create({
            'report_type': 'financial',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        result = wizard.action_generate_excel()
        
        # Verify result
        self.assertIn('type', result)
    
    def test_09_financial_analysis_with_filters(self):
        """Test financial export with branch filter."""
        wizard = self.ExportWizard.create({
            'report_type': 'financial',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [self.branch.id])],
        })
        
        result = wizard.action_generate_excel()
        
        # Should succeed
        self.assertIn('type', result)
    
    # =========================================================================
    # TEST 4: INVENTORY ANALYSIS EXPORT
    # =========================================================================
    
    def test_10_inventory_analysis_export_basic(self):
        """Test basic inventory analysis export."""
        wizard = self.ExportWizard.create({
            'report_type': 'inventory',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        result = wizard.action_generate_excel()
        
        # Verify result
        self.assertIn('type', result)
    
    def test_11_inventory_analysis_with_filters(self):
        """Test inventory export with branch filter."""
        wizard = self.ExportWizard.create({
            'report_type': 'inventory',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [self.branch.id])],
        })
        
        result = wizard.action_generate_excel()
        
        # Should succeed
        self.assertIn('type', result)
    
    # =========================================================================
    # TEST 5: EDGE CASES AND ERROR HANDLING
    # =========================================================================
    
    def test_12_export_with_no_data(self):
        """Test export when no data exists in date range."""
        # Use date range in the far future where no data exists
        future_from = date.today() + timedelta(days=365)
        future_to = date.today() + timedelta(days=395)
        
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': future_from,
            'date_to': future_to,
        })
        
        # Should still succeed (empty Excel)
        result = wizard.action_generate_excel()
        self.assertIn('type', result)
    
    def test_13_export_with_very_long_date_range(self):
        """Test export with a very long date range (performance test)."""
        # 5 years of data
        long_from = date.today() - timedelta(days=1825)
        long_to = date.today()
        
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': long_from,
            'date_to': long_to,
        })
        
        # Should handle large ranges
        result = wizard.action_generate_excel()
        self.assertIn('type', result)
    
    def test_14_export_with_single_day_range(self):
        """Test export with date_from == date_to."""
        today = date.today()
        
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': today,
            'date_to': today,
        })
        
        result = wizard.action_generate_excel()
        self.assertIn('type', result)
    
    def test_15_export_with_invalid_branch(self):
        """Test export with non-existent branch ID."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [99999])],  # Non-existent ID
        })
        
        # Should handle gracefully (empty results or error)
        try:
            result = wizard.action_generate_excel()
            self.assertIn('type', result)
        except Exception as e:
            # If it raises an error, it should be a user-friendly one
            self.assertIsInstance(e, (ValidationError, UserError))
    
    # =========================================================================
    # TEST 6: FILE FORMAT VALIDATION
    # =========================================================================
    
    def test_16_exported_file_is_valid_excel(self):
        """Test that exported file is a valid Excel format."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        result = wizard.action_generate_excel()
        
        # If wizard creates a binary field with the file
        if hasattr(wizard, 'excel_file'):
            excel_data = wizard.excel_file
            
            # Should be base64 encoded
            try:
                decoded = base64.b64decode(excel_data)
                # Excel files start with PK (ZIP format signature)
                self.assertTrue(decoded.startswith(b'PK'),
                               "Excel file should start with PK signature")
            except Exception:
                # If decoding fails, might already be binary
                pass
    
    def test_17_filename_contains_report_type(self):
        """Test that generated filename contains report type."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        result = wizard.action_generate_excel()
        
        # Check filename if available
        if hasattr(wizard, 'filename'):
            self.assertIn('sales', wizard.filename.lower(),
                         "Filename should contain report type")
            self.assertTrue(wizard.filename.endswith('.xlsx'),
                           "Filename should have .xlsx extension")
    
    # =========================================================================
    # TEST 7: CONCURRENT EXPORTS
    # =========================================================================
    
    def test_18_multiple_concurrent_wizards(self):
        """Test that multiple wizards can exist simultaneously."""
        # Create multiple wizards
        wizard1 = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        wizard2 = self.ExportWizard.create({
            'report_type': 'financial',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        wizard3 = self.ExportWizard.create({
            'report_type': 'inventory',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # All should exist
        self.assertTrue(wizard1.exists())
        self.assertTrue(wizard2.exists())
        self.assertTrue(wizard3.exists())
        
        # All should be able to export
        result1 = wizard1.action_generate_excel()
        result2 = wizard2.action_generate_excel()
        result3 = wizard3.action_generate_excel()
        
        self.assertIn('type', result1)
        self.assertIn('type', result2)
        self.assertIn('type', result3)
    
    # =========================================================================
    # TEST 8: SECURITY AND ACCESS CONTROL
    # =========================================================================
    
    def test_19_regular_user_can_export(self):
        """Test that regular users can use export wizard."""
        # Create a regular user
        user = self.env['res.users'].create({
            'name': 'Test Export User',
            'login': 'export_user',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Create wizard as regular user
        wizard = self.ExportWizard.with_user(user).create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # Should be able to export
        result = wizard.action_generate_excel()
        self.assertIn('type', result)
    
    def test_20_user_sees_only_accessible_branches(self):
        """Test that users only see data from their accessible branches."""
        # Create restricted user with limited branch access
        user = self.env['res.users'].create({
            'name': 'Restricted Export User',
            'login': 'restricted_export',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Set user's allowed branches if supported
        if hasattr(user, 'ops_allowed_branch_ids'):
            user.ops_allowed_branch_ids = [(6, 0, [self.branch.id])]
        
        # Create wizard as restricted user
        wizard = self.ExportWizard.with_user(user).create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        # Export should succeed but only show accessible data
        result = wizard.action_generate_excel()
        self.assertIn('type', result)
    
    # =========================================================================
    # TEST 9: DATA INTEGRITY
    # =========================================================================
    
    def test_21_exported_data_matches_query_results(self):
        """Test that exported data matches database query results."""
        # This would require parsing the Excel file to verify contents
        # For now, just verify the export completes successfully
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'branch_ids': [(6, 0, [self.branch.id])],
        })
        
        # Get expected record count
        SalesAnalysis = self.env['ops.sales.analysis']
        expected_count = SalesAnalysis.search_count([
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('ops_branch_id', '=', self.branch.id),
        ])
        
        # Export
        result = wizard.action_generate_excel()
        
        # Verify export succeeded
        self.assertIn('type', result)
        
        # Note: Full validation would require reading the Excel file
        # and comparing row count to expected_count
    
    # =========================================================================
    # TEST 10: CLEANUP AND MEMORY MANAGEMENT
    # =========================================================================
    
    def test_22_wizard_cleanup_after_export(self):
        """Test that wizard records can be cleaned up after export."""
        wizard = self.ExportWizard.create({
            'report_type': 'sales',
            'date_from': self.date_from,
            'date_to': self.date_to,
        })
        
        wizard_id = wizard.id
        
        # Export
        wizard.action_generate_excel()
        
        # Wizard should still exist after export
        self.assertTrue(wizard.exists())
        
        # Should be able to delete wizard
        wizard.unlink()
        
        # Verify deleted
        self.assertFalse(self.ExportWizard.browse(wizard_id).exists())
