# OPS Framework - Corporate Reporting System Implementation Plan

**Document Version:** 1.0.0
**Created:** 2026-02-02
**Status:** Ready for Implementation
**Estimated Duration:** 8-10 days
**Target Completion:** 2026-02-12

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Project Scope](#project-scope)
3. [Phase 1: Foundation (COMPLETE)](#phase-1-foundation-complete)
4. [Phase 2: UI View Feature](#phase-2-ui-view-feature)
5. [Phase 3: Wizard UI Refactoring](#phase-3-wizard-ui-refactoring)
6. [Phase 4: Report Template Redesign](#phase-4-report-template-redesign)
7. [Phase 5: Excel Export Enhancement](#phase-5-excel-export-enhancement)
8. [Phase 6: Security Fixes](#phase-6-security-fixes)
9. [Phase 7: Cleanup](#phase-7-cleanup)
10. [Phase 8: Testing & Validation](#phase-8-testing--validation)
11. [Risk Assessment](#risk-assessment)
12. [Success Criteria](#success-criteria)
13. [Rollback Plan](#rollback-plan)

---

## 📊 EXECUTIVE SUMMARY

### Objective
Transform OPS Framework reporting from functional to **corporate-grade, board-ready** with consistent branding, professional styling, and enhanced user experience across all 16 official reports.

### Current State
- ✅ 31 wizards exist (8 reporting + 23 operational)
- ✅ Reports generate PDF/Excel outputs
- ✅ Dynamic account fetching (no hardcoded accounts)
- ✅ Security mixin with IT Admin Blindness
- ❌ Inconsistent visual design across reports
- ❌ No in-browser preview (must print/export)
- ❌ Daily books missing security controls
- ❌ Duplicate/deprecated files exist

### Target State
- ✅ All 16 reports styled per HTML Balance Sheet sample
- ✅ Consistent corporate branding with company colors
- ✅ UI View feature (browser preview with toolbar)
- ✅ Corporate-branded Excel exports
- ✅ Wizard forms styled per OPS Theme Guide
- ✅ Security consistent across all reports
- ✅ Clean codebase with deprecated files archived

### Impact
**Users:** Board members, executives, auditors, finance teams
**Quality Level:** Board presentation ready
**Compliance:** SOX, IFRS, IAS standards maintained

---

## 🎯 PROJECT SCOPE

### In Scope: 16 Official Corporate Reports

#### Financial Intelligence (9 Reports)
1. Balance Sheet (IAS 1 format)
2. Profit & Loss Statement
3. Cash Flow Statement
4. Trial Balance
5. General Ledger
6. Aged Receivables
7. Aged Payables
8. Partner Ledger
9. Statement of Account

#### Treasury Intelligence (3 Reports)
10. PDC Registry
11. PDC Maturity Analysis
12. PDCs in Hand

#### Asset Intelligence (2 Reports)
13. Fixed Asset Register
14. Depreciation Schedule

#### Inventory Intelligence (2 Reports)
15. Stock Valuation
16. Inventory Aging

### Out of Scope
- 23 operational wizards (no visual changes)
- Dashboard redesign (separate project)
- Theme changes outside reporting module
- New features or functionality additions

---

## ✅ PHASE 1: FOUNDATION (COMPLETE)

### Status: 100% Complete

#### Deliverables Created
✅ **Corporate SCSS Stylesheet**
- File: `ops_matrix_accounting/static/src/scss/ops_corporate_reports.scss`
- Lines: 652
- Features: wkhtmltopdf compatible, print-optimized, BEM naming

✅ **Shared QWeb Components**
- File: `ops_matrix_accounting/report/components/ops_corporate_report_components.xml`
- Lines: 506
- Components: Header, title, filter bar, notes, footer, tables, badges, KPI cards

✅ **Python Report Helpers**
- File: `ops_matrix_accounting/models/ops_report_helpers.py`
- Lines: 557
- Functions: Color generation, formatting, classification, context preparation

✅ **Module Registration**
- Updated: `models/__init__.py`
- Verified: `__manifest__.py` includes all new files

---

## 🔧 PHASE 2: UI VIEW FEATURE

**Duration:** 1 day
**Priority:** P1 (High)
**Dependencies:** Phase 1 complete

### Overview
Add browser preview functionality so users can view reports in their browser before printing or exporting. Includes toolbar with Print/Export/Close actions.

---

### Task 2.1: Add action_view_report() to Base Wizard

**File:** `addons/ops_matrix_accounting/wizard/ops_base_report_wizard.py`

**Location:** After `get_color_scheme()` method (line 702)

**Code to Add:**

```python
    # =========================================================================
    # UI VIEW FEATURE
    # =========================================================================

    def action_view_report(self):
        """
        Open report in UI View mode (browser preview with toolbar).

        Returns:
            dict: Action to open report HTML in new tab
        """
        self.ensure_one()

        # Run validation
        validation_result = self._validate_filters()
        if isinstance(validation_result, dict) and 'warning' in validation_result:
            return validation_result

        # Security check
        engine_name = self._get_engine_name()
        if engine_name:
            self._check_intelligence_access(engine_name)

        # Get report template name
        template_name = self._get_report_template_xmlid()

        # Return action to open in new tab with controller
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f'{base_url}/ops/report/html/{template_name}?wizard_id={self.id}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """
        Get the XML ID of the report template for this wizard.
        Must be overridden by child classes.

        Returns:
            str: XML ID of report template (e.g., 'ops_matrix_accounting.report_general_ledger')
        """
        raise NotImplementedError(
            "Wizards must implement _get_report_template_xmlid() to use UI View feature"
        )
```

**Testing:**
```python
# Test in Odoo shell
wizard = env['ops.general.ledger.wizard.enhanced'].create({
    'company_id': env.company.id,
    'date_from': '2026-01-01',
    'date_to': '2026-01-31',
    'report_type': 'gl',
})
result = wizard.action_view_report()
print(result)  # Should return act_url action
```

---

### Task 2.2: Create Report Controller

**File:** `addons/ops_matrix_accounting/controllers/ops_report_controller.py` (NEW)

**Full Content:**

```python
# -*- coding: utf-8 -*-
"""
OPS Framework - Report Web Controller
======================================
Handles HTML report rendering for UI View mode.
"""

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)


class OpsReportController(http.Controller):
    """Web controller for OPS corporate report HTML rendering"""

    @http.route('/ops/report/html/<string:template_xmlid>', type='http', auth='user')
    def report_html_view(self, template_xmlid, wizard_id=None, **kwargs):
        """
        Render report as HTML for UI View mode with toolbar.

        Args:
            template_xmlid (str): Full XML ID of report template
            wizard_id (int): Wizard record ID

        Returns:
            Response: HTML content with OPS corporate styling
        """
        if not wizard_id:
            return request.not_found("Missing wizard_id parameter")

        try:
            wizard_id = int(wizard_id)
        except (ValueError, TypeError):
            return request.not_found("Invalid wizard_id")

        # Get wizard model from template mapping
        wizard_model = self._get_wizard_model(template_xmlid)
        if not wizard_model:
            return request.not_found(f"Unknown template: {template_xmlid}")

        # Verify wizard exists and user has access
        try:
            wizard = request.env[wizard_model].browse(wizard_id)
            if not wizard.exists():
                return request.not_found("Wizard record not found")

            # Check access rights
            wizard.check_access_rights('read')
            wizard.check_access_rule('read')

        except AccessError as e:
            return request.render('http_routing.403', {'message': str(e)})

        # Validate wizard filters
        validation_result = wizard._validate_filters()
        if isinstance(validation_result, dict) and 'warning' in validation_result:
            return request.render('ops_matrix_accounting.report_validation_error', {
                'error_message': validation_result.get('warning', {}).get('message', 'Validation failed'),
            })

        # Security check (IT Admin Blindness)
        try:
            engine_name = wizard._get_engine_name()
            if engine_name:
                wizard._check_intelligence_access(engine_name)
        except AccessError as e:
            return request.render('http_routing.403', {'message': str(e)})

        # Generate report data
        try:
            report_data = wizard._get_report_data()
        except Exception as e:
            _logger.error(f"Error generating report data: {e}", exc_info=True)
            return request.render('ops_matrix_accounting.report_generation_error', {
                'error_message': str(e),
            })

        # Get report helpers for context
        helpers = request.env['ops.report.helpers']
        context = helpers.get_report_context(wizard, report_data)
        context['ui_view_mode'] = True
        context['wizard_id'] = wizard_id
        context['template_xmlid'] = template_xmlid

        # Render report template
        try:
            # Extract module and template name from XML ID
            if '.' in template_xmlid:
                module, template_name = template_xmlid.split('.', 1)
                full_template_id = f'{module}.{template_name}'
            else:
                full_template_id = template_xmlid

            html_content = request.env['ir.qweb']._render(full_template_id, context)
        except Exception as e:
            _logger.error(f"Error rendering template {template_xmlid}: {e}", exc_info=True)
            return request.render('ops_matrix_accounting.report_render_error', {
                'error_message': str(e),
                'template_xmlid': template_xmlid,
            })

        # Wrap in UI View container with toolbar
        wrapped_html = self._wrap_ui_view(html_content, wizard, template_xmlid)

        return request.make_response(wrapped_html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])

    def _wrap_ui_view(self, html_content, wizard, template_xmlid):
        """
        Wrap report HTML in UI View container with toolbar.

        Args:
            html_content (str): Rendered report HTML
            wizard: Wizard record
            template_xmlid (str): Template XML ID

        Returns:
            str: Complete HTML page with toolbar
        """
        report_title = wizard.report_title if hasattr(wizard, 'report_title') else 'OPS Report'

        # Get base URL for assets
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        toolbar_html = f"""
        <div class="ops-report-toolbar" style="display: flex; justify-content: flex-end; gap: 12px;
             margin-bottom: 16px; padding: 12px; background: white; border-radius: 8px;
             box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <button onclick="window.print()"
                    style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;
                           background: #5B6BBB; color: white; border: none; border-radius: 6px;
                           font-size: 9pt; font-weight: 500; cursor: pointer;">
                <i class="fa fa-print"></i> Print PDF
            </button>
            <a href="/ops/report/excel/{template_xmlid}?wizard_id={wizard.id}"
               style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;
                      background: #16a34a; color: white; border: none; border-radius: 6px;
                      font-size: 9pt; font-weight: 500; text-decoration: none;">
                <i class="fa fa-file-excel-o"></i> Export Excel
            </a>
            <button onclick="window.close()"
                    style="display: flex; align-items: center; gap: 6px; padding: 8px 16px;
                           background: #6b7280; color: white; border: none; border-radius: 6px;
                           font-size: 9pt; font-weight: 500; cursor: pointer;">
                <i class="fa fa-times"></i> Close
            </button>
        </div>
        """

        wrapper = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report_title} - OPS Framework</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
            <link rel="stylesheet" href="{base_url}/ops_matrix_accounting/static/src/scss/ops_corporate_reports.scss"/>
            <style>
                body {{
                    margin: 0;
                    background: #f5f5f5;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                }}
                .ops-report-ui-view {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 24px;
                }}
                .ops-corporate-report {{
                    background: white;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    padding: 40px;
                }}
                @media print {{
                    body {{
                        background: white;
                    }}
                    .ops-report-toolbar {{
                        display: none !important;
                    }}
                    .ops-report-ui-view {{
                        padding: 0;
                        max-width: none;
                    }}
                    .ops-corporate-report {{
                        box-shadow: none;
                        border-radius: 0;
                        padding: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="ops-report-ui-view">
                {toolbar_html}
                {html_content}
            </div>
        </body>
        </html>
        """
        return wrapper

    def _get_wizard_model(self, template_xmlid):
        """
        Map report template XML ID to wizard model.

        Args:
            template_xmlid (str): Report template XML ID

        Returns:
            str: Wizard model name or None
        """
        # Extract template name from XML ID
        template_name = template_xmlid.split('.')[-1] if '.' in template_xmlid else template_xmlid

        # Mapping of report templates to wizard models
        mapping = {
            # Financial Intelligence (Enhanced GL Wizard)
            'report_general_ledger': 'ops.general.ledger.wizard.enhanced',
            'report_trial_balance': 'ops.general.ledger.wizard.enhanced',
            'report_profit_loss': 'ops.general.ledger.wizard.enhanced',
            'report_balance_sheet': 'ops.general.ledger.wizard.enhanced',
            'report_cash_flow': 'ops.general.ledger.wizard.enhanced',
            'report_aged_receivable': 'ops.general.ledger.wizard.enhanced',
            'report_aged_payable': 'ops.general.ledger.wizard.enhanced',
            'report_partner_ledger': 'ops.general.ledger.wizard.enhanced',
            'report_statement_account': 'ops.general.ledger.wizard.enhanced',

            # Treasury Intelligence
            'report_pdc_registry': 'ops.treasury.report.wizard',
            'report_pdc_maturity': 'ops.treasury.report.wizard',
            'report_pdc_on_hand': 'ops.treasury.report.wizard',

            # Asset Intelligence
            'report_asset_register': 'ops.asset.report.wizard',
            'report_depreciation_schedule': 'ops.asset.report.wizard',
            'report_asset_disposal': 'ops.asset.report.wizard',

            # Inventory Intelligence
            'report_stock_valuation': 'ops.inventory.report.wizard',
            'report_inventory_aging': 'ops.inventory.report.wizard',
            'report_inventory_movement': 'ops.inventory.report.wizard',
            'report_negative_stock': 'ops.inventory.report.wizard',

            # Daily Books
            'report_cash_book': 'ops.cash.book.wizard',
            'report_day_book': 'ops.day.book.wizard',
            'report_bank_book': 'ops.bank.book.wizard',
        }

        return mapping.get(template_name)

    @http.route('/ops/report/excel/<string:template_xmlid>', type='http', auth='user')
    def report_excel_download(self, template_xmlid, wizard_id=None, **kwargs):
        """
        Generate and download Excel export for report.

        Args:
            template_xmlid (str): Report template XML ID
            wizard_id (int): Wizard record ID

        Returns:
            Response: Excel file download
        """
        if not wizard_id:
            return request.not_found("Missing wizard_id parameter")

        try:
            wizard_id = int(wizard_id)
        except (ValueError, TypeError):
            return request.not_found("Invalid wizard_id")

        wizard_model = self._get_wizard_model(template_xmlid)
        if not wizard_model:
            return request.not_found(f"Unknown template: {template_xmlid}")

        try:
            wizard = request.env[wizard_model].browse(wizard_id)
            if not wizard.exists():
                return request.not_found("Wizard record not found")

            # Check access
            wizard.check_access_rights('read')

            # Call wizard's Excel export method
            if hasattr(wizard, 'action_export_excel'):
                return wizard.action_export_excel()
            else:
                raise UserError("Excel export not available for this report")

        except Exception as e:
            _logger.error(f"Error generating Excel export: {e}", exc_info=True)
            return request.not_found(str(e))
```

**Register Controller:**

Edit `addons/ops_matrix_accounting/controllers/__init__.py`:

```python
from . import ops_report_controller
```

If `controllers/` directory doesn't exist:
```bash
mkdir -p addons/ops_matrix_accounting/controllers
touch addons/ops_matrix_accounting/controllers/__init__.py
```

Edit `addons/ops_matrix_accounting/__init__.py`:

```python
from . import controllers  # Add this line
from . import models
from . import wizard
from . import report
```

---

### Task 2.3: Implement _get_report_template_xmlid() in Each Wizard

**File:** `addons/ops_matrix_accounting/wizard/ops_general_ledger_wizard_enhanced.py`

**Add after class definition (around line 100):**

```python
    def _get_report_template_xmlid(self):
        """Return XML ID of report template based on report_type"""
        self.ensure_one()

        template_mapping = {
            'gl': 'ops_matrix_accounting.report_general_ledger',
            'tb': 'ops_matrix_accounting.report_trial_balance',
            'pl': 'ops_matrix_accounting.report_profit_loss',
            'bs': 'ops_matrix_accounting.report_balance_sheet',
            'cf': 'ops_matrix_accounting.report_cash_flow',
            'aged_receivable': 'ops_matrix_accounting.report_aged_receivable',
            'aged_payable': 'ops_matrix_accounting.report_aged_payable',
            'partner': 'ops_matrix_accounting.report_partner_ledger',
            'statement': 'ops_matrix_accounting.report_statement_account',
        }

        return template_mapping.get(self.report_type, 'ops_matrix_accounting.report_general_ledger')
```

**Repeat for other wizards:**

- `ops_treasury_report_wizard.py` - map treasury_report_type to templates
- `ops_asset_report_wizard.py` - map asset_report_type to templates
- `ops_inventory_report_wizard.py` - map inventory_report_type to templates
- Daily book wizards - return their specific template IDs

---

### Task 2.4: Add "View Report" Buttons to Wizard Forms

**Pattern for all wizard views:**

```xml
<footer>
    <button name="action_view_report" string="View Report" type="object"
            class="btn-primary" icon="fa-eye"
            help="Open report in browser for preview"/>
    <button name="action_generate_report" string="Print PDF" type="object"
            class="btn-secondary" icon="fa-print"
            help="Generate PDF for printing or download"/>
    <button name="action_export_excel" string="Export Excel" type="object"
            class="btn-success" icon="fa-file-excel-o"
            help="Export data to Excel spreadsheet"
            attrs="{'invisible': [('excel_available', '=', False)]}"/>
    <button name="action_save_template" string="Save as Template" type="object"
            class="btn-link" icon="fa-save"
            help="Save current filters as reusable template"/>
    <button string="Cancel" class="btn-default" special="cancel"/>
</footer>
```

**Files to Update:**

1. `views/ops_general_ledger_wizard_enhanced_views.xml`
2. `wizard/ops_treasury_report_wizard_views.xml`
3. `wizard/ops_asset_report_wizard_views.xml`
4. `views/ops_inventory_report_views.xml`
5. `wizard/ops_balance_sheet_wizard_views.xml`
6. `views/ops_daily_reports_views.xml`

---

### Phase 2 Testing Checklist

```
□ Restart Odoo: docker restart gemini_odoo19
□ Update module: -u ops_matrix_accounting
□ Open Financial Intelligence wizard
□ Click "View Report" button
□ Verify browser opens new tab
□ Verify report displays with toolbar
□ Click "Print PDF" - verify print dialog
□ Click "Export Excel" - verify download (if implemented)
□ Click "Close" - verify tab closes
□ Test IT Admin user - verify AccessError
□ Test branch-restricted user - verify filtering
□ Repeat for all 8 wizard types
```

---

## 🎨 PHASE 3: WIZARD UI REFACTORING

**Duration:** 1 day
**Priority:** P1 (High)
**Dependencies:** None (can run parallel to Phase 2)

### Overview
Apply OPS Theme styling to all 8 wizard forms for consistent, professional UI matching the theme guide.

---

### Design Principles (from OPS_THEME_GUIDEBOOK.md)

1. **Card-based layout** - Group related fields in `<group>` elements
2. **Clean labels** - Clear, concise field labels
3. **Smart defaults** - Pre-populate common values
4. **Progressive disclosure** - Hide advanced options in expandable sections
5. **Visual hierarchy** - Important fields prominent, optional fields subtle
6. **Inline help** - Use `help` attribute for guidance
7. **Color coding** - Use `decoration-*` for status indication

---

### Task 3.1: Financial Intelligence Wizard

**File:** `views/ops_general_ledger_wizard_enhanced_views.xml`

**Current Issues:**
- Fields not grouped logically
- No visual separation between sections
- Advanced options always visible
- No preview stats

**Updated Structure:**

```xml
<record id="view_ops_general_ledger_wizard_enhanced_form" model="ir.ui.view">
    <field name="name">ops.general.ledger.wizard.enhanced.form</field>
    <field name="model">ops.general.ledger.wizard.enhanced</field>
    <field name="arch" type="xml">
        <form string="Financial Intelligence">
            <!-- Template Quick Start (if templates exist) -->
            <group name="template_section" string="📁 Quick Start"
                   attrs="{'invisible': [('template_count', '=', 0)]}">
                <field name="template_count" invisible="1"/>
                <field name="report_template_id"
                       placeholder="Load a saved template..."
                       options="{'no_create': True}"
                       help="Load previously saved filter configuration"/>
            </group>

            <!-- Report Type Selection -->
            <group name="report_type_section" string="📊 Report Selection">
                <field name="report_type" widget="radio"
                       options="{'horizontal': false}"
                       help="Select the financial report type to generate"/>
            </group>

            <!-- Period Selection -->
            <group name="period_section" string="📅 Reporting Period">
                <group>
                    <field name="date_from"
                           attrs="{'required': [('report_type', 'not in', ['bs'])]}"
                           help="Start date of reporting period"/>
                    <field name="date_to"
                           attrs="{'required': [('report_type', 'not in', ['bs'])]}"
                           help="End date of reporting period"/>
                </group>
                <group>
                    <field name="as_of_date"
                           attrs="{'invisible': [('report_type', '!=', 'bs')],
                                   'required': [('report_type', '=', 'bs')]}"
                           help="Balance sheet cutoff date"/>
                    <field name="comparison_date"
                           attrs="{'invisible': [('report_type', 'not in', ['bs', 'pl'])]}"
                           help="Prior period for comparative column"/>
                </group>
            </group>

            <!-- Scope Filters -->
            <group name="scope_section" string="🎯 Scope &amp; Filters">
                <group>
                    <field name="company_id" options="{'no_create': True}"
                           help="Company to report on"/>
                    <field name="branch_ids" widget="many2many_tags"
                           options="{'no_create': True, 'color_field': 'color'}"
                           help="Filter by specific branches (leave empty for all)"/>
                    <field name="business_unit_ids" widget="many2many_tags"
                           options="{'no_create': True}"
                           help="Filter by business units"/>
                </group>
                <group>
                    <field name="target_move" widget="radio"
                           help="Include all entries or posted only"/>
                    <field name="account_ids" widget="many2many_tags"
                           attrs="{'invisible': [('report_type', 'in', ['bs', 'pl', 'cf'])]}"
                           help="Limit to specific accounts (leave empty for all)"/>
                    <field name="partner_ids" widget="many2many_tags"
                           attrs="{'invisible': [('report_type', 'not in', ['partner', 'statement', 'aged_receivable', 'aged_payable'])]}"
                           help="Filter by specific partners"/>
                </group>
            </group>

            <!-- Advanced Options (Collapsible) -->
            <notebook>
                <page string="⚙️ Display Options" name="display_options">
                    <group>
                        <group>
                            <field name="include_initial_balance"
                                   attrs="{'invisible': [('report_type', 'not in', ['gl', 'partner'])]}"
                                   help="Show opening balance for the period"/>
                            <field name="display_account"
                                   attrs="{'invisible': [('report_type', 'in', ['bs', 'pl', 'cf'])]}"
                                   help="Filter accounts by activity"/>
                            <field name="report_format"
                                   attrs="{'invisible': [('report_type', 'in', ['bs', 'pl', 'cf'])]}"
                                   help="Level of detail in output"/>
                        </group>
                        <group>
                            <field name="show_partner_details"
                                   attrs="{'invisible': [('report_type', 'not in', ['gl', 'tb'])]}"
                                   help="Include partner breakdown"/>
                            <field name="show_analytic"
                                   attrs="{'invisible': [('report_type', 'not in', ['gl', 'tb'])]}"
                                   help="Include analytic account details"/>
                            <field name="hierarchy_view"
                                   attrs="{'invisible': [('report_type', 'not in', ['bs', 'pl'])]}"
                                   help="Show account hierarchy or flat list"/>
                        </group>
                    </group>
                </page>

                <page string="📈 Aging Settings" name="aging_settings"
                      attrs="{'invisible': [('report_type', 'not in', ['aged_receivable', 'aged_payable'])]}">
                    <group>
                        <group>
                            <field name="period_length" help="Days per aging bucket"/>
                            <field name="aging_date" help="Cutoff date for age calculation"/>
                        </group>
                        <group>
                            <field name="show_original_currency" help="Display in invoice currency"/>
                            <field name="group_by_partner" help="Separate section per partner"/>
                        </group>
                    </group>
                </page>
            </notebook>

            <!-- Preview Section -->
            <group name="preview_section" string="👁️ Preview">
                <field name="record_count" readonly="1"
                       help="Estimated number of records"/>
                <field name="filter_summary" readonly="1" colspan="2"
                       widget="text"
                       help="Human-readable summary of applied filters"/>
            </group>

            <!-- Action Buttons -->
            <footer>
                <button name="action_view_report" string="View Report" type="object"
                        class="btn-primary" icon="fa-eye"/>
                <button name="action_generate_report" string="Print PDF" type="object"
                        class="btn-secondary" icon="fa-print"/>
                <button name="action_export_excel" string="Export Excel" type="object"
                        class="btn-success" icon="fa-file-excel-o"/>
                <button name="action_save_template" string="Save Template" type="object"
                        class="btn-link" icon="fa-save"/>
                <button string="Cancel" class="btn-default" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

### Task 3.2-3.8: Other Wizard Forms

Apply same pattern to:

| # | File | Wizard | Key Sections |
|---|------|--------|-------------|
| 3.2 | `wizard/ops_treasury_report_wizard_views.xml` | Treasury Intelligence | Report type, date range, bank/journal filters, status filters |
| 3.3 | `wizard/ops_asset_report_wizard_views.xml` | Asset Intelligence | Report type, cutoff date, category filters, status filters |
| 3.4 | `views/ops_inventory_report_views.xml` | Inventory Intelligence | Report type, valuation date, location/category filters |
| 3.5 | `wizard/ops_balance_sheet_wizard_views.xml` | Balance Sheet | Cutoff date, comparison date, hierarchy options |
| 3.6 | `views/ops_daily_reports_views.xml` | Cash Book | Date, journal selection |
| 3.7 | `views/ops_daily_reports_views.xml` | Day Book | Date, journal filters |
| 3.8 | `views/ops_daily_reports_views.xml` | Bank Book | Date, bank journal selection |

**Common Structure for All:**
1. Template quick start (if applicable)
2. Report/type selection
3. Date/period selection
4. Scope filters (company, branch, BU)
5. Type-specific filters (in expandable section)
6. Display options (in notebook/page)
7. Preview stats
8. Action buttons

---

### Phase 3 Testing Checklist

```
□ Update module: -u ops_matrix_accounting
□ Open each wizard from menu
□ Verify clean, card-based layout
□ Verify emoji icons display correctly
□ Verify collapsible sections work
□ Verify field visibility rules work
□ Verify help text appears on hover
□ Test template loading
□ Verify preview stats update
□ Test on mobile/tablet viewport
```

---

## 📄 PHASE 4: REPORT TEMPLATE REDESIGN

**Duration:** 3-4 days
**Priority:** P0 (Critical)
**Dependencies:** Phase 1 complete

### Overview
Redesign all 16 report QWeb templates to use shared corporate components with consistent styling matching the HTML Balance Sheet sample.

---

### Master Template Pattern

Every report MUST follow this structure:

```xml
<template id="report_[name]_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-set="company" t-value="doc.company_id or env.company"/>

            <div class="ops-corporate-report">
                <!-- Corporate Header -->
                <t t-call="ops_matrix_accounting.report_corporate_header"/>

                <!-- Report Title -->
                <t t-call="ops_matrix_accounting.report_corporate_title">
                    <t t-set="report_title" t-value="doc.report_title or 'Financial Report'"/>
                    <t t-set="report_pillar" t-value="'Financial Intelligence'"/>
                    <t t-set="date_from" t-value="doc.date_from"/>
                    <t t-set="date_to" t-value="doc.date_to"/>
                </t>

                <!-- Filter Info Bar -->
                <t t-call="ops_matrix_accounting.report_filter_bar"/>

                <!-- REPORT-SPECIFIC CONTENT -->
                <!-- Use shared section headers, tables, and formatting -->

                <!-- Notes Section -->
                <t t-call="ops_matrix_accounting.report_notes_section"/>

                <!-- Corporate Footer -->
                <t t-call="ops_matrix_accounting.report_corporate_footer"/>
            </div>
        </t>
    </t>
</template>
```

---

### Task 4.1: General Ledger Report

**File:** `report/ops_general_ledger_template.xml`

**Sections:**
1. Corporate header (shared)
2. Title: "General Ledger"
3. Filter bar (shared)
4. Account sections with:
   - Section header per account (with account code + name)
   - Transaction table with columns: Date, Journal, Reference, Partner, Description, Debit, Credit, Balance
   - Running balance column
   - Subtotal per account
5. Grand total (all accounts)
6. Balance verification badge (DR = CR)
7. Notes section (shared)
8. Footer (shared)

**Table Structure:**

```xml
<!-- Account Section Loop -->
<t t-foreach="accounts" t-as="account">
    <!-- Account Header -->
    <t t-call="ops_matrix_accounting.section_header_financial">
        <t t-set="section_title" t-value="'%s - %s' % (account['code'], account['name'])"/>
    </t>

    <!-- Transaction Table -->
    <table class="ops-corp-table" style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
        <thead>
            <tr style="border-bottom: 2px solid #1e293b;">
                <th style="text-align: left;">Date</th>
                <th style="text-align: left;">Journal</th>
                <th style="text-align: left;">Reference</th>
                <th style="text-align: left;">Partner</th>
                <th style="text-align: left;">Description</th>
                <th style="text-align: right;">Debit</th>
                <th style="text-align: right;">Credit</th>
                <th style="text-align: right;">Balance</th>
            </tr>
        </thead>
        <tbody>
            <!-- Opening Balance Row -->
            <t t-if="account.get('initial_balance')">
                <tr style="background-color: #f8fafc;">
                    <td colspan="5" style="padding: 6px 10px; font-weight: 600;">
                        Opening Balance
                    </td>
                    <td style="text-align: right; padding: 6px 10px;">-</td>
                    <td style="text-align: right; padding: 6px 10px;">-</td>
                    <td style="text-align: right; padding: 6px 10px; font-weight: 600;">
                        <t t-call="ops_matrix_accounting.format_corporate_amount">
                            <t t-set="value" t-value="account['initial_balance']"/>
                        </t>
                    </td>
                </tr>
            </t>

            <!-- Transaction Rows -->
            <t t-foreach="account.get('lines', [])" t-as="line">
                <tr>
                    <td style="padding: 6px 10px;">
                        <t t-esc="line['date'].strftime('%b %d, %Y')"/>
                    </td>
                    <td style="padding: 6px 10px;">
                        <t t-esc="line['journal']"/>
                    </td>
                    <td style="padding: 6px 10px;">
                        <t t-esc="line['reference'] or ''"/>
                    </td>
                    <td style="padding: 6px 10px;">
                        <t t-esc="line['partner'] or ''"/>
                    </td>
                    <td style="padding: 6px 10px;">
                        <t t-esc="line['description'] or line['name']"/>
                    </td>
                    <td style="text-align: right; padding: 6px 10px; font-family: Consolas, Monaco, monospace;">
                        <t t-if="line['debit'] > 0">
                            <t t-call="ops_matrix_accounting.format_corporate_amount">
                                <t t-set="value" t-value="line['debit']"/>
                            </t>
                        </t>
                        <t t-else=""><span style="color: #94a3b8;">-</span></t>
                    </td>
                    <td style="text-align: right; padding: 6px 10px; font-family: Consolas, Monaco, monospace;">
                        <t t-if="line['credit'] > 0">
                            <t t-call="ops_matrix_accounting.format_corporate_amount">
                                <t t-set="value" t-value="line['credit']"/>
                            </t>
                        </t>
                        <t t-else=""><span style="color: #94a3b8;">-</span></t>
                    </td>
                    <td style="text-align: right; padding: 6px 10px; font-family: Consolas, Monaco, monospace; font-weight: 500;">
                        <t t-call="ops_matrix_accounting.format_corporate_amount">
                            <t t-set="value" t-value="line['balance']"/>
                        </t>
                    </td>
                </tr>
            </t>

            <!-- Account Subtotal -->
            <tr class="ops-subtotal-row" style="border-top: 1px solid #e2e8f0; background-color: #f8fafc;">
                <td colspan="5" style="padding: 8px 10px; font-weight: 600; color: #475569;">
                    Total <t t-esc="account['code']"/>
                </td>
                <td style="text-align: right; padding: 8px 10px; font-weight: 600; font-family: Consolas, Monaco, monospace;">
                    <t t-call="ops_matrix_accounting.format_corporate_amount">
                        <t t-set="value" t-value="account['total_debit']"/>
                    </t>
                </td>
                <td style="text-align: right; padding: 8px 10px; font-weight: 600; font-family: Consolas, Monaco, monospace;">
                    <t t-call="ops_matrix_accounting.format_corporate_amount">
                        <t t-set="value" t-value="account['total_credit']"/>
                    </t>
                </td>
                <td style="text-align: right; padding: 8px 10px; font-weight: 600; font-family: Consolas, Monaco, monospace;">
                    <t t-call="ops_matrix_accounting.format_corporate_amount">
                        <t t-set="value" t-value="account['ending_balance']"/>
                    </t>
                </td>
            </tr>
        </tbody>
    </table>
</t>

<!-- Grand Total -->
<table class="ops-corp-table" style="width: 100%; border-collapse: collapse; margin-top: 20px;">
    <tr class="ops-total-row" style="border-top: 2px solid #1e293b; border-bottom: 3px double #1e293b; background-color: #f1f5f9;">
        <td colspan="5" style="padding: 10px; font-size: 11px; font-weight: 700; text-transform: uppercase;">
            GRAND TOTAL
        </td>
        <td style="text-align: right; padding: 10px; font-weight: 700; font-family: Consolas, Monaco, monospace;">
            <t t-call="ops_matrix_accounting.format_corporate_amount">
                <t t-set="value" t-value="grand_total_debit"/>
            </t>
        </td>
        <td style="text-align: right; padding: 10px; font-weight: 700; font-family: Consolas, Monaco, monospace;">
            <t t-call="ops_matrix_accounting.format_corporate_amount">
                <t t-set="value" t-value="grand_total_credit"/>
            </t>
        </td>
        <td style="text-align: right; padding: 10px; font-weight: 700; font-family: Consolas, Monaco, monospace;">
            <t t-call="ops_matrix_accounting.format_corporate_amount">
                <t t-set="value" t-value="grand_total_balance"/>
            </t>
        </td>
    </tr>
</table>

<!-- Balance Check -->
<t t-call="ops_matrix_accounting.balance_check_badge">
    <t t-set="is_balanced" t-value="abs(grand_total_debit - grand_total_credit) &lt; 0.01"/>
    <t t-set="difference" t-value="grand_total_debit - grand_total_credit"/>
</t>
```

---

### Task 4.2-4.16: Remaining Reports

Apply same pattern with report-specific content:

| # | Report | File | Special Requirements |
|---|--------|------|---------------------|
| 4.2 | Trial Balance | `ops_financial_report_template.xml` | Two-column (DR/CR), balance check badge |
| 4.3 | Profit & Loss | `ops_financial_report_template.xml` | Revenue/Expense sections, GP/OP/NP subtotals, margin % |
| 4.4 | Balance Sheet | `ops_balance_sheet_template.xml` | Asset/Liability/Equity sections, balance equation |
| 4.5 | Cash Flow | `ops_financial_report_template.xml` | Operating/Investing/Financing sections |
| 4.6 | Aged Receivables | `ops_financial_report_template.xml` | Aging buckets with colors, total due |
| 4.7 | Aged Payables | `ops_financial_report_template.xml` | Aging buckets with colors, total payable |
| 4.8 | Partner Ledger | `ops_financial_report_template.xml` | Per-partner sections, running balance |
| 4.9 | Statement of Account | `ops_financial_report_template.xml` | Customer-facing format, bank details |
| 4.10 | PDC Registry | `ops_treasury_report_templates.xml` | Status badges, by-bank grouping |
| 4.11 | PDC Maturity | `ops_treasury_report_templates.xml` | Maturity timeline, overdue highlight |
| 4.12 | PDCs in Hand | `ops_treasury_report_templates.xml` | Summary by bank, total value |
| 4.13 | Asset Register | `ops_asset_report_templates.xml` | Category groups, NBV calculation |
| 4.14 | Depreciation Schedule | `ops_asset_report_templates.xml` | Period projections, method display |
| 4.15 | Stock Valuation | `ops_inventory_report_templates.xml` | Location/category groups, valuation method |
| 4.16 | Inventory Aging | `ops_inventory_report_templates.xml` | Age buckets with colors, last movement |

---

### Phase 4 Key Design Elements

**For ALL Reports:**

1. **Corporate header** (shared component)
   - Company logo or initials
   - Company name and location
   - Print date and user

2. **Report title section** (shared component)
   - Report name
   - Pillar/category label
   - Period/date display

3. **Filter info bar** (shared component)
   - Scope (branches/consolidated)
   - Currency
   - Business units (if applicable)
   - Entry status (posted/all)

4. **Section headers** (color-coded by type)
   - Financial sections: Blue (#5B6BBB)
   - Asset sections: Green (#16a34a)
   - Liability sections: Orange (#f59e0b)
   - Equity sections: Purple (#9333ea)
   - Revenue sections: Green (#16a34a)
   - Expense sections: Red (#dc2626)
   - Treasury sections: Cyan (#0891b2)

5. **Data tables**
   - Clean headers (9px uppercase)
   - Alternating row colors
   - Monospace fonts for numbers
   - Right-aligned numeric columns
   - No vertical borders (horizontal only)

6. **Value formatting**
   - Positive: Default text color
   - Negative: Red with parentheses
   - Zero: Gray
   - Thousands separators
   - 2 decimal places

7. **Subtotal rows**
   - Light background (#f8fafc)
   - Bold text
   - 1px top border

8. **Total rows**
   - Darker background (#f1f5f9)
   - Bold text
   - 2px top border, 3px double bottom border
   - Uppercase labels

9. **Notes section** (shared component)
   - Standard notes (currency, posting status, etc.)
   - Report-specific notes

10. **Footer** (shared component)
    - "Powered by OPS Framework" badge
    - Page numbers

---

### Phase 4 Testing Checklist

```
□ Generate each report as PDF
□ Verify corporate header displays correctly
□ Verify company logo appears (or initials if no logo)
□ Verify report title and period display
□ Verify filter info bar shows applied filters
□ Verify section headers use correct colors
□ Verify tables have clean styling
□ Verify numbers format correctly (thousands separator)
□ Verify positive values in black, negative in red with ()
□ Verify zero values in gray
□ Verify subtotals highlighted
□ Verify grand totals prominent
□ Verify balance checks (where applicable)
□ Verify notes section displays
□ Verify footer with OPS badge and page numbers
□ Test with/without company logo
□ Test with different primary colors
□ Test multi-page reports (page break handling)
□ Visual comparison to HTML Balance Sheet sample
```

---

## 📊 PHASE 5: EXCEL EXPORT ENHANCEMENT

**Duration:** 2 days
**Priority:** P1 (High)
**Dependencies:** Phase 1 complete

### Overview
Update Excel export generators to use corporate branding with company colors, professional formatting, and consistent structure.

---

### Corporate Excel Format Standards

**All Excel exports MUST include:**

1. **Company Header Block** (Rows 1-4)
   - Row 1: Company name (bold, 16pt)
   - Row 2: Report title (bold, 14pt)
   - Row 3: Period/date range
   - Row 4: Generated date and user

2. **Filter Summary Block** (Row 5-6)
   - Background: Primary color light
   - Border: Primary color
   - Contains: Scope, currency, filters applied

3. **Data Table** (Starting Row 8)
   - Header row: Primary color background, white text, bold
   - Alternating rows: White/light gray
   - Number columns: Right-aligned, thousand separator, 2 decimals
   - Positive values: Black
   - Negative values: Red
   - Subtotals: Bold, light background
   - Grand totals: Bold, primary color background, white text

4. **Column widths**: Auto-sized to content
5. **Freeze panes**: Header row frozen
6. **Print settings**: Fit to page, landscape orientation

---

### Task 5.1: Update Excel Format Helper

**File:** `report/excel_styles.py`

**Add method:**

```python
def get_corporate_excel_formats(workbook, company):
    """
    Generate OPS corporate Excel formats based on company primary color.

    Args:
        workbook: xlsxwriter workbook object
        company: res.company record

    Returns:
        dict: Format objects keyed by name
    """
    primary_hex = company.primary_color or '#5B6BBB'

    # Convert hex to RGB for xlsxwriter
    hex_color = primary_hex.lstrip('#')
    try:
        primary_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        primary_rgb = (91, 107, 187)  # Default OPS blue

    # Calculate light version (15% opacity with white)
    light_rgb = tuple(int(c * 0.15 + 255 * 0.85) for c in primary_rgb)
    light_hex = '#{:02x}{:02x}{:02x}'.format(*light_rgb)

    formats = {
        # Company header
        'company_name': workbook.add_format({
            'font_size': 16,
            'bold': True,
            'font_color': '#1e293b',
            'font_name': 'Arial',
        }),

        # Report title
        'report_title': workbook.add_format({
            'font_size': 14,
            'bold': True,
            'font_color': '#1e293b',
            'font_name': 'Arial',
        }),

        # Report metadata
        'metadata': workbook.add_format({
            'font_size': 9,
            'font_color': '#64748b',
            'font_name': 'Arial',
        }),

        # Filter bar
        'filter_bar': workbook.add_format({
            'font_size': 9,
            'bg_color': light_hex,
            'border': 1,
            'border_color': primary_hex,
            'font_name': 'Arial',
        }),

        # Table header
        'table_header': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'font_color': '#ffffff',
            'bg_color': primary_hex,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': False,
            'font_name': 'Arial',
        }),

        # Table header (right-aligned for numbers)
        'table_header_num': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'font_color': '#ffffff',
            'bg_color': primary_hex,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'font_name': 'Arial',
        }),

        # Regular text cell
        'text': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'font_name': 'Arial',
        }),

        # Regular text cell (alternating row)
        'text_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'font_name': 'Arial',
        }),

        # Number cell (positive)
        'number': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        }),

        # Number cell (positive, alternating row)
        'number_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        }),

        # Number cell (negative)
        'number_negative': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '(#,##0.00)',
            'font_color': '#dc2626',
            'font_name': 'Consolas',
        }),

        # Number cell (negative, alternating row)
        'number_negative_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'align': 'right',
            'num_format': '(#,##0.00)',
            'font_color': '#dc2626',
            'font_name': 'Consolas',
        }),

        # Number cell (zero)
        'number_zero': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_color': '#94a3b8',
            'font_name': 'Consolas',
        }),

        # Number cell (zero, alternating row)
        'number_zero_alt': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': '#f8fafc',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_color': '#94a3b8',
            'font_name': 'Consolas',
        }),

        # Subtotal row
        'subtotal_label': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': light_hex,
            'font_color': '#475569',
            'font_name': 'Arial',
        }),

        'subtotal_number': workbook.add_format({
            'font_size': 9,
            'bold': True,
            'border': 1,
            'border_color': '#e2e8f0',
            'bg_color': light_hex,
            'align': 'right',
            'num_format': '#,##0.00',
            'font_color': '#475569',
            'font_name': 'Consolas',
        }),

        # Total row
        'total_label': workbook.add_format({
            'font_size': 10,
            'bold': True,
            'border': 2,
            'border_color': '#1e293b',
            'bg_color': primary_hex,
            'font_color': '#ffffff',
            'font_name': 'Arial',
        }),

        'total_number': workbook.add_format({
            'font_size': 10,
            'bold': True,
            'border': 2,
            'border_color': '#1e293b',
            'bg_color': primary_hex,
            'font_color': '#ffffff',
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Consolas',
        }),

        # Percentage format
        'percentage': workbook.add_format({
            'font_size': 9,
            'border': 1,
            'border_color': '#e2e8f0',
            'align': 'right',
            'num_format': '0.0%',
            'font_name': 'Consolas',
        }),
    }

    return formats
