# OPS Matrix Framework - Developer Guide

This guide provides comprehensive information for developers who want to extend, customize, or integrate with the OPS Matrix Framework. It covers the framework's architecture, extension points, development best practices, and advanced customization techniques.

## Framework Architecture

### Module Structure

The OPS Matrix Framework consists of two main modules:

```
ops_matrix_core/           # Foundation module
├── models/                # Core business models (branches, BUs, personas, governance)
├── views/                 # User interface definitions
├── controllers/           # API endpoints (ops_matrix_api.py with 256-bit token auth)
├── security/              # Access control and record rules
├── data/                  # Initial data and templates
├── wizards/               # Configuration wizards
├── reports/               # Zero-bloat SQL views (sales.analysis, financial.analysis, inventory.analysis)
└── tools/                 # Utility functions

ops_matrix_accounting/     # Financial and asset management
├── models/                # Accounting models (assets, PDC, budgeting, consolidated reporting)
├── reports/               # Financial reports with Excel export
└── wizards/               # Accounting wizards
```

### Core Models Hierarchy

```
res.company (Odoo base)
├── ops.branch
│   ├── ops.business.unit (many-to-many relationship)
│   └── res.users (branch managers)

ops.persona
├── res.users (many-to-many through ops.persona.delegation)
├── ops.branch (allowed branches)
└── ops.business.unit (allowed business units)

Transactional Models (extended):
├── sale.order
├── purchase.order
├── account.move
├── stock.picking
└── product.template
```

### Unified Model Map

The OPS Matrix Framework integrates deeply with Odoo native models through matrix mixins and extension patterns:

```
Odoo Native Models (Extended)
├── res.company
│   ├── ops_code (auto-generated)
│   ├── ops_manager_id (Country Manager)
│   ├── ops_analytic_account_id (auto-created)
│   └── Operational Branches tab (ops.branch lines)
│
├── res.users
│   ├── ops_persona_ids (delegation system)
│   ├── ops_allowed_branch_ids (computed)
│   └── ops_allowed_business_unit_ids (computed)
│
├── account.move (journal entries)
│   └── ops.matrix.mixin (branch/BU tracking)
│
├── sale.order
│   ├── ops_branch_id
│   ├── ops_business_unit_id
│   └── ops_analytic_account_id
│
├── purchase.order
│   ├── ops_branch_id
│   ├── ops_business_unit_id
│   └── ops_analytic_account_id
│
├── stock.picking
│   ├── ops_branch_id
│   └── ops_business_unit_id
│
└── product.template
    └── ops_silo_id (product isolation)

OPS Matrix Core Models
├── ops.branch
│   ├── linked to res.company via tab
│   ├── manager_id (res.users)
│   └── business_unit_ids (many-to-many)
│
├── ops.business.unit
│   ├── leader_id (res.users)
│   ├── branch_ids (many-to-many)
│   └── company_id (res.company)
│
├── ops.persona
│   ├── allowed_branch_ids (ops.branch)
│   ├── allowed_business_unit_ids (ops.business.unit)
│   ├── user_ids via ops.persona.delegation
│   └── is_manager flag
│
├── ops.governance.rule (6 rule types)
│   ├── approval workflows
│   └── SLA integration
│
├── ops.approval.request
│   └── automated workflows
│
├── ops.sla.template (business calendar integration)
│   └── ops.sla.instance tracking
│
└── ops.api.key (256-bit tokens)

OPS Matrix Accounting Models
├── ops.asset (lifecycle: draft → running → close/sold)
│   ├── ops.asset.category (hierarchical)
│   ├── ops.asset.model
│   ├── ops.asset.depreciation (manual lines)
│   └── ops.matrix.mixin
│
├── ops.pdc (post-dated checks)
│   └── journal entries with anti-fraud
│
├── ops.budget (multi-dimensional by Branch × BU)
│   └── cost control
│
└── ops.consolidated.reporting
    └── company-level P&L with branch/BU breakdown

Zero-Bloat Reporting (SQL Views in Core)
├── ops.sales.analysis
├── ops.financial.analysis
└── ops.inventory.analysis
    └── Excel export via ops_excel_export_wizard
```

