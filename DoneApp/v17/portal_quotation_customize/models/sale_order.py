# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import email_split
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    def portal_update_qty(self, quantity):
        """Update qty from portal interaction.

        Guardrails:
        - Only draft quotation can be edited.
        - Quantity must be >= 0.
        """
        self.ensure_one()
        order = self.order_id

        if order.state not in ['draft', 'sent']:
            raise UserError(_("Only draft quotations can be edited from the portal."))

        try:
            qty = float(quantity)
        except Exception:
            raise UserError(_("Invalid quantity value."))

        if qty < 0:
            raise UserError(_("Quantity cannot be negative."))

        # You decide what 0 means. here we just write 0
        self.write({'product_uom_qty': qty})

        return True


    def portal_delete_line(self):
        """Delete line from portal with guardrails."""
        self.ensure_one()
        order = self.order_id

        if order.state not in ['draft', 'sent']:
            raise UserError(_("Only draft quotations can be edited from the portal."))

        self.unlink()
        return True
