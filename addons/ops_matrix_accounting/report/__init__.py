# Report Parsers (AbstractModel for QWeb PDF reports)
from . import ops_financial_report_parser
from . import ops_financial_matrix_report
from . import ops_general_ledger_report
from . import ops_asset_register_report

# Excel infrastructure (Phase 5 - Corporate Design System)
from . import excel_styles
from . import ops_xlsx_abstract

# XLSX Report Generators (Phase 5 - Corporate Design System)
from . import ops_asset_register_xlsx
# from . import ops_general_ledger_xlsx  # TODO: Update to use ops.xlsx.abstract
# from . import ops_financial_matrix_xlsx  # TODO: Update to use ops.xlsx.abstract
# from . import ops_treasury_report_xlsx  # TODO: Update to use ops.xlsx.abstract
