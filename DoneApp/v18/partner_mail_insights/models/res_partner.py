# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    incoming_mail_count = fields.Integer(
        string="Incoming",
        compute="_compute_mail_counts",
        help="Number of emails received by this contact (recipients / to / cc)",
    )
    outgoing_mail_count = fields.Integer(
        string="Outgoing",
        compute="_compute_mail_counts",
        help="Number of outgoing emails posted on this contact's thread",
    )

    def _mail_partner_ids(self):
        self.ensure_one()
        partner_ids = self.commercial_partner_id.ids
        if self.id not in partner_ids:
            partner_ids.append(self.id)
        return partner_ids

    def _domain_incoming(self):
        self.ensure_one()
        partner_ids = self._mail_partner_ids()
        email = (self.email or "").strip()
        domain = ["&", ("message_type", "=", "email")]
        if email:
            return domain + [
                "|",
                "|",
                ("partner_ids", "in", partner_ids),
                ("author_id", "in", partner_ids),
                ("email_from", "ilike", email),
            ]
        return domain + [
            "|",
            ("partner_ids", "in", partner_ids),
            ("author_id", "in", partner_ids),
        ]

    def _domain_outgoing(self):
        self.ensure_one()
        dom = [
            ("model", "=", "res.partner"),
            ("res_id", "=", self.id),
            ("message_type", "in", ["comment", "email_outgoing"]),
        ]
        return dom

    @api.depends("email")
    def _compute_mail_counts(self):
        Mail = self.env["mail.message"].sudo()
        for partner in self:
            partner.incoming_mail_count = Mail.search_count(partner._domain_incoming())
            partner.outgoing_mail_count = Mail.search_count(partner._domain_outgoing())

    def action_view_incoming_mails(self):
        self.ensure_one()
        return {
            "name": _("Incoming Emails"),
            "type": "ir.actions.act_window",
            "res_model": "mail.message",
            "view_mode": "list,form",
            "domain": self._domain_incoming(),
            "context": {},
            "target": "current",
        }

    def action_view_outgoing_mails(self):
        self.ensure_one()
        return {
            "name": _("Outgoing Emails"),
            "type": "ir.actions.act_window",
            "res_model": "mail.message",
            "view_mode": "list,form",
            "domain": self._domain_outgoing(),
            "context": {},
            "target": "current",
        }
