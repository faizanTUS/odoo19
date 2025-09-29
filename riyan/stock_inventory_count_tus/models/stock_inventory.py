# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare
from odoo.tools.misc import OrderedSet
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo import SUPERUSER_ID
_logger = logging.getLogger("Inventory Counting")


class Inventory(models.Model):
    """
    Inventory
    """

    _name = "stock.inventory"
    _description = "Inventory"
    _order = "date desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        "Internal Reference",
        readonly=True,
        required=True,
        default=lambda self: _("New"),
    )
    duration = fields.Float("Duration (Hours)", compute="compute_duration", store=True)
    total_product = fields.Integer("Total Product", compute="compute_total_product")
    start_date = fields.Datetime("Start Date", default=fields.Date.today())
    end_date = fields.Datetime("End Date")

    date = fields.Datetime(
        "Inventory Date",
        readonly=True,
        required=True,
        default=fields.Datetime.now,
        help="If the inventory adjustment is not validated, date at which the theoretical quantities have been checked.\n"
        "If the inventory adjustment is validated, date at which the inventory adjustment has been validated.",
    )
    line_ids = fields.Many2many(
        "stock.quant",
        string="Inventories",
        copy=False,
        readonly=False,
    )
    move_ids = fields.Many2many(
        "stock.move",
        string="Stock Move",
        copy=False,
        readonly=False,
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("cancel", "Cancelled"),
            ("confirm", "In Progress"),
            ("done", "Validated"),
        ],
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
    )

    company_id = fields.Many2one(
        "res.company",
        "Company",
        index=True,
        required=True,
        default=lambda self: self.env.company,
        readonly = True,
    )

    location_ids = fields.Many2many(
        "stock.location",
        string="Locations",
        check_company=True,
        domain="[('company_id', '=', company_id), ('usage', '=', 'internal')]",
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        check_company=True,
        domain="[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True,
        help="Specify Products to focus your inventory on particular Products.",
    )
    start_empty = fields.Boolean(
        "Empty Inventory", help="Allows to start with an empty inventory."
    )
    prefill_counted_quantity = fields.Selection(
        string="Counted Quantities",
        default="counted",
        help="Allows to start with a pre-filled counted quantity for each lines or "
        "with all counted quantities set to zero.",
        selection=[
            ("counted", "Default to stock on hand"),
            ("zero", "Default to zero"),
        ],
    )
    exhausted = fields.Boolean(
        "Include Exhausted Products",
        readonly=True,
        help="Include also products with quantity of 0",
    )
    is_lock = fields.Boolean("Is Lock")
    inventory_line_ids = fields.One2many(
        "stock.inventory.line",
        "inventory_id",
        string="Inventories",
        copy=False,
        readonly=False,
    )
    user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.uid, string="Responsible"
    )

    is_inventory_count = fields.Boolean(
        string="Is Inventory Count", copy=False, default=True
    )
    stock_inventory_category = fields.Many2one(
        "product.category", string="Category", tracking=True
    )
    from_date_range = fields.Datetime("From Date", tracking=True)
    to_date_range = fields.Datetime(
        "To Date", tracking=True, default=lambda self: fields.Datetime.now()
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", tracking=True)

    # @api.model
    # def create(self, vals):
    #     vals["name"] = self.env["ir.sequence"].next_by_code("stock.inventory") or "New"
    #     return super(Inventory, self).create(vals)

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            sequence = self.env["ir.sequence"].next_by_code("stock.inventory")
            vals["name"] = sequence or "New"
        return super(Inventory, self).create(vals_list)

    def compute_total_product(self):
        for rec in self:
            rec.total_product = len(
                rec.inventory_line_ids
                and rec.inventory_line_ids.mapped("product_id")
                or []
            )

    @api.depends("start_date", "end_date")
    def compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration = (
                    fields.Datetime.from_string(record.end_date)
                    - fields.Datetime.from_string(record.start_date)
                ).total_seconds() / 3600
            else:
                record.duration = 0

    def action_view_stock_inventory_line(self):
        view = self.env.ref("stock_inventory_count_tus.stock_inventory_line_list")
        return {
            "type": "ir.actions.act_window",
            "name": _("Inventory Line"),
            "res_model": "stock.inventory.line",
            "views": [(view.id, "list")],
            "domain": [("id", "in", self.inventory_line_ids.ids)],
            "view_mode": "list",
            "view_id": view.id,
            "target": "self",
        }

    def lock_inventory_count(self):
        self.is_lock = True

    def unlock_inventory_count(self):
        self.is_lock = False

    def _product_of_stock_inventory_category(self):
        domain = [
            ("type", "=", "product"),
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ]
        for rec in self:
            if rec.env.context.get("is_inventory_count"):
                product = self.env["product.product"].search(
                    [("categ_id", "=", rec.stock_inventory_category.id)]
                )
                if product:
                    domain.append(("id", "in", product.ids))
        return domain

    def action_view_count_stock_move_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.stock_move_line_action"
        )
        # Define domains and context
        move_domain = [
            ("location_dest_id.usage", "in", ["internal", "transit", "customer"]),
            ("company_id", "=", self.company_id.id),
        ]
        domain_loc = []
        if self.location_ids:
            domain_loc = [
                ("id", "child_of", self.location_ids.ids),
                ("company_id", "=", self.company_id.id),
            ]
        else:
            domain_loc = [
                ("company_id", "=", self.company_id.id),
                ("usage", "in", ["internal", "transit", "customer"]),
            ]
        if self.warehouse_id:
            domain_loc.append(("warehouse_id", "=", self.warehouse_id.id))
        locations_ids = [
            l["id"] for l in self.env["stock.location"].search_read(domain_loc, ["id"])
        ]
        if locations_ids:
            move_domain = expression.AND(
                [
                    move_domain,
                    [
                        "|",
                        ("location_id", "in", locations_ids),
                        ("location_dest_id", "in", locations_ids),
                    ],
                ]
            )
        product_ids = self._get_product_domain(is_start_inventory=True)
        if self.product_ids:
            move_domain = expression.AND(
                [move_domain, [("product_id", "in", self.product_ids.ids)]]
            )
        else:
            move_domain = expression.AND([move_domain, product_ids])
        if self.from_date_range:
            move_domain = expression.AND(
                [move_domain, [("date", ">=", self.from_date_range)]]
            )
        if self.to_date_range:
            move_domain = expression.AND(
                [move_domain, [("date", "<=", self.to_date_range)]]
            )
        action["domain"] = move_domain
        return action

    @api.onchange("warehouse_id", "stock_inventory_category")
    def _onchange_domain_product_id(self):
        """
        Domain prepare for Product
        """
        domain = []
        if self.env.context.get("is_inventory_count"):
            domain = self._get_product_domain(is_start_inventory=False)
        domain = expression.AND(
            [
                domain,
                [
                    ("type", "=", "product"),
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", self.env.company.id),
                ],
            ]
        )
        return {"domain": {"product_ids": domain}}

    def _get_product_domain(self, is_start_inventory=False):
        product_domain = [
            ("active", "in", [False, True]),
            "|",
            ("company_id", "!=", False),
            ("company_id", "=", self.company_id.id),
        ]
        domain = []
        if self.warehouse_id:
            product_ids = self.env["product.product"].search(product_domain)
            if product_ids and is_start_inventory:
                domain.append(("product_id", "in", product_ids.ids))
            elif product_ids:
                domain.append(("id", "in", product_ids.ids))
        if self.stock_inventory_category:
            product = self.env["product.product"].search(
                [("categ_id", "=", self.stock_inventory_category.id)]
            )
            if product and is_start_inventory:
                domain.append(("product_id", "in", product.ids))
            elif product:
                domain.append(("id", "in", product.ids))
        return domain

    @api.model
    def default_get(self, fields):
        is_inventory_count = self.env.context.get("is_inventory_count")
        vals = super(Inventory, self).default_get(fields)
        vals["is_inventory_count"] = is_inventory_count
        return vals

    def _get_quantities(self):
        """Return quantities group by product_id, location_id, lot_id, package_id and owner_id

        :return: a dict with keys as tuple of group by and quantity as value
        :rtype: dict
        """
        self.ensure_one()

        # Define domains and context
        domain = [
            ("location_id.usage", "in", ["internal", "transit", "customer"]),
            ("company_id", "=", self.company_id.id),
        ]
        move_domain = [
            ("location_dest_id.usage", "in", ["internal", "transit", "customer"]),
            ("company_id", "=", self.company_id.id),
        ]
        if self.location_ids:
            domain_loc = [
                ("id", "child_of", self.location_ids.ids),
                ("company_id", "=", self.company_id.id),
            ]
        else:
            domain_loc = [
                ("company_id", "=", self.company_id.id),
                ("usage", "in", ["internal", "transit", "customer"]),
            ]
        if self.warehouse_id:
            domain_loc.append(("warehouse_id", "=", self.warehouse_id.id))
        locations_ids = [
            l["id"] for l in self.env["stock.location"].search_read(domain_loc, ["id"])
        ]
        if locations_ids:
            domain.append(("location_id", "in", locations_ids))
            move_domain = expression.AND(
                [
                    move_domain,
                    [
                        "|",
                        ("location_id", "in", locations_ids),
                        ("location_dest_id", "in", locations_ids),
                    ],
                ]
            )
        product_ids = self._get_product_domain(is_start_inventory=True)
        if self.product_ids:
            domain = expression.AND(
                [domain, [("product_id", "in", self.product_ids.ids)]]
            )
            move_domain = expression.AND(
                [move_domain, [("product_id", "in", self.product_ids.ids)]]
            )
        else:
            domain = expression.AND([domain, product_ids])
            move_domain = expression.AND([move_domain, product_ids])
        if self.from_date_range:
            domain = expression.AND([domain, [("in_date", ">=", self.from_date_range)]])
            move_domain = expression.AND(
                [move_domain, [("date", ">=", self.from_date_range)]]
            )
        if self.to_date_range:
            domain = expression.AND([domain, [("in_date", "<=", self.to_date_range)]])
            move_domain = expression.AND(
                [move_domain, [("date", "<=", self.to_date_range)]]
            )
        fields = [
            "product_id",
            "location_id",
            "lot_id",
            "package_id",
            "owner_id",
            "use_expiration_date",
            "quantity:sum",
        ]
        group_by = ["product_id", "location_id", "lot_id", "package_id", "owner_id"]
        move_ids = self.env["stock.move.line"].search(move_domain)
        if move_ids:
            locations_ids = move_ids.location_dest_id + move_ids.location_id
            locations_ids = locations_ids.filtered(
                lambda l: l.usage == "internal"
                and l.name not in ["Staging", "Shipping Staging", "Input", "Output"]
            )
            domain = [
                ("product_id", "in", move_ids.product_id.ids),
                ("location_id", "in", locations_ids.ids),
            ]
        quants = self.env["stock.quant"].read_group(
            domain, fields, group_by, lazy=False
        )
        return [
            {
                (
                    quant["product_id"] and quant["product_id"][0] or False,
                    quant["location_id"] and quant["location_id"][0] or False,
                    quant["lot_id"] and quant["lot_id"][0] or False,
                    quant["package_id"] and quant["package_id"][0] or False,
                    quant["owner_id"] and quant["owner_id"][0] or False,
                ): quant["quantity"]
                for quant in quants
            },
            move_ids,
        ]

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.env.user.has_group("stock.group_stock_multi_locations"):
            warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.company_id.id)], limit=1)
            if warehouse:
                self.location_ids = warehouse.lot_stock_id

    def copy_data(self, default=None):
        name = _("%s (copy)") % (self.name)
        default = dict(default or {}, name=name)
        return super(Inventory, self).copy_data(default)

    def unlink(self):
        for inventory in self:
            if inventory.state not in ("draft", "cancel") and not self.env.context.get(
                MODULE_UNINSTALL_FLAG, False
            ):
                raise UserError(
                    _(
                        "You can only delete a draft inventory adjustment. If the inventory adjustment is not done, you can cancel it."
                    )
                )
        return super(Inventory, self).unlink()

    def action_validate(self):
        self.state = "done"
        self.end_date = fields.Datetime.now()
        self.user_id = self.env.uid
        return True

    def action_check(self):
        """Checks the inventory and computes the stock move to do"""
        # tde todo: clean after _generate_moves
        for inventory in self.filtered(lambda x: x.state not in ("done", "cancel")):
            # first remove the existing stock moves linked to this inventory
            inventory.with_context(prefetch_fields=False).mapped("move_ids").unlink()
            inventory.line_ids._generate_moves()

    def action_cancel_draft(self):
        """Cancel the inventory"""
        self.line_ids = False
        self.inventory_line_ids.unlink()
        self.write({"state": "draft"})

    def action_start(self):
        self.ensure_one()
        self._action_start()
        self._check_company()
        res = self.with_context(start_inventory=True).action_open_inventory_lines()
        return res

    def _action_start(self):
        """Confirms the Inventory Adjustment and generates its inventory lines
        if its state is draft and don't have already inventory lines (can happen
        with demo data or tests).
        """
        for inventory in self:
            if inventory.state != "draft":
                continue
            vals = {
                "state": "confirm",
                "date": fields.Datetime.now(),
                "start_date": fields.Datetime.now(),
                "user_id": self.env.user.id,
            }
            inventory.write(vals)

    def action_open_inventory_lines(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "list",
            "name": _("Inventory Lines"),
            "res_model": "stock.inventory.line",
        }
        context = {
            "is_inventory_count": True,
            "default_is_editable": True,
            "default_company_id": self.company_id.id,
        }

        action["view_id"] = self.env.ref(
            "stock_inventory_count_tus.stock_inventory_line_list"
        ).id
        if not self.inventory_line_ids:
            self.env["stock.inventory.line"].create(self._get_inventory_lines_values())
        action["context"] = context
        action["domain"] = [("inventory_id", "=", self.id)]
        return action

    def action_print(self):
        return self.env.ref("stock.action_report_inventory").report_action(self)

    def _get_exhausted_inventory_lines_vals(self, non_exhausted_set):
        """Return the values of the inventory lines to create if the user
        wants to include exhausted products. Exhausted products are products
        without quantities or quantity equal to 0.

        :param non_exhausted_set: set of tuple (product_id, location_id) of non-exhausted product-location
        :return: a list containing the `stock.quant` values to create
        :rtype: list
        """
        self.ensure_one()
        if self.product_ids:
            product_ids = self.product_ids.ids
        else:
            product_ids = self.env["product.product"].search_read(
                [
                    "|",
                    ("company_id", "=", self.company_id.id),
                    ("company_id", "=", False),
                    ("type", "=", "product"),
                    ("active", "=", True),
                ],
                ["id"],
            )
            product_ids = [p["id"] for p in product_ids]

        if self.location_ids:
            location_ids = self.location_ids.ids
        else:
            location_ids = (
                self.env["stock.warehouse"]
                .search([("company_id", "=", self.company_id.id)])
                .lot_stock_id.ids
            )

        vals = []
        for product_id in product_ids:
            p_id = self.env["product.product"].browse(product_id)
            for location_id in location_ids:
                if (product_id, location_id) not in non_exhausted_set:
                    vals.append(
                        {
                            "inventory_id": self.id,
                            "product_id": product_id,
                            "product_uom_id": p_id
                            and p_id.uom_id
                            and p_id.uom_id.id
                            or False,
                            "location_id": location_id,
                            "theoretical_qty": 0,
                        }
                    )
        return vals

    def _get_inventory_lines_values(self):
        """Return the values of the inventory lines to create for this inventory.

        :return: a list containing the `stock.quant` values to create
        :rtype: list
        """
        self.ensure_one()
        get_quantities = self._get_quantities()
        quants_groups = get_quantities[0]
        move_ids = get_quantities[1]
        vals = []
        product_ids = OrderedSet()
        for (
            product_id,
            location_id,
            lot_id,
            package_id,
            owner_id,
        ), quantity in quants_groups.items():
            temp_lines = move_ids.filtered(lambda m: m.product_id.id == product_id)
            temp_location_ids = temp_lines.mapped("location_id") + temp_lines.mapped(
                "location_dest_id"
            )
            if location_id in temp_location_ids.ids:
                line_values = {
                    "inventory_id": self.id,
                    "qty_done": 0
                    if self.prefill_counted_quantity == "zero"
                    else quantity,
                    "theoretical_qty": quantity,
                    "prod_lot_id": lot_id,
                    "partner_id": owner_id,
                    "product_id": product_id,
                    "location_id": location_id,
                    "package_id": package_id,
                }
                product_ids.add(product_id)
                vals.append(line_values)
        product_id_to_product = dict(
            zip(product_ids, self.env["product.product"].browse(product_ids))
        )
        for val in vals:
            val["product_uom_id"] = product_id_to_product[
                val["product_id"]
            ].product_tmpl_id.uom_id.id
        if self.exhausted:
            vals += self._get_exhausted_inventory_lines_vals(
                {(l["product_id"], l["location_id"]) for l in vals}
            )
        return vals

    def _get_stock_inventory_lines_values(self, move_ids):
        """Return the values of the inventory lines to create for this inventory.

        :return: a list containing the `stock.inventory.line` values to create
        :rtype: list
        """
        self.ensure_one()
        vals = []
        product_ids = OrderedSet()
        prefill_counted_quantity = self.prefill_counted_quantity != "zero"
        for move in move_ids:
            existing_updated = False
            for val in vals:
                if move.product_id.id == val.get(
                    "product_id"
                ) and move.location_dest_id.id == val.get("location_dest_id"):
                    val["qty_done"] += prefill_counted_quantity and move.qty_done or 0
                    val["theoretical_qty"] += move.qty_done or 0
                    existing_updated = True
                    break
            if existing_updated:
                continue
            line_values = {
                "inventory_id": self.id,
                "qty_done": prefill_counted_quantity and move.qty_done or 0,
                "theoretical_qty": move.qty_done,
                "prod_lot_id": move.lot_id.id,
                "product_id": move.product_id.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "package_id": move.package_id.id,
            }
            product_ids.add(move.product_id.id)
            vals.append(line_values)
        product_id_to_product = dict(
            zip(product_ids, self.env["product.product"].browse(product_ids))
        )
        for val in vals:
            val["product_uom_id"] = product_id_to_product[
                val["product_id"]
            ].product_tmpl_id.uom_id.id
        if self.exhausted:
            vals += self._get_exhausted_inventory_lines_vals(
                {(l["product_id"], l["location_dest_id"]) for l in vals}
            )
        return vals