from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


def _get_safe_eval_context(env):
    """
    Build a safe evaluation context for KPI domain filters.
    Provides common date functions and utilities.
    """
    today = fields.Date.context_today(env['res.users'])

    def context_today():
        """Return today's date (compatible with Odoo domain syntax)."""
        return today

    return {
        'datetime': datetime,
        'date': date,
        'timedelta': timedelta,
        'relativedelta': relativedelta,
        'context_today': context_today,
        'today': today,
        'uid': env.uid,
    }


class OpsKpiValue(models.Model):
    """
    KPI Computed Values - Stores calculated KPI values.
    Can be computed in real-time or cached via cron.
    """
    _name = 'ops.kpi.value'
    _description = 'KPI Computed Value'
    _order = 'compute_date desc'
    _rec_name = 'kpi_id'

    kpi_id = fields.Many2one('ops.kpi', string='KPI', required=True, ondelete='cascade')

    # Scope
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    branch_id = fields.Many2one('ops.branch', string='Branch',
                                help='If set, value is branch-specific')
    user_id = fields.Many2one('res.users', string='Computed For',
                              help='If set, value is user-specific')

    # Values
    value = fields.Float(string='Value', digits=(16, 2))
    previous_value = fields.Float(string='Previous Period Value', digits=(16, 2))
    trend_percentage = fields.Float(string='Trend %', compute='_compute_trend', store=True)
    trend_direction = fields.Selection([
        ('up', 'Up'),
        ('down', 'Down'),
        ('flat', 'Flat'),
    ], string='Trend', compute='_compute_trend', store=True)

    # Period
    period = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('last_30_days', 'Last 30 Days'),
        ('last_90_days', 'Last 90 Days'),
        ('all_time', 'All Time'),
    ], string='Period', required=True)

    # Timestamps
    compute_date = fields.Datetime(string='Computed At', default=fields.Datetime.now)
    period_start = fields.Date(string='Period Start')
    period_end = fields.Date(string='Period End')

    @api.depends('value', 'previous_value')
    def _compute_trend(self):
        for record in self:
            if record.previous_value and record.previous_value != 0:
                change = ((record.value - record.previous_value) / abs(record.previous_value)) * 100
                record.trend_percentage = round(change, 1)
                if change > 1:
                    record.trend_direction = 'up'
                elif change < -1:
                    record.trend_direction = 'down'
                else:
                    record.trend_direction = 'flat'
            else:
                record.trend_percentage = 0
                record.trend_direction = 'flat'

    @api.model
    def _get_period_dates(self, period):
        """Calculate start and end dates for a period."""
        today = fields.Date.context_today(self)

        if period == 'today':
            return today, today
        elif period == 'this_week':
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == 'this_month':
            start = today.replace(day=1)
            return start, today
        elif period == 'this_quarter':
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter * 3 + 1, day=1)
            return start, today
        elif period == 'this_year':
            start = today.replace(month=1, day=1)
            return start, today
        elif period == 'last_30_days':
            start = today - timedelta(days=30)
            return start, today
        elif period == 'last_90_days':
            start = today - timedelta(days=90)
            return start, today
        else:  # all_time
            return None, None

    @api.model
    def _get_previous_period_dates(self, period, current_start, current_end):
        """Calculate previous period dates for comparison."""
        if not current_start or not current_end:
            return None, None

        delta = (current_end - current_start).days + 1

        if period in ('today', 'this_week', 'last_30_days', 'last_90_days'):
            prev_end = current_start - timedelta(days=1)
            prev_start = prev_end - timedelta(days=delta - 1)
        elif period == 'this_month':
            prev_end = current_start - timedelta(days=1)
            prev_start = prev_end.replace(day=1)
        elif period == 'this_quarter':
            prev_end = current_start - timedelta(days=1)
            quarter = (prev_end.month - 1) // 3
            prev_start = prev_end.replace(month=quarter * 3 + 1, day=1)
        elif period == 'this_year':
            prev_start = current_start - relativedelta(years=1)
            prev_end = current_end - relativedelta(years=1)
        else:
            return None, None

        return prev_start, prev_end

    @api.model
    def compute_kpi_value(self, kpi, period=None, branch_id=None, user_id=None):
        """
        Compute KPI value respecting OPS security.
        Returns dict with value, previous_value, trend info.
        """
        if not kpi._check_user_access():
            return {'error': 'Access Denied', 'value': 0}

        period = period or kpi.default_period
        period_start, period_end = self._get_period_dates(period)

        # Build secure domain with proper evaluation context
        eval_context = _get_safe_eval_context(self.env)
        base_domain = safe_eval(kpi.domain_filter, eval_context) if kpi.domain_filter else []
        domain = kpi._get_secure_domain(base_domain)

        # Add date filter if applicable
        if period_start and period_end and kpi.date_field:
            domain.extend([
                (kpi.date_field, '>=', fields.Date.to_string(period_start)),
                (kpi.date_field, '<=', fields.Date.to_string(period_end)),
            ])

        # Compute current value
        try:
            Model = self.env[kpi.source_model]

            if kpi.calculation_type == 'count':
                value = Model.search_count(domain)
            elif kpi.calculation_type == 'sum':
                records = Model.search(domain)
                value = sum(records.mapped(kpi.measure_field) or [0])
            elif kpi.calculation_type == 'average':
                records = Model.search(domain)
                values = records.mapped(kpi.measure_field) or [0]
                value = sum(values) / len(values) if values else 0
            else:
                value = 0
        except Exception as e:
            _logger.error("Error computing KPI %s: %s", kpi.code, str(e))
            return {'error': str(e), 'value': 0}

        # Compute previous period value for trend
        previous_value = 0
        if kpi.show_trend:
            prev_start, prev_end = self._get_previous_period_dates(
                period, period_start, period_end
            )
            if prev_start and prev_end:
                prev_domain = kpi._get_secure_domain(base_domain)
                if kpi.date_field:
                    prev_domain.extend([
                        (kpi.date_field, '>=', fields.Date.to_string(prev_start)),
                        (kpi.date_field, '<=', fields.Date.to_string(prev_end)),
                    ])
                try:
                    if kpi.calculation_type == 'count':
                        previous_value = Model.search_count(prev_domain)
                    elif kpi.calculation_type == 'sum':
                        records = Model.search(prev_domain)
                        previous_value = sum(records.mapped(kpi.measure_field) or [0])
                    elif kpi.calculation_type == 'average':
                        records = Model.search(prev_domain)
                        values = records.mapped(kpi.measure_field) or [0]
                        previous_value = sum(values) / len(values) if values else 0
                except Exception as e:
                    _logger.warning("Error computing previous KPI %s: %s", kpi.code, str(e))

        # Calculate trend
        trend_pct = 0
        trend_dir = 'flat'
        if previous_value and previous_value != 0:
            trend_pct = round(((value - previous_value) / abs(previous_value)) * 100, 1)
            if trend_pct > 1:
                trend_dir = 'up'
            elif trend_pct < -1:
                trend_dir = 'down'

        return {
            'kpi_id': kpi.id,
            'kpi_code': kpi.code,
            'kpi_name': kpi.name,
            'value': value,
            'previous_value': previous_value,
            'trend_percentage': trend_pct,
            'trend_direction': trend_dir,
            'trend_is_good': (
                (trend_dir == 'up' and kpi.trend_direction == 'up_good') or
                (trend_dir == 'down' and kpi.trend_direction == 'down_good') or
                kpi.trend_direction == 'neutral'
            ),
            'period': period,
            'period_start': period_start,
            'period_end': period_end,
            'format_type': kpi.format_type,
            'icon': kpi.icon,
            'color': kpi.color,
            'category': kpi.category,
        }
