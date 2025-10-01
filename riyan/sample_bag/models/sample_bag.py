# See LICENSE file for full copyright and licensing details.
import base64
import io
import logging
from datetime import datetime

import xlsxwriter

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SampleBag(models.Model):
    _name = "sample.bag"
    _description = "Sample Bag model to store all details regarding sample bags"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def default_warehouse_id(self):
        warehouse_id = self.env["stock.warehouse"].sudo().search([])
        if warehouse_id:
            warehouse_id = warehouse_id[0]
        return warehouse_id.id

    name = fields.Char("Sample Bag Name")
    image_1920 = fields.Binary("Image")
    salesperson_id = fields.Many2one("res.partner", copy=False, tracking=True)
    warehouse_id = fields.Many2one(
        "stock.warehouse", copy=False, tracking=True, default=default_warehouse_id
    )
    sample_bag_date = fields.Datetime(
        "Sample Bag Date", default=lambda self: datetime.now()
    )
    last_refill_date = fields.Datetime("Last Refill Date", copy=False)
    sample_bag_lines_ids = fields.One2many(
        "sample.bag.line", "sample_bag_id", string="Sample Bag Lines"
    )
    state = fields.Selection(
        string="Status",
        selection=[("draft", "Draft"), ("in_process", "In Process"), ("done", "Done")],
        default="draft",
        tracking=True,
    )
    total_items = fields.Float(
        string="Total items in Sample Bag",
        compute="_total_items_in_sample_bag",
        readonly=True,
        help="Number of Items In Sample Bag Lines",
        store=True,
    )
    total_price = fields.Float(
        string="Total Price of Sample Bag",
        compute="_total_price_of_sample_bag",
        readonly=True,
        help="Total Price of Number of Items In Sample Bag Lines",
        store=True,
    )
    sale_order_ids = fields.One2many(
        "sale.order", "sale_from_sample_bag_id", string="Sale Orders"
    )

    sample_bag_so_count = fields.Integer(compute="_compute_sample_bag_so_count")
    so_to_sample_bag_count = fields.Integer(compute="_compute_so_to_sample_bag_count")
    sample_bag_transfers_count = fields.Integer(
        compute="_compute_sample_bag_transfers_count"
    )
    detail_file = fields.Binary("File")


    # @api.model
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         sequence = self.env["ir.sequence"].next_by_code("stock.inventory")
    #         vals["name"] = sequence or "New"
    #     return super(Inventory, self).create(vals_list)

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("sample.bag")
            if vals.get("salesperson_id", False) in self.search(
                [("state", "not in", ["done"])]
            ).mapped("salesperson_id.id"):
                raise ValidationError(
                    "You can't create other sample bag for this salesperson"
                )
        return super(SampleBag, self).create(vals_list)

    def reset_to_draft(self):
        for rec in self:
            rec.state = "draft"

    @api.depends("sample_bag_lines_ids.sample_qty")
    def _total_items_in_sample_bag(self):
        """
        Count total items in sample bag
        :return:
        """
        for sample in self:
            sample.total_items = sum(sample.sample_bag_lines_ids.mapped("sample_qty"))

    @api.depends("sample_bag_lines_ids.sample_qty")
    def _total_price_of_sample_bag(self):
        for sample in self:
            sample_price = []
            for line in sample.sample_bag_lines_ids:
                sample_price.append(line.sample_qty * line.lst_price)
            sample.total_price = sum(sample_price)

    def _compute_sample_bag_so_count(self):
        """
        Sample bag sale order counts compute method
        """
        for record in self:
            record.sample_bag_so_count = self.env["sale.order"].search_count(
                [("sale_from_sample_bag_id", "=", self.id)]
            )

    def _compute_so_to_sample_bag_count(self):
        """
        Sample bag sale order counts compute method sample bag from sale order
        """
        for record in self:
            record.so_to_sample_bag_count = self.env["sale.order"].search_count(
                [("sample_bag_id", "=", self.id)]
            )

    def _compute_sample_bag_transfers_count(self):
        """
        sample bag delivery counts compute method
        """
        for record in self:
            record.sample_bag_transfers_count = self.env["stock.picking"].search_count(
                [("sample_bag_id", "=", self.id)]
            )

    def get_sample_bag_so(self):
        """
        Sample bag sale order redirects method
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Customer Orders",
            "view_mode": "list,form",
            "res_model": "sale.order",
            "domain": [("sale_from_sample_bag_id", "=", self.id)],
            "context": "{'create': False}",
        }

    def get_so_to_sample_bag(self):
        """
        Sample bag sale order redirects method
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Distributor Orders",
            "view_mode": "list,form",
            "res_model": "sale.order",
            "domain": [("sample_bag_id", "=", self.id)],
            "context": "{'create': False}",
        }

    def get_sample_bag_transfers(self):
        """
        sample bag delivery (transfers) redirects method
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Sample Bag Transfers",
            "view_mode": "list,form",
            "res_model": "stock.picking",
            "domain": [("sample_bag_id", "=", self.id)],
            "context": "{'create': False}",
        }

    # ===== wizard second form view =========
    def open_refill_form_view(self):
        """
        Refill form view action
        """
        return {
            "name": "Refill Sample Bag",
            "view_mode": "form",
            "res_model": "sample.bag.create.so",
            "view_id": self.env.ref("sample_bag.sample_bag_refill_form_view").id,
            "context": {"refill": True},
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def get_buffer_products_list(self):
        """
        Buffer products smart button code for only non-core products
        """
        self.ensure_one()
        products_lst = []
        buffer_qty = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sample_bag.sample_bag_buffer_qty")
        )
        lines = self.sample_bag_lines_ids.filtered(lambda x: x.product_id)
        for line in lines:
            location_id = self.warehouse_id.lot_stock_id
            if location_id:
                line_qty_at_location = self.env["stock.quant"]._get_available_quantity(
                    line.product_id, location_id
                )
                if line_qty_at_location < buffer_qty:
                    products_lst.append(line.product_id.id)
        return {
            "type": "ir.actions.act_window",
            "name": "Buffer Products List",
            "view_mode": "list,form",
            "res_model": "product.product",
            "domain": [("id", "in", products_lst)],
            "context": "{'create': False}",
        }

    def start_process(self):
        """
        Start process wwith validation of warehouse enabled, products not archived, duplicates UL's
        and state changes to in_process
        """
        if self.salesperson_id and self.warehouse_id:
            if not self.salesperson_id.active or not self.warehouse_id.active:
                _logger.info(
                    "Salesperson or warehouse is archived! in this sample_bag:{}".format(
                        self.id
                    )
                )
                raise ValidationError(
                    "Please check, Salesperson or Warehouse is Archived!"
                )
        if self.sample_bag_lines_ids.filtered(lambda x: x.product_id.active == False):
            _logger.info("Some Products are Archived in sample bag line")
            raise ValidationError(
                "These Products are Archived: {}".format(
                    self.sample_bag_lines_ids.filtered(
                        lambda x: x.product_id.active == False
                    ).mapped("product_id.default_code")
                )
            )
        default_codes = self.sample_bag_lines_ids.mapped("internal_reference")
        dup_default_codes = list(
            {x for x in default_codes if default_codes.count(x) > 1}
        )
        if len(dup_default_codes):
            raise ValidationError(
                "Remove Duplicate Products:\n{}".format(dup_default_codes)
            )
        qty_missing_lines = []
        for line in self.sample_bag_lines_ids:
            location_id = self.warehouse_id.lot_stock_id
            if location_id:
                line_qty_at_location = self.env["stock.quant"]._get_available_quantity(
                    line.product_id, location_id
                )
                if line.sample_qty > line_qty_at_location:
                    qty_missing_lines.append(line.product_id.default_code)
        if qty_missing_lines:
            pass

        self.state = "in_process"
        self.sample_bag_date = datetime.now()

    # =========== Export xlsx from sample bag ==========================
    def export_sample_bag_xlsx_report(self):
        """
        generate xlsx report
        :return:
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet("Sample Bag")
        self.prepare_sample_bag_xlsx_header(workbook, sheet)
        self.write_sample_bag_data_in_xlsx_sheet(sheet, workbook)
        workbook.close()
        output.seek(0)
        output = base64.encodebytes(output.read())
        self.write({"detail_file": output})
        filename = "sample_bag_{}_{}.xlsx".format(
            self.name, datetime.now().strftime("%d_%m_%y-%H:%M:%S")
        )
        return {
            "type": "ir.actions.act_url",
            "url": "web/content/?model=sample.bag&field=detail_file&download=true&id=%s&filename=%s"
            % (self.id, filename),
            "target": "new",
        }

    def write_sample_bag_data_in_xlsx_sheet(self, sheet, workbook):
        """
        Write Data in sheet
        :return:
        """
        merge_super_col_style = workbook.add_format(
            {"font_name": "Arial", "font_size": 11, "bold": True, "align": "center"}
        )
        row = 7
        row_data_style = workbook.add_format({"font_name": "Arial"})
        if self.warehouse_id and self.warehouse_id.lot_stock_id:
            location_id = self.warehouse_id.lot_stock_id
        for line in self.sample_bag_lines_ids:
            sheet.write(
                row,
                0,
                str(line.last_refill_date.date()) if line.last_refill_date else "",
                row_data_style,
            )
            sheet.write(row, 1, line.internal_reference, row_data_style)
            sheet.write(row, 2, line.product_id.display_name, row_data_style)
            sheet.write(row, 3, line.sample_qty, row_data_style)
            line_qty_at_location = 0
            if location_id:
                line_qty_at_location = self.env["stock.quant"]._get_available_quantity(
                    line.product_id, location_id
                )
            sheet.write(row, 4, line_qty_at_location, row_data_style)
            sheet.write(row, 5, line.lst_price, row_data_style)
            row += 1
        row += 1
        sheet.write(row, 0, "Total", merge_super_col_style)
        sheet.write(row, 3, self.total_items, merge_super_col_style)
        return sheet

    def prepare_sample_bag_xlsx_header(self, workbook, sheet):
        """
        Prepare XLSX header
        :param workbook:
        :param sheet:
        :return:
        """
        merge_super_col_style = workbook.add_format(
            {"font_name": "Arial", "font_size": 11, "bold": True, "align": "center"}
        )

        super_col_style = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "font_color": "#FFA500",
                "bold": True,
            }
        )
        header = "Sample Bag"
        sheet.write(1, 0, "Exported {}".format(header), super_col_style)
        sheet.write(2, 0, "Sample Bag: {}".format(self.name), super_col_style)
        sheet.write(
            3, 0, "Salesperson: {}".format(self.salesperson_id.name), super_col_style
        )
        sheet.write(
            4,
            0,
            "Sample Bag Date: {}".format(str(self.sample_bag_date.date())),
            super_col_style,
        )
        row = 6
        sheet.write(row, 0, "Last Refill Date", merge_super_col_style)
        sheet.write(row, 1, "Internal Reference", merge_super_col_style)
        sheet.write(row, 2, "Product Name", merge_super_col_style)
        sheet.write(row, 3, "Quantity", merge_super_col_style)
        sheet.write(row, 4, "Warehouse Quantity", merge_super_col_style)
        sheet.write(row, 5, "Price", merge_super_col_style)
        return sheet

    # =========== Export xlsx from sample bag END ==========================
