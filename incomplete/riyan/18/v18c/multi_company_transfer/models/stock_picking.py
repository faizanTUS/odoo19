# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        res = super()._action_done()
        self._multi_company_transfer_check_done()
        return res

    def _multi_company_transfer_check_done(self):
        """When a picking linked to a multi-company transfer is set to done,
        check if both pickings are done and if so, mark the transfer as done.
        """
        for picking in self:
            transfer_out = self.env['multi.company.transfer'].search([
                ('outgoing_picking_id', '=', picking.id),
            ], limit=1)
            transfer_in = self.env['multi.company.transfer'].search([
                ('incoming_picking_id', '=', picking.id),
            ], limit=1)
            for transfer in (transfer_out | transfer_in):
                transfer._transfer_done()
