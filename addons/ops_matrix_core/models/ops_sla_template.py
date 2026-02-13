# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class OpsSlaTemplate(models.Model):
    _name = 'ops.sla.template'
    _description = 'SLA Template'

    name = fields.Char(
        string='Name',
        required=True,
        help='Descriptive name for this SLA (Service Level Agreement) template. '
             'Use clear names that explain what is being measured and the time expectation. '
             'Examples: "Approval Response - 24 Hours", "Quote Processing - 2 Business Days", '
             '"Customer Support Ticket - 4 Hours", "Order Fulfillment - 48 Hours". '
             'Best Practice: Include both the activity and the time frame in the name. '
             'This name appears in: SLA reports, deadline notifications, dashboard views.'
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Target Model',
        required=True,
        ondelete='cascade',
        help='The Odoo model (object type) this SLA applies to. Required. '
             'Common models: '
             '- ops.approval.request (Approval Requests) '
             '- helpdesk.ticket (Support Tickets) '
             '- sale.order (Sales Orders) '
             '- project.task (Project Tasks). '
             'Scope: SLA instances are created automatically for records of this model type. '
             'Example: SLA on "sale.order" tracks how long from order creation to confirmation.'
    )
    calendar_id = fields.Many2one(
        'resource.calendar',
        string='Working Calendar',
        required=True,
        default=lambda self: self.env.company.resource_calendar_id,
        help='Working calendar that defines business hours for SLA deadline calculations. '
             'Determines: Which days are working days, what hours count as working hours, holidays. '
             'Default: Company\'s default working calendar (typically Mon-Fri 9am-5pm). '
             'Important: Deadlines are calculated in business hours, not calendar hours. '
             'Example: 8-hour SLA on Friday 3pm → Deadline is Monday 3pm (skipping weekend). '
             'Use Cases: '
             '- Standard business hours: Mon-Fri 9-5 '
             '- 24/7 operations: All days, all hours '
             '- Shift work: Custom calendar matching your shifts.'
    )
    target_duration = fields.Float(
        string='Target Duration (Hours)',
        required=True,
        help='Time allowed to complete the action, measured in working hours. '
             'Examples: '
             '- Express approval: 4 hours '
             '- Standard approval: 24 hours (1 business day) '
             '- Quote processing: 48 hours (2 business days) '
             '- Complex reviews: 160 hours (4 weeks). '
             'Calculation: Uses business hours from the Working Calendar above. '
             '24 hours means 24 working hours (3 business days if 8-hour days). '
             'Warning: System generates alerts when deadlines approach or are missed. '
             'Best Practice: Set realistic targets based on historical performance data.'
    )
    active = fields.Boolean(
        default=True,
        help='If unchecked, this SLA template is no longer in use and won\'t create new SLA instances. '
             'Use Cases: '
             '- Uncheck: Deprecated SLA, pilot SLA ended, changed business process '
             '- Check: Reactivate SLA for seasonal processes. '
             'Effect: Inactive templates stop generating new SLA instances but existing instances remain. '
             'Historical SLA data is preserved even when template is deactivated. '
             'Use this instead of deleting templates that have historical tracking data.'
    )
    enabled = fields.Boolean(
        string="Enabled",
        default=False,
        copy=False,
        help='If checked, this SLA template is enforced and will actively track deadlines. '
             'CATALOG MODE: Templates can be visible (active=True) but not enforced (enabled=False). '
             'This allows administrators to review available SLA templates without activating them.'
    )

    # Some tests/data refer to target_days; provide a stored integer alias for compatibility.
    target_days = fields.Integer(
        string='Target Days',
        help='Target duration expressed in days for backward compatibility with legacy data/tests. '
             'When used, consider aligning with target_duration (hours) if both are present.',
        store=True,
    )

    def _compute_deadline(self, start_dt: datetime) -> datetime:
        """
        Calculate the deadline based on the start datetime and target duration,
        respecting the working calendar.
        """
        self.ensure_one()
        if not start_dt:
            return False
        
        # plan_hours returns the end datetime after adding target_duration hours
        # to start_dt within the calendar's working intervals.
        deadline = self.calendar_id.plan_hours(self.target_duration, start_dt)
        return deadline
