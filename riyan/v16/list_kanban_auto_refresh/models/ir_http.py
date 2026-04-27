# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models

MIN_INTERVAL_MS = 1000


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super().session_info()
        uid = res.get("uid")
        if not uid:
            return res
        icp = self.env["ir.config_parameter"].sudo()
        raw_enabled = icp.get_param("list_kanban_auto_refresh.enabled", "False")
        if isinstance(raw_enabled, bool):
            enabled = raw_enabled
        else:
            enabled = str(raw_enabled or "").lower() in ("1", "true", "yes")
        try:
            interval_ms = int(
                icp.get_param("list_kanban_auto_refresh.interval_ms", "10000") or "10000"
            )
        except ValueError:
            interval_ms = 10000
        interval_ms = max(MIN_INTERVAL_MS, interval_ms)
        res["list_kanban_auto_refresh"] = {
            "global_enabled": enabled,
            "interval_ms": interval_ms,
        }
        return res
