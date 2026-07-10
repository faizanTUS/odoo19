# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CloseSessionWizard(models.TransientModel):
    _name = "close.session.wizard"
    _description = "Close Pos Session Wizard"

    payment_method_ids = fields.One2many(
        "close.session.wizard.line", "session_close_id", string="Session Payment Liens"
    )
    note = fields.Text(string="Notes")
    total_orders = fields.Integer()
    total_amount = fields.Float()

    def action_close_session(self):
        active_id = self.env.context.get("active_id")
        if active_id:
            session_id = self.env["pos.session"].browse(active_id)
            default_cash = self.payment_method_ids.filtered(
                lambda l: l.is_default
            ).counted
            closing_cash = session_id.post_closing_cash_details(default_cash)
            if closing_cash.get("successful"):
                session_id.update_closing_control_state_session(self.note)
                bank_payment = [
                    (pm.payment_method_id.id, pm.differences)
                    for pm in self.payment_method_ids.filtered(
                        lambda l: l.payment_type == "bank"
                    )
                ]
                closing_ui = session_id.with_context(
                    self.env.context
                ).close_session_from_ui(bank_payment)
                if not closing_ui.get("successful"):
                    raise UserError(_(closing_ui.get("message")))
                else:
                    return {"type": "ir.actions.act_window_close"}
            else:
                raise UserError(_(closing_cash.get("message")))


class CloseSessionWizardLine(models.TransientModel):
    _name = "close.session.wizard.line"
    _description = "Close Pos Session Wizard Line"

    session_close_id = fields.Many2one("close.session.wizard", string="Session Close")
    payment_method_id = fields.Many2one("pos.payment.method", string="Payment Method")
    expected_counted = fields.Float("Expected")
    counted = fields.Float("Counted")
    is_default = fields.Boolean(default=False)
    differences = fields.Float("differences")
    payment_type = fields.Char()

    @api.onchange("counted")
    def onchange_counted(self):
        self.differences = self.counted - self.expected_counted
