# -*- coding: utf-8 -*-
from odoo import models, fields, tools

class MaterialRequestReport(models.Model):
    _name = 'material.request.report'
    _description = 'Reporte Consolidado de Solicitudes (PIM / SIM)'
    _auto = False

    name = fields.Char('Referencia', readonly=True)
    request_type = fields.Selection([('pim', 'Pañol (PIM)'), ('sim', 'Compras (SIM)')], string='Tipo', readonly=True)
    project_id = fields.Many2one('project.project', 'Obra', readonly=True)
    state = fields.Char('Estado', readonly=True)
    user_id = fields.Many2one('res.users', 'Solicitante', readonly=True)
    date_request = fields.Datetime('Fecha de Solicitud', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    p.id AS id,
                    p.name AS name,
                    'pim' AS request_type,
                    p.project_id AS project_id,
                    p.state AS state,
                    p.user_id AS user_id,
                    p.date_request AS date_request
                FROM material_request_pim p
                UNION ALL
                SELECT
                    s.id + 1000000 AS id,
                    s.name AS name,
                    'sim' AS request_type,
                    s.project_id AS project_id,
                    s.state AS state,
                    s.user_id AS user_id,
                    s.date_request AS date_request
                FROM material_request_sim s
            )
        """ % self._table)
