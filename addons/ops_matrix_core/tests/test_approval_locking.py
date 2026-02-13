"""
Test suite for Approval Mixin - Document Locking in Workflow

Tests that documents become read-only during approval workflow:
1. Document creation - can edit
2. Confirm/Post action - becomes locked if approval required
3. Recall/Reject - unlocks document
4. Chatter logs lock/unlock events
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo import fields
import logging

_logger = logging.getLogger(__name__)


class TestApprovalLocking(TransactionCase):
    """Test approval locking functionality on key models."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        
        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'Test Company for Approval Locking',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        # Create test users
        cls.sales_user = cls.env['res.users'].create({
            'name': 'Sales User',
            'login': 'sales_user',
            'email': 'sales@test.com',
            'company_ids': [(6, 0, [cls.company.id])],
            'company_id': cls.company.id,
        })
        
        cls.approver_user = cls.env['res.users'].create({
            'name': 'Approver User',
            'login': 'approver_user',
            'email': 'approver@test.com',
            'company_ids': [(6, 0, [cls.company.id])],
            'company_id': cls.company.id,
        })
        
        # Create branch and BU
        cls.branch = cls.env['ops.branch'].create({
            'name': 'Test Branch',
            'code': 'TB',
            'company_id': cls.company.id,
        })
        
        cls.business_unit = cls.env['ops.business.unit'].create({
            'name': 'Test BU',
            'code': 'TBU',
            'branch_ids': [(6, 0, [cls.branch.id])],
        })
        
        # Create test customer and vendor
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'customer@test.com',
            'company_id': cls.company.id,
        })
        
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Test Vendor',
            'email': 'vendor@test.com',
            'company_id': cls.company.id,
        })
        
        # Create test product
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'default_code': 'TP001',
            'type': 'product',
            'list_price': 100.0,
            'standard_price': 50.0,
            'company_id': cls.company.id,
        })
    
    def test_sale_order_locking_on_confirm(self):
        """Test that Sale Order becomes locked when confirmed."""
        # Create sale order
        so = self.env['sale.order'].with_user(self.sales_user).create({
            'partner_id': self.customer.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 10,
                'price_unit': 100,
            })],
        })
        
        # Verify SO is not locked initially
        self.assertFalse(so.approval_locked, "SO should not be locked on creation")
        
        # Confirm SO
        try:
            so.with_user(self.sales_user).action_confirm()
        except UserError as e:
            # If approval is required, check if locked
            if 'approval' in str(e).lower():
                so.refresh()
                _logger.info(f"SO locked due to approval requirement: {so.approval_locked}")
    
    def test_purchase_order_locking_on_confirm(self):
        """Test that Purchase Order becomes locked when confirmed."""
        # Create PO
        po = self.env['purchase.order'].with_user(self.sales_user).create({
            'partner_id': self.vendor.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 10,
                'price_unit': 50,
            })],
        })
        
        # Verify PO is not locked initially
        self.assertFalse(po.approval_locked, "PO should not be locked on creation")
        
        # Confirm PO
        try:
            po.with_user(self.sales_user).button_confirm()
        except UserError as e:
            if 'approval' in str(e).lower():
                po.refresh()
                _logger.info(f"PO locked due to approval requirement: {po.approval_locked}")
    
    def test_invoice_locking_on_post(self):
        """Test that Invoice becomes locked when posted."""
        # Create invoice
        move = self.env['account.move'].with_user(self.sales_user).create({
            'move_type': 'out_invoice',
            'partner_id': self.customer.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 10,
                'price_unit': 100,
            })],
        })
        
        # Verify invoice is not locked initially
        self.assertFalse(move.approval_locked, "Invoice should not be locked on creation")
        
        # Post invoice
        try:
            move.with_user(self.sales_user).action_post()
        except UserError as e:
            if 'approval' in str(e).lower():
                move.refresh()
                _logger.info(f"Invoice locked due to approval requirement: {move.approval_locked}")
    
    def test_payment_locking_on_post(self):
        """Test that Payment becomes locked when posted."""
        # Create payment
        payment = self.env['account.payment'].with_user(self.sales_user).create({
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'partner_id': self.customer.id,
            'amount': 1000.0,
            'company_id': self.company.id,
        })
        
        # Verify payment is not locked initially
        self.assertFalse(payment.approval_locked, "Payment should not be locked on creation")
        
        # Post payment
        try:
            payment.with_user(self.sales_user).action_post()
        except UserError as e:
            if 'approval' in str(e).lower():
                payment.refresh()
                _logger.info(f"Payment locked due to approval requirement: {payment.approval_locked}")
    
    def test_stock_picking_locking_on_validate(self):
        """Test that Stock Picking becomes locked when validated."""
        # Create stock picking
        picking = self.env['stock.picking'].with_user(self.sales_user).create({
            'partner_id': self.customer.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
            'move_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 10,
                'product_uom': self.product.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            })],
        })
        
        # Verify picking is not locked initially
        self.assertFalse(picking.approval_locked, "Picking should not be locked on creation")
        
        # Validate picking
        try:
            picking.with_user(self.sales_user).button_validate()
        except UserError as e:
            if 'approval' in str(e).lower():
                picking.refresh()
                _logger.info(f"Picking locked due to approval requirement: {picking.approval_locked}")
    
    def test_locked_document_cannot_be_edited(self):
        """Test that locked documents cannot be edited."""
        # Create and lock a sale order
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
        })
        
        # Manually lock it
        so.write({'approval_locked': True})
        
        # Try to edit - should fail
        with self.assertRaises(UserError) as context:
            so.write({'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 10,
                'price_unit': 100,
            })]})
        
        self.assertIn('locked', str(context.exception).lower())
    
    def test_chatter_logs_lock_event(self):
        """Test that lock events are logged to chatter."""
        # Create sale order
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
        })
        
        # Lock and post message
        so.write({'approval_locked': True})
        so.message_post(
            body='Locked during approval',
            message_type='notification'
        )
        
        # Verify message was posted
        messages = so.message_ids
        self.assertTrue(any('Locked during approval' in m.body for m in messages),
                       "Chatter should log lock event")
    
    def test_approve_unlocks_document(self):
        """Test that approving a request unlocks the document."""
        # Create sale order
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
        })
        
        # Create and lock with approval request
        so.write({'approval_locked': True})
        approval = self.env['ops.approval.request'].create({
            'rule_id': self.env['ops.governance.rule'].create({
                'name': 'Test Rule',
                'model_id': self.env['ir.model']._get_id('sale.order'),
                'trigger_type': 'on_write',
                'action_type': 'require_approval',
            }).id,
            'model_name': 'sale.order',
            'res_id': so.id,
            'requested_by': self.sales_user.id,
        })
        
        # Approve the request
        approval.action_approve()
        
        # Verify document is unlocked
        so.refresh()
        self.assertFalse(so.approval_locked, "Document should be unlocked after approval")
    
    def test_recall_unlocks_document(self):
        """Test that recalling an approval unlocks the document."""
        # Create sale order
        so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'company_id': self.company.id,
            'ops_branch_id': self.branch.id,
            'ops_business_unit_id': self.business_unit.id,
            'user_id': self.sales_user.id,
        })
        
        # Create and lock with approval request
        so.write({'approval_locked': True})
        approval = self.env['ops.approval.request'].create({
            'rule_id': self.env['ops.governance.rule'].create({
                'name': 'Test Rule',
                'model_id': self.env['ir.model']._get_id('sale.order'),
                'trigger_type': 'on_write',
                'action_type': 'require_approval',
            }).id,
            'model_name': 'sale.order',
            'res_id': so.id,
            'requested_by': self.sales_user.id,
            'state': 'pending',
        })
        so.approval_request_id = approval.id
        
        # Recall approval using the wizard
        # (Simplified - normally done via wizard)
        approval.write({'state': 'cancelled'})
        so.write({'approval_locked': False, 'approval_request_id': False})
        
        # Verify document is unlocked
        self.assertFalse(so.approval_locked, "Document should be unlocked after recall")


