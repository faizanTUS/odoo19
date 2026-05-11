# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_cumulative_qty_by_template(self):
        """Return {product_tmpl_id: total_qty_in_product_uom} for this order."""
        self.ensure_one()
        qty_by_tmpl = defaultdict(float)
        for line in self.order_line:
            if not line.product_id or line.display_type:
                continue
            product = line.product_id
            qty_in_product_uom = line.product_uom._compute_quantity(
                line.product_uom_qty,
                product.uom_id,
                rounding_method="HALF-UP",
            )
            qty_by_tmpl[product.product_tmpl_id.id] += qty_in_product_uom
        return qty_by_tmpl

    def _reprice_lines_cumulative_template(self):
        """Re-price order lines using cumulative-by-template logic when enabled."""
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

                unit_price = pricelist._get_price_for_qty(
                    product=product,
                    qty=cumulative_qty_in_product_uom,
                    partner=order.partner_id,
                    date=order.date_order and order.date_order.date()
                    or fields.Date.context_today(self),
                    uom=line.product_uom,
                )

                line.price_unit = unit_price

    @api.onchange(
        "pricelist_id",
        "order_line",
        "order_line.product_id",
        "order_line.product_uom_qty",
        "order_line.product_uom",
    )
    def _onchange_reprice_cumulative(self):
        self._reprice_lines_cumulative_template()

    def write(self, vals):
        res = super().write(vals)
        if {"pricelist_id", "order_line"} & vals.keys():
            for order in self:
                order._reprice_lines_cumulative_template()
        return res

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        values = super()._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kwargs,
        )
        if self.pricelist_id and self.pricelist_id.cumulative_by_template:
            self._reprice_lines_cumulative_template()
        return values

    def _recompute_prices(self):
        super()._recompute_prices()
        if self.pricelist_id and self.pricelist_id.cumulative_by_template:
            self._reprice_lines_cumulative_template()
