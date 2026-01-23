from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from typing import List, Dict, Any, Tuple
import base64
import io
import logging

_logger = logging.getLogger(__name__)
try:
    from pypdf import PdfMerger
except ImportError:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        PdfMerger = None

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'ops.governance.mixin', 'ops.matrix.mixin', 'ops.approval.mixin', 'ops.segregation.of.duties.mixin']

    # ==========================================================================
    # DEFAULT VALUES: Automatically inherit matrix dimensions from user
    # ==========================================================================
    @api.model
    def default_get(self, fields_list):
        """
        Override default_get to automatically populate matrix dimensions
        from the current user's default branch and business unit.

        This ensures:
        1. Sales orders inherit the user's primary branch by default
        2. Sales orders inherit the user's default business unit by default
        3. Users don't have to manually select these on every order
        """
        defaults = super().default_get(fields_list)
        user = self.env.user

        # Auto-populate ops_branch_id from user's primary branch or default branch
        if 'ops_branch_id' in fields_list and not defaults.get('ops_branch_id'):
            branch_id = user.primary_branch_id.id or user.ops_default_branch_id.id
            if branch_id:
                defaults['ops_branch_id'] = branch_id

        # Auto-populate ops_business_unit_id from user's default business unit
        if 'ops_business_unit_id' in fields_list and not defaults.get('ops_business_unit_id'):
            bu_id = user.ops_default_business_unit_id.id
            if bu_id:
                defaults['ops_business_unit_id'] = bu_id

        return defaults

    # ==========================================================================
    # STATE EXTENSION: Add 'waiting_approval' state for governance workflow
    # ==========================================================================
    state = fields.Selection(
        selection_add=[
            ('waiting_approval', 'Waiting Approval'),
        ],
        ondelete={'waiting_approval': 'set default'}
    )

    # ==========================================================================
    # REQUIRED MATRIX DIMENSIONS: Override mixin fields to enforce at DB level
    # ==========================================================================
    # These fields are inherited from ops.matrix.mixin but we override them
    # to make them REQUIRED at the database level for sale.order
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
        help='Branch where this sale order originates. Required for all orders.'
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
        help='Business Unit responsible for this sale order. Required for all orders.'
    )

    # Additional sale order specific fields
    ops_credit_check_passed = fields.Boolean(
        string='Credit Check Passed',
        default=False,
        readonly=True,
        help='Indicates if partner passed credit firewall check'
    )
    ops_credit_check_notes = fields.Text(
        string='Credit Check Notes',
        readonly=True,
        help='Notes from credit firewall evaluation'
    )

    # Approval request link (computed for convenience)
    approval_request_ids = fields.One2many(
        'ops.approval.request',
        compute='_compute_approval_request_ids',
        string='Approval Requests'
    )
    approval_request_count = fields.Integer(
        compute='_compute_approval_request_ids',
        string='Approval Count'
    )

    def _compute_approval_request_ids(self):
        """Compute approval requests linked to this sale order."""
        ApprovalRequest = self.env['ops.approval.request']
        for order in self:
            requests = ApprovalRequest.search([
                ('model_name', '=', 'sale.order'),
                ('res_id', '=', order.id)
            ])
            order.approval_request_ids = requests
            order.approval_request_count = len(requests)

    @api.constrains('ops_branch_id', 'ops_business_unit_id')
    def _check_matrix_dimensions_required(self) -> None:
        """
        IRON LOCK: Enforce that Branch and Business Unit are always set on save.

        This constraint prevents sales orders from being saved without
        proper matrix dimensions, ensuring full governance tracking.

        Exemptions:
        - Superuser/Admin bypass for system operations
        """
        for order in self:
            # Skip checks for superuser/admin
            if order.env.is_superuser() or order.env.user.has_group('base.group_system'):
                continue

            if not order.ops_branch_id:
                raise ValidationError(_(
                    "🔒 GOVERNANCE VIOLATION: Branch is required!\n\n"
                    "Order '%(order_name)s' cannot be saved without a Branch.\n\n"
                    "Please select a Branch in the Matrix Dimensions section."
                ) % {'order_name': order.name or 'New'})

            if not order.ops_business_unit_id:
                raise ValidationError(_(
                    "🔒 GOVERNANCE VIOLATION: Business Unit is required!\n\n"
                    "Order '%(order_name)s' cannot be saved without a Business Unit.\n\n"
                    "Please select a Business Unit in the Matrix Dimensions section."
                ) % {'order_name': order.name or 'New'})

    @api.constrains('order_line')
    def _check_business_unit_silo(self) -> None:
        """
        Strictly enforce that a user can only sell products belonging to
        their allowed Business Units.

        Note: This constraint works alongside the governance rules engine.
        For more complex rules, use ops.governance.rule instead.
        """
        for order in self:
            # Skip check for Superuser/Admin to allow setup
            if order.env.is_superuser():
                continue

            # Get user's allowed units (from persona or legacy fields)
            effective_access = order.user_id.get_effective_matrix_access()
            user_allowed_units = effective_access['business_unit_ids'].ids if effective_access['business_unit_ids'] else []
            
            for line in order.order_line:
                product_unit = line.product_id.business_unit_id
                
                # If product has a unit, and it's not in user's allowed list
                if product_unit and product_unit.id not in user_allowed_units:
                    raise ValidationError(_(
                        "SILO VIOLATION: You cannot sell product '%s' (Unit: %s). "
                        "You are not assigned to this Business Unit."
                    ) % (line.product_id.name, product_unit.name))

    def _get_products_availability_data(self) -> List[Dict[str, Any]]:
        """
        Task 4: Prepare data for Products Availability Report.
        Returns availability data for each storable product in the sale order.
        """
        self.ensure_one()
        availability_data = []
        
        for line in self.order_line:
            product = line.product_id
            
            # Skip service and consumable products
            if product.type in ['service', 'consu']:
                continue
            
            # Get stock on hand for the product
            stock_on_hand = product.qty_available
            
            # Calculate display qty = min(ordered qty, stock on hand)
            display_qty = min(line.product_uom_qty, stock_on_hand)
            
            # Determine if stock is insufficient (for styling)
            is_insufficient = stock_on_hand < line.product_uom_qty
            
            availability_data.append({
                'sku': product.default_code or '',
                'product_name': product.name,
                'ordered_qty': line.product_uom_qty,
                'stock_on_hand': stock_on_hand,
                'display_qty': display_qty,
                'is_insufficient': is_insufficient,
            })
        
        return availability_data

    @api.model
    def _get_unique_product_documents(self):
        """Get unique documents from all order lines, removing duplicates"""
        documents = {}
        
        for line in self.order_line:
            # Check for product documents - if the field exists (Odoo 18+ feature or custom)
            # In Odoo 19, product documents are standard.
            if line.product_id and hasattr(line.product_id, 'product_document_ids'):
                for doc in line.product_id.product_document_ids:
                    # In Odoo 19, product.document has 'show_in_quotation'
                    if (not hasattr(doc, 'show_in_quotation') or doc.show_in_quotation) and doc.id not in documents:
                        documents[doc.id] = {
                            'name': doc.name,
                            'product_ids': [line.product_id]
                        }
                    elif doc.id in documents:
                        documents[doc.id]['product_ids'].append(line.product_id)
        
        return list(documents.values())

    def _is_immediate_payment_term(self) -> bool:
        """
        SMART GATE HELPER: Determine if the payment term is immediate/cash.

        Immediate payment terms have:
        1. No payment term set (defaults to immediate)
        2. Payment term with 0 days due
        3. Payment term name containing 'immediate', 'cash', 'prepaid', 'advance'

        Returns:
            bool: True if this is an immediate/cash transaction
        """
        self.ensure_one()
        payment_term = self.payment_term_id

        # No payment term = immediate payment
        if not payment_term:
            return True

        # Check payment term name for cash/immediate keywords
        term_name = (payment_term.name or '').lower()
        cash_keywords = ['immediate', 'cash', 'prepaid', 'advance', 'cod', 'upon receipt', 'due immediately']
        if any(kw in term_name for kw in cash_keywords):
            return True

        # Check if all payment lines have 0 days due
        if payment_term.line_ids:
            max_days = max(line.nb_days for line in payment_term.line_ids)
            if max_days == 0:
                return True

        return False

    def _check_partner_credit_firewall(self) -> Tuple[bool, str, bool]:
        """
        Credit Firewall: Check if partner can have this order confirmed.

        Returns tuple of (passed: bool, message: str, is_warning_only: bool)

        SMART GATE LOGIC ("Speed at Quote, Governance at Credit"):
        - CASH/Immediate Payment: Allow confirmation even for unverified customers
        - CREDIT Transactions: Block if customer is NOT Master Verified

        This enables:
        - Walk-in sales and cash transactions to flow freely
        - Credit/receivables transactions to require proper customer verification
        """
        self.ensure_one()

        if self.env.is_superuser():
            return True, 'Superuser bypass', False

        partner = self.partner_id
        is_cash_transaction = self._is_immediate_payment_term()

        # ======================================================================
        # SMART GATE: Master Data Verification Check
        # ======================================================================
        # Cash transactions bypass the verification requirement
        # Credit transactions require Master Verified = True
        # ======================================================================
        if hasattr(partner, 'ops_master_verified'):
            if not partner.ops_master_verified:
                if is_cash_transaction:
                    # CASH GATE: Allow cash transactions for unverified customers
                    return True, (
                        f"✅ CASH GATE PASSED: Customer '{partner.name}' is NOT Master Verified, "
                        f"but payment is immediate/cash. Transaction allowed."
                    ), False
                else:
                    # CREDIT GATE: Block credit transactions for unverified customers
                    payment_term_name = self.payment_term_id.name if self.payment_term_id else 'Not Set'
                    return False, (
                        f"🚫 CREDIT TRANSACTION BLOCKED\n\n"
                        f"Customer '{partner.name}' is NOT MASTER VERIFIED.\n\n"
                        f"Payment Term: {payment_term_name}\n\n"
                        f"SMART GATE RULE:\n"
                        f"• Credit transactions require Master Data verification\n"
                        f"• Cash/Immediate transactions are allowed for any customer\n\n"
                        f"OPTIONS:\n"
                        f"1. Change Payment Term to 'Immediate Payment' or 'Cash'\n"
                        f"2. Contact Finance to verify customer '{partner.name}'"
                    ), False

        # Check 1: Partner Stewardship State (soft-pass draft for branch users)
        # These remain HARD BLOCKS - cannot confirm orders for blocked/archived partners
        if hasattr(partner, 'ops_state'):
            if partner.ops_state == 'blocked':
                return False, 'Partner is blocked from transactions', False
            if partner.ops_state == 'archived':
                return False, 'Partner is archived', False

            # Allow draft partners to proceed but log the state for auditing
            if partner.ops_state == 'draft':
                return True, 'Partner in draft state - soft-pass credit firewall', False

            # Any other non-approved state is blocked
            if partner.ops_state not in ['approved']:
                return False, f'Partner state is "{partner.ops_state}" - orders cannot be confirmed', False

        # Check 2: Partner Activity - HARD BLOCK
        if not partner.active:
            return False, 'Partner is inactive', False

        # Check 3: Credit Limit Enforcement - NOW WARNING ONLY
        # The hard block is enforced at Picking validation (button_validate)
        if hasattr(partner, 'ops_credit_limit') and hasattr(partner, 'ops_total_outstanding'):
            if partner.ops_credit_limit > 0:
                total_outstanding = partner.ops_total_outstanding
                potential_total = total_outstanding + self.amount_total

                if potential_total > partner.ops_credit_limit:
                    # Return as WARNING ONLY - order can still be confirmed
                    return True, (
                        f'⚠️ CREDIT WARNING: This order would exceed credit limit. '
                        f'Current outstanding: {total_outstanding:.2f}, '
                        f'Order amount: {self.amount_total:.2f}, '
                        f'Credit limit: {partner.ops_credit_limit:.2f}. '
                        f'NOTE: Delivery will be BLOCKED until credit is cleared.'
                    ), True

        # Check 4: Partner Confirmation Restrictions (if field exists) - HARD BLOCK
        if hasattr(partner, 'ops_confirmation_restrictions'):
            if partner.ops_confirmation_restrictions:
                return False, f'Partner restrictions: {partner.ops_confirmation_restrictions}', False

        return True, 'Credit check passed', False

    def _evaluate_governance_rules_for_confirm(self) -> bool:
        """
        GOVERNANCE INTERCEPTOR: Evaluate governance rules BEFORE confirmation.

        This method is called BEFORE super().action_confirm() to ensure that:
        1. Rules like ">$10K requires approval" are evaluated
        2. If approval is required, the order transitions to 'waiting_approval'
        3. An approval request is created and linked to the order
        4. The confirmation is blocked until approval is granted

        Returns:
            bool: True if approval is required (confirmation should be blocked),
                  False if no approval is needed (confirmation can proceed)
        """
        self.ensure_one()

        # Skip if already in waiting_approval state
        if self.state == 'waiting_approval':
            return True

        # Skip if there's an approved approval request for this order
        ApprovalRequest = self.env['ops.approval.request']
        approved_approval = ApprovalRequest.search([
            ('model_name', '=', 'sale.order'),
            ('res_id', '=', self.id),
            ('state', '=', 'approved'),
        ], limit=1)

        if approved_approval:
            _logger.info(
                "OPS Governance: SO %s has approved approval request - allowing confirmation",
                self.name
            )
            return False  # Allow confirmation to proceed

        # Find applicable governance rules that require approval
        GovernanceRule = self.env['ops.governance.rule']
        rules = GovernanceRule.search([
            ('active', '=', True),
            ('enabled', '=', True),
            ('model_id.model', '=', 'sale.order'),
            ('action_type', '=', 'require_approval'),
            '|',
                ('company_id', '=', False),
                ('company_id', '=', self.company_id.id),
        ])

        if not rules:
            return False  # No approval rules, allow confirmation

        # Evaluate each rule to see if it triggers
        for rule in rules:
            triggered = False
            rule_message = ''

            try:
                if rule.condition_code:
                    code = rule.condition_code.strip()
                    if code:
                        safe_locals = {
                            'self': self,
                            'record': self,
                            'user': self.env.user,
                            'env': self.env,
                        }
                        from odoo.tools.safe_eval import safe_eval
                        triggered = safe_eval(code, safe_locals)
                        rule_message = rule.error_message or f"Rule '{rule.name}' triggered"

                elif rule.condition_domain:
                    domain = rule._parse_domain_string(rule.condition_domain)
                    triggered = bool(self.filtered_domain(domain))
                    rule_message = rule.error_message or f"Rule '{rule.name}' triggered"

            except Exception as e:
                _logger.error(
                    "Error evaluating governance rule %s for SO %s: %s",
                    rule.name, self.name, str(e)
                )
                continue

            if triggered:
                _logger.info(
                    "OPS Governance: Rule '%s' triggered for SO %s - requiring approval",
                    rule.name, self.name
                )

                # Check for existing pending approval
                existing_approval = ApprovalRequest.search([
                    ('model_name', '=', 'sale.order'),
                    ('res_id', '=', self.id),
                    ('rule_id', '=', rule.id),
                    ('state', '=', 'pending'),
                ], limit=1)

                if not existing_approval:
                    # Create approval request
                    approvers = self._get_governance_approvers(rule)

                    existing_approval = ApprovalRequest.create({
                        'name': _("Approval Required: %s - %s") % (self.name, rule.name),
                        'rule_id': rule.id,
                        'model_name': 'sale.order',
                        'res_id': self.id,
                        'notes': rule_message,
                        'approver_ids': [(6, 0, approvers.ids)] if approvers else [],
                        'requested_by': self.env.user.id,
                    })

                    _logger.info(
                        "OPS Governance: Created approval request %s for SO %s",
                        existing_approval.id, self.name
                    )

                # Transition order to waiting_approval state
                self.with_context(approval_unlock=True).write({
                    'state': 'waiting_approval',
                    'approval_locked': True,
                    'approval_request_id': existing_approval.id,
                })

                # Post to chatter for visibility
                if hasattr(self, 'message_post'):
                    self.message_post(
                        body=_(
                            "<strong>🔒 Confirmation Blocked - Approval Required</strong><br/><br/>"
                            "Rule: %s<br/>"
                            "Reason: %s<br/><br/>"
                            "This order cannot be confirmed until approval is granted.<br/>"
                            "An approval request has been sent to authorized approvers."
                        ) % (rule.name, rule_message),
                        subject=_("Approval Required for Confirmation"),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )

                return True  # Block confirmation

        return False  # No rules triggered, allow confirmation

    def _get_governance_approvers(self, rule) -> 'models.Model':
        """
        Get the list of users who can approve this governance rule.

        Priority:
        1. Rule-specific approver groups
        2. OPS Manager group
        3. Admin user (fallback)

        Args:
            rule: The ops.governance.rule record

        Returns:
            res.users recordset of approvers
        """
        approvers = self.env['res.users']

        # Try rule-specific approver group first
        if hasattr(rule, 'approver_group_id') and rule.approver_group_id:
            try:
                group_data = rule.approver_group_id.read(['users'])[0]
                user_ids = group_data.get('users', [])
                if user_ids:
                    approvers = self.env['res.users'].browse(user_ids).filtered(
                        lambda u: u.active and self.company_id.id in u.company_ids.ids
                    )[:5]
            except Exception:
                pass

        # Fallback to OPS Manager group
        if not approvers:
            try:
                manager_group = self.env.ref('ops_matrix_core.group_ops_manager', raise_if_not_found=False)
                if manager_group:
                    group_data = manager_group.read(['users'])[0]
                    user_ids = group_data.get('users', [])
                    if user_ids:
                        approvers = self.env['res.users'].browse(user_ids).filtered(
                            lambda u: u.active and self.company_id.id in u.company_ids.ids
                        )[:5]
            except Exception:
                pass

        # Final fallback to admin
        if not approvers:
            admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
            if admin_user and admin_user.active:
                approvers = admin_user

        return approvers

    def action_confirm(self) -> bool:
        """
        Override action_confirm to enforce credit firewall and governance rules.

        This ensures that:
        1. Segregation of Duties (SoD) rules are enforced
        2. Governance rules (margins, discounts, approvals) are evaluated BEFORE confirmation
        3. Credit firewall checks pass
        4. All validations happen before state changes to 'sale'

        GOVERNANCE INTERCEPTOR: Rules are evaluated BEFORE super() is called.
        If a rule requires approval, the order transitions to 'waiting_approval'
        state and the confirmation is blocked until approval is granted.
        """
        for order in self:
            _logger.info("OPS Governance: Checking SO %s for confirmation rules", order.name)

            # ADMIN BYPASS: Skip governance for administrators
            if self.env.su or self.env.user.has_group('base.group_system'):
                _logger.info("OPS Governance: Admin bypass for SO %s", order.name)
                # Log admin override for audit trail
                try:
                    self.env['ops.security.audit'].sudo().log_security_override(
                        model_name=order._name,
                        record_id=order.id,
                        reason='Admin bypass used to confirm Sale Order without governance checks'
                    )
                except Exception as e:
                    _logger.warning("Failed to log admin override: %s", str(e))
            else:
                # Check Segregation of Duties (SoD) rules BEFORE governance rules
                order._check_sod_violation('confirm')

                # =================================================================
                # GOVERNANCE INTERCEPTOR: Evaluate rules BEFORE super().action_confirm()
                # =================================================================
                # This must happen BEFORE the confirmation proceeds to ensure:
                # - Rules like ">$10K requires approval" block confirmation
                # - Orders transition to 'waiting_approval' if approval is needed
                # - The confirmation does NOT proceed until approval is granted
                # =================================================================
                approval_required = order._evaluate_governance_rules_for_confirm()

                if approval_required:
                    _logger.info(
                        "OPS Governance: SO %s requires approval - transitioning to waiting_approval",
                        order.name
                    )
                    # Order already transitioned to waiting_approval by the method
                    # Return early - do NOT call super().action_confirm()
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Approval Required'),
                            'message': _(
                                'Order %s requires approval before confirmation. '
                                'An approval request has been created.'
                            ) % order.name,
                            'type': 'warning',
                            'sticky': True,
                        }
                    }

                _logger.info("OPS Governance: SO %s passed all governance checks", order.name)

            # Perform credit check
            passed, message, is_warning_only = order._check_partner_credit_firewall()

            if not passed:
                order.write({
                    'ops_credit_check_passed': False,
                    'ops_credit_check_notes': message
                })
                raise UserError(_('Credit Firewall: ' + message))

            # Handle credit limit warnings (soft block at SO, hard block at Picking)
            if is_warning_only:
                order.write({
                    'ops_credit_check_passed': False,  # Mark as not fully passed
                    'ops_credit_check_notes': message
                })
                # Log the warning
                _logger.warning(
                    "Credit Warning on SO %s: %s (Delivery will be blocked)",
                    order.name, message
                )
                # Post warning to chatter for visibility
                if hasattr(order, 'message_post'):
                    order.message_post(
                        body=_(
                            "<strong>⚠️ Credit Limit Warning</strong><br/>"
                            "%s<br/><br/>"
                            "<em>Order confirmed, but delivery will be blocked until credit is cleared.</em>"
                        ) % message,
                        subject=_("Credit Limit Warning"),
                        message_type='notification',
                        subtype_xmlid='mail.mt_note',
                    )
            else:
                order.write({
                    'ops_credit_check_passed': True,
                    'ops_credit_check_notes': message
                })

        # Call parent method to confirm
        return super().action_confirm()
    
    def action_quotation_send(self):
        """
        Override email sending to enforce governance rules.

        This prevents users from sending quotations/orders by email
        if they violate governance rules or have pending approvals.

        STRICT GOVERNANCE: Orders in 'waiting_approval' state cannot be sent.
        """
        # HARD BLOCK: Cannot send orders waiting for approval
        for order in self:
            if order.state == 'waiting_approval':
                raise UserError(_(
                    "🚫 SEND BLOCKED: You cannot send order '%s' while it is waiting for approval.\n\n"
                    "Orders pending approval cannot be shared externally via email.\n"
                    "Please wait for approval or use the 'Recall Approval' button to make changes."
                ) % order.display_name)

        # ADMIN BYPASS: Allow administrators to send anything
        if self.env.su or self.env.user.has_group('base.group_system'):
            # Log admin override for audit trail
            try:
                for order in self:
                    self.env['ops.security.audit'].sudo().log_security_override(
                        model_name=order._name,
                        record_id=order.id,
                        reason='Admin bypass used to send Sale Order/Quotation without governance checks'
                    )
            except Exception as e:
                _logger.warning("Failed to log admin override: %s", str(e))
            return super().action_quotation_send()

        for order in self:
            _logger.info("OPS Governance: Checking SO %s for email commitment", order.name)
            
            # Check for pending approvals
            if hasattr(order, 'approval_request_ids'):
                pending_approvals = order.approval_request_ids.filtered(
                    lambda a: a.state == 'pending'
                )
                
                if pending_approvals:
                    rule_names = ', '.join(pending_approvals.mapped('rule_id.name'))
                    raise UserError(_(
                        "🚫 COMMITMENT BLOCKED: You cannot Email document '%s' "
                        "until it satisfies company Governance Rules.\n\n"
                        "⏳ Pending Approval: %s\n\n"
                        "This document is locked for external commitment (email or print) "
                        "until the required approvals are granted."
                    ) % (order.display_name, rule_names))
            
            # Enforce governance rules
            try:
                order._enforce_governance_rules(order, trigger_type='on_write')
                _logger.info("OPS Governance: SO %s passed all governance checks for email", order.name)
            except UserError as e:
                # Re-raise with enhanced message for email context
                error_message = str(e)
                if 'requires approval' in error_message.lower():
                    raise UserError(_(
                        "🚫 COMMITMENT BLOCKED: You cannot Email document '%s'.\n\n"
                        "%s\n\n"
                        "External commitment (email/print) is blocked until approval is granted."
                    ) % (order.display_name, error_message))
                else:
                    raise UserError(_(
                        "🚫 COMMITMENT BLOCKED: You cannot Email document '%s'.\n\n%s"
                    ) % (order.display_name, error_message))
        
        # If all checks pass, proceed with email wizard
        return super().action_quotation_send()

    def _get_report_base_filename(self):
        """
        Override to block report generation (print) for orders waiting approval.

        STRICT GOVERNANCE: Orders in 'waiting_approval' cannot be printed.
        This prevents sharing unapproved pricing/terms externally.
        """
        self.ensure_one()

        # HARD BLOCK: Cannot print orders waiting for approval (non-admin)
        if self.state == 'waiting_approval':
            if not (self.env.su or self.env.user.has_group('base.group_system')):
                raise UserError(_(
                    "🚫 PRINT BLOCKED: You cannot print order '%s' while it is waiting for approval.\n\n"
                    "Orders pending approval cannot be printed or shared externally.\n"
                    "Please wait for approval or use the 'Recall Approval' button to make changes."
                ) % self.display_name)

        return super()._get_report_base_filename()

    def action_preview_sale_order(self):
        """
        Override preview action to block for orders waiting approval.
        """
        for order in self:
            if order.state == 'waiting_approval':
                if not (self.env.su or self.env.user.has_group('base.group_system')):
                    raise UserError(_(
                        "🚫 PREVIEW BLOCKED: You cannot preview order '%s' while it is waiting for approval.\n\n"
                        "Orders pending approval cannot be previewed or shared externally.\n"
                        "Please wait for approval or use the 'Recall Approval' button to make changes."
                    ) % order.display_name)

        return super().action_preview_sale_order()

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to propagate matrix dimensions to lines."""
        # Enforce branch isolation on creation (non-admin users)
        sanitized_vals = []
        for vals in vals_list:
            user = self.env.user
            # Skip superuser/admin bypass to avoid blocking setup
            if not (self.env.su or user.has_group('base.group_system')):
                branch_id = vals.get('ops_branch_id') or user.ops_default_branch_id.id
                if branch_id:
                    allowed = user.ops_allowed_branch_ids.ids
                    if allowed and branch_id not in allowed:
                        raise ValidationError(_(
                            "Branch isolation violation: You cannot create Sale Orders in branch '%s'."
                        ) % self.env['ops.branch'].browse(branch_id).display_name)
                else:
                    # Require a branch to be set for regular users
                    raise ValidationError(_("Branch is required for Sale Orders."))
            sanitized_vals.append(vals)

        orders = super().create(sanitized_vals)
        for order in orders:
            if order.order_line:
                order._propagate_matrix_to_lines('order_line')
        return orders

    def write(self, vals):
        """
        Override write to enforce strict governance locking during approval workflow.

        SECURITY: When state is 'waiting_approval', critical fields cannot be modified.
        This prevents users from changing order details while approval is pending,
        which could create liability risks.

        Protected fields: order_line, amount_total, payment_term_id, partner_id,
                         pricelist_id, and any pricing-related fields.
        """
        # Allow unlocking via context (used by approve/reject/recall methods)
        if self._context.get('approval_unlock'):
            return super().write(vals)

        # Define protected fields that cannot be edited during approval
        PROTECTED_FIELDS = {
            'order_line',
            'partner_id',
            'partner_invoice_id',
            'partner_shipping_id',
            'pricelist_id',
            'payment_term_id',
            'fiscal_position_id',
            'date_order',
            'validity_date',
            'currency_id',
        }

        # Check if any protected field is being modified
        modified_protected = PROTECTED_FIELDS.intersection(vals.keys())

        for order in self:
            # ADMIN BYPASS: Administrators can always modify
            if self.env.su or self.env.user.has_group('base.group_system'):
                continue

            # STRICT LOCK: Block modifications when waiting_approval
            if order.state == 'waiting_approval' and modified_protected:
                raise UserError(_(
                    "🔒 ORDER LOCKED: This order is waiting for approval.\n\n"
                    "You cannot modify the following while approval is pending:\n"
                    "• Order lines (products, quantities, prices)\n"
                    "• Customer information\n"
                    "• Payment terms\n"
                    "• Pricelist or currency\n\n"
                    "To make changes, use the 'Recall Approval' button first."
                ))

            # APPROVED/SALE STATE: Log warning for audit trail (future enhancement)
            # For now, allow standard Odoo behavior for confirmed orders
            if order.state in ['sale', 'done'] and modified_protected:
                _logger.warning(
                    "OPS Governance: Protected fields modified on confirmed SO %s by user %s. Fields: %s",
                    order.name, self.env.user.name, ', '.join(modified_protected)
                )

        return super().write(vals)

    @api.onchange('ops_branch_id', 'ops_business_unit_id')
    def _onchange_matrix_dimensions(self):
        """Propagate matrix dimensions to order lines when changed."""
        super()._onchange_matrix_dimensions()
        if self.order_line:
            for line in self.order_line:
                line.ops_branch_id = self.ops_branch_id
                line.ops_business_unit_id = self.ops_business_unit_id
    
    def _prepare_invoice(self):
        """Propagate matrix dimensions to invoice."""
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update(self._prepare_invoice_vals())
        return invoice_vals

    # ==========================================================================
    # APPROVAL WORKFLOW ACTIONS
    # ==========================================================================

    def action_request_approval(self):
        """
        Request approval for this sale order.
        Sets state to 'waiting_approval' and creates approval request.
        """
        self.ensure_one()

        if self.state not in ['draft', 'sent']:
            raise UserError(_("Approval can only be requested for draft or sent quotations."))

        # Find applicable approval rules
        ApprovalRule = self.env['ops.approval.rule']
        rules = ApprovalRule.search([
            ('active', '=', True),
            ('model_name', '=', 'sale.order'),
            ('company_id', '=', self.company_id.id)
        ])

        # Also check governance rules that require approval
        GovernanceRule = self.env['ops.governance.rule']
        gov_rules = GovernanceRule.search([
            ('active', '=', True),
            ('model_id.model', '=', 'sale.order'),
            ('require_approval', '=', True),
            ('company_id', '=', self.company_id.id)
        ])

        approval_request = None

        # Try approval rules first
        for rule in rules:
            if rule.check_requires_approval(self):
                approval_request = rule.create_approval_request(
                    self,
                    notes=_("Approval requested for Sale Order %s") % self.name
                )
                break

        # If no approval rule matched, try governance rules
        if not approval_request and gov_rules:
            for rule in gov_rules:
                result = rule.validate_record(self, trigger_type='on_write')
                if result.get('requires_approval'):
                    approval_request = rule.action_create_approval_request(
                        self,
                        'approval_workflow',
                        '\n'.join(result.get('warnings', []))
                    )
                    break

        # If still no request, create a generic one
        if not approval_request:
            # Find default approvers using robust ORM approach
            approvers = self.env['res.users']

            try:
                # Method 1: Get users via group's users field (read to avoid lazy loading issues)
                manager_group = self.env.ref('ops_matrix_core.group_ops_manager', raise_if_not_found=False)
                if manager_group:
                    # Force load the users field via read()
                    group_data = manager_group.read(['users'])[0] if manager_group else {}
                    user_ids = group_data.get('users', [])
                    if user_ids:
                        approvers = self.env['res.users'].browse(user_ids).filtered(
                            lambda u: u.active and self.company_id.id in u.company_ids.ids
                        )[:5]
            except Exception:
                pass  # Fall through to next method

            # Method 2: Fallback to admin user
            if not approvers:
                admin_user = self.env.ref('base.user_admin', raise_if_not_found=False)
                if admin_user and admin_user.active:
                    approvers = admin_user

            if not approvers:
                raise UserError(_(
                    "No approvers found. Please configure approval rules or manager users."
                ))

            approval_request = self.env['ops.approval.request'].create({
                'name': _("Approval Request: %s") % self.name,
                'model_name': 'sale.order',
                'res_id': self.id,
                'notes': _("Manual approval requested for Sale Order %s") % self.name,
                'approver_ids': [(6, 0, approvers.ids)],
                'requested_by': self.env.user.id,
            })

        # Update state and lock
        self.write({
            'state': 'waiting_approval',
            'approval_locked': True,
            'approval_request_id': approval_request.id,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approval Requested'),
                'message': _('Approval request created: %s') % approval_request.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_view_approvals(self):
        """View approval requests for this sale order."""
        self.ensure_one()
        return {
            'name': _('Approval Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.approval.request',
            'view_mode': 'list,form',
            'domain': [
                ('model_name', '=', 'sale.order'),
                ('res_id', '=', self.id)
            ],
            'context': {
                'default_model_name': 'sale.order',
                'default_res_id': self.id,
                'create': False,
            },
            'target': 'current',
        }

    def action_approve(self):
        """Approve the sale order (from waiting_approval state)."""
        self.ensure_one()

        if self.state != 'waiting_approval':
            raise UserError(_("Only orders in 'Waiting Approval' state can be approved."))

        # Approve the linked request
        if self.approval_request_id:
            self.approval_request_id.action_approve()

        # Unlock and change state back to sent (or draft)
        self.with_context(approval_unlock=True).write({
            'state': 'sent',
            'approval_locked': False,
        })

        return True

    def action_reject_approval(self):
        """Reject the approval and return to draft."""
        self.ensure_one()

        if self.state != 'waiting_approval':
            raise UserError(_("Only orders in 'Waiting Approval' state can be rejected."))

        # Reject the linked request
        if self.approval_request_id:
            self.approval_request_id.action_reject()

        # Unlock and change state back to draft
        self.with_context(approval_unlock=True).write({
            'state': 'draft',
            'approval_locked': False,
        })

        return True

    def action_recall_approval(self):
        """
        Recall an approval request - allows the salesperson to pull back the
        request to make edits. Only works when state is 'waiting_approval'.
        """
        self.ensure_one()

        if self.state != 'waiting_approval':
            raise UserError(_("You can only recall orders that are waiting for approval."))

        # Cancel the related approval request
        if self.approval_request_id:
            try:
                self.approval_request_id.write({'state': 'cancelled'})
            except Exception as e:
                _logger.warning("Failed to cancel approval request: %s", str(e))

        # Unlock and return to draft state
        self.with_context(approval_unlock=True).write({
            'state': 'draft',
            'approval_locked': False,
        })

        _logger.info("OPS Governance: SO %s recalled from approval by user %s",
                     self.name, self.env.user.name)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approval Recalled'),
                'message': _('Order %s has been recalled. You can now make edits.') % self.name,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_print_product_bundle(self) -> Dict[str, Any]:
        """
        Task 5: Bulk Product Doc Generator (Smart Merge)
        Generate a single merged PDF of product documents (datasheets) for a sale order,
        removing duplicates using SHA-1 checksums.
        """
        self.ensure_one()
        
        if not PdfMerger:
            raise UserError(_('PyPDF library is not installed. Cannot merge PDFs.'))
        
        # Collect all PDF attachments from products
        pdf_attachments = []
        seen_checksums = set()
        
        for line in self.order_line:
            product = line.product_id
            
            # Find PDF attachments linked to this product
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'product.product'),
                ('res_id', '=', product.id),
                ('mimetype', '=', 'application/pdf'),
            ])
            
            # Also check product template attachments
            if product.product_tmpl_id:
                template_attachments = self.env['ir.attachment'].search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', product.product_tmpl_id.id),
                    ('mimetype', '=', 'application/pdf'),
                ])
                attachments |= template_attachments
            
            # Deduplicate by checksum
            for attachment in attachments:
                checksum = attachment.checksum
                if checksum and checksum not in seen_checksums:
                    seen_checksums.add(checksum)
                    pdf_attachments.append(attachment)
        
        if not pdf_attachments:
            raise UserError(_('No PDF documents found for the products in this sale order.'))
        
        # Merge PDFs
        merger = PdfMerger()
        
        try:
            for attachment in pdf_attachments:
                # Decode base64 attachment data
                pdf_data = base64.b64decode(attachment.datas)
                pdf_stream = io.BytesIO(pdf_data)
                merger.append(pdf_stream)
            
            # Get merged PDF output
            output_stream = io.BytesIO()
            merger.write(output_stream)
            merger.close()
            output_stream.seek(0)
            
            # Encode to base64
            merged_pdf_data = base64.b64encode(output_stream.read()).decode('utf-8')
            
            # Create attachment for the merged PDF
            attachment = self.env['ir.attachment'].create({
                'name': f'Product_Bundle_{self.name}.pdf',
                'type': 'binary',
                'datas': merged_pdf_data,
                'res_model': 'sale.order',
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })
            
            # Return action to open the merged PDF in a new tab
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
            
        except Exception as e:
            raise UserError(_('Error merging PDFs: %s') % str(e))


class SaleOrderLine(models.Model):
    """Extend sale.order.line with Matrix Mixin for dimension propagation."""
    _inherit = ['sale.order.line', 'ops.matrix.mixin', 'ops.field.visibility.mixin']
    _name = 'sale.order.line'
    
    # These fields are inherited from ops.matrix.mixin:
    # - ops_branch_id
    # - ops_business_unit_id
    # - ops_company_id
    # - ops_analytic_distribution
    
    # ==========================================================================
    # PRICE PROTECTION: Field to control price_unit editability
    # ==========================================================================
    can_edit_unit_price = fields.Boolean(
        string='Can Edit Unit Price',
        compute='_compute_can_edit_unit_price',
        store=False,
        help="Determines if the current user can edit unit prices. Only Managers and Admins can edit."
    )

    # The Cost Shield: Field-Level Security for Sale Order Line Costs
    can_user_access_cost_prices = fields.Boolean(
        string='Can Access Cost Prices',
        compute='_compute_can_user_access_cost_prices',
        store=False,
        help="Determines if the current user can view cost prices on sale order lines."
    )
    
    # Cost Shield Protected Fields - ISS-002 Hardening
    # These fields are restricted to Administrators and OPS Managers only
    # Model-level security prevents both UI and API access by unauthorized users
    purchase_price = fields.Float(
        string='Cost',
        compute='_compute_purchase_price',
        digits='Product Price',
        store=True,
        groups="base.group_system,ops_matrix_core.group_ops_manager",
        help="Unit cost price from product (protected field - Admin/OPS Manager only)"
    )
    
    margin = fields.Float(
        string='Margin',
        compute='_compute_margin',
        digits='Product Price',
        store=True,
        groups="base.group_system,ops_matrix_core.group_ops_manager",
        help="Gross margin amount (Sale Price - Cost) x Quantity (protected field - Admin/OPS Manager only)"
    )
    
    margin_percent = fields.Float(
        string='Margin %',
        compute='_compute_margin',
        store=True,
        groups="base.group_system,ops_matrix_core.group_ops_manager",
        help="Gross margin percentage (protected field - Admin/OPS Manager only)"
    )
    
    @api.depends_context('uid')
    def _compute_can_edit_unit_price(self):
        """
        PRICE PROTECTION: Determine if user can edit unit prices.

        Only OPS Managers (group_ops_manager) and System Administrators (group_system)
        can edit unit prices. Sales Representatives see prices as readonly.

        This prevents unauthorized price changes that could affect margins.
        """
        is_manager = self.env.user.has_group('ops_matrix_core.group_ops_manager')
        is_admin = self.env.user.has_group('base.group_system')
        can_edit = is_manager or is_admin

        for record in self:
            record.can_edit_unit_price = can_edit

    @api.depends_context('uid')
    def _compute_can_user_access_cost_prices(self):
        """
        Check if user has authority to view cost prices on sale order lines.

        Security Logic:
        - System administrators (base.group_system) always have access
        - Other users must have 'can_access_cost_prices' authority flag
        - This protects margin calculations from unauthorized viewing

        This implements "The Cost Shield" anti-fraud measure.
        """
        for record in self:
            # Administrators bypass all restrictions
            if self.env.user.has_group('base.group_system'):
                record.can_user_access_cost_prices = True
            else:
                # Check persona authority flag
                record.can_user_access_cost_prices = self.env.user.has_ops_authority('can_access_cost_prices')
    
    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_purchase_price(self):
        """
        Compute the unit cost (purchase price) from product standard_price.
        
        ISS-002 Security: This field is protected by model-level groups,
        preventing unauthorized users from accessing cost data via UI or API.
        """
        for line in self:
            if line.product_id:
                # Convert to line UOM if different from product UOM
                line.purchase_price = line.product_id.standard_price
            else:
                line.purchase_price = 0.0
    
    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal')
    def _compute_margin(self):
        """
        Compute margin and margin percentage for sale order lines.
        
        ISS-002 Security: These fields are protected by model-level groups,
        preventing unauthorized users from accessing margin data via UI or API.
        
        Calculation:
        - Margin = (Unit Price - Cost) * Quantity
        - Margin % = (Margin / Sale Price) * 100 if Sale Price > 0
        """
        for line in self:
            if line.product_id:
                # Calculate total cost
                total_cost = line.purchase_price * line.product_uom_qty
                
                # Calculate margin (subtotal - cost)
                line.margin = line.price_subtotal - total_cost
                
                # Calculate margin percentage
                if line.price_subtotal:
                    line.margin_percent = (line.margin / line.price_subtotal) * 100.0
                else:
                    line.margin_percent = 0.0
            else:
                line.margin = 0.0
                line.margin_percent = 0.0
    
    def _get_default_ops_branch(self):
        """Get default branch from parent order if available."""
        if self._context.get('default_order_id'):
            order = self.env['sale.order'].browse(self._context['default_order_id'])
            if order.ops_branch_id:
                return order.ops_branch_id.id
        return super()._get_default_ops_branch()
    
    def _get_default_ops_business_unit(self):
        """Get default BU from parent order if available."""
        if self._context.get('default_order_id'):
            order = self.env['sale.order'].browse(self._context['default_order_id'])
            if order.ops_business_unit_id:
                return order.ops_business_unit_id.id
        return super()._get_default_ops_business_unit()
    
    def write(self, vals):
        """
        Override write to enforce PRICE PROTECTION.

        Only OPS Managers and System Administrators can modify price_unit.
        Regular Sales Reps attempting to change prices will be blocked.

        This provides model-level enforcement that works regardless of UI.
        """
        # Check if price_unit is being modified
        if 'price_unit' in vals:
            # Skip check for superuser/admin
            if not (self.env.su or self.env.user.has_group('base.group_system')):
                # Check if user is OPS Manager
                if not self.env.user.has_group('ops_matrix_core.group_ops_manager'):
                    raise UserError(_(
                        "🔒 PRICE PROTECTION: You are not authorized to change unit prices.\n\n"
                        "Only Managers and Administrators can modify the Unit Price field.\n"
                        "Please contact your manager if a price adjustment is required."
                    ))

        return super().write(vals)

    @api.onchange('order_id')
    def _onchange_order_id_propagate_dimensions(self):
        """
        When order_id changes or is set, inherit the order's matrix dimensions.

        This ensures that when a line is added to an order with specific dimensions,
        it automatically gets the correct dimensions.
        """
        if self.order_id:
            # Inherit dimensions from parent order if not already set
            if not self.ops_branch_id and self.order_id.ops_branch_id:
                self.ops_branch_id = self.order_id.ops_branch_id
            if not self.ops_business_unit_id and self.order_id.ops_business_unit_id:
                self.ops_business_unit_id = self.order_id.ops_business_unit_id

    @api.constrains('product_id', 'order_id')
    def _check_product_branch_activation(self):
        """
        BRANCH ACTIVATION GOVERNANCE: Ensure products are activated for the order's branch.

        For Global Master products, verify they are explicitly activated for the
        branch specified on the parent Sales Order. This prevents selling products
        in branches where they haven't been approved for distribution.
        """
        for line in self:
            # Skip validation for superuser/admin
            if self.env.is_superuser() or self.env.user.has_group('base.group_system'):
                continue

            if not line.product_id or not line.order_id:
                continue

            product_tmpl = line.product_id.product_tmpl_id
            order_branch = line.order_id.ops_branch_id

            # Check if product is a Global Master
            if product_tmpl.ops_is_global_master:
                # Check if product is activated for this branch
                if order_branch and order_branch not in product_tmpl.ops_branch_activation_ids:
                    raise ValidationError(_(
                        "🚫 BRANCH ACTIVATION BLOCK: Product '%(product)s' is a Global Master "
                        "and is NOT activated for branch '%(branch)s'.\n\n"
                        "Global Master products must be explicitly activated for each branch "
                        "before they can be sold in that branch.\n\n"
                        "Contact Master Data Management to request activation."
                    ) % {
                        'product': product_tmpl.name,
                        'branch': order_branch.display_name,
                    })