```

---

### Task 5.2-5.9: Update Excel Generators

Apply corporate formatting to each Excel export method:

| # | Wizard | Method | File |
|---|--------|--------|------|
| 5.2 | Financial Intelligence | `action_export_excel()` | `wizard/ops_general_ledger_wizard_enhanced.py` |
| 5.3 | Treasury Intelligence | `action_export_excel()` | `wizard/ops_treasury_report_wizard.py` |
| 5.4 | Asset Intelligence | `action_export_excel()` | `wizard/ops_asset_report_wizard.py` |
| 5.5 | Inventory Intelligence | `action_export_excel()` | `wizard/ops_inventory_report_wizard.py` |
| 5.6 | Balance Sheet | `action_generate_xlsx()` | `wizard/ops_balance_sheet_wizard.py` |
| 5.7 | Cash Book | `action_export_excel()` | `wizard/ops_daily_reports_wizard.py` |
| 5.8 | Day Book | `action_export_excel()` | `wizard/ops_daily_reports_wizard.py` |
| 5.9 | Bank Book | `action_export_excel()` | `wizard/ops_daily_reports_wizard.py` |

**Standard Excel Export Structure:**

```python
def action_export_excel(self):
    """Generate corporate-branded Excel export"""
    self.ensure_one()

    # Validate filters
    validation_result = self._validate_filters()
    if isinstance(validation_result, dict) and 'warning' in validation_result:
        return validation_result

    # Security check
    self._check_intelligence_access(self._get_engine_name())

    # Get report data
    report_data = self._get_report_data()

    # Create Excel file
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet(self.report_title[:31])  # Sheet name limit

    # Get corporate formats
    from ...report.excel_styles import get_corporate_excel_formats
    formats = get_corporate_excel_formats(workbook, self.company_id)

    # Set column widths
    worksheet.set_column('A:A', 15)  # Date/code column
    worksheet.set_column('B:E', 20)  # Text columns
    worksheet.set_column('F:H', 15)  # Number columns

    # Freeze header row
    worksheet.freeze_panes(8, 0)  # Freeze after headers (row 8)

    row = 0

    # Company header
    worksheet.write(row, 0, self.company_id.name, formats['company_name'])
    row += 1

    worksheet.write(row, 0, self.report_title, formats['report_title'])
    row += 1

    period_text = f"Period: {self.date_from} to {self.date_to}"
    worksheet.write(row, 0, period_text, formats['metadata'])
    row += 1

    generated_text = f"Generated: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')} by {self.env.user.name}"
    worksheet.write(row, 0, generated_text, formats['metadata'])
    row += 2

    # Filter bar
    filter_text = f"Scope: {self.filter_summary} | Currency: {self.currency_id.name}"
    worksheet.merge_range(row, 0, row, 7, filter_text, formats['filter_bar'])
    row += 2

    # Table headers
    headers = ['Date', 'Journal', 'Reference', 'Partner', 'Description', 'Debit', 'Credit', 'Balance']
    for col, header in enumerate(headers):
        if col >= 5:  # Number columns
            worksheet.write(row, col, header, formats['table_header_num'])
        else:
            worksheet.write(row, col, header, formats['table_header'])
    row += 1

    # Data rows
    for idx, line in enumerate(report_data.get('lines', [])):
        alt = idx % 2 == 1  # Alternating rows

        # Text columns
        worksheet.write(row, 0, line['date'], formats['text_alt'] if alt else formats['text'])
        worksheet.write(row, 1, line['journal'], formats['text_alt'] if alt else formats['text'])
        worksheet.write(row, 2, line['reference'], formats['text_alt'] if alt else formats['text'])
        worksheet.write(row, 3, line['partner'], formats['text_alt'] if alt else formats['text'])
        worksheet.write(row, 4, line['description'], formats['text_alt'] if alt else formats['text'])

        # Number columns (with value-based formatting)
        for col, key in [(5, 'debit'), (6, 'credit'), (7, 'balance')]:
            value = line[key]
            if abs(value) < 0.01:
                fmt = formats['number_zero_alt'] if alt else formats['number_zero']
            elif value < 0:
                fmt = formats['number_negative_alt'] if alt else formats['number_negative']
            else:
                fmt = formats['number_alt'] if alt else formats['number']
            worksheet.write(row, col, abs(value), fmt)

        row += 1

    # Total row
    worksheet.write(row, 0, 'GRAND TOTAL', formats['total_label'])
    worksheet.write(row, 1, '', formats['total_label'])
    worksheet.write(row, 2, '', formats['total_label'])
    worksheet.write(row, 3, '', formats['total_label'])
    worksheet.write(row, 4, '', formats['total_label'])
    worksheet.write(row, 5, report_data['total_debit'], formats['total_number'])
    worksheet.write(row, 6, report_data['total_credit'], formats['total_number'])
    worksheet.write(row, 7, report_data['total_balance'], formats['total_number'])

    # Set print options
    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 0)  # Fit to 1 page wide
    worksheet.set_paper(9)  # A4
    worksheet.set_margins(0.5, 0.5, 0.75, 0.75)

    # Close workbook and prepare download
    workbook.close()
    output.seek(0)

    # Create attachment
    filename = f"{self.report_title}_{fields.Date.today()}.xlsx"
    attachment = self.env['ir.attachment'].create({
        'name': filename,
        'datas': base64.b64encode(output.read()),
        'type': 'binary',
        'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })

    # Return download action
    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment.id}?download=true',
        'target': 'self',
    }
