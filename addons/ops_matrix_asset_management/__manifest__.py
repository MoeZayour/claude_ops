{
    'name': 'OPS Matrix - Asset Management',
    'version': '19.0.1.0.0',
    'category': 'Operations/Assets',
    'summary': 'Asset Management for the OPS Matrix Framework',
    'description': """
        DEPRECATED: This module has been superseded by ops_matrix_accounting.

        The ops_matrix_accounting module provides complete asset management with:
        - Full depreciation schedule generation
        - Proper workflow states (draft → running → paused → sold/disposed)
        - Integration with ops.analytic.mixin
        - Better validation and constraints

        This module is disabled to prevent model conflicts with ops.asset.
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
    # DEPRECATED: Features moved to ops_matrix_accounting
    'installable': False,
    'application': True,
    'auto_install': False,
}
