# Part of TechUltra Solutions Pvt Ltd. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from collections import defaultdict


class WebsiteSaleProductMatrix(WebsiteSale):

    def _get_shop_order(self, force_create=False):
        """
        Helper method to get the current sale order.
        In Odoo 19, the method might have changed, so we try multiple approaches.
        """
        # Try to get from session first
        sale_order_id = request.session.get('sale_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order.exists() and order.state == 'draft':
                return order

        # Try to get from partner's active orders
        partner = request.env.user.partner_id
        order = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft'),
            ('website_id', '=', request.website.id),
        ], limit=1, order='id desc')

        if order:
            request.session['sale_order_id'] = order.id
            return order

        # If force_create, create a new order
        if force_create:
            # Get pricelist - try to get from partner or website
            pricelist = partner.property_product_pricelist
            if not pricelist:
                pricelist = request.env['product.pricelist'].sudo().search([
                    '|', ('website_id', '=', request.website.id),
                    ('website_id', '=', False)
                ], limit=1)

            order = request.env['sale.order'].sudo().create({
                'partner_id': partner.id,
                'pricelist_id': pricelist.id if pricelist else False,
                'website_id': request.website.id,
            })
            request.session['sale_order_id'] = order.id
            return order

        return None

    def _prepare_product_values(self, product, category, **kwargs):
        """Override to add color_size_matrix to product values."""
        import logging
        _logger = logging.getLogger(__name__)

        values = super()._prepare_product_values(product, category, **kwargs)

        # Get current order - force create to ensure we always have one
        order = self._get_shop_order(force_create=True)

        _logger.info(f"=== MATRIX DEBUG ===")
        _logger.info(f"Product: {product.name} (ID: {product.id})")
        _logger.info(f"Order: {order}")
        _logger.info(f"Order Pricelist: {order.pricelist_id if order else 'No order'}")

        if not order or not order.pricelist_id:
            _logger.warning("No order or pricelist - returning empty matrix")
            values['color_size_matrix'] = {}
            return values

        pricelist = order.pricelist_id
        partner = order.partner_id if order else request.env.user.partner_id

        _logger.info(f"Pricelist: {pricelist.name} (ID: {pricelist.id})")
        _logger.info(f"Partner: {partner.name if partner else 'No partner'}")

        matrix_data = product._prepare_color_size_matrix_data(
            pricelist=pricelist,
            partner=partner,
        )

        _logger.info(f"Matrix data keys: {matrix_data.keys() if matrix_data else 'Empty'}")
        _logger.info(f"Matrix rows count: {len(matrix_data.get('rows', []))}")

        values['color_size_matrix'] = matrix_data
        return values

    @http.route(['/shop/cart/update_multi'], type='json', auth='public', website=True, csrf=False)
    def cart_update_multi(self, lines=None, **post):
        """
        Add multiple products to cart at once.
        Expected format: lines = [{'product_id': 123, 'quantity': 5}, ...]
        """
        # Get or create order
        order = self._get_shop_order(force_create=True)

        if not lines or not order:
            return {
                'cart_quantity': order.cart_quantity if order else 0,
                'order_id': order.id if order else False,
                'results': [],
            }

        # Check if order is in draft state
        if order.state != 'draft':
            request.session['sale_order_id'] = None
            order = self._get_shop_order(force_create=True)

        cart_results = []
        for line in lines:
            product_id = line.get('product_id')
            quantity = line.get('quantity')

            # Validate input
            try:
                product_id = int(product_id)
                quantity = float(quantity)
            except (TypeError, ValueError):
                continue

            if product_id <= 0 or quantity <= 0:
                continue

            try:
                # In Odoo 19, try _cart_update first, if it doesn't exist, use direct order line creation
                if hasattr(order, '_cart_update'):
                    res = order._cart_update(
                        product_id=product_id,
                        add_qty=quantity,
                        **post
                    )
                    cart_results.append(res)
                else:
                    # Fallback: Create order lines directly
                    product = request.env['product.product'].browse(product_id)
                    if not product.exists():
                        continue

                    # Check if product already exists in cart
                    existing_line = order.order_line.filtered(
                        lambda l: l.product_id.id == product_id and not l.is_delivery
                    )

                    if existing_line:
                        # Update existing line
                        existing_line[0].product_uom_qty += quantity
                        cart_results.append({
                            'line_id': existing_line[0].id,
                            'quantity': existing_line[0].product_uom_qty,
                        })
                    else:
                        # Create new line
                        order_line = request.env['sale.order.line'].sudo().create({
                            'order_id': order.id,
                            'product_id': product_id,
                            'product_uom_qty': quantity,
                        })
                        cart_results.append({
                            'line_id': order_line.id,
                            'quantity': order_line.product_uom_qty,
                        })
            except Exception as e:
                # Log error but continue with other lines
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f"Error adding product {product_id} to cart: {str(e)}")
                cart_results.append({
                    'line_id': False,
                    'quantity': 0,
                    'warning': str(e),
                })

        # Update session with cart quantity
        request.session['website_sale_cart_quantity'] = order.cart_quantity

        # If cart becomes empty, reset session
        if not order.cart_quantity:
            request.session['sale_order_id'] = None

        return {
            'cart_quantity': order.cart_quantity,
            'order_id': order.id if order.cart_quantity else False,
            'results': cart_results,
        }

    @http.route(['/shop/matrix/get_prices'], type='json', auth='public', website=True, csrf=False)
    def get_matrix_prices(self, product_template_id, quantities=None, **post):
        """
        Get prices for variants based on each variant's quantity.
        quantities: dict {variant_id: quantity}
        Returns: dict {variant_id: {'price': price, 'unit_price': unit_price}}
        """
        if not quantities:
            quantities = {}

        product_template = request.env['product.template'].browse(int(product_template_id))
        if not product_template.exists():
            return {}

        # Get current order - force create to ensure we always have one
        order = self._get_shop_order(force_create=True)

        if not order or not order.pricelist_id:
            return {}

        pricelist = order.pricelist_id
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

        # Process each variant with proper pricing context
        for variant_id, qty_value in qty_map.items():
            variant = ProductProduct.browse(variant_id)
            if not variant.exists():
                continue

            # Use pricelist method to get accurate price
            unit_price = pricelist._get_product_price(
                product=variant,
                quantity=qty_value,
                currency=pricelist.currency_id,
                date=False,
                uom=variant.uom_id,
            )

            results[variant_id] = {
                'price': unit_price * qty_value,
                'unit_price': unit_price,
            }

        return results