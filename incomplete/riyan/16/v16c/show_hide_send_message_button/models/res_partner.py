# See LICENSE file for full copyright and licensing details.
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Check access of the record send message button based on model.
    def mail_partner_format(self, fields=None):
        res = super().mail_partner_format(fields=fields)
        for partner in self:
            res[partner].update(
                {
                    "not_send_msgs_btn_in_chatter": self.env["ir.model"].search_read(
                        [
                            (
                                "id",
                                "in",
                                (self.env.user.not_send_msgs_btn_in_chatter).ids,
                            )
                        ],
                        ["id", "name", "model"],
                    )
                    if self.env.user.not_send_msgs_btn_in_chatter
                    else []
                }
            )
        return res
