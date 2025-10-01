# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SampleBagLine(models.Model):
    _name = "sample.bag.line"
    _description = "Sample Bag Line"
    _order = "sequence asc"

    product_id = fields.Many2one("product.product", string="Product")
    sample_qty = fields.Float("Quantity")
    sample_bag_id = fields.Many2one("sample.bag")
    internal_reference = fields.Char(
        string="Internal Reference", related="product_id.default_code"
    )
    lst_price = fields.Float("Price", related="product_id.lst_price")
    qty_at_location = fields.Float(
        "Location Qty", compute="_compute_warehouse_location_qty", default=0
    )
    out_sample_bag = fields.Float(
        "Other Sample Bag Count",
        copy=False,
        compute="_count_total_products_in_other_sample_bags",
        help="This field describes the count of other sample bags where this product exist.",
    )
    last_refill_date = fields.Datetime("Last Refill Date", copy=False)
    sequence = fields.Integer(string="Sequence", default=10)

    @api.depends("sample_qty")
    def _count_total_products_in_other_sample_bags(self):
        for rec in self:
            rec.out_sample_bag = len(
                self.env["sample.bag.line"]
                .search(
                    [
                        ("product_id", "=", rec.product_id.id),
                        ("sample_bag_id", "!=", rec.sample_bag_id.id),
                    ]
                )
                .sample_bag_id.filtered(lambda x: x.state not in ["draft"])
                .ids
            )

    @api.depends("product_id", "sample_qty")
    def _compute_warehouse_location_qty(self):
        """
        Warehouse location qty => compute method to store the qty in the sample bag line
        """
        for rec in self:
            if rec.product_id:
                location_id = rec.sample_bag_id.warehouse_id.lot_stock_id
                if location_id:
                    rec.qty_at_location = self.env[
                        "stock.quant"
                    ]._get_available_quantity(rec.product_id, location_id)
                if not location_id:
                    rec.qty_at_location = 0
            if not rec.product_id:
                rec.qty_at_location = 0

    def sample_bags_redirect_action(self):
        """
        Sample bag line button for redirecting the sample bags which contains this product
        """
        sample_bags = (
            self.env["sample.bag.line"]
            .search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("sample_bag_id", "!=", self.sample_bag_id.id),
                ]
            )
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
