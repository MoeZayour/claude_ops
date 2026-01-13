# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)


class OpsPerformanceMonitor(models.Model):
    """
    Performance Monitoring and Alerting System

    Features:
    - Track slow queries (>1 second)
    - Monitor report generation times
    - Alert on anomalies
    - Dashboard for admins
    - Recommend missing indexes
    """
    _name = 'ops.performance.monitor'
    _description = 'OPS Performance Monitor'
    _order = 'timestamp desc'

    # ========================================================================
    # FIELDS
    # ========================================================================

    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        index=True
    )

    operation_type = fields.Selection([
        ('query', 'Database Query'),
        ('report', 'Report Generation'),
        ('search', 'Search Operation'),
        ('write', 'Write Operation'),
        ('read', 'Read Operation'),
        ('compute', 'Compute Field'),
        ('api_call', 'API Call'),
    ], string='Operation Type', required=True, readonly=True, index=True)

    operation_name = fields.Char(
        string='Operation Name',
        required=True,
        readonly=True,
        help='Name or description of the operation'
    )

    duration_ms = fields.Integer(
        string='Duration (ms)',
        required=True,
        readonly=True,
        help='Execution time in milliseconds',
        index=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True,
        ondelete='restrict'
    )

    model_name = fields.Char(
        string='Model',
        readonly=True,
        index=True
    )

    record_count = fields.Integer(
        string='Record Count',
        default=0,
        readonly=True,
        help='Number of records processed'
    )

    sql_query = fields.Text(
        string='SQL Query',
        readonly=True,
        help='SQL query that was executed (if applicable)'
    )

    is_slow = fields.Boolean(
        string='Slow Operation',
        compute='_compute_is_slow',
        store=True,
        index=True
    )

    severity = fields.Selection([
        ('info', 'Normal'),
        ('warning', 'Slow'),
        ('critical', 'Very Slow'),
    ], string='Severity', compute='_compute_severity', store=True, index=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True
    )

    context_data = fields.Text(
        string='Context',
        readonly=True,
        help='Additional context about the operation (JSON)'
    )

    # ========================================================================
    # COMPUTE METHODS
    # ========================================================================

    @api.depends('duration_ms', 'operation_type')
    def _compute_is_slow(self):
        """Determine if operation is slow based on thresholds."""
        # Get thresholds from config
        config = self.env['ir.config_parameter'].sudo()

        thresholds = {
            'query': int(config.get_param('ops.perf.threshold.query', default='1000')),
            'report': int(config.get_param('ops.perf.threshold.report', default='5000')),
            'search': int(config.get_param('ops.perf.threshold.search', default='500')),
            'write': int(config.get_param('ops.perf.threshold.write', default='2000')),
            'read': int(config.get_param('ops.perf.threshold.read', default='500')),
            'compute': int(config.get_param('ops.perf.threshold.compute', default='1000')),
            'api_call': int(config.get_param('ops.perf.threshold.api', default='3000')),
        }

        for monitor in self:
            threshold = thresholds.get(monitor.operation_type, 1000)
            monitor.is_slow = monitor.duration_ms > threshold

    @api.depends('duration_ms', 'operation_type')
    def _compute_severity(self):
        """Classify severity based on how slow the operation is."""
        config = self.env['ir.config_parameter'].sudo()

        for monitor in self:
            # Base thresholds
            warning_threshold = 1000  # 1 second
            critical_threshold = 5000  # 5 seconds

            # Adjust by operation type
            if monitor.operation_type == 'report':
                warning_threshold = 5000
                critical_threshold = 15000
            elif monitor.operation_type in ['search', 'read']:
                warning_threshold = 500
                critical_threshold = 2000

            if monitor.duration_ms >= critical_threshold:
                monitor.severity = 'critical'
            elif monitor.duration_ms >= warning_threshold:
                monitor.severity = 'warning'
            else:
                monitor.severity = 'info'

    # ========================================================================
    # MONITORING METHODS
    # ========================================================================

    @api.model
    def log_operation(self, operation_type, operation_name, duration_ms, **kwargs):
        """
        Log a performance metric.

        Args:
            operation_type: Type of operation
            operation_name: Name/description of operation
            duration_ms: Duration in milliseconds
            **kwargs: Additional context (user_id, model_name, record_count, etc.)
        """
        # Only log slow operations to save space (configurable)
        config = self.env['ir.config_parameter'].sudo()
        log_all = config.get_param('ops.perf.log_all', default='False') == 'True'

        if not log_all:
            thresholds = {
                'query': 1000,
                'report': 5000,
                'search': 500,
                'write': 2000,
                'read': 500,
                'compute': 1000,
                'api_call': 3000,
            }
            threshold = thresholds.get(operation_type, 1000)

            if duration_ms < threshold:
                return  # Don't log fast operations

        # Create monitor record
        vals = {
            'operation_type': operation_type,
            'operation_name': operation_name,
            'duration_ms': duration_ms,
            'user_id': kwargs.get('user_id') or self.env.user.id,
            'model_name': kwargs.get('model_name'),
            'record_count': kwargs.get('record_count', 0),
            'sql_query': kwargs.get('sql_query'),
            'company_id': kwargs.get('company_id') or self.env.company.id,
            'context_data': kwargs.get('context_data'),
        }

        monitor = self.sudo().create(vals)

        # Log critical operations
        if monitor.severity == 'critical':
            _logger.warning(
                f"Slow operation detected: {operation_name} took {duration_ms}ms "
                f"(type: {operation_type}, user: {monitor.user_id.name})"
            )

            # Create security audit entry for very slow operations
            self.env['ops.security.audit'].sudo().create({
                'user_id': monitor.user_id.id,
                'event_type': 'performance_alert',
                'model_name': monitor.model_name,
                'details': f"Very slow operation: {operation_name} took {duration_ms}ms",
                'severity': 'warning',
            })

        return monitor

    @api.model
    def log_query(self, query, duration_ms, **kwargs):
        """Log a database query."""
        return self.log_operation(
            'query',
            f"SQL Query ({len(query)} chars)",
            duration_ms,
            sql_query=query,
            **kwargs
        )

    @api.model
    def log_report(self, report_name, duration_ms, **kwargs):
        """Log a report generation."""
        return self.log_operation(
            'report',
            f"Report: {report_name}",
            duration_ms,
            **kwargs
        )

    # ========================================================================
    # CONTEXT MANAGER FOR AUTOMATIC TRACKING
    # ========================================================================

    @api.model
    def track(self, operation_type, operation_name, **kwargs):
        """
        Context manager to automatically track operation duration.

        Usage:
            with self.env['ops.performance.monitor'].track('report', 'Sales Report'):
                # ... operation code ...
                pass
        """
        return PerformanceTracker(self, operation_type, operation_name, **kwargs)

    # ========================================================================
    # ANALYTICS & REPORTING
    # ========================================================================

    @api.model
    def get_slow_operations(self, days=7, limit=50):
        """Get slowest operations in last N days."""
        date_from = fields.Datetime.now() - timedelta(days=days)

        return self.search([
            ('timestamp', '>=', date_from),
            ('is_slow', '=', True)
        ], order='duration_ms desc', limit=limit)

    @api.model
    def get_performance_trends(self, days=30):
        """Get performance trends over time."""
        date_from = fields.Datetime.now() - timedelta(days=days)

        self.env.cr.execute("""
            SELECT
                DATE(timestamp) as date,
                operation_type,
                COUNT(*) as count,
                AVG(duration_ms) as avg_duration,
                MAX(duration_ms) as max_duration,
                SUM(CASE WHEN is_slow THEN 1 ELSE 0 END) as slow_count
            FROM ops_performance_monitor
            WHERE timestamp >= %s
            GROUP BY DATE(timestamp), operation_type
            ORDER BY date DESC, operation_type
        """, (date_from,))

        results = self.env.cr.fetchall()

        trends = []
        for row in results:
            trends.append({
                'date': row[0],
                'operation_type': row[1],
                'count': row[2],
                'avg_duration': int(row[3]),
                'max_duration': row[4],
                'slow_count': row[5],
            })

        return trends

    @api.model
    def get_model_performance(self, days=7):
        """Get performance statistics by model."""
        date_from = fields.Datetime.now() - timedelta(days=days)

        self.env.cr.execute("""
            SELECT
                model_name,
                operation_type,
                COUNT(*) as count,
                AVG(duration_ms) as avg_duration,
                SUM(CASE WHEN is_slow THEN 1 ELSE 0 END) as slow_count
            FROM ops_performance_monitor
            WHERE timestamp >= %s
            AND model_name IS NOT NULL
            GROUP BY model_name, operation_type
            ORDER BY avg_duration DESC
            LIMIT 50
        """, (date_from,))

        results = self.env.cr.fetchall()

        stats = []
        for row in results:
            stats.append({
                'model_name': row[0],
                'operation_type': row[1],
                'count': row[2],
                'avg_duration': int(row[3]),
                'slow_count': row[4],
            })

        return stats

    @api.model
    def recommend_indexes(self):
        """
        Analyze slow queries and recommend missing indexes.
        This is a simplified version - real analysis would be more complex.
        """
        # Get slow queries
        slow_queries = self.search([
            ('operation_type', '=', 'query'),
            ('is_slow', '=', True),
            ('sql_query', '!=', False)
        ], order='duration_ms desc', limit=100)

        recommendations = []

        # Simple heuristic: look for WHERE clauses without indexes
        for query in slow_queries:
            if not query.sql_query:
                continue

            # Look for common patterns
            sql_lower = query.sql_query.lower()

            # Check for table scans
            if 'where' in sql_lower and 'limit' not in sql_lower:
                recommendations.append({
                    'query': query.sql_query[:200],
                    'duration_ms': query.duration_ms,
                    'recommendation': 'Consider adding an index on WHERE clause columns',
                    'model': query.model_name,
                })

        return recommendations

    @api.model
    def get_dashboard_data(self):
        """Get performance dashboard data."""
        now = fields.Datetime.now()
        today = now.replace(hour=0, minute=0, second=0)

        return {
            'slow_operations_today': self.search_count([
                ('timestamp', '>=', today),
                ('is_slow', '=', True)
            ]),
            'critical_operations_today': self.search_count([
                ('timestamp', '>=', today),
                ('severity', '=', 'critical')
            ]),
            'avg_duration_today': self._get_avg_duration(today),
            'slowest_model': self._get_slowest_model(days=1),
            'total_operations_today': self.search_count([
                ('timestamp', '>=', today)
            ]),
        }

    def _get_avg_duration(self, date_from):
        """Get average duration since date."""
        self.env.cr.execute("""
            SELECT AVG(duration_ms)
            FROM ops_performance_monitor
            WHERE timestamp >= %s
        """, (date_from,))

        result = self.env.cr.fetchone()
        return int(result[0]) if result and result[0] else 0

    def _get_slowest_model(self, days=1):
        """Get slowest model in last N days."""
        date_from = fields.Datetime.now() - timedelta(days=days)

        self.env.cr.execute("""
            SELECT model_name, AVG(duration_ms) as avg_duration
            FROM ops_performance_monitor
            WHERE timestamp >= %s
            AND model_name IS NOT NULL
            GROUP BY model_name
            ORDER BY avg_duration DESC
            LIMIT 1
        """, (date_from,))

        result = self.env.cr.fetchone()
        return result[0] if result else None

    # ========================================================================
    # CLEANUP
    # ========================================================================

    @api.model
    def cleanup_old_records(self, days=30):
        """Clean up old performance records."""
        threshold_date = fields.Datetime.now() - timedelta(days=days)

        old_records = self.search([
            ('timestamp', '<', threshold_date),
            ('severity', '!=', 'critical'),  # Keep critical logs longer
        ])

        count = len(old_records)
        old_records.unlink()

        _logger.info(f"Cleaned up {count} old performance monitor records (>{days} days)")

        return count


class PerformanceTracker:
    """Context manager for tracking operation performance."""

    def __init__(self, monitor_model, operation_type, operation_name, **kwargs):
        self.monitor_model = monitor_model
        self.operation_type = operation_type
        self.operation_name = operation_name
        self.kwargs = kwargs
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)

        # Log the operation
        self.monitor_model.log_operation(
            self.operation_type,
            self.operation_name,
            duration_ms,
            **self.kwargs
        )

        return False  # Don't suppress exceptions
