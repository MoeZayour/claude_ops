# OPS Framework - Administrator Guide

## 1. System Configuration
- The framework is built on Odoo 19.
- Configuration is managed via `/etc/odoo/odoo.conf`.

## 2. User Management
- Assign users to specific groups (e.g., Accountant, Sales Manager) to control access.
- Use the **Settings > Users & Companies** menu.

## 3. Security Setup
- Security rules are defined in `ir.model.access.csv` for each module.
- Field-level security is managed via groups on field definitions.

## 4. Backup & Restore
- Standard Odoo database backup via `/web/database/manager`.
- File system backups for the `filestore` directory.

## 5. Performance Tuning
- Ensure sufficient RAM for Odoo workers.
- Optimize PostgreSQL configuration for the expected load.
