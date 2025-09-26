# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    new_currency_rate = fields.Float(string="New Currency Rate", digits=(16, 4))

    allow_custom_currency_rate = fields.Boolean(
        related="company_id.allow_custom_currency_rate"
    )

    def button_validate(self):
        """
        Passing currency rate context while validating the transfer
        @return: super call
        """
        if all(self.mapped("allow_custom_currency_rate")):
            if not self.env.context.get("button_validate_picking_ids"):
                self = self.with_context(button_validate_picking_ids=self.ids)
            res = self._pre_action_done_hook()
            if res is not True:
                return res
            for rec in self:
                super(
                    StockPicking,
                    rec.with_context(new_currency_rate=rec.new_currency_rate),
                ).button_validate()
            if self.env.user.has_group("stock.group_reception_report"):
                pickings_show_report = self.filtered(
                    lambda p: p.picking_type_id.auto_show_reception_report
                )
                lines = pickings_show_report.move_ids.filtered(
                    lambda m: m.product_id.type == "product"
                    and m.state != "cancel"
                    and m.quantity_done
                    and not m.move_dest_ids
                )
                if lines:
                    # don't show reception report if all already assigned/nothing to assign
                    wh_location_ids = self.env["stock.location"]._search(
                        [
                            (
                                "id",
                                "child_of",
                                pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids,
                            ),
                            ("usage", "!=", "supplier"),
                        ]
                    )
                    if self.env["stock.move"].search(
                        [
                            (
                                "state",
                                "in",
                                [
                                    "confirmed",
                                    "partially_available",
                                    "waiting",
                                    "assigned",
                                ],
                            ),
                            ("product_qty", ">", 0),
                            ("location_id", "in", wh_location_ids),
                            ("move_orig_ids", "=", False),
                            ("picking_id", "not in", pickings_show_report.ids),
                            ("product_id", "in", lines.product_id.ids),
                        ],
                        limit=1,
                    ):
                        action = pickings_show_report.action_view_reception_report()
                        action["context"] = {
                            "default_picking_ids": pickings_show_report.ids
                        }
                        return action
            return True
        return super(StockPicking, self).button_validate()

    def write(self, vals):
        """
        Passing currency rate context while saving the transfer
        @param vals: updated value list
        @return: True
        """
        for rec in self:
            if rec.allow_custom_currency_rate:
                rec = rec.with_context(new_currency_rate=rec.new_currency_rate)
            super(StockPicking, rec).write(vals)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """
        Passing currency rate context while creating new transfer
        @param vals_list: creating record values
        @return: super call result
        """
        new_currency_rate = self._context.get("new_currency_rate") or 0
        if type(vals_list) == list:
            for val in vals_list:
                val["new_currency_rate"] = new_currency_rate
        else:
            vals_list["new_currency_rate"] = new_currency_rate
        result = super(
            StockPicking, self.with_context(new_currency_rate=new_currency_rate)
        ).create(vals_list)
        return result
