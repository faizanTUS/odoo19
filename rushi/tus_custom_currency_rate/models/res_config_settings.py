# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Using this field we are allowing to manage custom currency rate for different models
    allow_custom_currency_rate = fields.Boolean(
        related="company_id.allow_custom_currency_rate",
        string="Allow New Currency Rate?",
        readonly=False,
        help="Allow new currency rate to manage custom rate on different models",
    )
