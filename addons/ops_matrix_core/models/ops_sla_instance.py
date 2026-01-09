from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz
import logging

_logger = logging.getLogger(__name__)

class OpsSLAInstance(models.Model):
    _name = 'ops.sla.instance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'SLA Instance'
    _order = 'deadline asc'
    
    name = fields.Char('Reference', required=True, default='New')
    template_id = fields.Many2one('ops.sla.template', 'SLA Template', required=True, ondelete='cascade')
    model_name = fields.Char('Model', related='template_id.model_id.model', store=True)
    res_id = fields.Integer('Record ID', required=True, index=True)
    
    start_date = fields.Datetime('Start Date', required=True, default=fields.Datetime.now)
    deadline = fields.Datetime('Deadline', required=True, compute='_compute_deadline', store=True)
    completion_date = fields.Datetime('Completion Date')
    
    state = fields.Selection([
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed (Timeout)'),
        ('escalated', 'Escalated'),
    ], default='running', tracking=True)
    
    # For dashboard compatibility with existing views if any
    status = fields.Selection([
        ('running', 'Running'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('violated', 'Violated'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('escalated', 'Escalated'),
    ], string='Status', compute='_compute_status_compat', store=True)
    
    escalation_level = fields.Integer('Escalation Level', default=0)
    current_approver_id = fields.Many2one('res.users', 'Current Approver')
    
    # Time tracking
    elapsed_hours = fields.Float('Elapsed Hours', compute='_compute_elapsed')
    remaining_hours = fields.Float('Remaining Hours', compute='_compute_remaining')
    is_overdue = fields.Boolean('Overdue', compute='_compute_overdue')
    progress = fields.Float(string='Progress (%)', compute='_compute_progress')

    @api.depends('template_id', 'start_date')
    def _compute_deadline(self):
        for record in self:
            if record.template_id and record.start_date:
                # Use the template's compute_deadline if it exists and is robust
                if hasattr(record.template_id, '_compute_deadline'):
                    record.deadline = record.template_id._compute_deadline(record.start_date)
                else:
                    timeout_hours = record.template_id.target_duration or 24
                    record.deadline = record.start_date + timedelta(hours=timeout_hours)
            else:
                record.deadline = False

    @api.depends('state', 'deadline')
    def _compute_status_compat(self):
        now = fields.Datetime.now()
        for record in self:
            if record.state != 'running':
                record.status = record.state
                continue
            
            if not record.deadline:
                record.status = 'running'
                continue

            if now > record.deadline:
                record.status = 'violated'
            else:
                total_time = (record.deadline - record.start_date).total_seconds()
                if total_time > 0:
                    elapsed_time = (now - record.start_date).total_seconds()
                    percent = (elapsed_time / total_time) * 100.0
                    if percent > 90:
                        record.status = 'critical'
                    elif percent > 75:
                        record.status = 'warning'
                    else:
                        record.status = 'running'
                else:
                    record.status = 'violated'

    @api.depends('start_date', 'completion_date')
    def _compute_elapsed(self):
        for record in self:
            if record.completion_date:
                delta = record.completion_date - record.start_date
            else:
                delta = fields.Datetime.now() - record.start_date
            record.elapsed_hours = delta.total_seconds() / 3600
    
    @api.depends('deadline', 'state')
    def _compute_remaining(self):
        now = fields.Datetime.now()
        for record in self:
            if record.state in ['completed', 'failed'] or not record.deadline:
                record.remaining_hours = 0
            else:
                delta = record.deadline - now
                record.remaining_hours = max(0, delta.total_seconds() / 3600)
    
    @api.depends('deadline', 'state')
    def _compute_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_overdue = (
                record.state == 'running' and 
                record.deadline and record.deadline < now
            )

    @api.depends('start_date', 'deadline', 'state', 'completion_date')
    def _compute_progress(self):
        now = fields.Datetime.now()
        for record in self:
            if record.state == 'completed':
                record.progress = 100.0
                continue
            
            if not record.deadline or not record.start_date:
                record.progress = 0.0
                continue
            
            total_time = (record.deadline - record.start_date).total_seconds()
            if total_time <= 0:
                record.progress = 100.0
                continue
                
            if record.completion_date:
                elapsed_time = (record.completion_date - record.start_date).total_seconds()
            else:
                elapsed_time = (now - record.start_date).total_seconds()
            record.progress = min(100.0, max(0.0, (elapsed_time / total_time) * 100.0))

    @api.model
    def _cron_check_escalations(self):
        """
        Cron job to check and escalate overdue SLA instances
        Runs every 15 minutes
        """
        overdue = self.search([
            ('state', '=', 'running'),
            ('deadline', '<', fields.Datetime.now()),
        ])
        
        for sla in overdue:
            sla.action_escalate()
        
        # Also check approaching deadlines (1 hour warning)
        approaching = self.search([
            ('state', '=', 'running'),
            ('deadline', '>', fields.Datetime.now()),
            ('deadline', '<', fields.Datetime.now() + timedelta(hours=1)),
        ])
        
        for sla in approaching:
            sla._send_warning_notification()
    
    def action_escalate(self):
        """Escalate SLA to next approval level"""
        self.ensure_one()
        
        # Determine next escalation level
        next_level = self.escalation_level + 1
        max_level = 3  # Maximum 3 escalation levels
        
        if next_level > max_level:
            # No more escalation possible - mark as failed
            self.write({
                'state': 'failed',
                'completion_date': fields.Datetime.now(),
            })
            self._send_failed_notification()
            return
        
        # Find escalation approver
        escalation_approver = self._get_escalation_approver(next_level)
        
        if not escalation_approver:
            # No approver found - mark as failed
            self.write({
                'state': 'failed',
                'completion_date': fields.Datetime.now(),
            })
            return
        
        # Create escalated approval request
        # Note: We assume ops.approval.request exists and has these fields
        try:
            escalated_request = self.env['ops.approval.request'].create({
                'name': f"ESCALATED (Level {next_level}): {self.name}",
                'model_name': self.model_name,
                'res_id': self.res_id,
                'approver_ids': [(6, 0, [escalation_approver.id])],
                'escalation_level': next_level,
                'state': 'pending',
            })
        except Exception as e:
            _logger.error(f"Failed to create escalated approval request: {e}")
        
        # Update SLA
        self.write({
            'state': 'escalated',
            'escalation_level': next_level,
            'current_approver_id': escalation_approver.id,
        })
        
        # Send notifications
        self._send_escalation_notification(escalation_approver, next_level)
        
        # Log in chatter
        self.message_post(
            body=f"Escalated to Level {next_level} - Approver: {escalation_approver.name}",
            subject="SLA Escalated"
        )
    
    def _get_escalation_approver(self, level):
        """Get approver for escalation level"""
        # Level 1: Direct manager
        # Level 2: Manager's manager
        # Level 3: Executive (CEO/CFO)
        
        if level == 1:
            # Original approver's manager
            if self.current_approver_id and hasattr(self.current_approver_id, 'parent_id') and self.current_approver_id.parent_id:
                return self.current_approver_id.parent_id
            # Fallback to employee manager if hr module is used
            employee = self.env['hr.employee'].search([('user_id', '=', self.current_approver_id.id)], limit=1)
            if employee and employee.parent_id and employee.parent_id.user_id:
                return employee.parent_id.user_id
        
        elif level == 2:
            # Manager's manager or BU leader
            if self.current_approver_id:
                employee = self.env['hr.employee'].search([('user_id', '=', self.current_approver_id.id)], limit=1)
                if employee and employee.parent_id and employee.parent_id.parent_id and employee.parent_id.parent_id.user_id:
                    return employee.parent_id.parent_id.user_id
            
            # Fallback to BU manager
            if self.template_id.company_id:
                # Try to find a BU manager
                bu = self.env['ops.business.unit'].search([('company_id', '=', self.template_id.company_id.id)], limit=1)
                if bu and bu.manager_id:
                    return bu.manager_id
        
        elif level == 3:
            # Executive level - find CEO or CFO persona
            ceo_persona = self.env['ops.persona'].search([
                ('code', 'in', ['CEO', 'CFO'])
            ], limit=1)
            if ceo_persona and ceo_persona.user_ids:
                return ceo_persona.user_ids[0]
        
        return False
    
    def _send_warning_notification(self):
        """Send warning notification for approaching deadline"""
        self.ensure_one()
        
        if not self.current_approver_id:
            return
        
        template = self.env.ref('ops_matrix_core.email_template_sla_warning', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        # Also create activity
        self.activity_schedule(
            'mail.mail_activity_data_warning',
            summary=f'SLA Deadline Approaching: {self.name}',
            note=f'Deadline in {self.remaining_hours:.1f} hours',
            user_id=self.current_approver_id.id,
        )
    
    def _send_escalation_notification(self, approver, level):
        """Send escalation notification"""
        self.ensure_one()
        
        template = self.env.ref('ops_matrix_core.email_template_sla_escalation', raise_if_not_found=False)
        if template:
            ctx = {
                'approver_name': approver.name,
                'escalation_level': level,
            }
            template.with_context(ctx).send_mail(self.id, force_send=True)
    
    def _send_failed_notification(self):
        """Send notification when SLA fails (max escalation reached)"""
        self.ensure_one()
        
        template = self.env.ref('ops_matrix_core.email_template_sla_failed', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
    
    def action_complete(self):
        """Mark SLA as completed"""
        self.write({
            'state': 'completed',
            'completion_date': fields.Datetime.now(),
        })
        
        # Calculate if it was within SLA
        if self.completion_date <= self.deadline:
            self.message_post(body="✅ Completed within SLA", subject="SLA Met")
        else:
            overtime = (self.completion_date - self.deadline).total_seconds() / 3600
            self.message_post(
                body=f"⚠️ Completed {overtime:.1f} hours over SLA",
                subject="SLA Missed"
            )
