# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OpsSlaMixin(models.AbstractModel):
    _name = 'ops.sla.mixin'
    _inherit = ['mail.thread']
    _description = 'SLA Mixin'

    @classmethod
    def _valid_field_parameter(cls, field, name):
        # Add 'auto_join' to valid parameters
        return name == 'auto_join' or models.BaseModel._valid_field_parameter(cls, field, name)

    sla_instance_ids = fields.One2many(
        'ops.sla.instance', 
        'res_id', 
        string='SLA Instances',
        domain=lambda self: [('res_model', '=', self._name)],
        auto_join=True
    )

    def _initiate_sla(self, template_xml_id):
        """
        Helper method to search for a template and create an instance for the current record.
        """
        self.ensure_one()
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not template or template._name != 'ops.sla.template':
            return False
        
        return self.env['ops.sla.instance'].create({
            'template_id': template.id,
            'res_id': self.id,
            'start_datetime': fields.Datetime.now(),
        })
