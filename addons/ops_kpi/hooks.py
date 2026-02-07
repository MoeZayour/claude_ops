import logging

_logger = logging.getLogger(__name__)

# Default chart_kpi_codes per board code
_BOARD_CHART_CODES = {
    'IT_ADMIN': 'SYS_USERS_ACTIVE,SYS_SESSIONS',
    'CEO': 'SALES_REVENUE_MTD,SALES_ORDERS_MTD,AR_TOTAL',
    'CFO': 'SALES_REVENUE_MTD,AR_TOTAL,AP_TOTAL',
    'BRANCH_MGR': 'SALES_REVENUE_MTD,SALES_ORDERS_MTD',
    'SALES_MGR': 'SALES_REVENUE_MTD,SALES_ORDERS_MTD',
    'PURCHASE_MGR': 'PURCHASE_TOTAL_MTD,PURCHASE_ORDERS_MTD',
    'SALES_REP': 'MY_SALES_MTD,MY_ORDERS_MTD',
    'AR_CLERK': 'AR_TOTAL,AR_OVERDUE,AR_COLLECTED_MTD',
    'AP_CLERK': 'AP_TOTAL,AP_OVERDUE,AP_DUE_7_DAYS',
    'TREASURY': 'TREASURY_CASH_BALANCE,TREASURY_CASH_IN_MTD',
}


def post_init_hook(env):
    """Set chart_kpi_codes on boards that don't have them yet."""
    Board = env['ops.kpi.board']
    for code, chart_codes in _BOARD_CHART_CODES.items():
        boards = Board.search([('code', '=', code), ('chart_kpi_codes', '=', False)])
        if boards:
            boards.write({'chart_kpi_codes': chart_codes})
            _logger.info("Set chart_kpi_codes='%s' on board %s", chart_codes, code)
