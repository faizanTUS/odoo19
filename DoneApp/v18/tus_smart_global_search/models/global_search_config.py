# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    global_search_model_ids = fields.Many2many(
        comodel_name="ir.model",
        relation="res_users_global_search_model_rel",
        column1="user_id",
        column2="model_id",
        string="Global Search Models",
        domain=[
            "|",
            ("is_mail_thread", "=", True),
            ("is_mail_activity", "=", True),
        ],
        help="Models this user can search in the global search. "
             "If none are selected, a built-in default set (contacts, common documents, …) is used.",
    )