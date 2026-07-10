# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models
class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_purchase_ids = fields.One2many(
        "purchase.order.line",
        "product_id",
        string="Purchase Orders"
    )

    @api.depends("variant_purchase_ids.product_id")
    def _compute_product_variant_purchase_history(self):
        config_parameter = self.env["ir.config_parameter"].sudo()
        for product in self:
            item_limit = int(
                config_parameter.get_param("tus_product_purchase_price_history.purchase_item_limit") or 0
            )
            history_data = config_parameter.get_param("tus_product_purchase_price_history.purchase_history_data") or "both"

            order_lines = self.env["purchase.order.line"].search(
                [("product_id", "=", product.id)],
                limit=item_limit if item_limit > 0 else None
            )

            # Filter based on state
            if history_data == "rfq":
                order_lines = order_lines.filtered(lambda l: l.state == "draft")
            elif history_data == "purchase":
                order_lines = order_lines.filtered(lambda l: l.state == "purchase")
            elif history_data == "both":
                order_lines = order_lines.filtered(lambda l: l.state in ["draft", "purchase"])

            # Assign the collected order lines to product product
            product.variant_purchase_ids = [(6, 0, order_lines.ids)] if order_lines else [(5, 0, 0)]
