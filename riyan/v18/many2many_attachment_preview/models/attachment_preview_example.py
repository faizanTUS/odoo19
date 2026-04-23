# -*- coding: utf-8 -*-
from odoo import fields, models


class Map2AttachmentExample(models.Model):
    """Single in-module example: many2many_binary + preview (no extra apps required)."""

    _name = "map2.attachment.example"
    _description = "Attachment Preview Example"
    _order = "id desc"

    name = fields.Char(string="Title", required=True, default="Example")

    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="map2_attachment_example_ir_attachment_rel",
        column1="example_id",
        column2="attachment_id",
        string="Attachments",
    )
