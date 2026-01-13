# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import ipaddress
import logging

_logger = logging.getLogger(__name__)


class OpsIpWhitelist(models.Model):
    """
    IP-based Access Control System

    Features:
    - Allow/Deny rules for IP ranges (CIDR notation)
    - Apply rules to specific users/groups
    - Rule priority via sequence
    - Statistics tracking
    - Integration with login process
    - Log blocked attempts
    """
    _name = 'ops.ip.whitelist'
    _description = 'OPS IP Whitelist Rules'
    _order = 'sequence, id'

    # ========================================================================
    # FIELDS
    # ========================================================================

    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Descriptive name for this IP rule'
    )

    sequence = fields.Integer(
        string='Priority',
        default=10,
        help='Lower number = higher priority. First matching rule wins.'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    rule_type = fields.Selection([
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ], string='Rule Type', required=True, default='allow')

    ip_address = fields.Char(
        string='IP Address/Range',
        required=True,
        help='Single IP (192.168.1.1) or CIDR range (192.168.1.0/24)'
    )

    apply_to = fields.Selection([
        ('all', 'All Users'),
        ('users', 'Specific Users'),
        ('groups', 'User Groups'),
    ], string='Apply To', required=True, default='all')

    user_ids = fields.Many2many(
        'res.users',
        'ops_ip_whitelist_user_rel',
        'rule_id',
        'user_id',
        string='Users',
        help='Specific users this rule applies to'
    )

    group_ids = fields.Many2many(
        'res.groups',
        'ops_ip_whitelist_group_rel',
        'rule_id',
        'group_id',
        string='User Groups',
        help='User groups this rule applies to'
    )

    description = fields.Text(
        string='Description',
        help='Purpose and details of this rule'
    )

    blocked_count = fields.Integer(
        string='Blocked Attempts',
        default=0,
        readonly=True,
        help='Number of times this rule blocked access'
    )

    allowed_count = fields.Integer(
        string='Allowed Attempts',
        default=0,
        readonly=True,
        help='Number of times this rule allowed access'
    )

    last_triggered = fields.Datetime(
        string='Last Triggered',
        readonly=True
    )

    created_by_user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    # ========================================================================
    # VALIDATION
    # ========================================================================

    @api.constrains('ip_address')
    def _check_ip_address(self):
        """Validate IP address or CIDR range format."""
        for rule in self:
            try:
                # Try to parse as IP network (supports both single IP and CIDR)
                ipaddress.ip_network(rule.ip_address, strict=False)
            except ValueError as e:
                raise UserError(_(
                    "Invalid IP address format: %s\n"
                    "Use single IP (192.168.1.1) or CIDR notation (192.168.1.0/24)"
                ) % str(e))

    @api.constrains('apply_to', 'user_ids', 'group_ids')
    def _check_apply_to(self):
        """Validate that users/groups are specified when needed."""
        for rule in self:
            if rule.apply_to == 'users' and not rule.user_ids:
                raise UserError(_("Please specify at least one user for this rule."))
            if rule.apply_to == 'groups' and not rule.group_ids:
                raise UserError(_("Please specify at least one group for this rule."))

    # ========================================================================
    # IP CHECKING LOGIC
    # ========================================================================

    @api.model
    def check_ip_access(self, ip_address, user_id):
        """
        Check if IP is allowed for the given user.

        Args:
            ip_address: IP address to check
            user_id: User ID attempting access

        Returns:
            tuple: (allowed: bool, rule: record or None, message: str)
        """
        if not ip_address:
            _logger.warning("No IP address provided for access check")
            return True, None, "No IP address to check"

        # Get user
        user = self.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            return False, None, "Invalid user"

        # System admins bypass IP checks (configurable)
        config = self.env['ir.config_parameter'].sudo()
        bypass_admin = config.get_param('ops.ip.bypass_admin', default='True') == 'True'

        if bypass_admin and user.has_group('base.group_system'):
            _logger.info(f"System admin {user.name} bypassed IP whitelist")
            return True, None, "Admin bypass"

        # Get applicable rules (active only, ordered by sequence)
        rules = self.search([('active', '=', True)], order='sequence, id')

        # Parse IP address
        try:
            client_ip = ipaddress.ip_address(ip_address)
        except ValueError as e:
            _logger.error(f"Invalid IP address format: {ip_address}")
            return False, None, f"Invalid IP format: {str(e)}"

        # Check rules in order (first match wins)
        for rule in rules:
            # Check if rule applies to this user
            if not rule._applies_to_user(user):
                continue

            # Check if IP matches rule
            if rule._ip_matches(client_ip):
                # Update statistics
                rule.sudo().write({
                    'last_triggered': fields.Datetime.now(),
                })

                if rule.rule_type == 'allow':
                    rule.sudo().write({'allowed_count': rule.allowed_count + 1})
                    _logger.info(f"IP {ip_address} allowed by rule: {rule.name}")
                    return True, rule, f"Allowed by rule: {rule.name}"
                else:  # deny
                    rule.sudo().write({'blocked_count': rule.blocked_count + 1})

                    # Log blocked attempt
                    self.env['ops.security.audit'].sudo().create({
                        'user_id': user_id,
                        'event_type': 'ip_blocked',
                        'details': f"IP {ip_address} blocked by rule: {rule.name}",
                        'ip_address': ip_address,
                        'severity': 'warning',
                    })

                    _logger.warning(f"IP {ip_address} blocked by rule: {rule.name}")
                    return False, rule, f"Blocked by rule: {rule.name}"

        # Default behavior: Allow if no rules match (configurable)
        default_allow = config.get_param('ops.ip.default_allow', default='True') == 'True'

        if default_allow:
            _logger.info(f"IP {ip_address} allowed (no matching rules, default allow)")
            return True, None, "No matching rules (default allow)"
        else:
            # Log blocked attempt
            self.env['ops.security.audit'].sudo().create({
                'user_id': user_id,
                'event_type': 'ip_blocked',
                'details': f"IP {ip_address} blocked (no matching rules, default deny)",
                'ip_address': ip_address,
                'severity': 'warning',
            })

            _logger.warning(f"IP {ip_address} blocked (no matching rules, default deny)")
            return False, None, "No matching rules (default deny)"

    def _applies_to_user(self, user):
        """Check if this rule applies to the given user."""
        self.ensure_one()

        if self.apply_to == 'all':
            return True
        elif self.apply_to == 'users':
            return user.id in self.user_ids.ids
        elif self.apply_to == 'groups':
            user_groups = user.groups_id.ids
            return any(group_id in user_groups for group_id in self.group_ids.ids)

        return False

    def _ip_matches(self, client_ip):
        """
        Check if client IP matches this rule's IP/range.

        Args:
            client_ip: ipaddress.IPv4Address or IPv6Address object

        Returns:
            bool: True if IP matches
        """
        self.ensure_one()

        try:
            network = ipaddress.ip_network(self.ip_address, strict=False)
            return client_ip in network
        except ValueError:
            _logger.error(f"Invalid IP format in rule {self.name}: {self.ip_address}")
            return False

    # ========================================================================
    # ACTIONS
    # ========================================================================

    def action_test_ip(self):
        """Test this rule with a sample IP (wizard would be better)."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Test IP Rule'),
            'res_model': 'ops.ip.test.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_rule_id': self.id},
        }

    def action_view_blocked_attempts(self):
        """View audit log of blocked attempts for this rule."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Blocked Attempts'),
            'res_model': 'ops.security.audit',
            'view_mode': 'tree,form',
            'domain': [
                ('event_type', '=', 'ip_blocked'),
                ('details', 'ilike', self.name)
            ],
        }

    # ========================================================================
    # REPORTING
    # ========================================================================

    @api.model
    def get_ip_statistics(self, days=30):
        """Get IP blocking statistics."""
        date_from = fields.Datetime.now() - fields.timedelta(days=days)

        # Get blocked attempts from audit log
        blocked_attempts = self.env['ops.security.audit'].search_count([
            ('event_type', '=', 'ip_blocked'),
            ('timestamp', '>=', date_from)
        ])

        # Get active rules count
        active_rules = self.search_count([('active', '=', True)])

        # Get most triggered rule
        rules = self.search([('active', '=', True)], order='blocked_count desc', limit=1)
        most_blocked = rules[0] if rules else None

        return {
            'total_blocked': blocked_attempts,
            'active_rules': active_rules,
            'most_blocked_rule': most_blocked.name if most_blocked else None,
            'most_blocked_count': most_blocked.blocked_count if most_blocked else 0,
        }

    @api.model
    def get_blocked_ips(self, days=7):
        """Get list of IPs that were blocked in last N days."""
        date_from = fields.Datetime.now() - fields.timedelta(days=days)

        self.env.cr.execute("""
            SELECT DISTINCT ip_address, COUNT(*) as count
            FROM ops_security_audit
            WHERE event_type = 'ip_blocked'
            AND timestamp >= %s
            GROUP BY ip_address
            ORDER BY count DESC
            LIMIT 50
        """, (date_from,))

        results = self.env.cr.fetchall()
        return [{'ip': row[0], 'count': row[1]} for row in results]

    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================

    @api.model
    def create_rule_from_template(self, template_name):
        """Create common IP rules from templates."""
        templates = {
            'local_network': {
                'name': 'Allow Local Network',
                'rule_type': 'allow',
                'ip_address': '192.168.0.0/16',
                'description': 'Allow access from local network',
            },
            'office_network': {
                'name': 'Allow Office Network',
                'rule_type': 'allow',
                'ip_address': '10.0.0.0/8',
                'description': 'Allow access from office network',
            },
            'vpn_network': {
                'name': 'Allow VPN',
                'rule_type': 'allow',
                'ip_address': '172.16.0.0/12',
                'description': 'Allow access from VPN',
            },
            'block_public': {
                'name': 'Block Public Internet',
                'rule_type': 'deny',
                'ip_address': '0.0.0.0/0',
                'description': 'Block all public internet access',
                'sequence': 999,  # Low priority (last resort)
            },
        }

        if template_name not in templates:
            raise UserError(_("Unknown template: %s") % template_name)

        return self.create(templates[template_name])

    # ========================================================================
    # SECURITY
    # ========================================================================

    @api.model
    def create(self, vals):
        """Log rule creation."""
        rule = super(OpsIpWhitelist, self).create(vals)

        self.env['ops.security.audit'].sudo().create({
            'user_id': self.env.user.id,
            'event_type': 'ip_rule_created',
            'model_name': self._name,
            'record_id': rule.id,
            'record_name': rule.name,
            'details': f"IP rule created: {rule.name} ({rule.rule_type} {rule.ip_address})",
            'severity': 'info',
        })

        return rule

    def write(self, vals):
        """Log rule modifications."""
        result = super(OpsIpWhitelist, self).write(vals)

        for rule in self:
            # Don't log statistics updates
            if set(vals.keys()) <= {'blocked_count', 'allowed_count', 'last_triggered'}:
                continue

            self.env['ops.security.audit'].sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'ip_rule_modified',
                'model_name': self._name,
                'record_id': rule.id,
                'record_name': rule.name,
                'details': f"IP rule modified: {rule.name}",
                'severity': 'warning',
            })

        return result

    def unlink(self):
        """Log rule deletion."""
        for rule in self:
            self.env['ops.security.audit'].sudo().create({
                'user_id': self.env.user.id,
                'event_type': 'ip_rule_deleted',
                'model_name': self._name,
                'record_id': rule.id,
                'record_name': rule.name,
                'details': f"IP rule deleted: {rule.name}",
                'severity': 'critical',
            })

        return super(OpsIpWhitelist, self).unlink()


class OpsIpTestWizard(models.TransientModel):
    """Wizard to test IP rules."""
    _name = 'ops.ip.test.wizard'
    _description = 'Test IP Rule'

    rule_id = fields.Many2one('ops.ip.whitelist', string='Rule')
    test_ip = fields.Char(string='Test IP Address', required=True)
    user_id = fields.Many2one('res.users', string='Test User', required=True,
                              default=lambda self: self.env.user)
    result = fields.Text(string='Test Result', readonly=True)

    def action_test(self):
        """Run IP test."""
        allowed, rule, message = self.env['ops.ip.whitelist'].check_ip_access(
            self.test_ip,
            self.user_id.id
        )

        result = f"IP: {self.test_ip}\n"
        result += f"User: {self.user_id.name}\n"
        result += f"Result: {'✓ ALLOWED' if allowed else '✗ BLOCKED'}\n"
        result += f"Message: {message}\n"

        if rule:
            result += f"Matching Rule: {rule.name}\n"

        self.result = result

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
