from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class OpsBudget(models.Model):
    _name = 'ops.budget'
    _description = 'Matrix Budget Control'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc, id desc'

    name = fields.Char(string='Budget Name', required=True, tracking=True)
    active = fields.Boolean(default=True)
    
    # Matrix Dimensions (Required)
    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        required=True,
        tracking=True,
        help="Branch this budget applies to"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='ops_branch_id.company_id',
        store=True,
        readonly=True
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        required=True,
        tracking=True,
        help="Business unit this budget applies to"
    )
    
    # Date Range
    date_from = fields.Date(string='Start Date', required=True, tracking=True)
    date_to = fields.Date(string='End Date', required=True, tracking=True)
    
    # Budget Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Budget Lines
    line_ids = fields.One2many('ops.budget.line', 'budget_id', string='Budget Lines')
    
    # Totals
    total_planned = fields.Monetary(
        string='Total Planned',
        compute='_compute_totals',
        store=True
    )
    total_practical = fields.Monetary(
        string='Total Actual',
        compute='_compute_totals',
        store=True
    )
    total_committed = fields.Monetary(
        string='Total Committed',
        compute='_compute_totals',
        store=True
    )
    available_balance = fields.Monetary(
        string='Available Balance',
        compute='_compute_totals',
        store=True
    )
    variance = fields.Monetary(
        string='Variance',
        compute='_compute_totals',
        store=True,
        help='Alias for available balance to display variance in list views.'
    )
    budget_utilization = fields.Float(
        string='Budget Utilization',
        compute='_compute_totals',
        store=True,
        help='Ratio of actual + committed spend over planned amount (0-1+).'
    )
    is_over_budget = fields.Boolean(
        string='Over Budget',
        compute='_compute_totals',
        store=True,
        help='Indicates spending has exceeded the planned budget.'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    _sql_constraints = [
        ('unique_matrix_budget', 'unique(ops_branch_id, ops_business_unit_id, date_from, date_to)',
         'A budget already exists for this Branch/Business Unit combination in the specified date range!')
    ]

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for budget in self:
            if budget.date_to < budget.date_from:
                raise ValidationError('End Date must be after Start Date')

            # Check for overlapping date ranges
            overlapping = self.search([
                ('id', '!=', budget.id),
                ('ops_branch_id', '=', budget.ops_branch_id.id),
                ('ops_business_unit_id', '=', budget.ops_business_unit_id.id),
                ('date_from', '<=', budget.date_to),
                ('date_to', '>=', budget.date_from)
            ])
            if overlapping:
                raise ValidationError(
                    'Budget dates overlap with existing budget(s) for the same Branch/Business Unit!'
                )

    @api.depends('line_ids.planned_amount', 'line_ids.practical_amount', 'line_ids.committed_amount')
    def _compute_totals(self):
        for budget in self:
            budget.total_planned = sum(budget.line_ids.mapped('planned_amount'))
            budget.total_practical = sum(budget.line_ids.mapped('practical_amount'))
            budget.total_committed = sum(budget.line_ids.mapped('committed_amount'))
            budget.available_balance = budget.total_planned - budget.total_practical - budget.total_committed
            budget.variance = budget.available_balance
            if budget.total_planned:
                budget.budget_utilization = (budget.total_practical + budget.total_committed) / budget.total_planned
            else:
                budget.budget_utilization = 0.0
            budget.is_over_budget = budget.available_balance < 0

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def check_budget_availability(self, branch_id=None, business_unit_id=None, amount=0.0,
                                   date=None, account_id=None, ops_branch_id=None,
                                   ops_business_unit_id=None):
        """Check if sufficient budget is available for a planned expense.

        Args:
            branch_id: The branch requesting the expense (preferred)
            business_unit_id: The business unit requesting the expense (preferred)
            amount: The amount to check
            date: Date to check budget for (defaults to today)
            account_id: Optional - specific expense account to check
            ops_branch_id: Legacy param - alias for branch_id
            ops_business_unit_id: Legacy param - alias for business_unit_id

        Returns:
            dict: {
                'available': bool - whether budget is available,
                'remaining': float - remaining budget amount,
                'over_amount': float - amount over budget (if any),
                'budget_id': int - ID of the applicable budget,
                'budget_name': str - name of the applicable budget,
                'message': str - human-readable message
            }
        """
        # Handle legacy parameter names
        branch_id = branch_id or ops_branch_id
        business_unit_id = business_unit_id or ops_business_unit_id
        check_date = date or fields.Date.today()

        result = {
            'available': True,
            'remaining': 0.0,
            'over_amount': 0.0,
            'budget_id': False,
            'budget_name': '',
            'message': ''
        }

        if not branch_id or not business_unit_id:
            result['message'] = 'No branch or business unit specified'
            return result

        domain = [
            ('state', '=', 'confirmed'),
            ('ops_branch_id', '=', branch_id),
            ('ops_business_unit_id', '=', business_unit_id),
            ('date_from', '<=', check_date),
            ('date_to', '>=', check_date)
        ]

        active_budget = self.search(domain, limit=1)
        if not active_budget:
            result['message'] = 'No active budget found for this period'
            return result

        result['budget_id'] = active_budget.id
        result['budget_name'] = active_budget.name

        # If specific account requested, check that line
        if account_id:
            budget_line = active_budget.line_ids.filtered(
                lambda l: l.general_account_id.id == account_id
            )
            if not budget_line:
                result['message'] = 'No budget line for specified account'
                return result
            available = budget_line.available_amount
        else:
            # Check overall budget
            available = active_budget.available_balance

        result['remaining'] = available

        if available < amount:
            result['available'] = False
            result['over_amount'] = amount - available
            result['message'] = f'Budget exceeded by {result["over_amount"]:.2f}'
        else:
            result['message'] = f'Budget available: {available:.2f} remaining'

        return result


class OpsBudgetLine(models.Model):
    _name = 'ops.budget.line'
    _description = 'Matrix Budget Line'
    _order = 'general_account_id'

    budget_id = fields.Many2one('ops.budget', string='Budget', required=True, ondelete='cascade')
    general_account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
        required=True,
        domain=[('account_type', '=', 'expense')]
    )
    
    planned_amount = fields.Monetary(string='Planned Amount', required=True)
    practical_amount = fields.Monetary(string='Actual Amount', compute='_compute_practical_amount', store=True)
    committed_amount = fields.Monetary(string='Committed Amount', compute='_compute_committed_amount', store=True)
    available_amount = fields.Monetary(string='Available Amount', compute='_compute_available_amount', store=True)
    
    currency_id = fields.Many2one(related='budget_id.currency_id')
    company_id = fields.Many2one('res.company', related='budget_id.company_id', store=True, readonly=True)

    _sql_constraints = [
        ('unique_account_per_budget', 'unique(budget_id, general_account_id)',
         'You can only have one budget line per account!')
    ]

    @api.depends('planned_amount', 'practical_amount', 'committed_amount')
    def _compute_available_amount(self):
        for line in self:
            line.available_amount = line.planned_amount - line.practical_amount - line.committed_amount

    @api.depends('general_account_id', 'budget_id.date_from', 'budget_id.date_to',
                 'budget_id.ops_branch_id', 'budget_id.ops_business_unit_id')
    def _compute_practical_amount(self):
        """Compute actual spend from posted account moves using ORM (H-1 audit fix).

        Practical = Sum of debit - credit from posted vendor bills/refunds/entries
        matching the budget's branch, BU, account, and date range.
        """
        AML = self.env['account.move.line'].sudo()

        budget_lines = {}
        for line in self:
            if not line.general_account_id or not line.budget_id or not line.budget_id.ops_branch_id:
                line.practical_amount = 0.0
                continue
            budget_lines.setdefault(line.budget_id.id, []).append(line)

        for _budget_id, lines in budget_lines.items():
            budget = lines[0].budget_id
            account_ids = [l.general_account_id.id for l in lines]

            domain = [
                ('account_id', 'in', account_ids),
                ('move_id.state', '=', 'posted'),
                ('move_id.move_type', 'in', ('in_invoice', 'in_refund', 'entry')),
                ('date', '>=', budget.date_from),
                ('date', '<=', budget.date_to),
                ('company_id', '=', budget.company_id.id),
            ]
            if budget.ops_branch_id:
                domain.append(('ops_branch_id', '=', budget.ops_branch_id.id))
            if budget.ops_business_unit_id:
                domain.append(('ops_business_unit_id', '=', budget.ops_business_unit_id.id))

            try:
                move_lines = AML.search(domain)
                results = {}
                for aml in move_lines:
                    acc_id = aml.account_id.id
                    results[acc_id] = results.get(acc_id, 0.0) + (aml.debit - aml.credit)
            except Exception as e:
                _logger.error("Budget practical amount calculation error: %s", e)
                results = {}

            for line in lines:
                line.practical_amount = results.get(line.general_account_id.id, 0.0)

    @api.depends('general_account_id', 'budget_id.date_from', 'budget_id.date_to',
                 'budget_id.ops_branch_id', 'budget_id.ops_business_unit_id')
    def _compute_committed_amount(self):
        """
        Compute committed amount from purchase orders using batched SQL.

        Committed = PO lines (confirmed/done) not yet fully invoiced, matching:
        - Same branch as budget
        - Date within budget period
        - Product expense account matches budget line account

        Formula: price_subtotal - (qty_invoiced * price_unit) gives the uninvoiced portion.

        Lines are grouped by their parent budget to minimise SQL round-trips.
        """
        # Partition lines by budget for batch processing
        budget_lines = {}
        for line in self:
            if not line.general_account_id or not line.budget_id or not line.budget_id.ops_branch_id:
                line.committed_amount = 0.0
                continue
            budget_lines.setdefault(line.budget_id.id, []).append(line)

        POL = self.env['purchase.order.line']

        for budget_id, lines in budget_lines.items():
            budget = lines[0].budget_id
            account_ids = [l.general_account_id.id for l in lines]

            # Use ORM search instead of raw SQL to avoid JSONB
            # comparison issues with company-dependent fields in Odoo 19
            try:
                po_lines = POL.search([
                    ('order_id.state', 'in', ['purchase', 'done']),
                    ('order_id.ops_business_unit_id', '=', budget.ops_business_unit_id.id),
                    ('order_id.ops_branch_id', '=', budget.ops_branch_id.id),
                    ('order_id.date_order', '>=', budget.date_from),
                    ('order_id.date_order', '<=', budget.date_to),
                    ('order_id.company_id', '=', budget.company_id.id),
                ])

                # Build committed amounts by expense account
                results = {}
                for pol in po_lines:
                    account = pol.product_id.categ_id.property_account_expense_categ_id
                    if account and account.id in account_ids:
                        uninvoiced = pol.price_subtotal - (pol.qty_invoiced * pol.price_unit)
                        results[account.id] = results.get(account.id, 0.0) + uninvoiced
            except Exception as e:
                _logger.error("Budget committed amount calculation error: %s", e)
                results = {}

            for line in lines:
                line.committed_amount = results.get(line.general_account_id.id, 0.0)
