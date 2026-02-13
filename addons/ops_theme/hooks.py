# -*- coding: utf-8 -*-
"""
OPS Theme — Lifecycle Hooks
============================
Pre-init handles column renames for the Smart Skins refactor.
Post-init ensures clean state.
Uninstall removes theme assets.
"""

import logging

_logger = logging.getLogger(__name__)


def _column_exists(cr, table, column):
    """Check if a column exists in a table."""
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
    """, (table, column))
    return bool(cr.fetchone())


def _rename_column(cr, table, old_col, new_col):
    """Rename a column if old exists and new does not."""
    if _column_exists(cr, table, old_col) and not _column_exists(cr, table, new_col):
        cr.execute(
            'ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s"' % (table, old_col, new_col)
        )
        _logger.info("OPS Theme: Renamed %s.%s → %s", table, old_col, new_col)
        return True
    return False


def pre_init_hook(env):
    """Rename columns from old field names to new Design Guide names.

    This runs BEFORE Odoo loads the module's models, so when the ORM
    creates fields with the new names, it finds existing columns and
    preserves data.
    """
    cr = env.cr

    # ops.theme.skin: primary_color → brand_color, secondary_color → action_color
    _rename_column(cr, 'ops_theme_skin', 'primary_color', 'brand_color')
    _rename_column(cr, 'ops_theme_skin', 'secondary_color', 'action_color')

    # res.company: ops_primary_color → ops_brand_color, ops_secondary_color → ops_action_color
    _rename_column(cr, 'res_company', 'ops_primary_color', 'ops_brand_color')
    _rename_column(cr, 'res_company', 'ops_secondary_color', 'ops_action_color')

    _logger.info("OPS Theme: pre_init_hook complete (Smart Skins column migration).")


def post_init_hook(env):
    """Post-install hook for ops_theme.

    Ensures skin data records exist and are updated to the new field names.
    """
    _logger.info("OPS Theme: post_init_hook complete (Smart Skins system).")


def uninstall_hook(env):
    """Remove ir.asset and ir.attachment records created by ops_theme.

    When the module is installed, it may create custom ir.asset records
    (e.g., color overrides via compile-time SCSS replacement). These
    records are not automatically removed by Odoo's module uninstaller,
    leaving orphaned assets that can cause SCSS compilation errors.
    """
    _logger.info("OPS Theme: Running uninstall cleanup...")

    # Remove any custom ir.asset records created for color overrides
    custom_assets = env['ir.asset'].search([
        '|', '|',
        ('path', 'like', '/ops_theme/'),
        ('target', 'like', '/ops_theme/'),
        ('path', 'like', '/_custom/'),
    ])
    if custom_assets:
        _logger.info(
            "OPS Theme: Removing %d custom ir.asset records",
            len(custom_assets),
        )
        custom_assets.unlink()

    # Remove any custom ir.attachment records (SCSS content storage)
    custom_attachments = env['ir.attachment'].search([
        '|',
        ('url', 'like', '/ops_theme/'),
        ('url', 'like', '/_custom/'),
        ('type', '=', 'binary'),
        ('mimetype', '=', 'text/scss'),
    ])
    if custom_attachments:
        _logger.info(
            "OPS Theme: Removing %d custom ir.attachment records",
            len(custom_attachments),
        )
        custom_attachments.unlink()

    # Clear asset caches to ensure clean state
    env.registry.clear_cache('assets')
    _logger.info("OPS Theme: Uninstall cleanup complete.")
