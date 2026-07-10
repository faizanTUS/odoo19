# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    discount_amount = fields.Float(string="Discount Amount")

    def _export_for_ui(self, orderline):
        result = super()._export_for_ui(orderline)
        result['discount_amount'] = orderline.discount_amount
        return result
