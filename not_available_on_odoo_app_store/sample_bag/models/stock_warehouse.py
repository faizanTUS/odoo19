# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class StockWarehouseInherit(models.Model):
    _inherit = "stock.warehouse"

    sample_bag_in_type_id = fields.Many2one(
        "stock.picking.type", string="Sample Bag In Type"
    )
    sample_bag_out_type_id = fields.Many2one(
        "stock.picking.type", string="Sample Bag Out Type"
    )
