# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MaterialRequestPIM(models.Model):
    _name = 'material.request.pim'
    _description = 'Pedido Interno de Material (PIM)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    project_id = fields.Many2one(
        'project.project',
        string='Obra / Centro de Costo',
        required=True,
        tracking=True,
        states={'requested': [('readonly', False)]},
        readonly=True,
    )
    sim_id = fields.Many2one(
        'material.request.sim',
        string='Referencia SIM',
        help='Vínculo informativo a una SIM existente. No es vinculante.',
        tracking=True,
    )
    state = fields.Selection([
        ('requested', 'Solicitado'),
        ('quotation', 'En Cotización'),
        ('po_issued', 'Orden de Compra Emitida'),
        ('received', 'Ingresado a Depósito'),
        ('closed', 'Cerrado'),
        ('canceled', 'Anulado'),
    ], string='Estado', default='requested', tracking=True, copy=False)

    priority = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Media'),
        ('2', 'Alta'),
        ('3', 'CRÍTICA'),
    ], string='Prioridad', default='1', tracking=True)

    justification = fields.Text(
        string='Justificación',
        required=True,
        help='Justificación obligatoria del pedido de material.',
    )
    line_ids = fields.One2many(
        'material.request.pim.line',
        'pim_id',
        string='Ítems de Material',
        copy=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Solicitante',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True,
    )
    date_request = fields.Datetime(
        string='Fecha de Solicitud',
        default=fields.Datetime.now,
        readonly=True,
    )
    date_quotation = fields.Datetime(
        string='Fecha de Cotización',
        readonly=True,
    )
    date_po_issued = fields.Datetime(
        string='Fecha de OC',
        readonly=True,
    )
    date_received = fields.Datetime(
        string='Fecha de Ingreso',
        readonly=True,
    )
    date_closed = fields.Datetime(
        string='Fecha de Cierre',
        readonly=True,
    )
    notes = fields.Text(string='Notas')

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'pim_attachment_rel',
        'pim_id',
        'attachment_id',
        string='Adjuntos',
        help='Presupuestos, fotos de referencia u otros documentos.',
    )

    # ----- Smart Button: linked purchase orders -----
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        'pim_purchase_order_rel',
        'pim_id',
        'purchase_order_id',
        string='Órdenes de Compra',
    )
    purchase_order_count = fields.Integer(
        string='Cantidad OC',
        compute='_compute_purchase_order_count',
    )

    # =====================================================================
    # COMPUTE
    # =====================================================================
    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(rec.purchase_order_ids)

    # =====================================================================
    # CRUD
    # =====================================================================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'material.request.pim'
                ) or _('New')
        return super().create(vals_list)

    # =====================================================================
    # STATE TRANSITIONS
    # =====================================================================
    def action_send_quotation(self):
        """Solicitado -> En Cotización"""
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Debe agregar al menos un ítem de material.'))
            if not rec.justification:
                raise UserError(_('La justificación es obligatoria.'))
            rec.date_quotation = fields.Datetime.now()
            rec.state = 'quotation'

    def action_issue_po(self):
        """En Cotización -> Orden de Compra Emitida"""
        for rec in self:
            rec.date_po_issued = fields.Datetime.now()
            rec.state = 'po_issued'

    def action_receive(self):
        """Orden de Compra Emitida -> Ingresado a Depósito"""
        for rec in self:
            rec.date_received = fields.Datetime.now()
            rec.state = 'received'

    def action_close(self):
        """Ingresado a Depósito -> Cerrado"""
        for rec in self:
            rec.date_closed = fields.Datetime.now()
            rec.state = 'closed'

    def action_cancel(self):
        """Cualquier estado -> Anulado"""
        for rec in self:
            if rec.state == 'closed':
                raise UserError(_('No se puede anular un PIM ya cerrado.'))
            rec.state = 'canceled'

    def action_reset_draft(self):
        """Anulado -> Solicitado"""
        for rec in self:
            rec.state = 'requested'

    # =====================================================================
    # SMART BUTTONS
    # =====================================================================
    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        if self.purchase_order_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.purchase_order_ids[0].id
        else:
            action['domain'] = [('id', 'in', self.purchase_order_ids.ids)]
        return action

    def action_view_sim(self):
        self.ensure_one()
        if not self.sim_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': _('SIM Vinculada'),
            'res_model': 'material.request.sim',
            'view_mode': 'form',
            'res_id': self.sim_id.id,
        }


class MaterialRequestPIMLine(models.Model):
    _name = 'material.request.pim.line'
    _description = 'Línea de PIM'

    pim_id = fields.Many2one(
        'material.request.pim',
        string='PIM',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Material',
        required=True,
    )
    product_category_id = fields.Many2one(
        related='product_id.categ_id',
        string='Categoría',
        store=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unidad de Medida',
        related='product_id.uom_id',
        readonly=True,
    )
    qty_requested = fields.Float(
        string='Cantidad Solicitada',
        required=True,
        default=1.0,
    )
    notes = fields.Char(string='Notas')
