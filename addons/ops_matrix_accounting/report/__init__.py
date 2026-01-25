# Report Parsers (AbstractModel for QWeb PDF reports)
from . import ops_financial_report_parser
from . import ops_financial_matrix_report
from . import ops_general_ledger_report
from . import ops_asset_register_report

# XLSX Report Generators
from . import ops_asset_register_xlsx
from . import ops_general_ledger_xlsx
from . import ops_financial_matrix_xlsx

# Excel Style Factory (centralized styles for all XLSX reports)
from . import excel_styles
