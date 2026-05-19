# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_after_validation = fields.Boolean(string="Allow Cancel/Reset After Validation",
        config_parameter="tus_reversal.allow_after_validation")
    auto_handle_dependencies = fields.Boolean(string="Auto Handle Dependencies (Bills/Pickings)",
        config_parameter="tus_reversal.auto_handle_dependencies")
    require_reason = fields.Boolean(string="Require Reason in Wizard",
        config_parameter="tus_reversal.require_reason")
