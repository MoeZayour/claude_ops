# PHASE 1: Data Contracts + Bridge Parser
# Run with: claude -p "$(cat PHASE_1_CONTRACTS.md)"
# Prerequisite: Phase 0 completed
# Estimated: ~15 minutes

## CONTEXT
You are building the foundation layer for OPS Framework report engine v2 in `/opt/gemini_odoo19/addons/ops_matrix_accounting/`.
Read the master spec: `cat /opt/gemini_odoo19/addons/claude_files/REPORT_ENGINE_REWRITE_MASTER.md`
Phase 0 has archived old code. Now build the data contracts and bridge parser.

## YOUR TASK

### File 1: `report/ops_report_contracts.py`

Create the data contract module. This defines THREE report shapes as dataclasses plus helper functions.

Requirements:
1. Import `dataclasses.dataclass, field, asdict` and `typing` types
2. Define these dataclasses exactly as specified in the master spec Section 4:
   - `ReportMeta` — common metadata (report_type, title, shape, company info, dates, filters dict, generated_at/by, currency info)
   - `ReportColors` — company branding colors (primary, primary_dark, primary_light, text_on_primary, body_text, success, danger, warning, zero, border)
   - `LineEntry` — single journal entry line for Shape A
   - `LineGroup` — group of lines with opening_balance and totals
   - `ShapeAReport` — line-based report (meta, colors, groups[], grand_totals, visible_columns[])
   - `HierarchyNode` — recursive node for Shape B (code, name, level, style, values dict, children[])
   - `ShapeBReport` — hierarchy report (meta, colors, value_columns[], sections[], net_result)
   - `ColumnDef` — dynamic column definition for Shape C (key, label, col_type, width, align, subtotal)
   - `MatrixRow` — single row in Shape C (level, style, values dict)
   - `ShapeCReport` — matrix report (meta, colors, columns[], rows[], totals dict)

3. Define helper functions:
   - `build_report_meta(wizard, report_type, report_title, shape)` → ReportMeta
     - Extracts company info from wizard.company_id
     - Builds filters dict dynamically by checking hasattr on wizard for: branch_ids, business_unit_ids, journal_ids, account_ids, partner_ids, target_move, warehouse_ids, product_category_ids, partner_type
     - Handles both date_from/date_to and as_of_date patterns
     - Gets currency from company_id.currency_id
   - `build_report_colors(company)` → ReportColors
     - Reads from company.ops_report_primary_color, ops_report_text_on_primary, ops_report_body_text_color
     - Calls company.get_report_primary_light() and get_report_primary_dark() with try/except fallbacks
   - `to_dict(dataclass_instance)` → dict
     - Wrapper around `asdict()` that handles None values cleanly

4. CRITICAL: Add `from odoo import fields` import for datetime formatting
5. Add module docstring explaining the 3 shapes and when each is used

### File 2: `report/ops_report_bridge.py`

Create the universal bridge parser. ONE parser for ALL reports.

```python
from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

# Allowed wizard models (security whitelist)
ALLOWED_WIZARD_MODELS = [
    'ops.gl.report.wizard',
    'ops.tb.report.wizard',
    'ops.pnl.report.wizard',
    'ops.bs.report.wizard',
    'ops.cf.report.wizard',
    'ops.aged.report.wizard',
    'ops.partner.ledger.wizard',
    'ops.cash.book.wizard',
    'ops.day.book.wizard',
    'ops.bank.book.wizard',
    'ops.asset.report.wizard',
    'ops.inventory.report.wizard',
    'ops.treasury.report.wizard',
    'ops.budget.vs.actual.wizard',
    'ops.consolidation.intelligence.wizard',
]


class OpsReportBridge(models.AbstractModel):
    """Universal bridge parser for all OPS corporate reports.

    This is the ONLY parser in the report engine. It connects
    ir.actions.report to wizard._get_report_data() via a thin bridge.

    The wizard owns the data logic. This bridge just:
    1. Validates the wizard model and record
    2. Calls wizard._get_report_data()
    3. Passes the data contract dict to the QWeb template
    """
    _name = 'report.ops_matrix_accounting.report_document'
    _description = 'OPS Universal Report Bridge'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Bridge between ir.actions.report and wizard data engine.

        Args:
            docids: List of wizard record IDs
            data: Dict with 'wizard_model' and optionally 'wizard_id'

        Returns:
            Dict with: doc_ids, doc_model, docs, data (contract), helpers, colors
        """
        data = data or {}
        wizard_model = data.get('wizard_model', self.env.context.get('active_model'))
        wizard_id = data.get('wizard_id') or (docids[0] if docids else self.env.context.get('active_id'))

        # Security: only allow whitelisted wizard models
        if wizard_model not in ALLOWED_WIZARD_MODELS:
            _logger.warning("Blocked report request for non-whitelisted model: %s", wizard_model)
            raise UserError(_("Invalid report configuration."))

        if not wizard_id:
            raise UserError(_("No report wizard record specified."))

        wizard = self.env[wizard_model].browse(int(wizard_id))
        if not wizard.exists():
            raise UserError(_("Report wizard record not found (ID: %s).") % wizard_id)

        # Wizard generates the data contract
        try:
            report_data = wizard._get_report_data()
        except Exception as e:
            _logger.error("Report data generation failed: %s", e, exc_info=True)
            raise UserError(_("Failed to generate report: %s") % str(e))

        return {
            'doc_ids': docids or [wizard_id],
            'doc_model': wizard_model,
            'docs': wizard,
            'data': report_data,
            'helpers': self.env['ops.report.helpers'],
            'colors': report_data.get('colors', {}),
            'meta': report_data.get('meta', {}),
        }
```

