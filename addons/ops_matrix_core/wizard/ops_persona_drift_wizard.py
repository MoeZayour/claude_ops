# -*- coding: utf-8 -*-
"""
OPS Persona Drift Detection Wizard
===================================
Analyze user permissions against their assigned personas to detect permission drift.
"""

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class OpsPersonaDriftWizard(models.TransientModel):
    """Wizard to detect persona drift across users."""

    _name = 'ops.persona.drift.wizard'
    _description = 'Persona Drift Detection Wizard'

    # -------------------------------------------------------------------------
    # FILTER FIELDS
    # -------------------------------------------------------------------------

    user_ids = fields.Many2many(
        'res.users',
        string='Specific Users',
        help='Leave empty to check all users',
    )

    include_admins = fields.Boolean(
        string='Include System Admins',
        default=False,
        help='Include users with administrator rights in the analysis',
    )

    only_show_drift = fields.Boolean(
        string='Only Show Drift',
        default=True,
        help='Only display users with permission drift',
    )

    # -------------------------------------------------------------------------
    # RESULT FIELDS
    # -------------------------------------------------------------------------

    result_ids = fields.One2many(
        'ops.persona.drift.result',
        'wizard_id',
        string='Results',
    )

    # Summary fields
    total_users_checked = fields.Integer(
        string='Users Checked',
        readonly=True,
    )

    users_with_drift = fields.Integer(
        string='Users with Drift',
        readonly=True,
    )

    users_without_persona = fields.Integer(
        string='Users Without Persona',
        readonly=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed'),
    ], default='draft')

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_detect_drift(self):
        """Run persona drift detection analysis."""
        self.ensure_one()

        # Clear previous results
        self.result_ids.unlink()

        # Determine which users to check
        domain = [
            ('active', '=', True),
            ('share', '=', False),  # Exclude portal users
        ]

        if not self.include_admins:
            domain.append(('id', 'not in', [1, 2]))  # Exclude admin and public

        if self.user_ids:
            domain.append(('id', 'in', self.user_ids.ids))

        users = self.env['res.users'].sudo().search(domain)

        results = []
        drift_count = 0
        no_persona_count = 0

        for user in users:
            result_data = self._analyze_user_drift(user)

            if result_data:
                # Apply filter
                if self.only_show_drift and result_data['drift_status'] == 'ok':
                    continue

                results.append({
                    'wizard_id': self.id,
                    **result_data
                })

                if result_data['drift_status'] != 'ok':
                    drift_count += 1
                if result_data['drift_status'] == 'no_persona':
                    no_persona_count += 1

        # Create result records
        self.env['ops.persona.drift.result'].create(results)

        self.write({
            'state': 'done',
            'total_users_checked': len(users),
            'users_with_drift': drift_count,
            'users_without_persona': no_persona_count,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _analyze_user_drift(self, user):
        """
        Analyze a single user for permission drift.

        Returns dict with drift analysis or None if user should be skipped.
        """
        # Get user's personas
        personas = user.ops_persona_ids.filtered(lambda p: p.active)

        if not personas:
            return {
                'user_id': user.id,
                'drift_status': 'no_persona',
                'persona_names': '',
                'expected_groups': '',
                'actual_groups': self._format_groups(user.groups_id),
                'extra_groups': '',
                'missing_groups': '',
                'severity': 'medium',
            }

        # Get expected groups from personas
        # Note: This assumes personas have a way to define expected groups
        # If persona doesn't have access_group_ids, we'll check for sensitive groups
        expected_groups = self.env['res.groups']

        for persona in personas:
            # Check if persona has access_group_ids field
            if hasattr(persona, 'access_group_ids') and persona.access_group_ids:
                expected_groups |= persona.access_group_ids

        # Get actual groups (filter to relevant ones)
        actual_groups = user.groups_id

        # Define sensitive/OPS-related groups to check
        ops_groups = actual_groups.filtered(
            lambda g: 'ops' in g.full_name.lower() or
                     any(kw in g.name.lower() for kw in ['admin', 'manager', 'cost', 'margin', 'executive', 'power'])
        )

        # Calculate drift
        if expected_groups:
            extra_groups = ops_groups - expected_groups
            missing_groups = expected_groups - actual_groups
        else:
            # No expected groups defined - just report OPS groups
            extra_groups = ops_groups
            missing_groups = self.env['res.groups']

        # Determine drift status
        if extra_groups and missing_groups:
            drift_status = 'drift'
            severity = 'high'
        elif extra_groups:
            drift_status = 'extra_permissions'
            # Check severity based on group types
            if any(kw in g.name.lower() for g in extra_groups for kw in ['admin', 'cost', 'power']):
                severity = 'critical'
            else:
                severity = 'medium'
        elif missing_groups:
            drift_status = 'missing_permissions'
            severity = 'low'
        else:
            drift_status = 'ok'
            severity = 'low'

        return {
            'user_id': user.id,
            'drift_status': drift_status,
            'persona_names': ', '.join(personas.mapped('name')),
            'expected_groups': self._format_groups(expected_groups) if expected_groups else 'Not defined',
            'actual_groups': self._format_groups(ops_groups),
            'extra_groups': self._format_groups(extra_groups),
            'missing_groups': self._format_groups(missing_groups),
            'severity': severity,
        }

    def _format_groups(self, groups):
        """Format group recordset as comma-separated names."""
        if not groups:
            return ''
        return ', '.join(groups.mapped('name')[:10])  # Limit to first 10

    def action_export_excel(self):
        """Export drift report to Excel."""
        self.ensure_one()

        # This will be implemented with the audit evidence wizard
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Export'),
                'message': _('Excel export is available via the Audit Evidence Export wizard.'),
                'type': 'info',
            }
        }

    def action_reset(self):
        """Reset wizard to draft state."""
        self.ensure_one()
        self.result_ids.unlink()
        self.write({
            'state': 'draft',
            'total_users_checked': 0,
            'users_with_drift': 0,
            'users_without_persona': 0,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class OpsPersonaDriftResult(models.TransientModel):
    """Individual result from persona drift analysis."""

    _name = 'ops.persona.drift.result'
    _description = 'Persona Drift Analysis Result'
    _order = 'severity_order, drift_status'

    wizard_id = fields.Many2one(
        'ops.persona.drift.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
    )

    user_login = fields.Char(
        related='user_id.login',
        string='Login',
    )

    drift_status = fields.Selection([
        ('ok', 'No Drift'),
        ('extra_permissions', 'Extra Permissions'),
        ('missing_permissions', 'Missing Permissions'),
        ('drift', 'Permission Drift'),
        ('no_persona', 'No Persona Assigned'),
    ], string='Status', required=True)

    severity = fields.Selection([
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], string='Severity', default='medium')

    severity_order = fields.Integer(
        compute='_compute_severity_order',
        store=True,
    )

    persona_names = fields.Char(string='Assigned Personas')
    expected_groups = fields.Text(string='Expected Groups')
    actual_groups = fields.Text(string='Actual OPS Groups')
    extra_groups = fields.Text(string='Extra Permissions')
    missing_groups = fields.Text(string='Missing Permissions')

    @api.depends('severity')
    def _compute_severity_order(self):
        """Compute sort order for severity."""
        severity_map = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
        for result in self:
            result.severity_order = severity_map.get(result.severity, 5)

    def action_view_user(self):
        """Open user form in a new window."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'res_id': self.user_id.id,
            'view_mode': 'form',
            'target': 'new',
        }
