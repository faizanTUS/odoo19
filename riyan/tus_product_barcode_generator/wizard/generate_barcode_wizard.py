# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import base64
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import qrcode
import logging

_logger = logging.getLogger(__name__)


class GenerateBarcodeWizard(models.TransientModel):
    _name = 'generate.barcode.wizard'
    _description = 'Generate Barcode Wizard'

    override_existing = fields.Boolean("Override Barcode if Exist")
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
    ], string="Barcode Type", default='ean13', required=True)

    prefix = fields.Char("Prefix", help="Prefix to start the barcode with.")
    barcode_length = fields.Integer("Barcode Length", default=13)
    generate_qr_from = fields.Selection([
        ('barcode', 'Barcode'),
        ('name', 'Product Name'),
        ('url', 'Product URL'),
    ], string="QR Code Source", default='barcode', help="Only used if Barcode Type is QR Code")

    sample_barcode = fields.Char("Sample Barcode", compute="_compute_sample_barcode")
    preview_image = fields.Binary("Preview", compute="_compute_sample_image")

    @api.onchange('barcode_type')
    def _onchange_barcode_type(self):
        length_map = {
            'ean8': 8,
            'ean13': 13,
            'ean14': 14,
            'isbn10': 10,
            'isbn13': 13,
            'upca': 12,
            'itf': 14,
        }
        self.barcode_length = length_map.get(self.barcode_type, 13)
        self.prefix = self._get_common_prefix()

    def _get_common_prefix(self):
        active_ids = self.env.context.get('active_ids', [])
        barcodes = self.env['product.template'].browse(active_ids).mapped('barcode')
        prefixes = [b[:3] for b in barcodes if b and len(b) >= 3]
        return max(set(prefixes), key=prefixes.count) if prefixes else ''

    @api.depends('barcode_type', 'prefix', 'barcode_length')
    def _compute_sample_barcode(self):
        for rec in self:
            numeric_len = rec.barcode_length - len(rec.prefix or '')
            rec.sample_barcode = (rec.prefix or '') + str(random.randint(10**(numeric_len-1), 10**numeric_len - 1)) if numeric_len > 0 else ''

    @api.depends('barcode_type', 'sample_barcode', 'generate_qr_from')
    def _compute_sample_image(self):
        for rec in self:
            try:
                if rec.barcode_type == 'qrcode':
                    data = rec.sample_barcode
                    if rec.generate_qr_from == 'name':
                        data = 'Sample Product'
                    elif rec.generate_qr_from == 'url':
                        data = 'https://example.com/product'

                    qr = qrcode.QRCode(version=1, box_size=10, border=2)
                    qr.add_data(data)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    rec.preview_image = base64.b64encode(buffer.getvalue())
                else:
                    barcode_class = barcode.get_barcode_class(rec.barcode_type)
                    buffer = BytesIO()
                    barcode_obj = barcode_class(rec.sample_barcode, writer=ImageWriter())
                    barcode_obj.write(buffer)
                    rec.preview_image = base64.b64encode(buffer.getvalue())
            except Exception as e:
                rec.preview_image = False

    def generate_barcodes(self):
        product_ids = self.env['product.template'].browse(self.env.context.get('active_ids'))

        if not product_ids:
            raise UserError(_("No products selected."))

        products_to_override = product_ids.filtered(lambda p: p.barcode and not self.override_existing)
        if products_to_override:
            names = ", ".join(products_to_override.mapped('name')[:5])
            if len(products_to_override) > 5:
                names += ", ..."
            raise UserError(_(
                "The following products already have barcodes:\n%s\n\n"
                "To override them, check the 'Override Barcode if Exist' option."
            ) % names)

        for product in product_ids:
            if product.barcode and not self.override_existing:
                continue

            if self.barcode_type == 'qrcode':
                if product.barcode and not self.override_existing:
                    continue

                if self.generate_qr_from == 'name':
                    value = product.name
                elif self.generate_qr_from == 'url':
                    value = f"https://example.com/product/{product.id}"
                else:
                    value = self._generate_code()
            else:
                value = self._generate_code()

            old_barcode = product.barcode or "None"
            product.barcode_type = self.barcode_type
            product.barcode = value
            product.generate_barcode_image()

            _logger.info(
                "[Barcode Generator] Product '%s' barcode updated from '%s' to '%s'",
                product.name, old_barcode, product.barcode
            )

        return {'type': 'ir.actions.act_window_close'}

    def _generate_code(self):
        total_len = self.barcode_length
        prefix_len = len(self.prefix or '')
        number_len = total_len - prefix_len
        if number_len < 1:
            raise UserError(_("Prefix too long for the specified barcode length."))

        return (self.prefix or '') + str(random.randint(10**(number_len - 1), 10**number_len - 1))
