# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    allow_custom_currency_rate = fields.Boolean(
        "Allow New Currency Rate?",
        store=True,
        copy=False,
        readonly=False,
        help="Allow new currency rate to manage custom rate on different models",
    )