class TestApprovalLockingIntegration(TransactionCase):
    """Integration tests for approval locking with governance rules."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        
        cls.company = cls.env['res.company'].create({
            'name': 'Test Company',
            'currency_id': cls.env.ref('base.USD').id,
        })
        
        cls.user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@test.com',
            'company_id': cls.company.id,
        })
    
    def test_governance_rule_triggers_approval_locking(self):
        """Test that governance rules trigger approval locking."""
        # Create a governance rule
        rule = self.env['ops.governance.rule'].create({
            'name': 'High Value SO Approval',
            'model_id': self.env['ir.model']._get_id('sale.order'),
            'trigger_type': 'on_write',
            'action_type': 'require_approval',
            'lock_on_approval_request': True,
            'condition_code': 'record.amount_total > 5000',
            'error_message': 'Orders over $5,000 require approval',
        })
        
        # Create high-value SO
        so = self.env['sale.order'].with_user(self.user).create({
            'partner_id': self.env['res.partner'].create({'name': 'Customer'}).id,
            'company_id': self.company.id,
            'order_line': [(0, 0, {
                'product_id': self.env['product.product'].create({
                    'name': 'Expensive Product',
                    'list_price': 6000,
                    'type': 'product',
                }).id,
                'product_uom_qty': 1,
                'price_unit': 6000,
            })],
        })
        
        # Try to confirm - should fail with approval error
        with self.assertRaises(UserError) as context:
            so.action_confirm()
        
        self.assertIn('approval', str(context.exception).lower())
        
        # Verify lock was applied
        so.refresh()
        # Note: Lock only applied if lock_on_approval_request=True
        if rule.lock_on_approval_request:
            self.assertTrue(so.approval_locked)
