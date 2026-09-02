# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, models, _, fields
from odoo.tools import html_sanitize

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_open_cancel_reset_wizard(self):
        self.ensure_one()
        return self.env["tus.cancel.reset.wizard"].with_context(
            active_ids=self.ids, active_model="account.move"
        ).action_open_wizard()

    def _tus_log(self, action, reason=None, note=None):
        for m in self:
            self.env["tus.reversal.audit.log"].create({
                "action": action, "model": m._name, "res_id": m.id,
                "display_name_related": m.display_name, "reason": reason,
                "origin": m.invoice_origin, "note": note,
            })
            html_message = html_sanitize(f"""
                            <p><b>Action:</b> {action}</p>
                            <p><b>Reason:</b> {reason or '-'}</p>
                        """)
            # m.message_post(body=_("Action: %s<br/>Reason: %s") % (action, reason or "-"))
            m.message_post(
                body=html_message,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
