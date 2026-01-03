# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)

TRIGGER_TYPES = [
    ('on_create', 'On Create'),
    ('on_write', 'On Write'),
    ('on_unlink', 'On Delete'),
]

ACTION_TYPES = [
    ('warning', 'Warning'),
    ('block', 'Block'),
    ('require_approval', 'Require Approval'),
]


class OpsGovernanceRule(models.Model):
    _name = 'ops.governance.rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'OPS Governance Rule - Dynamic Rule Engine with Matrix & Pricing Controls'
    _order = 'sequence, name'

    # --- CORE FIELDS ---
    name = fields.Char(
        string='Rule Name',
        required=True,
        tracking=True,
        help='Descriptive name for this governance rule. '
             'Use clear, action-oriented names that explain what the rule enforces. '
             'Examples: "Sales Order Discount Limit", "Margin Protection - Electronics", '
             '"Branch Selection Required", "High-Value Purchase Approval". '
             'Best Practice: Include the rule type and scope in the name for easy identification. '
             'This name appears in: approval requests, violation logs, compliance reports.'
    )
    code = fields.Char(string='Rule Code', required=True, copy=False, readonly=True,
                      default=lambda self: self.env['ir.sequence'].next_by_code('ops.governance.rule') or 'New')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in which rules are evaluated. Lower numbers = higher priority (evaluated first). '
             'Default is 10. Important: Rule evaluation stops at first blocking rule. '
             'Use Cases: '
             '- Critical validations (branch selection): sequence = 1 '
             '- Discount limits: sequence = 5 '
             '- Margin protection: sequence = 10 '
             '- Notifications: sequence = 20. '
             'Tip: Use increments of 5 to allow inserting rules between existing ones.'
    )
    description = fields.Text(string='Description', compute='_compute_description', store=True)
    
    # --- SCOPE & TARGETING ---
    model_id = fields.Many2one(
        'ir.model',
        string='Applies To Model',
        required=True,
        ondelete='cascade',
        help='The Odoo model (object type) this rule applies to. Required. '
             'Common models: '
             '- sale.order (Sales Orders) '
             '- sale.order.line (Sales Order Lines) '
             '- purchase.order (Purchase Orders) '
             '- account.move (Invoices/Bills) '
             '- stock.picking (Transfers). '
             'Scope: Rule only evaluates records of this model type. '
             'Example: Discount rule on "sale.order.line" validates each line item discount.'
    )
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                default=lambda self: self.env.company)
    
    rule_type = fields.Selection([
        ('matrix_validation', 'Matrix Validation'),
        ('discount_limit', 'Discount Limit'),
        ('margin_protection', 'Margin Protection'),
        ('price_override', 'Price Override'),
        ('approval_workflow', 'Approval Workflow'),
        ('notification', 'Notification'),
        ('approval', 'Approval (Legacy Template)'),
        ('legacy', 'Legacy (Backward Compatibility)'),
    ], string='Rule Type',
       required=True,
       tracking=True,
       default='legacy',
       help='Category of governance control this rule enforces. '
            'Matrix Validation: Ensures branch/BU are selected and valid. '
            'Discount Limit: Controls maximum discounts by role/category. '
            'Margin Protection: Enforces minimum profit margins. '
            'Price Override: Limits price changes from list price. '
            'Approval Workflow: Routes transactions for approval. '
            'Notification: Sends alerts without blocking. '
            'Legacy: Custom rules using domain/code conditions. '
            'Each type has specific configuration fields that appear when selected.')
    
    # New unified trigger field
    trigger_event = fields.Selection([
        ('always', 'Always'),
        ('on_create', 'On Create'),
        ('on_write', 'On Write'),
        ('on_state_change', 'On State Change'),
    ], string='Trigger Event',
       default='always',
       tracking=True,
       help='When this rule should be evaluated. '
            'Always: Checks on every create and update operation. '
            'On Create: Only when record is first created. '
            'On Write: Only when record is modified (not on creation). '
            'On State Change: Only when status field changes (draft→confirmed). '
            'Performance Tip: Use specific triggers instead of "Always" for better performance. '
            'Example: Discount validation on "On Write" since discounts can change after creation.')

    # Generic threshold/comparison helpers for template data (backward compatibility)
    threshold_value = fields.Float(
        string='Threshold Value',
        help='Generic numeric threshold used by template rules (e.g., discount % or amount). '
             'Kept for backward compatibility with seeded templates.'
    )
    comparison_operator = fields.Selection([
        ('greater_than', 'Greater Than'),
        ('greater_or_equal', 'Greater Than or Equal'),
        ('less_than', 'Less Than'),
        ('less_or_equal', 'Less Than or Equal'),
        ('equal', 'Equal To'),
        ('not_equal', 'Not Equal To'),
    ], string='Comparison Operator', default='greater_than',
       help='Comparison operator used with threshold_value for legacy/template rules.')
    
    # New unified condition logic field - Changed to Char for domain widget
    condition_logic = fields.Char(
        string='Condition Logic',
        help='Optional filter to limit when this rule applies. Use the visual domain builder. '
             'Click "Add a filter" to build conditions without coding. '
             'Examples: '
             '- Apply only to orders > $10,000: [("amount_total", ">", 10000)] '
             '- Apply only to specific partner: [("partner_id", "=", 123)] '
             '- Apply to confirmed orders: [("state", "=", "sale")]. '
             'Leave empty to apply to all records of the selected model. '
             'Advanced: Supports Python domain syntax for complex conditions.'
    )
    
    # Computed field for domain widget anchor
    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        store=True,
        readonly=True,
        help='Technical model name for domain widget'
    )
    
    # Legacy fields for backward compatibility
    trigger_condition = fields.Selection([
        ('always', 'Always'),
        ('on_create', 'On Create'),
        ('on_update', 'On Update'),
        ('on_state_change', 'On State Change'),
        # Legacy template placeholders for seeded rules
        ('discount_percent', 'Discount Percent (Template)'),
        ('amount_total', 'Amount Total (Template)'),
    ], string='Trigger Condition (Legacy)', default='always')
    
    state_condition = fields.Char(string='State Condition',
                                 help='Python expression for state evaluation. Example: state in ["draft", "sent"]')
    
    # --- MATRIX DIMENSION VALIDATION ---
    enforce_branch_bu = fields.Boolean(
        string='Enforce Branch/BU Selection',
        help='When enabled, validates that Branch and Business Unit are properly selected on transactions. '
             'Checks performed: '
             '- Branch field is filled (if "Branch Required" checked) '
             '- Business Unit field is filled (if "Business Unit Required" checked) '
             '- Selected BU operates in selected Branch (compatibility check). '
             'Use for: Ensuring matrix organization compliance, preventing unallocated transactions. '
             'Applies to: sale.order, purchase.order, account.move, stock.picking models. '
             'Related fields: "Allowed Branches", "Allowed Business Units" for additional restrictions.'
    )
    
    allowed_branch_ids = fields.Many2many('ops.branch', 'rule_branch_rel',
                                         string='Allowed Branches',
                                         help='Restrict to specific branches. Empty = all branches.')
    
    allowed_business_unit_ids = fields.Many2many('ops.business.unit', 'rule_bu_rel',
                                                string='Allowed Business Units',
                                                help='Restrict to specific BUs. Empty = all BUs.')
    
    branch_required = fields.Boolean(
        string='Branch Required',
        default=True,
        help='If enabled, transactions must have a branch selected. '
             'When to enable: Always (for matrix organizations). '
             'When to disable: For global/unallocated transactions, centralized purchasing. '
             'Validation: Blocks save if branch is empty. '
             'Default: Enabled (recommended for matrix compliance).'
    )
    bu_required = fields.Boolean(
        string='Business Unit Required',
        default=True,
        help='If enabled, transactions must have a business unit selected. '
             'When to enable: Always (for profit center tracking). '
             'When to disable: For corporate overhead, shared services, R&D. '
             'Validation: Blocks save if BU is empty. '
             'Default: Enabled (recommended for P&L tracking).'
    )
    
    # --- DISCOUNT CONTROL ---
    enforce_discount_limit = fields.Boolean(
        string='Enforce Discount Limit',
        help='When enabled, validates that discounts do not exceed authorized limits. '
             'How it works: '
             '1. System checks user\'s persona/role '
             '2. Looks up their discount authority (in Discount Limits section below) '
             '3. Compares transaction discount to their limit '
             '4. Blocks or requires approval if exceeded. '
             'Use for: Protecting margins, preventing unauthorized discounting. '
             'Configure: Add role-based limits in "Role-Based Discount Limits" tab. '
             'Related: Set "Global Discount Limit %" for default maximum.'
    )
    global_discount_limit = fields.Float(
        string='Global Discount Limit %',
        default=0.0,
        help='Default maximum discount percentage if no role-specific limit is defined. '
             'Applies to: All users who don\'t have a higher limit in Role-Based Discount Limits. '
             'Range: 0-100 (0 = no discounts allowed, 100 = any discount allowed). '
             'Examples: '
             '- Sales rep default = 5% '
             '- Manager can override up to 15% in discount limits '
             '- Executive can override up to 30% in discount limits. '
             'Leave at 0 if all users must have explicitly defined limits.'
    )
    
    discount_validation_level = fields.Selection([
        ('line', 'Per Line'),
        ('order', 'Per Order'),
        ('both', 'Both Line and Order'),
    ], string='Discount Validation Level', default='line')
    
    # --- MARGIN PROTECTION ---
    enforce_margin_protection = fields.Boolean(
        string='Enforce Margin Protection',
        help='When enabled, ensures profit margins meet minimum thresholds. '
             'How it works: '
             '1. Calculates margin: (Revenue - Cost) / Revenue × 100 '
             '2. Compares to minimum margin rules (by product category, BU, branch) '
             '3. Blocks or requires approval if margin too low. '
             'Use for: Preventing unprofitable sales, protecting company margins. '
             'Configure: Set "Global Minimum Margin %" and add category-specific rules below. '
             'Calculation: Uses product standard cost vs. sale price.'
    )
    global_minimum_margin = fields.Float(
        string='Global Minimum Margin %',
        default=0.0,
        help='Default minimum profit margin percentage for all products. '
             'Applies unless category-specific rule exists (see Category-Specific Margin Rules). '
             'Range: 0-100 (e.g., 15.0 = 15% margin required). '
             'Examples: '
             '- Retail: 25% minimum '
             '- Wholesale: 10% minimum '
             '- Services: 40% minimum. '
             'Calculation: ((Sale Price - Cost) / Sale Price) × 100 must be ≥ this value.'
    )
    warning_margin_threshold = fields.Float(string='Warning Margin Threshold %', default=5.0,
                                           help='Margin percentage that triggers warning')
    
    # --- PRICE OVERRIDE CONTROL ---
    enforce_price_override = fields.Boolean(string='Enforce Price Override Control')
    global_max_price_variance = fields.Float(string='Global Max Price Variance %', default=0.0)
    
    # --- APPROVAL CONFIGURATION ---
    require_approval = fields.Boolean(
        string='Require Approval',
        help='When enabled, violations trigger approval workflow instead of blocking. '
             'Behavior: '
             '- Unchecked: Violations block the transaction (hard stop) '
             '- Checked: Transaction allowed but approval request created. '
             'Use Cases: '
             '- Exceptions allowed with management approval '
             '- High-value transactions need review '
             '- Unusual discount requests. '
             'Workflow: System finds approvers based on branch/BU and routes request. '
             'Approvers: Configure in "Approval Users/Personas" or notification groups.'
    )
    approval_workflow_id = fields.Many2one('ops.approval.workflow', string='Approval Workflow')
    auto_create_approval = fields.Boolean(string='Auto-Create Approval Request', default=True)
    
    # --- NOTIFICATION ---
    notify_users = fields.Boolean(string='Notify Users')
    notify_template_id = fields.Many2one('mail.template', string='Notification Template')
    notify_groups = fields.Many2many('res.groups', string='Notify Groups')
    
    # --- RELATED RECORDS ---
    discount_limit_ids = fields.One2many('ops.governance.discount.limit', 'rule_id',
                                        string='Role-Based Discount Limits')
    
    margin_rule_ids = fields.One2many('ops.governance.margin.rule', 'rule_id',
                                     string='Category-Specific Margin Rules')
    
    price_authority_ids = fields.One2many('ops.governance.price.authority', 'rule_id',
                                         string='Role-Based Price Authority')
    
    # --- COMPUTED FIELDS ---
    violation_count = fields.Integer(string='Violation Count', compute='_compute_violation_count')
    active_approval_count = fields.Integer(string='Active Approvals', compute='_compute_approval_count')
    
    # --- LEGACY FIELDS (Backward Compatibility) ---
    trigger_type = fields.Selection(TRIGGER_TYPES, string='Trigger Event', default='on_write')
    condition_domain = fields.Text(string='Condition Domain')
    condition_code = fields.Text(string='Condition Code (Python)')
    action_type = fields.Selection(ACTION_TYPES, string='Action Type', default='warning')
    error_message = fields.Char(string='Error/Warning Message')
    approval_user_ids = fields.Many2many('res.users', 'rule_user_rel', string='Approval Users')
    approval_persona_ids = fields.Many2many('ops.persona', 'rule_approval_persona_rel',
                                           'rule_id', 'persona_id', string='Approval Personas')
    lock_on_approval_request = fields.Boolean(string='Lock During Approval', default=True)
    min_margin_percent = fields.Float(string='Minimum Margin %')
    max_discount_percent = fields.Float(string='Maximum Discount %')
    business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')
    
    # --- VALIDATION METHODS ---
    
    @api.constrains('allowed_branch_ids', 'company_id')
    def _check_branch_company(self):
        """Ensure allowed branches belong to rule's company."""
        for rule in self:
            invalid_branches = rule.allowed_branch_ids.filtered(
                lambda b: b.company_id != rule.company_id
            )
            if invalid_branches:
                raise ValidationError(
                    _("Branches %s do not belong to company %s") % (
                        ', '.join(invalid_branches.mapped('name')),
                        rule.company_id.name
                    )
                )
    
    @api.constrains('min_margin_percent', 'max_discount_percent')
    def _check_percentages(self):
        """Validate margin and discount percentages."""
        for record in self:
            if record.min_margin_percent and (record.min_margin_percent < 0 or record.min_margin_percent > 100):
                raise ValidationError(_('Minimum margin percentage must be between 0 and 100.'))
            if record.max_discount_percent and (record.max_discount_percent < 0 or record.max_discount_percent > 100):
                raise ValidationError(_('Maximum discount percentage must be between 0 and 100.'))
    
    # --- BUSINESS METHODS ---
    
    def validate_record(self, record, trigger_type='always'):
        """Validate record against this rule."""
        self.ensure_one()
        
        # ADMIN BYPASS: Skip validation for Administrator and System Managers
        if self.env.su or self.env.user.has_group('base.group_system'):
            return {'valid': True, 'warnings': [], 'errors': [], 'requires_approval': False}
        
        # Check if rule applies to this trigger (use trigger_event if set, fallback to trigger_condition)
        active_trigger = self.trigger_event or self.trigger_condition
        if active_trigger != 'always' and active_trigger != trigger_type:
            return {'valid': True, 'warnings': [], 'errors': [], 'requires_approval': False}
        
        # Evaluate new condition_logic field if specified
        if self.condition_logic:
            try:
                eval_context = {
                    'record': record,
                    'self': record,
                    'user': self.env.user,
                    'env': self.env,
                }
                # Add common fields to context
                for field in ['state', 'amount_total', 'amount_untaxed', 'partner_id', 'company_id']:
                    if hasattr(record, field):
                        eval_context[field] = getattr(record, field)
                
                condition_result = safe_eval(self.condition_logic, eval_context)
                if not condition_result:
                    return {'valid': True, 'warnings': [], 'errors': [], 'requires_approval': False}
            except Exception as e:
                _logger.warning(f"Could not evaluate condition_logic for rule {self.name}: {e}")
                return {'valid': True, 'warnings': [], 'errors': [], 'requires_approval': False}
        
        # Check legacy state condition if specified
        if self.state_condition:
            try:
                if not safe_eval(self.state_condition, {'record': record, 'state': record.state if hasattr(record, 'state') else None}):
                    return {'valid': True, 'warnings': [], 'errors': [], 'requires_approval': False}
            except Exception as e:
                _logger.warning(f"Could not evaluate state condition for rule {self.name}: {e}")
        
        errors = []
        warnings = []
        requires_approval = False
        
        # 1. MATRIX DIMENSION VALIDATION
        if self.enforce_branch_bu:
            matrix_result = self._validate_matrix_dimensions(record)
            errors.extend(matrix_result['errors'])
            warnings.extend(matrix_result['warnings'])
            requires_approval = requires_approval or matrix_result['requires_approval']
        
        # 2. DISCOUNT LIMIT VALIDATION
        if self.enforce_discount_limit:
            discount_result = self._validate_discount(record)
            errors.extend(discount_result['errors'])
            warnings.extend(discount_result['warnings'])
            requires_approval = requires_approval or discount_result['requires_approval']
        
        # 3. MARGIN PROTECTION VALIDATION
        if self.enforce_margin_protection:
            margin_result = self._validate_margin(record)
            errors.extend(margin_result['errors'])
            warnings.extend(margin_result['warnings'])
            requires_approval = requires_approval or margin_result['requires_approval']
        
        # 4. PRICE OVERRIDE VALIDATION
        if self.enforce_price_override:
            price_result = self._validate_price_override(record)
            errors.extend(price_result['errors'])
            warnings.extend(price_result['warnings'])
            requires_approval = requires_approval or price_result['requires_approval']
        
        # 5. LEGACY CONDITION VALIDATION
        if self.rule_type == 'legacy' and (self.condition_domain or self.condition_code):
            legacy_result = self._evaluate_legacy_condition(record)
            if not legacy_result:
                errors.extend([self.error_message or 'Legacy rule condition not met'])
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors,
            'requires_approval': requires_approval,
        }
    
    def _validate_matrix_dimensions(self, record):
        """Validate matrix dimensions (Branch/BU)."""
        errors = []
        warnings = []
        requires_approval = False
        
        # Check if record has matrix fields
        has_branch = hasattr(record, 'ops_branch_id')
        has_bu = hasattr(record, 'ops_business_unit_id')
        
        # Branch validation
        if self.branch_required and has_branch:
            if not record.ops_branch_id:
                errors.append(_("Branch selection is required by governance rule '%s'") % self.name)
            elif self.allowed_branch_ids and record.ops_branch_id not in self.allowed_branch_ids:
                errors.append(
                    _("Branch '%s' is not allowed. Allowed branches: %s") % (
                        record.ops_branch_id.name,
                        ', '.join(self.allowed_branch_ids.mapped('name'))
                    )
                )
        
        # BU validation
        if self.bu_required and has_bu:
            if not record.ops_business_unit_id:
                errors.append(_("Business Unit selection is required by governance rule '%s'") % self.name)
            elif self.allowed_business_unit_ids and record.ops_business_unit_id not in self.allowed_business_unit_ids:
                errors.append(
                    _("Business Unit '%s' is not allowed. Allowed BUs: %s") % (
                        record.ops_business_unit_id.name,
                        ', '.join(self.allowed_business_unit_ids.mapped('name'))
                    )
                )
        
        # Cross-validation: Ensure BU operates in selected branch
        if has_branch and has_bu and record.ops_branch_id and record.ops_business_unit_id:
            if record.ops_branch_id not in record.ops_business_unit_id.branch_ids:
                errors.append(
                    _("Business Unit '%s' does not operate in branch '%s'") % (
                        record.ops_business_unit_id.name,
                        record.ops_branch_id.name
                    )
                )
        
        return {'errors': errors, 'warnings': warnings, 'requires_approval': requires_approval}
    
    def _validate_discount(self, record):
        """Validate discount against limits."""
        errors = []
        warnings = []
        requires_approval = False
        
        # Get current user and their persona
        user = self.env.user
        user_personas = user.persona_ids if hasattr(user, 'persona_ids') else self.env['ops.persona']
        
        if record._name == 'sale.order.line':
            # Line-level discount validation
            discount = record.discount
            
            # Get user's discount limit from persona
            max_discount = self._get_user_discount_limit(user, user_personas, record)
            
            if discount > max_discount:
                # Check if approval is configured
                if self.require_approval:
                    requires_approval = True
                    warnings.append(
                        _("Discount %.2f%% exceeds your limit of %.2f%%. Approval will be requested.") % (
                            discount, max_discount
                        )
                    )
                else:
                    errors.append(
                        _("Discount %.2f%% exceeds maximum allowed %.2f%%.") % (discount, max_discount)
                    )
        
        elif record._name == 'sale.order':
            # Order-level discount validation
            if self.discount_validation_level in ['order', 'both']:
                order_discount = getattr(record, 'global_discount', 0.0) or 0.0
                max_discount = self._get_user_discount_limit(user, user_personas, record)
                
                if order_discount > max_discount:
                    if self.require_approval:
                        requires_approval = True
                        warnings.append(
                            _("Order discount %.2f%% exceeds your limit of %.2f%%. Approval will be requested.") % (
                                order_discount, max_discount
                            )
                        )
                    else:
                        errors.append(
                            _("Order discount %.2f%% exceeds maximum allowed %.2f%%.") % (order_discount, max_discount)
                        )
        
        return {'errors': errors, 'warnings': warnings, 'requires_approval': requires_approval}
    
    def _validate_margin(self, record):
        """Validate margin against thresholds."""
        errors = []
        warnings = []
        requires_approval = False
        
        if record._name == 'sale.order.line':
            margin_percent = self._calculate_line_margin(record)
            min_margin = self._get_minimum_margin(
                record.product_id.categ_id,
                getattr(record, 'ops_business_unit_id', False),
                getattr(record, 'ops_branch_id', False)
            )
            
            if margin_percent < min_margin:
                if self.require_approval:
                    requires_approval = True
                    warnings.append(
                        _("Margin %.2f%% is below minimum %.2f%%. Approval will be requested.") % (
                            margin_percent, min_margin
                        )
                    )
                else:
                    errors.append(
                        _("Margin %.2f%% is below minimum required %.2f%%.") % (margin_percent, min_margin)
                    )
            elif margin_percent < (min_margin + self.warning_margin_threshold):
                warnings.append(
                    _("Margin %.2f%% is close to minimum threshold %.2f%%.") % (margin_percent, min_margin)
                )
        
        elif record._name == 'sale.order':
            # Calculate order-level margin
            order_margin = self._calculate_order_margin(record)
            # Use lowest margin requirement from order lines
            min_margins = [
                self._get_minimum_margin(
                    line.product_id.categ_id,
                    getattr(line, 'ops_business_unit_id', False),
                    getattr(line, 'ops_branch_id', False)
                )
                for line in record.order_line if line.product_id
            ]
            min_margin = min(min_margins) if min_margins else self.global_minimum_margin
            
            if order_margin < min_margin:
                if self.require_approval:
                    requires_approval = True
                    warnings.append(
                        _("Order margin %.2f%% is below minimum %.2f%%. Approval will be requested.") % (
                            order_margin, min_margin
                        )
                    )
                else:
                    errors.append(
                        _("Order margin %.2f%% is below minimum required %.2f%%.") % (order_margin, min_margin)
                    )
        
        return {'errors': errors, 'warnings': warnings, 'requires_approval': requires_approval}
    
    def _validate_price_override(self, record):
        """Validate price override against authorized limits."""
        errors = []
        warnings = []
        requires_approval = False
        
        if record._name == 'sale.order.line':
            # Get product list price
            list_price = record.product_id.list_price
            current_price = record.price_unit
            
            if list_price > 0:
                variance_percent = abs((current_price - list_price) / list_price * 100)
                max_variance = self._get_user_price_variance_limit(self.env.user, record)
                
                if variance_percent > max_variance:
                    if self.require_approval:
                        requires_approval = True
                        warnings.append(
                            _("Price variance %.2f%% exceeds your limit of %.2f%%. Approval will be requested.") % (
                                variance_percent, max_variance
                            )
                        )
                    else:
                        errors.append(
                            _("Price variance %.2f%% exceeds maximum allowed %.2f%%.") % (variance_percent, max_variance)
                        )
        
        return {'errors': errors, 'warnings': warnings, 'requires_approval': requires_approval}
    
    def _evaluate_legacy_condition(self, record):
        """Evaluate legacy condition (backward compatibility)."""
        try:
            # Try domain first if available
            if self.condition_domain:
                domain = self._parse_domain_string(self.condition_domain)
                matches = record.filtered_domain(domain)
                if not matches:
                    return False
            
            # Try Python code if available
            if self.condition_code:
                safe_locals = {
                    'self': record,
                    'record': record,
                    'user': record.env.user,
                    'env': record.env,
                }
                result = safe_eval(self.condition_code, safe_locals)
                return bool(result)
            
            return True
        except Exception as e:
            _logger.error(f'Error evaluating legacy rule condition: {e}')
            return False
    
    def _parse_domain_string(self, domain_str):
        """Parse a domain string into a list."""
        try:
            import ast
            return ast.literal_eval(domain_str)
        except (ValueError, SyntaxError) as e:
            raise ValidationError(_('Invalid domain syntax: %s') % str(e))
    
    def _get_user_discount_limit(self, user, personas, record=None):
        """Get maximum discount percentage for user based on role/persona."""
        max_discount = self.global_discount_limit
        
        # Get context for scope restrictions
        branch_id = getattr(record, 'ops_branch_id', False)
        bu_id = getattr(record, 'ops_business_unit_id', False)
        category_id = False
        if record._name == 'sale.order.line' and hasattr(record, 'product_id'):
            category_id = record.product_id.categ_id.id
        
        # Check persona-based limits
        for persona in personas:
            limit_rules = self.discount_limit_ids.filtered(lambda r: r.persona_id == persona)
            for limit_rule in limit_rules:
                applicable_limit = limit_rule.get_applicable_limit(
                    user,
                    branch_id.id if branch_id else False,
                    bu_id.id if bu_id else False,
                    category_id
                )
                if applicable_limit > 0:
                    max_discount = max(max_discount, applicable_limit)
        
        # Check group-based limits
        for limit_rule in self.discount_limit_ids.filtered(lambda r: r.user_group_id):
            try:
                if user.has_group(limit_rule.user_group_id.xml_id or 'base.group_user'):
                    applicable_limit = limit_rule.get_applicable_limit(
                        user,
                        branch_id.id if branch_id else False,
                        bu_id.id if bu_id else False,
                        category_id
                    )
                    if applicable_limit > 0:
                        max_discount = max(max_discount, applicable_limit)
            except Exception:
                pass
        
        return max_discount
    
    def _calculate_line_margin(self, order_line):
        """Calculate margin percentage for a sale order line."""
        if order_line.price_subtotal == 0:
            return 0.0
        
        # Get product cost
        cost = order_line.product_id.standard_price * order_line.product_uom_qty
        revenue = order_line.price_subtotal
        margin = revenue - cost
        margin_percent = (margin / revenue) * 100 if revenue else 0.0
        
        return margin_percent
    
    def _calculate_order_margin(self, order):
        """Calculate margin percentage for entire order."""
        total_revenue = order.amount_untaxed
        if total_revenue == 0:
            return 0.0
        
        total_cost = sum(
            line.product_id.standard_price * line.product_uom_qty
            for line in order.order_line if line.product_id
        )
        total_margin = total_revenue - total_cost
        margin_percent = (total_margin / total_revenue) * 100
        
        return margin_percent
    
    def _get_minimum_margin(self, category, business_unit, branch):
        """Get minimum margin for product category, BU, and branch."""
        if not category:
            return self.global_minimum_margin
        
        # First try specific rule (category + BU + branch)
        if business_unit and branch:
            margin_rule = self.margin_rule_ids.filtered(
                lambda r: r.product_category_id == category and
                         r.business_unit_id == business_unit and
                         r.branch_id == branch
            )
            if margin_rule:
                return margin_rule[0].minimum_margin_percent
        
        # Try category + BU
        if business_unit:
            margin_rule = self.margin_rule_ids.filtered(
                lambda r: r.product_category_id == category and
                         r.business_unit_id == business_unit and
                         not r.branch_id
            )
            if margin_rule:
                return margin_rule[0].minimum_margin_percent
        
        # Try category + branch
        if branch:
            margin_rule = self.margin_rule_ids.filtered(
                lambda r: r.product_category_id == category and
                         not r.business_unit_id and
                         r.branch_id == branch
            )
            if margin_rule:
                return margin_rule[0].minimum_margin_percent
        
        # Try category only
        margin_rule = self.margin_rule_ids.filtered(
            lambda r: r.product_category_id == category and
                     not r.business_unit_id and
                     not r.branch_id
        )
        if margin_rule:
            return margin_rule[0].minimum_margin_percent
        
        # Fallback to global minimum
        return self.global_minimum_margin
    
    def _get_user_price_variance_limit(self, user, record=None):
        """Get user's price variance authority."""
        max_variance = self.global_max_price_variance
        personas = user.persona_ids if hasattr(user, 'persona_ids') else self.env['ops.persona']
        
        # Get context for scope restrictions
        branch_id = getattr(record, 'ops_branch_id', False)
        bu_id = getattr(record, 'ops_business_unit_id', False)
        category_id = False
        if record and record._name == 'sale.order.line' and hasattr(record, 'product_id'):
            category_id = record.product_id.categ_id.id
        
        # Check persona-based limits
        for persona in personas:
            auth_rules = self.price_authority_ids.filtered(lambda r: r.persona_id == persona)
            for auth_rule in auth_rules:
                authority = auth_rule.get_applicable_authority(
                    user,
                    branch_id.id if branch_id else False,
                    bu_id.id if bu_id else False,
                    category_id
                )
                if authority['max_variance'] > 0:
                    max_variance = max(max_variance, authority['max_variance'])
        
        return max_variance
    
    def action_create_approval_request(self, record, violation_type, violation_details):
        """Create approval request for governance violation."""
        self.ensure_one()
        
        if not self.require_approval:
            return False
        
        # Find approvers based on matrix dimensions
        approvers = self._find_approvers(record, violation_type)
        
        if not approvers:
            _logger.warning(f"No approvers found for rule {self.name}")
            return False
        
        # Create approval request
        approval = self.env['ops.approval.request'].create({
            'name': _("Governance Approval: %s - %s") % (violation_type, record.name or record._name),
            'rule_id': self.id,
            'model_name': record._name,
            'res_id': record.id,
            'notes': violation_details,
            'approver_ids': [(6, 0, approvers.ids)],
            'requested_by': self.env.user.id,
        })
        
        # Send notifications
        if self.notify_users:
            try:
                approval.message_post(
                    body=_("Governance approval requested: %s") % violation_details,
                    partner_ids=approvers.mapped('partner_id').ids,
                )
            except Exception as e:
                _logger.warning(f"Could not send notification: {e}")
        
        return approval
    
    def _find_approvers(self, record, violation_type):
        """Find approvers based on matrix dimensions and violation type."""
        approvers = self.env['res.users']
        
        # Get personas that can approve for this branch/BU
        Persona = self.env['ops.persona']
        domain = [
            ('company_id', '=', record.company_id.id if hasattr(record, 'company_id') else self.env.company.id),
            ('active', '=', True),
        ]
        
        # Add matrix dimension filters
        if hasattr(record, 'ops_branch_id') and record.ops_branch_id:
            domain.append(('branch_ids', 'in', record.ops_branch_id.id))
        
        if hasattr(record, 'ops_business_unit_id') and record.ops_business_unit_id:
            domain.append(('business_unit_ids', 'in', record.ops_business_unit_id.id))
        
        # Add approval authority filters based on violation type
        if violation_type == 'discount':
            domain.append(('can_approve_discounts', '=', True))
        elif violation_type == 'margin':
            domain.append(('can_approve_margin_exceptions', '=', True))
        elif violation_type == 'price':
            domain.append(('can_approve_price_overrides', '=', True))
        elif violation_type == 'matrix':
            domain.append(('can_approve_matrix_exceptions', '=', True))
        
        # Get personas and extract users
        try:
            personas = Persona.search(domain)
            approvers |= personas.mapped('user_id')
        except Exception as e:
            _logger.warning(f"Error finding persona approvers: {e}")
        
        # Also check group-based approvers
        if self.notify_groups:
            group_users = self.env['res.users'].search([
                ('group_ids', 'in', self.notify_groups.ids),
                ('company_id', 'in', [self.company_id.id, False]),
            ])
            approvers |= group_users
        
        # Fallback to approval_user_ids if no approvers found
        if not approvers and self.approval_user_ids:
            approvers = self.approval_user_ids
        
        return approvers
    
    # --- LEGACY METHODS (Backward Compatibility) ---
    
    def _trigger_approval_if_needed(self, record):
        """Check if record matches this rule and trigger approval workflow if needed."""
        self.ensure_one()
        
        # Only process if rule is active
        if not self.active:
            return False
        
        # For new rule types, use validate_record
        if self.rule_type != 'legacy':
            result = self.validate_record(record)
            if not result['valid'] or result['requires_approval']:
                violation_details = '\n'.join(result['errors'] + result['warnings'])
                return self.action_create_approval_request(record, self.rule_type, violation_details)
            return False
        
        # Legacy logic
        if not self._evaluate_legacy_condition(record):
            return False
        
        # Action: Warning (log and continue)
        if self.action_type == 'warning':
            try:
                record.message_post(
                    body=_('<strong>Governance Alert:</strong> %s') % self.error_message,
                    message_type='notification'
                )
            except Exception:
                pass
            return False
        
        # Action: Block (prevent operation)
        if self.action_type == 'block':
            raise ValidationError(_('Governance Rule Blocked: %s') % self.error_message)
        
        # Action: Require Approval
        if self.action_type == 'require_approval':
            approvers = self.approval_user_ids | self.env['res.users'].search([
                ('persona_ids', 'in', self.approval_persona_ids.ids)
            ])
            
            try:
                approval = self.env['ops.approval.request'].create({
                    'name': _('Approval Required: %s') % self.name,
                    'rule_id': self.id,
                    'model_name': record._name,
                    'res_id': record.id,
                    'notes': self.error_message,
                    'approver_ids': [(6, 0, approvers.ids)],
                })
                
                # Lock record if configured
                if self.lock_on_approval_request and hasattr(record, 'active'):
                    try:
                        record.write({'active': False})
                    except Exception:
                        pass
                
                return True
            except Exception as e:
                _logger.error(f"Error creating approval request: {e}")
                return False
        
        return False
    
    @api.model
    def evaluate_rules_for_record(self, record, trigger_type='on_write'):
        """Evaluate all applicable rules for a record."""
        # ADMIN BYPASS: Skip all rule evaluation for Administrator and System Managers
        if self.env.su or self.env.user.has_group('base.group_system'):
            return
        
        rules = self.search([
            ('active', '=', True),
            ('model_id.model', '=', record._name),
            '|',
            ('trigger_type', '=', trigger_type),
            ('trigger_condition', '=', 'always')
        ], order='sequence ASC')
        
        for rule in rules:
            rule._trigger_approval_if_needed(record)
    
    # --- COMPUTED METHODS ---
    
    @api.depends('rule_type', 'enforce_branch_bu', 'enforce_discount_limit', 
                 'enforce_margin_protection', 'enforce_price_override')
    def _compute_description(self):
        """Generate rule description based on configuration."""
        for rule in self:
            parts = []
            
            if rule.enforce_branch_bu:
                parts.append(_("Enforces Branch/BU selection"))
            
            if rule.enforce_discount_limit:
                parts.append(_("Discount limit: %.2f%%") % rule.global_discount_limit)
            
            if rule.enforce_margin_protection:
                parts.append(_("Minimum margin: %.2f%%") % rule.global_minimum_margin)
            
            if rule.enforce_price_override:
                parts.append(_("Max price variance: %.2f%%") % rule.global_max_price_variance)
            
            if rule.require_approval:
                parts.append(_("Requires approval"))
            
            rule.description = " | ".join(parts) if parts else _("No validations configured")
    
    def _compute_violation_count(self):
        """Count violations for this rule."""
        for rule in self:
            rule.violation_count = self.env['ops.approval.request'].search_count([
                ('rule_id', '=', rule.id),
                ('state', 'in', ['pending', 'approved', 'rejected']),
            ])
    
    def _compute_approval_count(self):
        """Count active approval requests."""
        for rule in self:
            rule.active_approval_count = self.env['ops.approval.request'].search_count([
                ('rule_id', '=', rule.id),
                ('state', '=', 'pending'),
            ])
    
    def action_check_compliance(self):
        """Manual compliance check action - shows statistics for this rule."""
        self.ensure_one()
        
        # Refresh computed fields
        self._compute_violation_count()
        self._compute_approval_count()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Compliance Check'),
                'message': _(
                    'Rule: %s\n'
                    'Active: %s\n'
                    'Total Violations: %d\n'
                    'Pending Approvals: %d'
                ) % (
                    self.name,
                    _('Yes') if self.active else _('No'),
                    self.violation_count,
                    self.active_approval_count
                ),
                'type': 'info',
                'sticky': False,
            }
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate code if not provided."""
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('ops.governance.rule') or 'GR0001'
        return super().create(vals_list)