**Key Integration Patterns:**
- `ops.matrix.mixin`: Adds branch/BU fields to transactional models
- `ops.analytic.mixin`: Links to analytic accounts for reporting
- `ops.sla.mixin`: SLA tracking on applicable models
- Security via persona-based access (Branch ∩ BU for sales/financial, BU ∪ global for inventory)
- RESTful API (`controllers/ops_matrix_api.py`) with 256-bit token auth

## Extension Points

### 1. Model Extensions

#### Extending Core Models
To add custom fields to OPS Matrix models:

```python
# In your custom module's models/__init__.py
from . import your_custom_model

# In models/your_custom_model.py
from odoo import models, fields, api

class OPSBranch(models.Model):
    _inherit = 'ops.branch'

    # Add custom fields
    custom_field = fields.Char(string='Custom Field')
    branch_type = fields.Selection([
        ('retail', 'Retail'),
        ('warehouse', 'Warehouse'),
        ('office', 'Office')
    ], string='Branch Type')

    # Add custom methods
    def custom_method(self):
        # Your custom logic here
        pass
```

#### Creating New Models with OPS Integration
```python
class CustomOPSModel(models.Model):
    _name = 'custom.ops.model'
    _description = 'Custom OPS Model'

    # Required OPS fields
    ops_branch_id = fields.Many2one('ops.branch', string='Branch')
    ops_business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit')

    # Custom fields
    name = fields.Char(required=True)
    description = fields.Text()

    # Computed fields
    @api.depends('ops_branch_id', 'ops_business_unit_id')
    def _compute_access_domain(self):
        for record in self:
            # Custom access logic
            pass
```

### 2. Security and Access Control

#### Custom Record Rules
```xml
<!-- In security/ir_rule.xml -->
<record id="custom_model_branch_rule" model="ir.rule">
    <field name="name">Custom Model Branch Access</field>
    <field name="model_id" ref="model_custom_ops_model"/>
    <field name="domain_force">[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

#### Custom Access Rights
```xml
<!-- In security/ir.model.access.csv -->
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_model_user,custom.model.user,model_custom_ops_model,base.group_user,1,1,1,0
access_custom_model_manager,custom.model.manager,model_custom_ops_model,group_custom_manager,1,1,1,1
```

### 3. API Extensions

#### Adding Custom API Endpoints
```python
# In controllers/custom_api.py
from odoo import http
from odoo.http import request

class CustomAPIController(http.Controller):
    _prefix = '/api/v1/ops_matrix'

    @http.route('/custom_endpoint', type='json', auth='public', methods=['POST'], csrf=False)
    def custom_endpoint(self, **kwargs):
        # API key authentication
        api_key = request.httprequest.headers.get('X-API-Key')
        if not self._authenticate_api_key(api_key):
            return {'success': False, 'error': 'Invalid API key'}

        # Your custom logic
        result = self._process_custom_request(kwargs)
        return {'success': True, 'data': result}

    def _authenticate_api_key(self, api_key):
        # Implement API key validation
        return True  # Placeholder

    def _process_custom_request(self, data):
        # Custom business logic
        return {'message': 'Custom endpoint response'}
```

#### Extending Existing Endpoints
```python
# Monkey patch existing API methods
from odoo.addons.ops_matrix_core.controllers.ops_matrix_api import OPSMatrixAPI

def custom_me_method(self):
    # Original method
    result = original_me_method(self)

    # Add custom data
    result['data']['custom_field'] = 'additional_info'
    return result

# Apply monkey patch
original_me_method = OPSMatrixAPI.me
OPSMatrixAPI.me = custom_me_method
```

### 4. User Interface Extensions

#### Adding Custom Dashboard Widgets
```xml
<!-- In views/custom_dashboard.xml -->
<record id="custom_dashboard_widget" model="ir.ui.view">
    <field name="name">Custom Dashboard Widget</field>
    <field name="model">board.board</field>
    <field name="inherit_id" ref="ops_matrix_core.ops_executive_dashboard"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@class='o_dashboard_content']" position="inside">
            <div class="custom-widget">
                <h4>Custom Metrics</h4>
                <div class="metric-value" t-field="custom_value"/>
            </div>
        </xpath>
    </field>
