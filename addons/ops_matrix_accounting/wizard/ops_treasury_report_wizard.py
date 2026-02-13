# -*- coding: utf-8 -*-
"""
OPS Matrix Treasury Intelligence Engine (v2 Data Contracts)
============================================================

PDC analysis wizard refactored to use Shape C (matrix) data contracts.
Reports: Registry, Maturity Analysis, PDCs in Hand.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dataclasses import asdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeCReport, ColumnDef, MatrixRow,
)

_logger = logging.getLogger(__name__)


class OpsTreasuryReportWizard(models.TransientModel):
    """Treasury Intelligence - PDC Analysis Engine"""
    _name = 'ops.treasury.report.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Treasury Intelligence - PDC Report Wizard'

    # Template domain override
    report_template_id = fields.Many2one(
        domain="[('engine', '=', 'treasury'), '|', ('is_global', '=', True), ('user_id', '=', uid)]"
    )

    # ============================================
    # 1. REPORT TYPE SELECTOR
    # ============================================
    report_type = fields.Selection([
        ('registry', 'PDC Registry'),
        ('maturity', 'Maturity Analysis'),
        ('on_hand', 'PDCs in Hand'),
    ], string='Report Type', required=True, default='registry',
       help='Select the type of treasury report to generate')

    pdc_type = fields.Selection([
        ('inbound', 'Receivable (Customers)'),
        ('outbound', 'Payable (Vendors)'),
        ('both', 'Both'),
    ], string='PDC Type', required=True, default='inbound',
       help='Type of post-dated checks to analyze')

    # ============================================
    # 2. DATE FILTERS
    # ============================================
    date_from = fields.Date(string='From Date', help='Filter by maturity date from')
    date_to = fields.Date(string='To Date', help='Filter by maturity date to')
    as_of_date = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        help='Reference date for maturity analysis'
    )

    # ============================================
    # 3. DIMENSION FILTERS
    # ============================================
    branch_ids = fields.Many2many(
        'ops.branch', 'treasury_wizard_branch_rel', 'wizard_id', 'branch_id',
        string='Branches', help='Filter by specific branches. Leave empty for all.'
    )
    partner_ids = fields.Many2many(
        'res.partner', 'treasury_wizard_partner_rel', 'wizard_id', 'partner_id',
        string='Partners', help='Filter by specific customers/vendors'
    )
    bank_ids = fields.Many2many(
        'res.bank', 'treasury_wizard_bank_rel', 'wizard_id', 'bank_id',
        string='Banks', help='Filter by specific banks'
    )

    # ============================================
    # 4. STATUS FILTERS
    # ============================================
    state_filter = fields.Selection([
        ('all', 'All Statuses'),
        ('open', 'Open Only (Not Cleared)'),
        ('cleared', 'Cleared Only'),
        ('bounced', 'Bounced Only'),
    ], string='Status Filter', default='all', help='Filter by check status')

    # ============================================
    # 5. MATURITY ANALYSIS OPTIONS
    # ============================================
    period_length = fields.Integer(string='Period Length (days)', default=30,
                                   help='Number of days per aging period')

    # ============================================
    # 6. OUTPUT OPTIONS
    # ============================================
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('branch', 'By Branch'),
        ('partner', 'By Partner'),
        ('bank', 'By Bank'),
        ('state', 'By Status'),
    ], string='Group By', default='none')

    # ============================================
    # 7. COMPUTED FIELDS
    # ============================================
    total_amount = fields.Monetary(
        compute='_compute_totals', string='Total Amount', currency_field='currency_id'
    )

    # ============================================
    # BASE CLASS HOOK IMPLEMENTATIONS
    # ============================================

    def _get_engine_name(self):
        return 'treasury'

    def _get_report_shape(self):
        return 'matrix'

    def _get_report_titles(self):
        pdc_suffix = {
            'inbound': 'Receivable', 'outbound': 'Payable', 'both': 'All PDCs',
        }.get(self.pdc_type, '')
        return {
            'registry': f'PDC Registry - {pdc_suffix}',
            'maturity': f'PDC Maturity Analysis - {pdc_suffix}',
            'on_hand': f'PDCs in Hand - {pdc_suffix}',
        }

    def _get_scalar_fields_for_template(self):
        return ['report_type', 'pdc_type', 'state_filter', 'period_length', 'group_by']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'partner_ids', 'bank_ids']

    def _get_report_template_xmlid(self):
        self.ensure_one()
        mapping = {
            'registry': 'ops_matrix_accounting.report_treasury_registry_corporate',
            'maturity': 'ops_matrix_accounting.report_treasury_maturity_corporate',
            'on_hand': 'ops_matrix_accounting.report_treasury_on_hand_corporate',
        }
        return mapping.get(self.report_type, mapping['registry'])

    def _add_filter_summary_parts(self, parts):
        if self.date_from and self.date_to:
            parts[:] = [p for p in parts if not p.startswith('Period:')]
            parts.append(f"Maturity: {self.date_from} to {self.date_to}")
        elif self.date_from:
            parts[:] = [p for p in parts if not p.startswith('Period:')]
            parts.append(f"Maturity from: {self.date_from}")
        elif self.date_to:
            parts.append(f"Maturity to: {self.date_to}")
        if self.branch_ids:
            parts.append(f"Branches: {len(self.branch_ids)} selected")
        if self.partner_ids:
            parts.append(f"Partners: {len(self.partner_ids)} selected")
        if self.state_filter != 'all':
            parts.append(f"Status: {dict(self._fields['state_filter'].selection).get(self.state_filter)}")

    def _estimate_record_count(self):
        count = 0
        if self.pdc_type in ('inbound', 'both'):
            count += self.env['ops.pdc.receivable'].search_count(self._build_domain('inbound'))
        if self.pdc_type in ('outbound', 'both'):
            count += self.env['ops.pdc.payable'].search_count(self._build_domain('outbound'))
        return count

    @api.depends('pdc_type', 'branch_ids', 'partner_ids', 'date_from', 'date_to', 'state_filter')
    def _compute_totals(self):
        for wizard in self:
            try:
                total = 0.0
                if wizard.pdc_type in ('inbound', 'both'):
                    pdcs = self.env['ops.pdc.receivable'].search(wizard._build_domain('inbound'))
                    total += sum(pdcs.mapped('amount'))
                if wizard.pdc_type in ('outbound', 'both'):
                    pdcs = self.env['ops.pdc.payable'].search(wizard._build_domain('outbound'))
                    total += sum(pdcs.mapped('amount'))
                wizard.total_amount = total
            except Exception as e:
                _logger.error(f"Error calculating totals: {e}")
                wizard.total_amount = 0.0

    # ============================================
    # DOMAIN BUILDING
    # ============================================

    def _build_domain(self, pdc_type):
        """Build domain for PDC query with branch isolation."""
        self.ensure_one()
        # Branch isolation -- ALWAYS included
        domain = list(self._get_branch_filter_domain(branch_field='branch_id'))

        if self.date_from:
            domain.append(('maturity_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('maturity_date', '<=', self.date_to))
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        if self.bank_ids:
            domain.append(('bank_id', 'in', self.bank_ids.ids))

        if self.state_filter == 'open':
            if pdc_type == 'inbound':
                domain.append(('state', 'in', ['draft', 'deposited']))
            else:
                domain.append(('state', 'in', ['draft', 'issued', 'presented']))
        elif self.state_filter == 'cleared':
            domain.append(('state', '=', 'cleared'))
        elif self.state_filter == 'bounced':
            if pdc_type == 'inbound':
                domain.append(('state', '=', 'bounced'))
            else:
                domain.append(('id', '=', 0))

        if self.report_type == 'on_hand':
            if pdc_type == 'inbound':
                domain.append(('state', 'in', ['draft', 'deposited']))
            else:
                domain.append(('state', 'in', ['draft', 'issued']))

        return domain

    # ============================================
    # REPORT DATA (v2 contracts)
    # ============================================

    def _get_report_data(self):
        """Get report data as v2 ShapeCReport dict."""
        self.ensure_one()
        self._check_intelligence_access(self._get_pillar_name())

        dispatch = {
            'registry': self._get_registry_data,
            'maturity': self._get_maturity_data,
            'on_hand': self._get_on_hand_data,
        }
        return dispatch.get(self.report_type, self._get_registry_data)()

    def _get_registry_data(self):
        """PDC Registry -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'registry', self._get_report_titles()['registry'], 'matrix')
        colors = build_report_colors(self.company_id)

        columns = [
            ColumnDef(key='pdc_number', label='PDC #', col_type='string'),
            ColumnDef(key='pdc_type', label='Type', col_type='string', width=8),
            ColumnDef(key='partner', label='Partner', col_type='string'),
            ColumnDef(key='bank', label='Bank', col_type='string'),
            ColumnDef(key='amount', label='Amount', col_type='currency', align='right', subtotal=True),
            ColumnDef(key='check_date', label='Issue Date', col_type='date'),
            ColumnDef(key='maturity_date', label='Due Date', col_type='date'),
            ColumnDef(key='status', label='Status', col_type='string', width=10),
            ColumnDef(key='branch', label='Branch', col_type='string'),
        ]

        rows = []
        totals = {'inbound_total': 0.0, 'outbound_total': 0.0}

        if self.pdc_type in ('inbound', 'both'):
            pdcs = self.env['ops.pdc.receivable'].search(
                self._build_domain('inbound'), order='maturity_date, id')
            for pdc in pdcs:
                rows.append(MatrixRow(values={
                    'pdc_number': pdc.name or '',
                    'pdc_type': 'Receivable',
                    'partner': pdc.partner_id.name or '',
                    'bank': pdc.bank_id.name if pdc.bank_id else '',
                    'amount': pdc.amount,
                    'check_date': str(pdc.check_date) if pdc.check_date else '',
                    'maturity_date': str(pdc.maturity_date) if pdc.maturity_date else '',
                    'status': dict(pdc._fields['state'].selection).get(pdc.state, ''),
                    'branch': pdc.branch_id.name if pdc.branch_id else '',
                }))
                totals['inbound_total'] += pdc.amount

        if self.pdc_type in ('outbound', 'both'):
            pdcs = self.env['ops.pdc.payable'].search(
                self._build_domain('outbound'), order='maturity_date, id')
            for pdc in pdcs:
                rows.append(MatrixRow(values={
                    'pdc_number': pdc.name or '',
                    'pdc_type': 'Payable',
                    'partner': pdc.partner_id.name or '',
                    'bank': pdc.bank_id.name if pdc.bank_id else '',
                    'amount': pdc.amount,
                    'check_date': str(pdc.check_date) if pdc.check_date else '',
                    'maturity_date': str(pdc.maturity_date) if pdc.maturity_date else '',
                    'status': dict(pdc._fields['state'].selection).get(pdc.state, ''),
                    'branch': pdc.branch_id.name if pdc.branch_id else '',
                }))
                totals['outbound_total'] += pdc.amount

        totals['net_position'] = totals['inbound_total'] - totals['outbound_total']
        totals['total_count'] = len(rows)

        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_maturity_data(self):
        """PDC Maturity Analysis -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'maturity', self._get_report_titles()['maturity'], 'matrix')
        colors = build_report_colors(self.company_id)

        today = self.as_of_date or fields.Date.today()
        period = self.period_length

        columns = [
            ColumnDef(key='bucket', label='Aging Bucket', col_type='string'),
            ColumnDef(key='inbound', label='Inbound', col_type='currency', align='right', subtotal=True),
            ColumnDef(key='outbound', label='Outbound', col_type='currency', align='right', subtotal=True),
            ColumnDef(key='net', label='Net Position', col_type='currency', align='right', subtotal=True),
            ColumnDef(key='inbound_count', label='In Count', col_type='number', align='right', subtotal=True),
            ColumnDef(key='outbound_count', label='Out Count', col_type='number', align='right', subtotal=True),
        ]

        buckets = [
            ('overdue', 'Overdue'),
            ('current', 'Current (Not Due)'),
            ('period_1', f'1-{period} days'),
            ('period_2', f'{period+1}-{period*2} days'),
            ('period_3', f'{period*2+1}-{period*3} days'),
            ('period_4', f'{period*3+1}-{period*4} days'),
            ('older', f'>{period*4} days'),
        ]

        aging = {key: {'inbound': 0.0, 'outbound': 0.0, 'inbound_count': 0, 'outbound_count': 0}
                 for key, _ in buckets}

        if self.pdc_type in ('inbound', 'both'):
            domain = self._build_domain('inbound')
            domain.append(('state', 'in', ['draft', 'deposited']))
            pdcs = self.env['ops.pdc.receivable'].search(domain)
            self._age_pdcs(pdcs, aging, today, period, 'inbound')

        if self.pdc_type in ('outbound', 'both'):
            domain = self._build_domain('outbound')
            domain.append(('state', 'in', ['draft', 'issued', 'presented']))
            pdcs = self.env['ops.pdc.payable'].search(domain)
            self._age_pdcs(pdcs, aging, today, period, 'outbound')

        rows = []
        for key, label in buckets:
            b = aging[key]
            rows.append(MatrixRow(values={
                'bucket': label,
                'inbound': b['inbound'],
                'outbound': b['outbound'],
                'net': b['inbound'] - b['outbound'],
                'inbound_count': b['inbound_count'],
                'outbound_count': b['outbound_count'],
            }))

        total_in = sum(b['inbound'] for b in aging.values())
        total_out = sum(b['outbound'] for b in aging.values())
        rows.append(MatrixRow(style='grand_total', values={
            'bucket': 'Total',
            'inbound': total_in,
            'outbound': total_out,
            'net': total_in - total_out,
            'inbound_count': sum(b['inbound_count'] for b in aging.values()),
            'outbound_count': sum(b['outbound_count'] for b in aging.values()),
        }))

        totals = {'inbound_total': total_in, 'outbound_total': total_out, 'net_position': total_in - total_out}

        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    def _get_on_hand_data(self):
        """PDCs in Hand -> Shape C matrix report."""
        self.ensure_one()
        meta = build_report_meta(self, 'on_hand', self._get_report_titles()['on_hand'], 'matrix')
        colors = build_report_colors(self.company_id)

        today = fields.Date.today()

        columns = [
            ColumnDef(key='pdc_number', label='PDC #', col_type='string'),
            ColumnDef(key='pdc_type', label='Type', col_type='string', width=8),
            ColumnDef(key='partner', label='Partner', col_type='string'),
            ColumnDef(key='bank', label='Bank', col_type='string'),
            ColumnDef(key='amount', label='Amount', col_type='currency', align='right', subtotal=True),
            ColumnDef(key='maturity_date', label='Due Date', col_type='date'),
            ColumnDef(key='days_held', label='Days Held', col_type='number', align='right'),
            ColumnDef(key='status', label='Status', col_type='string'),
            ColumnDef(key='branch', label='Branch', col_type='string'),
        ]

        rows = []
        totals = {'inbound_total': 0.0, 'outbound_total': 0.0}

        if self.pdc_type in ('inbound', 'both'):
            pdcs = self.env['ops.pdc.receivable'].search(
                self._build_domain('inbound'), order='maturity_date, id')
            for pdc in pdcs:
                days_held = (today - pdc.check_date).days if pdc.check_date else 0
                rows.append(MatrixRow(values={
                    'pdc_number': pdc.name or '',
                    'pdc_type': 'Receivable',
                    'partner': pdc.partner_id.name or '',
                    'bank': pdc.bank_id.name if pdc.bank_id else '',
                    'amount': pdc.amount,
                    'maturity_date': str(pdc.maturity_date) if pdc.maturity_date else '',
                    'days_held': days_held,
                    'status': dict(pdc._fields['state'].selection).get(pdc.state, ''),
                    'branch': pdc.branch_id.name if pdc.branch_id else '',
                }))
                totals['inbound_total'] += pdc.amount

        if self.pdc_type in ('outbound', 'both'):
            pdcs = self.env['ops.pdc.payable'].search(
                self._build_domain('outbound'), order='maturity_date, id')
            for pdc in pdcs:
                days_held = (today - pdc.check_date).days if pdc.check_date else 0
                rows.append(MatrixRow(values={
                    'pdc_number': pdc.name or '',
                    'pdc_type': 'Payable',
                    'partner': pdc.partner_id.name or '',
                    'bank': pdc.bank_id.name if pdc.bank_id else '',
                    'amount': pdc.amount,
                    'maturity_date': str(pdc.maturity_date) if pdc.maturity_date else '',
                    'days_held': days_held,
                    'status': dict(pdc._fields['state'].selection).get(pdc.state, ''),
                    'branch': pdc.branch_id.name if pdc.branch_id else '',
                }))
                totals['outbound_total'] += pdc.amount

        totals['net_position'] = totals['inbound_total'] - totals['outbound_total']
        totals['total_count'] = len(rows)

        return asdict(ShapeCReport(meta=meta, colors=colors, columns=columns, rows=rows, totals=totals))

    # ============================================
    # HELPER METHODS
    # ============================================

    def _age_pdcs(self, pdcs, buckets, today, period, pdc_type):
        """Age PDCs into appropriate buckets."""
        for pdc in pdcs:
            days_to_maturity = (pdc.maturity_date - today).days
            if days_to_maturity < 0:
                bucket = 'overdue'
            elif days_to_maturity == 0:
                bucket = 'current'
            elif days_to_maturity <= period:
                bucket = 'period_1'
            elif days_to_maturity <= period * 2:
                bucket = 'period_2'
            elif days_to_maturity <= period * 3:
                bucket = 'period_3'
            elif days_to_maturity <= period * 4:
                bucket = 'period_4'
            else:
                bucket = 'older'
            buckets[bucket][pdc_type] += pdc.amount
            buckets[bucket][f'{pdc_type}_count'] += 1

    def _return_report_action(self, data):
        """Return appropriate report action for PDF generation."""
        report_refs = {
            'registry': 'ops_matrix_accounting.action_report_pdc_registry',
            'maturity': 'ops_matrix_accounting.action_report_pdc_maturity',
            'on_hand': 'ops_matrix_accounting.action_report_pdc_on_hand',
        }
        return self.env.ref(report_refs.get(self.report_type, report_refs['registry'])).report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_pdcs(self):
        """Open filtered PDCs in list view."""
        self.ensure_one()
        if self.pdc_type == 'inbound':
            model, domain, name = 'ops.pdc.receivable', self._build_domain('inbound'), _('Receivable PDCs')
        elif self.pdc_type == 'outbound':
            model, domain, name = 'ops.pdc.payable', self._build_domain('outbound'), _('Payable PDCs')
        else:
            model, domain, name = 'ops.pdc.receivable', self._build_domain('inbound'), _('Receivable PDCs')
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': model,
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'search_default_group_by_state': 1},
        }

    # ============================================
    # ONCHANGE METHODS
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type == 'maturity':
            self.state_filter = 'open'
        if self.report_type == 'on_hand':
            self.state_filter = 'all'

    @api.onchange('pdc_type')
    def _onchange_pdc_type(self):
        self.partner_ids = False
