# -*- coding: utf-8 -*-
"""
OPS Aged Receivables / Payables Wizard (v2)
============================================

Shape C report with dynamic aging columns.

Author: OPS Matrix Framework
Version: 2.0 (Report Engine v2 - Phase 3)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dataclasses import asdict
from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeCReport, ColumnDef, MatrixRow,
)
import logging

_logger = logging.getLogger(__name__)


class OpsAgedReportWizard(models.TransientModel):
    _name = 'ops.aged.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Aged Receivables / Payables Report'

    # =========================================================================
    # Fields
    # =========================================================================
    as_of_date = fields.Date(
        string='As of Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help='Date from which aging buckets are computed.',
    )

    partner_type = fields.Selection([
        ('customer', 'Customers (Receivables)'),
        ('vendor', 'Vendors (Payables)'),
    ], string='Partner Type', required=True, default='customer')

    partner_ids = fields.Many2many(
        'res.partner',
        'ops_aged_wiz_partner_rel',
        'wizard_id', 'partner_id',
        string='Partners',
        help='Leave empty for all partners.',
    )

    aging_type = fields.Selection([
        ('by_due_date', 'By Due Date'),
        ('by_invoice_date', 'By Invoice Date'),
    ], string='Aging Type', default='by_due_date', required=True)

    period_length = fields.Integer(
        string='Period Length (days)',
        default=30,
        required=True,
        help='Number of days per aging bucket.',
    )

    # =========================================================================
    # Base class hook implementations
    # =========================================================================

    def _get_engine_name(self):
        return 'financial'

    def _get_report_shape(self):
        return 'matrix'

    def _get_report_titles(self):
        return {'aged': 'Aged Receivables / Payables'}

    def _get_scalar_fields_for_template(self):
        return ['target_move', 'partner_type', 'aging_type', 'period_length']

    def _get_m2m_fields_for_template(self):
        return ['partner_ids', 'branch_ids', 'business_unit_ids']

    # =========================================================================
    # Domain builder
    # =========================================================================

    def _build_aged_domain(self):
        """Build domain for open (unreconciled) items up to as_of_date."""
        self.ensure_one()

        # Determine account type based on partner_type
        if self.partner_type == 'customer':
            account_type = 'asset_receivable'
        else:
            account_type = 'liability_payable'

        domain = [
            ('date', '<=', self.as_of_date),
            ('company_id', '=', self.company_id.id),
            ('account_id.account_type', '=', account_type),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),  # Only posted entries
        ]

        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        elif self.partner_type == 'customer':
            domain.append(('partner_id.customer_rank', '>', 0))
        elif self.partner_type == 'vendor':
            domain.append(('partner_id.supplier_rank', '>', 0))

        # Branch isolation
        domain += self._get_branch_filter_domain()

        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))
        if self.business_unit_ids:
            domain.append(('ops_business_unit_id', 'in', self.business_unit_ids.ids))

        return domain

    # =========================================================================
    # Report data generation
    # =========================================================================

    def _get_report_data(self):
        """Build Shape C data for Aged Receivables/Payables."""
        self.ensure_one()

        # Security gate
        self._check_intelligence_access(self._get_engine_name())

        MoveLine = self.env['account.move.line']
        period = self.period_length
        as_of = self.as_of_date

        # Search open items
        domain = self._build_aged_domain()
        lines = MoveLine.search(domain, order='partner_id, date')

        # Bucket labels
        bucket_keys = ['current', 'bucket_1', 'bucket_2', 'bucket_3', 'bucket_4']
        bucket_labels = {
            'current': 'Current',
            'bucket_1': '1-{}'.format(period),
            'bucket_2': '{}-{}'.format(period + 1, period * 2),
            'bucket_3': '{}-{}'.format(period * 2 + 1, period * 3),
            'bucket_4': '>{}'.format(period * 3),
        }

        # Group by partner and bucket
        partner_data = {}  # partner_id -> {name, current, bucket_1..4, total}
        for line in lines:
            partner = line.partner_id
            partner_key = partner.id if partner else 0
            partner_name = partner.name if partner else 'Unknown'

            if partner_key not in partner_data:
                partner_data[partner_key] = {
                    'partner_name': partner_name,
                    'current': 0.0,
                    'bucket_1': 0.0,
                    'bucket_2': 0.0,
                    'bucket_3': 0.0,
                    'bucket_4': 0.0,
                    'total': 0.0,
                }

            # Calculate age
            if self.aging_type == 'by_due_date':
                ref_date = line.date_maturity or line.date
            else:
                ref_date = line.date

            if ref_date:
                age_days = (as_of - ref_date).days
            else:
                age_days = 0

            amount = line.amount_residual if hasattr(line, 'amount_residual') else line.balance

            # Bucket
            if age_days <= 0:
                partner_data[partner_key]['current'] += amount
            elif age_days <= period:
                partner_data[partner_key]['bucket_1'] += amount
            elif age_days <= period * 2:
                partner_data[partner_key]['bucket_2'] += amount
            elif age_days <= period * 3:
                partner_data[partner_key]['bucket_3'] += amount
            else:
                partner_data[partner_key]['bucket_4'] += amount

            partner_data[partner_key]['total'] += amount

        # --- Column definitions ---
        columns = [
            ColumnDef(key='partner_name', label='Partner', col_type='string', width=30, align='left'),
            ColumnDef(key='current', label=bucket_labels['current'], col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='bucket_1', label=bucket_labels['bucket_1'], col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='bucket_2', label=bucket_labels['bucket_2'], col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='bucket_3', label=bucket_labels['bucket_3'], col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='bucket_4', label=bucket_labels['bucket_4'], col_type='currency', width=15, align='right', subtotal=True),
            ColumnDef(key='total', label='Total', col_type='currency', width=15, align='right', subtotal=True),
        ]

        # --- Rows (sorted by total descending) ---
        rows = []
        sorted_partners = sorted(
            partner_data.values(),
            key=lambda x: abs(x['total']),
            reverse=True,
        )
        for pdata in sorted_partners:
            rows.append(MatrixRow(
                level=0,
                style='detail',
                values=pdata,
            ))

        # --- Totals ---
        totals = {
            'current': sum(p['current'] for p in partner_data.values()),
            'bucket_1': sum(p['bucket_1'] for p in partner_data.values()),
            'bucket_2': sum(p['bucket_2'] for p in partner_data.values()),
            'bucket_3': sum(p['bucket_3'] for p in partner_data.values()),
            'bucket_4': sum(p['bucket_4'] for p in partner_data.values()),
            'total': sum(p['total'] for p in partner_data.values()),
        }

        # --- Assemble Shape C report ---
        title = 'Aged Receivables' if self.partner_type == 'customer' else 'Aged Payables'
        meta = build_report_meta(self, 'aged', title, 'matrix')
        colors = build_report_colors(self.company_id)

        report = ShapeCReport(
            meta=meta,
            colors=colors,
            columns=columns,
            rows=rows,
            totals=totals,
        )

        return asdict(report)

    # =========================================================================
    # Report action
    # =========================================================================

    def _return_report_action(self, data):
        action_map = {
            'customer': 'ops_matrix_accounting.action_report_aged_receivables',
            'vendor': 'ops_matrix_accounting.action_report_aged_payables',
        }
        ref = action_map.get(self.partner_type, action_map['customer'])
        report = self.env.ref(ref)
        return report.report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_filters_extra(self):
        if not self.as_of_date:
            raise UserError(_("Please set the As of Date."))
        if self.period_length < 1:
            raise UserError(_("Period length must be at least 1 day."))
        return True
