# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsersPreferences(models.Model):
    """Extend res.users with OPS Theme user preferences."""

    _inherit = 'res.users'

    ops_chatter_position = fields.Selection(
        selection=[
            ('side', 'Side'),
            ('bottom', 'Bottom'),
        ],
        string='Chatter Position',
        default='bottom',
        help='Position of the chatter/messaging panel on form views.',
    )

    # =========================================================================
    # UI ENHANCEMENT PREFERENCES
    # =========================================================================
    ops_sidebar_type = fields.Selection(
        selection=[
            ('invisible', 'Hidden'),
            ('small', 'Small Icons'),
            ('large', 'Large Icons'),
        ],
        string='Sidebar Type',
        default='large',
        help='Type of sidebar navigation display.',
    )
    ops_sidebar_position = fields.Selection(
        selection=[
            ('left', 'Left Side'),
            ('right', 'Right Side'),
        ],
        string='Sidebar Position',
        default='left',
        help='Position of the sidebar navigation.',
    )
    ops_dialog_size = fields.Selection(
        selection=[
            ('normal', 'Normal'),
            ('fullscreen', 'Fullscreen'),
        ],
        string='Dialog Size',
        default='normal',
        help='Default dialog display mode.',
    )
    ops_home_view_mode = fields.Selection(
        selection=[
            ('grid', 'Grid View'),
            ('list', 'List View'),
            ('tiles', 'Tile View'),
        ],
        string='Home View Mode',
        default='grid',
        help='Layout mode for the applications home screen.',
    )

    @property
    def SELF_READABLE_FIELDS(self):
        """Add OPS Theme fields to user-readable fields."""
        return super().SELF_READABLE_FIELDS + [
            'ops_chatter_position',
            'ops_sidebar_type',
            'ops_sidebar_position',
            'ops_dialog_size',
            'ops_home_view_mode',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Add OPS Theme fields to user-writeable fields."""
        return super().SELF_WRITEABLE_FIELDS + [
            'ops_chatter_position',
            'ops_sidebar_type',
            'ops_sidebar_position',
            'ops_dialog_size',
            'ops_home_view_mode',
        ]
