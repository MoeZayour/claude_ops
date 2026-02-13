from odoo import models, fields, api, tools

class OpsApprovalDashboard(models.Model):
    _name = 'ops.approval.dashboard'
    _description = 'Unified Approval Dashboard'
    _auto = False
    _order = 'date_request desc'

    res_model = fields.Char(string='Resource Model', readonly=True)
    res_id = fields.Integer(string='Resource ID', readonly=True)
    name = fields.Char(string='Source Document', readonly=True)
    requester_id = fields.Many2one('res.users', string='Requester', readonly=True)
    date_request = fields.Datetime(string='Request Date', readonly=True)
    sla_status = fields.Selection([
        ('running', 'Running'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('violated', 'Violated'),
        ('completed', 'Completed'),
        ('escalated', 'Escalated'),
        ('failed', 'Failed')
    ], string='SLA Status', readonly=True)
    time_to_breach = fields.Float(string='Time to Breach (Hours)', readonly=True)
    required_persona_id = fields.Many2one('ops.persona', string='Required Persona', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        # Check if all required tables exist
        required_tables = [
            'ops_approval_request', 
            'ops_governance_rule', 
            'ops_persona', 
            'ops_sla_instance',
            'rule_approval_persona_rel'
        ]
        for table in required_tables:
            self.env.cr.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = %s
                )
            """, (table,))
            if not self.env.cr.fetchone()[0]:
                return

        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    req.id AS id,
                    req.model_name AS res_model,
                    req.res_id AS res_id,
                    req.name AS name,
                    req.requested_by AS requester_id,
                    req.create_date AS date_request,
                    COALESCE(sla.status, 'running') AS sla_status,
                    EXTRACT(EPOCH FROM (sla.deadline - NOW())) / 3600 AS time_to_breach,
                    p.id AS required_persona_id
                FROM
                    ops_approval_request req
                LEFT JOIN
                    ops_governance_rule r ON req.rule_id = r.id
                LEFT JOIN
                    rule_approval_persona_rel rel ON r.id = rel.rule_id
                LEFT JOIN
                    ops_persona p ON rel.persona_id = p.id
                LEFT JOIN
                    ops_sla_instance sla ON sla.res_id = req.res_id
                LEFT JOIN
                    ops_sla_template tmpl ON sla.template_id = tmpl.id
                LEFT JOIN
                    ir_model m ON tmpl.model_id = m.id AND m.model = req.model_name
                WHERE
                    req.state = 'pending'
            )
        """)

    def action_view_source(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }
