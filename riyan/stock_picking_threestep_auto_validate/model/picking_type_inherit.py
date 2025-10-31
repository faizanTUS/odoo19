# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    delivery_auto_validate = fields.Boolean(string="Delivery Auto Validate")
    pack_auto_validate = fields.Boolean(string="Pack Auto Validate")

    show_my_boolean_visible = fields.Boolean(
        compute="_compute_show_my_boolean_visible",
        store=False
    )

    def _compute_show_my_boolean_visible(self):
        for rec in self:
            rec.show_my_boolean_visible = False
            # Ensure warehouse belongs to same company as picking type
            if rec.warehouse_id and rec.warehouse_id.company_id == rec.company_id:
                # Check the selection value in warehouse
                if rec.warehouse_id.delivery_steps == 'pick_pack_ship':
                    rec.show_my_boolean_visible = True


    # @api.constrains('delivery_auto_validate', 'pack_auto_validate')
    # def _constraint_pack_auto_validate(self):
    #     pack_conf = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id), ('pack_type_id', '=', self.id)])
    #     delivery_conf = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id), ('out_type_id', '=', self.id)])
    #     pack_msg = 'Please set a pack in warehouse'
    #     deliver_msg = 'Please set a delivery in warehouse'
    #     msg = ''
    #     if pack_conf:
    #         msg += "pack_msg: %s "% (pack_msg)
    #     if delivery_conf:
    #         msg += "%sdeliver_msg: %s" % ('\n' if pack_msg else '', deliver_msg)
    #     if pack_conf or delivery_conf:
    #         raise ValidationError(_(msg))

    @api.constrains('delivery_auto_validate', 'pack_auto_validate')
    def _constraint_pack_auto_validate(self):
        for rec in self:
            msg = []

            if rec.pack_auto_validate:
                pack_conf = self.env['stock.warehouse'].search([
                    ('company_id', '=', rec.env.company.id),
                    ('pack_type_id', '=', rec.id)
                ])
                if not pack_conf:
                    msg.append(_("Please configure a warehouse with this operation type as Pack."))

            if rec.delivery_auto_validate:
                delivery_conf = self.env['stock.warehouse'].search([
                    ('company_id', '=', rec.env.company.id),
                    ('out_type_id', '=', rec.id)
                ])
                if not delivery_conf:
                    msg.append(_("Please configure a warehouse with this operation type as Delivery."))

            if msg:
                raise ValidationError("\n".join(msg))