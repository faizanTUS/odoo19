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

    def _get_price_for_qty(self, product, qty, date=False, uom=False):
        """Unit price for ``product`` at quantity ``qty`` (native pricelist rule selection).

        ``qty`` is the quantity used to match min_quantity tiers (e.g. cumulative template qty).
        """
        self.ensure_one()
        if not product:
            return 0.0
        date = date or fields.Datetime.now()
        currency = self.currency_id or self.env.company.currency_id
        return self._get_product_price(
            product,
            qty,
            uom=uom or product.uom_id,
            date=date,
            currency=currency,
        )
