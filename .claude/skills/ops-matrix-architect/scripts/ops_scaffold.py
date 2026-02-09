#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPS Matrix Module Scaffold Generator
====================================

Generates a new Odoo 19 module following OPS Matrix Framework standards.

Features:
- Creates proper directory structure
- Generates manifest with ops_matrix_core dependency
- Creates model inheriting ops.matrix.mixin
- Generates security files
- Creates basic view templates

Usage:
    python ops_scaffold.py <module_name> [--model <model_name>] [--path <addons_path>]

Examples:
    python ops_scaffold.py ops_matrix_hr
    python ops_scaffold.py ops_matrix_fleet --model ops.vehicle
    python ops_scaffold.py ops_matrix_crm --path /opt/gemini_odoo19/addons
"""

import os
import sys
import argparse
from datetime import datetime


# ============================================================================
# TEMPLATES
# ============================================================================

MANIFEST_TEMPLATE = '''{{
    'name': 'OPS Matrix - {display_name}',
    'version': '19.0.1.0.0',
    'category': 'OPS Framework',
    'summary': '{summary}',
    'description': """
        OPS Matrix {display_name} Module
        {underline}

        Features:
        - Integrated with OPS Matrix Framework
        - Branch/Business Unit aware
        - Multi-level approval support
    """,
    'author': 'Antigravity AI',
    'website': 'https://github.com/MoeZayour/claude_ops',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'ops_matrix_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/{model_file}_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}}
'''

INIT_PY_ROOT = '''# -*- coding: utf-8 -*-
from . import models
'''

INIT_PY_MODELS = '''# -*- coding: utf-8 -*-
from . import {model_file}
'''

MODEL_TEMPLATE = '''# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class {model_class}(models.Model):
    """
    {model_description}

    Inherits: ops.matrix.mixin for branch/BU tracking
    """
    _name = '{model_name}'
    _description = '{model_description}'
    _inherit = ['ops.matrix.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # =========================================================================
    # Fields
    # =========================================================================

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        tracking=True,
    )

    code = fields.Char(
        string='Reference',
        copy=False,
        readonly=True,
        default='New',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    notes = fields.Text(
        string='Notes',
    )

    # =========================================================================
    # Computed Fields
    # =========================================================================

    # =========================================================================
    # Constraints
    # =========================================================================

    # =========================================================================
    # CRUD Methods
    # =========================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence."""
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    '{model_name}'
                ) or 'New'
        return super().create(vals_list)

    def unlink(self):
        """Prevent deletion of confirmed records."""
        for record in self:
            if record.state not in ('draft', 'cancelled'):
                raise ValidationError(
                    "You cannot delete a record that is not in Draft or Cancelled state."
                )
        return super().unlink()

    # =========================================================================
    # Action Methods
    # =========================================================================

    def action_confirm(self):
        """Confirm the record."""
        for record in self:
            record._check_branch_access()
            record.state = 'confirmed'

    def action_done(self):
        """Mark as done."""
        for record in self:
            record._check_branch_access()
            record.state = 'done'

    def action_cancel(self):
        """Cancel the record."""
        for record in self:
            record._check_branch_access()
            record.state = 'cancelled'

    def action_draft(self):
        """Reset to draft."""
        for record in self:
            record._check_branch_access()
            record.state = 'draft'

    # =========================================================================
    # Business Methods
    # =========================================================================
