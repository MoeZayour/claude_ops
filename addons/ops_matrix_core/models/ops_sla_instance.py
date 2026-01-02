# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz
import logging

_logger = logging.getLogger(__name__)

class OpsSlaInstance(models.Model):
    _name = 'ops.sla.instance'
    _description = 'SLA Instance'
    _order = 'deadline asc'

    template_id = fields.Many2one('ops.sla.template', string='Template', required=True, ondelete='cascade')
    res_model = fields.Char(string='Related Model', related='template_id.model_id.model', store=True, readonly=True)
    res_id = fields.Integer(string='Related Record ID', required=True, index=True)
    
    start_datetime = fields.Datetime(string='Start Date', default=fields.Datetime.now, required=True)
    deadline = fields.Datetime(string='Deadline', compute='_compute_deadline', store=True)
    
    status = fields.Selection([
        ('running', 'Running'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('violated', 'Violated'),
        ('completed', 'Completed')
    ], string='Status', default='running', required=True, compute='_compute_status', store=True)
    
    progress = fields.Float(string='Progress (%)', compute='_compute_progress')

    @api.depends('start_datetime', 'template_id', 'template_id.target_duration', 'template_id.calendar_id')
    def _compute_deadline(self):
        """Compute SLA deadline with proper timezone handling.
        
        This method calculates the deadline considering:
        - Company timezone (not UTC)
        - Business days if template has calendar configured
        - DST (Daylight Saving Time) transitions
        """
        for record in self:
            if not record.template_id or not record.start_datetime:
                record.deadline = False
                continue
            
            try:
                # Get company and timezone
                company = record.template_id.company_id or self.env.company
                tz_name = company.partner_id.tz or 'UTC'
                tz = pytz.timezone(tz_name)
                
                # Convert start time to company timezone
                start_utc = pytz.utc.localize(record.start_datetime)
                start_local = start_utc.astimezone(tz)
                
                # Get target duration from template
                if hasattr(record.template_id, 'target_days'):
                    target_days = record.template_id.target_days
                elif hasattr(record.template_id, 'target_duration'):
                    # Convert hours to days if duration is in hours
                    target_days = record.template_id.target_duration / 24.0
                else:
                    _logger.warning(
                        f"SLA template {record.template_id.id} has no target duration"
                    )
                    record.deadline = False
                    continue
                
                # Calculate deadline based on calendar
                calendar = company.resource_calendar_id
                use_business_days = (
                    hasattr(record.template_id, 'use_business_days') and
                    record.template_id.use_business_days
                )
                
                if calendar and use_business_days:
                    # Use business days calculation
                    deadline_local = self._add_business_days(
                        start_local,
                        int(target_days),
                        calendar,
                        tz
                    )
                else:
                    # Simple day addition (calendar days)
                    deadline_local = start_local + timedelta(days=target_days)
                
                # Convert back to UTC for storage
                deadline_utc = deadline_local.astimezone(pytz.utc)
                record.deadline = deadline_utc.replace(tzinfo=None)
                
            except Exception as e:
                _logger.error(
                    f"Error computing SLA deadline for instance {record.id}: {e}",
                    exc_info=True
                )
                record.deadline = False
    
    def _add_business_days(self, start_date, days, calendar, tz):
        """Add business days respecting company calendar.
        
        Args:
            start_date: Starting datetime (timezone-aware)
            days: Number of business days to add
            calendar: Company resource calendar
            tz: Timezone object
            
        Returns:
            datetime: Deadline in company timezone
        """
        current = start_date
        days_added = 0
        
        # Safety limit to prevent infinite loops
        max_iterations = days * 3  # Allow for weekends/holidays
        iterations = 0
        
        while days_added < days and iterations < max_iterations:
            current += timedelta(days=1)
            iterations += 1
            
            # Check if current date is a work day
            work_date = current.date()
            
            # Use calendar's work day check if available
            try:
                if hasattr(calendar, '_work_days_data_compute'):
                    work_data = calendar._work_days_data_compute(
                        work_date, work_date
                    )
                    if work_data.get(work_date):
                        days_added += 1
                elif hasattr(calendar, 'resource_id'):
                    # Fallback: check if it's a weekday (Mon-Fri)
                    if current.weekday() < 5:
                        days_added += 1
                else:
                    # No calendar method, assume Mon-Fri
                    if current.weekday() < 5:
                        days_added += 1
            except Exception as e:
                _logger.warning(
                    f"Error checking work day in calendar: {e}. "
                    f"Falling back to Mon-Fri."
                )
                if current.weekday() < 5:
                    days_added += 1
        
        if iterations >= max_iterations:
            _logger.warning(
                f"Business day calculation hit iteration limit. "
                f"Requested {days} days, added {days_added}"
            )
        
        return current

    @api.depends('deadline', 'status')
    def _compute_status(self):
        now = fields.Datetime.now()
        for record in self:
            if record.status == 'completed':
                continue
            
            if not record.deadline:
                record.status = 'running'
                continue

            if now > record.deadline:
                record.status = 'violated'
            else:
                # Calculate time elapsed percentage
                total_time = (record.deadline - record.start_datetime).total_seconds()
                if total_time > 0:
                    elapsed_time = (now - record.start_datetime).total_seconds()
                    percent = (elapsed_time / total_time) * 100.0
                    
                    if percent > 90:
                        record.status = 'critical'
                    elif percent > 75:
                        record.status = 'warning'
                    else:
                        record.status = 'running'
                else:
                    record.status = 'violated'

    def _compute_progress(self):
        now = fields.Datetime.now()
        for record in self:
            if record.status == 'completed':
                record.progress = 100.0
                continue
            
            if not record.deadline or not record.start_datetime:
                record.progress = 0.0
                continue
            
            total_time = (record.deadline - record.start_datetime).total_seconds()
            if total_time <= 0:
                record.progress = 100.0
                continue
                
            elapsed_time = (now - record.start_datetime).total_seconds()
            record.progress = min(100.0, max(0.0, (elapsed_time / total_time) * 100.0))

    def action_complete(self):
        self.write({'status': 'completed'})

    @api.model
    def _cron_check_sla_status(self):
        """
        Cron job to re-evaluate SLA statuses and notify chatter on changes.
        """
        instances = self.search([('status', 'in', ['running', 'warning', 'critical'])])
        for rec in instances:
            old_status = rec.status
            rec._compute_status()
            if rec.status != old_status:
                # Notify related document chatter
                try:
                    target_record = self.env[rec.res_model].browse(rec.res_id)
                    if target_record.exists() and hasattr(target_record, 'message_post'):
                        target_record.message_post(
                            body=f"SLA Status Change: {old_status.capitalize()} → {rec.status.capitalize()} (Template: {rec.template_id.name})",
                            subtype_xmlid='mail.mt_note'
                        )
                except Exception:
                    continue
