# -*- coding: utf-8 -*-
"""
OPS Matrix Accounting - Corporate Balance Sheet Wizard
======================================================

IAS 1 compliant Balance Sheet with:
- Current + Prior Period comparison
- Account-level detail within each section
- Branch/BU filtering capability
- Balance verification indicator

Author: OPS Matrix Framework
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging
import xlsxwriter
from io import BytesIO
import base64
from ..report.excel_styles import get_corporate_excel_formats

_logger = logging.getLogger(__name__)


class OpsBalanceSheetWizard(models.TransientModel):
    """Corporate Balance Sheet Wizard - IAS 1 Compliant"""
    _name = 'ops.balance.sheet.wizard'
    _inherit = ['ops.intelligence.security.mixin']  # Security mixin for IT Admin Blindness
    _description = 'Corporate Balance Sheet Wizard'

    # -------------------------------------------------------------------------
    # WIZARD FIELDS
    # -------------------------------------------------------------------------
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    date_end = fields.Date(
        string='As of Date',
        required=True,
        default=fields.Date.context_today
    )

    show_comparison = fields.Boolean(
        string='Show Comparative Period',
        default=True
    )

    comparison_type = fields.Selection([
        ('year', 'Same Date Last Year'),
        ('month', 'Same Date Last Month'),
        ('quarter', 'Same Date Last Quarter'),
        ('custom', 'Custom Date'),
    ], string='Comparison Type', default='year')

    date_comparison = fields.Date(
        string='Comparative Date',
        compute='_compute_date_comparison',
        store=True,
        readonly=False
    )

    # Branch/BU Filtering
    ops_branch_ids = fields.Many2many(
        'ops.branch',
        'ops_bs_wizard_branch_rel',
        'wizard_id',
        'branch_id',
        string='Branches',
        help='Leave empty for consolidated view'
    )

    ops_business_unit_ids = fields.Many2many(
        'ops.business.unit',
        'ops_bs_wizard_bu_rel',
        'wizard_id',
        'bu_id',
        string='Business Units',
        help='Leave empty for all business units'
    )

    # Display Options
    show_zero_balances = fields.Boolean(
        string='Show Zero Balances',
        default=False
    )

    show_account_codes = fields.Boolean(
        string='Show Account Codes',
        default=True
    )

    hierarchy_level = fields.Selection([
        ('summary', 'Summary Only (Section Totals)'),
        ('standard', 'Standard (Account Groups)'),
        ('detailed', 'Detailed (All Accounts)'),
    ], string='Detail Level', default='standard')

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    target_move = fields.Selection([
        ('posted', 'Posted Entries Only'),
        ('all', 'All Entries'),
    ], string='Target Moves', default='posted', required=True)

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------
    @api.depends('date_end', 'comparison_type', 'show_comparison')
    def _compute_date_comparison(self):
        for wizard in self:
            if not wizard.show_comparison or not wizard.date_end:
                wizard.date_comparison = False
            elif wizard.comparison_type == 'year':
                wizard.date_comparison = wizard.date_end - relativedelta(years=1)
            elif wizard.comparison_type == 'month':
                wizard.date_comparison = wizard.date_end - relativedelta(months=1)
            elif wizard.comparison_type == 'quarter':
                wizard.date_comparison = wizard.date_end - relativedelta(months=3)
            # 'custom' leaves it as manually set

    # -------------------------------------------------------------------------
    # DATA FETCHING METHODS
    # -------------------------------------------------------------------------
    def _get_account_balances(self, date_to, branch_ids=None, bu_ids=None):
        """
        Fetch account balances as of a specific date.
        Returns dict: {account_id: balance}

        Balance Sheet accounts use cumulative balance from beginning of time.
        """
        self.ensure_one()

        domain = [
            ('date', '<=', date_to),
            ('company_id', '=', self.company_id.id),
        ]

        # Filter by move state
        if self.target_move == 'posted':
            domain.append(('parent_state', '=', 'posted'))

        # Branch filtering
        if branch_ids:
            domain.append(('ops_branch_id', 'in', branch_ids.ids))

        # BU filtering
        if bu_ids:
            domain.append(('ops_business_unit_id', 'in', bu_ids.ids))

        # Only Balance Sheet accounts (Assets, Liabilities, Equity)
        # These have include_initial_balance = True
        domain.append(('account_id.include_initial_balance', '=', True))

        # Read grouped data
        aml_data = self.env['account.move.line'].read_group(
            domain=domain,
            fields=['account_id', 'balance:sum'],
            groupby=['account_id'],
            lazy=False
        )

        return {item['account_id'][0]: item['balance'] for item in aml_data if item['account_id']}

    def _classify_account(self, account):
        """
        Classify account into Balance Sheet sections based on account_type.
        Returns tuple: (section, subsection)
        """
        acc_type = account.account_type or ''

        # Asset classification
        if acc_type in ('asset_receivable', 'asset_cash', 'asset_current', 'asset_prepayments'):
            return ('assets', 'current')
        elif acc_type in ('asset_fixed', 'asset_non_current'):
            return ('assets', 'non_current')

        # Liability classification
        elif acc_type in ('liability_payable', 'liability_credit_card', 'liability_current'):
            return ('liabilities', 'current')
        elif acc_type in ('liability_non_current',):
            return ('liabilities', 'non_current')

        # Equity classification
        elif acc_type in ('equity', 'equity_unaffected'):
            return ('equity', 'equity')

        # Unknown - skip
        return (None, None)

    def _get_account_hierarchy(self):
        """
        Build the Balance Sheet structure based on account types.
        Returns structured dict for template rendering.
        """
        self.ensure_one()

        # Get all BS accounts for the company
        # Note: Odoo 19 uses company_ids (Many2many) not company_id
        accounts = self.env['account.account'].search([
            ('company_ids', 'in', [self.company_id.id]),
            ('include_initial_balance', '=', True),  # BS accounts only
        ])

        # Fetch balances for current period
        balances_current = self._get_account_balances(
            self.date_end,
            self.ops_branch_ids,
            self.ops_business_unit_ids
        )

        # Fetch balances for comparison period
        balances_comparison = {}
        if self.show_comparison and self.date_comparison:
            balances_comparison = self._get_account_balances(
                self.date_comparison,
                self.ops_branch_ids,
                self.ops_business_unit_ids
            )

        # Structure the data
        structure = {
            'assets': {
                'current': [],
                'non_current': [],
                'total': 0,
                'total_comparison': 0,
                'current_total': 0,
                'current_total_comparison': 0,
                'non_current_total': 0,
                'non_current_total_comparison': 0,
            },
            'liabilities': {
                'current': [],
                'non_current': [],
                'total': 0,
                'total_comparison': 0,
                'current_total': 0,
                'current_total_comparison': 0,
                'non_current_total': 0,
                'non_current_total_comparison': 0,
            },
            'equity': {
                'lines': [],
                'total': 0,
                'total_comparison': 0,
            },
        }

        # Classify accounts
        for account in accounts:
            balance = balances_current.get(account.id, 0)
            balance_comp = balances_comparison.get(account.id, 0)

            # Skip zero balances if option selected
            if not self.show_zero_balances and balance == 0 and balance_comp == 0:
                continue

            section, subsection = self._classify_account(account)
            if not section:
                continue

            # Calculate variance
            variance = balance - balance_comp
            variance_pct = 0
            if balance_comp and balance_comp != 0:
                variance_pct = (variance / abs(balance_comp)) * 100

            line = {
                'account_id': account.id,
                'code': account.code if self.show_account_codes else '',
                'name': account.name,
                'balance': balance,
                'balance_comparison': balance_comp,
                'variance': variance,
                'variance_pct': variance_pct,
            }

            if section == 'assets':
                if subsection == 'current':
                    structure['assets']['current'].append(line)
                    structure['assets']['current_total'] += balance
                    structure['assets']['current_total_comparison'] += balance_comp
                else:
                    structure['assets']['non_current'].append(line)
                    structure['assets']['non_current_total'] += balance
                    structure['assets']['non_current_total_comparison'] += balance_comp
                structure['assets']['total'] += balance
                structure['assets']['total_comparison'] += balance_comp

            elif section == 'liabilities':
                if subsection == 'current':
                    structure['liabilities']['current'].append(line)
                    structure['liabilities']['current_total'] += balance
                    structure['liabilities']['current_total_comparison'] += balance_comp
                else:
                    structure['liabilities']['non_current'].append(line)
                    structure['liabilities']['non_current_total'] += balance
                    structure['liabilities']['non_current_total_comparison'] += balance_comp
                structure['liabilities']['total'] += balance
                structure['liabilities']['total_comparison'] += balance_comp

            elif section == 'equity':
                structure['equity']['lines'].append(line)
                structure['equity']['total'] += balance
                structure['equity']['total_comparison'] += balance_comp

        # Sort by account code
        for subsection in ['current', 'non_current']:
            structure['assets'][subsection].sort(key=lambda x: x.get('code', ''))
            structure['liabilities'][subsection].sort(key=lambda x: x.get('code', ''))
        structure['equity']['lines'].sort(key=lambda x: x.get('code', ''))

        return structure

    def _prepare_report_data(self):
        """
        Prepare complete data structure for the Balance Sheet template.
        """
        self.ensure_one()

        hierarchy = self._get_account_hierarchy()

        # Assets are positive, Liabilities and Equity are negative in standard accounting
        # For display, we show absolute values for L&E
        total_assets = hierarchy['assets']['total']
        total_liabilities = abs(hierarchy['liabilities']['total'])
        total_equity = abs(hierarchy['equity']['total'])
        total_liab_equity = total_liabilities + total_equity

        # Comparison totals
        total_assets_comp = hierarchy['assets']['total_comparison']
        total_liabilities_comp = abs(hierarchy['liabilities']['total_comparison'])
        total_equity_comp = abs(hierarchy['equity']['total_comparison'])
        total_liab_equity_comp = total_liabilities_comp + total_equity_comp

        # Calculate balance check
        # In accounting: Assets = Liabilities + Equity
        # Both sides should be equal
        is_balanced = abs(total_assets - total_liab_equity) < 0.01
        balance_difference = total_assets - total_liab_equity

        return {
            # Header info
            'company': self.company_id,
            'date_end': self.date_end,
            'date_comparison': self.date_comparison if self.show_comparison else None,
            'show_comparison': self.show_comparison,
            'currency': self.currency_id,
            'hierarchy_level': self.hierarchy_level,

            # Filters applied
            'branches': self.ops_branch_ids,
            'business_units': self.ops_business_unit_ids,
            'is_consolidated': not self.ops_branch_ids,
            'target_move': self.target_move,

            # Account data (raw - balances as-is from GL)
            'assets': hierarchy['assets'],
            'liabilities': hierarchy['liabilities'],
            'equity': hierarchy['equity'],

            # Display totals (absolute values for L&E)
            'total_assets': total_assets,
            'total_assets_comparison': total_assets_comp,
            'total_liabilities': total_liabilities,
            'total_liabilities_comparison': total_liabilities_comp,
            'total_equity': total_equity,
            'total_equity_comparison': total_equity_comp,
            'total_liab_equity': total_liab_equity,
            'total_liab_equity_comparison': total_liab_equity_comp,

            # Subtotals
            'current_assets_total': hierarchy['assets']['current_total'],
            'current_assets_total_comparison': hierarchy['assets']['current_total_comparison'],
            'non_current_assets_total': hierarchy['assets']['non_current_total'],
            'non_current_assets_total_comparison': hierarchy['assets']['non_current_total_comparison'],
            'current_liabilities_total': abs(hierarchy['liabilities']['current_total']),
            'current_liabilities_total_comparison': abs(hierarchy['liabilities']['current_total_comparison']),
            'non_current_liabilities_total': abs(hierarchy['liabilities']['non_current_total']),
            'non_current_liabilities_total_comparison': abs(hierarchy['liabilities']['non_current_total_comparison']),

            # Balance verification
            'is_balanced': is_balanced,
            'balance_difference': balance_difference,

            # Generation metadata
            'generated_by': self.env.user.name,
            'generated_at': fields.Datetime.now(),
        }

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------
    def action_view_report(self):
        """Open report in UI View mode (browser preview with toolbar)."""
        self.ensure_one()

        # Get report template name
        template_name = self._get_report_template_xmlid()

        # Return action to open in new tab with controller
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = f'{base_url}/ops/report/html/{template_name}?wizard_id={self.id}'

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def _get_report_template_xmlid(self):
        """Return XML ID of the balance sheet report template."""
        return 'ops_matrix_accounting.report_balance_sheet'

    def action_generate_pdf(self):
        """Generate PDF Balance Sheet report."""
        self.ensure_one()

        # Security: Check IT Admin Blindness & Persona Access
        self._check_intelligence_access('Financial')

        # Security: Validate branch access if branches are selected
        if self.ops_branch_ids:
            self._validate_branch_access(self.ops_branch_ids)

        # Audit: Log report generation
        self._log_intelligence_report(
            pillar='Financial',
            report_type='Balance Sheet',
            filters_dict={
                'date_end': str(self.date_end),
                'show_comparison': self.show_comparison,
                'branches': self.ops_branch_ids.mapped('name'),
                'target_move': self.target_move,
            },
            output_format='pdf'
        )

        return self.env.ref(
            'ops_matrix_accounting.report_balance_sheet_corporate'
        ).report_action(self)

    def action_preview(self):
        """Preview the Balance Sheet in a form view."""
        self.ensure_one()

        # Security: Check IT Admin Blindness & Persona Access
        self._check_intelligence_access('Financial')

        # Security: Validate branch access if branches are selected
        if self.ops_branch_ids:
            self._validate_branch_access(self.ops_branch_ids)

        return {
            'name': _('Balance Sheet Preview'),
            'type': 'ir.actions.act_window',
            'res_model': 'ops.balance.sheet.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'preview_mode': True},
        }

    def action_generate_xlsx(self):
        """Generate Excel Balance Sheet with corporate formatting."""
        self.ensure_one()

        # Security: Check IT Admin Blindness & Persona Access
        self._check_intelligence_access('Financial')

        # Security: Validate branch access if branches are selected
        if self.ops_branch_ids:
            self._validate_branch_access(self.ops_branch_ids)

        # Get report data
        report_data = self._prepare_report_data()

        # Generate Excel file
        try:
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})

            # Get corporate formats
            formats = get_corporate_excel_formats(workbook, self.company_id)

            # Create worksheet
            worksheet = workbook.add_worksheet('Balance Sheet')

            # Set column widths
            worksheet.set_column(0, 0, 50)  # Account name
            worksheet.set_column(1, 1, 18)  # Current period
            if self.show_comparison:
                worksheet.set_column(2, 2, 18)  # Comparison period
                worksheet.set_column(3, 3, 18)  # Variance
                worksheet.set_column(4, 4, 12)  # Variance %

            # Write header block (rows 0-5)
            row = 0
            worksheet.write(row, 0, report_data['company'].name, formats['company_name'])
            row += 1
            worksheet.write(row, 0, 'Balance Sheet', formats['report_title'])
            row += 1
            worksheet.write(row, 0, f"As of: {report_data['date_end']}", formats['metadata'])
            row += 1

            if report_data['show_comparison']:
                worksheet.write(row, 0, f"Comparison: {report_data['date_comparison']}", formats['metadata'])
                row += 1

            # Filters
            if report_data['branches']:
                worksheet.write(row, 0, f"Branches: {', '.join(report_data['branches'].mapped('name'))}", formats['metadata'])
                row += 1
            elif report_data['is_consolidated']:
                worksheet.write(row, 0, "Scope: Consolidated (All Branches)", formats['metadata'])
                row += 1

            worksheet.write(row, 0, f"Currency: {report_data['currency'].name}", formats['metadata'])
            row += 2

            # Write table headers (row 7)
            worksheet.write(row, 0, 'Account', formats['table_header'])
            worksheet.write(row, 1, str(report_data['date_end']), formats['table_header_num'])
            col_idx = 2
            if self.show_comparison:
                worksheet.write(row, col_idx, str(report_data['date_comparison']), formats['table_header_num'])
                col_idx += 1
                worksheet.write(row, col_idx, 'Variance', formats['table_header_num'])
                col_idx += 1
                worksheet.write(row, col_idx, 'Variance %', formats['table_header_num'])
            row += 1

            # Freeze panes at row 8 (after headers)
            worksheet.freeze_panes(row, 0)

            # Write Assets section
            row = self._write_balance_sheet_section(
                worksheet, formats, row,
                'ASSETS',
                report_data['assets'],
                report_data
            )
            row += 1

            # Write Liabilities section
            row = self._write_balance_sheet_section(
                worksheet, formats, row,
                'LIABILITIES',
                report_data['liabilities'],
                report_data,
                negate_values=True
            )
            row += 1

            # Write Equity section
            row = self._write_balance_sheet_section(
                worksheet, formats, row,
                'EQUITY',
                report_data['equity'],
                report_data,
                negate_values=True
            )
            row += 1

            # Write balance verification
            worksheet.write(row, 0, 'BALANCE CHECK', formats['total_label'])
            balance_diff = report_data['balance_difference']
            balance_status = 'BALANCED' if report_data['is_balanced'] else f'OUT OF BALANCE ({balance_diff:,.2f})'
            if self.show_comparison:
                worksheet.write(row, 1, balance_status, formats['total_label'])
                worksheet.write(row, 2, '', formats['total_label'])
                worksheet.write(row, 3, '', formats['total_label'])
                worksheet.write(row, 4, '', formats['total_label'])
            else:
                worksheet.write(row, 1, balance_status, formats['total_label'])

            # Set print options
            worksheet.set_landscape()
            worksheet.set_paper(9)  # A4
            worksheet.fit_to_pages(1, 0)  # Fit to 1 page wide

            # Close workbook
            workbook.close()
            output.seek(0)

            # Create attachment
            date_str = self.date_end.strftime('%Y%m%d')
            filename = f"Balance_Sheet_{date_str}.xlsx"

            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(output.read()),
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            })

            # Audit: Log report generation
            self._log_intelligence_report(
                pillar='Financial',
                report_type='Balance Sheet',
                filters_dict={
                    'date_end': str(self.date_end),
                    'show_comparison': self.show_comparison,
                    'branches': self.ops_branch_ids.mapped('name'),
                    'target_move': self.target_move,
                },
                output_format='xlsx'
            )

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        except ImportError:
            raise UserError(_('xlsxwriter library is not installed. Please install it to export to Excel.'))

    def _write_balance_sheet_section(self, worksheet, formats, start_row, section_title, section_data, report_data, negate_values=False):
        """
        Write a Balance Sheet section (Assets, Liabilities, or Equity) to Excel.

        Args:
            worksheet: xlsxwriter worksheet
            formats: dict of format objects
            start_row: starting row number
            section_title: 'ASSETS', 'LIABILITIES', or 'EQUITY'
            section_data: section data dict
            report_data: full report data
            negate_values: if True, display absolute values (for L&E)

        Returns:
            int: next available row number
        """
        row = start_row

        # Write section header
        worksheet.write(row, 0, section_title, formats['subtotal_label'])
        if self.show_comparison:
            worksheet.write(row, 1, '', formats['subtotal_label'])
            worksheet.write(row, 2, '', formats['subtotal_label'])
            worksheet.write(row, 3, '', formats['subtotal_label'])
            worksheet.write(row, 4, '', formats['subtotal_label'])
        else:
            worksheet.write(row, 1, '', formats['subtotal_label'])
        row += 1

        # Handle different section structures
        if section_title in ('ASSETS', 'LIABILITIES'):
            # Write Current subsection
            row = self._write_subsection(
                worksheet, formats, row,
                f'  Current {section_title.title()}',
                section_data.get('current', []),
                section_data.get('current_total', 0),
                section_data.get('current_total_comparison', 0),
                report_data,
                negate_values
            )

            # Write Non-Current subsection
            row = self._write_subsection(
                worksheet, formats, row,
                f'  Non-Current {section_title.title()}',
                section_data.get('non_current', []),
                section_data.get('non_current_total', 0),
                section_data.get('non_current_total_comparison', 0),
                report_data,
                negate_values
            )

            # Write section total
            total = section_data.get('total', 0)
            total_comp = section_data.get('total_comparison', 0)
            if negate_values:
                total = abs(total)
                total_comp = abs(total_comp)

            worksheet.write(row, 0, f'Total {section_title.title()}', formats['total_label'])
            worksheet.write(row, 1, total, formats['total_number'])

            if self.show_comparison:
                worksheet.write(row, 2, total_comp, formats['total_number'])
                variance = total - total_comp
                worksheet.write(row, 3, variance, formats['total_number'])
                variance_pct = (variance / abs(total_comp) * 100) if total_comp else 0
                worksheet.write(row, 4, variance_pct / 100, formats['percentage'])
            row += 1

        else:  # EQUITY
            # Write equity lines
            for line in section_data.get('lines', []):
                balance = line['balance']
                balance_comp = line['balance_comparison']
                if negate_values:
                    balance = abs(balance)
                    balance_comp = abs(balance_comp)

                account_name = line['name']
                if line.get('code') and self.show_account_codes:
                    account_name = f"{line['code']} - {account_name}"

                # Determine format based on value
                is_alt = row % 2 == 0
                if balance > 0:
                    num_fmt = formats['number_alt'] if is_alt else formats['number']
                elif balance < 0:
                    num_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
                else:
                    num_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']

                text_fmt = formats['text_alt'] if is_alt else formats['text']

                worksheet.write(row, 0, f'    {account_name}', text_fmt)
                worksheet.write(row, 1, balance, num_fmt)

                if self.show_comparison:
                    num_fmt_comp = formats['number_alt'] if is_alt else formats['number']
                    worksheet.write(row, 2, balance_comp, num_fmt_comp)
                    variance = line['variance']
                    worksheet.write(row, 3, variance, num_fmt)
                    variance_pct = line['variance_pct'] / 100 if line['variance_pct'] else 0
                    worksheet.write(row, 4, variance_pct, formats['percentage'])
                row += 1

            # Write section total
            total = section_data.get('total', 0)
            total_comp = section_data.get('total_comparison', 0)
            if negate_values:
                total = abs(total)
                total_comp = abs(total_comp)

            worksheet.write(row, 0, 'Total Equity', formats['total_label'])
            worksheet.write(row, 1, total, formats['total_number'])

            if self.show_comparison:
                worksheet.write(row, 2, total_comp, formats['total_number'])
                variance = total - total_comp
                worksheet.write(row, 3, variance, formats['total_number'])
                variance_pct = (variance / abs(total_comp) * 100) if total_comp else 0
                worksheet.write(row, 4, variance_pct / 100, formats['percentage'])
            row += 1

        return row

    def _write_subsection(self, worksheet, formats, start_row, subsection_title, lines, subtotal, subtotal_comp, report_data, negate_values=False):
        """
        Write a subsection (e.g., Current Assets) to Excel.

        Returns:
            int: next available row number
        """
        row = start_row

        # Write subsection title
        worksheet.write(row, 0, subsection_title, formats['subtotal_label'])
        if self.show_comparison:
            worksheet.write(row, 1, '', formats['subtotal_label'])
            worksheet.write(row, 2, '', formats['subtotal_label'])
            worksheet.write(row, 3, '', formats['subtotal_label'])
            worksheet.write(row, 4, '', formats['subtotal_label'])
        else:
            worksheet.write(row, 1, '', formats['subtotal_label'])
        row += 1

        # Write account lines
        for line in lines:
            balance = line['balance']
            balance_comp = line['balance_comparison']
            if negate_values:
                balance = abs(balance)
                balance_comp = abs(balance_comp)

            account_name = line['name']
            if line.get('code') and self.show_account_codes:
                account_name = f"{line['code']} - {account_name}"

            # Determine format based on value
            is_alt = row % 2 == 0
            if balance > 0:
                num_fmt = formats['number_alt'] if is_alt else formats['number']
            elif balance < 0:
                num_fmt = formats['number_negative_alt'] if is_alt else formats['number_negative']
            else:
                num_fmt = formats['number_zero_alt'] if is_alt else formats['number_zero']

            text_fmt = formats['text_alt'] if is_alt else formats['text']

            worksheet.write(row, 0, f'    {account_name}', text_fmt)
            worksheet.write(row, 1, balance, num_fmt)

            if self.show_comparison:
                num_fmt_comp = formats['number_alt'] if is_alt else formats['number']
                worksheet.write(row, 2, balance_comp, num_fmt_comp)
                variance = line['variance']
                worksheet.write(row, 3, variance, num_fmt)
                variance_pct = line['variance_pct'] / 100 if line['variance_pct'] else 0
                worksheet.write(row, 4, variance_pct, formats['percentage'])
            row += 1

        # Write subtotal
        if negate_values:
            subtotal = abs(subtotal)
            subtotal_comp = abs(subtotal_comp)

        worksheet.write(row, 0, f'  {subsection_title} Subtotal', formats['subtotal_label'])
        worksheet.write(row, 1, subtotal, formats['subtotal_number'])

        if self.show_comparison:
            worksheet.write(row, 2, subtotal_comp, formats['subtotal_number'])
            variance = subtotal - subtotal_comp
            worksheet.write(row, 3, variance, formats['subtotal_number'])
            variance_pct = (variance / abs(subtotal_comp) * 100) if subtotal_comp else 0
            worksheet.write(row, 4, variance_pct / 100, formats['percentage'])
        row += 1

        return row

    # Aliases for standard naming convention
    def action_generate_report(self):
        """Alias for action_generate_pdf for UI consistency."""
        return self.action_generate_pdf()

    def action_export_excel(self):
        """Alias for action_generate_xlsx for UI consistency."""
        return self.action_generate_xlsx()
