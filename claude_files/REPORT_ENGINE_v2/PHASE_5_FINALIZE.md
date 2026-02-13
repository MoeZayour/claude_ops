# PHASE 5: Excel Renderer + Controller + Menus + Manifest + Test
# Run with: claude -p "$(cat PHASE_5_FINALIZE.md)"
# Prerequisite: Phases 0-4 completed
# Estimated: ~30 minutes

## CONTEXT
Final phase. Build the Excel renderer, HTML controller, update menus and manifest, then test.

Read FIRST:
1. Data contracts: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/ops_report_contracts.py`
2. Existing excel_styles.py for reference: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/excel_styles.py`
3. Current manifest: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/__manifest__.py`
4. Current menus: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/views/accounting_menus.xml`

## YOUR TASK

### File 1: `report/ops_excel_renderer.py` (~400 lines)

Generic Excel renderer that reads data contracts and produces .xlsx files.

```python
import io
import xlsxwriter
from odoo import models, api, _
from odoo.exceptions import UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class OpsExcelRenderer(models.AbstractModel):
    """Generic Excel renderer for all OPS report shapes.
    
    Reads the data contract dict and renders the appropriate shape.
    No report-specific code — fully driven by the contract.
    """
    _name = 'ops.excel.renderer'
    _description = 'OPS Generic Excel Renderer'

    def render(self, report_data):
        """Main entry point. Returns binary XLSX content.
        
        Args:
            report_data: Dict matching one of the 3 shape contracts
            
        Returns:
            bytes: XLSX file content
        """
        # Export permission check
        if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
            raise AccessError(_("You do not have permission to export data."))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        meta = report_data.get('meta', {})
        colors = report_data.get('colors', {})
        
        # Initialize formats from colors
        formats = self._create_formats(workbook, colors)
        
        shape = meta.get('shape', 'matrix')
        if shape == 'lines':
            self._render_lines(workbook, formats, report_data)
        elif shape == 'hierarchy':
            self._render_hierarchy(workbook, formats, report_data)
        else:
            self._render_matrix(workbook, formats, report_data)
        
        workbook.close()
        output.seek(0)
        return output.read()

    def _create_formats(self, workbook, colors):
        """Create all Excel formats from color config."""
        primary = colors.get('primary', '#5B6BBB')
        text_on_primary = colors.get('text_on_primary', '#FFFFFF')
        body_text = colors.get('body_text', '#1a1a1a')
        primary_light = colors.get('primary_light', '#edeef5')
        
        return {
            'title': workbook.add_format({
                'bold': True, 'font_size': 14, 'font_color': primary,
                'bottom': 2, 'bottom_color': primary,
            }),
            'company': workbook.add_format({
                'bold': True, 'font_size': 16, 'font_color': body_text,
            }),
            'header': workbook.add_format({
                'bold': True, 'font_size': 9, 'font_color': text_on_primary,
                'bg_color': primary, 'border': 1, 'border_color': primary,
                'text_wrap': True, 'valign': 'vcenter',
            }),
            'header_right': workbook.add_format({
                'bold': True, 'font_size': 9, 'font_color': text_on_primary,
                'bg_color': primary, 'border': 1, 'border_color': primary,
                'text_wrap': True, 'valign': 'vcenter', 'align': 'right',
            }),
            'detail': workbook.add_format({
                'font_size': 9, 'font_color': body_text,
                'border': 1, 'border_color': '#e5e7eb',
            }),
            'detail_number': workbook.add_format({
                'font_size': 9, 'font_color': body_text,
                'border': 1, 'border_color': '#e5e7eb',
                'num_format': '#,##0.00', 'align': 'right',
            }),
            'detail_negative': workbook.add_format({
                'font_size': 9, 'font_color': colors.get('danger', '#dc2626'),
                'border': 1, 'border_color': '#e5e7eb',
                'num_format': '#,##0.00', 'align': 'right',
            }),
            'group_header': workbook.add_format({
                'bold': True, 'font_size': 9, 'font_color': body_text,
                'bg_color': primary_light, 'border': 1, 'border_color': '#e5e7eb',
            }),
            'total': workbook.add_format({
                'bold': True, 'font_size': 9, 'font_color': body_text,
                'top': 2, 'top_color': primary,
                'num_format': '#,##0.00', 'align': 'right',
            }),
            'grand_total': workbook.add_format({
                'bold': True, 'font_size': 10, 'font_color': text_on_primary,
                'bg_color': primary,
                'num_format': '#,##0.00', 'align': 'right',
            }),
            'filter_label': workbook.add_format({
                'bold': True, 'font_size': 8, 'font_color': '#6b7280',
            }),
            'filter_value': workbook.add_format({
                'font_size': 8, 'font_color': '#6b7280',
            }),
            'section': workbook.add_format({
                'bold': True, 'font_size': 10, 'font_color': primary,
                'bottom': 1, 'bottom_color': primary,
            }),
        }

    def _write_report_header(self, ws, formats, meta, row=0):
        """Write company name, report title, dates, filters. Returns next row."""
        ws.write(row, 0, meta.get('company_name', ''), formats['company'])
        row += 1
        ws.write(row, 0, meta.get('report_title', 'Report'), formats['title'])
        row += 1
        
        # Date range
        if meta.get('date_from') and meta.get('date_to'):
            ws.write(row, 0, f"Period: {meta['date_from']} to {meta['date_to']}", formats['filter_value'])
        elif meta.get('as_of_date'):
            ws.write(row, 0, f"As of: {meta['as_of_date']}", formats['filter_value'])
        row += 1
        
        # Filters
        filters = meta.get('filters', {})
        if filters:
            for key, value in filters.items():
                display_val = ', '.join(str(v) for v in value) if isinstance(value, list) else str(value)
                ws.write(row, 0, f"{key.replace('_', ' ').title()}:", formats['filter_label'])
                ws.write(row, 1, display_val, formats['filter_value'])
                row += 1
        
        row += 1  # Blank row before data
        return row

    def _render_lines(self, workbook, formats, data):
        """Render Shape A (line-based) report."""
        # Implementation: iterate groups, write group headers, line rows, group totals, grand totals
        # Use visible_columns to determine which columns to include
        pass  # IMPLEMENT FULLY

    def _render_hierarchy(self, workbook, formats, data):
        """Render Shape B (hierarchy) report."""
        # Implementation: recursive section rendering with indentation
        # value_columns define the numeric columns
        pass  # IMPLEMENT FULLY

    def _render_matrix(self, workbook, formats, data):
        """Render Shape C (matrix/table) report."""
        # Implementation: dynamic columns from data['columns'], rows with styling
        pass  # IMPLEMENT FULLY
```

