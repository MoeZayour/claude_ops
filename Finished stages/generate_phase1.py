import os
import pathlib

# Configuration
BASE_DIR = "addons/ops_matrix_core"

# File Contents
files = {
    f"{BASE_DIR}/__init__.py": """from . import models""",

    f"{BASE_DIR}/__manifest__.py": """# -*- coding: utf-8 -*-
{
    'name': "Matrix Operations Core",
    'summary': "Core architecture for Matrix Organization (Branches & Business Units)",
    'description': \"\"\"
        Version 1.8 - Foundation
        
        Implements the Matrix Organizational Structure:
        1. Geographic Branches (Admin/HR)
        2. Functional Business Units (P&L/Sales)
        3. Multi-Unit User Access Matrix
        
        This module provides the schema and basic views for the Matrix system.
    \"\"\",
    'author': "Gemini-3.0-Pro",
    'website': "http://www.yourcompany.com",
    'category': 'Sales/Configuration',
    'version': '19.0.1.0.0',
    'depends': ['base', 'sale_management', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/ops_branch_views.xml',
        'views/ops_business_unit_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
""",

    f"{BASE_DIR}/models/__init__.py": """from . import ops_branch
from . import ops_business_unit
from . import res_users
""",

    f"{BASE_DIR}/models/ops_branch.py": """from odoo import models, fields

class OpsBranch(models.Model):
    _name = 'ops.branch'
    _description = 'Operational Branch (Geographic)'
    _order = 'name'

    name = fields.Char(string='Branch Name', required=True)
    code = fields.Char(string='Branch Code', required=True, size=5, help="Short code e.g., DXB, KSA")
    sequence = fields.Integer(default=10)
    manager_id = fields.Many2one('res.users', string='Branch Manager', help="The administrative head of this location.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('code_company_uniq', 'unique (code, company_id)', 'The Branch Code must be unique per company!')
    ]
""",

    f"{BASE_DIR}/models/ops_business_unit.py": """from odoo import models, fields

class OpsBusinessUnit(models.Model):
    _name = 'ops.business.unit'
    _description = 'Business Unit (Functional)'
    _order = 'sequence, name'

    name = fields.Char(string='Unit Name', required=True)
    code = fields.Char(string='Unit Code', required=True, size=5, help="Short code e.g., RET, WHL")
    sequence = fields.Integer(default=10)
    leader_id = fields.Many2one('res.users', string='Unit Leader', help="The functional head of this business line.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_company_uniq', 'unique (code, company_id)', 'The Unit Code must be unique per company!')
    ]
""",

    f"{BASE_DIR}/models/res_users.py": """from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Primary Assignment (For default creation logic)
    default_branch_id = fields.Many2one('ops.branch', string='Default Branch')
    default_business_unit_id = fields.Many2one('ops.business.unit', string='Default Business Unit')

    # Matrix Access (For visibility logic)
    allowed_business_unit_ids = fields.Many2many(
        'ops.business.unit', 
        'res_users_business_unit_rel', 
        'user_id', 
        'unit_id', 
        string='Allowed Business Units',
        help="The Business Units this user is allowed to access/transact in."
    )

    @api.onchange('default_business_unit_id')
    def _onchange_default_unit(self):
        \"\"\"Ensure the default unit is automatically added to allowed units.\"\"\"
        if self.default_business_unit_id and self.default_business_unit_id not in self.allowed_business_unit_ids:
            self.allowed_business_unit_ids = [(4, self.default_business_unit_id.id)]
""",

    f"{BASE_DIR}/views/ops_branch_views.xml": """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="view_ops_branch_tree" model="ir.ui.view">
        <field name="name">ops.branch.tree</field>
        <field name="model">ops.branch</field>
        <field name="arch" type="xml">
            <tree string="Branches" editable="bottom">
                <field name="sequence" widget="handle"/>
                <field name="code"/>
                <field name="name"/>
                <field name="manager_id"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_ops_branch_form" model="ir.ui.view">
        <field name="name">ops.branch.form</field>
        <field name="model">ops.branch</field>
        <field name="arch" type="xml">
            <form string="Branch">
                <sheet>
                    <div class="oe_title">
                        <label for="name" class="oe_edit_only"/>
                        <h1><field name="name"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="code"/>
                            <field name="manager_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="action_ops_branch" model="ir.actions.act_window">
        <field name="name">Branches</field>
        <field name="res_model">ops.branch</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Menu: Settings > Users & Companies > Branches -->
    <menuitem id="menu_ops_branch"
              name="Branches"
              parent="base.menu_users"
              action="action_ops_branch"
              sequence="20"/>
</odoo>
""",

    f"{BASE_DIR}/views/ops_business_unit_views.xml": """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="view_ops_business_unit_tree" model="ir.ui.view">
        <field name="name">ops.business.unit.tree</field>
        <field name="model">ops.business.unit</field>
        <field name="arch" type="xml">
            <tree string="Business Units" editable="bottom">
                <field name="sequence" widget="handle"/>
                <field name="code"/>
                <field name="name"/>
                <field name="leader_id"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </tree>
        </field>
    </record>

    <!-- Action -->
    <record id="action_ops_business_unit" model="ir.actions.act_window">
        <field name="name">Business Units</field>
        <field name="res_model">ops.business.unit</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Menu: Sales > Configuration > Business Units -->
    <menuitem id="menu_ops_business_unit"
              name="Business Units"
              parent="sale.menu_sale_config"
              action="action_ops_business_unit"
              sequence="10"/>
</odoo>
""",

    f"{BASE_DIR}/views/res_users_views.xml": """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_users_form_matrix_inherit" model="ir.ui.view">
        <field name="name">res.users.form.matrix.inherit</field>
        <field name="model">res.users</field>
        <field name="inherit_id" ref="base.view_users_form"/>
        <field name="arch" type="xml">
            <notebook position="inside">
                <page string="Matrix Assignment">
                    <group>
                        <group string="Primary Assignment">
                            <field name="default_branch_id"/>
                            <field name="default_business_unit_id"/>
                        </group>
                        <group string="Access Matrix">
                            <field name="allowed_business_unit_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
                        </group>
                    </group>
                </page>
            </notebook>
        </field>
    </record>
</odoo>
""",

    f"{BASE_DIR}/security/ir.model.access.csv": """id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ops_branch_user,ops.branch.user,model_ops_branch,base.group_user,1,0,0,0
access_ops_branch_manager,ops.branch.manager,model_ops_branch,base.group_system,1,1,1,1
access_ops_business_unit_user,ops.business.unit.user,model_ops_business_unit,base.group_user,1,0,0,0
access_ops_business_unit_manager,ops.business.unit.manager,model_ops_business_unit,base.group_system,1,1,1,1
"""
}

def create_module():
    print(f"🚀 Starting generation of module: {BASE_DIR}")
    
    # Create directories
    dirs = [
        BASE_DIR,
        f"{BASE_DIR}/models",
        f"{BASE_DIR}/views",
        f"{BASE_DIR}/security",
        f"{BASE_DIR}/static/description"
    ]
    
    for d in dirs:
        pathlib.Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {d}")

    # Create files
    for filepath, content in files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Created file: {filepath}")

    print("\n✨ Module generation complete!")
    print("👉 Next steps:")
    print("1. Restart your Odoo container: docker restart gemini_odoo19")
    print("2. Go to Apps -> Update App List")
    print("3. Install 'Matrix Operations Core'")

if __name__ == "__main__":
    create_module()