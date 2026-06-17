# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PettyCashReplenishment(models.Model):
    _name = "petty.cash.replenishment"
    _description = "Petty Cash Replenishment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        required=True,
        copy=False,
        default="/",
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related="fund_id.currency_id",
        store=True,
    )
    fund_id = fields.Many2one(
        "petty.cash.fund",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    requested_by_id = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        required=True,
    )
    date = fields.Date(default=fields.Date.context_today, required=True)
    amount = fields.Monetary(
        currency_field="currency_id",
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("petty.cash.replenishment") or "/"
        return super().create(vals_list)

    def action_submit(self):
        self.filtered(lambda r: r.state == "draft").write({"state": "submitted"})

    def action_approve(self):
        self.filtered(lambda r: r.state == "submitted").write({"state": "approved"})

    def action_done(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError(_("Only approved replenishments can be posted."))
            fund = rec.fund_id
            if not fund.source_bank_journal_id or not fund.source_bank_journal_id.default_account_id:
                raise UserError(_("Configure a replenishment source journal with a default account."))
            bank_account = fund.source_bank_journal_id.default_account_id
            move = self.env["account.move"].create(
                {
                    "move_type": "entry",
                    "journal_id": fund.source_bank_journal_id.id,
                    "date": rec.date,
                    "ref": rec.name,
                    "company_id": rec.company_id.id,
                    "petty_cash_fund_id": fund.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "account_id": fund.petty_cash_account_id.id,
                                "debit": rec.amount,
                                "credit": 0.0,
                                "name": _("Petty cash replenishment"),
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "account_id": bank_account.id,
                                "debit": 0.0,
                                "credit": rec.amount,
                                "name": _("Petty cash replenishment"),
                            },
                        ),
                    ],
                }
            )
            move.action_post()
            rec.move_id = move
            rec.state = "done"
            rec.message_post(body=_("Replenishment posted: %s") % (move.display_name,))

    def action_cancel(self):
        self.filtered(lambda r: r.state in ("draft", "submitted", "approved")).write({"state": "cancelled"})
