# -*- coding: utf-8 -*-
from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, UserError
from typing import List, Dict, Any, Optional
import logging

_logger = logging.getLogger(__name__)


class OpsGovernanceMixin(models.AbstractModel):
    """
    Mixin to add governance rule enforcement to any model.
    
    Models that inherit from this mixin will automatically enforce
    ops.governance.rule records during create and write operations.
    """
    _name = 'ops.governance.mixin'
    _description = 'Operations Governance Mixin - Rule Enforcement'

    approval_locked = fields.Boolean(
        string='Approval Locked',
        default=False,
        help='Record is locked pending approval',
        copy=False
    )

    approval_request_ids = fields.One2many(
        'ops.approval.request',
        compute='_compute_approval_requests',
        string='Approval Request List'
    )

    approval_request_count = fields.Integer(
        compute='_compute_approval_requests',
        string='Number of Approvals'
    )

    def _compute_approval_requests(self) -> None:
        for record in self:
            if record.id:
                approvals = self.env['ops.approval.request'].search([
                    ('model_name', '=', record._name),
                    ('res_id', '=', record.id),
                ])
                record.approval_request_ids = approvals
                record.approval_request_count = len(approvals)
            else:
                record.approval_request_ids = False
                record.approval_request_count = 0

    def action_view_approvals(self) -> Dict[str, Any]:
        """Open approval requests for this record."""
        self.ensure_one()
        return {
            'name': 'Approval Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'ops.approval.request',
            'view_mode': 'list,form',
            'domain': [('model_name', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_model_name': self._name, 'default_res_id': self.id},
        }

    def action_request_approval(self) -> bool:
        """Manually request approval."""
        self.ensure_one()
        # Find applicable rules that require approval
        rules = self.env['ops.governance.rule'].search([
            ('model_id.model', '=', self._name),
            ('action_type', '=', 'require_approval'),
            ('active', '=', True),
        ])
        
        if not rules:
            raise UserError(_('No approval rules configured for this model.'))
        
        # Apply first matching rule
        for rule in rules:
            self._apply_governance_rule(rule, 'manual')
            break
        
        return True

    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]) -> 'OpsGovernanceMixin':
        """
        Override create to enforce governance rules on record creation.
        
        :param vals_list: List of dictionaries for new records
        :return: Created records
        """
        # Create the records first
        records = super().create(vals_list)
        
        # Enforce governance rules
        self._enforce_governance_rules(records, 'on_create')
        
        return records

    def write(self, vals: Dict[str, Any]) -> bool:
        """
        Override write to enforce governance rules on record updates.
        
        :param vals: Dictionary of values to update
        :return: Result of parent write operation
        """
        # Check if record is approval locked
        for record in self:
            if hasattr(record, 'approval_locked') and record.approval_locked:
                # Check if user is trying to change fields other than approval_locked
                if set(vals.keys()) - {'approval_locked'}:
                    # Cancel pending approvals if data changed
                    pending_approvals = self.env['ops.approval.request'].search([
                        ('model_name', '=', record._name),
                        ('res_id', '=', record.id),
                        ('state', '=', 'pending'),
                    ])
                    pending_approvals.write({'state': 'cancelled'})
                    
                    # Unlock and allow change
                    vals['approval_locked'] = False
        
        result = super().write(vals)
        
        # Enforce governance rules
        self._enforce_governance_rules(self, 'on_write')
        
        return result

    def unlink(self) -> bool:
        """
        Override unlink to enforce governance rules on record deletion.
        
        :return: Result of parent unlink operation
        """
        # Enforce governance rules before deletion
        self._enforce_governance_rules(self, 'on_unlink')
        
        return super().unlink()

    def _enforce_governance_rules(self, records, trigger_type: str) -> None:
        """
        Find and enforce all active governance rules for this model and trigger type.
        
        :param records: Record(s) to evaluate rules against
        :param trigger_type: Type of trigger ('on_create', 'on_write', 'on_unlink')
        :raises ValidationError: If a rule with action_type='block' is triggered
        :raises UserError: If a rule with action_type='warning' is triggered
        """
        if not records:
            return

        # ADMIN BYPASS: Skip governance rule enforcement for Administrator and System Managers
        if self.env.su or self.env.user.has_group('base.group_system'):
            # Log admin override for audit trail
            try:
                for record in records:
                    self.env['ops.security.audit'].sudo().log_security_override(
                        model_name=record._name,
                        record_id=record.id,
                        reason=f'Admin bypass used to skip governance rule enforcement on {trigger_type}'
                    )
                _logger.info(
                    "Admin bypass used by %s on %s (trigger: %s)",
                    self.env.user.name,
                    model_name,
                    trigger_type
                )
            except Exception as e:
                _logger.warning("Failed to log admin override: %s", str(e))
            return

        # Get the model name
        model_name = self._name

        # Try to find governance rules, but gracefully handle ACL errors
        # CATALOG MODE: Only enforce rules that are both active (visible) AND enabled (enforced)
        try:
            rules = self.env['ops.governance.rule'].search([
                ('active', '=', True),
                ('enabled', '=', True),
                ('model_id.model', '=', model_name),
                ('trigger_type', '=', trigger_type),
            ])
        except Exception as e:
            # If user doesn't have access to governance rules, just skip enforcement
            _logger.debug(f"Governance rule enforcement skipped (ACL/access issue): {str(e)}")
            return

        if not rules:
            return

        # Evaluate each rule
        warnings = []
        for rule in rules:
            for record in records:
                res = self._apply_governance_rule(rule, trigger_type, record)
                if res and 'warning' in res:
                    warnings.append(res['warning']['message'])

        # Display accumulated warnings
        if warnings:
            warning_msg = '\n'.join(set(warnings))  # Remove duplicates
            raise UserError(
                f'Governance Warnings:\n{warning_msg}\n\n'
                f'Please review the above warnings before proceeding.'
            )

    def _apply_governance_rule(self, rule, trigger_type: str, record=None) -> Optional[Dict[str, Any]]:
        """Apply a governance rule and handle different action types."""
        if record is None:
            record = self
            
        # Evaluate condition
        try:
            if rule.condition_code:
                # Clean and validate the code
                code = rule.condition_code.strip()
                if not code:
                    return {}
                
                # Execute in safe context
                safe_locals = {
                    'self': record,
                    'record': record,
                    'user': record.env.user,
                    'env': record.env,
                }
                from odoo.tools.safe_eval import safe_eval
                result = safe_eval(code, safe_locals)
            elif rule.condition_domain:
                domain = rule._parse_domain_string(rule.condition_domain)
                result = bool(record.filtered_domain(domain))
            else:
                result = True
        except SyntaxError as e:
            # Log syntax errors but don't crash
            _logger.error(f"Syntax error in rule {rule.name}: {str(e)}")
            return {}
        except Exception as e:
            # For other errors, show user-friendly message
            raise UserError(f"Error evaluating rule '{rule.name}': {str(e)}")
        
        if result:
            # Rule triggered - take action based on action_type
            if rule.action_type == 'block':
                raise UserError(rule.error_message or f"Operation blocked by rule: {rule.name}")
            
            elif rule.action_type == 'warning':
                return {
                    'warning': {
                        'title': 'Governance Rule Warning',
                        'message': rule.error_message or f"Warning from rule: {rule.name}",
                    }
                }
            
            elif rule.action_type == 'require_approval':
                # ============================================================
                # FOUR-EYES PRINCIPLE (SEGREGATION OF DUTIES)
                # ============================================================
                # Prevent self-approval: A user cannot approve a transaction
                # they themselves created, even if they have the required Persona.
                # This implements the "Four-Eyes Principle" for fraud prevention.
                #
                # Enhanced with vertical escalation and Chatter notifications
                # Exception: System administrators bypass this for emergency situations
                # ============================================================
                if not self.env.user.has_group('base.group_system'):
                    # Check if create_uid exists and matches current user
                    if hasattr(record, 'create_uid') and record.create_uid and record.create_uid.id == self.env.user.id:
                        # Get user's primary persona
                        primary_persona = self.env.user.ops_persona_ids[:1] if self.env.user.ops_persona_ids else False
                        
                        if not primary_persona:
                            # No persona assigned - configuration error
                            _logger.error(
                                f"SoD Configuration Error: User {self.env.user.name} (ID: {self.env.user.id}) "
                                f"has no persona assigned. Record: {record._name} (ID: {record.id})"
                            )
                            raise UserError(
                                _("SoD Configuration Error: You have no persona assigned. "
                                  "Please contact your system administrator to configure your organizational role.")
                            )
                        
                        # Get parent persona for escalation
                        parent_persona = primary_persona.parent_id if primary_persona else False
                        
                        # Log the violation attempt
                        _logger.warning(
                            f"SoD Violation: User {self.env.user.name} (ID: {self.env.user.id}, Persona: {primary_persona.name}) "
                            f"attempted to approve their own record {record._name} (ID: {record.id}). "
                            f"Rule: {rule.name}"
                        )
                        
                        if parent_persona:
                            # Escalation path exists - post Chatter notification
                            if hasattr(record, 'message_post'):
                                try:
                                    # Find users with the parent persona for reference
                                    parent_users = self.env['res.users'].search([
                                        ('ops_persona_ids', 'in', parent_persona.id)
                                    ])
                                    
                                    escalation_body = _(
                                        "🔒 <strong>Segregation of Duties - Escalation Required</strong><br/><br/>"
                                        "Self-approval restricted. This request has been escalated to <strong>%s</strong> for secondary verification.<br/><br/>"
                                        "<em>User %s (Persona: %s) attempted to self-approve this transaction.</em>"
                                    ) % (parent_persona.name, self.env.user.name, primary_persona.name)
                                    
                                    if parent_users:
                                        escalation_body += _("<br/><br/>Authorized approvers: %s") % ', '.join(parent_users.mapped('name'))
                                    
                                    record.message_post(
                                        body=escalation_body,
                                        subject=_("Segregation of Duties - Escalation Required"),
                                        message_type='notification',
                                        subtype_xmlid='mail.mt_note',
                                    )
                                    _logger.info(
                                        f"SoD escalation posted to Chatter for {record._name} (ID: {record.id}), "
                                        f"escalated to {parent_persona.name}"
                                    )
                                except Exception as e:
                                    # Log but don't fail if Chatter posting fails
                                    _logger.warning(f"Failed to post escalation to Chatter: {str(e)}")
                            
                            # Raise error with escalation information
                            raise UserError(
                                _("SoD Violation: Self-approval is prohibited.\n\n"
                                  "This transaction must be reviewed by your supervisor (%s).\n\n"
                                  "An escalation notice has been logged.") % parent_persona.name
                            )
                        else:
                            # Executive deadlock - no parent authority
                            if hasattr(record, 'message_post'):
                                try:
                                    deadlock_body = _(
                                        "⚠️ <strong>Executive Deadlock Detected</strong><br/><br/>"
                                        "User <strong>%s</strong> (Persona: <strong>%s</strong>) attempted self-approval "
                                        "but has no higher authority in the organizational hierarchy.<br/><br/>"
                                        "<em>This transaction requires Superuser or Internal Audit override.</em>"
                                    ) % (self.env.user.name, primary_persona.name)
                                    
                                    record.message_post(
                                        body=deadlock_body,
                                        subject=_("Executive Deadlock - Override Required"),
                                        message_type='notification',
                                        subtype_xmlid='mail.mt_note',
                                    )
                                    _logger.info(
                                        f"Executive deadlock logged for {record._name} (ID: {record.id}), "
                                        f"Persona: {primary_persona.name}"
                                    )
                                except Exception as e:
                                    _logger.warning(f"Failed to post deadlock notice to Chatter: {str(e)}")
                            
                            # Raise error for executive deadlock
                            raise UserError(
                                _("Executive Deadlock: As a %s, you have no higher authority in the organizational structure.\n\n"
                                  "This transaction requires Superuser or Internal Audit override to proceed.") % primary_persona.name
                            )
                
                # Check if already has approved approval
                approved_approval = self.env['ops.approval.request'].search([
                    ('model_name', '=', record._name),
                    ('res_id', '=', record.id),
                    ('rule_id', '=', rule.id),
                    ('state', '=', 'approved'),
                ], limit=1)
                
                if approved_approval:
                    # Approval already granted - allow operation to proceed
                    _logger.info(f"Governance: Approval already granted for {record._name} ID {record.id}")
                    return {}
                
                # Check if already has pending approval
                existing_approval = self.env['ops.approval.request'].search([
                    ('model_name', '=', record._name),
                    ('res_id', '=', record.id),
                    ('rule_id', '=', rule.id),
                    ('state', '=', 'pending'),
                ], limit=1)
                
                if not existing_approval:
                    # Create approval request
                    approval = self.env['ops.approval.request'].create({
                        'rule_id': rule.id,
                        'model_name': record._name,
                        'res_id': record.id,
                        'notes': rule.error_message or f"Approval required by rule: {rule.name}",
                    })
                    
                    # Lock record if configured
                    if rule.lock_on_approval_request and hasattr(record, 'approval_locked'):
                        record.write({'approval_locked': True})
                    
                    # Notify approvers
                    if approval.approver_ids:
                        approval.message_subscribe(partner_ids=approval.approver_ids.mapped('partner_id').ids)
                        approval.message_post(
                            body=f"Approval requested by {record.env.user.name} for {record.display_name}",
                            subject="New Approval Request"
                        )
                    
                    _logger.info(f"Governance: Created approval request {approval.id} for {record._name} ID {record.id}")
                
                # BLOCK THE OPERATION - Approval is required but not yet granted
                raise UserError(
                    rule.error_message or
                    f"This operation requires approval.\n\n"
                    f"An approval request has been submitted to authorized approvers. "
                    f"You will be notified once the approval is granted.\n\n"
                    f"Rule: {rule.name}"
                )
        
        return {}
