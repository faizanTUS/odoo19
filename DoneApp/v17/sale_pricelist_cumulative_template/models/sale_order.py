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
            qty_in_product_uom = line.product_uom_id._compute_quantity(
                line.product_uom_qty,
                product.uom_id,
                rounding_method="HALF-UP",
            )
            qty_by_tmpl[product.product_tmpl_id.id] += qty_in_product_uom
        return qty_by_tmpl

    def _reprice_lines_cumulative_template(self):
        """Re-price order lines using cumulative-by-template logic when enabled on the pricelist."""
        for order in self:
            pricelist = order.pricelist_id
            if not pricelist or not pricelist.cumulative_by_template:
                continue

            qty_by_tmpl = order._compute_cumulative_qty_by_template()
            price_date = (
                order.date_order and order.date_order.date()
            ) or fields.Date.context_today(order)

            for line in order.order_line:
                if not line.product_id or line.display_type:
                    continue
                product = line.product_id
                tmpl_id = product.product_tmpl_id.id
                cumulative_qty = qty_by_tmpl.get(tmpl_id, 0.0)

                line.price_unit = pricelist._get_price_for_qty(
                    product=product,
                    qty=cumulative_qty,
                    partner=order.partner_id,
                    date=price_date,
                    uom=line.product_uom_id,
                )

    @api.onchange(
        "pricelist_id",
        "order_line",
        "order_line.product_id",
        "order_line.product_uom_qty",
        "order_line.product_uom_id",
    )
    def _onchange_reprice_cumulative(self):
        self._reprice_lines_cumulative_template()

    def write(self, vals):
        res = super().write(vals)
        if {"pricelist_id", "order_line"} & vals.keys():
            for order in self:
                order._reprice_lines_cumulative_template()
        return res

    def _cart_update_order_line(self, order_line, quantity, **kwargs):
        res = super()._cart_update_order_line(order_line, quantity, **kwargs)
        if self.pricelist_id.cumulative_by_template:
            self._reprice_lines_cumulative_template()
        return res

    def _recompute_prices(self):
        super()._recompute_prices()
        self.filtered(
            lambda o: o.pricelist_id.cumulative_by_template
        )._reprice_lines_cumulative_template()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    _CUMULATIVE_REPRICE_FIELDS = frozenset(
        {"product_uom_qty", "product_uom_id", "product_id", "display_type"}
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.order_id.filtered(
            lambda o: o.pricelist_id.cumulative_by_template
        )._reprice_lines_cumulative_template()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if self._CUMULATIVE_REPRICE_FIELDS & vals.keys():
            self.order_id.filtered(
                lambda o: o.pricelist_id.cumulative_by_template
            )._reprice_lines_cumulative_template()
        return res

    def unlink(self):
        orders = self.order_id
        res = super().unlink()
        orders.filtered(
            lambda o: o.pricelist_id.cumulative_by_template
        )._reprice_lines_cumulative_template()
        return res
