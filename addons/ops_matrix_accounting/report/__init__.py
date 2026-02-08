# OPS Matrix Accounting - Report Parsers & Generators

# QWeb Parsers (AbstractModel for PDF/HTML rendering)
from . import ops_financial_report_parser
from . import ops_financial_matrix_report
from . import ops_general_ledger_report
from . import ops_asset_register_report
from . import ops_corporate_report_parsers

# Excel infrastructure (Phase 5 - Corporate Design System)
from . import excel_styles
from . import ops_xlsx_abstract

# Wave 1 — Report-specific Excel builders (TB, P&L, BS, CF)
from . import ops_excel_report_builders

# XLSX Report Generators (inherit from ops.xlsx.abstract)
from . import ops_asset_register_xlsx
from . import ops_general_ledger_xlsx
from . import ops_financial_matrix_xlsx
from . import ops_treasury_report_xlsx
