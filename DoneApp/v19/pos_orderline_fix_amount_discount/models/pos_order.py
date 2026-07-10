# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super(PosOrder, self)._get_fields_for_order_line()
        fields.extend(['discount_amount'])
        return fields

    @api.model
    # def _get_invoice_lines_values(self, line_values, pos_order_line): 
    def _get_invoice_lines_values(self, line_values, pos_line, move_type):
        res = super()._get_invoice_lines_values(line_values, pos_line,move_type)
        res.update({'discount_amount': line_values['record'].discount_amount if line_values['record'] else 0})
        return res
