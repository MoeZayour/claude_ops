# -*- coding: utf-8 -*-
"""
OPS Theme — Lifecycle Hooks
============================
Clean removal of theme assets on uninstall.
"""

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post-install hook for ops_theme.

    Skin data uses noupdate=1, so this hook can be used to update
    existing skin records on module upgrade if needed.
    """
    _logger.info("OPS Theme: post_init_hook complete (light-only skin system).")


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
