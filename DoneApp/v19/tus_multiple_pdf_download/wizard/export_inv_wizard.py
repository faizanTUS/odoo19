from odoo import models, fields, api
import base64
import pyminizip
import tempfile
import os
from odoo.exceptions import UserError
import shutil


class ExportPDFWizard(models.TransientModel):
    _name = 'export.pdf.wizard'
    _description = 'Export PDF Wizard'

    invoice_ids = fields.Many2many(
        'account.move', string='Invoices/Bills',
        domain=lambda self: [('move_type', 'in', ('out_invoice', 'in_invoice', 'out_refund','in_refund'))]
    )
    payment_ids = fields.Many2many(
        'account.payment', string='Account Payment',
        domain=lambda self: [('payment_type', 'in', ('outbound', 'inbound'))]
    )
    production_ids = fields.Many2many('mrp.production', string='Production Order')
    sale_order_ids = fields.Many2many('sale.order', string='Sale Order')
    picking_ids = fields.Many2many('stock.picking', string='Delivery Slip')
    is_production = fields.Boolean()
    is_sale = fields.Boolean()
    is_quotation = fields.Boolean()
    is_delivery = fields.Boolean()
    is_purchase = fields.Boolean()
    is_purchase_rfq = fields.Boolean()
    is_work_order = fields.Boolean()
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Order')

    workorder_ids = fields.Many2many('mrp.workorder', string='Production Order')
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

    has_incoming = fields.Boolean(compute='_compute_delivery_types')
    has_outgoing = fields.Boolean(compute='_compute_delivery_types')
    has_both = fields.Boolean(compute='_compute_delivery_types')

    # Global password field
    zip_password = fields.Char('ZIP Password', help='Password for the ZIP file')

    @api.depends('picking_ids')
    def _compute_delivery_types(self):
        for wizard in self:
            has_incoming = any(picking.picking_type_id.code == 'incoming' for picking in wizard.picking_ids)
            has_outgoing = any(picking.picking_type_id.code == 'outgoing' for picking in wizard.picking_ids)
            wizard.has_incoming = has_incoming
            wizard.has_outgoing = has_outgoing
            wizard.has_both = has_incoming and has_outgoing

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update({
            'invoice_ids': [(6, 0, self._context.get('default_invoice_ids', []))],
            'payment_ids': [(6, 0, self._context.get('default_payment_ids', []))],
            'production_ids': [(6, 0, self._context.get('default_production_ids', []))],
            'sale_order_ids': [(6, 0, self._context.get('default_sale_order_ids', []))],
            'purchase_order_ids': [(6, 0, self._context.get('default_purchase_ids', []))],
            'workorder_ids': [(6, 0, self._context.get('default_workorder_ids', []))],
            'picking_ids': [(6, 0, self._context.get('default_picking_ids', []))],
        })
        return res

    def _generate_zip(self, filename, records, report_name, password):
        # Use a temporary directory to store the PDF files before zipping
        temp_dir = tempfile.mkdtemp()

        try:
            pdf_files = []
            for record in records:
                # Validate and sanitize the record name
                sanitized_name = record.name.strip() if record.name else f"record_{record.id}"
                sanitized_name = sanitized_name.replace("/", "_").replace("\\", "_")
                pdf_file_path = os.path.join(temp_dir, f'{sanitized_name}.pdf')

                # Ensure the directory exists
                os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

                # Generate the PDF content
                pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(report_name, res_ids=[record.id])

                # Write the PDF content to a file
                with open(pdf_file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)

                # Validate that the file has been created
                if os.path.exists(pdf_file_path):
                    pdf_files.append(pdf_file_path)
                else:
                    raise UserError(f"PDF file was not created successfully for record {record.name}")

            # Path for the password-protected ZIP file
            zip_file_path = os.path.join(temp_dir, filename)

            # Check that there are files to compress
            if pdf_files:
                # Use pyminizip to compress files with a password
                pyminizip.compress_multiple(pdf_files, [], zip_file_path, password, 5)
            else:
                raise UserError("No PDF files were generated to include in the ZIP file.")

            # Read the password-protected ZIP file
            with open(zip_file_path, 'rb') as zip_file:
                zip_data = zip_file.read()

            # Create an attachment for the ZIP file
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(zip_data),
                'store_fname': filename,
                'mimetype': 'application/zip',
            })

            return attachment
        finally:
            # Use shutil to remove the entire temporary directory
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

    def action_mrp_production(self):
        return self._export_action('Production Order.zip', self.production_ids, 'mrp.action_report_production_order')



    def action_all_sale_quotation(self):
        return self._export_action('Quotation and Sale Order.zip', self.sale_order_ids,'sale.report_saleorder')


    def action_sale_quotation(self):
        return self._export_action('Sale Quotation.zip', self.sale_order_ids.filtered(lambda p: p.state in ['draft', 'sent']),'sale.report_saleorder')

    def action_sale_order(self):
        return self._export_action('Sale Order.zip', self.sale_order_ids.filtered(lambda p: p.state in ['sale']), 'sale.report_saleorder')


    def action_all_purchase_quotation(self):
        return self._export_action('Quotation and Purchase Order.zip', self.purchase_order_ids,'purchase.action_report_purchase_order')

    def action_purchase_order(self):
        return self._export_action('Purchase Order.zip', self.purchase_order_ids,
                                   'purchase.action_report_purchase_order')

    def action_purchase_quotation(self):
        return self._export_action('Purchase Quotation.zip',self.purchase_order_ids,
                                   'purchase.action_report_purchase_order')




    def action_delivery_report(self):
        return self._export_action('Receipts(Incoming)Deliveries(Outgoing).zip', self.picking_ids.filtered(
            lambda p: p.picking_type_id.code in ['incoming', 'outgoing']), 'stock.action_report_delivery')

    def action_incoming_delivery(self):
        return self._export_action('Receipts (Incoming ).zip',
                                   self.picking_ids.filtered(lambda p: p.picking_type_id.code == 'incoming'),
                                   'stock.action_report_delivery')

    def action_outgoing_delivery(self):
        return self._export_action('Deliveries (Outgoing).zip',
                                   self.picking_ids.filtered(lambda p: p.picking_type_id.code == 'outgoing'),
                                   'stock.action_report_delivery')

    def action_work_order(self):
        return self._export_action('Work Order.zip', self.workorder_ids, 'mrp.action_report_workorder')

    def _export_action(self, filename, records, report_name):
        password = self.zip_password or ''  # Use the entered password, or none if empty
        attachment = self._generate_zip(filename, records, report_name, password)
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}/{attachment.name}',
            'target': 'new',
        }
