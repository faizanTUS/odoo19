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
        """Unit price for ``product`` when rules are evaluated at quantity ``qty``.

        Uses the standard pricelist API so partner, date, and UoM match native
        behaviour (Odoo 16: ``_get_product_price``).
        """
        self.ensure_one()
        partner = partner or self.env.company.partner_id
        date = date or fields.Date.context_today(self)
        return self._get_product_price(
            product,
            qty,
            uom=uom or None,
            date=date,
            partner=partner,
        )
