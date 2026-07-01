from odoo import exceptions, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_cancel(self):
        quant_obj = self.env["stock.quant"]
        move_obj = self.env["account.move"]
        for pick in self:
            if self.env.context.get("Flag", False) and pick.state == "done":
                account_moves = pick.move_line_ids
                for move_line in account_moves:
                    if move_line.state == "cancel":
                        continue
                    landed_cost_rec = []
                    try:
                        landed_cost_rec = self.env["stock.landed.cost"].search(
                            [("picking_ids", "=", pick.id), ("state", "=", "done")]
                        )
                    except:
                        pass

                    if landed_cost_rec:
                        raise exceptions.Warning(
                            "This Delivery is set in landed cost record %s you need to delete it fisrt then you can cancel this Delivery"
                            % ",".join(landed_cost_rec.mapped("name"))
                        )

                    if (
                        move_line.state == "done"
                        and move_line.product_id.type == "product"
                    ):
                        quantity = move_line.product_uom_id._compute_quantity(
                            move_line.qty_done, move_line.product_id.uom_id
                        )
                        quant_obj._update_available_quantity(
                            move_line.product_id,
                            move_line.location_id,
                            quantity,
                            move_line.lot_id,
                        )
                        quant_obj._update_available_quantity(
                            move_line.product_id,
                            move_line.location_dest_id,
                            quantity * -1,
                            move_line.lot_id,
                        )
                    if (
                        move_line.move_id.procure_method == "make_to_order"
                        and not move_line.move_id.move_orig_ids
                    ):
                        move_line.state = "waiting"
                    elif move_line.move_id.move_orig_ids and not all(
                        orig.state in ("done", "cancel")
                        for orig in move_line.move_id.move_orig_ids
                    ):
                        move_line.state = "waiting"
                    else:
                        move_line.state = "confirmed"
                    siblings_states = (
                        move_line.move_id.move_dest_ids.mapped("move_orig_ids")
                        - move_line.move_id
                    ).mapped("state")
                    if move_line.move_id.propagate_cancel:
                        if all(state == "cancel" for state in siblings_states):
                            move_line.move_dest_ids._action_cancel()
                    else:
                        if all(
                            state in ("done", "cancel") for state in siblings_states
                        ):
                            move_line.move_id.move_dest_ids.write(
                                {"procure_method": "make_to_stock"}
                            )
                        move_line.move_id.move_dest_ids.write(
                            {"move_orig_ids": [(3, move_line.id, 0)]}
                        )
                    move_line.move_id.write(
                        {"state": "cancel", "move_orig_ids": [(5, 0, 0)]}
                    )
                    acnt_moves = move_obj.search([("stock_move_id", "=", move_line.id)])
                    valuation = move_line.move_id.stock_valuation_layer_ids
                    valuation and valuation.sudo().unlink()
                    if acnt_moves:
                        for account_move in acnt_moves:
                            account_move.with_context(
                                {"force_delete": True}
                            ).line_ids.sudo().remove_move_reconcile()
                            account_move.with_context(
                                {"force_delete": True}
                            ).button_cancel()
                            account_move.with_context({"force_delete": True}).unlink()
        res = super(StockPicking, self).action_cancel()
        return res
