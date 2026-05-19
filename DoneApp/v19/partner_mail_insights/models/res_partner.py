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

    def _domain_incoming(self):
        self.ensure_one()
        email = (self.email or "").strip()
        dom_email = (
            ["|", ("incoming_email_to", "ilike", email), ("incoming_email_cc", "ilike", email)]
            if email
            else False
        )
        dom_partner = [("partner_ids", "in", self.id)]
        if dom_email:
            return ["|"] + dom_partner + dom_email
        return dom_partner

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
