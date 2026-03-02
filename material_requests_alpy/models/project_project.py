# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    pim_ids = fields.One2many('material.request.pim', 'project_id', string='PIMs')
    pim_count = fields.Integer(compute='_compute_pim_count', string='Cantidad PIM')

    @api.depends('pim_ids')
    def _compute_pim_count(self):
        for rec in self:
            rec.pim_count = len(rec.pim_ids)

    def action_view_pims(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('material_requests_alpy.action_pim_list')
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {'default_project_id': self.id}
        return action
