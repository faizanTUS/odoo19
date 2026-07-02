# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api
import base64
import pyminizip
import tempfile
import os
from odoo.exceptions import UserError
import shutil


class ExportPurchasePDFWizard(models.TransientModel):
    _name = 'export.purchase.pdf.wizard'
    _description = 'Export Purchase PDF Wizard'

    is_production = fields.Boolean()
    is_purchase = fields.Boolean()
    is_purchase_rfq = fields.Boolean()

    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Order')

    zip_password = fields.Char('ZIP Password', help='Password for the ZIP file')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update({
            'purchase_order_ids': [(6, 0, self._context.get('default_purchase_ids', []))],
        })
        return res

    def _generate_zip(self, filename, records, report_name, password):
        temp_dir = tempfile.mkdtemp()

        try:
            pdf_files = []
            for record in records:
                sanitized_name = record.name.strip() if record.name else f"record_{record.id}"
                sanitized_name = sanitized_name.replace("/", "_").replace("\\", "_")
                pdf_file_path = os.path.join(temp_dir, f'{sanitized_name}.pdf')

                os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_name, res_ids=[record.id])

                with open(pdf_file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)

                if os.path.exists(pdf_file_path):
                    pdf_files.append(pdf_file_path)
                else:
                    raise UserError(f"PDF file was not created successfully for record {record.name}")

            zip_file_path = os.path.join(temp_dir, filename)

            if pdf_files:
                pyminizip.compress_multiple(pdf_files, [], zip_file_path, password, 5)
            else:
                raise UserError("No PDF files were generated to include in the ZIP file.")

            with open(zip_file_path, 'rb') as zip_file:
                zip_data = zip_file.read()

            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(zip_data),
                'store_fname': filename,
                'mimetype': 'application/zip',
            })

            return attachment
        finally:
            shutil.rmtree(temp_dir)

    def action_all_purchase_quotation(self):
        return self._export_action('Quotation and Purchase Order.zip', self.purchase_order_ids, 'purchase.action_report_purchase_order')

    def action_purchase_order(self):
        return self._export_action(
            'Purchase Order.zip',
            self.purchase_order_ids.filtered(lambda p: p.state in ['to_approve', 'purchase']),
            'purchase.action_report_purchase_order',
        )

    def action_purchase_quotation(self):
        return self._export_action(
            'Purchase Quotation.zip',
            self.purchase_order_ids.filtered(lambda p: p.state in ['draft', 'sent']),
            'purchase.action_report_purchase_order',
        )

    def _export_action(self, filename, records, report_name):
        password = self.zip_password or ''
        attachment = self._generate_zip(filename, records, report_name, password)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}/{attachment.name}',
            'target': 'new',
        }
