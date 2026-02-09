# -*- coding: utf-8 -*-
"""
OPS Corporate Report Parsers — Waves 1-6
=========================================
QWeb PDF report parsers for the corporate template redesign.
Each parser calls the existing wizard's _get_report_data() and transforms
the output into the flat variable dict expected by the corporate templates.
"""
from odoo import models, api
import hashlib
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


# ============================================================
# SHARED HELPER FUNCTIONS
# ============================================================

def generate_report_id(prefix):
    """Generate unique report ID: PREFIX-YYYYMMDD-HHMMSS-XXXX"""
    now = datetime.now()
    run_hash = hashlib.md5(
        f"{now.isoformat()}{prefix}".encode()
    ).hexdigest()[:4].upper()
    return f"{prefix}-{now.strftime('%Y%m%d-%H%M%S')}-{run_hash}"


def get_report_colors(company):
    """Get all report color values from company settings with safe fallbacks."""
    try:
        primary = company.ops_report_primary_color or '#5B6BBB'
    except (AttributeError, Exception):
        primary = '#5B6BBB'
    try:
        text_on_primary = company.ops_report_text_on_primary or '#FFFFFF'
    except (AttributeError, Exception):
        text_on_primary = '#FFFFFF'
    try:
        body_text_color = company.ops_report_body_text_color or '#1a1a1a'
    except (AttributeError, Exception):
        body_text_color = '#1a1a1a'
    # Compute light variant (15% blend with white)
    try:
        primary_light = company.get_report_primary_light()
    except (AttributeError, Exception):
        h = primary.lstrip('#')
        r, g, b = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
        primary_light = '#{:02x}{:02x}{:02x}'.format(
            int(r * 0.15 + 255 * 0.85),
            int(g * 0.15 + 255 * 0.85),
            int(b * 0.15 + 255 * 0.85))
    # Compute dark variant (75% factor)
    try:
        primary_dark = company.get_report_primary_dark()
    except (AttributeError, Exception):
        h = primary.lstrip('#')
        r, g, b = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
        primary_dark = '#{:02x}{:02x}{:02x}'.format(
            int(r * 0.75), int(g * 0.75), int(b * 0.75))
    return {
        'primary_color': primary,
        'text_on_primary': text_on_primary,
        'body_text_color': body_text_color,
        'primary_light': primary_light,
        'primary_dark': primary_dark,
    }


def format_date(date_val):
    """Format date to DD MMM YYYY for display."""
    if not date_val:
        return ''
    if isinstance(date_val, str):
        try:
            date_obj = datetime.strptime(date_val, '%Y-%m-%d')
            return date_obj.strftime('%d %b %Y')
        except (ValueError, TypeError):
            return date_val
    if hasattr(date_val, 'strftime'):
        return date_val.strftime('%d %b %Y')
    return str(date_val)


def format_date_long(date_val):
    """Format date to 'Wednesday, 15 January 2026' for Day Book headers."""
    if not date_val:
        return ''
    if isinstance(date_val, str):
        try:
            date_obj = datetime.strptime(date_val, '%Y-%m-%d')
            return date_obj.strftime('%A, %d %B %Y')
        except (ValueError, TypeError):
            return date_val
    if hasattr(date_val, 'strftime'):
        return date_val.strftime('%A, %d %B %Y')
    return str(date_val)


# ============================================================
# WAVE 1: CASH BOOK PARSER
# ============================================================

class OpsCashBookCorporateParser(models.AbstractModel):
    """Cash Book corporate report parser.

    Reads pre-computed data from the wizard and injects template variables.
    Template: report_cash_book_corporate
    """
    _name = 'report.ops_matrix_accounting.report_cash_book_corporate'
    _description = 'Cash Book Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.cash.book.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)

        return {
            'doc_ids': docids,
            'doc_model': 'ops.cash.book.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'currency_symbol': company.currency_id.symbol or '',
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'target_move': wizard.target_move,
            'branch_names': ', '.join(wizard.ops_branch_ids.mapped('name')) or 'All',
            'journal_names': ', '.join(wizard.journal_ids.mapped('name')),
            'report_run_id': generate_report_id('CB'),
            # Report data
            'opening_balance': report_data.get('opening_balance', 0),
            'closing_balance': report_data.get('closing_balance', 0),
            'lines': report_data.get('lines', []),
            'total_debit': report_data.get('total_debit', 0),
            'total_credit': report_data.get('total_credit', 0),
            'net_movement': report_data.get('total_debit', 0) - report_data.get('total_credit', 0),
            'line_count': len(report_data.get('lines', [])),
            # Colors
            **colors,
        }


