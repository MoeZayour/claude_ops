#!/usr/bin/env python3
"""
Script to fix the missing Excel Export Wizard records in the database.
"""
import psycopg2
import json
from datetime import datetime

# Connect to the database (via Docker network)
conn = psycopg2.connect(
    host="gemini_odoo19_db",
    port=5432,
    database="mz-db",
    user="odoo",
    password="odoo"
)
conn.autocommit = False
cursor = conn.cursor()

print("Starting Excel Export Wizard fix...")

# 1. Check if view already exists
cursor.execute("SELECT id FROM ir_ui_view WHERE model = %s AND name = %s", 
               ('ops.excel.export.wizard', 'ops.excel.export.wizard.form'))
if cursor.fetchone():
    print("View already exists, skipping...")
else:
    # Get next view ID
    cursor.execute("SELECT nextval('ir_ui_view_id_seq')")
    view_id = cursor.fetchone()[0]
    
    # Insert the view
    arch_xml = '''<form string="Export to Excel">
    <sheet>
        <div class="oe_title" invisible="state == 'done'">
            <h1>
                <field name="report_type" widget="radio" options="{'horizontal': true}"/>
            </h1>
        </div>
        
        <group col="4" invisible="state == 'done'">
            <group colspan="2">
                <field name="date_from"/>
                <field name="date_to"/>
            </group>
            <group colspan="2">
                <field name="branch_ids" widget="many2many_tags"/>
                <field name="business_unit_ids" widget="many2many_tags"/>
            </group>
        </group>
        
        <group invisible="state != 'done'">
            <div class="alert alert-success" role="alert">
                <strong>Excel file generated successfully!</strong>
                <p>Click the download button below to save the file.</p>
            </div>
            <field name="filename" invisible="1"/>
            <field name="excel_file" filename="filename" invisible="1"/>
        </group>
        
        <field name="state" invisible="1"/>
    </sheet>
    <footer>
        <button name="action_generate_excel"
                string="Generate Excel"
                type="object"
                icon="fa-cog"
                class="btn-primary"
                invisible="state == 'done'"/>
        <button name="action_download"
                string="Download"
                type="object"
                icon="fa-download"
                class="btn-primary"
                invisible="state != 'done'"/>
        <button string="Cancel" class="btn-secondary" special="cancel" icon="fa-times"/>
    </footer>
</form>'''
    
    arch_db = json.dumps({"en_US": arch_xml})
    
    cursor.execute("""
        INSERT INTO ir_ui_view (id, name, model, arch_db, type, active, priority, mode, create_uid, create_date, write_uid, write_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (view_id, 'ops.excel.export.wizard.form', 'ops.excel.export.wizard', 
          arch_db, 'form', True, 16, 'primary', 1, datetime.now(), 1, datetime.now()))
    print(f"Created view with ID: {view_id}")

# 2. Check if action already exists
cursor.execute("SELECT id FROM ir_act_window WHERE res_model = %s AND name->>'en_US' = %s", 
               ('ops.excel.export.wizard', 'Export to Excel'))
if cursor.fetchone():
    print("Action already exists, skipping...")
else:
    # Get next action ID
    cursor.execute("SELECT nextval('ir_actions_id_seq')")
    action_id = cursor.fetchone()[0]
    
    # Get the view ID we just created
    cursor.execute("SELECT id FROM ir_ui_view WHERE model = %s AND name = %s", 
                   ('ops.excel.export.wizard', 'ops.excel.export.wizard.form'))
    view_result = cursor.fetchone()
    if view_result:
        view_id = view_result[0]
    else:
        # Get any existing view for this model
        cursor.execute("SELECT id FROM ir_ui_view WHERE model = %s LIMIT 1", 
                       ('ops.excel.export.wizard',))
        view_result = cursor.fetchone()
        view_id = view_result[0] if view_result else None
    
    name_json = json.dumps({"en_US": "Export to Excel"})
    
    cursor.execute("""
        INSERT INTO ir_act_window (id, name, type, view_mode, res_model, target, context, binding_model_id, binding_view_types, binding_type, create_uid, create_date, write_uid, write_date, view_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (action_id, name_json, 'ir.actions.act_window', 'form', 'ops.excel.export.wizard', 
          'new', '{}', None, None, 'action', 1, datetime.now(), 1, datetime.now(), view_id))
    print(f"Created action with ID: {action_id}")

# 3. Check if menu already exists
cursor.execute("SELECT id FROM ir_ui_menu WHERE name->>'en_US' = %s", ('Excel Export',))
if cursor.fetchone():
    print("Menu already exists, skipping...")
else:
    # Get the parent menu (Accounting -> Reporting)
    cursor.execute("SELECT id FROM ir_ui_menu WHERE name->>'en_US' = %s LIMIT 1", ('Reporting',))
    parent_result = cursor.fetchone()
    if parent_result:
        parent_id = parent_result[0]
    else:
        # Use the OPS Analytics menu as parent
        cursor.execute("SELECT id FROM ir_ui_menu WHERE name->>'en_US' = %s LIMIT 1", ('OPS Analytics',))
        parent_result = cursor.fetchone()
        parent_id = parent_result[0] if parent_result else None
        if not parent_id:
            print("Could not find parent menu, using root...")
            parent_id = 1  # Root menu
    
    # Get next menu ID
    cursor.execute("SELECT nextval('ir_ui_menu_id_seq')")
    menu_id = cursor.fetchone()[0]
    
    name_json = json.dumps({"en_US": "Excel Export"})
    
    cursor.execute("""
        INSERT INTO ir_ui_menu (id, name, parent_id, action, sequence, create_uid, create_date, write_uid, write_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (menu_id, name_json, parent_id, f'ir.actions.act_window,{action_id}', 95, 1, datetime.now(), 1, datetime.now()))
    print(f"Created menu with ID: {menu_id}")

conn.commit()
print("\nAll Excel Export Wizard records created successfully!")
print("\nSummary:")
print("- View ID:", view_id if 'view_id' in dir() else 'N/A')
print("- Action ID:", action_id if 'action_id' in dir() else 'N/A')
print("- Menu ID:", menu_id if 'menu_id' in dir() else 'N/A')

cursor.close()
conn.close()
