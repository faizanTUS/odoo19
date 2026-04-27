# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class DocumentTag(models.Model):
    _name = "document.tag"
    _description = "Document / Attachment Tag"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    color = fields.Integer(string="Color Index")
