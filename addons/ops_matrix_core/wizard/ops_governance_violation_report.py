# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import csv
import io
import base64
import logging

_logger = logging.getLogger(__name__)


class OpsGovernanceViolationReport(models.TransientModel):
    """Wizard for generating governance violation reports with matrix filtering"""
    _name = 'ops.governance.violation.report'
    _description = 'Governance Violations Dashboard & Reporting'
    
    # --- FILTERS ---
    date_from = fields.Date(
        string='From Date', 
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    
    date_to = fields.Date(
        string='To Date', 
        required=True,
        default=lambda self: fields.Date.today()
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        default=lambda self: self.env.company
    )
    
    branch_id = fields.Many2one(
        'ops.branch', 
        string='Branch',
        domain="[('company_id', '=', company_id)]"
    )
    
    business_unit_id = fields.Many2one(
        'ops.business.unit', 
        string='Business Unit',
        domain="[('company_ids', 'in', [company_id])]"
    )
    
    rule_id = fields.Many2one(
        'ops.governance.rule', 
        string='Specific Rule',
        domain="[('company_id', '=', company_id)]"
    )
    
    violation_type = fields.Selection([
        ('all', 'All Violations'),
        ('matrix', 'Matrix Validation'),
        ('discount', 'Discount Limit'),
        ('margin', 'Margin Protection'),
        ('price', 'Price Override'),
        ('other', 'Other'),
    ], string='Violation Type', default='all')
    
    approval_status = fields.Selection([
        ('all', 'All Statuses'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Approval Status', default='all')
    
    # --- REPORT OPTIONS ---
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('rule', 'By Rule'),
        ('type', 'By Violation Type'),
        ('branch', 'By Branch'),
        ('bu', 'By Business Unit'),
        ('user', 'By User'),
        ('severity', 'By Severity'),
    ], string='Group By', default='none')
    
    include_details = fields.Boolean(string='Include Details', default=True)
    include_resolved = fields.Boolean(string='Include Resolved', default=False)
    
    # --- COMPUTED RESULTS ---
    violation_count = fields.Integer(
        string='Violation Count', 
        compute='_compute_violation_stats', 
        store=False
    )
    
    pending_count = fields.Integer(
        string='Pending Count', 
        compute='_compute_violation_stats', 
        store=False
    )
    
    approved_count = fields.Integer(
        string='Approved Count', 
        compute='_compute_violation_stats', 
        store=False
    )
    
    rejected_count = fields.Integer(
        string='Rejected Count', 
        compute='_compute_violation_stats', 
        store=False
    )
    
    # --- COMPUTED METHODS ---
    
    @api.depends('date_from', 'date_to', 'company_id', 'branch_id', 'business_unit_id',
                'rule_id', 'violation_type', 'approval_status')
    def _compute_violation_stats(self):
        """Compute violation statistics."""
        for wizard in self:
            domain = wizard._get_base_domain()
            
            all_violations = self.env['ops.approval.request'].search(domain)
            wizard.violation_count = len(all_violations)
            wizard.pending_count = len(all_violations.filtered(lambda r: r.state == 'pending'))
            wizard.approved_count = len(all_violations.filtered(lambda r: r.state == 'approved'))
            wizard.rejected_count = len(all_violations.filtered(lambda r: r.state == 'rejected'))
    
    # --- BUSINESS METHODS ---
    
    def _get_base_domain(self):
        """Build base domain for violation queries."""
        self.ensure_one()
        
        domain = [
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to),
            ('is_governance_violation', '=', True),
        ]
        
        if self.company_id:
            domain.append(('ops_company_id', '=', self.company_id.id))
        
        if self.branch_id:
            domain.append(('ops_branch_id', '=', self.branch_id.id))
        
        if self.business_unit_id:
            domain.append(('ops_business_unit_id', '=', self.business_unit_id.id))
        
        if self.rule_id:
            domain.append(('rule_id', '=', self.rule_id.id))
        
        if self.violation_type != 'all':
            domain.append(('violation_type', '=', self.violation_type))
        
        if self.approval_status != 'all':
            domain.append(('state', '=', self.approval_status))
        
        if not self.include_resolved:
            domain.append(('state', 'in', ['pending']))
        
        return domain
    
    def _get_violations(self):
        """Get violations based on filters."""
        self.ensure_one()
        
        domain = self._get_base_domain()
        approvals = self.env['ops.approval.request'].search(domain, order='create_date desc')
        
        # Format data
        violations = []
        for approval in approvals:
            violations.append({
                'id': approval.id,
                'name': approval.name,
                'date': approval.create_date,
                'user': approval.requested_by.name,
                'branch': approval.ops_branch_id.name if approval.ops_branch_id else '',
                'bu': approval.ops_business_unit_id.name if approval.ops_business_unit_id else '',
                'rule': approval.rule_id.name if approval.rule_id else '',
                'violation_type': dict(approval._fields['violation_type'].selection).get(approval.violation_type, ''),
                'violation_summary': approval.violation_summary or '',
                'severity': dict(approval._fields['violation_severity'].selection).get(approval.violation_severity, ''),
                'status': dict(approval._fields['state'].selection).get(approval.state, ''),
                'approvers': ', '.join(approval.approver_ids.mapped('name')),
            })
        
        # Group if requested
        if self.group_by != 'none':
            violations = self._group_violations(violations)
        
        return violations
    
    def _group_violations(self, violations):
        """Group violations by selected criteria."""
        grouped = {}
        
        for violation in violations:
            key = ''
            
            if self.group_by == 'rule':
                key = violation.get('rule', 'No Rule')
            elif self.group_by == 'type':
                key = violation.get('violation_type', 'Unknown')
            elif self.group_by == 'branch':
                key = violation.get('branch', 'No Branch')
            elif self.group_by == 'bu':
                key = violation.get('bu', 'No BU')
            elif self.group_by == 'user':
                key = violation.get('user', 'Unknown User')
            elif self.group_by == 'severity':
                key = violation.get('severity', 'Unknown Severity')
            
            if key not in grouped:
                grouped[key] = {
                    'key': key,
                    'count': 0,
                    'violations': [],
                    'pending': 0,
                    'approved': 0,
                    'rejected': 0,
                }
            
            grouped[key]['count'] += 1
            grouped[key]['violations'].append(violation)
            
            if violation['status'] == 'Pending':
                grouped[key]['pending'] += 1
            elif violation['status'] == 'Approved':
                grouped[key]['approved'] += 1
            elif violation['status'] == 'Rejected':
                grouped[key]['rejected'] += 1
        
        # Convert to list and sort by count
        result = list(grouped.values())
        result.sort(key=lambda x: x['count'], reverse=True)
        return result
    
    def action_generate_report(self):
        """Generate and display report."""
        self.ensure_one()
        
        violations = self._get_violations()
        
        # Return list view of filtered approval requests
        return {
            'type': 'ir.actions.act_window',
            'name': _('Governance Violations Report: %s to %s') % (self.date_from, self.date_to),
            'res_model': 'ops.approval.request',
            'view_mode': 'list,form,pivot,graph',
            'domain': self._get_base_domain(),
            'context': {
                'search_default_group_by_violation_type': 1 if self.group_by == 'type' else 0,
                'search_default_group_by_branch': 1 if self.group_by == 'branch' else 0,
                'search_default_group_by_rule': 1 if self.group_by == 'rule' else 0,
            },
        }
    
    def action_export_csv(self):
        """Export violations to CSV."""
        self.ensure_one()
        
        violations = self._get_violations()
        
        if not violations:
            raise UserError(_("No violations found matching the selected criteria."))
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'Date', 'User', 'Branch', 'Business Unit', 'Rule', 
            'Violation Type', 'Violation Summary', 'Severity', 'Status', 'Approvers'
        ])
        
        writer.writeheader()
        
        # Handle both grouped and ungrouped data
        rows_to_write = []
        if violations and 'violations' in violations[0]:  # Grouped data
            for group in violations:
                for sub_violation in group['violations']:
                    rows_to_write.append(sub_violation)
        else:  # Ungrouped data
            rows_to_write = violations
        
        for violation in rows_to_write:
            writer.writerow({
                'Date': violation.get('date', ''),
                'User': violation.get('user', ''),
                'Branch': violation.get('branch', ''),
                'Business Unit': violation.get('bu', ''),
                'Rule': violation.get('rule', ''),
                'Violation Type': violation.get('violation_type', ''),
                'Violation Summary': violation.get('violation_summary', ''),
                'Severity': violation.get('severity', ''),
                'Status': violation.get('status', ''),
                'Approvers': violation.get('approvers', ''),
            })
        
        # Create attachment
        csv_data = output.getvalue().encode('utf-8')
        filename = f'governance_violations_{fields.Date.today()}.csv'
        
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(csv_data),
            'res_model': 'ops.governance.violation.report',
            'res_id': self.id,
            'type': 'binary',
        })
        
        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def action_view_violations(self):
        """Open filtered violations view."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Governance Violations'),
            'res_model': 'ops.approval.request',
            'view_mode': 'list,form,pivot,graph',
            'domain': self._get_base_domain(),
            'context': {
                'search_default_pending': 1 if self.approval_status == 'pending' else 0,
                'search_default_group_by_date': 1,
                'search_default_group_by_violation_type': 1,
            },
        }
    
    def action_view_summary(self):
        """Display summary statistics."""
        self.ensure_one()
        
        violations = self._get_violations()
        
        if self.group_by == 'none':
            summary_message = _(
                "Total Violations: %s\n"
                "Pending: %s\n"
                "Approved: %s\n"
                "Rejected: %s"
            ) % (
                self.violation_count,
                self.pending_count,
                self.approved_count,
                self.rejected_count
            )
        else:
            # Grouped summary
            summary_lines = [_("Grouped by %s:") % self.group_by]
            for group in violations[:10]:  # Show top 10 groups
                summary_lines.append(
                    _("  %s: %s violations (%s pending)") % (
                        group['key'],
                        group['count'],
                        group['pending']
                    )
                )
            summary_message = "\n".join(summary_lines)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Violation Summary'),
                'message': summary_message,
                'type': 'info',
                'sticky': True,
            }
        }