IMPORTANT: Fully implement all three render methods. Do NOT leave them as `pass`.
Reference the archived `excel_styles.py` for format patterns: `cat /opt/gemini_odoo19/addons/ops_matrix_accounting/report/excel_styles.py`

Then update `ops_base_report_wizard.py` `action_export_to_excel()`:
```python
def action_export_to_excel(self):
    if not self.env.user.has_group('ops_matrix_core.group_ops_can_export'):
        raise AccessError(_("You do not have permission to export data."))
    
    report_data = self._get_report_data()
    self._log_report_generation(report_data)
    
    renderer = self.env['ops.excel.renderer']
    xlsx_content = renderer.render(report_data)
    
    # Create attachment and return download action
    filename = f"{report_data.get('meta', {}).get('report_title', 'Report')}_{fields.Date.today()}.xlsx"
    attachment = self.env['ir.attachment'].create({
        'name': filename,
        'type': 'binary',
        'datas': base64.b64encode(xlsx_content),
        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    
    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment.id}?download=true',
        'target': 'self',
    }
```

### File 2: `controllers/ops_report_controller.py` (~150 lines)

New HTML view controller:

```python
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

# Whitelist of allowed wizard models
ALLOWED_MODELS = [
    'ops.gl.report.wizard', 'ops.tb.report.wizard', 'ops.pnl.report.wizard',
    'ops.bs.report.wizard', 'ops.cf.report.wizard', 'ops.aged.report.wizard',
    'ops.partner.ledger.wizard', 'ops.cash.book.wizard', 'ops.day.book.wizard',
    'ops.bank.book.wizard', 'ops.asset.report.wizard', 'ops.inventory.report.wizard',
    'ops.treasury.report.wizard', 'ops.budget.vs.actual.wizard',
    'ops.consolidation.intelligence.wizard',
]

# Map shape to template
SHAPE_TEMPLATES = {
    'lines': 'ops_matrix_accounting.ops_report_shape_lines',
    'hierarchy': 'ops_matrix_accounting.ops_report_shape_hierarchy',
    'matrix': 'ops_matrix_accounting.ops_report_shape_matrix',
}


class OpsReportController(http.Controller):

    @http.route('/ops/report/html/<string:wizard_model>/<int:wizard_id>', type='http', auth='user')
    def report_html_view(self, wizard_model, wizard_id, **kwargs):
        """Render any OPS report as HTML for browser viewing."""
        if wizard_model not in ALLOWED_MODELS:
            return request.not_found("Invalid report type")
        
        try:
            wizard = request.env[wizard_model].browse(wizard_id)
            if not wizard.exists():
                return request.not_found("Report not found")
            wizard.check_access_rights('read')
            wizard.check_access_rule('read')
        except AccessError as e:
            return request.render('http_routing.403', {'message': str(e)})
        
        try:
            report_data = wizard._get_report_data()
        except Exception as e:
            _logger.error("Report generation failed: %s", e, exc_info=True)
            return request.make_response(
                f'<html><body><h2>Error</h2><p>{e}</p></body></html>',
                headers=[('Content-Type', 'text/html')]
            )
        
        shape = report_data.get('meta', {}).get('shape', 'matrix')
        template = SHAPE_TEMPLATES.get(shape, SHAPE_TEMPLATES['matrix'])
        
        html_content = request.env['ir.qweb']._render(template, {
            'data': report_data,
            'meta': report_data.get('meta', {}),
            'colors': report_data.get('colors', {}),
            'helpers': request.env['ops.report.helpers'],
        })
        
        # Wrap in HTML chrome with print toolbar
        chrome = f'''<!DOCTYPE html>
<html>
<head><title>{report_data.get('meta', {}).get('report_title', 'Report')}</title>
<style>
    body {{ margin: 0; padding: 0; }}
    .ops-toolbar {{ background: #f3f4f6; padding: 8px 16px; display: flex; gap: 8px; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; z-index: 100; }}
    .ops-toolbar button {{ padding: 6px 14px; border: 1px solid #d1d5db; border-radius: 4px; background: white; cursor: pointer; font-size: 13px; }}
    .ops-toolbar button:hover {{ background: #f9fafb; }}
    .ops-content {{ padding: 16px; }}
    @media print {{ .ops-toolbar {{ display: none; }} }}
</style>
</head>
<body>
<div class="ops-toolbar">
    <button onclick="window.print()">🖨 Print</button>
    <button onclick="window.close()">✕ Close</button>
</div>
<div class="ops-content">{html_content}</div>
</body></html>'''
        
        return request.make_response(chrome, headers=[('Content-Type', 'text/html')])
```

