# Report Parsers (AbstractModel for QWeb PDF reports)
from . import ops_financial_report_parser
from . import ops_financial_matrix_report
from . import ops_general_ledger_report
from . import ops_asset_register_report

# XLSX Report Generators (disabled - report_xlsx dependency unavailable)
# Uncomment when oca/reporting-engine report_xlsx module is installed
# from . import ops_asset_register_xlsx
# from . import ops_general_ledger_xlsx
# from . import ops_financial_matrix_xlsx
# from . import excel_styles
