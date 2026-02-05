# -*- coding: utf-8 -*-
"""
Extend Segregation of Duties for Accounting Module

Adds support for bank reconciliation SoD rules by extending
the model_name and action selections.
"""

from odoo import models, fields


class OpsSoDRuleAccountingExtension(models.Model):
    """Extend SoD to support accounting-specific document types"""
    _inherit = 'ops.segregation.of.duties'

    # Extend model_name selection to include bank reconciliation
    model_name = fields.Selection(
        selection_add=[
            ('ops.bank.reconciliation', 'Bank Reconciliation'),
        ],
        ondelete={'ops.bank.reconciliation': 'cascade'}
    )

    # Extend action selections to include reconcile
    action_1 = fields.Selection(
        selection_add=[
            ('reconcile', 'Reconcile'),
        ],
        ondelete={'reconcile': 'cascade'}
    )

    action_2 = fields.Selection(
        selection_add=[
            ('reconcile', 'Reconcile'),
        ],
        ondelete={'reconcile': 'cascade'}
    )
