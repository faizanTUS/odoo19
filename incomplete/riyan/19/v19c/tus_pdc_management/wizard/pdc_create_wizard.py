# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TusPdcCreateWizard(models.TransientModel):
    _name = "tus.pdc.create.wizard"
    _description = "Create PDC from Invoice"

    invoice_ids = fields.Many2many("account.move", string="Invoices", required=True)
    pdc_type = fields.Selection([("customer", "Customer PDC"), ("vendor", "Vendor PDC")], required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    cheque_date = fields.Date(required=True)
    cheque_number = fields.Char(required=True)
    bank_name = fields.Char()
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one("res.currency", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        invoices = self.env["account.move"].browse(self.env.context.get("active_ids", []))

        if invoices:
            partner = invoices[0].partner_id.commercial_partner_id
            if any(inv.partner_id.commercial_partner_id != partner for inv in invoices):
                raise UserError(_("All selected invoices must belong to the same partner."))

            move_types = set(invoices.mapped("move_type"))
            if move_types & {"out_invoice", "out_refund"}:
                pdc_type = "customer"
            elif move_types & {"in_invoice", "in_refund"}:
                pdc_type = "vendor"
            else:
                raise UserError(_("Unsupported document type for PDC."))

            res["partner_id"] = partner.id
            res["pdc_type"] = pdc_type
            res["invoice_ids"] = [(6, 0, invoices.ids)]
            res["currency_id"] = invoices[0].company_id.currency_id.id
            res["amount"] = sum(invoices.mapped("amount_residual"))

        return res

    def action_create_pdc(self):
        self.ensure_one()

        pdc = self.env["tus.pdc.payment"].create({
            "pdc_type": self.pdc_type,
            "partner_id": self.partner_id.id,
            "cheque_date": self.cheque_date,
            "cheque_number": self.cheque_number,
            "bank_name": self.bank_name,
            "amount": self.amount,
            "invoice_ids": [(6, 0, self.invoice_ids.ids)],
        })

        return {
            "type": "ir.actions.act_window",
            "name": _("PDC Payment"),
            "res_model": "tus.pdc.payment",
            "view_mode": "form",
            "res_id": pdc.id,
            "target": "current",
        }
