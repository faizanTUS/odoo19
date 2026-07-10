# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_amount = fields.Float(string="Discount Amount")

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'discount_amount')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False
            # Compute 'price_subtotal'.
            # This line is customization
            line_discount_price_unit = (line.price_unit * (1 - (line.discount / 100.0)))
            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total'.
            if line.tax_ids:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded'] - line.discount_amount
                line.price_total = taxes_res['total_included'] - line.discount_amount
            else:
                line.price_total = line.price_subtotal = subtotal - line.discount_amount

    def _convert_to_tax_base_line_dict(self):
        res = super()._convert_to_tax_base_line_dict()
        res.update({'discount_amount': self.discount_amount})
        return res
