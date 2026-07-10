# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    hide_pricelist_price = fields.Boolean(
        string='Hide Pricelist Price on Product',
        related='product_tmpl_id.hide_pricelist_price',
        readonly=False,
    )
    hide_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        string='Hide Pricelist From the Product',
        related='product_tmpl_id.hide_pricelist_ids',
        readonly=False,
    )
    pricelist_price_line_ids = fields.One2many(
        comodel_name='product.pricelist.price.line',
        inverse_name='product_id',
        string='Pricelist Price on The Product',
        compute='_compute_pricelist_price_line_ids',
        readonly=True,
    )
    user_display_pricelist_on_product = fields.Boolean(
        string='User: Display Pricelist on Product',
        compute='_compute_user_display_pricelist_on_product',
        help='Technical: mirrors current user preference to show/hide pricelist section in view.',
    )

    @api.depends()
    def _compute_user_display_pricelist_on_product(self):
        for product in self:
            product.user_display_pricelist_on_product = self.env.user.display_pricelist_on_product

    @api.depends(
        'product_tmpl_id', 'product_tmpl_id.list_price', 'product_tmpl_id.hide_pricelist_price',
        'product_tmpl_id.hide_pricelist_ids'
    )
    def _compute_pricelist_price_line_ids(self):
        Line = self.env['product.pricelist.price.line']
        for product in self:
            if not product.product_tmpl_id.id:
                product.pricelist_price_line_ids = Line
                continue
            if product.product_tmpl_id.hide_pricelist_price:
                product.pricelist_price_line_ids = Line
                continue
            product.pricelist_price_line_ids = product.product_tmpl_id._get_pricelist_price_lines(product)

    def write(self, vals):
        # Clean up old transient lines BEFORE write so IDs are not referenced anymore
        trigger_fields = {'hide_pricelist_ids', 'hide_pricelist_price', 'list_price'}
        if trigger_fields & set(vals.keys()):
            Line = self.env['product.pricelist.price.line']
            for template in self:
                Line.search([
                    ('product_tmpl_id', '=', template.id),
                    ('product_id', '=', False),
                ]).unlink()
        return super().write(vals)
