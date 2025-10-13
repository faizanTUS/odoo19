# See LICENSE file for full copyright and licensing details.
from odoo import fields, models
from odoo.exceptions import ValidationError


class SampleBagFromSO(models.TransientModel):
    _name = "sample.bag.from.so"

    sample_bag_id = fields.Many2one("sample.bag", string="Sample Bag")
    is_existing_sample_bag = fields.Boolean("Is Existing Sample Bag", default=False)

    def update_existing_sample_bag(self):
        """
        Sample Bag refill case is from internal transfers with the help of the defined configuration of the operation type.
        """
        internal_transfer = (
            self.env["stock.picking"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        sample_bag = self.sample_bag_id
        if (
            internal_transfer
            and internal_transfer.picking_type_code == "internal"
            and sample_bag
        ):
            if internal_transfer.partner_id.id != sample_bag.salesperson_id.id:
                raise ValidationError(
                    "Please select the correct sample bag!\nSale Order->{}, Sample Bag->{}".format(
                        internal_transfer.partner_id.name,
                        sample_bag.salesperson_id.name,
                    )
                )
            if sample_bag:
                internal_transfer_uls = (
                    internal_transfer.move_line_ids.mapped(
                        "product_id.default_code"
                    )
                )
                # sample bag internal reference which has qty greater than 0, for 0 qty we will update the qty in sample bag
                sample_bag_uls = sample_bag.sample_bag_lines_ids.filtered(
                    lambda x: x.sample_qty > 0
                ).mapped("product_id.default_code")
                [ul for ul in internal_transfer_uls if ul in sample_bag_uls]

                if not len(
                    internal_transfer.move_line_ids.filtered(
                        lambda x: x.product_id
                    )
                ):
                    raise ValidationError(
                        "All Products are there in sample bag or No Products available to add in sample bag!"
                    )
                lines = []
                for line in internal_transfer.move_line_ids.filtered(
                    lambda x: x.product_id and x.quantity > 0
                ):
                    sample_bag_line = sample_bag.sample_bag_lines_ids.filtered(
                        lambda x: x.product_id.default_code
                        == line.product_id.default_code
                    )
                    if sample_bag_line:
                        sample_bag_line.write(
                            {
                                "sample_qty": line.quantity
                                + sample_bag_line.sample_qty,
                                "last_refill_date": internal_transfer.scheduled_date,
                            }
                        )
                    else:
                        lines.append(
                            (
                                0,
                                0,
                                {
                                    "product_id": line.product_id.id,
                                    "sample_qty": line.quantity,
                                    "sample_bag_id": sample_bag.id,
                                    "last_refill_date": internal_transfer.scheduled_date,
                                },
                            )
                        )
                if lines:
                    sample_bag.sample_bag_lines_ids = lines
                internal_transfer.sample_bag_id = sample_bag.id
                # unlinking the sample bag lines whose quantity less than 0.
                lines_to_unlink = sample_bag.sample_bag_lines_ids.filtered(
                    lambda x: x.sample_qty <= 0
                )
                if lines_to_unlink:
                    sample_bag.message_post(
                        body="Product Lines Unlinked:{}".format(
                            lines_to_unlink.mapped("product_id.default_code")
                        )
                    )
                    lines_to_unlink.unlink()

    def create_new_sample_bag(self):
        internal_transfer = (
            self.env["stock.picking"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if internal_transfer.partner_id.id in self.env["sample.bag"].search(
            [("state", "not in", ["done"])]
        ).mapped("salesperson_id.id"):
            raise ValidationError(
                "There is already sample bag assigned to this salesperson"
            )
        if internal_transfer:
            internal_transfer.picking_type_id.warehouse_id.lot_stock_id
            sample_bag_vals = {
                "salesperson_id": internal_transfer.partner_id.id,
                "warehouse_id": internal_transfer.picking_type_id.warehouse_id.id,
            }
        sample_bag = self.env["sample.bag"].sudo().create(sample_bag_vals)
        if sample_bag:
            lines = []
            for line in internal_transfer.move_line_ids.filtered(
                lambda x: x.product_id
            ):
                lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "sample_qty": line.quantity,
                            "sample_bag_id": sample_bag.id,
                            "last_refill_date": internal_transfer.scheduled_date,
                        },
                    )
                )
            if lines:
                sample_bag.sample_bag_lines_ids = lines
            internal_transfer.sample_bag_id = sample_bag.id
            # unlinking the sample bag lines whose quantity less than 0.
            lines_to_unlink = sample_bag.sample_bag_lines_ids.filtered(
                lambda x: x.sample_qty <= 0
            )
            if lines_to_unlink:
                sample_bag.message_post(
                    body="Product Lines Unlinked:{}".format(
                        lines_to_unlink.mapped("product_id.default_code")
                    )
                )
                lines_to_unlink.unlink()
