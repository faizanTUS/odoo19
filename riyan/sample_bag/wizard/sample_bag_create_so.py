# See LICENSE file for full copyright and licensing details.
import base64
import logging
from datetime import datetime
from io import BytesIO

import xlrd

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SampleBagCreateSO(models.TransientModel):
    _name = "sample.bag.create.so"
    _description = "Sample Bag Create SO Wizard model"

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

    sample_bag_create_so_line_ids = fields.One2many(
        "sample.bag.create.so.line", "sample_bag_create_so_id", string="Product Lines"
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", default=_default_partner
    )
    sample_bag_id = fields.Many2one("sample.bag", default=_default_session)
    is_normal_order = fields.Boolean("Deliver from Warehouse ?", default=True)
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
                    create = False
                    lines = []
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
                                    qty = self.env[
                                        "stock.quant"
                                    ]._get_available_quantity(
                                        product_id,
                                        line.sample_bag_id.warehouse_id.lot_stock_id,
                                    )
                                    lines.append(
                                        {
                                            "product_id": line.product_id.id,
                                            "sample_qty": value[1],
                                            "qty_at_location": qty,
                                        }
                                    )
                        if lines:
                            create = (
                                self.env["sample.bag.create.so.line"]
                                .sudo()
                                .create(lines)
                            )
                            self.sample_bag_create_so_line_ids = [(6, 0, create.ids)]
                    except Exception as e:
                        _logger.info(
                            "Exeption occured while fetching lines from the sheet:{}".format(
                                e
                            )
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
            for line in sample_bag.sample_bag_lines_ids:
                line.sample_qty
                stock = self.get_stock_3pl_location(sample_bag, line)
                lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.id,
                            "sample_qty": 0,
                            "qty_at_location": stock[1],
                        },
                    )
                )
        if lines:
            self.sample_bag_create_so_line_ids = lines

    def get_stock_3pl_location(self, sample_bag_id, line):
        good_stock = location_qty = 0
        location_id = sample_bag_id.warehouse_id.lot_stock_id
        if location_id:
            location_qty = self.env["stock.quant"]._get_available_quantity(
                line.product_id, location_id
            )
        return good_stock, location_qty

    def create_sample_bag_so(self):
        sample_bag = (
            self.env["sample.bag"]
            .sudo()
            .browse(int(self.env.context.get("active_id", False)))
        )
        if len(self.sample_bag_create_so_line_ids) == 0:
            raise ValidationError("Atleast select one product to make Sale Order!")
        default_codes = self.sample_bag_create_so_line_ids.mapped("internal_reference")
        dup_default_codes = list(
            {x for x in default_codes if default_codes.count(x) > 1}
        )
        if len(dup_default_codes):
            raise ValidationError(
                "Remove Duplicate Products:\n{}".format(dup_default_codes)
            )
        if sample_bag:
            for line in self.sample_bag_create_so_line_ids.filtered(
                lambda x: x.sample_qty > 0
            ):
                parent_line = sample_bag.sample_bag_lines_ids.filtered(
                    lambda x: x.product_id.id == line.product_id.id
                )
                if (
                    not self.is_normal_order
                    and parent_line.sample_qty < line.sample_qty
                ):
                    raise ValidationError(
                        "Product Quantity must not be greater than Demanded Quantity \n {}".format(
                            parent_line.product_id.default_code
                        )
                    )
                if self.is_normal_order and line.qty_at_location < line.sample_qty:
                    raise ValidationError(
                        "Product Quantity must not be greater than Demanded Quantity \n {}".format(
                            parent_line.product_id.default_code
                        )
                    )
            sale_order = self.create_sale_order_sample_bag(self, sample_bag)

            if sale_order:
                try:
                    if self.is_normal_order:
                        sale_order.state = "sent"
                    # sale_order.action_confirm()
                    if not self.is_normal_order:
                        # sale_order.state = 'sale'
                        sale_order.action_confirm()
                        picking = sale_order.picking_ids.filtered(
                            lambda x: x.state not in ["done", "cancel"]
                            and x.picking_type_code == "outgoing"
                        )
                        picking_type, src_location, dest_location = False, False, False
                        if sale_order.warehouse_id.sample_bag_out_type_id:
                            picking_type = (
                                sale_order.warehouse_id.sample_bag_out_type_id
                            )
                            src_location = (
                                sale_order.warehouse_id.sample_bag_out_type_id.default_location_src_id
                            )
                            dest_location = (
                                sale_order.warehouse_id.sample_bag_out_type_id.default_location_dest_id
                            )
                        if (
                            not picking
                            and picking_type
                            and src_location
                            and dest_location
                        ):
                            procurement = (
                                self.env["procurement.group"]
                                .sudo()
                                .search(
                                    [
                                        ("name", "=", sale_order.name),
                                        ("move_type", "=", "direct"),
                                        ("sale_id", "=", sale_order.id),
                                    ],
                                    limit=1,
                                )
                            )

                            if not procurement:
                                procurement = (
                                    self.env["procurement.group"]
                                    .sudo()
                                    .create(
                                        {
                                            "name": sale_order.name,
                                            "move_type": "direct",
                                            "sale_id": sale_order.id,
                                        }
                                    )
                                )
                            picking_vals = {
                                # 'picking_type_code':'internal',
                                "partner_id": sale_order.partner_shipping_id.id,
                                "picking_type_id": picking_type.id,
                                "move_type": "direct",
                                "location_id": src_location.id,
                                "location_dest_id": dest_location.id,
                                "sample_bag_id": sample_bag.id,
                                "origin": "{}-{}".format(
                                    sample_bag.salesperson_id.name, sale_order.name
                                ),
                                "is_sample_bag": True,
                                "group_id": procurement.id,
                                "sale_id": sale_order.id,
                            }
                            picking = self.env["stock.picking"].create(picking_vals)
                        if picking:
                            picking = picking[0]
                            picking.write({"state": "draft"})
                            picking.write(
                                {
                                    "picking_type_id": picking_type.id,
                                    "location_id": src_location.id,
                                    "location_dest_id": dest_location.id,
                                }
                            )
                            self.env.cr.commit()
                            if len(
                                sale_order.order_line.filtered(lambda x: x.product_id)
                            ) == len(
                                picking.move_ids.filtered(
                                    lambda x: x.product_id
                                )
                            ):
                                picking.move_ids.write(
                                    {
                                        "picking_type_id": picking_type.id,
                                        "location_id": src_location.id,
                                        "location_dest_id": dest_location.id,
                                    }
                                )
                                picking.write({"state": "confirmed"})
                            if len(
                                sale_order.order_line.filtered(lambda x: x.product_id)
                            ) == len(
                                picking.move_line_ids.filtered(
                                    lambda x: x.product_id
                                )
                            ):
                                picking.move_line_ids.write(
                                    {
                                        "picking_type_id": picking_type.id,
                                        "location_id": src_location.id,
                                        "location_dest_id": dest_location.id,
                                    }
                                )
                                self.env.cr.commit()
                                picking.write({"state": "confirmed"})
                                picking.action_confirm()
                                picking.action_assign()
                                picking.move_ids._set_quantities_to_reservation()
                                picking.with_context(
                                    skip_immediate=True, skip_backorder=True
                                ).button_validate()
                            if len(
                                sale_order.order_line.filtered(lambda x: x.product_id)
                            ) != len(
                                picking.move_ids.filtered(
                                    lambda x: x.product_id
                                )
                            ):
                                lines_vals = []
                                for line in sale_order.order_line.filtered(
                                    lambda x: x.product_id
                                ):
                                    stock_move_line_vals = {
                                        "name": line.product_id.display_name,
                                        "date": datetime.now(),
                                        "date_deadline": datetime.now(),
                                        "company_id": sale_order.company_id.id,
                                        "product_id": line.product_id.id,
                                        "product_uom_qty": line.product_uom_qty,
                                        "sale_line_id": line.id,
                                        "product_uom": line.product_uom.id,
                                        "location_id": src_location.id,
                                        "location_dest_id": dest_location.id,
                                        "procure_method": "make_to_stock",
                                    }
                                    lines_vals.append((0, 0, stock_move_line_vals))
                                if lines_vals:
                                    picking.write(
                                        {"move_ids": lines_vals}
                                    )
                                    picking.group_id = procurement.id
                                    picking.action_confirm()
                            sample_bag.message_post(
                                body="Delivery Order Created:{} from this sale order:{}`".format(
                                    picking.name, sale_order.name
                                )
                            )
                            if sample_bag:
                                # unlinking the sample bag lines whose quantity less than 0.
                                lines_to_unlink = (
                                    sample_bag.sample_bag_lines_ids.filtered(
                                        lambda x: x.sample_qty <= 0
                                    )
                                )
                                if lines_to_unlink:
                                    sample_bag.message_post(
                                        body="Product Lines Unlinked:{}".format(
                                            lines_to_unlink.mapped(
                                                "product_id.default_code"
                                            )
                                        )
                                    )
                                    lines_to_unlink.unlink()
                                    _logger.info(
                                        "Unlinking all sample bag lines whose qty will less than or equal to zero:{}".format(
                                            sample_bag.name
                                        )
                                    )
                            self.env.cr.commit()

                        # if sale_order.picking_ids:
                        #     picking = sale_order.picking_ids.filtered(lambda x:x.state not in ['done','cancel'])
                        #     if picking:
                        #         picking.action_confirm()
                        #         picking.action_assign()
                        #         if picking.state not in ['done', 'cancel']:
                        #             picking.delivery_validate_custom(picking)
                        #             self.env.cr.commit()
                        if picking.sale_id:
                            invoice = picking.sale_id._create_invoices()
                            _logger.info(
                                "Sample Bag-> Invoice Generated for this picking:{} ".format(
                                    picking.name
                                )
                            )
                            if invoice:
                                invoice.action_post()
                    _logger.info("====== SB->SO, Sample Bag Order ===== END =====")
                except Exception as e:
                    _logger.info(
                        "Exception occurs while performing the sale order confirm or posting from sample bag:{}".format(
                            e
                        )
                    )

    def create_sale_order_sample_bag(self, data, sample_bag):
        if data and sample_bag:
            if len(data.sample_bag_create_so_line_ids) == len(
                data.sample_bag_create_so_line_ids.filtered(lambda x: x.sample_qty == 0)
            ):
                raise ValidationError(
                    "Please Select atleast one product with Quantity!"
                )
            if (
                len(
                    data.sample_bag_create_so_line_ids.filtered(
                        lambda x: x.sample_qty > 0
                    )
                )
                > 0
            ):
                try:
                    user_id = (
                        sample_bag.salesperson_id.user_id.id
                        if sample_bag.salesperson_id.user_id
                        else self.env.uid
                    )
                    so_values = {
                        "date_order": datetime.now(),
                        "partner_id": data.partner_id.id,
                        "partner_invoice_id": data.partner_id.id,
                        "partner_shipping_id": data.partner_id.id,
                        "company_id": sample_bag.warehouse_id.company_id.id,
                        "warehouse_id": sample_bag.warehouse_id.id,
                        "user_id": user_id,
                        # "l10n_in_journal_id": sample_bag.warehouse_id.l10n_in_sale_journal_id.id,
                        # 'team_id': self.env['website'].search([],limit=1).crm_default_team_id.id,
                        "sale_from_sample_bag_id": sample_bag.id,
                    }
                    if not self.is_normal_order:
                        so_values.update({"is_sale_from_sample_bag": True})
                    # 'sample_bag_id': sample_bag.id,
                    # 'is_sample_bag':True
                    # removed this bcoz now we have o2m connection from sample bag to sale order
                    sale_order = self.env["sale.order"].create(so_values)
                    if sale_order:
                        lines = []
                        for line in data.sample_bag_create_so_line_ids.filtered(
                            lambda x: x.sample_qty > 0
                        ):
                            line_values = {
                                "order_id": sale_order.id,
                                "product_id": line.product_id.id,
                                "product_uom_qty": line.sample_qty,
                                "price_unit": line.product_id.lst_price,
                            }
                            lines.append((0, 0, line_values))
                            # ========== commented bcoz now this part is shifted to stock_move_line create part ========
                            # ========= qty deduct from the sale order line =========
                            if not self.is_normal_order:
                                parent_line = sample_bag.sample_bag_lines_ids.filtered(
                                    lambda x: x.product_id.id == line.product_id.id
                                )
                                if parent_line:
                                    sample_qty = (
                                        parent_line.sample_qty - line.sample_qty
                                    )
                                    parent_line.write({"sample_qty": sample_qty})
                        if lines:
                            sale_order.write({"order_line": lines})
                        sample_bag.message_post(
                            body="Sale Order Created:{} with this Customer:{}".format(
                                sale_order.name, sale_order.partner_id.name
                            )
                        )
                        if sample_bag:
                            # unlinking the sample bag lines whose quantity less than 0.
                            lines_to_unlink = sample_bag.sample_bag_lines_ids.filtered(
                                lambda x: x.sample_qty <= 0
                            )
                            if lines_to_unlink:
                                sample_bag.message_post(
                                    body="Product Lines Unlinked:{}".format(
                                        lines_to_unlink.mapped(
                                            "product_id.default_code"
                                        )
                                    )
                                )
                                lines_to_unlink.unlink()
                                _logger.info(
                                    "Unlinking all sample bag lines whose qty will less than or equal to zero:{}".format(
                                        sample_bag.name
                                    )
                                )

                        return sale_order
                except Exception as e:
                    _logger.info("Exception occurs {}".format(e))


