# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    automated_invoice_email = fields.Boolean(
        string="Automated Invoice Email",
        help="Automatically send an email when an invoice is confirmed for this customer.",
    )
