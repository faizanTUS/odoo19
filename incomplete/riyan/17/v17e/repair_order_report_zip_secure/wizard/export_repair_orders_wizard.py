from odoo import models, fields, api
import base64
import pyminizip
import tempfile
import os
import shutil


class ExportRepairOrderWizard(models.TransientModel):
    _name = 'export.repairs.order.wizard'
    _description = 'Export Repairs Order Wizard'

    repair_ids = fields.Many2many('repair.order', string='Production Order')

    zip_password = fields.Char('ZIP Password', help='Password for the ZIP file')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update({
            'repair_ids': [(6, 0, self._context.get('default_repair_ids', []))],
        })
        return res

    def _generate_zip(self, filename, records, report_name, password):
        temp_dir = tempfile.mkdtemp()

        try:
            pdf_files = []
            for record in records:
                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_name, res_ids=record.id)
                pdf_file_path = os.path.join(temp_dir, f'{record.name}.pdf')
                os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)
                with open(pdf_file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)
                pdf_files.append(pdf_file_path)

            zip_file_path = os.path.join(temp_dir, filename)

            pyminizip.compress_multiple(pdf_files, [], zip_file_path, password, 5)

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
        return self._export_action('Repairs.zip', self.repair_ids, 'repair.action_report_repair_order')

    def _export_action(self, filename, records, report_name):
        password = self.zip_password or ''
        attachment = self._generate_zip(filename, records, report_name, password)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}/{attachment.name}',
            'target': 'new',
        }