Update `controllers/__init__.py`:
```python
from . import ops_report_controller
```

### File 3: Update `report/__init__.py`

Add Excel renderer:
```python
from . import ops_excel_renderer
```

### File 4: Update menus in `views/accounting_menus.xml`

Read the current file first. Find the report menu section and update menu items to point to the new wizard actions.

The menu structure should be:
```
Accounting > Reporting
├── Matrix Financial Intelligence
│   ├── General Ledger      → action_gl_wizard
│   ├── Trial Balance        → action_tb_wizard
│   ├── Profit & Loss        → action_pnl_wizard
│   ├── Balance Sheet        → action_bs_wizard
│   ├── Cash Flow Statement  → action_cf_wizard
│   ├── Aged Receivables     → action_aged_wizard (partner_type=customer default)
│   ├── Aged Payables        → action_aged_wizard (partner_type=vendor default)
│   ├── Partner Ledger       → action_partner_ledger_wizard
│   └── Statement of Account → action_partner_ledger_wizard (report_type=soa default)
├── Daily Books
│   ├── Cash Book            → existing action
│   ├── Day Book             → existing action
│   └── Bank Book            → existing action
├── Treasury Intelligence
│   ├── PDC Registry         → existing action
│   ├── PDC Maturity         → existing action
│   └── PDCs in Hand         → existing action
├── Asset Intelligence
│   ├── Asset Register       → existing action
│   ├── Depreciation Schedule → existing action
│   ├── Asset Disposal        → existing action
│   ├── Asset Forecast        → existing action
│   └── Asset Movement        → existing action
├── Inventory Intelligence
│   ├── Stock Valuation      → existing action
│   ├── Inventory Aging      → existing action
│   ├── Inventory Movement   → existing action
│   └── Negative Stock       → existing action
├── Consolidation Intelligence
│   └── [existing menus]
└── Budget Analysis
    └── Budget vs Actual     → existing action
```