# ============================================================
# WAVE 1: DAY BOOK PARSER
# ============================================================

class OpsDayBookCorporateParser(models.AbstractModel):
    """Day Book corporate report parser.

    Template: report_day_book_corporate
    """
    _name = 'report.ops_matrix_accounting.report_day_book_corporate'
    _description = 'Day Book Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.day.book.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)

        # Transform journals_data to include formatted headers
        journals_data = report_data.get('journals_data', [])
        total_entries = 0
        for jd in journals_data:
            for mv in jd.get('moves', []):
                total_entries += len(mv.get('lines', []))

        return {
            'doc_ids': docids,
            'doc_model': 'ops.day.book.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'currency_symbol': company.currency_id.symbol or '',
            'report_date': format_date(wizard.date),
            'report_date_long': format_date_long(wizard.date),
            'target_move': wizard.target_move,
            'branch_names': ', '.join(wizard.ops_branch_ids.mapped('name')) or 'All',
            'journal_filter': ', '.join(wizard.journal_ids.mapped('name')) or 'All',
            'report_run_id': generate_report_id('DB'),
            # Report data
            'journals_data': journals_data,
            'grand_total_debit': report_data.get('grand_total_debit', 0),
            'grand_total_credit': report_data.get('grand_total_credit', 0),
            'journal_count': len(journals_data),
            'total_entries': total_entries,
            # Colors
            **colors,
        }


# ============================================================
# WAVE 1: BANK BOOK PARSER
# ============================================================

class OpsBankBookCorporateParser(models.AbstractModel):
    """Bank Book corporate report parser.

    Template: report_bank_book_corporate
    """
    _name = 'report.ops_matrix_accounting.report_bank_book_corporate'
    _description = 'Bank Book Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.bank.book.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)

        banks_data = report_data.get('banks_data', [])
        total_lines = sum(len(b.get('lines', [])) for b in banks_data)

        return {
            'doc_ids': docids,
            'doc_model': 'ops.bank.book.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'currency_symbol': company.currency_id.symbol or '',
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'target_move': wizard.target_move,
            'branch_names': ', '.join(wizard.ops_branch_ids.mapped('name')) or 'All',
            'journal_names': ', '.join(wizard.journal_ids.mapped('name')),
            'report_run_id': generate_report_id('BK'),
            # Report data
            'banks_data': banks_data,
            'grand_opening': report_data.get('grand_opening', 0),
            'grand_closing': report_data.get('grand_closing', 0),
            'grand_debit': report_data.get('grand_debit', 0),
            'grand_credit': report_data.get('grand_credit', 0),
            'net_movement': report_data.get('grand_debit', 0) - report_data.get('grand_credit', 0),
            'bank_count': len(banks_data),
            'total_lines': total_lines,
            # Colors
            **colors,
        }


# ============================================================
# WAVE 4: ASSET REGISTER PARSER
# ============================================================

class OpsAssetRegisterCorporateParser(models.AbstractModel):
    """Asset Register corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_asset_register_corp'
    _description = 'Asset Register Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.asset.report.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)
        totals = report_data.get('totals', {})
        return {
            'doc_ids': docids,
            'doc_model': 'ops.asset.report.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('AR'),
            'as_of_date': format_date(report_data.get('as_of_date', '')),
            'report_data': report_data,
            'assets': report_data.get('data', []),
            'total_gross': totals.get('total_gross_value', 0),
            'total_depreciation': totals.get('total_accumulated_depreciation', 0),
            'total_nbv': totals.get('total_net_book_value', 0),
            'asset_count': totals.get('asset_count', 0),
            **colors,
        }


# ============================================================
# WAVE 4: DEPRECIATION SCHEDULE PARSER
# ============================================================

class OpsDepreciationScheduleCorporateParser(models.AbstractModel):
    """Depreciation Schedule corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_depreciation_sched_corp'
    _description = 'Depreciation Schedule Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.asset.report.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)
        totals = report_data.get('totals', {})
        return {
            'doc_ids': docids,
            'doc_model': 'ops.asset.report.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('DS'),
            'date_from': format_date(report_data.get('date_from', '')),
            'date_to': format_date(report_data.get('date_to', '')),
            'report_data': report_data,
            **colors,
        }


