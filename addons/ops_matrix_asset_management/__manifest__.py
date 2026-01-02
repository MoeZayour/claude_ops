{
    'name': 'OPS Matrix - Asset Management',
    'version': '19.0.1.0.0',
    'category': 'Operations/Assets',
    'summary': 'Asset Management for the OPS Matrix Framework',
    'description': """
        Manages the lifecycle of company assets, from acquisition to disposal.
        Integrated with the OPS Matrix for dimensional tracking.
    """,
    'author': 'Gemini Agent',
    'website': 'https://github.com/MoeZayour',
    'license': 'LGPL-3',
    'depends': [
        'ops_matrix_core',
        'ops_matrix_accounting',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ops_asset_views.xml',
        'views/ops_asset_category_views.xml',
        'views/ops_asset_model_views.xml',
        'views/ops_asset_depreciation_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
