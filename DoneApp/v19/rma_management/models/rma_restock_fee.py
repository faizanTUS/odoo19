# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class RmaRestockFee(models.Model):
    _name = 'rma.restock.fee'
    _description = 'RMA Restocking Fee'

    name = fields.Char(string='Name', required=True)
    fee_type = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount'),
    ], string='Type', default='percentage', required=True)
    amount = fields.Float(string='Amount', required=True)
    active = fields.Boolean(default=True)
