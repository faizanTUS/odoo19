# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    discussion_enabled = fields.Boolean(
        string="Enable discussion",
        compute="_compute_discussion_enabled",
        inverse="_inverse_discussion_enabled",
        help="Allows this user to open Discuss, use the messaging menu in the top bar, and chat pop-ups.",
    )

    @api.depends("group_ids")
    def _compute_discussion_enabled(self):
        group = self.env.ref(
            "hide_user_discussion.group_discussion_enabled", raise_if_not_found=False
        )
        for user in self:
            user.discussion_enabled = bool(group and group in user.group_ids)

    def _inverse_discussion_enabled(self):
        group = self.env.ref("hide_user_discussion.group_discussion_enabled")
        for user in self:
            if user.discussion_enabled:
                user.group_ids = user.group_ids | group
            else:
                user.group_ids = user.group_ids - group