</record>
```

#### Custom JavaScript Components
```javascript
// In static/src/js/custom_widget.js
odoo.define('custom_module.CustomWidget', function (require) {
    'use strict';

    var Widget = require('web.Widget');

    var CustomWidget = Widget.extend({
        template: 'CustomWidgetTemplate',

        init: function (parent, options) {
            this._super(parent, options);
            this.data = options.data;
        },

        start: function () {
            this._loadData();
            return this._super();
        },

        _loadData: function () {
            // Load custom data via AJAX
            this._rpc({
                route: '/api/v1/ops_matrix/custom_data',
                params: {}
            }).then(function (result) {
                this.data = result;
                this.render();
            }.bind(this));
        }
    });

    return CustomWidget;
});
```

### 5. Report Extensions

#### Custom Excel Export Templates
```python
# In wizards/custom_excel_export.py
from odoo import models, fields, api
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class CustomExcelReport(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, objects):
        # Custom Excel generation logic
        sheet = workbook.add_worksheet('Custom Report')

        # Header
        bold = workbook.add_format({'bold': True})
        sheet.write('A1', 'Custom Report', bold)

        # Data
        row = 1
        for obj in objects:
            sheet.write(row, 0, obj.name)
            sheet.write(row, 1, obj.custom_field)
            row += 1
```

#### Custom Analysis Models
```python
# In models/custom_analysis.py
from odoo import models, fields, api

class CustomAnalysis(models.Model):
    _name = 'custom.analysis'
    _auto = False
    _description = 'Custom Analysis Model'

    # Dimensions
    branch_id = fields.Many2one('ops.branch', readonly=True)
    date = fields.Date(readonly=True)
    category = fields.Char(readonly=True)

    # Measures
    total_amount = fields.Float(readonly=True)
    count = fields.Integer(readonly=True)

    def init(self):
        # SQL view definition
        self._cr.execute("""
            CREATE OR REPLACE VIEW custom_analysis AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    so.ops_branch_id as branch_id,
                    so.date_order::date as date,
                    pt.categ_id as category,
                    SUM(so.amount_total) as total_amount,
                    COUNT(*) as count
                FROM sale_order so
                JOIN sale_order_line sol ON sol.order_id = so.id
                JOIN product_product pp ON pp.id = sol.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE so.state = 'sale'
                GROUP BY so.ops_branch_id, so.date_order::date, pt.categ_id
            )
        """)
```

## Development Best Practices

### 1. Code Organization
- Follow Odoo coding standards
- Use meaningful model and field names
- Implement proper error handling
- Add comprehensive logging

### 2. Security Considerations
- Always validate user permissions
- Use proper access controls
- Sanitize user inputs
- Implement audit logging for sensitive operations

### 3. Performance Optimization
- Use appropriate database indexes
- Implement efficient queries
- Cache frequently accessed data
- Avoid N+1 query problems

### 4. Testing
```python
# In tests/test_custom_module.py
from odoo.tests.common import TransactionCase

class TestCustomModule(TransactionCase):

    def setUp(self):
        super().setUp()
        # Test setup code

    def test_custom_functionality(self):
        # Test implementation
        self.assertTrue(True)

    def test_branch_isolation(self):
        # Test OPS-specific functionality
        branch = self.env['ops.branch'].create({'name': 'Test Branch'})
        self.assertTrue(branch.active)
```

### 5. Documentation
- Document all custom models and methods
- Provide API documentation
- Include installation and configuration instructions
- Maintain changelog for updates

## Advanced Customization

### 1. Workflow Engine Integration
```python
# Custom workflow integration
from odoo import models, api

class CustomApprovalWorkflow(models.Model):
    _inherit = 'ops.approval.request'

    def _get_approvers(self):
        # Custom approver selection logic
        approvers = super()._get_approvers()

        # Add custom logic based on OPS context
        if self.ops_branch_id:
            branch_manager = self.ops_branch_id.manager_id
            if branch_manager:
                approvers.append(branch_manager)

        return approvers
```

### 2. Governance Rule Extensions
```python
# Custom governance rules
class CustomGovernanceRule(models.Model):
    _inherit = 'ops.governance.rule'

    rule_type = fields.Selection(selection_add=[
        ('custom_rule', 'Custom Business Rule')
    ])

    def _evaluate_custom_rule(self, record):
        # Custom rule evaluation logic
        if self.rule_type == 'custom_rule':
            # Implement your custom business logic
            return self._check_custom_conditions(record)
        return super()._evaluate_custom_rule(record)
