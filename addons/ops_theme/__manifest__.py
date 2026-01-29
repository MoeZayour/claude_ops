# -*- coding: utf-8 -*-
{
    'name': 'OPS Theme',
    'version': '19.0.1.0.0',
    'category': 'Themes/Backend',
    'summary': 'Company-brandable backend theme with light/dark mode support',
    'description': """
OPS Theme - Enterprise Backend Theme
=====================================

Features:
- Company-brandable UI with dynamic colors
- Light/Dark/System color mode support
- Split-screen login page with company branding
- App grid home menu with horizontal menu tabs
- Chatter position toggle (below/right)
- Complete Odoo debranding
- PDF report theming
    """,
    'author': 'OPS Framework',
    'website': 'https://github.com/MoeZayour/claude_ops',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'ops_matrix_core',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {},
    'installable': True,
    'application': False,
    'auto_install': False,
}
