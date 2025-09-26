# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields,api
from odoo.exceptions import ValidationError

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    min_cost = fields.Float(string="Min Cost", required=True)
    max_cost = fields.Float(string="Max Cost", required=True)

    @api.constrains('min_cost', 'max_cost')
    def _check_cost_range(self):
        for rule in self:
            if rule.min_cost > rule.max_cost:
                raise ValidationError("Min Cost cannot be greater than Max Cost.")

            overlapping_rules = self.search([
                ('id', '!=', rule.id),
                ('pricelist_id', '=', rule.pricelist_id.id),
                ('min_cost', '<=', rule.max_cost),
                ('max_cost', '>=', rule.min_cost)
            ])
            if overlapping_rules:
                raise ValidationError("Overlapping pricing rules detected. Please adjust the cost range.")

    def write(self, vals):
        res = super(ProductPricelistItem, self).write(vals)
        if 'price_markup' in vals:
            self._update_sale_order_prices()
        return res

    def _update_sale_order_prices(self):
        for rule in self:
            sale_lines = self.env['sale.order.line'].search([
                ('product_id.standard_price', '>=', rule.min_cost),
                ('product_id.standard_price', '<=', rule.max_cost),
                ('order_id.pricelist_id', '=', rule.pricelist_id.id),
                ('order_id.state', '=', 'draft')
            ])

            for line in sale_lines:
                new_price = line.product_id.standard_price * (1 + rule.price_markup / 100)
                line.write({'price_unit': new_price})

    def _compute_price(self, product, quantity, uom, date, currency=None):
        pricelist = self.env.context.get('pricelist')
        if not pricelist:
            pricelist = self.env['product.pricelist'].browse(self.env.user.partner_id.property_product_pricelist.id)
        res = super()._compute_price(product, quantity, uom, date, currency)
        
        pricing_rules = self.env['product.pricelist.item'].search([
            ('min_cost', '<=', product.standard_price),
            ('max_cost', '>=', product.standard_price),
            ('pricelist_id', '=', pricelist.id) 
        ], order='min_cost ASC', limit=1)

        if pricing_rules:
            pricelist_price = product.standard_price * (1 + pricing_rules.price_markup / 100)
            return pricelist_price
        return res