```

---

### Phase 5 Testing Checklist

```
□ Export each report to Excel
□ Verify company name displays in header
□ Verify report title displays
□ Verify period/date range displays
□ Verify generated date and user displays
□ Verify filter bar has primary color background
□ Verify table headers have primary color background
□ Verify white text on colored headers
□ Verify alternating row colors
□ Verify number formatting (thousands separator, 2 decimals)
□ Verify negative numbers in red with parentheses
□ Verify zero values in gray
□ Verify subtotals highlighted
□ Verify grand totals with primary color background
□ Verify column widths appropriate
□ Verify header row frozen
□ Verify landscape orientation
□ Open in Excel/LibreOffice - verify formatting preserved
□ Test with different company primary colors
```

---

## 🔒 PHASE 6: SECURITY FIXES

**Duration:** 2 hours
**Priority:** P0 (Critical)
**Dependencies:** None

### Overview
Add `ops.intelligence.security.mixin` to Daily Books wizards to ensure IT Admin Blindness and branch isolation.

---

### Task 6.1: Cash Book Security

**File:** `wizard/ops_daily_reports_wizard.py`

**Current class definition (line ~25):**

```python
class OpsCashBookWizard(models.TransientModel):
    _name = 'ops.cash.book.wizard'
    _description = 'Cash Book Report Wizard'
