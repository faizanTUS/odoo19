# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models, api
from odoo.osv.expression import AND


class PosPaymentMethod(models.Model):
    """
    Pos Payment Method
    """
    _inherit = "pos.payment.method"

    user_ids = fields.Many2many("res.users", string="Allowed Users")


class PosPaymentMethodExt(models.Model):
    _inherit = "pos.payment.method"

    @api.model
    def _load_pos_data_domain(self, data, config):
        res = super(PosPaymentMethodExt, self)._load_pos_data_domain(data=data, config=config)
        method_list = []
        pos_payment_method_ids = self.sudo().search([("user_ids", "in", self.env.user.ids)])
        not_assign_user = self.env["pos.payment.method"].sudo().search([]).filtered(lambda x: not x.user_ids)
        if not_assign_user:
            method_list += not_assign_user.ids
        if pos_payment_method_ids:
            method_list += pos_payment_method_ids.ids
        res = AND([res, [("id", "in", method_list)]])
        return res
