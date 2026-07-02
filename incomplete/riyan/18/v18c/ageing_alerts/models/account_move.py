# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
from datetime import date

class AccountMove(models.Model):
    _inherit = "account.move"

    days_overdue = fields.Integer(
        string="Days Overdue",
        compute="_compute_ageing_data",
        store=True,
    )
    ageing_bucket = fields.Selection(
        [
            ("current", "Not Due / Current"),
            ("0_30", "0-30 Days"),
            ("31_60", "31-60 Days"),
            ("61_90", "61-90 Days"),
            ("90_plus", "> 90 Days"),
        ],
        string="Ageing Bucket",
        compute="_compute_ageing_data",
        store=True,
    )

    @api.depends("invoice_date_due", "payment_state", "state")
    def _compute_ageing_data(self):
        today = date.today()
        for move in self:
            # Defaults
            move.days_overdue = 0
            move.ageing_bucket = "current"

            # Only consider posted and unpaid/partially paid moves with a due date
            if (
                move.state != "posted"
                or move.payment_state in ("paid", "in_payment")
                or not move.invoice_date_due
            ):
                continue

            delta = (today - move.invoice_date_due).days

            if delta <= 0:
                move.days_overdue = 0
                move.ageing_bucket = "current"
            else:
                move.days_overdue = delta
                if 1 <= delta <= 30:
                    move.ageing_bucket = "0_30"
                elif 31 <= delta <= 60:
                    move.ageing_bucket = "31_60"
                elif 61 <= delta <= 90:
                    move.ageing_bucket = "61_90"
                else:
                    move.ageing_bucket = "90_plus"
