# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
from odoo.addons.website_sale.controllers.main import WebsiteSale


class TusImageSearch(WebsiteSale):

    def _get_search_options(self, category=None, pricelist=None, attrib_values=None, tags=None, min_price=0.0, max_price=0.0, conversion_rate=1, **post):
        options = super()._get_search_options(category=category, pricelist=pricelist, attrib_values=attrib_values, tags=tags, min_price=min_price, max_price=max_price, conversion_rate=conversion_rate, **post)
        if 'product_ids' in post.keys():
            options['product_ids'] = json.loads(post.get('product_ids', '[]'))
        return options
