# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    sample_bag_count = fields.Integer(compute="_compute_sample_bag_count", default=0)

    def _compute_sample_bag_count(self):
        """
        Method for compute count of total sample bags
        """
        for record in self:
            sample_bag = (
                self.env["sample.bag.line"]
                .search([("product_id", "=", record.id)])
                .sample_bag_id
            )
            record.sample_bag_count = len(
                sample_bag.filtered(lambda x: x.state not in ["draft"])
            )

    def get_products_in_sample_bag_count(self):
        """
        Redirect method for action of sample bag for smart button
        """
        self.ensure_one()
        sample_bags = (
            self.env["sample.bag.line"]
            .search([("product_id", "=", self.id)])
            .sample_bag_id.filtered(lambda x: x.state not in ["draft"])
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Sample Bags",
            "view_mode": "list,form",
            "res_model": "sample.bag",
            "domain": [("id", "in", sample_bags.ids)],
            "context": "{'create': False}",
        }
