# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_cumulative_qty_by_template(self):
        """Build {product_tmpl_id: total_qty_in_product_uom} for this order."""
        self.ensure_one()
        qty_by_tmpl = defaultdict(float)
        for line in self.order_line:
            if not line.product_id or line.display_type:
                continue
            product = line.product_id
            # Convert ordered qty to the product's base UoM for apples-to-apples tiers
            qty_in_product_uom = line.product_uom_id._compute_quantity(
                line.product_uom_qty, product.uom_id, rounding_method="HALF-UP"
            )
            qty_by_tmpl[product.product_tmpl_id.id] += qty_in_product_uom
        return qty_by_tmpl

    def _reprice_lines_cumulative_template(self):
        """Re-price order lines using cumulative-by-template logic (if enabled)."""
        for order in self:
            pricelist = order.pricelist_id
            if not pricelist or not pricelist.cumulative_by_template:
                continue

            qty_by_tmpl = order._compute_cumulative_qty_by_template()

            for line in order.order_line:
                if not line.product_id or line.display_type:
                    continue
                product = line.product_id
                tmpl_id = product.product_tmpl_id.id
                cumulative_qty_in_product_uom = qty_by_tmpl.get(tmpl_id, 0.0)

                # Evaluate rule on cumulative qty, but get a unit price for THIS variant
                # Odoo rules (min_quantity) care only about 'qty', product-specific
                # discounts still apply if rules are variant-specific.
                unit_price = pricelist._get_price_for_qty(
                    product=product,
                    qty=cumulative_qty_in_product_uom,
                    partner=order.partner_id,
                    date=order.date_order and order.date_order.date() or fields.Date.context_today(self),
                    uom=line.product_uom_id
                )

                # Respect discount pricing policy: price_unit should be the final base unit price
                # Taxes/discounts/fiscal position will be applied by standard flows.
                line.price_unit = unit_price

                # Optional: note for audit clarity (computed, not stored)
                line.cumulative_pricing_note = "Applied {}-pcs tier (template total)".format(
                    int(round(cumulative_qty_in_product_uom))
                )

    @api.onchange('pricelist_id', 'order_line', 'order_line.product_id', 'order_line.product_uom_qty', 'order_line.product_uom_id')
    def _onchange_reprice_cumulative(self):
        # Recompute prices live in the UI
        self._reprice_lines_cumulative_template()

    def write(self, vals):
        res = super().write(vals)
        # Keep prices consistent if quantities/products changed via RPC/write
        fields_trigger = {'pricelist_id', 'order_line'}
        if fields_trigger.intersection(vals.keys()):
            for order in self:
                order._reprice_lines_cumulative_template()
        return res

    def _cart_update_order_line(self, order_line, quantity, **kwargs):
        """
        Override cart update to apply cumulative pricing when items are added/updated.
        This is the main entry point for all website cart operations:
        - Adding products to cart
        - Updating quantities
        - Removing items
        """
        # Call parent to handle standard cart logic
        values = super()._cart_update_order_line(order_line, quantity, **kwargs)


        # Apply cumulative pricing if enabled on the pricelist
        if self.pricelist_id and self.pricelist_id.cumulative_by_template:
            self._reprice_lines_cumulative_template()

        return values

    def _recompute_prices(self):
        update_value = super()._recompute_prices()
        if self.pricelist_id and self.pricelist_id.cumulative_by_template:
            self._reprice_lines_cumulative_template()

        return update_value


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cumulative_pricing_note = fields.Char(
        string="Cumulative Tier Note",
        compute="_compute_cumulative_note",
        store=False
    )

    def _compute_cumulative_note(self):
        for line in self:
            # Filled opportunistically in parent method; keep empty if not applicable
            if not getattr(line, 'cumulative_pricing_note', False):
                line.cumulative_pricing_note = False
