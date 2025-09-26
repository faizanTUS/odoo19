# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_generate_barcode = fields.Boolean(
        string="Generate Barcode On Product Creation",
        config_parameter='tus_product_barcode_generator.auto_generate'
    )

    barcode_type = fields.Selection([
        ('code128', 'Code 128'),
        ('ean13', 'EAN-13'),
        ('ean8', 'EAN-8'),
        ('ean14', 'EAN-14'),
        ('isbn10', 'ISBN10'),
        ('isbn13', 'ISBN13'),
        ('upca', 'UPC-A'),
        ('itf', 'ITF14'),
        ('qrcode', 'QR Code'),
    ], string="Barcode Type", config_parameter='tus_product_barcode_generator.barcode_type', default='ean13')
