#!/usr/bin/env python3
"""Quick system check"""
modules = env['ir.module.module'].search([('name', 'in', ['ops_matrix_core', 'ops_matrix_accounting', 'ops_matrix_asset_management'])])
print("MODULES:", [(m.name, m.state) for m in modules])

menus = env['ir.ui.menu'].search([])
print("TOTAL MENUS:", len(menus))

ops_menus = env['ir.ui.menu'].search([('name', 'ilike', 'OPS')])
print("OPS MENUS:", len(ops_menus))

models = ['ops.company', 'ops.business_unit', 'ops.branch', 'ops.persona', 'ops.approval_request', 'ops.sob_rule', 'ops.asset']
print("MODELS:", [(m, bool(env['ir.model'].search([('model', '=', m)]))) for m in models])
print("DONE")
