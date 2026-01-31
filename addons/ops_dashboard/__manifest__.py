{
    'name': 'OPS Dashboard',
    'version': '19.0.2.0.0',
    'category': 'Productivity/Dashboards',
    'summary': 'Enterprise Persona-Based KPI Dashboards for OPS Matrix',
    'description': """
OPS Dashboard - Enterprise KPI System
======================================

Enterprise-grade dashboard system for trading companies with:

**12 Persona-Specific Dashboards:**
- P01 IT Admin: System Health (3 KPIs)
- P02 CEO: Executive Overview (8 KPIs)
- P03 CFO: Financial Command Center (14 KPIs)
- P05 Branch Manager: Branch Operations (12 KPIs)
- P06 Sales Manager: Sales Performance (10 KPIs)
- P07 Purchase Manager: Procurement Hub (9 KPIs)
- P10 Sales Rep: My Sales (4 KPIs, own records only)
- P13 AR Clerk: Receivables (6 KPIs)
- P14 AP Clerk: Payables (5 KPIs)
- P15 Treasury: Cash Management (8 KPIs)

**50+ KPIs for Trading Companies:**
- Sales: Revenue, Orders, Quotations, Margin
- Purchase: PO value, count, pending, receipts
- AR/AP: Totals, Overdue, Aging
- PDC: Registered, Deposited, Bounced, Issued
- Inventory: Value, SKU count, Low stock
- Treasury: Cash balance, In/Out flows
- Governance: 3-Way Match, Budget utilization
- Assets: NBV, Depreciation due

**Security Features:**
- IT Admin Blindness (sees system KPIs only)
- Branch Isolation for transactional KPIs
- Cost/Margin Access Controls
- Persona-based dashboard visibility
- Scope Types: company, bu, branch, own
    """,
    'author': 'OPS Framework',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'sale',
        'purchase',
        'account',
        'stock',
        'ops_matrix_core',
        'ops_matrix_accounting',
    ],
    'data': [
        'security/ops_dashboard_security.xml',
        'security/ir.model.access.csv',
        'data/ops_kpi_data.xml',
        'data/ops_dashboard_data.xml',
        'views/ops_dashboard_views.xml',
        'views/ops_dashboard_widget_views.xml',
        'views/ops_kpi_views.xml',
        'views/ops_dashboard_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Chart libraries (must load first)
            'ops_dashboard/static/src/lib/chart.min.js',
            'ops_dashboard/static/src/lib/apexcharts.min.js',
            # Stylesheets
            'ops_dashboard/static/src/scss/dashboard.scss',
            'ops_dashboard/static/src/scss/charts.scss',
            # JavaScript components
            'ops_dashboard/static/src/js/chart_components.js',
            'ops_dashboard/static/src/js/ops_dashboard_action.js',
            # Templates
            'ops_dashboard/static/src/xml/chart_templates.xml',
            'ops_dashboard/static/src/xml/ops_dashboard_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
