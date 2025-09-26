# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields,api
from odoo.tools import float_is_zero, is_html_empty


class ProductTemplate(models.Model):
    _inherit = "product.template"

    compute_price = fields.Float(string="Computed Price", compute="_compute_price", store=False)

    @api.depends('standard_price')
    def _compute_price(self):
        for product in self:
            cost_price = product.standard_price
            computed_price = cost_price

            pricing_rules = self.env['product.pricelist.item'].search([
                ('min_cost', '<=', cost_price),
                ('max_cost', '>=', cost_price)
            ], order='min_cost ASC', limit=1)

            if pricing_rules:
                computed_price = cost_price * (1 + pricing_rules.price_markup / 100)

            product.compute_price = computed_price
