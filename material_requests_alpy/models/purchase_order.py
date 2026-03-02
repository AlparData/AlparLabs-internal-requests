# -*- coding: utf-8 -*-
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    pim_id = fields.Many2one(
        'material.request.pim',
        string='PIM Origen',
        help='Pedido Interno de Material que originó esta compra.',
        copy=False,
    )
