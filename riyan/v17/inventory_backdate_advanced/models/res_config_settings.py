# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Stub for stock_sms field so Settings form does not break when stock_sms is not loaded."""
    _inherit = 'res.config.settings'

    stock_move_sms_validation = fields.Boolean(
        related='company_id.stock_move_sms_validation',
        string='SMS Validation with stock move',
        readonly=False
    )
