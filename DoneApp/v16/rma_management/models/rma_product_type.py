from odoo import models, fields

class RmaProductType(models.Model):
    _name = 'rma.product.type'
    _description = 'RMA Product Type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
