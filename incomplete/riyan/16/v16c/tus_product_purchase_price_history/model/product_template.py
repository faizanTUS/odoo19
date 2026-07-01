# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models

class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    purchase_ids = fields.One2many(
        "purchase.order.line",
        "product_template_id",
        string="Purchase Price History",
        compute="_compute_product_purchase_history",
    )

    @api.depends("purchase_ids.product_template_id")
    def _compute_product_purchase_history(self):
        for product_template in self:
            product_ids = self.env["product.product"].search(
                [("product_tmpl_id", "=", product_template.id)]
            )
            all_order_lines = self.env["purchase.order.line"]

            if product_ids:
                # Read values from res.company instead of ir.config_parameter
                item_limit = self.env.company.purchase_item_limit or 0
                history_data = self.env.company.purchase_history_data or "both"

                for product in product_ids:
                    order_lines = self.env["purchase.order.line"].search(
                        [("product_id", "=", product.id)],
                        limit=item_limit if item_limit > 0 else None
                    )

                    # Filter based on selected option
                    if history_data == "rfq":
                        order_lines = order_lines.filtered(lambda l: l.state == "draft")
                    elif history_data == "purchase":
                        order_lines = order_lines.filtered(lambda l: l.state == "purchase")

                    all_order_lines |= order_lines

            # Assign the collected order lines
            product_template.purchase_ids = [(6, 0, all_order_lines.ids)] if all_order_lines else [(5, 0, 0)]



