# OPS Dashboard - Model Code Reference

This document contains the complete code for all OPS Dashboard models.

---

## 1. ops_kpi.py

```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsKpi(models.Model):
    """
    KPI Definition - Defines what metrics can be displayed.
    Security-aware: respects OPS Matrix access controls.
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
    
    # Categorization
    category = fields.Selection([
        ('sales', 'Sales'),
        ('purchase', 'Purchase'),
        ('inventory', 'Inventory'),
        ('finance', 'Finance'),
        ('receivable', 'Accounts Receivable'),
        ('payable', 'Accounts Payable'),
        ('pdc', 'PDC Management'),
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
    
    # Persona Targeting
    persona_ids = fields.Many2many('ops.persona', string='Target Personas',
                                   help='Which personas should see this KPI')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'KPI code must be unique!'),
    ]
    
    @api.constrains('source_model')
    def _check_source_model(self):
        """Validate source model exists."""
        for kpi in self:
            if kpi.source_model:
                if kpi.source_model not in self.env:
                    raise ValidationError(
                        _("Model '%s' does not exist.") % kpi.source_model
                    )
    
    def _get_secure_domain(self, base_domain=None):
        """
        Build security-compliant domain for queries.
        CRITICAL: This method enforces OPS Matrix security.
        """
        user = self.env.user
        domain = list(base_domain or [])
        
        # IT Admin Blindness - they see NOTHING
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            if not self.visible_to_it_admin:
                return [('id', '=', 0)]  # Return empty result
        
        # Branch Isolation (unless manager/exec with bypass)
        if not user.has_group('ops_matrix_core.group_ops_manager'):
            branch_ids = user.ops_allowed_branch_ids.ids if hasattr(user, 'ops_allowed_branch_ids') else []
            if branch_ids:
                # Check if model has ops_branch_id field
                model = self.env.get(self.source_model)
                if model and 'ops_branch_id' in model._fields:
                    domain.append(('ops_branch_id', 'in', branch_ids))
        
        # Company Filter
        domain.append(('company_id', 'in', self.env.companies.ids))
        
        return domain
    
    def _check_user_access(self):
        """Check if current user can view this KPI."""
        user = self.env.user
        
        # IT Admin check
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
        
        return True
```

---

## 2. ops_kpi_value.py

```python
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


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
        
        # Build secure domain
        base_domain = safe_eval(kpi.domain_filter) if kpi.domain_filter else []
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
```

---

## 3. ops_dashboard.py

