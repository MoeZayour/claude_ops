from odoo import models, fields, api, Command, _
from typing import List, Dict, Any
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class OpsApprovalRequest(models.Model):
    _name = 'ops.approval.request'
    _description = 'Approval Request with Matrix Dimensions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default='New',
        tracking=True,
        help='Unique reference number for this approval request. '
             'Auto-generated on save (format: APP/XXXX). '
             'Used for: Tracking approvals, audit trails, communication with approvers. '
             'Example: APP/0001, APP/0025. '
             'Cannot be changed after creation.'
    )
    rule_id = fields.Many2one(
        'ops.governance.rule',
        string='Governance Rule',
        required=False,  # Made optional - can use approval_rule_id instead
        tracking=True,
        help='The governance rule that triggered this approval request. '
             'The rule defines: validation criteria, approvers, severity, actions. '
             'Click to view rule configuration and understand why approval is needed. '
             'Examples: "Discount Limit Rule", "Margin Protection - Electronics", "High Value Approval". '
             'Related: View rule details to see thresholds and authorized approvers.'
    )
    approval_rule_id = fields.Many2one(
        'ops.approval.rule',
        string='Approval Rule',
        required=False,
        tracking=True,
        help='The simple approval rule that triggered this request (alternative to governance rule).'
    )
    model_name = fields.Char(string='Model Name', required=True)
    res_id = fields.Integer(string='Record ID', required=True)
    record_ref = fields.Char(string='Record Reference', compute='_compute_record_ref', store=True)
    res_name = fields.Char(string='Record Name', compute='_compute_res_name', store=True)
    notes = fields.Text(
        string='Notes',
        help='Explanation of why this approval is needed and context for approvers. '
             'Include: Reason for exception, business justification, customer context, urgency. '
             'Examples: '
             '- "Customer is major account, discount requested to secure $500K annual contract" '
             '- "Market pricing requires 20% discount to match competitors" '
             '- "Low margin justified by high volume order (1000 units)". '
             'Best Practice: Provide enough detail for approvers to make informed decisions. '
             'Visible to: All approvers and requestor.'
    )
    response_notes = fields.Text(
        string='Response Notes',
        help='Approver\'s explanation of their decision (approval or rejection). '
             'Required when rejecting, optional when approving. '
             'Include: Reason for decision, conditions if any, guidance for future. '
             'Examples: '
             '- "Approved - customer is strategic account" '
             '- "Rejected - margin too low, no business justification provided" '
             '- "Approved conditionally - monitor for repeat requests". '
             'Visible to: Requestor and all users with approval access.'
    )
    
    # Tracking fields
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, required=True, tracking=True)
    requested_date = fields.Datetime(string='Requested Date', default=fields.Datetime.now, required=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, tracking=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)

    @api.depends('model_name', 'res_id')
    def _compute_record_ref(self):
        """Compute record reference string."""
        for request in self:
            if request.model_name and request.res_id:
                request.record_ref = f"{request.model_name},{request.res_id}"
            else:
                request.record_ref = False

    @api.depends('model_name', 'res_id')
    def _compute_res_name(self):
        """Compute display name of the related record."""
        for request in self:
            if request.model_name and request.res_id:
                try:
                    record = request.env[request.model_name].browse(request.res_id)
                    if record.exists():
                        request.res_name = record.display_name
                    else:
                        request.res_name = f"{request.model_name}#{request.res_id} (Deleted)"
                except Exception:
                    request.res_name = f"{request.model_name}#{request.res_id}"
            else:
                request.res_name = False
    
    # Matrix Dimensions (inherited from source record)
    branch_id = fields.Many2one('ops.branch', string='Branch', tracking=True)
    business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit', tracking=True)
    
    # --- MATRIX DIMENSION FIELDS (ENHANCED) ---
    ops_company_id = fields.Many2one('res.company', string='Company',
                                     compute='_compute_matrix_dimensions', store=True)
    
    ops_branch_id = fields.Many2one('ops.branch', string='OPS Branch',
                                    compute='_compute_matrix_dimensions', store=True)
    
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='OPS Business Unit',
                                           compute='_compute_matrix_dimensions', store=True)
    
    # --- GOVERNANCE VIOLATION DETAILS ---
    violation_type = fields.Selection([
        ('matrix', 'Matrix Validation'),
        ('discount', 'Discount Limit'),
        ('margin', 'Margin Protection'),
        ('price', 'Price Override'),
        ('other', 'Other'),
    ], string='Violation Type',
       tracking=True,
       help='Category of governance rule violation that triggered this approval. '
            'Matrix Validation: Missing or invalid branch/BU selection. '
            'Discount Limit: Discount exceeds authorized limit. '
            'Margin Protection: Profit margin below minimum threshold. '
            'Price Override: Price change exceeds authorized variance. '
            'Other: Custom rule violations. '
            'This determines which approvers are notified and what data is displayed.')
    
    violation_details = fields.Text(
        string='Violation Details',
        help='Detailed explanation of what governance rule was violated and how. '
             'Auto-generated by the system based on the violation type. '
             'Examples: '
             '- "Discount 15% exceeds your limit of 10%" '
             '- "Margin 8% below minimum 12% for Electronics category" '
             '- "Branch selection required but not provided". '
             'Provides context for approvers to understand the issue. '
             'Read-only, populated automatically by governance engine.'
    )
    
    # --- QUANTITATIVE VIOLATION DATA ---
    discount_percent = fields.Float(string='Discount %', digits=(5, 2))
    margin_percent = fields.Float(string='Margin %', digits=(5, 2))
    price_variance_percent = fields.Float(string='Price Variance %', digits=(5, 2))
    
    allowed_limit = fields.Float(string='Allowed Limit', digits=(5, 2),
                                help='What was the allowed limit')
    
    actual_value = fields.Float(string='Actual Value', digits=(5, 2),
                               help='What was the actual value')
    
    # --- APPROVAL CONTEXT ---
    is_governance_violation = fields.Boolean(string='Governance Violation',
                                            compute='_compute_is_governance_violation', store=True)
    
    violation_severity = fields.Selection([
        ('low', 'Low - Informational'),
        ('medium', 'Medium - Requires Attention'),
        ('high', 'High - Requires Approval'),
        ('critical', 'Critical - Blocking'),
    ], string='Violation Severity',
       default='medium',
       tracking=True,
       help='Severity level of this governance violation. '
            'Low: Informational only, no action blocked. '
            'Medium: Requires review but transaction can proceed. '
            'High: Requires approval before transaction can complete. '
            'Critical: Transaction completely blocked until approved. '
            'Severity affects: Notification urgency, approver priority, system behavior. '
            'Default: Medium (requires attention but not blocking).')
    
    # --- COMPUTED FIELDS ---
    matrix_summary = fields.Char(string='Matrix Summary',
                                compute='_compute_matrix_summary', store=True)
    
    violation_summary = fields.Char(string='Violation Summary',
                                   compute='_compute_violation_summary', store=True)
    
    # --- ESCALATION TRACKING ---
    original_sla_id = fields.Many2one('ops.sla.instance', string='Original SLA', help='The SLA instance that triggered this escalation.')
    escalation_level = fields.Integer('Current Escalation Level', default=0, tracking=True)
    escalation_date = fields.Datetime('Last Escalation Date', readonly=True, tracking=True)
    escalation_history = fields.Text('Escalation History', readonly=True)
    is_overdue = fields.Boolean('Overdue', compute='_compute_is_overdue', store=True)
    hours_pending = fields.Float('Hours Pending', compute='_compute_hours_pending', store=True)
    next_escalation_date = fields.Datetime('Next Escalation Date', compute='_compute_next_escalation_date', store=True)

    # --- COMPUTED METHODS ---

    @api.depends('requested_date', 'escalation_date', 'state')
    def _compute_hours_pending(self):
        for request in self:
            if request.state == 'pending':
                last_event_date = request.escalation_date or request.requested_date
                request.hours_pending = (fields.Datetime.now() - last_event_date).total_seconds() / 3600
            else:
                request.hours_pending = 0

    @api.depends('hours_pending', 'rule_id.escalation_timeout_hours')
    def _compute_is_overdue(self):
        for request in self:
            if request.state == 'pending' and request.rule_id and request.rule_id.enable_escalation:
                request.is_overdue = request.hours_pending > request.rule_id.escalation_timeout_hours
            else:
                request.is_overdue = False

    @api.depends('escalation_date', 'rule_id.escalation_timeout_hours')
    def _compute_next_escalation_date(self):
        for request in self:
            if request.state == 'pending' and request.rule_id and request.rule_id.enable_escalation:
                last_event_date = request.escalation_date or request.requested_date
                request.next_escalation_date = last_event_date + timedelta(hours=request.rule_id.escalation_timeout_hours)
            else:
                request.next_escalation_date = False

    @api.depends('record_ref')
    def _compute_matrix_dimensions(self):
        """Extract matrix dimensions from referenced record."""
        for approval in self:
            if approval.record_ref:
                try:
                    model_name, record_id = approval.record_ref.split(',')
                    record = self.env[model_name].browse(int(record_id))
                    
                    if record.exists():
                        if hasattr(record, 'company_id'):
                            approval.ops_company_id = record.company_id
                        
                        if hasattr(record, 'ops_branch_id'):
                            approval.ops_branch_id = record.ops_branch_id
                        elif hasattr(record, 'branch_id'):
                            approval.ops_branch_id = record.branch_id
                        
                        if hasattr(record, 'ops_business_unit_id'):
                            approval.ops_business_unit_id = record.ops_business_unit_id
                        elif hasattr(record, 'business_unit_id'):
                            approval.ops_business_unit_id = record.business_unit_id
                except Exception as e:
                    _logger.debug(f"Error computing matrix dimensions: {e}")
                    approval.ops_company_id = False
                    approval.ops_branch_id = False
                    approval.ops_business_unit_id = False
            else:
                approval.ops_company_id = False
                approval.ops_branch_id = False
                approval.ops_business_unit_id = False
    
    @api.depends('rule_id', 'violation_type')
    def _compute_is_governance_violation(self):
        for approval in self:
            approval.is_governance_violation = bool(approval.rule_id or approval.violation_type)
    
    @api.depends('ops_branch_id', 'ops_business_unit_id')
    def _compute_matrix_summary(self):
        for approval in self:
            parts = []
            if approval.ops_branch_id:
                parts.append(f"Branch: {approval.ops_branch_id.code or approval.ops_branch_id.name}")
            if approval.ops_business_unit_id:
                parts.append(f"BU: {approval.ops_business_unit_id.code or approval.ops_business_unit_id.name}")
            approval.matrix_summary = " | ".join(parts) if parts else "No matrix"
    
    @api.depends('violation_type', 'discount_percent', 'margin_percent', 'price_variance_percent', 'allowed_limit', 'actual_value')
    def _compute_violation_summary(self):
        for approval in self:
            if approval.violation_type == 'discount' and approval.discount_percent:
                approval.violation_summary = f"Discount: {approval.discount_percent:.2f}% (Limit: {approval.allowed_limit:.2f}%)"
            elif approval.violation_type == 'margin' and approval.margin_percent:
                approval.violation_summary = f"Margin: {approval.margin_percent:.2f}% (Min: {approval.allowed_limit:.2f}%)"
            elif approval.violation_type == 'price' and approval.price_variance_percent:
                approval.violation_summary = f"Price Variance: {approval.price_variance_percent:.2f}% (Max: {approval.allowed_limit:.2f}%)"
            elif approval.violation_type == 'matrix':
                approval.violation_summary = f"Matrix Validation: {approval.violation_details or 'Missing dimension'}"
            else:
                approval.violation_summary = approval.violation_details or "No violation details"
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status',
       default='pending',
       tracking=True,
       help='Current status of this approval request. '
            'Pending: Waiting for approver action. '
            'Approved: Request granted, transaction can proceed. '
            'Rejected: Request denied, transaction blocked or cancelled. '
            'Cancelled: Request withdrawn by requestor or system. '
            'State Changes: Pending → Approved/Rejected/Cancelled. '
            'Email notifications sent to requestor on status change.')

    approver_ids = fields.Many2many(
        'res.users',
        'ops_approval_request_user_rel',
        'request_id',
        'user_id',
        string='Approvers',
        tracking=True,
        help='Users authorized to approve or reject this request. '
             'Automatically determined based on: Governance rule configuration, matrix dimensions (branch/BU), violation type. '
             'Selection logic: '
             '- System finds personas with approval authority for the branch/BU '
             '- Filters by violation type (discount/margin/price approvers) '
             '- Falls back to rule-defined approvers if no matches. '
             'Any listed approver can approve/reject. '
             'Notification: All approvers are notified when request is created.'
    )
    
    # Workflow fields
    workflow_id = fields.Many2one('ops.approval.workflow', string='Workflow', related='rule_id.approval_workflow_id', store=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority',
       default='medium',
       tracking=True,
       help='Urgency level for this approval request. '
            'Low: Review within 5 business days. '
            'Medium: Review within 2 business days (default). '
            'High: Review within 1 business day. '
            'Urgent: Review immediately (same day). '
            'Affects: Notification frequency, dashboard placement, SLA tracking. '
            'Set urgency based on: Customer waiting, order deadline, business impact. '
            'Urgent requests appear at top of approver dashboard.')
    
    # --- BUSINESS METHODS ---
    
    def action_view_source_record(self):
        """Open the source record that triggered this approval."""
        self.ensure_one()
        if not self.record_ref:
            return None
        
        try:
            model_name, record_id = self.record_ref.split(',')
            return {
                'type': 'ir.actions.act_window',
                'name': self.name,
                'res_model': model_name,
                'res_id': int(record_id),
                'view_mode': 'form',
                'target': 'current',
            }
        except Exception as e:
            _logger.error(f"Error opening source record: {e}")
            return None
    
    def action_view_rule(self):
        """Open the governance rule that triggered this approval."""
        self.ensure_one()
        if not self.rule_id:
            return None
        
        return {
            'type': 'ir.actions.act_window',
            'name': self.rule_id.name,
            'res_model': 'ops.governance.rule',
            'res_id': self.rule_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _find_governance_approvers(self):
        """Find approvers for governance violations based on matrix dimensions."""
        self.ensure_one()
        
        if not self.rule_id:
            return self.env['res.users']
        
        # Use rule's approver finding logic
        if self.record_ref:
            try:
                model_name, record_id = self.record_ref.split(',')
                record = self.env[model_name].browse(int(record_id))
                if record.exists():
                    return self.rule_id._find_approvers(record, self.violation_type or 'other')
            except Exception as e:
                _logger.error(f"Error finding governance approvers: {e}")
        
        return self.env['res.users']

    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'OpsApprovalRequest':
        """Auto-set governance approvers and inherit matrix dimensions from source record."""
        for vals in vals_list:
            # Generate sequence if needed
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ops.approval.request') or 'APP/0001'
            
            # Inherit matrix dimensions from source record
            if vals.get('model_name') and vals.get('res_id'):
                try:
                    record = self.env[vals['model_name']].browse(vals['res_id'])
                    if record.exists():
                        # Legacy fields (backward compatibility)
                        if hasattr(record, 'branch_id') and 'branch_id' not in vals:
                            vals['branch_id'] = record.branch_id.id if record.branch_id else False
                        if hasattr(record, 'business_unit_id') and 'business_unit_id' not in vals:
                            vals['business_unit_id'] = record.business_unit_id.id if record.business_unit_id else False
                except Exception as e:
                    _logger.debug(f"Could not inherit matrix dimensions: {e}")
        
        records = super().create(vals_list)
        
        # Set approvers for governance violations
        for record in records:
            if record.is_governance_violation and not record.approver_ids:
                # Find governance-specific approvers
                approvers = record._find_governance_approvers()
                if approvers:
                    record.approver_ids = [(6, 0, approvers.ids)]
        
        return records
    
    def write(self, vals):
        """Track approval/rejection of governance violations."""
        result = super().write(vals)
        
        # If approved/rejected, update source record if it's a governance violation
        if 'state' in vals and vals['state'] in ['approved', 'rejected']:
            for record in self:
                if record.is_governance_violation:
                    record._update_source_record_approval(vals['state'])
        
        return result
    
    def _update_source_record_approval(self, approval_state):
        """Update source record with approval status."""
        for approval in self:
            if not approval.record_ref:
                continue
            
            try:
                model_name, record_id = approval.record_ref.split(',')
                record = self.env[model_name].browse(int(record_id))
                
                if record.exists():
                    # Add approval note to record
                    approval_note = _("Governance approval %s: %s") % (approval_state, approval.name)
                    
                    if hasattr(record, 'message_post'):
                        record.message_post(body=approval_note)
                    
                    # Set approval status field if it exists
                    if hasattr(record, 'governance_approval_status'):
                        record.governance_approval_status = approval_state
                    if hasattr(record, 'governance_approval_id'):
                        record.governance_approval_id = approval.id
            
            except Exception as e:
                _logger.error(f"Error updating source record: {e}")

    def action_approve(self) -> bool:
        """Approve the request, with delegation audit logging."""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending requests can be approved.'))

        user = self.env.user

        # Check if approval is via delegation
        delegation_info = self._check_delegation_approval(user)

        self.write({
            'state': 'approved',
            'approved_by': user.id,
            'approved_date': fields.Datetime.now(),
        })

        # Build approval message with delegation info
        if delegation_info:
            approval_msg = _(
                'Approval GRANTED by %(approver)s on behalf of %(delegator)s '
                '(Delegation: %(persona)s, valid until %(end_date)s)'
            ) % {
                'approver': user.name,
                'delegator': delegation_info['delegator'].name,
                'persona': delegation_info['persona'].name,
                'end_date': delegation_info['delegation'].end_date.strftime('%Y-%m-%d %H:%M') if delegation_info['delegation'].end_date else _('No end date'),
            }
            # Log to security audit
            try:
                self.env['ops.security.audit'].sudo().log_delegation_approval(
                    approval_request_id=self.id,
                    delegation_id=delegation_info['delegation'].id,
                    details=approval_msg
                )
            except Exception as e:
                _logger.warning(f"Could not log delegation approval to security audit: {e}")
        else:
            approval_msg = _('Approval GRANTED by %s') % user.name

        # Unlock the record
        if self.model_name and self.res_id:
            try:
                record = self.env[self.model_name].browse(self.res_id)
                if record.exists() and hasattr(record, 'approval_locked'):
                    record.with_context(approval_unlock=True).write({
                        'approval_locked': False,
                        'approval_request_id': False,
                    })

                    # Post to document with delegation info
                    if hasattr(record, 'message_post'):
                        record.message_post(
                            body=approval_msg,
                            message_type='notification',
                            subtype_xmlid='mail.mt_note'
                        )
            except Exception as e:
                _logger.debug(f"Could not unlock record: {e}")

        # Post to approval request
        self.message_post(
            body=approval_msg,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def _check_delegation_approval(self, user):
        """
        Check if user is approving via delegation and return delegation info.

        :param user: res.users record
        :return: dict with delegation info or None
        """
        # Try to get delegation info using the user's helper method
        if hasattr(user, 'get_delegation_info_for_authority'):
            # Check common approval authority fields
            for authority_field in ['can_approve_transactions', 'can_validate_invoices',
                                   'can_approve_discounts', 'can_approve_governance']:
                try:
                    delegation_info = user.get_delegation_info_for_authority(authority_field)
                    if delegation_info:
                        return delegation_info
                except Exception:
                    continue

        # Fallback: Check if user has any active delegations
        now = fields.Datetime.now()
        try:
            delegation = self.env['ops.persona.delegation'].sudo().search([
                ('delegate_id', '=', user.id),
                ('active', '=', True),
                ('start_date', '<=', now),
                '|',
                ('end_date', '=', False),
                ('end_date', '>=', now),
            ], limit=1)

            if delegation:
                # Check if the delegated persona is related to approval authority
                persona = delegation.persona_id
                # Check if user's own personas have approval authority
                user_personas = user.ops_persona_ids.filtered(lambda p: p.active)
                approval_fields = ['can_approve_transactions', 'can_validate_invoices',
                                   'can_approve_discounts', 'can_approve_governance']

                # If user doesn't have approval via their own personas, they're using delegation
                has_direct = any(
                    hasattr(p, f) and getattr(p, f)
                    for p in user_personas
                    for f in approval_fields
                )

                if not has_direct and persona:
                    return {
                        'delegation': delegation,
                        'delegator': delegation.delegator_id,
                        'persona': persona,
                    }
        except Exception as e:
            _logger.warning(f"Error checking delegation approval: {e}")

        return None

    def action_escalate(self):
        for request in self.filtered(lambda r: r.state == 'pending' and r.is_overdue):
            next_level = request.escalation_level + 1
            next_approver_persona = getattr(request.rule_id, f'escalation_level_{next_level}_persona_id', None)

            if next_approver_persona and next_approver_persona.user_id:
                original_approver = request.approver_ids
                new_approver = next_approver_persona.user_id

                history_entry = _("Escalated from level %s to %s on %s.") % (request.escalation_level, next_level, fields.Datetime.now())

                request.write({
                    'escalation_level': next_level,
                    'escalation_date': fields.Datetime.now(),
                    'approver_ids': [Command.set(new_approver.ids)],
                    'escalation_history': (request.escalation_history or '') + history_entry + '\n'
                })

                request._send_escalation_notifications(original_approver, new_approver, next_level)

                request.message_post(
                    body=_("Approval request escalated to level %s: %s") % (next_level, new_approver.name)
                )
            else:
                # Final escalation level reached, no further automatic action
                request.message_post(
                    body=_("Final escalation level reached, but no further approver is defined. Manual intervention required.")
                )

    @api.model
    def _cron_escalate_overdue_approvals(self):
        overdue_requests = self.search([
            ('state', '=', 'pending'),
            ('is_overdue', '=', True),
        ])
        _logger.info(f"Found {len(overdue_requests)} overdue approval requests to escalate.")
        for request in overdue_requests:
            try:
                request.action_escalate()
            except Exception as e:
                _logger.error(f"Failed to escalate approval request {request.name}: {e}")

    def _send_escalation_notifications(self, original_approver, new_approver, escalation_level):
        self.ensure_one()
        # Email to original (reminder)
        reminder_template = self.env.ref('ops_matrix_core.email_template_escalation_reminder', raise_if_not_found=False)
        if reminder_template:
            for user in original_approver:
                reminder_template.with_context(object=self, user=user).send_mail(self.id, force_send=True)

        # Email to new approver
        new_approver_template = self.env.ref('ops_matrix_core.email_template_escalation_new_approver', raise_if_not_found=False)
        if new_approver_template:
            new_approver_template.with_context(object=self, user=new_approver).send_mail(self.id, force_send=True)

        # System notifications
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('Approval Escalated: %s') % self.res_name,
            note=_('The approval request for %s has been escalated to you.') % self.res_name,
            user_id=new_approver.id,
        )

    def action_reject(self):
        """Open wizard to reject with reason."""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending requests can be rejected.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Approval Request'),
            'res_model': 'ops.approval.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_approval_request_id': self.id,
            },
        }
