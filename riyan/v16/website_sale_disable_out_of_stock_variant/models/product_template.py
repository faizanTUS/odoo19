# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.osv import expression


class WebsiteSearchableMixin(models.AbstractModel):
    _inherit = 'website.searchable.mixin'

    def _search_build_domain(self, base_domain, search, fields, search_extra=None):
        domain = super()._search_build_domain(
            base_domain,
            search,
            fields,
            search_extra
        )

        # Only apply to products
        if self._name != 'product.template':
            return domain

        website = self.env['website'].get_current_website()

        if not website.hide_out_of_stock_products_from_shop:
            return domain

        stock_domain = [
            '|',
            ('detailed_type', '=', False),
            ('qty_available', '>', 0),
        ]

        return expression.AND([domain, stock_domain])


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_additionnal_combination_info(self, product_or_template, quantity, uom, date, website):
        res = super()._get_additionnal_combination_info(product_or_template, quantity, uom, date, website)

        if not website.disable_out_of_stock_variant:
            return res

        if not product_or_template.is_product_variant:
            return res

        product = product_or_template.sudo()

        if product.detailed_type != 'product':
            return res

        free_qty = res.get('free_qty', product.free_qty)

        if free_qty <= 0:
            res['prevent_zero_price_sale'] = True
            res['compare_list_price'] = 0
            res['is_combination_possible'] = False
            res['product_type'] = 'out_of_stock'

        return res


    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        res = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        website = self.env['website'].get_current_website()
        if not website.disable_out_of_stock_variant:
            return res

        variant_id = res.get('product_id')
        if not variant_id:
            return res

        variant = self.env['product.product'].sudo().browse(variant_id)

        if variant.detailed_type != 'product':
            return res

        if variant.free_qty <= 0:
            res['is_combination_possible'] = False
            res['price'] = 0
            res['has_discounted_price'] = False

        return res
