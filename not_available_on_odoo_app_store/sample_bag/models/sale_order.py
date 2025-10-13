# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class SaleOrderSampleBagInherit(models.Model):
    _inherit = "sale.order"

    sample_bag_id = fields.Many2one("sample.bag", string="Sample Bag", copy=False)
    is_sample_bag = fields.Boolean("SO->SB", copy=False)
    is_sale_from_sample_bag = fields.Boolean("SB->SO", copy=False)
    sale_from_sample_bag_id = fields.Many2one(
        "sample.bag", string="Sale From Sample Bag", copy=False
    )

    def sample_bag_from_so_btn(self):
        """
        SAle order --> Sample Bag redirects method
        """
        self.ensure_one()
        sample_bag = []
        if self.sample_bag_id.id:
            sample_bag.append(self.sample_bag_id.id)
        return {
            "type": "ir.actions.act_window",
            "name": "Sample Bag",
            "view_mode": "list,form",
            "res_model": "sample.bag",
            "domain": [("id", "in", sample_bag)],
            "context": "{'create': False}",
        }

    def mark_sample_bag(self):
        self.message_post(body="Sale Order Marked as Sample Bag")
        self.is_sample_bag = True

    def unmark_sample_bag(self):
        self.message_post(body="Sale Order Un-Marked as Sample Bag")
        self.is_sample_bag = False