# ============================================================
# WAVE 4: PDC REGISTRY PARSER
# ============================================================

class OpsPDCRegistryCorporateParser(models.AbstractModel):
    """PDC Registry corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_treasury_registry_corporate'
    _description = 'PDC Registry Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.treasury.report.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.treasury.report.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('PR'),
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'report_data': report_data,
            **colors,
        }


# ============================================================
# WAVE 4: PDC MATURITY PARSER
# ============================================================

class OpsPDCMaturityCorporateParser(models.AbstractModel):
    """PDC Maturity Analysis corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_treasury_maturity_corporate'
    _description = 'PDC Maturity Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.treasury.report.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.treasury.report.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('PM'),
            'as_of_date': format_date(report_data.get('as_of_date', '')),
            'report_data': report_data,
            **colors,
        }


# ============================================================
# WAVE 4: PDCs IN HAND PARSER
# ============================================================

class OpsPDCsInHandCorporateParser(models.AbstractModel):
    """PDCs in Hand corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_treasury_on_hand_corporate'
    _description = 'PDCs in Hand Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.treasury.report.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard._get_report_data()
        colors = get_report_colors(company)
        return {
            'doc_ids': docids,
            'doc_model': 'ops.treasury.report.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('PH'),
            'as_of_date': format_date(report_data.get('as_of_date', '')),
            'report_data': report_data,
            **colors,
        }


# ============================================================
# WAVE 5: COMPANY CONSOLIDATION P&L PARSER
# ============================================================

class OpsCompanyConsolidationCorporateParser(models.AbstractModel):
    """Company Consolidation P&L corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_company_consol'
    _description = 'Company Consolidation P&L Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.company.consolidation'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        report_data = wizard.report_data or {}
        colors = get_report_colors(company)
        # Normalize totals key (summary mode uses 'totals', detail modes use 'summary')
        totals = report_data.get('totals', report_data.get('summary', {}))
        return {
            'doc_ids': docids,
            'doc_model': 'ops.company.consolidation',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('CC'),
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'detail_level': wizard.report_detail_level or 'summary',
            'branch_names': ', '.join(wizard.branch_ids.mapped('name')) or 'All',
            'report_data': report_data,
            'totals': totals,
            'total_income': totals.get('total_income', 0),
            'total_expense': totals.get('total_expense', 0),
            'net_profit': totals.get('net_profit', totals.get('total_net_profit', 0)),
            'branch_data': report_data.get('branch_data', []),
            'bu_data': report_data.get('bu_data', []),
            **colors,
        }


# ============================================================
# WAVE 5: BRANCH P&L PARSER
# ============================================================

class OpsBranchPLCorporateParser(models.AbstractModel):
    """Branch P&L corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_branch_pl_document'
    _description = 'Branch P&L Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.branch.report'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.branch_id.company_id or self.env.company
        report_data = wizard.report_data or {}
        colors = get_report_colors(company)
        totals = report_data.get('totals', {})
        return {
            'doc_ids': docids,
            'doc_model': 'ops.branch.report',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('BP'),
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'branch_name': wizard.branch_id.name or '',
            'branch_code': wizard.branch_id.code or '',
            'report_data': report_data,
            'totals': totals,
            'total_income': totals.get('total_income', 0),
            'total_expense': totals.get('total_expense', 0),
            'net_profit': totals.get('net_profit', 0),
            'bu_performance': report_data.get('bu_performance', []),
            'bu_count': totals.get('bu_count', 0),
            **colors,
        }


# ============================================================
# WAVE 5: BU PROFITABILITY PARSER
# ============================================================

class OpsBUProfitabilityCorporateParser(models.AbstractModel):
    """Business Unit Profitability corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_business_unit_document'
    _description = 'BU Profitability Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.business.unit.report'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        try:
            company = wizard.business_unit_id.primary_branch_id.company_id or self.env.company
        except (AttributeError, Exception):
            company = self.env.company
        report_data = wizard.report_data or {}
        colors = get_report_colors(company)
        totals = report_data.get('totals', {})
        return {
            'doc_ids': docids,
            'doc_model': 'ops.business.unit.report',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'report_run_id': generate_report_id('BU'),
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'bu_name': wizard.business_unit_id.name or '',
            'bu_code': wizard.business_unit_id.code or '',
            'report_data': report_data,
            'totals': totals,
            'total_income': totals.get('total_income', 0),
            'total_expense': totals.get('total_expense', 0),
            'net_profit': totals.get('net_profit', 0),
            'profit_margin': totals.get('profit_margin', 0),
            'branch_performance': report_data.get('branch_performance', []),
            'branch_count': totals.get('branch_count', 0),
            **colors,
        }


