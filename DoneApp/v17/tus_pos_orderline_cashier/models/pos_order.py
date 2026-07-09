from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    allow_orderline_user = fields.Boolean(related='session_id.config_id.allow_orderline_user')


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    cashier_id = fields.Many2one('hr.employee', string='Cashier',
                                     help='Cashier who selected in pos')


    def _order_line_fields(self, line, session_id=None):
        result = super()._order_line_fields(line, session_id)
        cashier_name = self.env["hr.employee"].search([("name",'=',line[2].get('orderline_cashier'))])
        if result and cashier_name:
            result[2]['cashier_id'] = cashier_name.id
        return result