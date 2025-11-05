# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_optional_view = fields.Boolean(
        string="Enable Optional Tree View",
        config_parameter="tus_show_optional_fields.is_optional_view",
    )
