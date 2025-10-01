# See LICENSE file for full copyright and licensing details.
import base64
import logging
from io import BytesIO

import xlrd

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class UpdateSalesPerson(models.TransientModel):
    _name = "update.salesperson"
    _description = "Update Salesperson in the sample bag"

    salesperson_id = fields.Many2one(
        "res.partner",
    )
    # domain = [('is_salesperson', '=', True)]
    is_partial = fields.Boolean("Is Partial", default=False)
    is_complete_transfer = fields.Boolean("Is Complete Transfer", default=False)
    sample_bag_create_so_line_ids = fields.One2many(
        "sample.bag.create.so.line", "update_salesperson_id", string="Product Lines"
    )
    sample_bag_id = fields.Many2one("sample.bag", string="Sample Bag", copy=False)
    xls_file = fields.Binary(attachment=True, string="XLS File")
    filename = fields.Char()
    add_file = fields.Selection(
        string="Add File", selection=[("file", "Upload From File")], required=False
    )

    def reassign_salesperson(self):
        sample_bag_rec = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        existing_sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .search(
                [
                    ("state", "not in", ["done"]),
                    ("salesperson_id", "=", self.salesperson_id.id),
                ]
            )
        )
        if existing_sample_bag:
            raise ValidationError(
                "You can't assign other sample bag for this salesperson"
            )
        if not self.salesperson_id:
            raise ValidationError("Please select salesperson which you want to update")
        try:
            if sample_bag_rec and not existing_sample_bag:
                sample_bag_rec.write({"salesperson_id": self.salesperson_id.id})
                self.env.cr.commit()
                sample_bag_rec.message_post(body="Reassign Salesperson Button Called!")
        except Exception as e:
            _logger.info("Exception occurs: {}".format(e))

    @api.onchange("is_partial")
    def update_product_lines_data(self):
        if self.is_complete_transfer:
            self.is_complete_transfer = False
        if self.is_partial:
            sample_bag = (
                self.env["sample.bag"]
                .sudo()
                .browse(int(self.env.context.get("active_id", False)))
            )
            lines = []
            if sample_bag:
                for line in sample_bag.sample_bag_lines_ids:
                    lines.append(
                        (
                            0,
                            0,
                            {
                                "product_id": line.product_id.id,
                                "sample_qty": 0,
                                "available_sample_qty": line.sample_qty,
                            },
                        )
                    )
            if lines:
                self.sample_bag_create_so_line_ids = lines
        if not self.is_partial:
            self.sample_bag_create_so_line_ids.unlink()

    @api.onchange("is_complete_transfer")
    def transfer_complete_sample_bag(self):
        if self.is_partial:
            self.is_partial = False
            self.env.cr.commit()
        if not self.is_complete_transfer and self.sample_bag_create_so_line_ids:
            self.sample_bag_create_so_line_ids.unlink()

    def create_partial_sample_bag(self):
        sample_bag_msg = ""
        selected_sample_bag_msg = ""
        if not self.sample_bag_id:
            _logger.info(
                "sample bag not set while doing the operation of is_partial from sample bag"
            )
            raise ValidationError(
                "Please select the sample bag in which you want to transfer the sample products!"
            )
        if (
            sum(self.sample_bag_create_so_line_ids.mapped("sample_qty")) == 0
            and self.is_partial
        ):
            raise ValidationError(
                "Atleast select one product or one quantity for any product to make Partial Sample Bag!"
            )
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if self.sample_bag_id:
            if self.sample_bag_id.state == "done":
                raise ValidationError("The sample bag is in already done state!")
        if sample_bag and self.sample_bag_id and self.is_partial:
            _logger.info(
                "==== Partial sample bag called from this sample bag:{} and the destination sample bag is:{}".format(
                    sample_bag.name, self.sample_bag_id.name
                )
            )
            lines = []
            for line in self.sample_bag_create_so_line_ids.filtered(
                lambda x: x.sample_qty > 0
            ):
                selected_sample_bag_line_id = (
                    self.sample_bag_id.sample_bag_lines_ids.filtered(
                        lambda x: x.internal_reference == line.internal_reference
                    )
                )
                if selected_sample_bag_line_id:
                    selected_sample_bag_line_id[0].write(
                        {
                            "sample_qty": selected_sample_bag_line_id[0].sample_qty
                            + line.sample_qty
                        }
                    )
                if not selected_sample_bag_line_id:
                    line_vals = {
                        "product_id": line.product_id.id,
                        "sample_qty": line.sample_qty,
                        "sample_bag_id": self.sample_bag_id.id,
                    }
                    lines.append((0, 0, line_vals))
                sample_bag_line = sample_bag.sample_bag_lines_ids.filtered(
                    lambda x: x.product_id == line.product_id
                )
                if sample_bag_line:
                    sample_bag_line.sample_qty = (
                        sample_bag_line.sample_qty - line.sample_qty
                    )
            self.sample_bag_id.write({"sample_bag_lines_ids": lines})
            _logger.info("===== lines:{} =====".format(lines))
            sample_bag_msg = (
                sample_bag_msg
                + "\nQuantities transferred to this sample bag:{}\nProducts:{},qty:{}".format(
                    self.sample_bag_id.name,
                    self.sample_bag_create_so_line_ids.filtered(
                        lambda x: x.sample_qty > 0
                    ).mapped("product_id.default_code"),
                    self.sample_bag_create_so_line_ids.filtered(
                        lambda x: x.sample_qty > 0
                    ).mapped("sample_qty"),
                )
            )
            selected_sample_bag_msg = (
                selected_sample_bag_msg
                + "\nQuantities added from this sample bag:{}\nProducts:{},qty:{}".format(
                    sample_bag.name,
                    self.sample_bag_create_so_line_ids.filtered(
                        lambda x: x.sample_qty > 0
                    ).mapped("product_id.default_code"),
                    self.sample_bag_create_so_line_ids.filtered(
                        lambda x: x.sample_qty > 0
                    ).mapped("sample_qty"),
                )
            )
            sample_bag.message_post(body=sample_bag_msg)
            self.sample_bag_id.message_post(body=selected_sample_bag_msg)
        if sample_bag and self.sample_bag_id and self.is_complete_transfer:
            _logger.info(
                "==== Complete sample bag called from this sample bag:{} and the destination sample bag is:{}".format(
                    sample_bag.name, self.sample_bag_id.name
                )
            )
            lines = []
            qty = sample_bag.sample_bag_lines_ids.mapped("sample_qty")
            for line in sample_bag.sample_bag_lines_ids.filtered(
                lambda x: x.sample_qty > 0
            ):
                selected_sample_bag_line_id = (
                    self.sample_bag_id.sample_bag_lines_ids.filtered(
                        lambda x: x.internal_reference == line.internal_reference
                    )
                )
                if selected_sample_bag_line_id:
                    selected_sample_bag_line_id[0].write(
                        {
                            "sample_qty": selected_sample_bag_line_id[0].sample_qty
                            + line.sample_qty
                        }
                    )
                if not selected_sample_bag_line_id:
                    line_vals = {
                        "product_id": line.product_id.id,
                        "sample_qty": line.sample_qty,
                        "sample_bag_id": self.sample_bag_id.id,
                    }
                    lines.append((0, 0, line_vals))
                sample_bag_line = sample_bag.sample_bag_lines_ids.filtered(
                    lambda x: x.product_id == line.product_id
                )
                if sample_bag_line:
                    sample_bag_line.sample_qty = (
                        sample_bag_line.sample_qty - line.sample_qty
                    )
            self.sample_bag_id.write({"sample_bag_lines_ids": lines})
            _logger.info("===== lines:{} =====".format(lines))
            #            After complete transfer of inv to other sample bag we will lock this order (Done)
            sample_bag.update({"state": "done"})
            sample_bag_msg = (
                sample_bag_msg
                + "\nQuantities transferred to this sample bag:{}\nProducts:{},qty:{}".format(
                    self.sample_bag_id.name,
                    sample_bag.sample_bag_lines_ids.mapped("product_id.default_code"),
                    qty,
                )
            )
            selected_sample_bag_msg = (
                selected_sample_bag_msg
                + "\nQuantities added from this sample bag:{}\nProducts:{},qty:{}".format(
                    sample_bag.name,
                    sample_bag.sample_bag_lines_ids.mapped("product_id.default_code"),
                    qty,
                )
            )
            sample_bag.message_post(body=sample_bag_msg)
            self.sample_bag_id.message_post(body=selected_sample_bag_msg)
        if sample_bag:
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
                _logger.info(
                    "Unlinking all sample bag lines whose qty will less than or equal to zero:{}".format(
                        sample_bag.name
                    )
                )

    def read_xlx_file(self):
        """
        cursereate Temp xlx file
        """
        file_data = self.xls_file
        work_book = False
        if not file_data:
            pass
            # raise UserError(_('Error!', "Please Select a File"))
        else:
            val = base64.b64decode(file_data)
            tempfile = BytesIO()
            tempfile.write(val)
            work_book = xlrd.open_workbook(file_contents=tempfile.getvalue())
        return work_book

    @api.onchange("xls_file")
    def get_lines_from_sheet(self):
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        work_book = self.read_xlx_file()
        if work_book:
            for sheet in work_book._sheet_list:
                if work_book._sheet_list.index(sheet) >= 1:
                    continue
                sheet_values = sheet._cell_values
                cell_values = list(filter(lambda x: x[1] != "", sheet_values[1:]))
                vals = []
                try:
                    for value in cell_values:
                        if value[0]:
                            product_id = (
                                self.env["product.product"]
                                .sudo()
                                .search(
                                    [("default_code", "=", str(value[0]).strip())],
                                    limit=1,
                                )
                            )
                            line = sample_bag.sample_bag_lines_ids.filtered(
                                lambda x: x.product_id == product_id
                            )
                            if product_id and line:
                                vals.append(
                                    {
                                        "product_id": product_id.id,
                                        "update_salesperson_id": self.id,
                                        "available_sample_qty": line.sample_qty,
                                        "sample_qty": value[1],
                                    }
                                )
                    create = self.env["sample.bag.create.so.line"].create(vals)
                except Exception as e:
                    _logger.info(
                        "Exeption occured while fetching lines from the sheet:{}".format(
                            e
                        )
                    )
                # create.check_qty()
                self.sample_bag_create_so_line_ids = [(6, 0, create.ids)]
