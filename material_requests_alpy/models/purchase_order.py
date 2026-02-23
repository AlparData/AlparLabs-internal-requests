# -*- coding: utf-8 -*-
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sim_id = fields.Many2one(
        'material.request.sim',
        string='SIM Origen',
        help='Solicitud Interna de Material que originó esta compra.',
        copy=False,
    )
