# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    """Stub for stock_sms field so Settings form does not break when stock_sms is not loaded."""
    _inherit = 'res.company'

    stock_move_sms_validation = fields.Boolean(
        string='SMS Confirmation',
        default=False,
        help='Send an automatic confirmation SMS when Delivery Orders are done (from Stock SMS app when installed).'
    )