```

**Updated:**

```python
class OpsCashBookWizard(models.TransientModel):
    _name = 'ops.cash.book.wizard'
    _inherit = ['ops.intelligence.security.mixin']  # ADD THIS
    _description = 'Cash Book Report Wizard'

    def _get_engine_name(self):
        """Return engine name for security checks"""
        return 'financial'
```

**Update `action_generate_report()` method:**

```python
def action_generate_report(self):
    """Generate Cash Book report with security checks"""
    self.ensure_one()

    # Security check
    self._check_intelligence_access('financial')

    # Validate date
    if not self.report_date:
        raise UserError(_("Please select a date for the report."))

    # Rest of existing logic...
```

---

### Task 6.2: Day Book Security

**Same file:** `wizard/ops_daily_reports_wizard.py`

**Current class definition (line ~150):**

```python
class OpsDayBookWizard(models.TransientModel):
    _name = 'ops.day.book.wizard'
    _description = 'Day Book Report Wizard'
```

**Updated:**

```python
class OpsDayBookWizard(models.TransientModel):
    _name = 'ops.day.book.wizard'
    _inherit = ['ops.intelligence.security.mixin']  # ADD THIS
    _description = 'Day Book Report Wizard'

    def _get_engine_name(self):
        """Return engine name for security checks"""
        return 'financial'
