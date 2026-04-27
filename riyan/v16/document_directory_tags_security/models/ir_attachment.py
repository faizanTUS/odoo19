# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    directory_id = fields.Many2one(
        "document.directory",
        string="Directory",
        ondelete="set null",
        index=True,
    )
    directory_name = fields.Char(
        related="directory_id.name",
        string="Directory Name",
        readonly=True,
        related_sudo=True,
    )
    document_tag_ids = fields.Many2many(
        "document.tag",
        "ir_attachment_document_tag_rel",
        "attachment_id",
        "tag_id",
        string="Document Tags",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        index=True,
        help="Used for “My Documents” and ownership reporting.",
    )
    document_sequence_ref = fields.Char(
        string="Document Reference",
        readonly=True,
        copy=False,
        index=True,
        help="Auto-generated code from the directory sequence or the global DOC/ fallback.",
    )

    def _read_group_allowed_fields(self):
        """Relax Odoo 16's hardcoded attachment read_group allowlist.

        Base Odoo 16 only permits a narrow set of `ir.attachment` fields in
        `read_group()` for non-system users. The web client can still trigger
        grouped reads for normal search/view fields when opening attachment
        actions, which leads to the generic "not allowed to access these
        fields" popup for Document Users.

        Keep obviously sensitive binary/storage fields blocked, but allow the
        normal stored/groupable attachment fields used by this module and the
        standard web client.
        """
        blocked = {
            "access_token",
            "checksum",
            "datas",
            "db_datas",
            "index_content",
            "raw",
            "store_fname",
        }
        allowed = set(super()._read_group_allowed_fields())
        allowed.update(
            name
            for name, field in self._fields.items()
            if name not in blocked and (field.store or field.type == "many2many")
        )
        allowed.add("directory_name")
        return sorted(allowed)

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        """Keep Odoo 16's `res_field=False` attachment safeguard without its
        overly strict non-admin field allowlist.

        For this module, normal users legitimately open custom attachment views
        that can trigger grouped reads on additional stored fields. The stock
        Odoo 16 guard raises the generic "not allowed to access these fields on
        attachments" popup even when the user already has model/record access.
        """
        if not fields:
            raise AccessError(_("Sorry, you must provide fields to read on attachments"))
        groupby = [groupby] if isinstance(groupby, str) else groupby
        if any("(" in field for field in fields + groupby):
            raise AccessError(
                _("Sorry, the syntax 'name:agg(field)' is not available for attachments")
            )
        domain = list(domain)
        if not any(item[0] in ("id", "res_field") for item in domain):
            domain.insert(0, ("res_field", "=", False))
        return models.Model.read_group(
            self,
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    @api.model_create_multi
    def create(self, vals_list):
        Directory = self.env["document.directory"].sudo()
        company = self.env.company
        for vals in vals_list:
            vals.setdefault("owner_id", self.env.user.id)
            if vals.get("res_field"):
                # Stored binary fields on models — skip hub numbering & directory auto-match
                continue
            res_model = vals.get("res_model")
            if not vals.get("directory_id") and res_model:
                dom = [
                    ("res_model_id.model", "=", res_model),
                    ("active", "=", True),
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", vals.get("company_id") or company.id),
                ]
                directory = Directory.search(dom, order="sequence asc, id asc", limit=1)
                if directory:
                    vals["directory_id"] = directory.id
            if not vals.get("document_sequence_ref"):
                if vals.get("directory_id"):
                    dir_rec = Directory.browse(vals["directory_id"])
                    vals["document_sequence_ref"] = dir_rec._get_next_sequence_code()
                else:
                    vals["document_sequence_ref"] = Directory._get_default_global_sequence_code()
            vals.setdefault("owner_id", self.env.user.id)
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        todo = self.filtered(lambda a: a.directory_id and not a.document_sequence_ref)
        if todo:
            for att in todo:
                att.sudo().write(
                    {"document_sequence_ref": att.directory_id._get_next_sequence_code()}
                )
        return res
