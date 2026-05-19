# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pending_payment_report_recipient_id = fields.Many2one(
        "res.partner",
        string="Auto-send Pending Payment Report To",
        help="Partner (user) to receive pending payment details email when using 'Send to Configured User'.",
    )

    def get_values(self):
        res = super().get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        partner_id = ICPSudo.get_param("pending_payment_report.recipient_id", default=False)
        res.update(
            pending_payment_report_recipient_id=int(partner_id) if partner_id else False,
        )
        return res

    def set_values(self):
        super().set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(
            "pending_payment_report.recipient_id",
            self.pending_payment_report_recipient_id.id or "",
        )
