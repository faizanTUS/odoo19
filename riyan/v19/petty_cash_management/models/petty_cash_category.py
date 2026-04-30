# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class PettyCashCategory(models.Model):
    _name = "petty.cash.category"
    _description = "Petty Cash Expense Category"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    expense_account_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        domain="[('company_ids', 'in', company_id)]",
        help="Debit account when a voucher in this category is paid.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "petty_cash_category_code_company_uniq",
            "unique(code, company_id)",
            "Category code must be unique per company.",
        ),
    ]