```

**Update `action_generate_report()` method:**

```python
def action_generate_report(self):
    """Generate Day Book report with security checks"""
    self.ensure_one()

    # Security check
    self._check_intelligence_access('financial')

    # Validate date
    if not self.report_date:
        raise UserError(_("Please select a date for the report."))

    # Rest of existing logic...
```

---

### Task 6.3: Bank Book Security

**Same file:** `wizard/ops_daily_reports_wizard.py`

**Current class definition (line ~275):**

```python
class OpsBankBookWizard(models.TransientModel):
    _name = 'ops.bank.book.wizard'
    _description = 'Bank Book Report Wizard'
```

**Updated:**

```python
class OpsBankBookWizard(models.TransientModel):
    _name = 'ops.bank.book.wizard'
    _inherit = ['ops.intelligence.security.mixin']  # ADD THIS
    _description = 'Bank Book Report Wizard'

    def _get_engine_name(self):
        """Return engine name for security checks"""
        return 'financial'
```

**Update `action_generate_report()` method:**

```python
def action_generate_report(self):
    """Generate Bank Book report with security checks"""
    self.ensure_one()

    # Security check
    self._check_intelligence_access('financial')

    # Validate inputs
    if not self.report_date:
        raise UserError(_("Please select a date for the report."))
    if not self.journal_ids:
        raise UserError(_("Please select at least one bank journal."))

    # Rest of existing logic...
