from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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
    persona_codes = fields.Char(
        string='Persona Codes',
        help='Comma-separated persona codes: P01,P02,P03. Alternative to persona_ids.'
    )

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
        if not model:
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

        # Persona codes check (if specified)
        if self.persona_codes:
            allowed_codes = [p.strip() for p in self.persona_codes.split(',') if p.strip()]
            user_personas = []
            if hasattr(user, 'ops_persona_ids'):
                user_personas = user.ops_persona_ids.mapped('code')
            if allowed_codes and not any(p in allowed_codes for p in user_personas):
                return False

        return True

    def compute_value(self, period=None):
        """
        Compute KPI value for current user with security.
        Wrapper for ops.kpi.value.compute_kpi_value().
        """
        self.ensure_one()
        return self.env['ops.kpi.value'].compute_kpi_value(self, period=period)
