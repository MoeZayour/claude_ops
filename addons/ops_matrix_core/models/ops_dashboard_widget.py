# -*- coding: utf-8 -*-
"""OPS Dashboard Widget Model for defining reusable dashboard components."""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class OpsDashboardWidget(models.Model):
    """Model for dashboard widgets."""
    
    _name = 'ops.dashboard.widget'
    _description = 'OPS Dashboard Widget'
    _order = 'sequence, name'
    
    # Basic Information
    name = fields.Char(
        string='Widget Name',
        required=True,
        translate=True
    )
    
    code = fields.Char(
        string='Widget Code',
        required=True,
        copy=False,
        help='Unique code for this widget'
    )
    
    description = fields.Text(
        string='Description',
        translate=True
    )
    
    # Technical Configuration
    widget_type = fields.Selection([
        ('kpi', 'KPI Card'),
        ('chart', 'Chart'),
        ('table', 'Data Table'),
        ('pivot', 'Pivot Table'),
        ('graph', 'Graph'),
        ('gauge', 'Gauge'),
        ('progress', 'Progress Bar'),
    ], string='Widget Type', required=True)
    
    model_name = fields.Char(
        string='Model',
        required=True,
        help='Technical name of the Odoo model (e.g., sale.order)'
    )
    
    domain = fields.Char(
        string='Domain',
        help='Domain filter for widget data (Python expression)'
    )
    
    # Display Configuration
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order in dashboard'
    )
    
    icon = fields.Char(
        string='Icon',
        help='FontAwesome icon class (e.g., fa-chart-line)'
    )
    
    color = fields.Char(
        string='Color',
        default='#1f77b4',
        help='Widget color (hex code)'
    )
    
    height = fields.Integer(
        string='Height (px)',
        default=300,
        help='Widget height in pixels'
    )
    
    width = fields.Selection([
        ('small', 'Small (1 column)'),
        ('medium', 'Medium (2 columns)'),
        ('large', 'Large (3 columns)'),
        ('full', 'Full width'),
    ], string='Width', default='medium')
    
    # Data Configuration
    measure_field = fields.Char(
        string='Measure Field',
        help='Field to measure (e.g., amount_total)'
    )
    
    dimension_field = fields.Char(
        string='Dimension Field',
        help='Field to group by (e.g., partner_id)'
    )
    
    group_by_fields = fields.Char(
        string='Group By Fields',
        help='Comma-separated list of fields to group by'
    )
    
    sort_by = fields.Char(
        string='Sort By',
        help='Field to sort results by'
    )
    
    limit = fields.Integer(
        string='Record Limit',
        default=10,
        help='Maximum number of records to display'
    )
    
    # Security
    group_ids = fields.Many2many(
        'res.groups',
        string='Allowed Groups',
        help='User groups that can see this widget'
    )
    
    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
        help='Companies where this widget is available'
    )
    
    # Status
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    is_system = fields.Boolean(
        string='System Widget',
        default=False,
        help='System widgets cannot be deleted'
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Widget code must be unique!'),
    ]
    
    # Methods
    @api.constrains('domain')
    def _check_domain(self):
        """Validate domain expression."""
        for widget in self:
            if widget.domain:
                try:
                    # Try to evaluate the domain to check syntax
                    eval(widget.domain)
                except Exception as e:
                    raise ValidationError(
                        _('Invalid domain expression: %s') % str(e)
                    )
    
    def get_widget_data(self, user_id=None, context=None):
        """Get data for this widget."""
        self.ensure_one()
        
        user = self.env['res.users'].browse(user_id) if user_id else self.env.user
        ctx = context or {}
        
        # Apply security filters
        domain = self._get_security_domain(user)
        if self.domain:
            domain += eval(self.domain)
        
        # Get data based on widget type
        data = {}
        if self.widget_type == 'kpi':
            data = self._get_kpi_data(domain, user, ctx)
        elif self.widget_type == 'chart':
            data = self._get_chart_data(domain, user, ctx)
        elif self.widget_type == 'table':
            data = self._get_table_data(domain, user, ctx)
        elif self.widget_type == 'pivot':
            data = self._get_pivot_data(domain, user, ctx)
        
        return data
    
    def _get_security_domain(self, user):
        """Get security domain based on user's matrix access."""
        domain = []
        
        if not self.model_name:
            return domain
            
        Model = self.env[self.model_name]
        
        # Company restriction
        if hasattr(Model, 'company_id') and user.company_ids:
            domain.append(('company_id', 'in', user.company_ids.ids))
        
        # Branch restriction (if model has ops_branch_id)
        if hasattr(Model, 'ops_branch_id'):
            if user.allowed_branch_ids:
                domain.append(('ops_branch_id', 'in', user.allowed_branch_ids.ids))
        
        # BU restriction (if model has ops_business_unit_id)
        if hasattr(Model, 'ops_business_unit_id'):
            if user.allowed_business_unit_ids:
                domain.append(('ops_business_unit_id', 'in', user.allowed_business_unit_ids.ids))
        
        return domain
    
    def _get_kpi_data(self, domain, user, context):
        """Get KPI data for widget."""
        if not self.measure_field:
            return {'value': 0, 'label': self.name}
        
        Model = self.env[self.model_name]
        records = Model.search(domain)
        
        # Calculate aggregate
        value = sum(records.mapped(self.measure_field))
        
        return {
            'value': value,
            'label': self.name,
            'icon': self.icon,
            'color': self.color,
        }
    
    def _get_chart_data(self, domain, user, context):
        """Get chart data for widget."""
        if not self.dimension_field or not self.measure_field:
            return {'labels': [], 'values': []}
        
        Model = self.env[self.model_name]
        
        # Use read_group for aggregation
        group_by = self.dimension_field
        data = Model.read_group(
            domain,
            [self.measure_field],
            [group_by],
            limit=self.limit,
            orderby=self.sort_by or f'{self.measure_field} desc'
        )
        
        labels = []
        values = []
        
        for item in data:
            label = item.get(group_by, 'Unknown')
            if isinstance(label, tuple):
                label = label[1]  # Get display name from tuple
            labels.append(str(label))
            values.append(item.get(self.measure_field, 0))
        
        return {
            'labels': labels,
            'values': values,
            'color': self.color,
        }
    
    def _get_table_data(self, domain, user, context):
        """Get table data for widget."""
        Model = self.env[self.model_name]
        
        fields = []
        if self.group_by_fields:
            fields = [f.strip() for f in self.group_by_fields.split(',')]
        if self.measure_field and self.measure_field not in fields:
            fields.append(self.measure_field)
        
        records = Model.search(domain, limit=self.limit, order=self.sort_by or 'id desc')
        
        data = []
        for record in records:
            row = {}
            for field in fields:
                value = record[field]
                if isinstance(value, models.Model):
                    value = value.display_name
                row[field] = value
            data.append(row)
        
        return {
            'headers': fields,
            'rows': data,
        }
    
    def _get_pivot_data(self, domain, user, context):
        """Get pivot data for widget."""
        # Similar to chart data but structured for pivot display
        return self._get_chart_data(domain, user, context)
    
    @api.ondelete(at_uninstall=False)
    def _unlink_except_system(self):
        """Prevent deletion of system widgets."""
        if any(widget.is_system for widget in self):
            raise UserError(
                _('System widgets cannot be deleted.')
            )
