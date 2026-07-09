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
        config_parameter = self.env["ir.config_parameter"].sudo()
        for product_template in self:
            product_id = self.env["product.product"].search(
                [("product_tmpl_id", "=", product_template.id)]
            )
            order_lines = self.env["sale.order.line"]
            if config_parameter.get_param(
                "tus_sale_price_history.product_item_limit"
            ) and config_parameter.get_param(
                "tus_sale_price_history.price_history_data"
            ):
                order_lines = self.env["sale.order.line"].search(
                    [("product_id", "=", product_id.id)],
                    limit=int(
                        config_parameter.get_param(
                            "tus_sale_price_history.product_item_limit"
                        )
                    ),
                )
                if (
                    config_parameter.get_param(
                        "tus_sale_price_history.price_history_data"
                    )
                    == "order_confirm"
                ):
                    order_lines = order_lines.filtered(lambda l: l.state == "draft")
                elif (
                    config_parameter.get_param(
                        "tus_sale_price_history.price_history_data"
                    )
                    == "done"
                ):
                    order_lines = order_lines.filtered(lambda l: l.state == "sale")
                else:
                    order_lines = order_lines.filtered(
                        lambda l: l.state in ["draft","sale"]
                    )
            if order_lines:
                product_template.sales_ids = [(6, 0, order_lines.ids)]
            else:
                product_template.sales_ids = [(4, False)]
