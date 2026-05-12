# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields


class BulkOrderWizard(models.TransientModel):
    _name = 'bulk.order.wizard'
    _description = 'Bulk Order Wizard'

    name = fields.Char("Reference")
