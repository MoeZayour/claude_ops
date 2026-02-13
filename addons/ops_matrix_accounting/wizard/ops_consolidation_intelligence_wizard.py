# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Consolidation Intelligence Wizard (v2 Data Contracts)
===============================================================================

Unified wizard for all 4 consolidation reports, refactored to use Shape B
(hierarchy) data contracts.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import date_utils
from dataclasses import asdict
from datetime import datetime
import logging

from ..report.ops_report_contracts import (
    build_report_meta, build_report_colors,
    ShapeBReport, HierarchyNode,
)

_logger = logging.getLogger(__name__)


class OpsConsolidationIntelligenceWizard(models.TransientModel):
    """Consolidation Intelligence Wizard - unified entry point for consolidated reports."""
    _name = 'ops.consolidation.intelligence.wizard'
    _inherit = 'ops.base.report.wizard'
    _description = 'Consolidation Intelligence Wizard'

    # -------------------------------------------------------------------------
    # REPORT SELECTION
    # -------------------------------------------------------------------------
    report_type = fields.Selection([
        ('company_consolidation', 'Company Consolidation P&L'),
        ('branch_pl', 'Branch Profit & Loss'),
        ('bu_report', 'Business Unit Report'),
        ('consolidated_bs', 'Consolidated Balance Sheet'),
    ], string='Report Type', required=True, default='company_consolidation')

    # -------------------------------------------------------------------------
    # COMMON FILTERS (override base to add defaults)
    # -------------------------------------------------------------------------
    date_from = fields.Date(
        string='From Date',
        default=lambda self: date_utils.start_of(datetime.now(), 'month'),
    )
    date_to = fields.Date(
        string='To Date',
        default=lambda self: date_utils.end_of(datetime.now(), 'month'),
    )
    as_of_date = fields.Date(
        string='As of Date',
        default=fields.Date.today,
        help='Balance sheet cutoff date',
    )

    # -------------------------------------------------------------------------
    # COMPANY CONSOLIDATION SPECIFIC
    # -------------------------------------------------------------------------
    report_detail_level = fields.Selection([
        ('summary', 'Summary Only'),
        ('by_branch', 'By Branch'),
        ('by_bu', 'By Business Unit'),
        ('by_account', 'By Account Group'),
    ], string='Detail Level', default='summary')

    compare_with_previous = fields.Boolean(string='Compare with Previous Period', default=True)

    # -------------------------------------------------------------------------
    # CONSOLIDATED BS SPECIFIC
    # -------------------------------------------------------------------------
    company_ids = fields.Many2many(
        'res.company', 'ops_consol_wizard_company_rel', 'wizard_id', 'company_id_rel',
        string='Companies', default=lambda self: self.env.company,
    )
    include_intercompany = fields.Boolean(string='Intercompany Eliminations', default=True)

    # -------------------------------------------------------------------------
    # BRANCH PL SPECIFIC
    # -------------------------------------------------------------------------
    branch_id = fields.Many2one('ops.branch', string='Branch',
                                 help='Select a specific branch for the Branch P&L report')

    # -------------------------------------------------------------------------
    # BU REPORT SPECIFIC
    # -------------------------------------------------------------------------
    business_unit_id = fields.Many2one('ops.business.unit', string='Business Unit',
                                       help='Select a specific business unit for the BU Report')

    # -------------------------------------------------------------------------
    # BASE CLASS HOOKS
    # -------------------------------------------------------------------------

    def _get_engine_name(self):
        return 'Financial'

    def _get_report_shape(self):
        return 'hierarchy'

    def _get_report_titles(self):
        return {
            'company_consolidation': 'Company Consolidation P&L',
            'branch_pl': 'Branch Profit & Loss',
            'bu_report': 'Business Unit Report',
            'consolidated_bs': 'Consolidated Balance Sheet',
        }

    def _get_scalar_fields_for_template(self):
        return ['report_type', 'report_detail_level', 'compare_with_previous', 'include_intercompany']

    def _get_m2m_fields_for_template(self):
        return ['branch_ids', 'business_unit_ids', 'company_ids']

    def _get_report_template_xmlid(self):
        self.ensure_one()
        mapping = {
            'company_consolidation': 'ops_matrix_accounting.report_company_consolidation_corporate',
            'branch_pl': 'ops_matrix_accounting.report_branch_pl_corporate',
            'bu_report': 'ops_matrix_accounting.report_business_unit_corporate',
            'consolidated_bs': 'ops_matrix_accounting.report_consolidated_bs_corporate',
        }
        return mapping.get(self.report_type, mapping['company_consolidation'])

    def _add_filter_summary_parts(self, parts):
        if self.branch_ids:
            parts.append(f"Branches: {len(self.branch_ids)} selected")
        if self.business_unit_ids:
            parts.append(f"BUs: {len(self.business_unit_ids)} selected")
        if self.report_detail_level and self.report_detail_level != 'summary':
            parts.append(f"Detail: {dict(self._fields['report_detail_level'].selection).get(self.report_detail_level)}")
        if self.compare_with_previous:
            parts.append("vs Previous Period")

    def _estimate_record_count(self):
        return 0  # Consolidation doesn't have a simple record count

    # -------------------------------------------------------------------------
    # REPORT DATA (v2 contracts)
    # -------------------------------------------------------------------------

    def _get_report_data(self):
        """Build consolidation report data as Shape B (hierarchy)."""
        self.ensure_one()
        self._check_intelligence_access(self._get_pillar_name())

        dispatch = {
            'company_consolidation': self._get_company_consolidation_data,
            'branch_pl': self._get_branch_pl_data,
            'bu_report': self._get_bu_report_data,
            'consolidated_bs': self._get_consolidated_bs_data,
        }
        return dispatch.get(self.report_type, self._get_company_consolidation_data)()

    def _build_account_hierarchy(self, move_lines, value_column_keys):
        """Build hierarchical P&L/BS structure from move lines.

        Groups by account type -> account group -> account.
        Returns list of HierarchyNode sections.
        """
        # Group by account type
        type_groups = {}
        for line in move_lines:
            acct = line.account_id
            atype = acct.account_type or 'other'
            type_label = dict(self.env['account.account']._fields['account_type'].selection).get(atype, atype)

            if atype not in type_groups:
                type_groups[atype] = {
                    'label': type_label,
                    'accounts': {},
                }

            aid = acct.id
            if aid not in type_groups[atype]['accounts']:
                type_groups[atype]['accounts'][aid] = {
                    'code': acct.code or '',
                    'name': acct.name or '',
                    'values': {k: 0.0 for k in value_column_keys},
                }

            # Determine which column this line belongs to (first key for simple reports)
            col_key = value_column_keys[0] if value_column_keys else 'amount'
            type_groups[atype]['accounts'][aid]['values'][col_key] += line.balance

        # Build hierarchy nodes
        sections = []
        for atype in ['income', 'income_other', 'expense_direct_cost', 'expense', 'expense_depreciation']:
            if atype not in type_groups:
                continue
            group = type_groups[atype]
            children = []
            section_values = {k: 0.0 for k in value_column_keys}

            for _aid, adata in sorted(group['accounts'].items(), key=lambda x: x[1]['code']):
                children.append(HierarchyNode(
                    code=adata['code'], name=adata['name'],
                    level=2, style='detail', values=adata['values'],
                ))
                for k in value_column_keys:
                    section_values[k] += adata['values'].get(k, 0.0)

            sections.append(HierarchyNode(
                code='', name=group['label'],
                level=0, style='section', values=section_values,
                children=children,
            ))

        return sections

    def _get_company_consolidation_data(self):
        """Company Consolidation P&L -> Shape B hierarchy."""
        self.ensure_one()
        meta = build_report_meta(self, 'company_consolidation', 'Company Consolidation P&L', 'hierarchy')
        colors = build_report_colors(self.company_id)

        # Determine value columns - one per entity being consolidated
        branches = self.branch_ids or self.env['ops.branch'].search([
            ('company_id', '=', self.company_id.id)])
        value_columns = [{'key': f'branch_{b.id}', 'label': b.name} for b in branches]
        value_columns.append({'key': 'total', 'label': 'Total'})
        col_keys = [vc['key'] for vc in value_columns]

        # Build account hierarchy with branch breakdown
        domain = [
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.account_type', 'in', ['income', 'income_other', 'expense', 'expense_direct_cost', 'expense_depreciation']),
        ]
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()
        if self.branch_ids:
            domain.append(('ops_branch_id', 'in', self.branch_ids.ids))

        lines = self.env['account.move.line'].search(domain)

        # Group by account, then by branch
        acct_data = {}
        for line in lines:
            acct = line.account_id
            aid = acct.id
            if aid not in acct_data:
                acct_data[aid] = {
                    'code': acct.code or '',
                    'name': acct.name or '',
                    'type': acct.account_type,
                    'values': {k: 0.0 for k in col_keys},
                }
            branch_key = f'branch_{line.ops_branch_id.id}' if line.ops_branch_id else 'total'
            if branch_key in acct_data[aid]['values']:
                acct_data[aid]['values'][branch_key] += line.balance
            acct_data[aid]['values']['total'] += line.balance

        # Build sections by account type
        type_order = ['income', 'income_other', 'expense_direct_cost', 'expense', 'expense_depreciation']
        type_labels = {
            'income': 'Revenue', 'income_other': 'Other Income',
            'expense_direct_cost': 'Cost of Revenue', 'expense': 'Operating Expenses',
            'expense_depreciation': 'Depreciation',
        }
        sections = []
        net_values = {k: 0.0 for k in col_keys}

        for atype in type_order:
            children = []
            section_values = {k: 0.0 for k in col_keys}
            for _aid, adata in sorted(
                ((a, d) for a, d in acct_data.items() if d['type'] == atype),
                key=lambda x: x[1]['code']
            ):
                children.append(HierarchyNode(
                    code=adata['code'], name=adata['name'],
                    level=2, style='detail', values=adata['values'],
                ))
                for k in col_keys:
                    section_values[k] += adata['values'].get(k, 0.0)

            if children:
                sections.append(HierarchyNode(
                    code='', name=type_labels.get(atype, atype),
                    level=0, style='section', values=section_values,
                    children=children,
                ))
                sign = -1 if atype.startswith('income') else 1
                for k in col_keys:
                    net_values[k] += section_values[k] * sign

        net_result = HierarchyNode(
            code='', name='Net Result', level=0, style='grand_total',
            values={k: -v for k, v in net_values.items()},
        )

        return asdict(ShapeBReport(
            meta=meta, colors=colors, value_columns=value_columns,
            sections=sections, net_result=net_result,
        ))

    def _get_branch_pl_data(self):
        """Branch P&L -> Shape B hierarchy."""
        self.ensure_one()
        if not self.branch_id:
            raise UserError(_('Please select a Branch for the Branch P&L report.'))

        meta = build_report_meta(self, 'branch_pl', f'Branch P&L - {self.branch_id.name}', 'hierarchy')
        colors = build_report_colors(self.company_id)

        value_columns = [{'key': 'actual', 'label': 'Actual'}]
        if self.compare_with_previous:
            value_columns.append({'key': 'previous', 'label': 'Previous Period'})
            value_columns.append({'key': 'variance', 'label': 'Variance'})
        col_keys = [vc['key'] for vc in value_columns]

        domain = [
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
            ('ops_branch_id', '=', self.branch_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.account_type', 'in', ['income', 'income_other', 'expense', 'expense_direct_cost', 'expense_depreciation']),
        ]
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()
        lines = self.env['account.move.line'].search(domain)
        sections = self._build_account_hierarchy(lines, ['actual'])

        if self.compare_with_previous:
            # Get previous period
            period_delta = (self.date_to - self.date_from).days + 1
            from dateutil.relativedelta import relativedelta as rd
            prev_from = self.date_from - rd(days=period_delta)
            prev_to = self.date_to - rd(days=period_delta)
            prev_domain = [
                ('move_id.state', '=', 'posted'),
                ('company_id', '=', self.company_id.id),
                ('ops_branch_id', '=', self.branch_id.id),
                ('date', '>=', prev_from),
                ('date', '<=', prev_to),
                ('account_id.account_type', 'in', ['income', 'income_other', 'expense', 'expense_direct_cost', 'expense_depreciation']),
            ]
            # Branch isolation
            prev_domain += self._get_branch_filter_domain()
            prev_lines = self.env['account.move.line'].search(prev_domain)
            prev_sections = self._build_account_hierarchy(prev_lines, ['previous'])

            # Merge previous data into main sections
            prev_map = {}
            for ps in prev_sections:
                for child in ps.children:
                    prev_map[child.code] = child.values.get('previous', 0.0)

            for section in sections:
                section.values['previous'] = 0.0
                section.values['variance'] = 0.0
                for child in section.children:
                    child.values['previous'] = prev_map.get(child.code, 0.0)
                    child.values['variance'] = child.values.get('actual', 0.0) - child.values.get('previous', 0.0)
                    section.values['previous'] += child.values['previous']
                    section.values['variance'] += child.values['variance']

        return asdict(ShapeBReport(meta=meta, colors=colors, value_columns=value_columns, sections=sections))

    def _get_bu_report_data(self):
        """Business Unit Report -> Shape B hierarchy."""
        self.ensure_one()
        if not self.business_unit_id:
            raise UserError(_('Please select a Business Unit for the BU Report.'))

        meta = build_report_meta(self, 'bu_report', f'BU Report - {self.business_unit_id.name}', 'hierarchy')
        colors = build_report_colors(self.company_id)

        value_columns = [{'key': 'actual', 'label': 'Actual'}]
        col_keys = [vc['key'] for vc in value_columns]

        domain = [
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
            ('ops_business_unit_id', '=', self.business_unit_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id.account_type', 'in', ['income', 'income_other', 'expense', 'expense_direct_cost', 'expense_depreciation']),
        ]
        # Branch isolation -- ALWAYS included
        domain += self._get_branch_filter_domain()
        lines = self.env['account.move.line'].search(domain)
        sections = self._build_account_hierarchy(lines, col_keys)

        return asdict(ShapeBReport(meta=meta, colors=colors, value_columns=value_columns, sections=sections))

    def _get_consolidated_bs_data(self):
        """Consolidated Balance Sheet -> Shape B hierarchy."""
        self.ensure_one()
        companies = self.company_ids if self.company_ids else self.company_id
        bs_date = self.as_of_date or fields.Date.today()

        meta = build_report_meta(self, 'consolidated_bs', 'Consolidated Balance Sheet', 'hierarchy')
        colors = build_report_colors(self.company_id)

        value_columns = [{'key': f'co_{c.id}', 'label': c.name} for c in companies]
        value_columns.append({'key': 'total', 'label': 'Total'})
        col_keys = [vc['key'] for vc in value_columns]

        bs_types = [
            'asset_receivable', 'asset_cash', 'asset_current', 'asset_non_current',
            'asset_prepayments', 'asset_fixed',
            'liability_payable', 'liability_credit_card', 'liability_current', 'liability_non_current',
            'equity', 'equity_unaffected',
        ]

        acct_data = {}
        for company in companies:
            domain = [
                ('move_id.state', '=', 'posted'),
                ('company_id', '=', company.id),
                ('date', '<=', bs_date),
                ('account_id.account_type', 'in', bs_types),
            ]
            # Branch isolation -- ALWAYS included
            domain += self._get_branch_filter_domain()
            lines = self.env['account.move.line'].search(domain)
            co_key = f'co_{company.id}'

            for line in lines:
                acct = line.account_id
                aid = acct.id
                if aid not in acct_data:
                    acct_data[aid] = {
                        'code': acct.code or '',
                        'name': acct.name or '',
                        'type': acct.account_type,
                        'values': {k: 0.0 for k in col_keys},
                    }
                acct_data[aid]['values'][co_key] += line.balance
                acct_data[aid]['values']['total'] += line.balance

        type_labels = {
            'asset_receivable': 'Receivables', 'asset_cash': 'Cash & Bank',
            'asset_current': 'Current Assets', 'asset_non_current': 'Non-Current Assets',
            'asset_prepayments': 'Prepayments', 'asset_fixed': 'Fixed Assets',
            'liability_payable': 'Payables', 'liability_credit_card': 'Credit Cards',
            'liability_current': 'Current Liabilities', 'liability_non_current': 'Non-Current Liabilities',
            'equity': 'Equity', 'equity_unaffected': 'Retained Earnings',
        }

        sections = []
        for atype in bs_types:
            children = []
            section_values = {k: 0.0 for k in col_keys}
            for _aid, adata in sorted(
                ((a, d) for a, d in acct_data.items() if d['type'] == atype),
                key=lambda x: x[1]['code']
            ):
                children.append(HierarchyNode(
                    code=adata['code'], name=adata['name'],
                    level=2, style='detail', values=adata['values'],
                ))
                for k in col_keys:
                    section_values[k] += adata['values'].get(k, 0.0)

            if children:
                sections.append(HierarchyNode(
                    code='', name=type_labels.get(atype, atype),
                    level=0, style='section', values=section_values,
                    children=children,
                ))

        return asdict(ShapeBReport(meta=meta, colors=colors, value_columns=value_columns, sections=sections))

    # -------------------------------------------------------------------------
    # REPORT ACTION
    # -------------------------------------------------------------------------

    def _return_report_action(self, data):
        """Return appropriate report action for PDF generation."""
        report_refs = {
            'company_consolidation': 'ops_matrix_accounting.action_report_company_consolidation',
            'branch_pl': 'ops_matrix_accounting.action_report_branch_pnl',
            'bu_report': 'ops_matrix_accounting.action_report_bu_report',
            'consolidated_bs': 'ops_matrix_accounting.action_report_consolidated_bs',
        }
        ref = report_refs.get(self.report_type, report_refs['company_consolidation'])
        return self.env.ref(ref).report_action(
            self, data={'wizard_id': self.id, 'wizard_model': self._name},
        )

    # -------------------------------------------------------------------------
    # LEGACY COMPATIBILITY
    # -------------------------------------------------------------------------
    def action_generate(self):
        """Legacy entry point - delegate to base class action_generate_report."""
        return self.action_generate_report()
