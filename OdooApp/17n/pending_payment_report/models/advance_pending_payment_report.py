# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class AdvancePendingPaymentReportLine(models.TransientModel):
    _name = "advance.pending.payment.report.line"
    _description = "Advance Pending Payment Report Line"

    report_id = fields.Many2one(
        "advance.pending.payment.report.wizard",
        string="Report",
        ondelete="cascade",
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency")
    total = fields.Monetary(string="Total", currency_field="currency_id")
    paid_amount = fields.Monetary(string="Paid Amount", currency_field="currency_id")
    pending_amount = fields.Monetary(string="Pending Amount", currency_field="currency_id")
    invoice_count = fields.Integer(string="Invoice Count", default=0)
    email = fields.Boolean(string="Email", default=False)
    email_id = fields.Char(string="Email ID", related="partner_id.email", readonly=True)
