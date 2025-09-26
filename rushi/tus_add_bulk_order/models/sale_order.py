# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger("Add Bulk Order")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def add_bulk_order_line_with_variant(self, sale_order_id, variant_id, quantity, price_unit=None):
        """
        Add order line with specific product variant and optional custom price.
        If price_unit is None, it will use the product's default list_price.
        """
        order = self.browse(sale_order_id)
        variant = self.env['product.product'].browse(variant_id)

        if not variant.exists():
            raise ValueError(f"Product variant with ID {variant_id} not found")

        attribute_values = []
        for ptav in variant.product_template_attribute_value_ids:
            attribute_values.append(f"{ptav.attribute_id.name}: {ptav.product_attribute_value_id.name}")

        attribute_display = f" ({', '.join(attribute_values)})" if attribute_values else ""

        line_vals = {
            'order_id': order.id,
            'product_id': variant_id,
            'product_uom_qty': quantity,
            'product_uom_id': variant.uom_id.id,
            'price_unit': price_unit if price_unit is not None else variant.list_price,  # Use custom price or default

            'name': f"{variant.display_name}{attribute_display}",
        }

        line = self.env['sale.order.line'].create(line_vals)

        _logger.info(
            f"Created sale order line: {line.id} for variant {variant_id} with quantity {quantity} at price {line_vals['price_unit']}")

        return line.id
