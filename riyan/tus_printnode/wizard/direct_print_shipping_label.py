from odoo import _, fields, models
from odoo.exceptions import UserError


class PrintnodeAttachmentPrint(models.TransientModel):
    _name = "printnode.attachment.print"
    _description = "Direct Print Label"

    attachment_line_ids = fields.One2many(
        "attachment.line", "wizard_id", string="Attachment Lines"
    )

    def default_get(self, fields):
        result = super(PrintnodeAttachmentPrint, self).default_get(fields)
        res_ids = self._context.get("active_ids")
        res_model = self._context.get("active_model")
        if res_ids and res_model:
            records = self.env[res_model].browse(res_ids)
            attachment_line_ids = self.env["attachment.line"]
            default_printer = (
                self.env.user.printnode_label_printer_id
                or self.env.user.printnode_printer_id
            )
            for record in records:
                printable_attachments = (
                    self.env["ir.attachment"]
                    .sudo()
                    .search(
                        [
                            ("res_model", "=", record._name),
                            ("res_id", "=", record.id),
                            (
                                "mimetype",
                                "in",
                                ["application/pdf", "application/octet-stream"],
                            ),
                        ]
                    )
                )
                for attachment in printable_attachments:
                    attachment_line_ids |= self.env["attachment.line"].create(
                        {
                            "attachment_id": attachment.id,
                            "printnode_printer_id": default_printer.id
                            if default_printer
                            else False,
                        }
                    )
            if attachment_line_ids:
                result.update(
                    {"attachment_line_ids": [(6, 0, attachment_line_ids.ids)]}
                )
        return result

    def do_direct_print(self):
        if self.attachment_line_ids.filtered(lambda x: not x.printnode_printer_id):
            raise UserError(
                _(
                    "Printer must be selected in all attachments. You can remove the line if you wish to don't print some of those."
                )
            )
        for line in self.attachment_line_ids:
            online = line.printnode_printer_id._check_printer_status()
            if not online:
                raise UserError(
                    _("Printer {} isn't available for print. Please check.").format(
                        line.printnode_printer_id.name
                    )
                )
            content_type = "pdf_base64"
            if line.attachment_id.mimetype == "application/octet-stream":
                content_type = "raw_base64"
            line.printnode_printer_id.print_document_from_attachments(
                line.attachment_id.name, line.attachment_id.datas, type=content_type
            )
        return {
            "effect": {
                "fadeout": "slow",
                "message": "Yeah! All documents sent to printer!",
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }


class AttachmentPrintLine(models.TransientModel):
    _name = "attachment.line"
    _description = "Direct Print Label Lines"

    attachment_id = fields.Many2one(
        "ir.attachment", string="Attachment", ondelete="cascade"
    )
    printnode_printer_id = fields.Many2one("printnode.printer", string="Printer")
    wizard_id = fields.Many2one("printnode.attachment.print", "Wizard")
