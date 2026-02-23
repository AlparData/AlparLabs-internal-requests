# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pim_id = fields.Many2one(
        'material.request.pim',
        string='PIM Origen',
        help='Pedido Interno de Material que originó este movimiento.',
        copy=False,
    )
