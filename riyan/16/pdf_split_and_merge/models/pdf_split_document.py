# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import fitz
import base64

class PdfSplitDocument(models.Model):
    _name = 'pdf.split.document'
    _description = 'PDF Split Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Filename')
    type = fields.Selection([('split', 'Split'), ('merge', 'Merge')], string='Type', required=True)
    pdf_file = fields.Binary('PDF File', required=True)
    split_ids = fields.One2many('pdf.split.result', 'document_id', string='Split PDFs')
    state = fields.Selection([('draft', 'To Split'), ('split', 'Splitted'), ('merged', 'Merged')], default='draft',
                             string='Status', tracking=True)

    def action_split_pdf(self):
        return {
            "type": "ir.actions.client",
            "tag": "open_split_pdf_dialog",
            "target": 'new',
            "props": {
                'documentId': self.id,
            },
        }

    def action_merge_pdf(self):
        return {
            "type": "ir.actions.client",
            "tag": "open_merge_pdf_dialog",
            "target": 'new',
            "props": {
                'documentId': self.id,
            },
        }

    @api.constrains('pdf_file', 'name')
    def _check_file_is_pdf(self):
        for record in self:
            if record.name and not record.name.lower().endswith('.pdf'):
                raise ValidationError(_("Only PDF files are allowed."))
