# See LICENSE file for full copyright and licensing details.
import base64
import logging
from io import BytesIO

import xlrd

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger("Scrap Quantity")


class ScrapQuantity(models.TransientModel):
    _name = "scrap.quantity"
    _description = "Scrap Quantity"

    def _get_default_sample_bag(self):
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if sample_bag:
            return sample_bag.id

    scrap_quantity_line_ids = fields.One2many(
        "scrap.quantity.line", "scrap_quantity_id", string="Product Lines"
    )
    sample_bag_id = fields.Many2one("sample.bag", default=_get_default_sample_bag)
    xls_file = fields.Binary(attachment=True, string="XLS File")
    filename = fields.Char()
    add_file = fields.Selection(
        string="Add File", selection=[("file", "Upload From File")], required=False
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
        if self.xls_file:
            sample_bag = self.sample_bag_id
            work_book = self.read_xlx_file()
            if work_book:
                for sheet in work_book._sheet_list:
                    if work_book._sheet_list.index(sheet) >= 1:
                        continue
                    sheet_values = sheet._cell_values
                    cell_values = list(filter(lambda x: x[0] != "", sheet_values[1:]))
                    vals = []
                    create = False
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
                                if product_id and line and line.sample_qty >= value[1]:
                                    vals.append(
                                        {
                                            "product_id": product_id.id,
                                            # 'scrap_quantity_id':self.id,
                                            "sample_bag_line_id": line.id,
                                            "available_sample_qty": line.sample_qty,
                                            "sample_qty": value[1],
                                        }
                                    )
                        create = self.env["scrap.quantity.line"].sudo().create(vals)
                    except Exception as e:
                        _logger.info(
                            "Exeption occured while fetching lines from the sheet:{}".format(
                                e
                            )
                        )
                    # create.check_qty()
                    self.scrap_quantity_line_ids = [(6, 0, create.ids)]

    @api.onchange("sample_bag_id")
    def get_lines_for_scrap(self):
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        lines = []
        if sample_bag:
            for line in sample_bag.sample_bag_lines_ids.filtered(
                lambda x: x.sample_qty > 0
            ):
                lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "available_sample_qty": line.sample_qty,
                            "sample_qty": 0,
                            "sample_bag_line_id": line.id,
                        },
                    )
                )
        if lines:
            self.scrap_quantity_line_ids = lines

    def scrap_qty_from_bag(self):
        _logger.info(
            "======= scrap_qty_from_bag button called ====== from this bag: {}".format(
                self.sample_bag_id.name
            )
        )
        if not len(self.scrap_quantity_line_ids.filtered(lambda x: x.sample_qty > 0)):
            raise ValidationError("Atleast select one qty to scrap!")
        msg = ""
        for scrap_qty_line in self.scrap_quantity_line_ids.filtered(
            lambda x: x.sample_qty > 0
        ):
            if scrap_qty_line.sample_bag_line_id:
                scrap_qty_line.sample_bag_line_id.sample_qty = (
                    scrap_qty_line.sample_bag_line_id.sample_qty
                    - scrap_qty_line.sample_qty
                )
                msg = msg + "[Product:{},Scrapped qty:{}]".format(
                    scrap_qty_line.internal_reference, scrap_qty_line.sample_qty
                )
        if len(msg):
            _logger.info(msg)
            self.sample_bag_id.message_post(body=msg)
        lines_to_unlink = self.sample_bag_id.sample_bag_lines_ids.filtered(
            lambda x: x.sample_qty <= 0
        )
        if lines_to_unlink:
            self.sample_bag_id.message_post(
                body="Product Lines Unlinked:{}".format(
                    lines_to_unlink.mapped("product_id.default_code")
                )
            )
            lines_to_unlink.unlink()
            _logger.info(
                "Unlinking all sample bag lines whose qty will less than or equal to zero"
            )


class ScrapQuantityLLine(models.TransientModel):
    _name = "scrap.quantity.line"
    _description = "Scrap Quantity Line"

    def get_domain(self):
        domain = []
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if sample_bag:
            domain.append(
                ("id", "in", sample_bag.sample_bag_lines_ids.mapped("product_id.id"))
            )
        return domain

    scrap_quantity_id = fields.Many2one("scrap.quantity")
    product_id = fields.Many2one("product.product", string="Product", domain=get_domain)
    internal_reference = fields.Char(
        string="Internal Reference", related="product_id.default_code"
    )
    available_sample_qty = fields.Float(
        "Available Quantity", default=0, help="Available Quantity in this Sample Bag"
    )
    sample_qty = fields.Float(
        "Quantity", default=0, help="Enter Quantity count to scrap from this Sample Bag"
    )
    sample_bag_line_id = fields.Many2one("sample.bag.line", string="Sample Bag Line")

    @api.onchange("sample_qty")
    def onchange_check_qty_for_scrap(self):
        for rec in self:
            if rec.sample_qty > rec.available_sample_qty:
                rec.sample_qty = 0
                raise ValidationError(
                    "You can't scrap the quantity greater than the available quantity."
                )
