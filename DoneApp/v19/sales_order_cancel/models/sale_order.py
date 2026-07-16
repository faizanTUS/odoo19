# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models


class SaleOrderCancel(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        for wizard in self:
            for inv in wizard.invoice_ids.filtered(
                lambda inv: inv.state == "posted"
            ):
                inv._reverse_moves(cancel=True)
            wizard.picking_ids.with_context({"Flag": True}).action_cancel()
            return super(SaleOrderCancel, self).action_cancel()