```python
from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class OpsDashboard(models.Model):
    """
    Dashboard Definition - Container for widgets/KPIs.
    Each dashboard targets specific personas.
    """
    _name = 'ops.dashboard'
    _description = 'OPS Dashboard'
    _inherit = ['mail.thread']
    _order = 'sequence, name'
    
    name = fields.Char(string='Dashboard Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, index=True,
                       help='Unique identifier: EXEC, BRANCH, SALES')
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # Targeting
    dashboard_type = fields.Selection([
        ('executive', 'Executive Dashboard'),
        ('branch', 'Branch Dashboard'),
        ('bu', 'Business Unit Dashboard'),
        ('sales', 'Sales Dashboard'),
        ('purchase', 'Purchase Dashboard'),
        ('finance', 'Finance Dashboard'),
        ('inventory', 'Inventory Dashboard'),
        ('custom', 'Custom Dashboard'),
    ], string='Type', required=True, default='custom')
    
    # Persona Access
    persona_ids = fields.Many2many('ops.persona', string='Target Personas',
                                   help='Which personas can view this dashboard')
    group_ids = fields.Many2many('res.groups', string='Access Groups',
                                 help='Additional groups that can view this dashboard')
    
    # Widgets
    widget_ids = fields.One2many('ops.dashboard.widget', 'dashboard_id', string='Widgets')
    widget_count = fields.Integer(compute='_compute_widget_count')
    
    # Display Settings
    auto_refresh = fields.Boolean(string='Auto Refresh', default=True)
    refresh_interval = fields.Selection([
        ('30000', '30 Seconds'),
        ('60000', '1 Minute'),
        ('120000', '2 Minutes'),
        ('300000', '5 Minutes'),
        ('600000', '10 Minutes'),
        ('0', 'Manual Only'),
    ], string='Refresh Interval', default='120000')
    
    columns = fields.Integer(string='Grid Columns', default=4,
                            help='Number of columns in the grid layout')
    
    # Company
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 
         'Dashboard code must be unique per company!'),
    ]
    
    @api.depends('widget_ids')
    def _compute_widget_count(self):
        for dashboard in self:
            dashboard.widget_count = len(dashboard.widget_ids)
    
    def _check_access(self):
        """Check if current user can access this dashboard."""
        user = self.env.user
        self.ensure_one()
        
        # System admin always has access
        if user.has_group('base.group_system'):
            return True
        
        # Check group access
        if self.group_ids:
            user_groups = user.groups_id
            if self.group_ids & user_groups:
                return True
        
        # Check persona access
        if self.persona_ids and hasattr(user, 'ops_persona_id'):
            if user.ops_persona_id in self.persona_ids:
                return True
        
        # Default: allow if no restrictions set
        if not self.group_ids and not self.persona_ids:
            return True
        
        return False
    
    @api.model
    def get_user_dashboards(self):
        """Get dashboards accessible to current user."""
        user = self.env.user
        
        # IT Admin gets no business dashboards
        if user.has_group('ops_matrix_core.group_ops_it_admin'):
            return []  # Return empty list for JSON serialization
        
        dashboards = self.search([('active', '=', True)])
        accessible = dashboards.filtered(lambda d: d._check_access())
        return accessible.read(['id', 'name', 'code', 'dashboard_type'])
    
    @api.model
    def get_dashboard_data(self, dashboard_id, period=None):
        """
        Main RPC method to fetch dashboard data.
        Returns all widget data for the dashboard.
        """
        dashboard = self.browse(dashboard_id)
        
        if not dashboard.exists():
            return {'error': 'Dashboard not found'}
        
        if not dashboard._check_access():
            return {'error': 'Access Denied'}
        
        # Collect widget data
        widgets_data = []
        for widget in dashboard.widget_ids.sorted('sequence'):
            widget_data = widget.get_widget_data(period=period)
            if widget_data and not widget_data.get('error'):
                widgets_data.append(widget_data)
        
        return {
            'dashboard_id': dashboard.id,
            'dashboard_name': dashboard.name,
            'dashboard_type': dashboard.dashboard_type,
            'refresh_interval': int(dashboard.refresh_interval or 0),
            'columns': dashboard.columns,
            'widgets': widgets_data,
        }
```

---

## 4. ops_dashboard_widget.py