'''

SECURITY_CSV_TEMPLATE = '''id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_file}_user,{model_name}.user,model_{model_table},ops_matrix_core.group_ops_matrix_user,1,0,0,0
access_{model_file}_branch_manager,{model_name}.branch_manager,model_{model_table},ops_matrix_core.group_ops_branch_manager,1,1,1,0
access_{model_file}_admin,{model_name}.admin,model_{model_table},ops_matrix_core.group_ops_matrix_admin,1,1,1,1
'''

VIEWS_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="view_{model_file}_tree" model="ir.ui.view">
        <field name="name">{model_name}.tree</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <tree string="{model_description}" decoration-muted="state == 'cancelled'" decoration-success="state == 'done'">
                <field name="code"/>
                <field name="name"/>
                <field name="ops_branch_id" optional="show"/>
                <field name="ops_business_unit_id" optional="hide"/>
                <field name="state" widget="badge" decoration-info="state == 'draft'" decoration-success="state == 'done'" decoration-danger="state == 'cancelled'"/>
                <field name="create_date" optional="hide"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_{model_file}_form" model="ir.ui.view">
        <field name="name">{model_name}.form</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <form string="{model_description}">
                <header>
                    <button name="action_confirm" string="Confirm" type="object" class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object" class="btn-primary" invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object" invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" string="Reset to Draft" type="object" invisible="state not in ('cancelled',)"/>
                    <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                    </div>
                    <widget name="web_ribbon" title="Cancelled" bg_color="text-bg-danger" invisible="state != 'cancelled'"/>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name" placeholder="Name..." required="1"/>
                        </h1>
                        <field name="code" readonly="1"/>
                    </div>
                    <group>
                        <group name="main">
                            <!-- Main fields here -->
                        </group>
                        <group name="matrix">
                            <field name="ops_branch_id" options="{{'no_create': True}}"/>
                            <field name="ops_business_unit_id" options="{{'no_create': True}}"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Notes" name="notes">
                            <field name="notes" placeholder="Add notes..."/>
                        </page>
                    </notebook>
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_{model_file}_search" model="ir.ui.view">
        <field name="name">{model_name}.search</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <search string="{model_description}">
                <field name="name"/>
                <field name="code"/>
                <field name="ops_branch_id"/>
                <field name="ops_business_unit_id"/>
                <separator/>
                <filter name="filter_active" string="Active" domain="[('active', '=', True)]"/>
                <filter name="filter_inactive" string="Archived" domain="[('active', '=', False)]"/>
                <separator/>
                <filter name="filter_draft" string="Draft" domain="[('state', '=', 'draft')]"/>
                <filter name="filter_confirmed" string="Confirmed" domain="[('state', '=', 'confirmed')]"/>
                <filter name="filter_done" string="Done" domain="[('state', '=', 'done')]"/>
                <separator/>
                <group expand="0" string="Group By">
                    <filter name="group_state" string="Status" context="{{'group_by': 'state'}}"/>
                    <filter name="group_branch" string="Branch" context="{{'group_by': 'ops_branch_id'}}"/>
                    <filter name="group_bu" string="Business Unit" context="{{'group_by': 'ops_business_unit_id'}}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="action_{model_file}" model="ir.actions.act_window">
        <field name="name">{model_description}</field>
        <field name="res_model">{model_name}</field>
        <field name="view_mode">tree,form</field>
        <field name="search_view_id" ref="view_{model_file}_search"/>
        <field name="context">{{'search_default_filter_active': 1}}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first {model_description}
            </p>
        </field>
    </record>
</odoo>
'''

MENUS_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Main Menu (under OPS Matrix) -->
    <menuitem
        id="menu_{module_name}_root"
        name="{display_name}"
        parent="ops_matrix_core.menu_ops_root"
        sequence="50"/>

    <!-- Submenu -->
    <menuitem
        id="menu_{model_file}"
        name="{model_description}"
        action="action_{model_file}"
        parent="menu_{module_name}_root"
        sequence="10"/>
