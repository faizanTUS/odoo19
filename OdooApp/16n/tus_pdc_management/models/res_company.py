# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    # Accounts
    customer_pdc_account_id = fields.Many2one(
        "account.account",
        string="Customer PDC Account",
        domain="[('deprecated','=',False)]",
    )
    vendor_pdc_account_id = fields.Many2one(
        "account.account",
        string="Vendor PDC Account",
        domain="[('deprecated','=',False)]",
    )
    customer_pdc_bounce_account_id = fields.Many2one(
        "account.account",
        string="Customer PDC Bounce Account",
        domain="[('deprecated','=',False)]",
    )
    vendor_pdc_bounce_account_id = fields.Many2one(
        "account.account",
        string="Vendor PDC Bounce Account",
        domain="[('deprecated','=',False)]",
    )

    # Journals
    customer_pdc_journal_id = fields.Many2one(
        "account.journal",
        string="Customer PDC Journal",
        domain="[('type','=','general')]",  # UI label is Miscellaneous
    )
    vendor_pdc_journal_id = fields.Many2one(
        "account.journal",
        string="Vendor PDC Journal",
        domain="[('type','=','general')]",
    )
    pdc_bank_journal_id = fields.Many2one(
        "account.journal",
        string="PDC Bank Journal",
        domain="[('type','=','bank')]",
    )
