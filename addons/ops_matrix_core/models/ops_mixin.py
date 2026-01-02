# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OpsMatrixMixin(models.AbstractModel):
    """
    Gold Standard Mixin for Matrix Awareness.
    Inherit this in Sale Order, Move, Picking, etc. to make them 'Matrix Aware'.
    """
    _name = 'ops.matrix.mixin'
    _description = 'Matrix Operations Mixin'

    ops_branch_id = fields.Many2one(
        'ops.branch',
        string='Branch',
        index=True,
        tracking=True,
        check_company=True,
        help="Physical or Geographic Operational Entity"
    )
    ops_business_unit_id = fields.Many2one(
        'ops.business.unit',
        string='Business Unit',
        index=True,
        tracking=True,
        check_company=True,
        help="Strategic or Logical Operational Entity"
    )

    # ---------------------------------------------------------
    # Default Generation Logic (Optional hook for downstream)
    # ---------------------------------------------------------
    def _get_default_ops_branch(self):
        """ Hook to fetch default branch from user context or settings """
        return self.env.user.employee_id.branch_id if hasattr(self.env.user, 'employee_id') else False
