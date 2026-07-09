from odoo import fields, models


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    product_item_limit = fields.Integer("Product Item Limit")
    price_history_data = fields.Selection(
        [("order_confirm", "order confirm"), ("done", "Done"), ("both", "Both")],
        default="both",
        string="Price History Based On",
    )

    def set_values(self):
        super(ResConfigSettingsInherit, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "tus_sale_price_history.price_history_data", self.price_history_data
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "tus_sale_price_history.product_item_limit", self.product_item_limit
        )

    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        res.update(
            price_history_data=self.env["ir.config_parameter"]
            .sudo()
            .get_param("tus_sale_price_history.price_history_data"),
            product_item_limit=int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("tus_sale_price_history.product_item_limit")
            ),
        )
        return res
