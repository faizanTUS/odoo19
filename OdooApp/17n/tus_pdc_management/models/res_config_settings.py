# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    customer_pdc_account_id = fields.Many2one(
        related="company_id.customer_pdc_account_id",
        readonly=False,
    )
    vendor_pdc_account_id = fields.Many2one(
        related="company_id.vendor_pdc_account_id",
        readonly=False,
    )
    customer_pdc_bounce_account_id = fields.Many2one(
        related="company_id.customer_pdc_bounce_account_id",
        readonly=False,
    )
    vendor_pdc_bounce_account_id = fields.Many2one(
        related="company_id.vendor_pdc_bounce_account_id",
        readonly=False,
    )

    customer_pdc_journal_id = fields.Many2one(
        related="company_id.customer_pdc_journal_id",
        readonly=False,
    )
    vendor_pdc_journal_id = fields.Many2one(
        related="company_id.vendor_pdc_journal_id",
        readonly=False,
    )
    pdc_bank_journal_id = fields.Many2one(
        related="company_id.pdc_bank_journal_id",
        readonly=False,
    )