```

---

### Phase 6 Testing Checklist

```
□ Update module: -u ops_matrix_accounting
□ Login as IT Admin user
□ Try to access Cash Book wizard
□ Verify AccessError: "IT Administrators cannot access Financial Intelligence reports"
□ Try to access Day Book wizard
□ Verify same AccessError
□ Try to access Bank Book wizard
□ Verify same AccessError
□ Login as branch-restricted user
□ Open Cash Book wizard
□ Verify only assigned branches visible
□ Generate report
□ Verify data filtered to user's branches only
□ Repeat for Day Book and Bank Book
□ Check ops_report_audit for logged accesses
```

---

## 🧹 PHASE 7: CLEANUP

**Duration:** 1 hour
**Priority:** P2 (Low)
**Dependencies:** Phase 4 complete (ensure no dependencies)

### Overview
Remove duplicate Balance Sheet wizard and archive deprecated files.

---

### Task 7.1: Remove Duplicate Balance Sheet Wizard

**Files to Delete:**

1. `wizard/ops_balance_sheet_wizard.py`
2. `wizard/ops_balance_sheet_wizard_views.xml`

**Files to Update:**

**File:** `wizard/__init__.py`

Remove line:
```python
from . import ops_balance_sheet_wizard
```

**File:** `__manifest__.py`

Remove from `data` list:
```python
"wizard/ops_balance_sheet_wizard_views.xml",
```

**Verification:**
- Balance Sheet functionality still available in Enhanced GL Wizard with `report_type='bs'`
- Existing Balance Sheet template in `report/ops_balance_sheet_template.xml` remains
- No menu actions reference `ops.balance.sheet.wizard` model

---

### Task 7.2: Archive Deprecated Files

**Create archive directory:**

```bash
mkdir -p /opt/gemini_odoo19/_archive/deprecated_2026_02_02
```

**Move deprecated files:**

```bash
cd /opt/gemini_odoo19/addons/ops_matrix_accounting

# Move deprecated wizards
mv deprecated/ ../../_archive/deprecated_2026_02_02/ops_matrix_accounting_wizards/

# Move any backup files
find . -name "*.backup*" -exec mv {} ../../_archive/deprecated_2026_02_02/backups/ \;
find . -name "*.bak" -exec mv {} ../../_archive/deprecated_2026_02_02/backups/ \;
find . -name "*_old.py" -exec mv {} ../../_archive/deprecated_2026_02_02/old_files/ \;
```

**Update git status:**

```bash
git status  # Verify no broken imports
git add .
git commit -m "chore(cleanup): Archive deprecated reporting wizards and remove duplicate Balance Sheet wizard"
```

---

### Task 7.3: Clean Manifest Comments

**File:** `__manifest__.py`

Remove outdated comments:

```python
# Before:
# DEPRECATED: ops_financial_report_wizard_views.xml moved to deprecated/
# DEPRECATED: ops_general_ledger_wizard_views.xml moved to deprecated/
# DISABLED: ops_report_menu.xml - references deprecated ops.financial.report.wizard model

# After: (Clean, no deprecation comments)
```

---

### Phase 7 Testing Checklist

```
□ Restart Odoo: docker restart gemini_odoo19
□ Update module: -u ops_matrix_accounting
□ Check logs for import errors
□ Verify all menus still accessible
□ Verify Balance Sheet accessible via Enhanced GL Wizard
□ Test generating Balance Sheet report
□ Verify no references to deleted models in database
□ Run git status - verify clean state
□ Verify archived files in _archive/ directory
```

---

## ✅ PHASE 8: TESTING & VALIDATION

**Duration:** 1 day
**Priority:** P0 (Critical)
**Dependencies:** Phases 1-7 complete

### Overview
Comprehensive testing of all 16 reports across PDF, Excel, and UI View modes with security and branding verification.

---

### Test Plan: Per-Report Checklist

For **EACH of the 16 reports**, complete this checklist:

**Report:** _______________________
**Wizard:** _______________________
**Tester:** _______________________
**Date:** _______________________

#### 1. Wizard UI (Phase 3)
```
□ Open wizard from menu
□ Clean, card-based layout displays
□ Emoji icons visible (if applicable)
□ Template quick start section (if applicable)
□ Date/period fields prepopulated with sensible defaults
□ Filter fields display correctly
□ Advanced options in collapsible section
□ Preview stats display (record count, filter summary)
□ All buttons display: View Report, Print PDF, Export Excel, Save Template, Cancel
```

#### 2. UI View Mode (Phase 2)
```
□ Click "View Report" button
□ New browser tab opens
□ Toolbar displays with Print/Export/Close buttons
□ Report displays with white background on gray
□ Report has shadow/card appearance
□ Corporate header visible with logo/initials
□ Company name and location display
□ Print date and user display
□ Report title centered and bold
□ Period/date range displays
□ Filter info bar visible with applied filters
□ Click "Print PDF" - browser print dialog opens
□ Click "Export Excel" - Excel file downloads (if implemented)
□ Click "Close" - tab closes
```

#### 3. PDF Export (Phase 4)
```
□ Click "Print PDF" from wizard
□ PDF generates without errors
□ Corporate header displays correctly
    □ Company logo (or initials if no logo)
    □ Company name bold, 16px
    □ Location in gray
    □ 2px primary color border at bottom
    □ Print date and user right-aligned
□ Report title section centered
    □ Title bold, large font
    □ Pillar/category label
    □ Period/date range
□ Filter info bar displays
    □ Light primary color background
    □ Scope, currency, filters listed
□ Section headers (if applicable)
    □ Colored left border (4px)
    □ Correct color per section type
    □ Background color matches
□ Data tables
    □ Clean headers (9px uppercase)
    □ No vertical borders
    □ Alternating row colors
    □ Numbers right-aligned
    □ Monospace font for numbers
□ Value formatting
    □ Positive values: Black
    □ Negative values: Red with ()
    □ Zero values: Gray
    □ Thousands separators present
    □ 2 decimal places
□ Subtotal rows (if applicable)
    □ Light background
    □ Bold text
    □ 1px top border
□ Grand total rows (if applicable)
    □ Darker background
    □ Bold text
    □ 2px top border, 3px double bottom
    □ Uppercase labels
□ Balance check (if applicable - BS, TB)
    □ Badge displays (BALANCED / UNBALANCED)
    □ Correct color (green/red)
    □ Difference shown if unbalanced
□ Notes section displays
    □ Standard notes present
    □ Report-specific notes present
□ Footer displays
    □ "Powered by OPS Framework" badge
    □ Page numbers (Page X of Y)
□ Multi-page handling (if applicable)
    □ Headers repeat on each page
    □ Page breaks logical (no orphaned rows)
    □ No content cut off
□ Visual comparison to HTML Balance Sheet sample
    □ Overall style matches
    □ Typography consistent
    □ Colors match
    □ Spacing/padding consistent
