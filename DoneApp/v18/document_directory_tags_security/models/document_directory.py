# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DocumentDirectory(models.Model):
    _name = "document.directory"
    _description = "Document Directory"
    _order = "sequence, name, id"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one(
        "document.directory",
        string="Parent Directory",
        ondelete="restrict",
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("document.directory", "parent_id", string="Sub-Directories")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )
    res_model_id = fields.Many2one(
        "ir.model",
        string="Related Model",
        ondelete="set null",
        help="When set, new attachments linked to this model can be auto-assigned to this directory.",
    )
    res_model_name = fields.Char(related="res_model_id.model", string="Technical Model", readonly=True)
    group_ids = fields.Many2many(
        "res.groups",
        "document_directory_group_rel",
        "directory_id",
        "group_id",
        string="Restrict to Groups",
        help="If empty, any internal user with document access may use this directory (subject to role rules). "
        "If set, the user must belong to at least one listed group.",
    )
    allowed_document_user_ids = fields.Many2many(
        "res.users",
        "document_directory_allowed_user_rel",
        "directory_id",
        "user_id",
        string="Assigned Document Users",
        help="Users in the “Document User” group may only see directories listed here.",
    )
    directory_tag_ids = fields.Many2many(
        "document.directory.tag",
        "document_directory_directory_tag_rel",
        "directory_id",
        "tag_id",
        string="Directory Tags",
    )
    sequence_id = fields.Many2one(
        "ir.sequence",
        string="Numbering Sequence",
        copy=False,
        ondelete="restrict",
        help="Technical sequence used to generate document reference codes for this folder.",
    )
    sequence_prefix = fields.Char(
        default="DOC/%(range_year)s/",
        help="Python format string passed to ir.sequence (e.g. DOC/%(range_year)s/). "
        "Year token uses range_year from the sequence date.",
    )
    sequence_padding = fields.Integer(default=4, help="Number of digits for the numeric part.")
    document_count = fields.Integer(compute="_compute_document_count")

    @api.depends("parent_path")
    def _compute_document_count(self):
        Attachment = self.env["ir.attachment"].sudo()
        for directory in self:
            directory.document_count = Attachment.search_count([("directory_id", "=", directory.id)])

    @api.model_create_multi
    def create(self, vals_list):
        directories = super().create(vals_list)
        directories._ensure_sequence()
        return directories

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ("sequence_prefix", "sequence_padding", "company_id")):
            for directory in self:
                if directory.sequence_id:
                    directory.sequence_id.sudo().write(
                        {
                            "prefix": directory.sequence_prefix or "",
                            "padding": directory.sequence_padding or 4,
                            "company_id": directory.company_id.id,
                        }
                    )
                else:
                    directory._ensure_sequence()
        return res

    def _ensure_sequence(self):
        Seq = self.env["ir.sequence"].sudo()
        for directory in self:
            if directory.sequence_id:
                continue
            prefix = directory.sequence_prefix or "DOC/"
            seq = Seq.create(
                {
                    "name": _("%s — Document directory") % directory.name,
                    "code": "document.hub.directory.%s" % directory.id,
                    "implementation": "standard",
                    "prefix": prefix,
                    "padding": directory.sequence_padding or 4,
                    "company_id": directory.company_id.id,
                }
            )
            directory.sudo().write({"sequence_id": seq.id})

    def unlink(self):
        seqs = self.mapped("sequence_id")
        res = super().unlink()
        seqs.sudo().unlink()
        return res

    def action_open_attachments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Documents in %s") % self.name,
            "res_model": "ir.attachment",
            "view_mode": "kanban,list,form",
            "domain": [("directory_id", "=", self.id)],
            "context": {"default_directory_id": self.id},
        }

    def _get_next_sequence_code(self):
        self.ensure_one()
        if not self.sequence_id:
            self._ensure_sequence()
        if not self.sequence_id:
            return False
        return self.sequence_id.sudo().next_by_id()

    @api.model
    def _get_default_global_sequence_code(self):
        """Fallback DOC/… code when no directory applies."""
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("document.hub.default")
            or "DOC/NEW"
        )

    def action_rebuild_sequence(self):
        """Advanced: recreate sequence from current prefix/padding (admin)."""
        for directory in self:
            old = directory.sequence_id
            directory.write({"sequence_id": False})
            if old:
                old.unlink()
        self._ensure_sequence()
        return True
