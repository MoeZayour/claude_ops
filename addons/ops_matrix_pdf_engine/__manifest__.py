{
    "name": "OPS Matrix - Modern PDF Engine",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "WeasyPrint-based PDF engine for modern CSS (Flexbox, Grid, Variables)",
    "description": """
        OPS Matrix Modern PDF Engine
        ============================

        Provides a WeasyPrint-based PDF rendering engine that supports:
        - CSS Flexbox and Grid layouts
        - CSS Variables (Custom Properties)
        - Modern fonts and typography
        - Full CSS3 support

        This module bypasses wkhtmltopdf limitations for advanced PDF generation.

        Usage:
        - Use `self.env['ops.pdf.engine'].generate_pdf()` to create PDFs
        - Modern CSS stylesheets can be used without restrictions
        - Suitable for complex dashboard and report layouts
    """,
    "author": "Antigravity AI",
    "website": "https://github.com/MoeZayour/claude_ops",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "ops_matrix_core",
        "ops_matrix_accounting",
    ],
    "external_dependencies": {
        "python": ["weasyprint"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/ops_modern_css.xml",
        "templates/modern_report_templates.xml",
        "views/wizard_button_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ops_matrix_pdf_engine/static/src/css/ops_modern_report.css",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