```

#### 4. Excel Export (Phase 5)
```
□ Click "Export Excel" from wizard
□ Excel file downloads
□ Open in Excel/LibreOffice
□ Company header block (rows 1-4)
    □ Company name bold, 16pt
    □ Report title bold, 14pt
    □ Period/date range
    □ Generated date and user
□ Filter summary block (rows 5-6)
    □ Primary color light background
    □ Border in primary color
    □ Filters listed
□ Data table (starting row 8)
    □ Header row: primary color bg, white text, bold
    □ Data rows: alternating white/light gray
    □ Number columns right-aligned
    □ Thousands separator present
    □ 2 decimal places
    □ Positive values: Black
    □ Negative values: Red
    □ Subtotals: Bold, light background
    □ Grand totals: Bold, primary color bg, white text
□ Column widths appropriate (not truncated)
□ Header row frozen
□ Print settings: Landscape, fit to page
□ Formatting preserved when reopening file
```

#### 5. Security Testing
```
□ Login as IT Admin user
□ Try to open wizard
□ Verify AccessError: "IT Administrators cannot access [Pillar] Intelligence reports"
□ Login as branch-restricted user (User A: Branch 1, 2)
□ Open wizard
□ Verify only assigned branches appear in branch_ids dropdown
□ Generate report with Branch 1 selected
□ Verify data only shows Branch 1 transactions
□ Try to manually filter by Branch 3 (not assigned)
□ Verify either: (a) Branch 3 not in dropdown, or (b) AccessError on generate
□ Login as BU Leader user
□ Open wizard
□ Verify access to all branches in assigned business units
□ Generate report
□ Verify data filtered correctly
□ Check ops_report_audit records
□ Verify audit entry created with correct user, report type, timestamp
```

#### 6. Branding with Custom Colors
```
□ Set company.primary_color to #FF5733 (orange)
□ Generate report as PDF
□ Verify primary color used in:
    □ Header border
    □ Section header borders
    □ Table header backgrounds
    □ Total row backgrounds
    □ Filter bar accents
□ Verify light version used in:
    □ Filter bar background
    □ Section header backgrounds
    □ Subtotal row backgrounds
