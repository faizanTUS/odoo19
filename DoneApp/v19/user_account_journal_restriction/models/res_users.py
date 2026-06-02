# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    allowed_journal_ids = fields.Many2many(
        "account.journal",
        "res_users_account_journal_rel",  # shared relation table
        "user_id",
        "journal_id",
        string="Allowed Journals",
        help="If set, this user will only be able to see and use these journals.",
        groups="account.group_account_manager",
    )

    @api.model
    def create(self, vals):
        # Standard create, but you can plug audits here if needed
        return super().create(vals)

    def write(self, vals):
        # Safety hook, e.g. you could log changes to allowed_journal_ids for audit
        return super().write(vals)
