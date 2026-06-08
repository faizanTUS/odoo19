# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    petty_cash_fund_id = fields.Many2one(
        "petty.cash.fund",
        string="Petty Cash Fund",
        readonly=True,
        ondelete="set null",
        index=True,
    )
