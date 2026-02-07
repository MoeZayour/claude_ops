from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)


class OpsKpi(models.Model):
    """
    KPI Definition - Defines what metrics can be displayed.
    Security-aware: respects OPS Matrix access controls.
    Enterprise dashboard with persona-based visibility.
    """
    _name = 'ops.kpi'
    _description = 'KPI Definition'
    _order = 'sequence, name'

    name = fields.Char(string='KPI Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, index=True,
                       help='Unique identifier: SALES_TOTAL, AR_AGING_30, etc.')
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Categorization - Extended for enterprise
    category = fields.Selection([
        ('sales', 'Sales'),
        ('purchase', 'Purchase'),
        ('inventory', 'Inventory'),
        ('finance', 'Finance'),
        ('receivable', 'Accounts Receivable'),
        ('payable', 'Accounts Payable'),
        ('pdc', 'PDC Management'),
        ('treasury', 'Treasury'),
        ('budget', 'Budget'),
        ('asset', 'Assets'),
        ('governance', 'Governance'),
        ('system', 'System'),
        ('operations', 'Operations'),
    ], string='Category', required=True, default='sales')

    # Data Source Configuration
    source_model = fields.Char(string='Source Model', required=True,
                               help='Odoo model name: sale.order, account.move, etc.')
    calculation_type = fields.Selection([
        ('count', 'Count Records'),
        ('sum', 'Sum Field'),
        ('average', 'Average Field'),
        ('custom', 'Custom Method'),
    ], string='Calculation', required=True, default='count')

    measure_field = fields.Char(string='Measure Field',
                                help='Field to sum/average: amount_total, etc.')
    domain_filter = fields.Char(string='Domain Filter', default='[]',
                                help='Additional domain filter as Python list')
    custom_formula = fields.Text(
        string='Custom Formula',
        help='Python expression for custom calculation type. '
             'Available context: env, model, domain, date, datetime, timedelta, relativedelta, today, uid.'
    )

    # Date Filtering
    date_field = fields.Char(string='Date Field', default='create_date',
                             help='Field for date range filtering')
    default_period = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('last_30_days', 'Last 30 Days'),
        ('last_90_days', 'Last 90 Days'),
        ('all_time', 'All Time'),
    ], string='Default Period', default='this_month')

    # Display Configuration
    format_type = fields.Selection([
        ('number', 'Number'),
        ('currency', 'Currency'),
        ('percentage', 'Percentage'),
        ('integer', 'Integer'),
    ], string='Format', default='number')

    icon = fields.Char(string='Icon', default='fa-chart-line',
                       help='FontAwesome icon class')
    color = fields.Char(string='Color', default='#3b82f6',
                        help='Hex color for the KPI card')

    # Trend Comparison
    show_trend = fields.Boolean(string='Show Trend', default=True,
                                help='Show comparison with previous period')
    trend_direction = fields.Selection([
        ('up_good', 'Up is Good (e.g., Sales)'),
        ('down_good', 'Down is Good (e.g., Expenses)'),
        ('neutral', 'Neutral'),
    ], string='Trend Direction', default='up_good')

    # OPS Security
    requires_cost_access = fields.Boolean(string='Requires Cost Access',
                                          help='Only show to users with group_ops_see_cost')
    requires_margin_access = fields.Boolean(string='Requires Margin Access',
                                            help='Only show to users with group_ops_see_margin')
    visible_to_it_admin = fields.Boolean(string='Visible to IT Admin', default=False,
                                         help='Should always be False for business data')

    # Persona Targeting - Enhanced for enterprise dashboards
    persona_ids = fields.Many2many('ops.persona', string='Target Personas',
                                   help='Which personas should see this KPI')

    # Scope Type - Determines data visibility level
    scope_type = fields.Selection([
        ('company', 'Company-Wide'),
        ('bu', 'Business Unit'),
        ('branch', 'Branch'),
        ('own', 'Own Records Only'),
    ], string='Data Scope', default='branch',
       help='company=All, bu=BU branches, branch=Own branch, own=Own records')

    _code_unique = models.Constraint(
        'unique(code)',
        'KPI code must be unique!',
    )

    @api.constrains('source_model')
    def _check_source_model(self):
        """Validate source model exists."""
        for kpi in self:
            if kpi.source_model:
                if kpi.source_model not in self.env:
                    raise ValidationError(
                        _("Model '%s' does not exist.") % kpi.source_model
                    )

    @api.constrains('domain_filter')
    def _check_domain_filter(self):
        """Prevent excessively large domain filters."""
        for record in self:
            if record.domain_filter and len(record.domain_filter) > 2000:
                raise ValidationError(_('Domain filter must not exceed 2000 characters.'))

    def _get_safe_eval_context(self):
        """Build a safe evaluation context for custom KPI formulas."""
        self.ensure_one()
        from datetime import datetime, timedelta, date
        from dateutil.relativedelta import relativedelta

        today = fields.Date.context_today(self)
        Model = self.env.get(self.source_model)

        # Build secure domain
        from .ops_kpi_value import _get_safe_eval_context as _base_eval_ctx
        base_eval = _base_eval_ctx(self.env)
        base_domain = safe_eval(self.domain_filter, base_eval) if self.domain_filter else []
        domain = self._get_secure_domain(base_domain)

        return {
            'env': self.env,
            'model': Model,
            'domain': domain,
            'date': date,
            'datetime': datetime,
            'timedelta': timedelta,
            'relativedelta': relativedelta,
            'today': today,
            'uid': self.env.uid,
        }

    def _get_secure_domain(self, base_domain=None):
        """
        Build security-compliant domain for queries.
        CRITICAL: This method enforces OPS Matrix security.
        Respects scope_type: company, bu, branch, own
        """
        self.ensure_one()
        user = self.env.user
        domain = list(base_domain or [])

        # IT Admin Blindness - they see NOTHING for business data
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            if not self.visible_to_it_admin:
                return [('id', '=', 0)]  # Return empty result

        # Get model reference
        model = self.env.get(self.source_model)
        if model is None:
            return domain

        # Apply scope-based filtering
        scope = self.scope_type or 'branch'

        if scope == 'company':
            # Company-wide: Only company filter (for execs)
            pass

        elif scope == 'bu':
            # Business Unit: All branches in user's BU
            if 'ops_branch_id' in model._fields:
                if hasattr(user, 'ops_business_unit_id') and user.ops_business_unit_id:
                    bu_branches = self.env['ops.branch'].search([
                        ('business_unit_id', '=', user.ops_business_unit_id.id)
                    ])
                    domain.append(('ops_branch_id', 'in', bu_branches.ids))

        elif scope == 'branch':
            # Branch: User's allowed branches only
            if not user.has_group('ops_matrix_core.group_ops_manager'):
                branch_ids = user.ops_allowed_branch_ids.ids if hasattr(user, 'ops_allowed_branch_ids') else []
                if branch_ids and 'ops_branch_id' in model._fields:
                    domain.append(('ops_branch_id', 'in', branch_ids))

        elif scope == 'own':
            # Own records only: Filter by create_uid or user_id
            if 'user_id' in model._fields:
                domain.append(('user_id', '=', user.id))
            elif 'create_uid' in model._fields:
                domain.append(('create_uid', '=', user.id))
            # Also apply branch filter for own scope
            if not user.has_group('ops_matrix_core.group_ops_manager'):
                branch_ids = user.ops_allowed_branch_ids.ids if hasattr(user, 'ops_allowed_branch_ids') else []
                if branch_ids and 'ops_branch_id' in model._fields:
                    domain.append(('ops_branch_id', 'in', branch_ids))

        # Company Filter (always applied)
        if 'company_id' in model._fields:
            domain.append(('company_id', 'in', self.env.companies.ids))

        return domain

    def _check_user_access(self):
        """
        Check if current user can view this KPI.
        Checks: IT Admin blindness, cost/margin access, persona codes.
        """
        self.ensure_one()
        user = self.env.user

        # System admin bypasses all
        if user.has_group('base.group_system'):
            return True

        # IT Admin check - only system KPIs visible
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            if not self.visible_to_it_admin:
                return False

        # Cost access check
        if self.requires_cost_access:
            if not user.has_group('ops_matrix_core.group_ops_see_cost'):
                return False

        # Margin access check
        if self.requires_margin_access:
            if not user.has_group('ops_matrix_core.group_ops_see_margin'):
                return False

        # Persona check (if specified via Many2many)
        if self.persona_ids:
            user_personas = user.ops_persona_ids if hasattr(user, 'ops_persona_ids') else self.env['ops.persona']
            if not (user_personas & self.persona_ids):
                return False

        return True

    def compute_value(self, period=None):
        """
        Compute KPI value for current user with security.
        Wrapper for ops.kpi.value.compute_kpi_value().
        """
        self.ensure_one()
        return self.env['ops.kpi.value'].compute_kpi_value(self, period=period)

    def get_time_series(self, period='this_month', granularity='day'):
        """
        Get time series data for trend charts (area/line charts).
        Returns list of {date, value} points for charting.

        Uses read_group for batched aggregation instead of per-point queries.

        Args:
            period: 'today', 'this_week', 'this_month', 'this_quarter', 'this_year', 'last_30_days'
            granularity: 'day', 'week', 'month' (for aggregating data points)

        Returns:
            {'data': [{'date': 'Jan 01', 'value': 12500}, ...], 'error': None}
        """
        self.ensure_one()

        if not self._check_user_access():
            return {'data': [], 'error': 'Access Denied'}

        try:
            from datetime import datetime, timedelta
            from dateutil.relativedelta import relativedelta

            today = fields.Date.context_today(self)
            date_field = self.date_field or 'create_date'

            # Determine date range based on period
            if period == 'today':
                start = today
                num_points = 1
                delta = timedelta(days=1)
            elif period == 'this_week':
                start = today - timedelta(days=today.weekday())
                num_points = (today - start).days + 1
                delta = timedelta(days=1)
            elif period == 'this_month':
                start = today.replace(day=1)
                num_points = (today - start).days + 1
                delta = timedelta(days=1)
            elif period == 'this_quarter':
                quarter = (today.month - 1) // 3
                start = today.replace(month=quarter * 3 + 1, day=1)
                if granularity == 'week':
                    num_points = ((today - start).days // 7) + 1
                    delta = timedelta(weeks=1)
                else:
                    num_points = (today - start).days + 1
                    delta = timedelta(days=1)
            elif period == 'this_year':
                start = today.replace(month=1, day=1)
                if granularity == 'month':
                    num_points = today.month
                    delta = relativedelta(months=1)
                elif granularity == 'week':
                    num_points = ((today - start).days // 7) + 1
                    delta = timedelta(weeks=1)
                else:
                    num_points = min((today - start).days + 1, 365)
                    delta = timedelta(days=1)
            elif period == 'last_30_days':
                start = today - timedelta(days=29)
                num_points = 30
                delta = timedelta(days=1)
            elif period == 'last_90_days':
                start = today - timedelta(days=89)
                if granularity == 'week':
                    num_points = 13
                    delta = timedelta(weeks=1)
                else:
                    num_points = 90
                    delta = timedelta(days=1)
            else:  # all_time - return monthly for last 12 months
                start = today - relativedelta(months=11)
                start = start.replace(day=1)
                num_points = 12
                delta = relativedelta(months=1)
                granularity = 'month'

            # Get model reference
            Model = self.env.get(self.source_model)
            if Model is None:
                return {'data': [], 'error': f'Model {self.source_model} not found'}

            # Build secure domain with full date range
            from odoo.tools.safe_eval import safe_eval
            from .ops_kpi_value import _get_safe_eval_context
            eval_context = _get_safe_eval_context(self.env)
            base_domain = safe_eval(self.domain_filter, eval_context) if self.domain_filter else []
            domain = self._get_secure_domain(base_domain.copy())
            domain.extend([
                (date_field, '>=', fields.Date.to_string(start)),
                (date_field, '<=', fields.Date.to_string(today)),
            ])

            # Map granularity to read_group groupby spec
            rg_granularity = granularity if granularity in ('day', 'week', 'month') else 'day'
            groupby_spec = f'{date_field}:{rg_granularity}'

            # Single _read_group call instead of N per-point queries
            value_map = {}
            count_map = {}

            if self.calculation_type in ('count', 'sum', 'average'):
                if self.calculation_type == 'count':
                    aggregates = ['__count']
                elif self.calculation_type == 'sum':
                    aggregates = [f'{self.measure_field}:sum']
                else:  # average — get sum + count, divide later
                    aggregates = [f'{self.measure_field}:sum', '__count']

                try:
                    grouped = Model._read_group(
                        domain, groupby=[groupby_spec], aggregates=aggregates,
                    )
                except Exception as e:
                    _logger.warning("_read_group failed for KPI %s: %s", self.code, e)
                    grouped = []

                for row in grouped:
                    # row is a tuple: (groupby_datetime, agg1, [agg2, ...])
                    group_dt = row[0]
                    if not group_dt:
                        continue
                    group_date = group_dt.date() if isinstance(group_dt, datetime) else group_dt

                    if self.calculation_type == 'count':
                        value_map[group_date] = row[1] or 0
                    elif self.calculation_type == 'sum':
                        value_map[group_date] = row[1] or 0
                    elif self.calculation_type == 'average':
                        value_map[group_date] = row[1] or 0  # sum
                        count_map[group_date] = row[2] or 0  # count

            # Generate complete series with zero-fill for gaps
            data = []
            current = start

            for i in range(num_points):
                # Normalize lookup key to match read_group bucket boundaries
                if rg_granularity == 'week':
                    lookup = current - timedelta(days=current.weekday())
                elif rg_granularity == 'month':
                    lookup = current.replace(day=1)
                else:
                    lookup = current

                value = value_map.get(lookup, 0)

                if self.calculation_type == 'average':
                    count = count_map.get(lookup, 0)
                    value = value / count if count > 0 else 0

                # Format date label
                if granularity == 'month':
                    date_label = current.strftime('%b')
                elif granularity == 'week':
                    date_label = f"W{current.isocalendar()[1]}"
                else:
                    date_label = current.strftime('%d')

                data.append({
                    'date': date_label,
                    'full_date': fields.Date.to_string(current),
                    'value': round(value, 2),
                })

                # Move to next period
                current = current + delta

                # Don't go beyond today
                if current > today:
                    break

            return {'data': data, 'error': None}

        except Exception as e:
            _logger.error("Error in get_time_series for KPI %s: %s", self.code, str(e))
            return {'data': [], 'error': str(e)}

    def get_breakdown(self, period='this_month', group_by='ops_branch_id'):
        """
        Get breakdown by dimension for bar/pie charts.
        Returns list of {name, value} for each group.

        Args:
            period: Time period to filter data
            group_by: Field to group by ('ops_branch_id', 'ops_business_unit_id', etc.)

        Returns:
            {'data': [{'name': 'Doha Branch', 'value': 45000, 'id': 1}, ...], 'error': None}
        """
        self.ensure_one()

        if not self._check_user_access():
            return {'data': [], 'error': 'Access Denied'}

        try:
            from datetime import timedelta

            today = fields.Date.context_today(self)
            date_field = self.date_field or 'create_date'

            # Get period dates
            period_start, period_end = self.env['ops.kpi.value']._get_period_dates(period)

            # Get model reference
            Model = self.env.get(self.source_model)
            if Model is None:
                return {'data': [], 'error': f'Model {self.source_model} not found'}

            # Check if group_by field exists
            if group_by not in Model._fields:
                return {'data': [], 'error': f'Field {group_by} not found in {self.source_model}'}

            # Build base domain
            from odoo.tools.safe_eval import safe_eval
            from .ops_kpi_value import _get_safe_eval_context
            eval_context = _get_safe_eval_context(self.env)
            base_domain = safe_eval(self.domain_filter, eval_context) if self.domain_filter else []
            domain = self._get_secure_domain(base_domain)

            # Add date filter
            if period_start and period_end and date_field:
                domain.extend([
                    (date_field, '>=', fields.Date.to_string(period_start)),
                    (date_field, '<=', fields.Date.to_string(period_end)),
                ])

            # Determine aggregation field
            if self.calculation_type == 'count':
                agg_field = 'id:count'
            elif self.calculation_type == 'sum' and self.measure_field:
                agg_field = f'{self.measure_field}:sum'
            elif self.calculation_type == 'average' and self.measure_field:
                agg_field = f'{self.measure_field}:avg'
            else:
                agg_field = 'id:count'

            # Use read_group for aggregation
            results = Model.read_group(
                domain=domain,
                fields=[group_by, agg_field],
                groupby=[group_by],
                orderby=f'{agg_field.split(":")[0]} desc' if ':' in agg_field else 'id desc',
            )

            data = []
            for result in results:
                group_value = result.get(group_by)
                if isinstance(group_value, tuple):
                    # Many2one field returns (id, name)
                    group_id = group_value[0]
                    group_name = group_value[1]
                else:
                    group_id = group_value
                    group_name = str(group_value) if group_value else 'Undefined'

                # Get the aggregated value
                if self.calculation_type == 'count':
                    value = result.get(f'{group_by}_count', 0)
                elif self.calculation_type in ('sum', 'average'):
                    value = result.get(self.measure_field, 0)
                else:
                    value = 0

                if group_name:  # Skip null groups
                    data.append({
                        'id': group_id,
                        'name': group_name,
                        'value': round(value, 2) if isinstance(value, float) else value,
                    })

            return {'data': data, 'error': None}

        except Exception as e:
            _logger.error("Error in get_breakdown for KPI %s: %s", self.code, str(e))
            return {'data': [], 'error': str(e)}

    def get_comparison(self, period='this_month'):
        """
        Get comparison with previous periods (MoM, YoY).
        Returns current value with last month and last year comparisons.

        Args:
            period: Time period for current value

        Returns:
            {
                'current': 12500,
                'last_month': 11200,
                'last_year': 10800,
                'mom_change': 11.6,
                'yoy_change': 15.7,
                'error': None
            }
        """
        self.ensure_one()

        if not self._check_user_access():
            return {'error': 'Access Denied'}

        try:
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta

            today = fields.Date.context_today(self)
            date_field = self.date_field or 'create_date'

            # Get current period dates
            period_start, period_end = self.env['ops.kpi.value']._get_period_dates(period)

            # Get model reference
            Model = self.env.get(self.source_model)
            if Model is None:
                return {'error': f'Model {self.source_model} not found'}

            # Build base domain
            from odoo.tools.safe_eval import safe_eval
            from .ops_kpi_value import _get_safe_eval_context
            eval_context = _get_safe_eval_context(self.env)
            base_domain = safe_eval(self.domain_filter, eval_context) if self.domain_filter else []

            def compute_value_for_period(start, end):
                """Helper to compute value for a specific period."""
                domain = self._get_secure_domain(base_domain.copy())
                if start and end and date_field:
                    domain.extend([
                        (date_field, '>=', fields.Date.to_string(start)),
                        (date_field, '<=', fields.Date.to_string(end)),
                    ])

                try:
                    if self.calculation_type == 'count':
                        return Model.search_count(domain)
                    elif self.calculation_type == 'sum':
                        records = Model.search(domain)
                        return sum(records.mapped(self.measure_field) or [0])
                    elif self.calculation_type == 'average':
                        records = Model.search(domain)
                        values = records.mapped(self.measure_field) or [0]
                        return sum(values) / len(values) if values else 0
                    else:
                        return 0
                except Exception as e:
                    _logger.warning("Error computing comparison value: %s", str(e))
                    return 0

            # Current period
            current = compute_value_for_period(period_start, period_end)

            # Last month (same day range, previous month)
            if period_start and period_end:
                lm_start = period_start - relativedelta(months=1)
                lm_end = period_end - relativedelta(months=1)
                last_month = compute_value_for_period(lm_start, lm_end)
            else:
                last_month = 0

            # Last year (same day range, previous year)
            if period_start and period_end:
                ly_start = period_start - relativedelta(years=1)
                ly_end = period_end - relativedelta(years=1)
                last_year = compute_value_for_period(ly_start, ly_end)
            else:
                last_year = 0

            # Calculate changes
            mom_change = 0
            if last_month and last_month != 0:
                mom_change = round(((current - last_month) / abs(last_month)) * 100, 1)

            yoy_change = 0
            if last_year and last_year != 0:
                yoy_change = round(((current - last_year) / abs(last_year)) * 100, 1)

            return {
                'current': round(current, 2) if isinstance(current, float) else current,
                'last_month': round(last_month, 2) if isinstance(last_month, float) else last_month,
                'last_year': round(last_year, 2) if isinstance(last_year, float) else last_year,
                'mom_change': mom_change,
                'yoy_change': yoy_change,
                'error': None,
            }

        except Exception as e:
            _logger.error("Error in get_comparison for KPI %s: %s", self.code, str(e))
            return {'error': str(e)}
