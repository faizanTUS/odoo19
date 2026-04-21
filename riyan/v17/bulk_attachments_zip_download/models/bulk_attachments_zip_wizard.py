# -*- coding: utf-8 -*-
import io
import zipfile
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


def _safe_zip_filename(name):
    if not name:
        name = "file"
    name = name.replace("\\", "_").replace("/", "_").replace("..", "_")
    return name[:255] or "file"


class BulkAttachmentsZipLine(models.TransientModel):
    _name = "bulk.attachments.zip.line"
    _description = "Bulk ZIP attachment line"

    wizard_id = fields.Many2one(
        "bulk.attachments.zip.wizard", required=True, ondelete="cascade"
    )
    attachment_id = fields.Many2one("ir.attachment", required=True, ondelete="restrict")
    name = fields.Char(related="attachment_id.name", readonly=True)
    mimetype = fields.Char(related="attachment_id.mimetype", readonly=True)
    file_size = fields.Integer(related="attachment_id.file_size", readonly=True)
    source = fields.Selection(
        [
            ("record", "Record"),
            ("field", "Record (file field)"),
            ("chatter", "Chatter"),
        ],
        string="Source",
        readonly=True,
    )


class BulkAttachmentsZipWizard(models.TransientModel):
    _name = "bulk.attachments.zip.wizard"
    _description = "Download selected records attachments as ZIP"

    res_model = fields.Char(string="Model", readonly=True)
    res_ids = fields.Char(string="Record IDs", readonly=True)
    include_chatter = fields.Boolean(
        string="Include chatter attachments",
        default=True,
        help="Also pack files posted on the chatter of the selected records.",
    )
    line_ids = fields.One2many(
        "bulk.attachments.zip.line", "wizard_id", string="Files"
    )
    attachment_count = fields.Integer(compute="_compute_stats", string="File count")
    total_bytes = fields.Integer(compute="_compute_stats", string="Total size (bytes)")

    @api.depends("line_ids", "line_ids.file_size")
    def _compute_stats(self):
        for wiz in self:
            wiz.attachment_count = len(wiz.line_ids)
            wiz.total_bytes = sum(wiz.line_ids.mapped("file_size"))

    @api.model
    def _get_config_int(self, key, default):
        param = self.env["ir.config_parameter"].sudo().get_param(key)
        try:
            v = int(param) if param is not None else default
        except (TypeError, ValueError):
            v = default
        return v if v > 0 else 0

    @api.model
    def _get_config_float(self, key, default):
        param = self.env["ir.config_parameter"].sudo().get_param(key)
        try:
            return float(param) if param is not None else default
        except (TypeError, ValueError):
            return default

    @api.model
    def _default_include_chatter_from_settings(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("bulk_attachments_zip.include_chatter", "True")
            == "True"
        )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ctx = self.env.context
        active_model = ctx.get("active_model") or ctx.get("default_res_model")
        active_ids = list(ctx.get("active_ids") or [])
        if not active_model or not active_ids:
            return res
        try:
            records = self.env[active_model].browse(active_ids).exists()
        except KeyError as e:
            raise UserError(
                _("Unknown model: %s") % active_model
            ) from e
        records.check_access_rights("read")
        records.check_access_rule("read")
        ids = records.ids
        res["res_model"] = active_model
        res["res_ids"] = ",".join(str(i) for i in ids)
        chatter_flag = self._default_include_chatter_from_settings()
        if ctx.get("default_include_chatter") is not None:
            chatter_flag = bool(ctx["default_include_chatter"])
        if "include_chatter" in fields_list:
            res["include_chatter"] = chatter_flag
        if "line_ids" in fields_list:
            res["line_ids"] = self._commands_for_lines(
                active_model, ids, chatter_flag
            )
        return res

    @api.model
    def _commands_for_lines(self, res_model, res_ids, include_chatter):
        # Include attachments backing Binary/Image fields (e.g. sale.order.signature).
        # Default ir.attachment search adds res_field=False and hides those rows.
        Attachment = self.env["ir.attachment"].with_context(skip_res_field_check=True)
        atts = Attachment.search(
            [("res_model", "=", res_model), ("res_id", "in", res_ids)]
        )
        seen = set(atts.ids)
        commands = [
            (
                0,
                0,
                {
                    "attachment_id": a.id,
                    "source": "field" if a.res_field else "record",
                },
            )
            for a in atts
        ]
        if include_chatter and "mail.message" in self.env:
            Message = self.env["mail.message"]
            messages = Message.search(
                [("model", "=", res_model), ("res_id", "in", res_ids)]
            )
            chatter = Attachment.search(
                [
                    ("res_model", "=", "mail.message"),
                    ("res_id", "in", messages.ids),
                ]
            )
            for a in chatter:
                if a.id in seen:
                    continue
                seen.add(a.id)
                commands.append((0, 0, {"attachment_id": a.id, "source": "chatter"}))
        return commands

    def action_refresh_lines(self):
        self.ensure_one()
        if not self.res_model or not self.res_ids:
            raise UserError(_("Missing model or record IDs."))
        ids = [int(x) for x in self.res_ids.split(",") if x.strip().isdigit()]
        recs = self.env[self.res_model].browse(ids).exists()
        recs.check_access_rights("read")
        recs.check_access_rule("read")
        cmds = self._commands_for_lines(self.res_model, ids, self.include_chatter)
        # Replace lines in one write (avoid unlink + create edge cases with required fields)
        self.write({"line_ids": [(5, 0, 0)] + cmds})
        # Returning False from call_button closes the modal; re-open the same wizard.
        return {
            "type": "ir.actions.act_window",
            "name": _("Download attachments (ZIP)"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "views": [(False, "form")],
        }

    @api.onchange("include_chatter")
    def _onchange_include_chatter(self):
        if self.res_model and self.res_ids:
            ids = [int(x) for x in self.res_ids.split(",") if x.strip().isdigit()]
            cmds = self._commands_for_lines(
                self.res_model, ids, self.include_chatter
            )
            self.line_ids = [(5, 0, 0)] + cmds

    def _validate_limits(self):
        self.ensure_one()
        max_files = self._get_config_int("bulk_attachments_zip.max_files", 500)
        max_mb = self._get_config_float("bulk_attachments_zip.max_total_mb", 200.0)
        if max_files and len(self.line_ids) > max_files:
            raise UserError(
                _("Too many files (%(count)s). Administrator limit: %(max)s.")
                % {"count": len(self.line_ids), "max": max_files}
            )
        total = sum(self.line_ids.mapped("file_size"))
        if max_mb > 0 and total > max_mb * 1024 * 1024:
            raise UserError(
                _("Total size exceeds the limit of %s MB (configured by administrator).")
                % max_mb
            )

    def _build_zip_stream(self):
        self.ensure_one()
        self._validate_limits()
        if not self.line_ids:
            raise UserError(_("No attachments to download."))
        buf = io.BytesIO()
        used_names = defaultdict(int)
        with zipfile.ZipFile(
            buf, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True
        ) as zf:
            for line in self.line_ids:
                att = line.attachment_id
                try:
                    att.check("read")
                except AccessError as e:
                    raise UserError(_("You cannot read attachment: %s") % att.name) from e
                data = att.raw
                if not data:
                    continue
                base = _safe_zip_filename(att.name)
                used_names[base] += 1
                n = used_names[base]
                if n == 1:
                    arcname = base
                elif "." in base:
                    stem, ext = base.rsplit(".", 1)
                    arcname = "%s (%d).%s" % (stem, n - 1, ext)
                else:
                    arcname = "%s (%d)" % (base, n - 1)
                zf.writestr(arcname, data)
        buf.seek(0)
        return buf

    def _zip_download_filename(self):
        self.ensure_one()
        base = (self.res_model or "attachments").strip() or "attachments"
        return "%s_attachments.zip" % base

    def action_download_zip(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("No attachments to download."))
        self._validate_limits()
        return {
            "type": "ir.actions.act_url",
            "url": "/bulk_attachments_zip/download/%s" % self.id,
            "target": "self",
        }
