# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        info = super().session_info()
        if not request.session.uid:
            return info
        svc = self.env["advanced.access.service"]
        rules = svc._rules_payload_json()
        info["aac_rules_json"] = rules
        return info

    @classmethod
    def _handle_debug(cls):
        super()._handle_debug()
        if not request.session.uid:
            return
        try:
            env = request.env
            # Routes with auth="none" (e.g. /odoo) only set request.env.uid inside the controller,
            # after _pre_dispatch. _rules_payload_json uses env.uid and would return empty rules here,
            # so debug mode would never be cleared for the web client bootstrap.
            if not env.uid:
                env = env(user=request.session.uid)
        except Exception:
            return
        if not env["base"]._aac_should_enforce():
            return
        rules = env["advanced.access.service"]._rules_dict()
        if rules and rules.get("disable_debug"):
            request.session.debug = ""
