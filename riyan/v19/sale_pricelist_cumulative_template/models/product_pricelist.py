# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    cumulative_by_template = fields.Boolean(
        string="Cumulative by Product Template",
        help="If enabled, quantity thresholds are evaluated using the "
             "sum of all variants (same product template) on the document."
    )

    def _get_price_for_qty(self, product, qty, partner=False, date=False, uom=False):
        """
        Unified helper across Odoo versions to get unit price for (product, qty).
        Keeps Odoo native rule selection; we just supply a 'qty' we want Odoo to
        evaluate against (the cumulative template quantity).
        """
        self.ensure_one()
        # Normalize inputs
        partner = partner or self.env.company.partner_id
        date = date or fields.Date.context_today(self)

        # v15–v18 share get_product_price; keep a safe fallback to _compute_price_rule
        get_price = getattr(self, "get_product_price", None)
        if callable(get_price):
            return self.get_product_price(product, qty, partner, date=date, uom=uom)

        # Fallback: handle modern _compute_price_rule signature (v18) first
        rule_fn = getattr(self, "_compute_price_rule", None)
        if callable(rule_fn):
            try:
                # Odoo 18 signature expects (products, quantity, ...)
                products = product if product._name == 'product.product' else product.product_variant_id
                res = self._compute_price_rule(
                    products=products,
                    quantity=qty,
                    currency=self.currency_id,
                    date=date,
                    uom=uom,
                )
                price, _rule_id = res.get(products.id, (0.0, False))
                return price
            except TypeError:
                # Older/alt signature fallback (tuple-based)
                res = self._compute_price_rule([(product, qty, partner)], date=date, uom_id=uom.id if uom else False)
                price, _rule_id = res.get(product.id, (0.0, False))
                return price

        # If neither exists, default list price as last resort
        return product.with_context(pricelist=self.id).price