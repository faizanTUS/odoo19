# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductPricelistPriceLine(models.TransientModel):
    _name = 'product.pricelist.price.line'
    _description = 'Pricelist Price Display Line'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        ondelete='cascade',
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        required=True,
        ondelete='cascade',
    )
    pricelist_name = fields.Char(
        string='Pricelist Name',
        related='pricelist_id.display_name',
        readonly=True,
    )
    min_quantity = fields.Float(
        string='Min Qty',
        digits='Product Unit of Measure',
        readonly=True,
    )
    price = fields.Float(
        string='Price',
        digits='Product Price',
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        readonly=True,
    )
    date_start = fields.Datetime(
        string='From Date',
        readonly=True,
    )
    date_end = fields.Datetime(
        string='To Date',
        readonly=True,
    )
