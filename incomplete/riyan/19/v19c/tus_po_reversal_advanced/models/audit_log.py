# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class TusReversalAuditLog(models.Model):
    _name = "tus.reversal.audit.log"
    _description = "Reversal/Reset Audit Log"
    _order = "create_date desc"

    action = fields.Selection([
        ("cancel", "Cancel"),
        ("reverse", "Reverse"),
        ("reset", "Reset to Draft"),
    ], required=True)
    model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    display_name_related = fields.Char(string="Record")
    reason = fields.Text()
    user_id = fields.Many2one("res.users", default=lambda s: s.env.user, readonly=True)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company, readonly=True)
    note = fields.Text()
    origin = fields.Char(help="PO/Bill/Picking that triggered this action")

    def as_mail_body(self):
        self.ensure_one()
        return _(
            "%(action)s on %(model)s(%(id)s) by %(user)s\nReason: %(reason)s\nNote: %(note)s",
        ) % {
            "action": dict(self._fields["action"].selection).get(self.action),
            "model": self.model, "id": self.res_id,
            "user": self.user_id.display_name,
            "reason": self.reason or "-",
            "note": self.note or "-",
        }
