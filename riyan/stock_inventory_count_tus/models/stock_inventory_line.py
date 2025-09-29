# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare
from odoo.tools.misc import OrderedSet
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.tools import float_compare

from odoo import SUPERUSER_ID

_logger = logging.getLogger("Inventory Counting")


class InventoryLine(models.Model):
    """A line of inventory"""

    _name = "stock.inventory.line"
    _description = "Inventory Line"
    _order = "product_id, inventory_id, prod_lot_id"

    is_editable = fields.Boolean(help="Technical field to restrict editing.")
    inventory_id = fields.Many2one(
        "stock.inventory",
        "Inventory",
        check_company=True,
        index=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", "Owner", check_company=True)
    product_id = fields.Many2one(
        "product.product",
        "Product",
        check_company=True,
        domain=lambda self: self._domain_product_id(),
        index=True,
        required=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom", "Product Unit of Measure", required=True, readonly=True
    )
    qty_done = fields.Float(
        "Counted Quantity",
        digits="Product Unit of Measure",
        default=0,
    )
    categ_id = fields.Many2one(related="product_id.categ_id", store=True)
    location_id = fields.Many2one(
        "stock.location", "Location", check_company=True, index=True, required=True
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        check_company=True,
        domain=lambda self: self._domain_location_id(),
        index=True,
        required=False,
    )
    # package_id = fields.Many2one(
    #     "stock.quant.package", "Pack", index=True, check_company=True
    # )
    package_id = fields.Many2one(
        "stock.package", "Pack", index=True, check_company=True
    )
    prod_lot_id = fields.Many2one(
        "stock.lot",
        "Lot/Serial Number",
        check_company=True,
        domain="[('product_id','=',product_id), ('company_id', '=', company_id)]",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        related="inventory_id.company_id",
        index=True,
        readonly=True,
        store=True,
    )
    state = fields.Selection(string="Status", related="inventory_id.state")
    theoretical_qty = fields.Float(
        "Theoretical Quantity", digits="Product Unit of Measure", readonly=True
    )
    difference_qty = fields.Float(
        "Difference",
        compute="_compute_difference",
        help="Indicates the gap between the product's theoretical quantity and its newest quantity.",
        readonly=True,
        digits="Product Unit of Measure",
        search="_search_difference_qty",
    )
    inventory_date = fields.Datetime(
        "Inventory Date",
        readonly=True,
        default=fields.Datetime.now,
        help="Last date at which the On Hand Quantity has been computed.",
    )
    outdated = fields.Boolean(
        string="Quantity outdated",
        compute="_compute_outdated",
        search="_search_outdated",
    )
    product_tracking = fields.Selection(
        string="Tracking", related="product_id.tracking", readonly=True
    )
    expiration_date = fields.Datetime(
        string="Expiration Date",
        related="prod_lot_id.expiration_date",
        store=True,
        help="This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.",
    )

    @api.model
    def _domain_location_id(self):
        if self.env.context.get("active_model") == "stock.inventory":
            inventory = self.env["stock.inventory"].browse(
                self.env.context.get("active_id")
            )
            if inventory.exists() and inventory.location_ids:
                return (
                        "[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit']), ('id', 'child_of', %s)]"
                        % inventory.location_ids.ids
                )
        return "[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]"

    @api.model
    def _domain_product_id(self):
        if self.env.context.get("active_model") == "stock.inventory":
            inventory = self.env["stock.inventory"].browse(
                self.env.context.get("active_id")
            )
            if inventory.exists() and len(inventory.product_ids) > 1:
                return (
                        "[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id), ('id', 'in', %s)]"
                        % inventory.product_ids.ids
                )
        return "[('type', '=', 'product'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]"

    def _search_difference_qty(self, operator, value):
        if not self._context.get("active_ids"):
            raise NotImplementedError(
                _(
                    "Unsupported search on %s outside of an Inventory Adjustment",
                    "difference_qty",
                )
            )
        value = abs(float(value or 0))
        lines = self.search([("inventory_id", "in", self._context.get("active_ids"))])
        if operator == "=":
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) == value)
        elif operator == "!=":
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) != value)
        elif operator == ">":
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) > value)
        elif operator == "<":
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) < value)
        elif operator == ">=":
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) >= value)
        elif operator == "<=":
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) <= value)
        else:
            line_ids = lines.filtered(lambda l: abs(l.difference_qty) == value)
        return [("id", "in", line_ids.ids)]

    @api.depends("qty_done", "theoretical_qty")
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.qty_done - line.theoretical_qty

    @api.depends(
        "inventory_date",
        "product_id.stock_move_ids",
        "theoretical_qty",
        "product_uom_id.rounding",
    )
    def _compute_outdated(self):
        quants_by_inventory = {
            inventory: inventory._get_quantities()[0] for inventory in self.inventory_id
        }
        for line in self:
            quants = quants_by_inventory[line.inventory_id]
            if line.state == "done" or not line.id:
                line.outdated = False
                continue
            qty = quants.get(
                (
                    line.product_id.id,
                    line.location_dest_id.id,
                    line.prod_lot_id.id,
                    line.package_id.id,
                    line.partner_id.id,
                ),
                0,
            )
            if (
                    float_compare(
                        qty,
                        line.theoretical_qty,
                        precision_rounding=line.product_uom_id.rounding,
                    )
                    != 0
            ):
                line.outdated = True
            else:
                line.outdated = False

    def _search_outdated(self, operator, value):
        if operator != "=":
            if operator == "!=" and isinstance(value, bool):
                value = not value
            else:
                raise NotImplementedError()
        if not self.env.context.get("default_inventory_id"):
            raise NotImplementedError(
                _(
                    "Unsupported search on %s outside of an Inventory Adjustment",
                    "outdated",
                )
            )
        lines = self.search(
            [("inventory_id", "=", self.env.context.get("default_inventory_id"))]
        )
        line_ids = lines.filtered(lambda line: line.outdated == value).ids
        return [("id", "in", line_ids)]

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, package_id=False, package_dest_id=False):
        """ Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param package_id: `stock.quant.package`
        :param package_dest_id: `stock.quant.package`
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        self.ensure_one()

        if self.env.context.get('inventory_name'):
            name = self.env.context.get('inventory_name')
        elif fields.Float.is_zero(qty, precision_rounding=self.product_uom_id.rounding):
            name = _('Product Quantity Confirmed')
        else:
            name = _('Product Quantity Updated')
        if self.env.user and self.env.user.id != SUPERUSER_ID:
            name += f'({self.env.user.display_name})'

        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'restrict_partner_id': self.partner_id.id,
            'is_inventory': True,
            'picked': True,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'quantity': qty,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': self.prod_lot_id.id,
                'package_id': package_id.id if package_id else False,
                'result_package_id': package_dest_id.id if package_dest_id else False,
                'owner_id': self.partner_id.id,
            })]
        }

    def _apply_inventory(self):
        move_vals = []
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise UserError(_('Only a stock manager can validate an inventory adjustment.'))
        for line in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(line.difference_qty, 0, precision_rounding=line.product_uom_id.rounding) > 0:
                move_vals.append(
                    line._get_inventory_move_values(line.difference_qty,
                                                    line.product_id.with_company(
                                                        line.company_id).property_stock_inventory,
                                                    line.location_id, package_dest_id=line.package_id))
            else:
                move_vals.append(
                    line._get_inventory_move_values(-line.difference_qty,
                                                    line.location_id,
                                                    line.product_id.with_company(
                                                        line.company_id).property_stock_inventory,
                                                    package_id=line.package_id))
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves._action_done()
        self.location_id.write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in self.mapped('location_id')}
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
            quant.theoretical_qty = quant.qty_done

    def action_apply_inventory(self):
        products_tracked_without_lot = []
        all_quant_ids = self.env['stock.quant']
        for line in self:
            rounding = line.product_uom_id.rounding
            rec_quant = self.env['stock.quant'].with_company(line.company_id).search(
                [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id),
                 ('lot_id', '=', line.prod_lot_id.id)])
            all_quant_ids += rec_quant
            if fields.Float.is_zero(line.difference_qty, precision_rounding=rounding) \
                    and fields.Float.is_zero(line.qty_done, precision_rounding=rounding) \
                    and fields.Float.is_zero(line.theoretical_qty, precision_rounding=rounding):
                continue
            if line.product_id.tracking in ['lot', 'serial'] and \
                    not line.prod_lot_id and line.qty_done != line.theoretical_qty and not line.theoretical_qty:
                products_tracked_without_lot.append(line.product_id.id)
        # for some reason if multi-record, env.context doesn't pass to wizards...
        ctx = dict(self.env.context or {})
        quants_outdated = all_quant_ids.filtered(lambda quant: quant.is_outdated)
        if quants_outdated:
            ctx['default_quant_ids'] = all_quant_ids.ids
            ctx['default_quant_to_fix_ids'] = quants_outdated and quants_outdated.ids or []
            return {
                'name': _('Conflict in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.inventory.conflict',
                'target': 'new',
                'context': ctx,
            }
        if products_tracked_without_lot:
            ctx['default_product_ids'] = products_tracked_without_lot
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'context': ctx,
            }
        self._apply_inventory()

    def action_set_counted_qty_to_onhand(self):
        self.qty_done = self.theoretical_qty
