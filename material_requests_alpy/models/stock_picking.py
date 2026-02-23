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

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.pim_id and picking.state == 'done':
                picking.pim_id._sync_shipped_quantities_from_pickings()
        return res
