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

    ops_color_mode = fields.Selection(
        selection=[
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        string='Color Mode',
        default='light',
        help='Color mode for the user interface.',
    )

    @property
    def SELF_READABLE_FIELDS(self):
        """Add OPS Theme fields to user-readable fields."""
        return super().SELF_READABLE_FIELDS + [
            'ops_chatter_position',
            'ops_color_mode',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Add OPS Theme fields to user-writeable fields."""
        return super().SELF_WRITEABLE_FIELDS + [
            'ops_chatter_position',
            'ops_color_mode',
        ]
