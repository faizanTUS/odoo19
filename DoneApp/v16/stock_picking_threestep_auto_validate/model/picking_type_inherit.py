# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    delivery_auto_validate = fields.Boolean(string="Delivery Auto Validate")
    pack_auto_validate = fields.Boolean(string="Pack Auto Validate")

    show_my_boolean_visible = fields.Boolean(
        compute='_compute_show_my_boolean_visible',
        store=False,
    )

    @api.depends(
        'warehouse_id',
        'warehouse_id.delivery_steps',
        'warehouse_id.company_id',
        'company_id',
    )
    def _compute_show_my_boolean_visible(self):
        for rec in self:
            rec.show_my_boolean_visible = False
            if (
                rec.warehouse_id
                and rec.warehouse_id.company_id == rec.company_id
                and rec.warehouse_id.delivery_steps == 'pick_pack_ship'
            ):
                rec.show_my_boolean_visible = True

    @api.constrains('delivery_auto_validate', 'pack_auto_validate')
    def _constraint_pack_auto_validate(self):
        for rec in self:
            msg = []

            if rec.pack_auto_validate:
                pack_conf = self.env['stock.warehouse'].search([
                    ('company_id', '=', rec.env.company.id),
                    ('pack_type_id', '=', rec.id),
                ])
                if not pack_conf:
                    msg.append(_("Please configure a warehouse with this operation type as Pack."))

            if rec.delivery_auto_validate:
                delivery_conf = self.env['stock.warehouse'].search([
                    ('company_id', '=', rec.env.company.id),
                    ('out_type_id', '=', rec.id),
                ])
                if not delivery_conf:
                    msg.append(_("Please configure a warehouse with this operation type as Delivery."))

            if msg:
                raise ValidationError('\n'.join(msg))
