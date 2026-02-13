# -*- coding: utf-8 -*-
"""
OPS Matrix Core - User API & Dashboard Configuration
=======================================================

Provides REST API key management, dashboard configuration fields,
and related action methods for res.users.

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResUsersApi(models.Model):
    _inherit = 'res.users'

    # ========================================================================
    # REST API AUTHENTICATION FIELDS
    # ========================================================================

    ops_api_key = fields.Char(
        string='API Key',
        copy=False,
        groups='base.group_system',
        help='API key for REST API authentication. Keep this secret! '
             'Used in X-API-Key header for API requests.'
    )

    ops_api_key_created = fields.Datetime(
        string='API Key Created',
        copy=False,
        readonly=True,
        groups='base.group_system',
        help='Timestamp when the current API key was generated'
    )

    ops_api_rate_limit = fields.Integer(
        string='API Rate Limit (per hour)',
        default=1000,
        groups='base.group_system',
        help='Maximum number of API calls this user can make per hour. '
             'Default: 1000 calls/hour'
    )

    # ========================================================================
    # DASHBOARD CONFIGURATION FIELDS
    # ========================================================================

    ops_dashboard_config = fields.Json(
        string='Dashboard Configuration',
        help='User-specific dashboard configuration'
    )

    favorite_dashboard_ids = fields.Many2many(
        'ir.actions.act_window',
        'user_favorite_dashboard_rel',
        'user_id',
        'action_id',
        string='Favorite Dashboards',
        help='User\'s favorite dashboard actions'
    )

    last_dashboard_access = fields.Datetime(
        string='Last Dashboard Access',
        help='Timestamp of last dashboard access'
    )

    def get_dashboard_config(self):
        """Get user's dashboard configuration with defaults."""
        self.ensure_one()

        default_config = {
            'dashboard_layout': 'standard',
            'default_date_range': 'month',
            'show_branch_first': True,
            'include_inactive_dimensions': False,
            'color_scheme': 'corporate',
            'primary_color': '#1f77b4',
            'secondary_color': '#ff7f0e',
            'success_color': '#2ca02c',
            'warning_color': '#d62728',
            'cache_duration': 15,
            'auto_refresh': True,
            'refresh_interval': 300,
        }

        user_config = self.ops_dashboard_config or {}
        return {**default_config, **user_config}

    def action_open_dashboard_config(self):
        """Open dashboard configuration wizard."""
        self.ensure_one()

        return {
            'name': _('Dashboard Configuration'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.dashboard.config',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
            }
        }

    # ========================================================================
    # REST API KEY MANAGEMENT ACTIONS
    # ========================================================================

    def action_generate_api_key(self):
        """Generate a new secure API key for the user."""
        self.ensure_one()

        import secrets

        # Generate secure random key (32 bytes = 256 bits)
        new_key = secrets.token_urlsafe(32)

        self.write({
            'ops_api_key': new_key,
            'ops_api_key_created': fields.Datetime.now()
        })

        _logger.info(f"API key generated for user {self.name} (ID: {self.id})")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Generated'),
                'message': _('New API key: %s\n\nSave this key securely. It will not be shown again.') % new_key,
                'type': 'success',
                'sticky': True,
            }
        }

    def action_revoke_api_key(self):
        """Revoke the user's API key."""
        self.ensure_one()

        self.write({
            'ops_api_key': False,
            'ops_api_key_created': False
        })

        _logger.warning(f"API key revoked for user {self.name} (ID: {self.id})")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('API Key Revoked'),
                'message': _('API key has been revoked. Generate a new key to continue using the API.'),
                'type': 'warning',
            }
        }
