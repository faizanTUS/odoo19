# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    allowed_user_ids = fields.Many2many(
        "res.users",
        "res_users_account_journal_rel",
        "journal_id",
        "user_id",
        string="Allowed Users",
        help="Users who are allowed to see and use this journal. "
             "If empty for a user, they will not see this journal.",
        groups="account.group_account_manager",
    )
