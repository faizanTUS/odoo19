# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import _, api, models,fields
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"
    journal_id = fields.Many2one(
        "account.journal",
        domain="[('id', 'in', allowed_journal_ids)]",
    )
    allowed_journal_ids = fields.Many2many(
        "account.journal",
        compute="_compute_allowed_journal_ids",
        string="Allowed Journals",
        readonly=True,
    )

    @api.depends_context("uid", "allowed_company_ids")
    def _compute_allowed_journal_ids(self):
        user = self.env.user
        restricted = user.has_group("user_account_journal_restriction.group_journal_restricted_user")
        allowed_journals = user.allowed_journal_ids if restricted else self.env["account.journal"].search([])
        for move in self:
            move.allowed_journal_ids = allowed_journals

    @api.model
    def _check_user_journal_access(self, vals_list):
        """Hard-enforce that the current user can only use allowed journals.
        Record rules limit visibility, still we validate on create/write.
        """
        user = self.env.user
        # Superuser or no restriction configured. Do not block.
        if user._is_admin():
            return

        # Only enforce for users explicitly marked as restricted.
        if not user.has_group("user_account_journal_restriction.group_journal_restricted_user"):
            return

        allowed_journals = user.allowed_journal_ids
        # Restricted users must have journals configured.
        if not allowed_journals:
            journal_ids = [
                vals.get("journal_id")
                for vals in vals_list
                if vals.get("journal_id")
            ]
            if journal_ids:
                raise UserError(
                    _(
                        "You do not have any allowed journals configured. "
                        "Please contact your Accounting Manager."
                    )
                )
            return

        allowed_ids = set(allowed_journals.ids)
        invalid_journals = []

        for vals in vals_list:
            j_id = vals.get("journal_id")
            if j_id and j_id not in allowed_ids:
                invalid_journals.append(j_id)

        if invalid_journals:
            journals = self.env["account.journal"].browse(list(set(invalid_journals)))
            raise UserError(
                _(
                    "You are not allowed to use the following journals. "
                    "Please contact your Accounting Manager.\n%s"
                )
                % ", ".join(journals.mapped("name"))
            )

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        self._check_user_journal_access(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        # Build a vals_list equivalent for validation.
        vals_list = []
        for move in self:
            move_vals = {}
            if "journal_id" in vals:
                move_vals["journal_id"] = vals["journal_id"]
            vals_list.append(move_vals)
        if any(v.get("journal_id") for v in vals_list):
            self._check_user_journal_access(vals_list)
        return super().write(vals)
