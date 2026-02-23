# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'

    pim_ids = fields.One2many('material.request.pim', 'project_id', string='PIMs')
    pim_count = fields.Integer(compute='_compute_pim_count', string='Cantidad PIM')
    
    sim_ids = fields.One2many('material.request.sim', 'project_id', string='SIMs')
    sim_count = fields.Integer(compute='_compute_sim_count', string='Cantidad SIM')

    @api.depends('pim_ids')
    def _compute_pim_count(self):
        for rec in self:
            rec.pim_count = len(rec.pim_ids)

    @api.depends('sim_ids')
    def _compute_sim_count(self):
        for rec in self:
            rec.sim_count = len(rec.sim_ids)

    def action_view_pims(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('material_requests_alpy.action_pim_list')
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {'default_project_id': self.id}
        return action

    def action_view_sims(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('material_requests_alpy.action_sim_list')
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {'default_project_id': self.id}
        return action