```python
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OpsDashboardWidget(models.Model):
    """
    Dashboard Widget - Individual component on a dashboard.
    Can display KPIs, charts, lists, etc.
    """
    _name = 'ops.dashboard.widget'
    _description = 'Dashboard Widget'
    _order = 'sequence, id'
    
    name = fields.Char(string='Widget Name', required=True)
    dashboard_id = fields.Many2one('ops.dashboard', string='Dashboard',
                                   required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    
    # Widget Type
    widget_type = fields.Selection([
        ('kpi', 'KPI Card'),
        ('kpi_group', 'KPI Group'),
        ('bar_chart', 'Bar Chart'),
        ('line_chart', 'Line Chart'),
        ('pie_chart', 'Pie Chart'),
        ('list', 'Top N List'),
        ('metric', 'Single Metric'),
    ], string='Type', required=True, default='kpi')
    
    # KPI Reference
    kpi_id = fields.Many2one('ops.kpi', string='KPI',
                             help='KPI definition for this widget')
    kpi_ids = fields.Many2many('ops.kpi', string='KPIs',
                               help='Multiple KPIs for group widget')
    
    # Display Configuration
    title = fields.Char(string='Display Title',
                        help='Override KPI name for display')
    subtitle = fields.Char(string='Subtitle')
    icon = fields.Char(string='Icon Override',
                       help='Override KPI icon')
    color = fields.Char(string='Color Override',
                        help='Override KPI color')
    
    # Grid Position
    position_x = fields.Integer(string='Column', default=0)
    position_y = fields.Integer(string='Row', default=0)
    width = fields.Integer(string='Width (columns)', default=1)
    height = fields.Integer(string='Height (rows)', default=1)
    
    # Period Override
    period_override = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('last_30_days', 'Last 30 Days'),
        ('last_90_days', 'Last 90 Days'),
        ('all_time', 'All Time'),
    ], string='Period Override')
    
    # For List widgets
    list_limit = fields.Integer(string='List Limit', default=5)
    list_model = fields.Char(string='List Model')
    list_fields = fields.Char(string='Display Fields',
                              help='Comma-separated field names')
    list_domain = fields.Char(string='List Domain', default='[]')
    list_order = fields.Char(string='Sort Order', default='id desc')
    
    def get_widget_data(self, period=None):
        """
        Get data for this widget.
        Returns formatted data ready for frontend display.
        """
        self.ensure_one()
        
        # Check access through KPI
        if self.kpi_id and not self.kpi_id._check_user_access():
            return None  # Skip this widget
        
        # Determine period
        widget_period = period or self.period_override or (
            self.kpi_id.default_period if self.kpi_id else 'this_month'
        )
        
        result = {
            'widget_id': self.id,
            'widget_type': self.widget_type,
            'name': self.title or (self.kpi_id.name if self.kpi_id else self.name),
            'subtitle': self.subtitle,
            'icon': self.icon or (self.kpi_id.icon if self.kpi_id else 'fa-chart-bar'),
            'color': self.color or (self.kpi_id.color if self.kpi_id else '#3b82f6'),
            'position': {
                'x': self.position_x,
                'y': self.position_y,
                'w': self.width,
                'h': self.height,
            },
        }
        
        if self.widget_type == 'kpi' and self.kpi_id:
            # Single KPI
            kpi_data = self.env['ops.kpi.value'].compute_kpi_value(
                self.kpi_id, period=widget_period
            )
            result.update(kpi_data)
            
        elif self.widget_type == 'kpi_group' and self.kpi_ids:
            # Multiple KPIs
            kpis_data = []
            for kpi in self.kpi_ids:
                if kpi._check_user_access():
                    kpi_data = self.env['ops.kpi.value'].compute_kpi_value(
                        kpi, period=widget_period
                    )
                    if not kpi_data.get('error'):
                        kpis_data.append(kpi_data)
            result['kpis'] = kpis_data
            
        elif self.widget_type == 'list':
            # Top N List
            result['list_data'] = self._get_list_data()
            
        elif self.widget_type in ('bar_chart', 'line_chart', 'pie_chart'):
            # Chart data - placeholder for now
            result['chart_data'] = {'labels': [], 'values': []}
        
        return result
    
    def _get_list_data(self):
        """Get data for list widget."""
        if not self.list_model or self.list_model not in self.env:
            return []
        
        Model = self.env[self.list_model]
        
        from odoo.tools.safe_eval import safe_eval
        base_domain = safe_eval(self.list_domain) if self.list_domain else []
        
        # Apply branch isolation if model has ops_branch_id
        user = self.env.user
        if 'ops_branch_id' in Model._fields:
            if not user.has_group('ops_matrix_core.group_ops_manager'):
                branch_ids = user.ops_allowed_branch_ids.ids if hasattr(user, 'ops_allowed_branch_ids') else []
                if branch_ids:
                    base_domain.append(('ops_branch_id', 'in', branch_ids))
        
        # Company filter
        if 'company_id' in Model._fields:
            base_domain.append(('company_id', 'in', self.env.companies.ids))
        
        records = Model.search(
            base_domain,
            limit=self.list_limit or 5,
            order=self.list_order or 'id desc'
        )
        
        display_fields = (self.list_fields or 'name').split(',')
        result = []
        for rec in records:
            row = {'id': rec.id}
            for field in display_fields:
                field = field.strip()
                if hasattr(rec, field):
                    val = getattr(rec, field)
                    if hasattr(val, 'name'):
                        val = val.name
                    elif hasattr(val, 'display_name'):
                        val = val.display_name
                    row[field] = val
            result.append(row)
        
        return result
```

---

**Document Complete**
