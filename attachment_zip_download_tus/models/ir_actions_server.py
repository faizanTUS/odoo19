""" Import Packages """
from urllib.parse import urlencode

from odoo import _, fields, models


class IrActionsServer(models.Model):
    """Ir Actions Server"""

    _inherit = "ir.actions.server"

    state = fields.Selection(
        selection_add=[
            ("zip_file", "Zip File"),
        ],
        ondelete={"zip_file": "cascade"},
    )
    action_message = fields.Text(
        string="Message",
        help="If set, this message will be displayed in the wizard.",
    )

    def _run_action_zip_file_multi(self, eval_context=None):
        """
        Create Dynamic context item menu in action.
        """
        context = dict(self.env.context)
        context.update({"server_action_id": self.id})
        if context and context.get("active_ids"):
            active_ids = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", context.get("active_model")),
                    ("res_id", "in", context.get("active_ids")),
                ]
            )
            if not active_ids:
                title = _("No attachment!")
                message = _("There is no document found to download.")
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "type": "warning",
                        "title": title,
                        "message": message,
                        "sticky": False,
                    },
                }
            params = urlencode({"attachment_ids": active_ids.ids})
            return {
                "type": "ir.actions.act_url",
                "url": f"/web/attachment/download_zip_file?{params}",
                "target": "new",
            }