class SampleBagCreateSO(models.TransientModel):
    _name = "sample.bag.create.so.line"
    _description = "Sample Bag Create SO Line"

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

    sample_bag_create_so_id = fields.Many2one("sample.bag.create.so")
    update_salesperson_id = fields.Many2one(comodel_name="update.salesperson")
    product_id = fields.Many2one("product.product", string="Product", domain=get_domain)
    internal_reference = fields.Char(
        string="Internal Reference", related="product_id.default_code"
    )
    sample_qty = fields.Float("Quantity", default=0)
    qty_at_location = fields.Float(
        "Location Qty", default=0, compute="_compute_warehouse_location_qty"
    )
    lst_price = fields.Float("Price", related="product_id.lst_price")
    available_sample_qty = fields.Float(
        "Available Quantity", default=0, help="Available Quantity in this Sample Bag"
    )

    @api.depends("product_id", "sample_qty")
    def _compute_warehouse_location_qty(self):
        for rec in self:
            sample_bag = (
                self.env["sample.bag"]
                .sudo()
                .browse(int(self.env.context.get("active_id", False)))
            )
            if sample_bag:
                if rec.product_id and rec.sample_bag_create_so_id:
                    stock_details = self.env[
                        "sample.bag.create.so"
                    ].get_stock_3pl_location(sample_bag, rec)
                    rec.write({"qty_at_location": stock_details[1]})
                if rec.product_id and not rec.sample_bag_create_so_id:
                    rec.qty_at_location = 0
                if not rec.product_id:
                    rec.qty_at_location = 0

    @api.onchange("sample_qty")
    def check_qty(self):
        for rec in self:
            if rec.sample_bag_create_so_id.is_normal_order:
                if rec.sample_qty > rec.qty_at_location:
                    pass
                    # raise ValidationError(
                    #     "Product Demanded Quantity must not be greater than 3PL Quantity or Warehouse Location Quantity")
            if not rec.sample_bag_create_so_id.is_normal_order:
                if rec.sample_bag_create_so_id.sample_bag_id:
                    parent_line = rec.sample_bag_create_so_id.sample_bag_id.sample_bag_lines_ids.filtered(
                        lambda x: x.internal_reference == rec.internal_reference
                    )
                    if parent_line:
                        if rec.sample_qty > parent_line.sample_qty:
                            raise ValidationError(
                                "Product Demanded Quantity must not be greater than Sample Bag Product Quantity"
                            )
            if rec.product_id and not rec.sample_bag_create_so_id:
                if rec.sample_qty > rec.available_sample_qty:
                    raise ValidationError(
                        "You can't transfer more than the available qty."
                    )
