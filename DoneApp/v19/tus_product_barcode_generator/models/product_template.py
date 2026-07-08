# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api,_
from io import BytesIO
import base64
from PIL import Image
import barcode
from barcode.writer import ImageWriter
import qrcode
import logging
import random
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_image = fields.Binary("Barcode Image", compute="_compute_barcode_image", store=True)
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
    ], string="Barcode Type")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'barcode_type' in fields_list and not defaults.get('barcode_type'):
            config = self.env['ir.config_parameter'].sudo()
            barcode_type = config.get_param('tus_product_barcode_generator.barcode_type', default='ean13')
            defaults['barcode_type'] = barcode_type
        return defaults

    @api.depends('barcode')
    def _compute_barcode_image(self):
        config = self.env['ir.config_parameter'].sudo()
        barcode_type = config.get_param('tus_product_barcode_generator.barcode_type', default='ean13')

        for product in self:
            if product.barcode:
                try:
                    barcode_class = barcode.get_barcode_class(barcode_type)
                    valid_length = {
                        'ean13': 12,
                        'ean8': 7,
                        'upca': 11,
                        'isbn10': 9,
                        'isbn13': 12,
                        'code128': None,
                        'itf': 13,
                        'ean14': 13,
                        'qrcode': None
                    }

                    required_len = valid_length.get(barcode_type)
                    code = product.barcode

                    if required_len and len(code) != required_len:
                        _logger.warning(f"Invalid barcode length for {barcode_type}: {code}")
                        product.barcode_image = False
                        continue

                    bar_code = barcode_class(code, writer=ImageWriter())
                    buffer = BytesIO()
                    bar_code.write(buffer, options={
                        'write_text': True,
                        'font_size': 10,
                        'module_width': 0.4,
                        'module_height': 12.0,
                        'text_distance': 4
                    })
                    product.barcode_image = base64.b64encode(buffer.getvalue())
                except Exception as e:
                    _logger.warning(f"Error generating barcode for {product.name}: {e}")
                    product.barcode_image = False
            else:
                product.barcode_image = False

    def action_generate_barcode(self):
        config = self.env['ir.config_parameter'].sudo()
        barcode_type = config.get_param('tus_product_barcode_generator.barcode_type', default='ean13')

        for product in self:
            if not product.barcode:
                if barcode_type == 'ean8':
                    product.barcode = str(random.randint(1000000, 9999999))
                elif barcode_type == 'ean13':
                    product.barcode = str(random.randint(100000000000, 999999999999))
                elif barcode_type == 'upca':
                    product.barcode = str(random.randint(10000000000, 99999999999))
                elif barcode_type == 'isbn10':
                    product.barcode = str(random.randint(100000000, 999999999))
                elif barcode_type == 'isbn13':
                    product.barcode = str(random.randint(100000000000, 999999999999))
                else:
                    product.barcode = str(random.randint(1000000000000, 9999999999999))

    def generate_barcode_image(self):
        for product in self:
            barcode_type = product.barcode_type
            barcode_number = product.barcode

            if not barcode_type:
                config = self.env['res.config.settings'].sudo().get_values()
                barcode_type = config.get('barcode_type')

            if not barcode_type:
                raise UserError(_("No Barcode Type set. Please set it in the Product or Settings."))
            expected_lengths = {
                'ean8': 8,
                'ean13': 13,
                'ean14': 14,
                'isbn10': 10,
                'isbn13': 13,
                'upca': 12,
                'itf': 14,
            }

            expected_length = expected_lengths.get(barcode_type)
            if not barcode_number:
                raise UserError(_("Please enter a barcode before generating the image."))

            if expected_length and len(barcode_number) != expected_length:
                raise UserError(_(
                    "Barcode '%s' does not match expected length for %s (required: %d digits)."
                ) % (barcode_number, barcode_type.upper(), expected_length))

            try:
                if barcode_type == 'qrcode':
                    # Handle QR Code separately using qrcode lib
                    import qrcode
                    qr = qrcode.QRCode(version=1, box_size=10, border=2)
                    qr.add_data(barcode_number)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    product.barcode_image = base64.b64encode(buffer.getvalue())
                else:
                    barcode_class = barcode.get_barcode_class(barcode_type)
                    buffer = BytesIO()
                    barcode_obj = barcode_class(barcode_number, writer=ImageWriter())
                    barcode_obj.write(buffer)
                    product.barcode_image = base64.b64encode(buffer.getvalue())

            except Exception as e:
                raise UserError(_("Failed to generate barcode: %s") % str(e))

    @api.model_create_multi
    def create(self, vals_list):
        config = self.env['ir.config_parameter'].sudo()
        auto = config.get_param('tus_product_barcode_generator.auto_generate') == 'True'
        default_type = config.get_param('tus_product_barcode_generator.barcode_type', default='ean13')

        for vals in vals_list:
            if not vals.get('barcode_type'):
                vals['barcode_type'] = default_type

            if auto and not vals.get('barcode'):
                if vals['barcode_type'] == 'ean8':
                    vals['barcode'] = str(random.randint(1000000, 9999999))
                elif vals['barcode_type'] == 'ean13':
                    vals['barcode'] = str(random.randint(100000000000, 999999999999))
                elif vals['barcode_type'] == 'upca':
                    vals['barcode'] = str(random.randint(10000000000, 99999999999))
                elif vals['barcode_type'] == 'isbn10':
                    vals['barcode'] = str(random.randint(100000000, 999999999))
                elif vals['barcode_type'] == 'isbn13':
                    vals['barcode'] = str(random.randint(100000000000, 999999999999))
                else:
                    vals['barcode'] = str(random.randint(1000000000000, 9999999999999))

        return super(ProductTemplate, self).create(vals_list)
