# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PettyCashApprovalRejectWizard(models.TransientModel):
    _name = "petty.cash.approval.reject.wizard"
    _description = "Reject Petty Cash Voucher"

    voucher_id = fields.Many2one(
        "petty.cash.voucher",
        required=True,
        ondelete="cascade",
    )
    reason = fields.Text(required=True)

    def action_confirm(self):
        self.ensure_one()
        self.voucher_id.action_reject(self.reason)
        return {"type": "ir.actions.act_window_close"}
