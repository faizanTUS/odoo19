# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MIN_INTERVAL_MS = 1000


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    list_kanban_auto_refresh_enabled = fields.Boolean(
        string="Allow auto refresh data",
        help="When enabled, list and kanban views can soft-reload data on a timer. "
        "Users may still turn auto refresh off per screen from the view toolbar.",
        config_parameter="list_kanban_auto_refresh.enabled",
        default=False,
    )
    list_kanban_auto_refresh_interval_ms = fields.Integer(
        string="Refresh interval (ms)",
        help="Default time between automatic data reloads in milliseconds. "
        "Minimum 1000 ms to protect server performance.",
        config_parameter="list_kanban_auto_refresh.interval_ms",
        default=10000,
    )

    @api.constrains("list_kanban_auto_refresh_interval_ms")
    def _check_list_kanban_auto_refresh_interval(self):
        for rec in self:
            if rec.list_kanban_auto_refresh_interval_ms < MIN_INTERVAL_MS:
                raise ValidationError(
                    _("Refresh interval must be at least %(min)s ms.", min=MIN_INTERVAL_MS)
                )
