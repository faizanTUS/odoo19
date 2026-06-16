# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import api, models


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.model
    def _sanitize_act_window_dict_for_web_client(self, action):
        """Strip view types not listed in web ``session.view_info`` (Odoo 19: e.g. ``activity``).

        Stored actions and ``get_formview_action()`` can reference chatter activity views; the
        web client only accepts types returned by ``ir.ui.view.get_view_info()`` and raises
        otherwise when executing ``ir.actions.act_window``.
        """
        if not action or action.get("type") != "ir.actions.act_window":
            return action
        try:
            allowed = set(self.env["ir.ui.view"].get_view_info().keys())
        except Exception:  # pylint: disable=broad-except
            allowed = {"list", "form", "graph", "pivot", "kanban", "calendar", "search"}
        out = dict(action)
        views = out.get("views")
        if views:
            filtered = []
            for item in views:
                row = list(item) if isinstance(item, (tuple, list)) else item
                if len(row) >= 2 and row[1] in allowed:
                    filtered.append(row)
            if filtered:
                out["views"] = filtered
            else:
                res_model = out.get("res_model")
                res_id = out.get("res_id")
                out["views"] = [[False, "form"]]
                if res_model is not None:
                    out["res_model"] = res_model
                if res_id is not None:
                    out["res_id"] = res_id
        vm = out.get("view_mode")
        if vm and isinstance(vm, str):
            modes = [m.strip() for m in vm.split(",") if m.strip() in allowed]
            out["view_mode"] = ",".join(modes) if modes else "form"
        return out

    def _get_action_dict(self):
        result = super()._get_action_dict()
        return self._sanitize_act_window_dict_for_web_client(result)
