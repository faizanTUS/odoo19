from odoo import models, fields, api
import base64
import pyminizip
import tempfile
import os
from odoo.exceptions import UserError
import shutil


class ExportPDFWizard(models.TransientModel):
    _name = 'export.accounting.pdf.wizard'
    _description = 'Export Accounting PDF Wizard'

    invoice_ids = fields.Many2many(
        'account.move', string='Invoices/Bills',
        domain=lambda self: [('move_type', 'in', self._context.get('default_move_types',
                                                                   ['out_invoice', 'in_invoice', 'out_refund',
                                                                    'in_refund']))]
    )
    payment_ids = fields.Many2many(
        'account.payment', string='Account Payment',
        domain=lambda self: [('payment_type', 'in', self._context.get('default_payment_type', ['outbound', 'inbound']))]
    )

    is_production = fields.Boolean()
    is_sale = fields.Boolean()
    is_quotation = fields.Boolean()

    is_delivery = fields.Boolean()
    is_purchase = fields.Boolean()
    is_purchase_rfq = fields.Boolean()
    is_work_order = fields.Boolean()

    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)
    move_type = fields.Selection([
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt')
    ], string='Move Type', required=True, default='out_invoice')

    zip_password = fields.Char('ZIP Password', help='Password for the ZIP file')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update({
            'invoice_ids': [(6, 0, self._context.get('default_invoice_ids', []))],
            'payment_ids': [(6, 0, self._context.get('default_payment_ids', []))],
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

    def action_export(self):
        return self._export_action('Invoices.zip', self.invoice_ids, 'account.account_invoices')

    def action_export_bill(self):
        return self._export_action('Vendor Bill.zip', self.invoice_ids, 'account.account_invoices')

    def action_customer_credit_notes(self):
        return self._export_action('Customer Credit Notes.zip', self.invoice_ids, 'account.account_invoices')

    def action_vendor_credit_notes(self):
        return self._export_action('Vendor Credit Notes.zip', self.invoice_ids, 'account.account_invoices')

    def action_customer_payment(self):
        return self._export_action('Customer Payment.zip', self.payment_ids, 'account.action_report_payment_receipt')

    def _export_action(self, filename, records, report_name):
        password = self.zip_password or ''
        attachment = self._generate_zip(filename, records, report_name, password)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}/{attachment.name}',
            'target': 'new',
        }