# ============================================================
# WAVE 5: CONSOLIDATED BALANCE SHEET PARSER
# ============================================================

class OpsConsolidatedBSCorporateParser(models.AbstractModel):
    """Consolidated Balance Sheet corporate report parser."""
    _name = 'report.ops_matrix_accounting.report_consol_balance_sheet'
    _description = 'Consolidated Balance Sheet Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.consolidated.balance.sheet'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = self.env.company
        report_data = wizard.report_data or {}
        colors = get_report_colors(company)
        consolidated = report_data.get('consolidated', {})
        return {
            'doc_ids': docids,
            'doc_model': 'ops.consolidated.balance.sheet',
            'docs': wizard,
            'company': company,
            'currency_name': wizard.currency_id.name or company.currency_id.name or '',
            'report_run_id': generate_report_id('BS'),
            'as_of_date': format_date(wizard.date),
            'company_names': ', '.join(wizard.company_ids.mapped('name')),
            'company_count': len(wizard.company_ids),
            'report_data': report_data,
            'consolidated': consolidated,
            'total_assets': consolidated.get('total_assets', 0),
            'total_liabilities': consolidated.get('total_liabilities', 0),
            'total_equity': consolidated.get('total_equity', 0),
            'companies_data': report_data.get('companies', []),
            'eliminations': report_data.get('eliminations', {}),
            **colors,
        }


# ============================================================
# WAVE 7: PARTNER LEDGER PARSER
# ============================================================

