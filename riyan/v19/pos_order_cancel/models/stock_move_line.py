# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done_or_cancel(self):
        if self.env.context.get('pos_order_cancel_done_picking'):
            return
        return super()._unlink_except_done_or_cancel()

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_force_cancel(self):
        """Force cancel posted invoice - unreconcile, ignore hash, set cancel state"""
        self.ensure_one()
        if self.state == 'cancel':
            return True

        # Unreconcile all lines (breaks payment link)
        self.line_ids.remove_move_reconcile()

        # Force write state (bypasses most checks)
        self.with_context(no_check_hash=True).sudo().write({
            'state': 'cancel',
            'auto_post': 'no',
        })

        # Optional: log it
        self.message_post(body="Forced cancel via POS Cancel Wizard - hash integrity may be broken")

        return True

    def button_draft(self):
        if self.sudo().pos_order_ids.filtered(lambda o: o.session_id.state != 'closed'):
            self.env.user._bus_send("simple_notification", {
                'type': 'danger',
                'message': (
                    "The invoice has been cancelled successfully."
                ),
                'sticky': True,
            })
            return False
        return super().button_draft()