### File 3: Update `report/__init__.py`

Replace the placeholder with proper imports:
```python
# OPS Matrix Accounting - Report Engine v2
# Data contracts and bridge parser

from . import ops_report_contracts
from . import ops_report_bridge

# Excel infrastructure
from . import excel_styles
# from . import ops_excel_renderer  # Phase 5
```

### File 4: Minor update to `wizard/ops_base_report_wizard.py`

Read the current file first: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/wizard/ops_base_report_wizard.py`

Add these fields/methods IF THEY DON'T ALREADY EXIST (check first, don't duplicate):

1. `output_format` field:
```python
output_format = fields.Selection([
    ('pdf', 'PDF Report'),
    ('excel', 'Excel Export'),
    ('html', 'View in Browser'),
], string='Output Format', default='pdf')
```

2. `_get_report_shape()` abstract method:
```python
def _get_report_shape(self):
    """Return report shape: 'lines', 'hierarchy', or 'matrix'. Subclasses MUST implement."""
    raise NotImplementedError("Subclasses must implement _get_report_shape()")
```

3. Verify these fields exist on base (add if missing):
- `date_from = fields.Date(string='Start Date')`
- `date_to = fields.Date(string='End Date')`
- `as_of_date = fields.Date(string='As of Date')`
- `branch_ids = fields.Many2many('ops.branch', string='Branches')`
- `business_unit_ids = fields.Many2many('ops.business.unit', string='Business Units')`
- `matrix_filter_mode = fields.Selection([('any','Any'),('exact','Exact')], default='any', string='Matrix Filter Mode')`
- `target_move = fields.Selection([('posted','Posted Only'),('all','All Entries')], default='posted', string='Target Moves')`

4. Update `action_generate_report()` to dispatch based on `output_format`:
```python
def action_generate_report(self):
    """Main entry point — dispatches to PDF, Excel, or HTML."""
    self.ensure_one()
    self._validate_filters()

    if self.output_format == 'excel':
        return self.action_export_to_excel()
    elif self.output_format == 'html':
        return self.action_view_in_browser()
    else:
        report_data = self._get_report_data()
        self._log_report_generation(report_data)
        return self._return_report_action(report_data)
```

5. Add export permission check:
```python
def action_export_to_excel(self):
    """Excel export with permission check."""
    if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
        raise AccessError(_("You do not have permission to export data. Contact your administrator."))
    report_data = self._get_report_data()
    self._log_report_generation(report_data)
    # Excel generation will be implemented in Phase 5
    raise UserError(_("Excel export is being upgraded. Please use PDF for now."))
```

6. Add HTML view method:
```python
def action_view_in_browser(self):
    """Open report in browser HTML view."""
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    url = f'{base_url}/ops/report/html/{self._name}/{self.id}'
    return {
        'type': 'ir.actions.act_url',
        'url': url,
        'target': 'new',
    }
```

IMPORTANT: Read the existing file CAREFULLY before editing. Do NOT remove existing methods that work. Only ADD new methods and fields. If a method already exists with similar functionality, update it rather than creating a duplicate.

### Verification

After creating files, verify:
```bash
cd /opt/gemini_odoo19/addons/ops_matrix_accounting
python3 -c "from report.ops_report_contracts import *; print('Contracts OK:', ShapeAReport.__name__, ShapeBReport.__name__, ShapeCReport.__name__)"
echo "report/__init__.py:" && cat report/__init__.py
echo "Bridge parser:" && head -20 report/ops_report_bridge.py
```

## RULES
- Do NOT modify any model files other than ops_base_report_wizard.py
- Do NOT create any XML files in this phase
- Do NOT run odoo update
- Use proper Odoo conventions (fields.Date, not datetime.date)
- All strings must be translatable: `_("text")`
- No f-strings in SQL queries
- Include proper module docstrings and method docstrings