□ Export to Excel
□ Verify orange color in table headers
□ Verify light orange in filter bar
□ Reset company.primary_color to default (#5B6BBB)
```

#### 7. Edge Cases
```
□ Generate report with no data (empty date range)
□ Verify "No records found" message or empty table
□ Verify no errors in log
□ Generate report with single record
□ Verify formatting correct (no layout issues)
□ Generate report with 10,000+ records
□ Verify performance acceptable (< 30 seconds)
□ Verify memory usage acceptable
□ Verify all pages render correctly
□ Test with very long text in description fields
□ Verify text doesn't break layout
□ Verify wrapping/truncation appropriate
□ Test with special characters in names (é, ñ, 中文)
□ Verify characters render correctly in PDF
□ Verify characters render correctly in Excel
```

---

### Master Testing Matrix

| # | Report | Wizard | PDF | Excel | UI View | Security | Branding | Edge Cases |
|---|--------|--------|-----|-------|---------|----------|----------|------------|
| 1 | General Ledger | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Trial Balance | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | Profit & Loss | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Balance Sheet | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Cash Flow | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Aged Receivables | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Aged Payables | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | Partner Ledger | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | Statement of Account | ops.general.ledger.wizard.enhanced | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | PDC Registry | ops.treasury.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 11 | PDC Maturity | ops.treasury.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 12 | PDCs in Hand | ops.treasury.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 13 | Asset Register | ops.asset.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 14 | Depreciation Schedule | ops.asset.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 15 | Stock Valuation | ops.inventory.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 16 | Inventory Aging | ops.inventory.report.wizard | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

---

### Regression Testing

Test existing functionality not modified by this project:

```
□ Operational wizards still work (23 wizards)
□ Dashboard loads correctly
□ Budget module functions
□ PDC management works
□ Asset depreciation runs
□ Fiscal period closure works
□ User security still enforced
□ Branch isolation still works
□ Audit logs still generated
□ Email notifications still sent
□ Scheduled actions still run
```

---

### Performance Testing

```
□ Module upgrade completes in < 2 minutes
□ Report generation (1,000 records) < 10 seconds
□ Report generation (10,000 records) < 30 seconds
□ PDF rendering < 5 seconds
□ Excel export < 10 seconds
□ UI View loads < 3 seconds
□ No memory leaks (check after 50 reports)
□ No SQL N+1 queries (check logs)
```

---

### Browser Compatibility (UI View Mode)

```
□ Chrome/Edge (latest)
□ Firefox (latest)
□ Safari (latest)
□ Mobile Chrome (Android)
□ Mobile Safari (iOS)
```

---

### Final Validation Checklist

```
□ All 16 reports pass full checklist
□ No errors in Odoo log
□ No console errors in browser
□ Module upgrade clean (no warnings)
□ Git status clean
□ All tests documented
□ Issues logged in tracking system
□ User acceptance testing complete
□ Documentation updated
□ Training materials prepared (if needed)
```

---

## ⚠️ RISK ASSESSMENT

### High Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking existing report functionality** | High - Users cannot generate reports | • Test thoroughly before deployment<br>• Keep backup of current module version<br>• Deploy during low-usage window |
| **Performance degradation with large datasets** | Medium - Slow report generation | • Test with 10K+ records<br>• Optimize queries if needed<br>• Add record count warnings |
| **wkhtmltopdf rendering issues** | Medium - PDFs look incorrect | • Use inline styles only<br>• Test extensively<br>• Avoid CSS3 features |
| **Excel format compatibility issues** | Low - Files won't open in some programs | • Use xlsxwriter (proven library)<br>• Test in Excel and LibreOffice<br>• Follow OOXML standards |
| **Security bypass** | High - Unauthorized data access | • Test IT Admin blocking thoroughly<br>• Test branch isolation extensively<br>• Review security mixin implementation |

### Medium Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| **UI View controller vulnerabilities** | Medium - XSS or injection attacks | • Sanitize wizard_id input<br>• Use Odoo's built-in security<br>• Check access rights |
| **Timezone issues in dates** | Low - Wrong dates in reports | • Use context_timestamp consistently<br>• Test across timezones |
| **Multi-company data leaks** | Medium - User sees wrong company data | • Always filter by company_id<br>• Test with multi-company setup |
| **Custom color parsing errors** | Low - Default colors used instead | • Validate hex color format<br>• Fallback to safe defaults |

### Low Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Minor styling inconsistencies** | Low - Cosmetic only | • Visual QA review<br>• Compare to sample |
| **Missing translations** | Low - English works, others may not | • Mark strings translatable<br>• Test in second language |
| **Mobile view formatting** | Low - Not primary use case | • Basic responsive CSS<br>• Test on tablet |

---

## 🎯 SUCCESS CRITERIA

### Must Have (Launch Blockers)

- ✅ All 16 reports generate without errors
- ✅ Corporate styling consistent across all reports
- ✅ PDF exports display correctly
- ✅ Excel exports work and format correctly
- ✅ UI View feature functional
- ✅ IT Admin Blindness enforced on all reports
- ✅ Branch isolation working correctly
- ✅ No errors in Odoo log during normal use
- ✅ Visual quality matches HTML Balance Sheet sample
- ✅ Company primary color applied throughout

### Should Have (High Priority)

- ✅ All wizard forms styled per OPS Theme Guide
- ✅ Template save/load working
- ✅ Preview stats displaying correctly
- ✅ Notes section in all reports
- ✅ Balance verification in BS and TB
- ✅ Aging colors in aged reports
- ✅ Status badges in PDC reports
- ✅ Multi-page PDFs format correctly

### Nice to Have (Enhancement)

- ✅ Excel export for all reports (currently 15/16)
- ✅ Responsive mobile view
- ✅ Print preview optimization
- ✅ Keyboard shortcuts for wizards
- ✅ Report favoriting/bookmarking

---

## 🔄 ROLLBACK PLAN

### If Critical Issues Found During Phase 8

**Option 1: Rollback Module**

```bash
# Restore from backup
cd /opt/gemini_odoo19
git checkout <commit-before-changes>

# Update module
docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db \
  -u ops_matrix_accounting --stop-after-init --no-http

# Restart
docker restart gemini_odoo19
```

**Option 2: Disable New Features**

```python
# In __manifest__.py, comment out new templates
"data": [
    # ...existing entries...
    # "report/components/ops_corporate_report_components.xml",  # DISABLED
    # Use old templates temporarily
]
```

**Option 3: Feature Flag**

```python
# Add to res.config.settings
use_corporate_reports = fields.Boolean(
    string="Use Corporate Report Styling",
    config_parameter='ops_matrix_accounting.use_corporate_reports',
    default=False,  # Disable by default until tested
)

# In report templates, check flag
<t t-if="env['ir.config_parameter'].sudo().get_param('ops_matrix_accounting.use_corporate_reports')">
    <!-- New corporate template -->
</t>
<t t-else="">
    <!-- Old template -->
</t>
```

---

## 📅 IMPLEMENTATION TIMELINE

### Week 1 (Days 1-5)

| Day | Phase | Tasks | Duration |
|-----|-------|-------|----------|
| **Day 1** | Phase 1 | Foundation (COMPLETE) | - |
| | Phase 2 | UI View Feature | 6 hrs |
| | | • Add action_view_report to base wizard | 1 hr |
| | | • Create report controller | 3 hrs |
| | | • Add View Report buttons to forms | 1 hr |
| | | • Test UI View feature | 1 hr |
| **Day 2** | Phase 3 | Wizard UI Refactoring | 6 hrs |
| | | • Financial Intelligence wizard | 1 hr |
| | | • Treasury/Asset/Inventory wizards | 2 hrs |
| | | • Daily book wizards | 0.5 hr |
| | | • Test all wizard forms | 0.5 hr |
| | Phase 6 | Security Fixes | 2 hrs |
| | | • Add mixin to Daily Books | 1 hr |
| | | • Test IT Admin blocking | 1 hr |
| **Day 3** | Phase 4 | Report Templates (Financial 1-5) | 6 hrs |
| | | • General Ledger | 1.5 hrs |
| | | • Trial Balance | 1 hr |
| | | • Profit & Loss | 1.5 hrs |
| | | • Balance Sheet | 1.5 hrs |
| | | • Cash Flow | 0.5 hr |
| **Day 4** | Phase 4 | Report Templates (Financial 6-9) | 6 hrs |
| | | • Aged Receivables | 1.5 hrs |
| | | • Aged Payables | 1 hr |
| | | • Partner Ledger | 1.5 hrs |
| | | • Statement of Account | 1.5 hrs |
| | | • Test financial reports | 0.5 hr |
| **Day 5** | Phase 4 | Report Templates (Treasury/Asset) | 6 hrs |
| | | • PDC Registry | 1 hr |
| | | • PDC Maturity | 1 hr |
| | | • PDCs in Hand | 0.5 hr |
| | | • Asset Register | 1 hr |
| | | • Depreciation Schedule | 1 hr |
| | | • Test treasury/asset reports | 0.5 hr |
| | Phase 7 | Cleanup | 1 hr |

### Week 2 (Days 6-10)

| Day | Phase | Tasks | Duration |
|-----|-------|-------|----------|
| **Day 6** | Phase 4 | Report Templates (Inventory) | 2 hrs |
| | | • Stock Valuation | 1 hr |
| | | • Inventory Aging | 1 hr |
| | Phase 5 | Excel Exports (1-8) | 4 hrs |
| | | • Update excel_styles.py helper | 1 hr |
| | | • Financial Intelligence exports | 2 hrs |
| | | • Treasury Intelligence exports | 1 hr |
| **Day 7** | Phase 5 | Excel Exports (9-16) | 3 hrs |
| | | • Asset Intelligence exports | 1 hr |
| | | • Inventory Intelligence exports | 1 hr |
| | | • Daily book exports | 1 hr |
| | Phase 8 | Testing (Reports 1-8) | 3 hrs |
| **Day 8** | Phase 8 | Testing (Reports 9-16) | 4 hrs |
| | | • Complete per-report checklists | 3 hrs |
| | | • Test security for all reports | 1 hr |
| **Day 9** | Phase 8 | Testing (Comprehensive) | 6 hrs |
| | | • Branding tests with custom colors | 1 hr |
| | | • Edge case testing | 2 hrs |
| | | • Performance testing | 1 hr |
| | | • Browser compatibility | 1 hr |
| | | • Regression testing | 1 hr |
| **Day 10** | Phase 8 | Final Validation & Documentation | 6 hrs |
| | | • Complete master testing matrix | 2 hrs |
| | | • Fix any issues found | 2 hrs |
| | | • User acceptance testing | 1 hr |
| | | • Update documentation | 1 hr |

**Total Duration:** 10 days
**Effort:** ~65 hours
**Team Size:** 1-2 developers
**Recommended:** 2 weeks with buffer

---

## 📝 DOCUMENTATION UPDATES NEEDED

After completion, update these documents:

1. **User Guide** (`docs/user/OPS_REPORTS_USER_GUIDE.md`)
   - Add UI View mode instructions
   - Update screenshots
   - Document View/Print/Export buttons

2. **Technical Documentation** (`docs/technical/OPS_REPORTING_ARCHITECTURE.md`)
   - Document report controller
   - Document corporate styling system
   - Document Excel format standards

3. **Developer Guide** (`docs/developer/OPS_REPORT_DEVELOPMENT.md`)
   - How to create new reports
   - How to use shared components
   - How to implement corporate styling

4. **Changelog** (`CHANGELOG.md`)
   - Version bump to v19.0.19.0.0
   - List all changes per phase

5. **README** (`README.md`)
   - Update feature list
   - Add corporate reporting section

---

## 🎉 POST-LAUNCH ACTIVITIES

### Immediate (Day 1 After Launch)

```
□ Monitor Odoo logs for errors
□ Monitor user feedback
□ Check performance metrics
□ Verify audit logs populating
□ Document any issues found
```

### First Week

```
□ Conduct user training session
□ Collect user feedback
□ Address minor issues
□ Create FAQ document
□ Update user documentation based on questions
```

### First Month

```
□ Review performance metrics
□ Analyze usage patterns
□ Plan enhancements based on feedback
□ Consider additional report types
□ Evaluate success against criteria
```

---

## 📞 SUPPORT CONTACTS

| Role | Name | Contact | Responsibility |
|------|------|---------|----------------|
| **Project Lead** | Claude Code | - | Overall implementation |
| **Technical Owner** | Moe Zayour | github.com/MoeZayour | Code review, deployment |
| **QA Lead** | TBD | - | Testing coordination |
| **User Champion** | TBD | - | UAT, feedback collection |

---

## ✅ SIGN-OFF

### Phase Completion Sign-offs

| Phase | Description | Completed By | Date | Sign-off |
|-------|-------------|--------------|------|----------|
| Phase 1 | Foundation | Claude Code | 2026-02-02 | ✅ |
| Phase 2 | UI View Feature | | | ☐ |
| Phase 3 | Wizard UI | | | ☐ |
| Phase 4 | Report Templates | | | ☐ |
| Phase 5 | Excel Exports | | | ☐ |
| Phase 6 | Security Fixes | | | ☐ |
| Phase 7 | Cleanup | | | ☐ |
| Phase 8 | Testing | | | ☐ |

### Final Project Sign-off

| Stakeholder | Role | Sign-off | Date |
|-------------|------|----------|------|
| Moe Zayour | Technical Owner | ☐ | |
| TBD | QA Lead | ☐ | |
| TBD | User Champion | ☐ | |

---

**Document Control:**
- **Version:** 1.0.0
- **Created:** 2026-02-02
- **Last Updated:** 2026-02-02
- **Next Review:** 2026-02-12
- **Location:** `/opt/gemini_odoo19/claude_files/OPS_CORPORATE_REPORTING_IMPLEMENTATION_PLAN.md`

---

## 📚 APPENDICES

### Appendix A: File Checklist

Complete list of files to create or modify:

**NEW FILES (7):**
1. `models/ops_report_helpers.py`
2. `controllers/__init__.py`
3. `controllers/ops_report_controller.py`

**EXISTING FILES TO UPDATE (45+):**
4. `models/__init__.py`
5. `__init__.py` (root)
6. `wizard/ops_base_report_wizard.py`
7. `wizard/ops_general_ledger_wizard_enhanced.py`
8. `wizard/ops_treasury_report_wizard.py`
9. `wizard/ops_asset_report_wizard.py`
10. `wizard/ops_inventory_report_wizard.py`
11. `wizard/ops_daily_reports_wizard.py` (3 classes)
12. `views/ops_general_ledger_wizard_enhanced_views.xml`
13. `wizard/ops_treasury_report_wizard_views.xml`
14. `wizard/ops_asset_report_wizard_views.xml`
15. `views/ops_inventory_report_views.xml`
16. `wizard/ops_balance_sheet_wizard_views.xml`
17. `views/ops_daily_reports_views.xml`
18. `report/ops_general_ledger_template.xml`
19. `report/ops_financial_report_template.xml`
20. `report/ops_balance_sheet_template.xml`
21. `report/ops_treasury_report_templates.xml`
22. `report/ops_asset_report_templates.xml`
23. `report/ops_inventory_report_templates.xml`
24. `report/excel_styles.py`
25-40. Excel export methods in 8 wizard files

**FILES TO DELETE (2):**
41. `wizard/ops_balance_sheet_wizard.py`
42. `wizard/ops_balance_sheet_wizard_views.xml`

---

### Appendix B: SQL Queries for Verification

**Check wizard access logs:**
```sql
SELECT
    user_id,
    wizard_model,
    report_type,
    timestamp,
    record_count
FROM ops_report_audit
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY timestamp DESC
LIMIT 100;
```

**Check IT Admin blocking:**
```sql
SELECT
    u.login,
    g.name as group_name
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.uid
JOIN res_groups g ON g.id = r.gid
WHERE g.name = 'IT Administrator';
```

**Check branch assignments:**
```sql
SELECT
    u.login,
    b.name as branch_name
FROM res_users u
JOIN ops_user_branch_rel r ON u.id = r.user_id
JOIN ops_branch b ON b.id = r.branch_id
ORDER BY u.login, b.name;
```

---

### Appendix C: Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Report generates blank PDF** | QWeb template error | Check Odoo log for rendering errors, verify template XML syntax |
| **Colors don't apply** | Invalid hex color | Verify company.primary_color format (#RRGGBB) |
| **IT Admin can still access** | Security mixin not inherited | Verify `_inherit = ['ops.intelligence.security.mixin']` |
| **Branch filter not working** | Missing branch_ids field | Ensure wizard has branch_ids Many2many field |
| **Excel download fails** | xlsxwriter not installed | `pip install xlsxwriter` in container |
| **UI View 404 error** | Controller not registered | Check `controllers/__init__.py` imported in main `__init__.py` |
| **Fonts look wrong in PDF** | wkhtmltopdf font issue | Use system fonts only (Arial, Consolas) |
| **Page breaks in wrong place** | CSS page-break not respected | Add `page-break-inside: avoid` to sections |

---

### Appendix D: Git Commit Convention

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `style`: Formatting changes
- `docs`: Documentation
- `test`: Testing
- `chore`: Maintenance

**Examples:**
```
feat(reports): Add UI View mode for browser preview

Implements controller and action to display reports in browser
with Print/Export toolbar.

Closes #123
```

```
refactor(wizards): Apply OPS theme styling to all report wizards

Updates 8 wizard forms with card-based layout, emoji icons,
and collapsible sections per OPS_THEME_GUIDEBOOK.md.
```

```
fix(security): Add IT Admin Blindness to Daily Books

Adds ops.intelligence.security.mixin to Cash Book, Day Book,
and Bank Book wizards.
```

---

**END OF IMPLEMENTATION PLAN**

*This document provides complete step-by-step instructions for implementing corporate-grade reporting across all 16 OPS Framework reports. Follow phases sequentially, complete all testing checklists, and update documentation before final sign-off.*

*For questions or clarifications, refer to the project contacts listed above.*
