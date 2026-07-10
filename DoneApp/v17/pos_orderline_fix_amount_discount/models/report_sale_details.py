# -*- coding: utf-8 -*-

from odoo import models, api


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        res = super().get_sale_details(date_start=date_start, date_stop=date_stop, config_ids=config_ids, session_ids=session_ids)
        sessions = []
        discount_number = 0
        if config_ids:
            configs = self.env['pos.config'].search([('id', 'in', config_ids)])
            if session_ids:
                sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
            else:
                sessions = self.env['pos.session'].search(
                    [('config_id', 'in', configs.ids), ('start_at', '>=', date_start), ('stop_at', '<=', date_stop)])
        else:
            sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
        for session in sessions:
            discount_number += len(session.order_ids.filtered(lambda o: o.lines.filtered(lambda l: l.discount > 0) or o.lines.filtered(lambda l: l.discount_amount > 0)))
        res['discount_number'] = discount_number
        return res

