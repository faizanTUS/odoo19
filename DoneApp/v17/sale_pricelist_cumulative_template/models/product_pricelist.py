# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    cumulative_by_template = fields.Boolean(
        string="Cumulative by Product Template",
        help="If enabled, quantity thresholds are evaluated using the "
        "sum of all variants (same product template) on the document.",
    )

    def _get_price_for_qty(self, product, qty, partner=False, date=False, uom=False):
        """Return unit price for ``product`` at quantity ``qty`` (native rule selection).

        ``qty`` is typically the cumulative quantity for the product template on the
        order; standard pricelist matching and rule computation apply otherwise.

        ``partner`` is accepted for compatibility with callers and customizations that
        extend price computation with partner context.
        """
        self.ensure_one()
        currency = self.currency_id or self.env.company.currency_id
        date = date or fields.Date.context_today(self)
        kw = {
            "currency": currency,
            "date": date,
        }
        if uom:
            kw["uom"] = uom
        if partner:
            kw["partner"] = partner
        return self._get_product_price(product, qty, **kw)
