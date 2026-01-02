from odoo import models, fields, api, Command, _
from typing import List, Dict, Any
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
        string='Rule',
        required=True,
        tracking=True,
        help='The governance rule that triggered this approval request. '
             'The rule defines: validation criteria, approvers, severity, actions. '
             'Click to view rule configuration and understand why approval is needed. '
             'Examples: "Discount Limit Rule", "Margin Protection - Electronics", "High Value Approval". '
             'Related: View rule details to see thresholds and authorized approvers.'
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
    
    # --- COMPUTED METHODS ---
    
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
        """Approve the request."""
        self.ensure_one()
        if self.state != 'pending':
            return False
            
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        
        # Unlock the record if it was locked
        if self.model_name and self.res_id:
            try:
                record = self.env[self.model_name].browse(self.res_id)
                if record.exists() and hasattr(record, 'approval_locked'):
                    record.write({'approval_locked': False})
            except Exception as e:
                _logger.debug(f"Could not unlock record: {e}")
        
        # Send notification
        try:
            self.message_post(
                body=_("Approval granted by %s") % self.env.user.name,
                message_type='notification'
            )
        except Exception:
            pass
        
        return True

    def action_reject(self) -> bool:
        """Reject the request."""
        self.ensure_one()
        if self.state != 'pending':
            return False
            
        self.write({
            'state': 'rejected',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        
        # Unlock the record if it was locked
        if self.model_name and self.res_id:
            try:
                record = self.env[self.model_name].browse(self.res_id)
                if record.exists() and hasattr(record, 'approval_locked'):
                    record.write({'approval_locked': False})
            except Exception as e:
                _logger.debug(f"Could not unlock record: {e}")
        
        # Send notification
        try:
            self.message_post(
                body=_("Approval rejected by %s. Reason: %s") % (self.env.user.name, self.response_notes or 'No reason given'),
                message_type='notification'
            )
        except Exception:
            pass
        
        return True

    def action_cancel(self) -> bool:
        """Cancel the request."""
        self.ensure_one()
        if self.state != 'pending':
            return False
            
        self.write({'state': 'cancelled'})
        
        # Unlock the record if it was locked
        if self.model_name and self.res_id:
            try:
                record = self.env[self.model_name].browse(self.res_id)
                if record.exists() and hasattr(record, 'approval_locked'):
                    record.write({'approval_locked': False})
            except Exception as e:
                _logger.debug(f"Could not unlock record: {e}")
        
        return True
