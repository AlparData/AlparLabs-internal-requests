# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PimCreatePoWizard(models.TransientModel):
    _name = 'pim.create.po.wizard'
    _description = 'Wizard para crear PO desde PIM'

    pim_id = fields.Many2one('material.request.pim', string='PIM', required=True)
    partner_id = fields.Many2one('res.partner', string='Proveedor', required=True, domain=[('supplier_rank', '>', 0)])

    def action_create_po(self):
        self.ensure_one()
        pim = self.pim_id

        if not pim.line_ids:
            raise UserError(_('No hay ítems en el PIM para comprar.'))

        po_vals = {
            'partner_id': self.partner_id.id,
            'pim_id': pim.id,
            'project_id': pim.project_id.id,
            'origin': pim.name,
            'order_line': [],
        }

        for line in pim.line_ids:
            po_vals['order_line'].append((0, 0, {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_qty': line.qty_requested,
                'product_uom': line.uom_id.id,
                'date_planned': fields.Datetime.to_datetime(pim.date_required),
            }))

        po = self.env['purchase.order'].create(po_vals)

        # Notificar en el chatter del PIM
        pim.message_post(
            body=f"Se ha generado un Presupuesto de Compra (RFQ): <a href='#' data-oe-model='purchase.order' data-oe-id='{po.id}'>{po.name}</a>"
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Presupuesto Creado'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
            'target': 'current',
        }
