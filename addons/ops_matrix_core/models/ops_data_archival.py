# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)


class OpsDataArchival(models.Model):
    """
    Automated Data Archival System

    Features:
    - Archive old transactions to maintain performance
    - Keep snapshots for historical reporting
    - Store archived data in separate table
    - Restore capability
    - Scheduled automatic archival
    - Statistics tracking
    """
    _name = 'ops.data.archival'
    _description = 'OPS Data Archival Job'
    _order = 'created_date desc'

    # ========================================================================
    # FIELDS
    # ========================================================================

    name = fields.Char(
        string='Archive Job Name',
        required=True,
        compute='_compute_name',
        store=True
    )

    model_name = fields.Selection([
        ('account.move', 'Journal Entries'),
        ('sale.order', 'Sales Orders'),
        ('purchase.order', 'Purchase Orders'),
        ('stock.picking', 'Stock Pickings'),
        ('ops.security.audit', 'Security Audit Logs'),
        ('ops.session.manager', 'Session Records'),
    ], string='Model to Archive', required=True)

    archive_date = fields.Date(
        string='Archive Date',
        required=True,
        default=fields.Date.today,
        help='Records older than this date will be archived'
    )

    record_age_days = fields.Integer(
        string='Record Age (Days)',
        default=730,  # 2 years
        required=True,
        help='Archive records older than this many days'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True)

    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True
    )

    start_date = fields.Datetime(
        string='Start Date',
        readonly=True
    )

    end_date = fields.Datetime(
        string='End Date',
        readonly=True
    )

    records_found = fields.Integer(
        string='Records Found',
        default=0,
        readonly=True
    )

    records_archived = fields.Integer(
        string='Records Archived',
        default=0,
        readonly=True
    )

    records_failed = fields.Integer(
        string='Records Failed',
        default=0,
        readonly=True
    )

    archive_size_bytes = fields.Integer(
        string='Archive Size (Bytes)',
        default=0,
        readonly=True,
        help='Estimated size of archived data in bytes'
    )

    error_log = fields.Text(
        string='Error Log',
        readonly=True
    )

    additional_filters = fields.Text(
        string='Additional Filters (JSON)',
        help='JSON domain for additional filtering'
    )

    keep_posted_only = fields.Boolean(
        string='Posted Records Only',
        default=True,
        help='For accounting records, only archive posted entries'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    created_by_user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    is_automatic = fields.Boolean(
        string='Automatic Job',
        default=False,
        help='Created by automated cron job'
    )

    # ========================================================================
    # COMPUTE METHODS
    # ========================================================================

    @api.depends('model_name', 'archive_date')
    def _compute_name(self):
        """Generate job name."""
        for job in self:
            if job.model_name and job.archive_date:
                model_label = dict(job._fields['model_name'].selection).get(job.model_name)
                job.name = f"Archive {model_label} before {job.archive_date}"
            else:
                job.name = "New Archive Job"

    # ========================================================================
    # ARCHIVAL EXECUTION
    # ========================================================================

    def action_run_archive(self):
        """Execute the archival job."""
        self.ensure_one()

        if self.state not in ['draft', 'failed']:
            raise UserError(_("Only draft or failed jobs can be run."))

        # Update state
        self.write({
            'state': 'running',
            'start_date': fields.Datetime.now(),
            'error_log': False,
        })

        try:
            # Calculate archive threshold date
            threshold_date = fields.Date.today() - timedelta(days=self.record_age_days)

            # Get records to archive
            domain = self._get_archive_domain(threshold_date)
            records = self.env[self.model_name].search(domain)

            self.write({'records_found': len(records)})

            _logger.info(f"Starting archival job: {self.name} - Found {len(records)} records")

            # Archive in batches
            batch_size = 100
            archived_count = 0
            failed_count = 0
            errors = []

            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]

                try:
                    # Archive batch
                    self._archive_batch(batch)
                    archived_count += len(batch)

                    # Commit after each batch
                    self.env.cr.commit()

                    _logger.info(f"Archived batch {i // batch_size + 1}: {len(batch)} records")

                except Exception as e:
                    failed_count += len(batch)
                    error_msg = f"Batch {i // batch_size + 1} failed: {str(e)}"
                    errors.append(error_msg)
                    _logger.error(error_msg)

                    # Rollback this batch and continue
                    self.env.cr.rollback()

            # Update job status
            self.write({
                'state': 'completed' if failed_count == 0 else 'failed',
                'end_date': fields.Datetime.now(),
                'records_archived': archived_count,
                'records_failed': failed_count,
                'error_log': '\n'.join(errors) if errors else False,
            })

            # Log completion
            self.env['ops.security.audit'].sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'data_archived',
                'model_name': self.model_name,
                'details': f"Archived {archived_count} records from {self.model_name}",
                'severity': 'info',
            })

            _logger.info(
                f"Archival job completed: {self.name} - "
                f"Archived: {archived_count}, Failed: {failed_count}"
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Archival Completed'),
                    'message': _('%d records archived successfully, %d failed') % (
                        archived_count, failed_count
                    ),
                    'type': 'success' if failed_count == 0 else 'warning',
                }
            }

        except Exception as e:
            # Job failed completely
            self.write({
                'state': 'failed',
                'end_date': fields.Datetime.now(),
                'error_log': str(e),
            })

            _logger.error(f"Archival job failed: {self.name} - Error: {str(e)}")

            raise UserError(_("Archival job failed: %s") % str(e))

    def _get_archive_domain(self, threshold_date):
        """Build domain for records to archive."""
        domain = []

        # Model-specific filters
        if self.model_name == 'account.move':
            domain = [
                ('date', '<', threshold_date),
            ]
            if self.keep_posted_only:
                domain.append(('state', '=', 'posted'))

        elif self.model_name == 'sale.order':
            domain = [
                ('date_order', '<', threshold_date),
                ('state', 'in', ['sale', 'done', 'cancel']),  # Only completed/cancelled orders
            ]

        elif self.model_name == 'purchase.order':
            domain = [
                ('date_order', '<', threshold_date),
                ('state', 'in', ['purchase', 'done', 'cancel']),
            ]

        elif self.model_name == 'stock.picking':
            domain = [
                ('date_done', '<', threshold_date),
                ('state', '=', 'done'),
            ]

        elif self.model_name == 'ops.security.audit':
            domain = [
                ('timestamp', '<', fields.Datetime.to_datetime(threshold_date)),
                ('severity', '!=', 'critical'),  # Keep critical logs
            ]

        elif self.model_name == 'ops.session.manager':
            domain = [
                ('logout_time', '<', fields.Datetime.to_datetime(threshold_date)),
                ('is_active', '=', False),
                ('is_suspicious', '=', False),  # Keep suspicious sessions
            ]

        # Add company filter
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))

        # Add additional filters from JSON
        if self.additional_filters:
            try:
                additional = json.loads(self.additional_filters)
                if isinstance(additional, list):
                    domain.extend(additional)
            except json.JSONDecodeError:
                _logger.warning(f"Invalid additional filters JSON: {self.additional_filters}")

        return domain

    def _archive_batch(self, records):
        """Archive a batch of records."""
        # Create archived records
        for record in records:
            try:
                # Serialize record data
                record_data = self._serialize_record(record)

                # Create archive entry
                self.env['ops.archived.record'].sudo().create({
                    'original_model': self.model_name,
                    'original_id': record.id,
                    'archive_job_id': self.id,
                    'record_data': json.dumps(record_data),
                    'company_id': record.company_id.id if hasattr(record, 'company_id') else False,
                })

            except Exception as e:
                _logger.error(f"Failed to archive record {record.id}: {str(e)}")
                raise

        # Delete original records
        # NOTE: This is destructive! Ensure backups exist!
        records.unlink()

    def _serialize_record(self, record):
        """Serialize record to JSON-compatible dict."""
        data = {}

        # Get all fields except computed and related
        for field_name, field in record._fields.items():
            if field.store and field_name not in ['__last_update', 'display_name']:
                try:
                    value = record[field_name]

                    # Handle different field types
                    if field.type == 'many2one':
                        data[field_name] = {'id': value.id, 'name': value.display_name} if value else None
                    elif field.type in ['one2many', 'many2many']:
                        data[field_name] = [{'id': r.id, 'name': r.display_name} for r in value]
                    elif field.type in ['date', 'datetime']:
                        data[field_name] = value.isoformat() if value else None
                    elif field.type == 'binary':
                        # Don't store large binary data
                        data[field_name] = '<binary data omitted>'
                    else:
                        data[field_name] = value

                except Exception as e:
                    _logger.warning(f"Could not serialize field {field_name}: {str(e)}")
                    data[field_name] = None

        return data

    # ========================================================================
    # ACTIONS
    # ========================================================================

    def action_cancel(self):
        """Cancel a running job."""
        self.ensure_one()

        if self.state != 'running':
            raise UserError(_("Only running jobs can be cancelled."))

        self.write({
            'state': 'cancelled',
            'end_date': fields.Datetime.now(),
        })

    def action_reset_to_draft(self):
        """Reset failed job to draft for retry."""
        self.ensure_one()

        if self.state not in ['failed', 'completed']:
            raise UserError(_("Only failed or completed jobs can be reset."))

        self.write({'state': 'draft'})

    def action_view_archived_records(self):
        """View archived records from this job."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Archived Records'),
            'res_model': 'ops.archived.record',
            'view_mode': 'tree,form',
            'domain': [('archive_job_id', '=', self.id)],
        }

    # ========================================================================
    # AUTOMATED ARCHIVAL
    # ========================================================================

    @api.model
    def run_automatic_archival(self):
        """
        Run automatic archival for all configured models.
        Called by cron job.
        """
        # Get configuration
        config = self.env['ir.config_parameter'].sudo()
        auto_archive_enabled = config.get_param('ops.archival.auto_enabled', default='False') == 'True'

        if not auto_archive_enabled:
            _logger.info("Automatic archival is disabled")
            return

        default_age_days = int(config.get_param('ops.archival.default_age_days', default='730'))

        # Models to auto-archive
        models_to_archive = [
            'account.move',
            'sale.order',
            'purchase.order',
            'stock.picking',
            'ops.security.audit',
            'ops.session.manager',
        ]

        jobs_created = []

        for model_name in models_to_archive:
            try:
                # Check if there are records to archive
                threshold_date = fields.Date.today() - timedelta(days=default_age_days)

                job = self.create({
                    'model_name': model_name,
                    'archive_date': threshold_date,
                    'record_age_days': default_age_days,
                    'is_automatic': True,
                })

                # Run immediately
                job.action_run_archive()

                jobs_created.append(job)

            except Exception as e:
                _logger.error(f"Automatic archival failed for {model_name}: {str(e)}")

        _logger.info(f"Automatic archival completed: {len(jobs_created)} jobs processed")

        return jobs_created

    # ========================================================================
    # REPORTING
    # ========================================================================

    @api.model
    def get_archival_statistics(self):
        """Get archival statistics for dashboard."""
        return {
            'total_jobs': self.search_count([]),
            'completed_jobs': self.search_count([('state', '=', 'completed')]),
            'failed_jobs': self.search_count([('state', '=', 'failed')]),
            'total_archived': sum(self.search([]).mapped('records_archived')),
            'archived_this_month': sum(self.search([
                ('end_date', '>=', fields.Date.today().replace(day=1))
            ]).mapped('records_archived')),
        }


class OpsArchivedRecord(models.Model):
    """Store archived records."""
    _name = 'ops.archived.record'
    _description = 'Archived Record'
    _order = 'archive_date desc'

    # ========================================================================
    # FIELDS
    # ========================================================================

    original_model = fields.Char(
        string='Original Model',
        required=True,
        readonly=True,
        index=True
    )

    original_id = fields.Integer(
        string='Original ID',
        required=True,
        readonly=True,
        index=True
    )

    archive_job_id = fields.Many2one(
        'ops.data.archival',
        string='Archive Job',
        required=True,
        readonly=True,
        ondelete='cascade'
    )

    archive_date = fields.Datetime(
        string='Archive Date',
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        index=True
    )

    record_data = fields.Text(
        string='Record Data (JSON)',
        required=True,
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True
    )

    restored = fields.Boolean(
        string='Restored',
        default=False,
        readonly=True
    )

    restored_date = fields.Datetime(
        string='Restored Date',
        readonly=True
    )

    # ========================================================================
    # RESTORE FUNCTIONALITY
    # ========================================================================

    def action_restore(self):
        """Restore archived record (careful - may cause issues)."""
        self.ensure_one()

        if self.restored:
            raise UserError(_("This record has already been restored."))

        # This is complex and risky - would need careful implementation
        # For now, just show the data
        return {
            'type': 'ir.actions.act_window',
            'name': _('Restore Archived Record'),
            'res_model': 'ops.restore.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_archived_record_id': self.id,
                'default_record_data': self.record_data,
            },
        }

    def action_view_data(self):
        """View archived record data."""
        self.ensure_one()

        try:
            data = json.loads(self.record_data)
            formatted = json.dumps(data, indent=2)
        except:
            formatted = self.record_data

        return {
            'type': 'ir.actions.act_window',
            'name': _('Archived Record Data'),
            'res_model': 'ops.archived.record',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
        }
