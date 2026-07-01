from odoo import models


class SaleOrderCancel(models.TransientModel):
    _inherit = "sale.order.cancel"

    def action_cancel(self):
        for wizard in self:
            for inv in wizard.order_id.invoice_ids.filtered(
                lambda inv: inv.state == "posted"
            ):
                inv._reverse_moves(cancel=True)
            wizard.order_id.picking_ids.with_context({"Flag": True}).action_cancel()
            return super(SaleOrderCancel, self).action_cancel()
