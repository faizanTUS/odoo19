# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.tools import html_sanitize


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_open_cancel_reset_wizard(self):
        self.ensure_one()
        return self.env["tus.cancel.reset.wizard"].with_context(
            active_ids=self.ids, active_model="stock.picking"
        ).action_open_wizard()

    def _tus_log(self, action, reason=None, note=None):
        for p in self:
            self.env["tus.reversal.audit.log"].create({
                "action": action, "model": p._name, "res_id": p.id,
                "display_name_related": p.display_name, "reason": reason, "origin": p.origin, "note": note,
            })
            html_message = html_sanitize(f"""
                                        <p><b>Action:</b> {action}</p>
                                        <p><b>Reason:</b> {reason or '-'}</p>
                                    """)
            p.message_post(body=html_message,
                           message_type="comment",
                           subtype_xmlid="mail.mt_note", )
            # p.message_post(body=_("Action: %s<br/>Reason: %s") % (action, reason or "-"))
