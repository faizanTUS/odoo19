# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import models, fields

class PdfSplitResult(models.Model):
    _name = 'pdf.split.result'
    _description = 'Split PDF Result'

    name = fields.Char('Filename')
    document_id = fields.Many2one('pdf.split.document', string='Original Document')
    split_file = fields.Binary('Split Page PDF', attachment="True")