```

### 3. SLA Engine Customization
```python
# Custom SLA calculations
class CustomSLAInstance(models.Model):
    _inherit = 'ops.sla.instance'

    def _calculate_custom_sla(self):
        # Custom SLA calculation logic
        if self.sla_template_id.custom_calculation:
            # Implement custom time calculations
            return self._custom_time_calculation()
        return super()._calculate_custom_sla()
```

### 4. Multi-Branch Reporting
```python
# Advanced multi-branch reporting
class AdvancedBranchReport(models.TransientModel):
    _name = 'advanced.branch.report'
    _description = 'Advanced Branch Performance Report'

    branch_ids = fields.Many2many('ops.branch', string='Branches')
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    include_bu_consolidation = fields.Boolean(default=True)

    def generate_report(self):
        # Multi-branch report generation
        data = self._collect_branch_data()
        if self.include_bu_consolidation:
            data.update(self._consolidate_bu_data(data))
        return self._format_report(data)

    def _collect_branch_data(self):
        # Efficient data collection across branches
        return {}

    def _consolidate_bu_data(self, branch_data):
        # Business unit consolidation logic
        return {}
```

## Migration and Upgrades

### Data Migration Scripts
```python
# In migrations/19.0.1.4/post-migration.py
def migrate(cr, version):
    # Migration logic for custom fields/data
    cr.execute("""
        UPDATE custom_ops_model
        SET new_field = old_field
        WHERE new_field IS NULL
    """)

    # Update OPS-related data
    cr.execute("""
        UPDATE custom_ops_model
        SET ops_branch_id = (
            SELECT id FROM ops_branch
            WHERE code = custom_ops_model.branch_code
            LIMIT 1
        )
        WHERE ops_branch_id IS NULL
    """)
```

### Version Compatibility
- Test custom modules with each OPS Matrix update
- Maintain backward compatibility when possible
- Document breaking changes clearly
- Provide migration guides for major updates

## Debugging and Troubleshooting

### Common Development Issues
1. **Access Denied Errors**: Check persona assignments and record rules
2. **Branch Isolation Problems**: Verify user-branch relationships
3. **API Authentication Failures**: Validate API key configuration
4. **Performance Issues**: Review query efficiency and indexing

### Debugging Tools
```python
# Debug OPS context
def debug_ops_context(self):
    user = self.env.user
    print("User:", user.name)
    print("Personas:", user.ops_persona_ids.mapped('name'))
    print("Allowed Branches:", user.ops_allowed_branch_ids.mapped('name'))
    print("Allowed BUs:", user.ops_allowed_business_unit_ids.mapped('name'))
```

### Logging Best Practices
```python
import logging

_logger = logging.getLogger(__name__)

def custom_method(self):
    _logger.info("Starting custom operation for user: %s", self.env.user.name)
    try:
        # Your logic here
        _logger.debug("Operation details: %s", details)
    except Exception as e:
        _logger.error("Error in custom operation: %s", str(e))
        raise
    _logger.info("Completed custom operation")
```

## Performance Considerations

### Database Optimization
- Add indexes on frequently queried OPS fields
- Use appropriate field types for performance
- Implement efficient domain filters
- Consider materialized views for complex analytics

### Code Performance
- Minimize database round trips
- Use batch operations when possible
- Implement caching for expensive operations
- Profile code performance regularly

### API Performance
- Implement pagination for large datasets
- Use efficient serialization
- Cache API responses when appropriate
- Monitor API usage patterns

## Support and Resources

### Development Resources
- [Odoo Documentation](https://www.odoo.com/documentation/) - Official Odoo docs
- [OPS Matrix Core Code](addons/ops_matrix_core) - Framework source code
- [API Reference](06_API_Reference.md) - Complete API documentation
- [Administrator Guide](05_Administrator_Guide.md) - System configuration

### Getting Help
- Review existing OPS Matrix code for patterns
- Check Odoo community forums
- Contact OPS Matrix development team
- Use the health endpoint for API testing

### Contributing
- Follow established coding standards
- Include comprehensive tests
- Document all changes
- Submit pull requests for review

This developer guide provides the foundation for extending and customizing the OPS Matrix Framework. Remember to always test thoroughly and follow security best practices when developing custom functionality.