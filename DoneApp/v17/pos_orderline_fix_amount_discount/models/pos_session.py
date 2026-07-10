# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models


class POSSession(models.Model):
    _inherit = 'pos.session'

    def get_total_discount(self):
        amount = 0
        for line in self.env['pos.order.line'].search([('order_id', 'in', self._get_closed_orders().ids), '|', ('discount', '>', 0), ('discount_amount', '>', 0)]):
            original_price = line.tax_ids.compute_all(line.price_unit, line.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id)['total_included']
            amount += original_price - line.price_subtotal_incl
        return amount
