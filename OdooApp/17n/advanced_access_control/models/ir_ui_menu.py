# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _load_menus_blacklist(self):
        ids = super()._load_menus_blacklist()
        ids = list(ids) if ids else []
        if not self.env["base"]._aac_should_enforce():
            return list(dict.fromkeys(ids))
        svc = self.env["advanced.access.service"]
        rules = svc._rules_dict()
        if rules:
            ids.extend(rules.get("hidden_menu_ids", []))
        return list(dict.fromkeys(ids))