For the new financial wizard actions, create menu items that open the wizard with appropriate defaults. Example for Aged Receivables:
```xml
<record id="action_aged_receivables_wizard" model="ir.actions.act_window">
    <field name="name">Aged Receivables</field>
    <field name="res_model">ops.aged.report.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <field name="context">{'default_partner_type': 'customer'}</field>
</record>
```

### File 5: Final `__manifest__.py` update

Read the current manifest. Ensure ALL new files are listed in correct order:

```python
'data': [
    # ... existing security, data files ...
    
    # Report Engine v2 — Templates (load order matters)
    'report/ops_report_base.xml',
    'report/ops_report_shape_lines.xml',
    'report/ops_report_shape_hierarchy.xml',
    'report/ops_report_shape_matrix.xml',
    'report/ops_report_actions.xml',
    'report/ops_report_configs.xml',
    
    # Keep existing
    'report/ops_corporate_report_layout.xml',
    'report/ops_report_invoice.xml',
    'report/ops_report_payment.xml',
    
    # Wizard views
    'wizard/ops_financial_wizard_views.xml',
    # ... other existing wizard view files ...
    
    # ... existing view files ...
],
```

Verify no archived files are still referenced:
```bash
grep "_archived_reports" __manifest__.py  # Should return nothing
```

### File 6: Module Upgrade + Test

NOW we update the module:
```bash
# Step 1: Clear asset cache
docker exec gemini_odoo19 bash -c 'PGPASSWORD=odoo psql -U odoo -d mz-db -h gemini_odoo19_db -c "DELETE FROM ir_attachment WHERE name LIKE '"'"'%assets%'"'"';"'

# Step 2: Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -u ops_matrix_accounting --stop-after-init 2>&1 | tail -50

# Step 3: Check for errors
docker logs gemini_odoo19 --tail 100 | grep -i "error\|traceback\|warning"

# Step 4: Restart
docker restart gemini_odoo19

# Step 5: Wait and check
sleep 10
docker logs gemini_odoo19 --tail 20
```

If there are errors, fix them iteratively:
1. Read the error message
2. Identify the file and line
3. Fix the issue
4. Re-run the update

Common issues to watch for:
- Missing XML IDs referenced in report actions
- Duplicate `_name` definitions (if old imports weren't fully cleaned)
- Missing fields on base wizard that children expect
- Incorrect `_inherit` references
- Missing ACL entries for new models

### Smoke Test Checklist

After successful module update, test via the web UI at https://ops.mz-im.com:

1. Log in as an accountant user
2. Navigate to Accounting > Reporting > Matrix Financial Intelligence
3. Open General Ledger wizard
4. Set date range, click Generate Report
5. Verify: report renders with company colors, filter bar shows, opening balance present, running balance per account
6. Test at least one report from each pillar:
   - Financial: GL
   - Daily: Cash Book
   - Treasury: PDC Registry
   - Asset: Asset Register
   - Inventory: Stock Valuation

For each, verify:
- [ ] Report renders without error
- [ ] Company header shows correct name and colors
- [ ] Filter bar displays active filters
- [ ] Data is correct (cross-check with a known transaction)
- [ ] Footer shows "Powered by OPS Framework" and page numbers

## RULES
- Fix ALL errors during module update — do not leave broken state
- If a wizard fails, comment it out in __init__.py temporarily and document the issue
- Keep the module installable — partial functionality is better than completely broken
- Log all issues found during testing for follow-up
