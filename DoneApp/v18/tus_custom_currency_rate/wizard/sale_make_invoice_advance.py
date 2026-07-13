# See LICENSE file for full copyright and licensing details.
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, sale_orders):
        """
        Passing New Currency rate from Sale Order in context while creating a invoice
        @param sale_orders: Sale Order object
        @return: super call
        """
        if not self.advance_payment_method == "delivered" and all(
            self.sale_order_ids.mapped("allow_custom_currency_rate")
        ):
            self = self.with_context(
                new_currency_rate=self.sale_order_ids.new_currency_rate
            )
        return super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
