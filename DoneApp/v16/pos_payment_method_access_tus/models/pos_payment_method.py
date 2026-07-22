# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models
from odoo.osv.expression import AND


class PosPaymentMethod(models.Model):
    """
    Pos Payment Method
    """
    _inherit = "pos.payment.method"

    user_ids = fields.Many2many("res.users", string="Allowed Users")


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_pos_payment_method(self):
        result = super(PosSession, self)._loader_params_pos_payment_method()
        method_list = []
        pos_payment_method_ids = (
            self.env["pos.payment.method"]
            .sudo()
            .search([("user_ids", "in", self.env.user.ids)])
        )
        not_assign_user = (
            self.env["pos.payment.method"]
            .sudo()
            .search([])
            .filtered(lambda x: not x.user_ids)
        )
        if not_assign_user:
            method_list += not_assign_user.ids
        if pos_payment_method_ids:
            method_list += pos_payment_method_ids.ids
        result["search_params"]["domain"] = AND(
            [result["search_params"]["domain"], [("id", "in", method_list)]]
        )
        return result
