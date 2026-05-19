# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request
from odoo.osv import expression
from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleDisableOutOfStock(WebsiteSale):
    def _shop_lookup_products(self, attrib_set, options, post, search):
        fuzzy_search_term, product_count, search_product = \
            super()._shop_lookup_products(attrib_set, options, post, search)

        website = http.request.website

        if not website.hide_out_of_stock_products_from_shop:
            return fuzzy_search_term, product_count, search_product

        # Hide products with 0 On Hand quantity
        filtered_products = search_product.filtered(
            lambda p: (
                not p.is_storable
                or p.qty_available > 0
            )
        )

        return fuzzy_search_term, len(filtered_products), filtered_products

    def products_autocomplete(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):
        res = super().products_autocomplete(
            search_type=search_type,
            term=term,
            order=order,
            limit=limit,
            max_nb_chars=max_nb_chars,
            options=options,
        )

        website = request.website

        if not website.hide_out_of_stock_products_from_shop:
            return res

        # Filter autocomplete results
        filtered_results = []
        for product in res.get('products', []):
            product_record = request.env['product.template'].browse(product.get('id'))
            if not product_record.is_storable or product_record.qty_available > 0:
                filtered_results.append(product)

        res['products'] = filtered_results
        return res