# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models
import base64
from io import BytesIO
import xlsxwriter


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_export_products_image(self):
        workbook_stream = BytesIO()
        workbook = xlsxwriter.Workbook(workbook_stream)
        sheet = workbook.add_worksheet('Products')

        # Define header format
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
        sheet.write(0, 0, 'Image', header_format)

        # Set column width for text fields
        sheet.set_column(0, 0, 15)  # Image column (width based on image size)

        row = 1
        for product in self:
            # Insert image if available (using image_128 for medium size)
            if product.image_128:
                image_data = BytesIO(base64.b64decode(product.image_128))

                # Scale image size to fit the cell
                x_scale = 0.9
                y_scale = 0.9
                sheet.set_column(0, 0, 16)  # Adjust width to fit the image
                sheet.set_row(row, 87)  # Adjust row height to fit the image

                sheet.insert_image(row, 0, 'image.png', {
                    'image_data': image_data,
                    'x_scale': x_scale,
                    'y_scale': y_scale,
                    'object_position': 1
                })

            row += 1

        workbook.close()
        workbook_stream.seek(0)

        # Create attachment and download
        attachment = self.env['ir.attachment'].create({
            'name': 'Exported_Products.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(workbook_stream.read()),
            'res_model': 'product.template',
            'res_id': self.ids[0],  # Use the first product ID to link the attachment
        })

        download_url = '/web/content/%s?download=true' % attachment.id
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'new',
        }

    def action_export_products(self):
        workbook_stream = BytesIO()
        workbook = xlsxwriter.Workbook(workbook_stream)
        sheet = workbook.add_worksheet('Products')

        # Define header format
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
        sheet.write(0, 0, 'Name', header_format)
        sheet.write(0, 1, 'Category', header_format)
        sheet.write(0, 2, 'Internal Reference', header_format)
        sheet.write(0, 3, 'Barcode', header_format)
        sheet.write(0, 4, 'Sale Price', header_format)
        sheet.write(0, 5, 'Cost', header_format)
        sheet.write(0, 6, 'Image', header_format)

        # Set column width for text fields
        sheet.set_column(0, 0, 30)  # Name column
        sheet.set_column(1, 1, 20)  # Category column
        sheet.set_column(2, 2, 20)  # Internal Reference column
        sheet.set_column(3, 3, 20)  # Barcode column
        sheet.set_column(4, 4, 15)  # Sale Price column
        sheet.set_column(5, 5, 15)  # Cost column
        sheet.set_column(6, 6, 15)  # Image column (width based on image size)

        row = 1
        for product in self:
            currency_symbol = product.currency_id.symbol
            sale_price = product.list_price
            cost_price = product.standard_price
            formatted_sale_price = f"{currency_symbol} {sale_price}"   # Combine the currency symbol and sale price
            formatted_cost_price = f"{currency_symbol} {cost_price}"   # Combine the currency symbol and cost price
            sheet.write(row, 0, product.name)
            sheet.write(row, 1, product.categ_id.name or '')
            sheet.write(row, 2, product.default_code or '')
            sheet.write(row, 3, product.barcode or '')
            sheet.write(row, 4, formatted_sale_price)  # Sale Price
            sheet.write(row, 5, formatted_cost_price)  # Cost

            # Insert image if available (using image_128 for medium size)
            if product.image_128:
                image_data = BytesIO(base64.b64decode(product.image_128))

                # Scale image size to fit the cell
                x_scale = 0.9
                y_scale = 0.9
                sheet.set_column(6, 6, 15.8)  # Adjust width to fit the image
                sheet.set_row(row, 87)  # Adjust row height to fit the image

                sheet.insert_image(row, 6, 'image.png', {
                    'image_data': image_data,
                    'x_scale': x_scale,
                    'y_scale': y_scale,
                    'object_position': 1
                })

            row += 1

        workbook.close()
        workbook_stream.seek(0)

        # Create attachment and download
        attachment = self.env['ir.attachment'].create({
            'name': 'Exported_Products.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(workbook_stream.read()),
            'res_model': 'product.template',
            'res_id': self.ids[0],  # Use the first product ID to link the attachment
        })

        download_url = '/web/content/%s?download=true' % attachment.id
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'new',
        }
