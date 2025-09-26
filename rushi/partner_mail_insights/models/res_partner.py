# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    incoming_mail_count = fields.Integer(
        string="Incoming",
        compute="_compute_mail_counts",
        help="Number of emails sent FROM this contact (email_from)"
    )
    outgoing_mail_count = fields.Integer(
        string="Outgoing",
        compute="_compute_mail_counts",
        help="Number of emails sent TO this contact (email_to / cc / recipients)"
    )

    def _domain_incoming(self):
        self.ensure_one()
        email = (self.email or "").strip() #email = springcircuit1@gmail.com
        dom = ['|',
               ('email_from', 'ilike', email),
               ('author_id', '=', self.id)]
        if not email:
            dom = [('author_id', '=', self.id)]
        return dom

    def _domain_outgoing(self):
        self.ensure_one()
        email = (self.email or "").strip()
        dom_email = ['|', ('incoming_email_to', 'ilike', email), ('incoming_email_cc', 'ilike', email)] if email else False
        dom_partner = [('partner_ids', 'in', self.id)]
        if dom_email:
            return ['|'] + dom_partner + dom_email  # (partner in recipients) OR (email_to/cc contains email)
        else:
            return dom_partner

    @api.depends('email')
    def _compute_mail_counts(self):
        Mail = self.env['mail.message'].sudo()
        for partner in self:
            if not partner:
                partner.incoming_mail_count = 0
                partner.outgoing_mail_count = 0
                continue
            incoming = Mail.search_count(partner._domain_incoming())
            outgoing = Mail.search_count(partner._domain_outgoing())
            partner.incoming_mail_count = incoming
            partner.outgoing_mail_count = outgoing

    def action_view_incoming_mails(self):
        self.ensure_one()
        action = {
            'name': _('Incoming Emails'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.message',
            'view_mode': 'list,form',
            'domain': self._domain_incoming(),
            'context': {'search_default_outgoing': 0},
            'target': 'current',
        }
        return action

    def action_view_outgoing_mails(self):
        self.ensure_one()
        action = {
            'name': _('Outgoing Emails'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.message',
            'view_mode': 'list,form',
            'domain': self._domain_outgoing(),
            'context': {'search_default_outgoing': 1},
            'target': 'current',
        }
        return action