# See LICENSE file for full copyright and licensing details.
from odoo import _, models


class PosSession(models.Model):
    _inherit = "pos.session"

    # Open Wizard with the close value based on payment method.
    def close_session_wizard(self):
        close_wz_id = self.env["close.session.wizard"].create(
            {
                "total_orders": self.order_count,
                "total_amount": self.total_payments_amount,
            }
        )
        closing_wz_lines = self.env["close.session.wizard.line"]
        closingData = self.get_closing_control_data()
        if closingData.get("default_cash_details"):
            payment_id = closingData.get("default_cash_details").get("id")
            payment_amount = closingData.get("default_cash_details").get("amount")
            closing_wz_lines += self.env["close.session.wizard.line"].create(
                {
                    "payment_method_id": payment_id,
                    "expected_counted": payment_amount,
                    "differences": 0 - payment_amount,
                    "is_default": True,
                    "payment_type": "cash",
                    "session_close_id": close_wz_id.id,
                }
            )
        other_method = [
            {
                "payment_method_id": payment.get("id"),
                "expected_counted": payment.get("amount"),
                "counted": payment.get("type") == "bank" and payment.get("amount") or 0,
                "payment_type": payment.get("type"),
                "is_default": False,
                "session_close_id": close_wz_id.id,
            }
            for payment in closingData.get("other_payment_methods")
        ]
        closing_wz_lines += self.env["close.session.wizard.line"].create(other_method)
        return {
            "name": _("Closing Session"),
            "type": "ir.actions.act_window",
            "res_model": "close.session.wizard",
            "view_mode": "form",
            "res_id": close_wz_id.id,
            "target": "new",
        }
