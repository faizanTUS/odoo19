# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super().session_info()
        uid = res.get("uid")
        if uid:
            res["discussion_enabled"] = self.env.user.has_group(
                "hide_user_discussion.group_discussion_enabled"
            )
        else:
            res["discussion_enabled"] = False
        return res
