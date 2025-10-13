# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class StockPickingInhherit(models.Model):
    _inherit = "stock.picking"

    sample_bag_id = fields.Many2one("sample.bag", copy=False)
    is_sample_bag = fields.Boolean("Sample Bag Transfer", copy=False)

    def mark_sample_bag(self):
        self.message_post(body="Sale Order Marked as Sample Bag")
        self.is_sample_bag = True


class StockPickingTypeInherit(models.Model):
    _inherit = "stock.picking.type"

    is_sample_bag_to_warehouse = fields.Boolean(
        "Is SB to Warehouse Operation?",
        default=False,
        help="Is sample bag to warehouse transfer operation?",
    )
