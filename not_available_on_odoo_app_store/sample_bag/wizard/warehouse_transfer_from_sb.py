# See LICENSE file for full copyright and licensing details.
import base64
import logging
from datetime import datetime
from io import BytesIO

import xlrd

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger("Warehouse Transfer")


class WarehouseTransfer(models.TransientModel):
    _name = "warehouse.transfer"
    _description = "Warehouse Transfer"

    def _default_session(self):
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if sample_bag:
            return sample_bag.id

    def _default_partner(self):
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if sample_bag:
            return sample_bag.salesperson_id.id

    warehouse_transfer_line_ids = fields.One2many(
        "warehouse.transfer.line", "warehouse_transfer_id", string="Product Lines"
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", default=_default_partner
    )
    sample_bag_id = fields.Many2one("sample.bag", default=_default_session)
    stock_picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", string="Warehouse Transfer Operation Type"
    )
    xls_file = fields.Binary(attachment=True, string="XLS File")
    filename = fields.Char()
    add_file = fields.Selection(
        string="Add File", selection=[("file", "Upload From File")], required=False
    )

    @api.onchange("sample_bag_id")
    def update_product_lines_data(self):
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
                # stock = self.get_stock_3pl_location(sample_bag, line)
                lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "sample_qty": 0,
                            "sb_available_qty": line.sample_qty,
                        },
                    )
                )
        if lines:
            self.warehouse_transfer_line_ids = lines

    def create_warehouse_internal_transfer_from_sb(self):
        if self.partner_id and self.stock_picking_type_id and self.sample_bag_id:
            _logger.info("===== Warehouse Transfer Operation Start =====")
            picking = self.env["stock.picking"].sudo()
            picking_vals = {
                # 'picking_type_code':'internal',
                "partner_id": self.partner_id.id,
                "picking_type_id": self.stock_picking_type_id.id,
                "move_type": "direct",
                "location_id": self.stock_picking_type_id.default_location_src_id.id,
                "location_dest_id": self.stock_picking_type_id.default_location_dest_id.id,
                "sample_bag_id": self.sample_bag_id.id,
                "origin": "warehouse Transfer -> {}".format(self.sample_bag_id.name),
                "is_sample_bag": True,
                "user_id": self.env.user.id,
            }
            picking = picking.create(picking_vals)
            if picking:
                _logger.info(
                    "===== Picking Generated ->{}->{} =====".format(
                        picking.id, picking.name
                    )
                )
                lines = []
                for line in self.warehouse_transfer_line_ids.filtered(
                    lambda x: x.sample_qty > 0
                ):
                    stock_move_line_vals = {
                        # "name": line.product_id.display_name,
                        "date": datetime.now(),
                        "date_deadline": datetime.now(),
                        "company_id": self.sample_bag_id.warehouse_id.company_id.id,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.sample_qty,
                        "product_uom": line.product_id.uom_id.id,
                        "location_id": self.stock_picking_type_id.default_location_src_id.id,
                        "location_dest_id": self.stock_picking_type_id.default_location_dest_id.id,
                        "procure_method": "make_to_stock",
                    }
                    lines.append((0, 0, stock_move_line_vals))
                    parent_line = self.sample_bag_id.sample_bag_lines_ids.filtered(
                        lambda x: x.product_id.id == line.product_id.id
                    )
                    if parent_line:
                        parent_line.write(
                            {"sample_qty": parent_line.sample_qty - line.sample_qty}
                        )
                if lines:
                    picking.write({"move_ids": lines})
                self.sample_bag_id.message_post(
                    body="Warehouse Transfer Created:{} for this salesperson:{} and with this products:{} and with qty:{}".format(
                        picking.name,
                        self.partner_id.name,
                        self.warehouse_transfer_line_ids.filtered(
                            lambda x: x.sample_qty > 0
                        ).mapped("product_id.display_name"),
                        self.warehouse_transfer_line_ids.filtered(
                            lambda x: x.sample_qty > 0
                        ).mapped("sample_qty"),
                    )
                )
                # unlinking the sample bag lines whose quantity less than 0.
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
                        "Unlinking all sample bag lines whose qty will less than or equal to zero:{}".format(
                            self.sample_bag_id.name
                        )
                    )
            # picking -> action_confirm and validating the picking transfer
            self.env.cr.commit()
            if picking:
                try:
                    picking.action_confirm()
                    picking.action_assign()
                    picking.move_ids._set_quantities_to_reservation()
                    picking.with_context(
                        skip_immediate=True, skip_backorder=True
                    ).button_validate()
                except Exception as e:
                    _logger.info(
                        "Some exception occurs while vaildating the Picking of the Warehouse Transfer: {}".format(
                            e
                        )
                    )

            return picking

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
                                            # 'sample_bag_line_id': line.id,
                                            "sb_available_qty": line.sample_qty,
                                            "sample_qty": value[1],
                                        }
                                    )
                        create = self.env["warehouse.transfer.line"].sudo().create(vals)
                    except Exception as e:
                        _logger.info(
                            "Exeption occured while fetching lines from the sheet:{}".format(
                                e
                            )
                        )
                    # create.check_qty()
                    self.warehouse_transfer_line_ids = [(6, 0, create.ids)]


class WarehouseTransferLine(models.TransientModel):
    _name = "warehouse.transfer.line"
    _description = "Warehouse Transfer Line"

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

    warehouse_transfer_id = fields.Many2one("warehouse.transfer")
    product_id = fields.Many2one("product.product", string="Product", domain=get_domain)
    internal_reference = fields.Char(
        string="Internal Reference", related="product_id.default_code"
    )
    sample_qty = fields.Float("Quantity", default=0)
    lst_price = fields.Float("Price", related="product_id.lst_price")
    sb_available_qty = fields.Float(
        "Available Quantity", default=0, help="Available Quantity in this Sample Bag"
    )

    @api.onchange("sample_qty")
    def check_qty(self):
        for rec in self:
            if rec.sample_qty > rec.sb_available_qty:
                rec.sample_qty = 0
                raise ValidationError("You can't transfer more than the available qty.")
