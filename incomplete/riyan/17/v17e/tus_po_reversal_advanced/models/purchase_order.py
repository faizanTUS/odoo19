# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.tools import html_sanitize

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_open_cancel_reset_wizard(self):
        self.ensure_one()
        return self.env["tus.cancel.reset.wizard"].with_context(
            active_ids=self.ids, active_model="purchase.order"
        ).action_open_wizard()

    def _tus_log(self, action, reason=None, note=None):
        for po in self:
            self.env["tus.reversal.audit.log"].create({
                "action": action,
                "model": po._name,
                "res_id": po.id,
                "display_name_related": po.display_name,
                "reason": reason,
                "origin": po.name,
                "note": note,
            })
            # po.message_post(body=_("Action: %s<br/>Reason: %s") % (action, reason or "-"))
            html_message = html_sanitize(f"""
                            <p><b>Action:</b> {action}</p>
                            <p><b>Reason:</b> {reason or '-'}</p>
                        """)

            po.message_post(
                body=html_message,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )

    # helper for dependency traversal
    def tus_get_related_pickings(self):
        return self.mapped("picking_ids")

    def tus_get_related_bills(self):
        return self.mapped("invoice_ids").filtered(lambda m: m.move_type in ("in_invoice","in_refund"))