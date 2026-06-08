# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PettyCashPolicy(models.Model):
    _name = "petty.cash.policy"
    _description = "Petty Cash Spend Policy"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    max_amount_per_voucher = fields.Monetary(
        string="Max Amount per Voucher",
        currency_field="currency_id",
        help="Maximum amount allowed on a single voucher.",
    )
    daily_limit_per_employee = fields.Monetary(
        currency_field="currency_id",
        help="Maximum total spend per employee per day across vouchers.",
    )
    monthly_limit_per_employee = fields.Monetary(
        currency_field="currency_id",
        help="Maximum total spend per employee per month across vouchers.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    category_ids = fields.Many2many(
        "petty.cash.category",
        "petty_cash_policy_category_rel",
        "policy_id",
        "category_id",
        string="Allowed Categories",
        help="If set, vouchers must use one of these categories.",
    )
    require_receipt = fields.Boolean(
        help="When enabled, funds using this policy flag vouchers without attachments for compliance.",
    )
    active = fields.Boolean(default=True)
