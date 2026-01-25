# -*- coding: utf-8 -*-
"""
OPS Matrix Treasury Intelligence Engine
=======================================

Comprehensive PDC (Post-Dated Check) analysis and reporting wizard.
Provides registry, maturity analysis, and on-hand tracking for both
receivable and payable post-dated checks.

Reports Supported:
- PDC Registry: Complete list with all details
- Maturity Analysis: Grouped by aging periods
- PDCs in Hand: Open/uncleared checks only

Author: OPS Matrix Framework
Version: 1.0 (Phase 3 - Treasury Engine)
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

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
    date_from = fields.Date(
        string='From Date',
        help='Filter by maturity date from'
    )
    date_to = fields.Date(
        string='To Date',
        help='Filter by maturity date to'
    )
    as_of_date = fields.Date(
        string='As of Date',
        default=lambda self: fields.Date.context_today(self),
        help='Reference date for maturity analysis'
    )

    # ============================================
    # 3. DIMENSION FILTERS
    # ============================================
    # company_id inherited from ops.base.report.wizard

    branch_ids = fields.Many2many(
        'ops.branch',
        'treasury_wizard_branch_rel',
        'wizard_id',
        'branch_id',
        string='Branches',
        help='Filter by specific branches. Leave empty for all.'
    )

    partner_ids = fields.Many2many(
        'res.partner',
        'treasury_wizard_partner_rel',
        'wizard_id',
        'partner_id',
        string='Partners',
        help='Filter by specific customers/vendors'
    )

    bank_ids = fields.Many2many(
        'res.bank',
        'treasury_wizard_bank_rel',
        'wizard_id',
        'bank_id',
        string='Banks',
        help='Filter by specific banks'
    )

    # ============================================
    # 4. STATUS FILTERS
    # ============================================
    state_filter = fields.Selection([
        ('all', 'All Statuses'),
        ('open', 'Open Only (Not Cleared)'),
        ('cleared', 'Cleared Only'),
        ('bounced', 'Bounced Only'),
    ], string='Status Filter', default='all',
       help='Filter by check status')

    # ============================================
    # 5. MATURITY ANALYSIS OPTIONS
    # ============================================
    period_length = fields.Integer(
        string='Period Length (days)',
        default=30,
        help='Number of days per aging period'
    )

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
    # report_title, filter_summary, record_count, currency_id inherited from base

    total_amount = fields.Monetary(
        compute='_compute_totals',
        string='Total Amount',
        currency_field='currency_id'
    )

    # ============================================
    # BASE CLASS HOOK IMPLEMENTATIONS
    # ============================================

    def _get_engine_name(self):
        """Return engine name for template filtering."""
        return 'treasury'

    def _get_report_titles(self):
        """Return mapping of report_type to human-readable title."""
        # Treasury has dynamic titles based on pdc_type
        pdc_suffix = {
            'inbound': 'Receivable',
            'outbound': 'Payable',
            'both': 'All PDCs',
        }.get(self.pdc_type, '')
        return {
            'registry': f'PDC Registry - {pdc_suffix}',
            'maturity': f'PDC Maturity Analysis - {pdc_suffix}',
            'on_hand': f'PDCs in Hand - {pdc_suffix}',
        }

    def _get_scalar_fields_for_template(self):
        """Return scalar fields for template save/load."""
        return ['report_type', 'pdc_type', 'state_filter', 'period_length', 'group_by']

    def _get_m2m_fields_for_template(self):
        """Return Many2many fields for template save/load."""
        return ['branch_ids', 'partner_ids', 'bank_ids']

    def _add_filter_summary_parts(self, parts):
        """Add treasury-specific filter descriptions."""
        # Override date display for maturity dates
        if self.date_from and self.date_to:
            # Remove generic date part and add maturity-specific
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
        """Estimate number of PDCs matching filters."""
        count = 0
        if self.pdc_type in ('inbound', 'both'):
            domain = self._build_domain('inbound')
            count += self.env['ops.pdc.receivable'].search_count(domain)
        if self.pdc_type in ('outbound', 'both'):
            domain = self._build_domain('outbound')
            count += self.env['ops.pdc.payable'].search_count(domain)
        return count

    @api.depends('pdc_type', 'branch_ids', 'partner_ids', 'date_from',
                 'date_to', 'state_filter')
    def _compute_totals(self):
        """Calculate total amount of matching PDCs."""
        for wizard in self:
            try:
                total = 0.0
                if wizard.pdc_type in ('inbound', 'both'):
                    domain = wizard._build_domain('inbound')
                    pdcs = self.env['ops.pdc.receivable'].search(domain)
                    total += sum(pdcs.mapped('amount'))
                if wizard.pdc_type in ('outbound', 'both'):
                    domain = wizard._build_domain('outbound')
                    pdcs = self.env['ops.pdc.payable'].search(domain)
                    total += sum(pdcs.mapped('amount'))
                wizard.total_amount = total
            except Exception as e:
                _logger.error(f"Error calculating totals: {e}")
                wizard.total_amount = 0.0

    # ============================================
    # DOMAIN BUILDING
    # ============================================

    def _build_domain(self, pdc_type):
        """Build domain for PDC query."""
        self.ensure_one()
        domain = []

        # Date filters (maturity date)
        if self.date_from:
            domain.append(('maturity_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('maturity_date', '<=', self.date_to))

        # Branch filter
        if self.branch_ids:
            domain.append(('branch_id', 'in', self.branch_ids.ids))

        # Partner filter
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        # Bank filter
        if self.bank_ids:
            domain.append(('bank_id', 'in', self.bank_ids.ids))

        # Status filter
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
                # Payable doesn't have bounced state, return empty
                domain.append(('id', '=', 0))

        # On-hand report: only open PDCs
        if self.report_type == 'on_hand':
            if pdc_type == 'inbound':
                domain.append(('state', 'in', ['draft', 'deposited']))
            else:
                domain.append(('state', 'in', ['draft', 'issued']))

        return domain

    # ============================================
    # REPORT GENERATION
    # ============================================
    # _validate_filters and action_generate_report inherited from base

    def _get_report_data(self):
        """Get report data based on report_type."""
        self.ensure_one()

        dispatch = {
            'registry': self._get_registry_data,
            'maturity': self._get_maturity_data,
            'on_hand': self._get_on_hand_data,
        }

        handler = dispatch.get(self.report_type, self._get_registry_data)
        return handler()

    # ============================================
    # PDC REGISTRY DATA
    # ============================================

    def _get_registry_data(self):
        """Get PDC Registry report data."""
        self.ensure_one()

        inbound_data = []
        outbound_data = []

        # Fetch receivable PDCs
        if self.pdc_type in ('inbound', 'both'):
            domain = self._build_domain('inbound')
            pdcs = self.env['ops.pdc.receivable'].search(domain, order='maturity_date, id')
            inbound_data = self._process_pdc_records(pdcs, 'inbound')

        # Fetch payable PDCs
        if self.pdc_type in ('outbound', 'both'):
            domain = self._build_domain('outbound')
            pdcs = self.env['ops.pdc.payable'].search(domain, order='maturity_date, id')
            outbound_data = self._process_pdc_records(pdcs, 'outbound')

        # Calculate totals
        inbound_total = sum(p['amount'] for p in inbound_data)
        outbound_total = sum(p['amount'] for p in outbound_data)

        return {
            'report_type': 'registry',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'date_from': str(self.date_from) if self.date_from else None,
            'date_to': str(self.date_to) if self.date_to else None,
            'filters': self._get_filter_dict(),
            'pdc_type': self.pdc_type,
            'inbound': {
                'data': inbound_data,
                'total': inbound_total,
                'count': len(inbound_data),
            },
            'outbound': {
                'data': outbound_data,
                'total': outbound_total,
                'count': len(outbound_data),
            },
            'totals': {
                'inbound_total': inbound_total,
                'outbound_total': outbound_total,
                'net_position': inbound_total - outbound_total,
                'total_count': len(inbound_data) + len(outbound_data),
            },
        }

    def _process_pdc_records(self, pdcs, pdc_type):
        """Process PDC records into report format."""
        data = []
        for pdc in pdcs:
            data.append({
                'id': pdc.id,
                'name': pdc.name,
                'partner_name': pdc.partner_id.name,
                'partner_id': pdc.partner_id.id,
                'amount': pdc.amount,
                'currency': pdc.currency_id.name,
                'check_number': pdc.check_number,
                'check_date': str(pdc.check_date) if pdc.check_date else '',
                'maturity_date': str(pdc.maturity_date),
                'bank_name': pdc.bank_id.name if pdc.bank_id else '',
                'branch_name': pdc.branch_id.name if pdc.branch_id else '',
                'branch_code': pdc.branch_id.code if pdc.branch_id else '',
                'state': pdc.state,
                'state_label': dict(pdc._fields['state'].selection).get(pdc.state),
                'pdc_type': pdc_type,
                'notes': pdc.notes or '',
            })
        return data

    # ============================================
    # MATURITY ANALYSIS DATA
    # ============================================

    def _get_maturity_data(self):
        """Get PDC Maturity Analysis report data."""
        self.ensure_one()

        today = self.as_of_date or fields.Date.today()
        period = self.period_length

        # Initialize aging buckets
        aging_buckets = {
            'overdue': {'label': 'Overdue', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
            'current': {'label': 'Current (Not Due)', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
            'period_1': {'label': f'1-{period} days', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
            'period_2': {'label': f'{period+1}-{period*2} days', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
            'period_3': {'label': f'{period*2+1}-{period*3} days', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
            'period_4': {'label': f'{period*3+1}-{period*4} days', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
            'older': {'label': f'>{period*4} days', 'inbound': 0, 'outbound': 0, 'inbound_count': 0, 'outbound_count': 0},
        }

        # Process inbound PDCs
        if self.pdc_type in ('inbound', 'both'):
            domain = self._build_domain('inbound')
            # Only analyze open PDCs for maturity
            domain.append(('state', 'in', ['draft', 'deposited']))
            pdcs = self.env['ops.pdc.receivable'].search(domain)
            self._age_pdcs(pdcs, aging_buckets, today, period, 'inbound')

        # Process outbound PDCs
        if self.pdc_type in ('outbound', 'both'):
            domain = self._build_domain('outbound')
            domain.append(('state', 'in', ['draft', 'issued', 'presented']))
            pdcs = self.env['ops.pdc.payable'].search(domain)
            self._age_pdcs(pdcs, aging_buckets, today, period, 'outbound')

        # Calculate totals
        total_inbound = sum(b['inbound'] for b in aging_buckets.values())
        total_outbound = sum(b['outbound'] for b in aging_buckets.values())

        return {
            'report_type': 'maturity',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'as_of_date': str(today),
            'period_length': period,
            'filters': self._get_filter_dict(),
            'pdc_type': self.pdc_type,
            'aging_buckets': list(aging_buckets.values()),
            'totals': {
                'inbound_total': total_inbound,
                'outbound_total': total_outbound,
                'net_position': total_inbound - total_outbound,
            },
        }

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

    # ============================================
    # PDCs IN HAND DATA
    # ============================================

    def _get_on_hand_data(self):
        """Get PDCs in Hand report data."""
        self.ensure_one()

        inbound_data = []
        outbound_data = []

        # Fetch open receivable PDCs (in hand = draft or deposited)
        if self.pdc_type in ('inbound', 'both'):
            domain = self._build_domain('inbound')
            # Already filtered for on_hand in _build_domain
            pdcs = self.env['ops.pdc.receivable'].search(domain, order='maturity_date, id')
            inbound_data = self._process_pdc_records(pdcs, 'inbound')

        # Fetch open payable PDCs (in hand = draft or issued)
        if self.pdc_type in ('outbound', 'both'):
            domain = self._build_domain('outbound')
            pdcs = self.env['ops.pdc.payable'].search(domain, order='maturity_date, id')
            outbound_data = self._process_pdc_records(pdcs, 'outbound')

        # Group by branch if requested
        grouped_inbound = {}
        grouped_outbound = {}
        if self.group_by == 'branch':
            grouped_inbound = self._group_by_field(inbound_data, 'branch_name')
            grouped_outbound = self._group_by_field(outbound_data, 'branch_name')
        elif self.group_by == 'partner':
            grouped_inbound = self._group_by_field(inbound_data, 'partner_name')
            grouped_outbound = self._group_by_field(outbound_data, 'partner_name')
        elif self.group_by == 'bank':
            grouped_inbound = self._group_by_field(inbound_data, 'bank_name')
            grouped_outbound = self._group_by_field(outbound_data, 'bank_name')
        elif self.group_by == 'state':
            grouped_inbound = self._group_by_field(inbound_data, 'state_label')
            grouped_outbound = self._group_by_field(outbound_data, 'state_label')

        inbound_total = sum(p['amount'] for p in inbound_data)
        outbound_total = sum(p['amount'] for p in outbound_data)

        return {
            'report_type': 'on_hand',
            'report_title': self.report_title,
            'wizard_id': self.id,
            'company_name': self.company_id.name,
            'company_currency': self.company_id.currency_id.name,
            'as_of_date': str(fields.Date.today()),
            'filters': self._get_filter_dict(),
            'pdc_type': self.pdc_type,
            'group_by': self.group_by,
            'inbound': {
                'data': inbound_data,
                'grouped': grouped_inbound,
                'total': inbound_total,
                'count': len(inbound_data),
            },
            'outbound': {
                'data': outbound_data,
                'grouped': grouped_outbound,
                'total': outbound_total,
                'count': len(outbound_data),
            },
            'totals': {
                'inbound_total': inbound_total,
                'outbound_total': outbound_total,
                'net_position': inbound_total - outbound_total,
            },
        }

    def _group_by_field(self, data, field_name):
        """Group data by a specific field."""
        grouped = {}
        for item in data:
            key = item.get(field_name, 'Unspecified') or 'Unspecified'
            if key not in grouped:
                grouped[key] = {
                    'name': key,
                    'items': [],
                    'total': 0,
                    'count': 0,
                }
            grouped[key]['items'].append(item)
            grouped[key]['total'] += item['amount']
            grouped[key]['count'] += 1
        return list(grouped.values())

    # ============================================
    # HELPER METHODS
    # ============================================

    def _get_filter_dict(self):
        """Get filter summary as dictionary."""
        return {
            'report_type': self.report_type,
            'pdc_type': self.pdc_type,
            'date_from': str(self.date_from) if self.date_from else None,
            'date_to': str(self.date_to) if self.date_to else None,
            'branch_count': len(self.branch_ids),
            'branch_names': self.branch_ids.mapped('name') if self.branch_ids else [],
            'partner_count': len(self.partner_ids),
            'bank_count': len(self.bank_ids),
            'state_filter': self.state_filter,
            'group_by': self.group_by,
        }

    def _return_report_action(self, data):
        """Return appropriate report action."""
        report_names = {
            'registry': 'ops_matrix_accounting.report_treasury_registry',
            'maturity': 'ops_matrix_accounting.report_treasury_maturity',
            'on_hand': 'ops_matrix_accounting.report_treasury_on_hand',
        }

        return {
            'type': 'ir.actions.report',
            'report_name': report_names.get(self.report_type, report_names['registry']),
            'report_type': 'qweb-pdf',
            'data': data,
            'config': False,
        }

    # ============================================
    # ACTION METHODS
    # ============================================

    def action_view_pdcs(self):
        """Open filtered PDCs in list view."""
        self.ensure_one()

        if self.pdc_type == 'inbound':
            model = 'ops.pdc.receivable'
            domain = self._build_domain('inbound')
            name = _('Receivable PDCs')
        elif self.pdc_type == 'outbound':
            model = 'ops.pdc.payable'
            domain = self._build_domain('outbound')
            name = _('Payable PDCs')
        else:
            # Both - show receivable by default
            model = 'ops.pdc.receivable'
            domain = self._build_domain('inbound')
            name = _('Receivable PDCs')

        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': model,
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'search_default_group_by_state': 1},
        }

    def action_export_excel(self):
        """Export report to Excel."""
        self.ensure_one()

        report_data = self._get_report_data()

        return {
            'type': 'ir.actions.report',
            'report_name': 'ops_matrix_accounting.report_treasury_xlsx',
            'report_type': 'xlsx',
            'data': report_data,
            'config': False,
        }

    # ============================================
    # ONCHANGE METHODS
    # ============================================

    @api.onchange('report_type')
    def _onchange_report_type(self):
        """Adjust options based on report type."""
        if self.report_type == 'maturity':
            # Maturity analysis should focus on open PDCs
            self.state_filter = 'open'
        if self.report_type == 'on_hand':
            # On-hand shows only open
            self.state_filter = 'all'  # Domain handles it

    @api.onchange('pdc_type')
    def _onchange_pdc_type(self):
        """Clear partner filter when switching PDC type."""
        self.partner_ids = False

    # ============================================
    # SMART TEMPLATE METHODS
    # ============================================
    # _onchange_report_template_id, _get_template_config, action_save_template
    # are inherited from ops.base.report.wizard
