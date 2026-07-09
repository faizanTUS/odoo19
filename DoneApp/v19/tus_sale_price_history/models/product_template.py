# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    sales_ids = fields.One2many(
        "sale.order.line",
        "product_template_id",
        string="Sale Price History",
        compute="_compute_product_sale_history",
    )

    @api.depends("sales_ids.product_template_id")
    def _compute_product_sale_history(self):
        config = self.env["ir.config_parameter"].sudo()

        item_limit = int(config.get_param("tus_sale_price_history.product_item_limit", 0))
        history_data = config.get_param("tus_sale_price_history.price_history_data", "all")

        for product_template in self:
            products = product_template.product_variant_ids

            if not products:
                product_template.sales_ids = [(5, 0, 0)]  # clear
                continue
            domain = [("product_id", "in", products.ids)]
            order_lines = self.env["sale.order.line"].search(domain, limit=item_limit or None)

            if history_data == "order_confirm":
                order_lines = order_lines.filtered(lambda l: l.state == "draft")
            elif history_data == "done":
                order_lines = order_lines.filtered(lambda l: l.state == "sale")
            else:
                order_lines = order_lines.filtered(lambda l: l.state in ["draft", "sale"])
            if order_lines:
                product_template.sales_ids = [(6, 0, order_lines.ids)]
            else:
                product_template.sales_ids = [(5, 0, 0)]
