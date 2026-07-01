# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    not_send_msgs_btn_in_chatter = fields.Many2many(
        "ir.model",
        "send_msgs_model_rel_user",
        "model_id",
        "send_msgs_id",
        "Hide Send Message Button",
    )