</odoo>
'''


# ============================================================================
# SCAFFOLD GENERATOR
# ============================================================================

class OPSModuleScaffold:
    """Generate OPS Matrix module scaffolding."""

    def __init__(self, module_name, model_name=None, addons_path=None):
        self.module_name = module_name
        self.addons_path = addons_path or '/opt/gemini_odoo19/addons'

        # Derive names from module_name
        # e.g., ops_matrix_hr -> hr
        suffix = module_name.replace('ops_matrix_', '').replace('ops_', '')

        # Model name: ops.suffix (e.g., ops.employee)
        self.model_name = model_name or f'ops.{suffix}'

        # Model file name: ops_suffix (e.g., ops_employee)
        self.model_file = self.model_name.replace('.', '_')

        # Model table name for security: ops_suffix
        self.model_table = self.model_file

        # Model class name: OpsEmployee
        parts = self.model_name.split('.')
        self.model_class = ''.join(word.capitalize() for word in parts)

        # Display name: HR
        self.display_name = suffix.replace('_', ' ').title()

        # Model description
        self.model_description = f'OPS {self.display_name}'

        # Module path
        self.module_path = os.path.join(self.addons_path, module_name)

    def create_directory_structure(self):
        """Create module directory structure."""
        directories = [
            self.module_path,
            os.path.join(self.module_path, 'models'),
            os.path.join(self.module_path, 'views'),
            os.path.join(self.module_path, 'security'),
            os.path.join(self.module_path, 'data'),
            os.path.join(self.module_path, 'report'),
            os.path.join(self.module_path, 'wizard'),
            os.path.join(self.module_path, 'static', 'description'),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"  Created: {directory}")

    def create_manifest(self):
        """Create __manifest__.py file."""
        content = MANIFEST_TEMPLATE.format(
            display_name=self.display_name,
            summary=f'OPS Matrix {self.display_name} management module',
            underline='=' * (len(f'OPS Matrix {self.display_name} Module') + 1),
            model_file=self.model_file,
        )

        filepath = os.path.join(self.module_path, '__manifest__.py')
        self._write_file(filepath, content)

    def create_init_files(self):
        """Create __init__.py files."""
        # Root __init__.py
        filepath = os.path.join(self.module_path, '__init__.py')
        self._write_file(filepath, INIT_PY_ROOT)

        # Models __init__.py
        content = INIT_PY_MODELS.format(model_file=self.model_file)
        filepath = os.path.join(self.module_path, 'models', '__init__.py')
        self._write_file(filepath, content)

    def create_model(self):
        """Create model file."""
        content = MODEL_TEMPLATE.format(
            model_class=self.model_class,
            model_name=self.model_name,
            model_description=self.model_description,
        )

        filepath = os.path.join(self.module_path, 'models', f'{self.model_file}.py')
        self._write_file(filepath, content)

    def create_security(self):
        """Create security files."""
        content = SECURITY_CSV_TEMPLATE.format(
            model_file=self.model_file,
            model_name=self.model_name,
            model_table=self.model_table,
        )

        filepath = os.path.join(self.module_path, 'security', 'ir.model.access.csv')
        self._write_file(filepath, content)

    def create_views(self):
        """Create view files."""
        # Main views
        content = VIEWS_TEMPLATE.format(
            model_file=self.model_file,
            model_name=self.model_name,
            model_description=self.model_description,
        )
        filepath = os.path.join(self.module_path, 'views', f'{self.model_file}_views.xml')
        self._write_file(filepath, content)

        # Menus
        content = MENUS_TEMPLATE.format(
            module_name=self.module_name,
            display_name=self.display_name,
            model_file=self.model_file,
            model_description=self.model_description,
        )
        filepath = os.path.join(self.module_path, 'views', 'menus.xml')
        self._write_file(filepath, content)

    def create_icon_placeholder(self):
        """Create a placeholder for icon.png."""
        filepath = os.path.join(self.module_path, 'static', 'description', '.gitkeep')
        self._write_file(filepath, '# Add icon.png here\n')

    def _write_file(self, filepath, content):
        """Write content to file."""
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Created: {filepath}")

    def generate(self):
        """Generate the complete module scaffold."""
        print(f"\n{'='*60}")
        print(f"OPS Matrix Module Scaffold Generator")
        print(f"{'='*60}")
        print(f"\nGenerating module: {self.module_name}")
        print(f"Model: {self.model_name}")
        print(f"Path: {self.module_path}")
        print(f"\n{'-'*60}\n")

        self.create_directory_structure()
        self.create_manifest()
        self.create_init_files()
        self.create_model()
        self.create_security()
        self.create_views()
        self.create_icon_placeholder()

        print(f"\n{'-'*60}")
        print(f"\nModule '{self.module_name}' created successfully!")
        print(f"\nNext steps:")
        print(f"  1. Add an icon.png to: {self.module_path}/static/description/")
        print(f"  2. Customize the model fields in: models/{self.model_file}.py")
        print(f"  3. Update views as needed")
        print(f"  4. Install the module:")
        print(f"     docker exec gemini_odoo19 odoo -c /etc/odoo/odoo.conf -d mz-db -i {self.module_name} --stop-after-init --no-http")
        print(f"\n{'='*60}\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate OPS Matrix Odoo 19 module scaffolding',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ops_scaffold.py ops_matrix_hr
  python ops_scaffold.py ops_matrix_fleet --model ops.vehicle
  python ops_scaffold.py ops_matrix_crm --path /opt/gemini_odoo19/addons
        """
    )

    parser.add_argument(
        'module_name',
        help='Module name (e.g., ops_matrix_hr)'
    )

    parser.add_argument(
        '--model',
        dest='model_name',
        help='Model name (default: derived from module name)'
    )

    parser.add_argument(
        '--path',
        dest='addons_path',
        default='/opt/gemini_odoo19/addons',
        help='Path to addons directory (default: /opt/gemini_odoo19/addons)'
    )

    args = parser.parse_args()

    # Validate module name
    if not args.module_name.startswith('ops_'):
        print(f"Warning: Module name should start with 'ops_' prefix.")
        print(f"Continuing with: {args.module_name}")

    # Generate scaffold
    scaffold = OPSModuleScaffold(
        module_name=args.module_name,
        model_name=args.model_name,
        addons_path=args.addons_path
    )

    try:
        scaffold.generate()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
