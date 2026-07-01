# Part of TechUltra Solutions Pvt Ltd. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from collections import defaultdict


class WebsiteSaleProductMatrix(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        values = super()._prepare_product_values(product, category, search, **kwargs)
        website = request.website
        pricelist = website.sudo().get_current_pricelist()
        if not pricelist:
            values['color_size_matrix'] = {}
            return values
        order = website.sale_get_order()
        partner = order.partner_id if order else request.env.user.partner_id
        values['color_size_matrix'] = product._prepare_color_size_matrix_data(
            pricelist=pricelist,
            partner=partner,
        )
        return values

    @http.route(['/shop/cart/update_multi'], type='json', auth='public', website=True, csrf=False)
    def cart_update_multi(self, lines=None, **post):
        order = request.website.sale_get_order(force_create=True)
        if not lines or not order:
            return {
                'cart_quantity': order.cart_quantity if order else 0,
                'order_id': order.id if order else False,
                'results': [],
            }

        # Check if order is in draft state
        if order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order(force_create=True)

        cart_results = []
        for line in lines:
            product_id = line.get('product_id')
            quantity = line.get('quantity')
            try:
                product_id = int(product_id)
                quantity = float(quantity)
            except (TypeError, ValueError):
                continue

            if product_id <= 0 or quantity <= 0:
                continue

            try:
                res = order._cart_update(product_id=product_id, add_qty=quantity, **post)
                cart_results.append(res)
            except Exception as e:
                # Log error but continue with other lines
                cart_results.append({
                    'line_id': False,
                    'quantity': 0,
                    'warning': str(e),
                })

        # Update session with cart quantity (cart_quantity is a computed field)
        request.session['website_sale_cart_quantity'] = order.cart_quantity

        # If cart becomes empty, reset it (like base controller does)
        if not order.cart_quantity:
            request.website.sale_reset()

        return {
            'cart_quantity': order.cart_quantity,
            'order_id': order.id if order.cart_quantity else False,
            'results': cart_results,
        }

    @http.route(['/shop/matrix/get_prices'], type='json', auth='public', website=True, csrf=False)
    def get_matrix_prices(self, product_template_id, quantities=None, **post):
        """
        Get prices for variants based on each variant's quantity (standard Odoo flow).
        quantities: dict {variant_id: quantity}
        Returns: dict {variant_id: {'price': price, 'unit_price': unit_price}}
        """
        if not quantities:
            quantities = {}

        product_template = request.env['product.template'].browse(int(product_template_id))
        if not product_template.exists():
            return {}

        website = request.website
        pricelist = website.sudo().get_current_pricelist()
        if not pricelist:
            return {}

        order = website.sale_get_order()
        partner = order.partner_id if order else request.env.user.partner_id

        # Convert quantities to numeric and ignore zeros
        qty_map = {}
        for variant_id_str, qty in quantities.items():
            try:
                variant_id = int(variant_id_str)
                qty_val = float(qty) if qty else 0.0
            except (ValueError, TypeError):
                continue
            if qty_val <= 0:
                continue
            qty_map[variant_id] = qty_val

        # If no variant has qty, return empty
        if not qty_map:
            return {}

        ProductProduct = request.env['product.product']
        results = {}

        # Group variants by same quantity to optimize price rule calls
        qty_groups = defaultdict(list)
        for variant_id, qty in qty_map.items():
            qty_groups[qty].append(variant_id)

        # Compute price per group
        for qty_value, variant_ids in qty_groups.items():
            variants = ProductProduct.browse(variant_ids)
            if not variants:
                continue

            price_info = pricelist._compute_price_rule(
                products=variants,
                qty=qty_value,
                currency=pricelist.currency_id,
                date=False,
                uom=False,
            )

            for variant in variants:
                unit_price, rule_id = price_info.get(
                    variant.id, (variant.lst_price or 0.0, False)
                )
                variant_qty = qty_map.get(variant.id, 0.0)

                results[variant.id] = {
                    'price': unit_price * variant_qty,
                    'unit_price': unit_price,
                }

        return results


