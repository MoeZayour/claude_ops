# -*- coding: utf-8 -*-
"""
OPS Audit Evidence Export Wizard
================================
Generate comprehensive audit evidence packages for compliance reporting.
"""

import base64
import io
import logging
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None
    _logger.warning("xlsxwriter not installed. Audit evidence export will be limited.")


class OpsAuditEvidenceWizard(models.TransientModel):
    """Wizard to export comprehensive audit evidence packages."""

    _name = 'ops.audit.evidence.wizard'
    _description = 'Audit Evidence Export Wizard'

    # -------------------------------------------------------------------------
    # CONTENT OPTIONS
    # -------------------------------------------------------------------------

    include_it_admin_rules = fields.Boolean(
        string='IT Admin Blindness Rules',
        default=True,
        help='Include all IT Admin blocking rules and their status',
    )

    include_security_groups = fields.Boolean(
        string='Security Groups',
        default=True,
        help='Include all OPS security groups and their members',
    )

    include_user_matrix = fields.Boolean(
        string='User-Group Matrix',
        default=True,
        help='Include a matrix of users and their group memberships',
    )

    include_record_rules = fields.Boolean(
        string='Record Rules',
        default=True,
        help='Include all record rules (ir.rule) for OPS models',
    )

    include_acl_coverage = fields.Boolean(
        string='ACL Coverage',
        default=True,
        help='Include ACL entries (ir.model.access) for OPS models',
    )

    include_sod_rules = fields.Boolean(
        string='SoD Rules & Violations',
        default=True,
        help='Include Segregation of Duties rules and violation logs',
    )

    include_persona_assignments = fields.Boolean(
        string='Persona Assignments',
        default=True,
        help='Include all user-persona assignments',
    )

    # -------------------------------------------------------------------------
    # DATE RANGE
    # -------------------------------------------------------------------------

    date_from = fields.Date(
        string='From Date',
        default=lambda self: fields.Date.today() - timedelta(days=90),
        help='Start date for violation logs',
    )

    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today,
        help='End date for violation logs',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------

    export_file = fields.Binary(
        string='Export File',
        readonly=True,
    )

    export_filename = fields.Char(
        string='Filename',
        readonly=True,
    )

    state = fields.Selection([
        ('draft', 'Configure'),
        ('done', 'Download'),
    ], default='draft')

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_generate_evidence_pack(self):
        """Generate Excel workbook with audit evidence."""
        self.ensure_one()

        if not xlsxwriter:
            raise UserError(_("xlsxwriter library is required for Excel export. Please install it."))

        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Define styles
        styles = self._create_styles(workbook)

        # Generate each sheet based on options
        if self.include_it_admin_rules:
            self._write_it_admin_rules_sheet(workbook, styles)

        if self.include_security_groups:
            self._write_security_groups_sheet(workbook, styles)

        if self.include_user_matrix:
            self._write_user_matrix_sheet(workbook, styles)

        if self.include_record_rules:
            self._write_record_rules_sheet(workbook, styles)

        if self.include_acl_coverage:
            self._write_acl_coverage_sheet(workbook, styles)

        if self.include_sod_rules:
            self._write_sod_sheet(workbook, styles)

        if self.include_persona_assignments:
            self._write_persona_assignments_sheet(workbook, styles)

        # Add summary sheet
        self._write_summary_sheet(workbook, styles)

        workbook.close()

        # Get file content
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        # Generate filename
        filename = f"OPS_Audit_Evidence_{fields.Date.today().strftime('%Y%m%d')}.xlsx"

        self.write({
            'export_file': file_data,
            'export_filename': filename,
            'state': 'done',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_reset(self):
        """Reset wizard to draft state."""
        self.ensure_one()
        self.write({
            'state': 'draft',
            'export_file': False,
            'export_filename': False,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    # -------------------------------------------------------------------------
    # STYLE HELPERS
    # -------------------------------------------------------------------------

    def _create_styles(self, workbook):
        """Create common styles for the workbook."""
        return {
            'title': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'font_color': '#1a237e',
                'bottom': 2,
            }),
            'header': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'bg_color': '#1a237e',
                'font_color': 'white',
                'border': 1,
                'text_wrap': True,
                'valign': 'vcenter',
            }),
            'cell': workbook.add_format({
                'font_size': 10,
                'border': 1,
                'valign': 'vcenter',
            }),
            'cell_wrap': workbook.add_format({
                'font_size': 10,
                'border': 1,
                'text_wrap': True,
                'valign': 'vcenter',
            }),
            'passed': workbook.add_format({
                'font_size': 10,
                'border': 1,
                'bg_color': '#c8e6c9',
                'font_color': '#1b5e20',
            }),
            'failed': workbook.add_format({
                'font_size': 10,
                'border': 1,
                'bg_color': '#ffcdd2',
                'font_color': '#b71c1c',
            }),
            'warning': workbook.add_format({
                'font_size': 10,
                'border': 1,
                'bg_color': '#fff9c4',
                'font_color': '#f57f17',
            }),
            'meta_label': workbook.add_format({
                'bold': True,
                'font_size': 10,
            }),
            'meta_value': workbook.add_format({
                'font_size': 10,
            }),
        }

    # -------------------------------------------------------------------------
    # SHEET GENERATORS
    # -------------------------------------------------------------------------

    def _write_summary_sheet(self, workbook, styles):
        """Write summary sheet with export metadata."""
        sheet = workbook.add_worksheet('Summary')
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 50)

        row = 0
        sheet.write(row, 0, 'OPS Framework Audit Evidence Package', styles['title'])
        row += 2

        # Metadata
        metadata = [
            ('Generated On', fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('Generated By', self.env.user.name),
            ('Company', self.company_id.name),
            ('Date Range', f"{self.date_from} to {self.date_to}"),
            ('', ''),
            ('Contents Included:', ''),
            ('IT Admin Blindness Rules', 'Yes' if self.include_it_admin_rules else 'No'),
            ('Security Groups', 'Yes' if self.include_security_groups else 'No'),
            ('User-Group Matrix', 'Yes' if self.include_user_matrix else 'No'),
            ('Record Rules', 'Yes' if self.include_record_rules else 'No'),
            ('ACL Coverage', 'Yes' if self.include_acl_coverage else 'No'),
            ('SoD Rules & Violations', 'Yes' if self.include_sod_rules else 'No'),
            ('Persona Assignments', 'Yes' if self.include_persona_assignments else 'No'),
        ]

        for label, value in metadata:
            sheet.write(row, 0, label, styles['meta_label'])
            sheet.write(row, 1, value, styles['meta_value'])
            row += 1

    def _write_it_admin_rules_sheet(self, workbook, styles):
        """Write IT Admin Blindness rules sheet."""
        sheet = workbook.add_worksheet('IT Admin Blindness')
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 50)

        row = 0
        headers = ['Model', 'Rule Name', 'Status', 'Domain']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        # Get IT Admin group
        it_admin_group = self.env.ref('ops_matrix_core.group_ops_it_admin', raise_if_not_found=False)

        if not it_admin_group:
            sheet.write(row, 0, 'IT Admin group not found!', styles['failed'])
            return

        # Get all IT Admin related rules
        rules = self.env['ir.rule'].sudo().search([
            ('groups', 'in', it_admin_group.id),
            ('active', '=', True),
        ])

        for rule in rules:
            is_blocking = "('id', '=', 0)" in (rule.domain_force or '') or "[(0, '=', 1)]" in (rule.domain_force or '')
            status_style = styles['passed'] if is_blocking else styles['warning']

            sheet.write(row, 0, rule.model_id.model, styles['cell'])
            sheet.write(row, 1, rule.name, styles['cell'])
            sheet.write(row, 2, 'Blocking' if is_blocking else 'Filtering', status_style)
            sheet.write(row, 3, rule.domain_force or '', styles['cell_wrap'])
            row += 1

    def _write_security_groups_sheet(self, workbook, styles):
        """Write security groups sheet."""
        sheet = workbook.add_worksheet('Security Groups')
        sheet.set_column('A:A', 40)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 50)

        row = 0
        headers = ['Group Name', 'Category', 'User Count', 'Users']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        # Get OPS-related groups
        groups = self.env['res.groups'].sudo().search([
            '|',
            ('name', 'ilike', 'ops'),
            ('category_id.name', 'ilike', 'ops'),
        ], order='category_id, name')

        for group in groups:
            users = group.users.filtered(lambda u: u.active and u.id not in [1, 2])
            user_names = ', '.join(users.mapped('name')[:10])
            if len(users) > 10:
                user_names += f'... (+{len(users) - 10} more)'

            sheet.write(row, 0, group.full_name, styles['cell'])
            sheet.write(row, 1, group.category_id.name or '', styles['cell'])
            sheet.write(row, 2, len(users), styles['cell'])
            sheet.write(row, 3, user_names, styles['cell_wrap'])
            row += 1

    def _write_user_matrix_sheet(self, workbook, styles):
        """Write user-group matrix sheet."""
        sheet = workbook.add_worksheet('User-Group Matrix')

        # Get active users (exclude admin/public)
        users = self.env['res.users'].sudo().search([
            ('active', '=', True),
            ('share', '=', False),
            ('id', 'not in', [1, 2]),
        ], order='name')

        # Get OPS groups
        groups = self.env['res.groups'].sudo().search([
            '|',
            ('name', 'ilike', 'ops'),
            ('category_id.name', 'ilike', 'ops'),
        ], order='name', limit=30)  # Limit columns

        if not users or not groups:
            sheet.write(0, 0, 'No data available', styles['cell'])
            return

        # Set column widths
        sheet.set_column('A:A', 30)  # User name
        for col in range(1, len(groups) + 1):
            sheet.set_column(col, col, 5)

        # Write headers
        row = 0
        sheet.write(row, 0, 'User', styles['header'])
        for col, group in enumerate(groups, 1):
            # Abbreviate group name for header
            name = group.name[:15] if len(group.name) > 15 else group.name
            sheet.write(row, col, name, styles['header'])
        row += 1

        # Write user rows
        for user in users:
            sheet.write(row, 0, user.name, styles['cell'])
            for col, group in enumerate(groups, 1):
                has_group = group in user.groups_id
                sheet.write(row, col, 'X' if has_group else '', styles['passed'] if has_group else styles['cell'])
            row += 1

    def _write_record_rules_sheet(self, workbook, styles):
        """Write record rules sheet."""
        sheet = workbook.add_worksheet('Record Rules')
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 60)

        row = 0
        headers = ['Model', 'Rule Name', 'Groups', 'Domain']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        # Get rules for OPS models
        rules = self.env['ir.rule'].sudo().search([
            ('model_id.model', 'like', 'ops.%'),
            ('active', '=', True),
        ], order='model_id, name')

        for rule in rules:
            group_names = ', '.join(rule.groups.mapped('name')) if rule.groups else 'Global'
            sheet.write(row, 0, rule.model_id.model, styles['cell'])
            sheet.write(row, 1, rule.name, styles['cell'])
            sheet.write(row, 2, group_names, styles['cell_wrap'])
            sheet.write(row, 3, rule.domain_force or '', styles['cell_wrap'])
            row += 1

    def _write_acl_coverage_sheet(self, workbook, styles):
        """Write ACL coverage sheet."""
        sheet = workbook.add_worksheet('ACL Coverage')
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:G', 8)

        row = 0
        headers = ['Model', 'ACL Name', 'Group', 'Read', 'Write', 'Create', 'Delete']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        # Get ACL for OPS models
        acls = self.env['ir.model.access'].sudo().search([
            ('model_id.model', 'like', 'ops.%'),
        ], order='model_id, group_id')

        for acl in acls:
            sheet.write(row, 0, acl.model_id.model, styles['cell'])
            sheet.write(row, 1, acl.name, styles['cell'])
            sheet.write(row, 2, acl.group_id.full_name if acl.group_id else 'Everyone', styles['cell'])
            sheet.write(row, 3, 'Y' if acl.perm_read else 'N', styles['passed'] if acl.perm_read else styles['cell'])
            sheet.write(row, 4, 'Y' if acl.perm_write else 'N', styles['passed'] if acl.perm_write else styles['cell'])
            sheet.write(row, 5, 'Y' if acl.perm_create else 'N', styles['passed'] if acl.perm_create else styles['cell'])
            sheet.write(row, 6, 'Y' if acl.perm_unlink else 'N', styles['passed'] if acl.perm_unlink else styles['cell'])
            row += 1

    def _write_sod_sheet(self, workbook, styles):
        """Write SoD rules and violations sheet."""
        sheet = workbook.add_worksheet('SoD Rules & Violations')
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 50)

        row = 0
        sheet.write(row, 0, 'Segregation of Duties Rules', styles['title'])
        row += 2

        # Write SoD rules
        headers = ['Model', 'Action 1', 'Action 2', 'Enabled', 'Description']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        sod_rules = self.env['ops.segregation.of.duties'].sudo().search([])
        for rule in sod_rules:
            sheet.write(row, 0, rule.model_name, styles['cell'])
            sheet.write(row, 1, rule.action_1, styles['cell'])
            sheet.write(row, 2, rule.action_2, styles['cell'])
            enabled_style = styles['passed'] if rule.enabled else styles['warning']
            sheet.write(row, 3, 'Yes' if rule.enabled else 'No', enabled_style)
            sheet.write(row, 4, rule.description or '', styles['cell_wrap'])
            row += 1

        # Write SoD violations
        row += 2
        sheet.write(row, 0, f'SoD Violations ({self.date_from} to {self.date_to})', styles['title'])
        row += 2

        headers = ['Date', 'User', 'Rule', 'Action', 'Blocked']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        violations = self.env['ops.segregation.of.duties.log'].sudo().search([
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to),
        ], order='create_date desc')

        for violation in violations[:100]:  # Limit to last 100
            sheet.write(row, 0, violation.create_date.strftime('%Y-%m-%d %H:%M'), styles['cell'])
            sheet.write(row, 1, violation.user_id.name if violation.user_id else '', styles['cell'])
            sheet.write(row, 2, violation.rule_id.name if hasattr(violation, 'rule_id') and violation.rule_id else '', styles['cell'])
            sheet.write(row, 3, violation.action_attempted if hasattr(violation, 'action_attempted') else '', styles['cell'])
            blocked = getattr(violation, 'blocked', False)
            sheet.write(row, 4, 'Yes' if blocked else 'No', styles['failed'] if blocked else styles['warning'])
            row += 1

    def _write_persona_assignments_sheet(self, workbook, styles):
        """Write persona assignments sheet."""
        sheet = workbook.add_worksheet('Persona Assignments')
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 40)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 30)

        row = 0
        headers = ['User', 'Login', 'Personas', 'Primary Branch', 'Business Units']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, styles['header'])
        row += 1

        # Get users with personas
        users = self.env['res.users'].sudo().search([
            ('active', '=', True),
            ('share', '=', False),
            ('id', 'not in', [1, 2]),
        ], order='name')

        for user in users:
            personas = user.ops_persona_ids.mapped('name') if user.ops_persona_ids else ['No persona']
            branches = user.ops_allowed_branch_ids.mapped('name') if user.ops_allowed_branch_ids else ['None']
            bus = user.ops_allowed_business_unit_ids.mapped('name') if user.ops_allowed_business_unit_ids else ['None']

            sheet.write(row, 0, user.name, styles['cell'])
            sheet.write(row, 1, user.login, styles['cell'])
            sheet.write(row, 2, ', '.join(personas), styles['cell_wrap'])
            sheet.write(row, 3, ', '.join(branches[:5]), styles['cell_wrap'])
            sheet.write(row, 4, ', '.join(bus[:5]), styles['cell_wrap'])
            row += 1
