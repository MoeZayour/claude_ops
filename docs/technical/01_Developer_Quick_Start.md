# OPS Framework - Developer Quick Start Guide

**Audience:** Developers
**Time to "Hello World":** 15 minutes

This guide will walk you through setting up the OPS Framework development environment and creating a simple extension module.

---

## Prerequisites

- Docker and Docker Compose installed
- Git command-line client
- A code editor (e.g., VS Code)
- Basic knowledge of Odoo module structure

---

## Step 1: Clone and Launch the Environment

1.  **Clone the Repository:**
    Get the complete source code, including the OPS modules and Docker configuration.

    ```bash
    git clone https://github.com/MoeZayour/claude_ops.git
    cd claude_ops
    ```

2.  **Start the Services:**
    Use Docker Compose to build and run the Odoo and PostgreSQL containers.

    ```bash
    docker-compose up -d
    ```

3.  **Monitor Logs:**
    Wait for the Odoo instance to initialize. You can monitor the progress by tailing the logs.

    ```bash
    docker logs gemini_odoo19 --follow
    ```
    Look for a line similar to `odoo.service.server: Odoo version 19.0`. Once you see it, press `Ctrl+C` to exit the logs.

4.  **Access Odoo:**
    Open your browser and navigate to `http://localhost:8089`. The default master password for database management is `admin`. You can log into the `mz-db` database with user `admin` and password `admin`.

---

## Step 2: Create Your "Hello World" Extension

Our goal is to add a new "Reference Number" field to the Sales Order form. This requires creating a new module that depends on `ops_matrix_core`.

1.  **Create Module Directory:**
    Create a new folder for your module inside the `addons` directory.

    ```bash
    mkdir -p addons/ops_matrix_helloworld
    mkdir -p addons/ops_matrix_helloworld/models
    mkdir -p addons/ops_matrix_helloworld/views
    ```

2.  **Create Manifest File:**
    This file tells Odoo about your module and its dependencies.

    **File: `addons/ops_matrix_helloworld/__manifest__.py`**
    ```python
    {
        'name': 'OPS Matrix - Hello World Extension',
        'version': '19.0.1.0.0',
        'category': 'OPS Framework',
        'author': 'Developer',
        'license': 'LGPL-3',
        'depends': ['ops_matrix_core', 'sale'],
        'data': [
            'views/sale_order_views.xml',
        ],
        'installable': True,
    }
    ```

3.  **Extend the Sale Order Model:**
    Add the new field to the `sale.order` model.

    **File: `addons/ops_matrix_helloworld/models/sale_order.py`**
    ```python
    from odoo import models, fields

    class SaleOrder(models.Model):
        _inherit = 'sale.order'

        hello_world_ref = fields.Char(string='Hello World Reference')
    ```

    **File: `addons/ops_matrix_helloworld/models/__init__.py`**
    ```python
    from . import sale_order
    ```

4.  **Add the Field to the View:**
    Inherit the existing sales order form to display your new field.

    **File: `addons/ops_matrix_helloworld/views/sale_order_views.xml`**
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <record id="view_order_form_helloworld" model="ir.ui.view">
            <field name="name">sale.order.form.helloworld</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.view_order_form"/>
            <field name="arch" type="xml">
                <field name="payment_term_id" position="after">
                    <field name="hello_world_ref"/>
                </field>
            </field>
        </record>
    </odoo>
    ```

---

## Step 3: Install and Verify

1.  **Install the Module:**
    Run the Odoo command inside the Docker container to install your new module.

    ```bash
    docker exec gemini_odoo19 odoo-bin \
      -d mz-db \
      -i ops_matrix_helloworld \
      --stop-after-init
    ```

2.  **Verify in the UI:**
    - Refresh your browser.
    - Navigate to **Sales → Orders → Orders**.
    - Create a new Sales Order or open an existing one.
    - You should now see the **"Hello World Reference"** field right below the "Payment Term" field.

**Congratulations! You have successfully extended the OPS Framework.**