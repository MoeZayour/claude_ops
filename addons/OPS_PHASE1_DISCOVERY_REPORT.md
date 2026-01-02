# OPS MATRIX — PHASE 1 DISCOVERY & SCENARIO MATRIX

Generated: 2025-12-31
Database: mz-db
Container: gemini_odoo19

## Module Discovery (Host → /opt/gemini_odoo19/addons)

- ops_matrix_core
- ops_matrix_accounting
- ops_matrix_reporting
- ops_matrix_asset_management
- Supporting deps observed in /mnt/extra-addons: report_xlsx, oca_reporting_engine/* (report_xlsx helper, csv/xml/sql export, etc.)

### Structures per instructions (per module)

#### ops_matrix_core
- Models: branches, business units, personas, governance rules/violations, approvals, security audit, archive policy, dashboards, mixins for matrix dimensions across sales/purchase/stock/account.
- Fields: extensive ops_branch_id / ops_business_unit_id, SLA, approval, audit, governance, dashboard configs, product/pricelist BU silo fields.
- Methods: action_*, _compute_*, _onchange_*, _check_*, create/write overrides for governance and security, SLA computations, approval workflows, matrix access calculations.
- Security groups: ops manager, ops admin, cross-branch BU leader, matrix administrator; record rules enforcing branch/BU intersection and admin bypass.
- Wizards: governance violation report, welcome wizard.
- Reports: none enumerated in core extraction (QWeb elsewhere for availability).

#### ops_matrix_accounting
- Models: ops.asset, ops.asset.category, ops.asset.depreciation, ops.budget (+ budget line), ops.company.consolidation, ops.branch.report, ops.business.unit.report, ops.consolidated.balance.sheet, ops.matrix.profitability.analysis, ops.pdc; account.move extensions.
- Fields: company, branch/business-unit links, depreciation params, budget amounts (planned/practical/committed), PDC data, consolidation dimensions.
- Methods: create/write/unlink overrides, depreciation compute, budget computes, consolidation/report helpers.
- Security/Rules: asset/branch/BU access, admin full-access rules, multi-company constraints.

#### ops_matrix_reporting
- Models: ops.financial.analysis, ops.inventory.analysis, ops.sales.analysis.
- Fields: date/move/account/branch/BU, debit/credit/balance; inventory quantities/values; sales qty/subtotal/margin.
- Methods: create/write/unlink overrides; analysis computation hooks.
- Record rules: branch AND BU intersection; manager/admin full access; warehouse manager access for inventory analysis.
- Wizards: ops_excel_export_wizard.

#### ops_matrix_asset_management
- Models: ops.asset_model, ops.asset, ops.asset.category, ops.asset.depreciation (asset management flavor, depends on core); asset views/forms.
- Fields: asset model params, depreciation profiles, branch/BU links.
- Security/Rules: ir.model.access for asset models/categories/depreciations; standard matrix visibility.

#### report_xlsx (dependency)
- Provides XLSX report engine; controllers, report abstract, sample partner XLSX report, JS action manager patch.

#### oca_reporting_engine components (dependencies)
- Various reporting helpers: report_xlsx_helper, report_async, report_csv, report_layout_config, report_py3o, report_qweb_* options, sql_export, sql_export_excel/mail, sql_request_abstract, base_comment_template, kpi, etc.

## Structural Highlights

- Core governance mixins, branches/BUs/personas, record rules, security audit, SLA, approvals
- Accounting: assets, budgets, PDC, consolidated reporting, move extensions
- Reporting: financial, inventory, sales analysis models with record rules
- Asset management: asset models/views (depends on core)

## Scenario Matrix Extraction (Odoo shell, --no-http)

### Models (sampled from extraction)
- ops.matrix.profitability.analysis
- ops.matrix.mixin (shared matrix fields)
- Extended: stock.picking, stock.move, stock.quant, stock.warehouse, stock.warehouse.orderpoint
- Extended: account.move, account.move.line (ops dimensions)
- Extended: product.template / product.product (business_unit_id)
- Extended: ops.governance.rule/violation/report, ops.inter.branch.transfer
- Extended wizards: ops.financial.report.wizard, ops.general.ledger.wizard, ops.asset.depreciation.wizard, ops.asset.register.wizard

### Record Rules (excerpt)
- Stock moves limited to allowed branches: domain on picking.ops_branch_id/company_ids
- Sale order lines limited by company/branch/BU intersection
- Stock picking/write constrained to allowed branches
- Business units limited to ops_allowed_business_unit_ids; matrix admins full access
- Cross-branch BU leader rules for SO/PO/Invoices by BU
- Governance rules visible to ops managers; admins full access
- Asset multi-company rules (ops.asset, ops.asset.category, ops.asset.depreciation)
- Product BU silo rules for templates/variants

### Reports
- Products Availability (sale.order, qweb-pdf)

### Observed Warnings During Shell Loads
- _sql_constraints legacy attribute flagged across multiple models
- purchase.order class missing explicit _name override
- Field parameter `tracking` on sale.order.line/purchase.order.line ops fields requires _valid_field_parameter (core overrides in res_users only)
- Persona compute_sudo/store inconsistency warnings

## Data Discovery Notes
- Security groups list returned empty in extraction (likely naming not matched on `ops matrix` filter); rule extraction succeeded.
- No crm.lead model present in DB during tests.

## Next Steps
- Address warnings (_sql_constraints → model.Constraint, add _name on purchase.order extension, allow tracking where needed).
- Map security groups for matrix test users (use group_ids) before governance tests.
- Rerun governance/workflow tests after group fixes.
