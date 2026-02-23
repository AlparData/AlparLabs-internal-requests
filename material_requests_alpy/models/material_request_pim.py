# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


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
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('pending_approval', 'Pendiente de Aprobación'),
        ('pending_stock', 'Pendiente de Stock'),
        ('approved', 'Aprobado'),
        ('shipped', 'Despachado'),
        ('delivered', 'Entregado'),
        ('canceled', 'Anulado'),
    ], string='Estado', default='draft', tracking=True, copy=False)

    location_id = fields.Many2one(
        'stock.location',
        string='Depósito Emisor',
        domain="[('usage', '=', 'internal')]",
        required=True,
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
        string='Fecha de Pedido',
        default=fields.Datetime.now,
        readonly=True,
    )
    date_approved = fields.Datetime(
        string='Fecha de Aprobación',
        readonly=True,
    )
    date_shipped = fields.Datetime(
        string='Fecha de Despacho',
        readonly=True,
    )
    date_delivered = fields.Datetime(
        string='Fecha de Entrega',
        readonly=True,
    )
    notes = fields.Text(string='Notas')
    has_stock_issues = fields.Boolean(
        string='Tiene Problemas de Stock',
        compute='_compute_has_stock_issues',
        store=True,
    )

    # ----- Smart Button counts -----
    sim_ids = fields.One2many(
        'material.request.sim',
        'pim_id',
        string='SIMs Vinculadas',
    )
    sim_count = fields.Integer(
        string='Cantidad de SIMs',
        compute='_compute_sim_count',
    )

    # =====================================================================
    # COMPUTE
    # =====================================================================
    @api.depends('sim_ids')
    def _compute_sim_count(self):
        for rec in self:
            rec.sim_count = len(rec.sim_ids)

    @api.depends('line_ids.stock_available', 'line_ids.qty_requested')
    def _compute_has_stock_issues(self):
        for rec in self:
            rec.has_stock_issues = any(
                line.stock_available < line.qty_requested
                for line in rec.line_ids
            )

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
    def action_submit(self):
        """Borrador -> Pendiente de Aprobación"""
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Debe agregar al menos un ítem de material.'))
            rec.state = 'pending_approval'

    def action_approve(self):
        """Pendiente de Aprobación -> Aprobado o Pendiente de Stock"""
        for rec in self:
            rec.date_approved = fields.Datetime.now()
            if rec.has_stock_issues:
                rec.state = 'pending_stock'
            else:
                rec.state = 'approved'

    def action_force_approve(self):
        """Pendiente de Stock -> Aprobado (forzar aprobación sin stock completo)"""
        for rec in self:
            rec.state = 'approved'

    def action_ship(self):
        """Aprobado -> Despachado"""
        for rec in self:
            rec.date_shipped = fields.Datetime.now()
            rec.state = 'shipped'

    def action_deliver(self):
        """Despachado -> Entregado"""
        for rec in self:
            rec.date_delivered = fields.Datetime.now()
            rec.state = 'delivered'

    def action_cancel(self):
        """Cualquier estado -> Anulado"""
        for rec in self:
            if rec.state == 'delivered':
                raise UserError(_('No se puede anular un PIM ya entregado.'))
            rec.state = 'canceled'

    def action_reset_draft(self):
        """Anulado -> Borrador"""
        for rec in self:
            rec.state = 'draft'

    # =====================================================================
    # SMART BUTTONS
    # =====================================================================
    def action_view_sims(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('SIMs Vinculadas'),
            'res_model': 'material.request.sim',
            'view_mode': 'list,form',
            'domain': [('pim_id', '=', self.id)],
            'context': {'default_pim_id': self.id, 'default_project_id': self.project_id.id},
        }

    def action_create_sim(self):
        """Crear SIM referenciada desde PIM en estado Pendiente de Stock, precargando materiales faltantes."""
        self.ensure_one()
        if self.state != 'pending_stock':
            raise UserError(_('Solo puede crear una SIM desde un PIM en estado "Pendiente de Stock".'))

        sim_lines = []
        for line in self.line_ids:
            missing_qty = line.qty_requested - line.stock_available
            if missing_qty > 0:
                sim_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'qty_requested': missing_qty,
                    'uom_id': line.uom_id.id,
                }))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Crear SIM Referenciada'),
            'res_model': 'material.request.sim',
            'view_mode': 'form',
            'context': {
                'default_project_id': self.project_id.id,
                'default_pim_id': self.id,
                'default_line_ids': sim_lines,
            },
            'target': 'current',
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
    state = fields.Selection(
        related='pim_id.state',
        string='Estado PIM',
        store=False,
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
    qty_shipped = fields.Float(
        string='Cantidad Despachada',
        default=0.0,
    )
    stock_available = fields.Float(
        string='Stock Disponible',
        compute='_compute_stock_available',
        store=False,
    )
    stock_status = fields.Selection([
        ('ok', 'Disponible'),
        ('partial', 'Parcial'),
        ('none', 'Sin Stock'),
    ], string='Estado de Stock', compute='_compute_stock_available')

    @api.depends('product_id', 'qty_requested', 'pim_id.location_id')
    def _compute_stock_available(self):
        for line in self:
            if line.product_id and line.pim_id.location_id:
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.pim_id.location_id.id),
                ], limit=1)
                line.stock_available = quant.quantity if quant else 0.0
            else:
                line.stock_available = 0.0

            # Determine status
            if line.stock_available >= line.qty_requested:
                line.stock_status = 'ok'
            elif line.stock_available > 0:
                line.stock_status = 'partial'
            else:
                line.stock_status = 'none'
