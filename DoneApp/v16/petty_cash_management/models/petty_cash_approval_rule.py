# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PettyCashApprovalRule(models.Model):
    _name = "petty.cash.approval.rule"
    _description = "Petty Cash Approval Rule"
    _order = "fund_id, sequence, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        related="fund_id.company_id",
        store=True,
    )
    fund_id = fields.Many2one(
        "petty.cash.fund",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    amount_from = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        required=True,
    )
    amount_to = fields.Monetary(
        currency_field="currency_id",
        required=True,
        help="Inclusive upper bound for this tier.",
    )
    currency_id = fields.Many2one(
        related="fund_id.currency_id",
        store=True,
    )
    approver_id = fields.Many2one(
        "res.users",
        required=True,
        domain="[('share', '=', False)]",
        help="User who must approve when the voucher amount falls in this range.",
    )
