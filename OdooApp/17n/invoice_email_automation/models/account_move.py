# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    automated_email_send = fields.Boolean(
        string="Automated Email Send",
        readonly=True
    )

    def action_post(self):
        res = super().action_post()

        to_send = self.filtered(
            lambda inv: inv.is_sale_document()
                        and inv.partner_id.automated_invoice_email
                        and not inv.automated_email_send
        )
        if not to_send:
            return res

        template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        if template:
            for inv in to_send:
                template.send_mail(inv.id, force_send=True)
            to_send.write({'automated_email_send': True})
        return res