class OpsPartnerLedgerCorporateParser(models.AbstractModel):
    """Partner Ledger corporate report parser.

    Groups move lines by partner with opening balance, running balance,
    and partner type classification (Customer / Vendor / Both).
    Template: report_partner_ledger_corporate
    """
    _name = 'report.ops_matrix_accounting.report_partner_ledger_corporate'
    _description = 'Partner Ledger Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.general.ledger.wizard.enhanced'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        colors = get_report_colors(company)

        report_data = self._build_partner_ledger_data(wizard)

        return {
            'doc_ids': docids,
            'doc_model': 'ops.general.ledger.wizard.enhanced',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'currency_symbol': company.currency_id.symbol or '',
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'report_run_id': generate_report_id('PTL'),
            'branch_names': ', '.join(wizard.branch_ids.mapped('name')) or 'All',
            'partner_filter': wizard.partner_type or 'all',
            'partners': report_data['partners'],
            'grand_total_debit': report_data['grand_total_debit'],
            'grand_total_credit': report_data['grand_total_credit'],
            'grand_total_balance': report_data['grand_total_balance'],
            'partner_count': len(report_data['partners']),
            **colors,
        }

    def _build_partner_ledger_data(self, wizard):
        """Build partner ledger data with opening balances and running balances."""
        MoveLine = self.env['account.move.line']

        # Get period lines using wizard's domain
        domain = wizard._build_domain()
        lines = MoveLine.search(domain, order='partner_id, date, id')

        # Apply matrix filtering if needed
        if wizard.matrix_filter_mode == 'exact' and wizard.branch_ids and wizard.business_unit_ids:
            try:
                exact_combinations = wizard._get_exact_matrix_combinations()
                lines = lines.filtered(
                    lambda l: (l.ops_branch_id.id, l.ops_business_unit_id.id) in exact_combinations
                )
            except Exception:
                _logger.debug('Failed to apply exact matrix combination filter', exc_info=True)

        # Get opening balances per partner (before date_from)
        opening_domain = [
            ('date', '<', wizard.date_from),
            ('company_id', '=', wizard.company_id.id),
            ('move_id.state', '=', 'posted'),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
        ]
        try:
            matrix_domain = wizard._build_matrix_domain()
            if matrix_domain:
                opening_domain += matrix_domain
        except Exception:
            _logger.debug('Failed to build matrix domain for opening balances', exc_info=True)

        opening_data = MoveLine._read_group(
            domain=opening_domain,
            groupby=['partner_id'],
            aggregates=['debit:sum', 'credit:sum'],
        )
        opening_map = {}
        for item in opening_data:
            if item[0]:
                opening_map[item[0].id] = (item[1] or 0) - (item[2] or 0)

        # Group lines by partner
        partner_groups = {}
        for line in lines:
            pid = line.partner_id.id or 0
            if pid not in partner_groups:
                partner_groups[pid] = {
                    'partner': line.partner_id,
                    'lines': [],
                }
            partner_groups[pid]['lines'].append(line)

        # Include partners with opening balance but no period lines
        for pid, opening in opening_map.items():
            if pid not in partner_groups and opening != 0:
                partner = self.env['res.partner'].browse(pid)
                if partner.exists():
                    partner_groups[pid] = {'partner': partner, 'lines': []}

        partners = []
        grand_debit = grand_credit = 0

        for pid, pdata in sorted(partner_groups.items(), key=lambda x: (x[1]['partner'].name or 'ZZZ')):
            partner = pdata['partner']
            plines = pdata['lines']

            opening = opening_map.get(pid, 0)
            balance = opening
            total_d = total_c = 0
            acct_types = set()

            formatted_lines = []
            for ml in plines:
                balance += ml.debit - ml.credit
                total_d += ml.debit
                total_c += ml.credit
                acct_types.add(ml.account_id.account_type)

                formatted_lines.append({
                    'date': format_date(ml.date),
                    'journal': ml.journal_id.code or '',
                    'account': ml.account_id.code or '',
                    'reference': ml.move_id.name or '',
                    'description': ml.name or '',
                    'debit': ml.debit,
                    'credit': ml.credit,
                    'balance': balance,
                })

            has_recv = 'asset_receivable' in acct_types
            has_pay = 'liability_payable' in acct_types
            if has_recv and has_pay:
                ptype = 'both'
            elif has_recv:
                ptype = 'receivable'
            elif has_pay:
                ptype = 'payable'
            else:
                ptype = 'other'

            grand_debit += total_d
            grand_credit += total_c

            partners.append({
                'name': partner.name or 'No Partner',
                'partner_type': ptype,
                'opening_balance': opening,
                'lines': formatted_lines,
                'total_debit': total_d,
                'total_credit': total_c,
                'closing_balance': balance,
            })

        return {
            'partners': partners,
            'grand_total_debit': grand_debit,
            'grand_total_credit': grand_credit,
            'grand_total_balance': grand_debit - grand_credit,
        }


# ============================================================
# WAVE 7: BUDGET VS ACTUAL PARSER
# ============================================================

class OpsBudgetVsActualCorporateParser(models.AbstractModel):
    """Budget vs Actual corporate report parser.

    Reads budget data from the wizard and formats for the corporate template.
    Template: report_budget_vs_actual_corporate
    """
    _name = 'report.ops_matrix_accounting.report_budget_vs_actual_corporate'
    _description = 'Budget vs Actual Corporate Report Parser'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['ops.budget.vs.actual.wizard'].browse(docids)
        if len(wizard) > 1:
            wizard = wizard[0]
        company = wizard.company_id or self.env.company
        colors = get_report_colors(company)
        report_data = wizard._get_report_data()

        return {
            'doc_ids': docids,
            'doc_model': 'ops.budget.vs.actual.wizard',
            'docs': wizard,
            'company': company,
            'currency_name': company.currency_id.name or '',
            'currency_symbol': company.currency_id.symbol or '',
            'date_from': format_date(wizard.date_from),
            'date_to': format_date(wizard.date_to),
            'report_run_id': generate_report_id('BVA'),
            'branch_names': ', '.join(wizard.ops_branch_ids.mapped('name')) or 'All',
            'bu_names': ', '.join(wizard.ops_business_unit_ids.mapped('name')) or 'All',
            'groups': report_data.get('groups', []),
            'grand_budget': report_data.get('grand_budget', 0),
            'grand_actual': report_data.get('grand_actual', 0),
            'grand_committed': report_data.get('grand_committed', 0),
            'grand_available': report_data.get('grand_available', 0),
            'grand_used_pct': report_data.get('grand_used_pct', 0),
            'budget_count': report_data.get('budget_count', 0),
            **colors,
        }
