# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_done_or_cancel(self):
        if self.env.context.get('pos_order_cancel_done_picking'):
            return
        return super()._unlink_except_done_or_cancel()
