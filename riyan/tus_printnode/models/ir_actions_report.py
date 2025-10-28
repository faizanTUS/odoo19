import datetime
import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import warnings
from odoo.tools.safe_eval import safe_eval


class ActionsReport(models.Model):
    _inherit = "ir.actions.report"

    printing_action_ids = fields.One2many(
        "user.wise.print", "report_id", string="Actions"
    )
    is_color_printer = fields.Boolean("Color Printer")

    def print_action(self):
        action = {}
        if user_action := self.env["user.wise.print"].search(
            [
                ("user_id", "=", self.env.uid),
                ("report_id", "=", self.id),
                # ("print_action_type", "!=", "user_default"),
            ],
            limit=1,
        ):
            user_action.node_printer_id.config_id.action_update_printers_list()
            action.update({t: u for t, u in user_action.print_action().items() if u})
        return action

    def printnode_print_action_for_report(self, report_name, value_number=False):
        name_report = self._get_report_from_name(report_name)
        if not name_report:
            return {}
        report_result = name_report.print_action()
        report_result.update(
            {
                "printer_name": report_result["printer"].name
                if report_result.get("printer")
                else False,
                "report_id": report_result.get("printer").id
                if report_result.get("printer")
                else report_result.get("printer"),
                "is_online": report_result["printer"].is_online
                if report_result.get("printer")
                else False,
                "is_color_printer": report_result["printer"].is_color_printer
                if report_result.get("printer")
                else False,
                "is_qweb_color_print": name_report.is_color_printer,
            }
        )
        return report_result

    def print_report_validation(self, printing_details, printer, document):
        if printer and document:
            online = printer._check_printer_status()
            if not online:
                raise UserError(
                    _("There is no available Printer to print.").format(printer.name)
                )
            if (
                printer.paper_ids
                and "paper" in printing_details
                and printing_details["paper"]
                and printing_details["paper"] not in printer.paper_ids.mapped("name")
            ):
                raise UserError(
                    _(
                        "The chosen paper size ({}) is not available for the printer{}. \nHere is a list of the available papers:\n{}"
                    ).format(
                        printing_details["paper"],
                        printer.name,
                        ",\n".join(printer.paper_ids.mapped("name")),
                    )
                )
            if self.report_type not in ["qweb-html", "qweb-pdf"]:
                raise UserError(
                    _(
                        "The chosen report type ({}) is not supported by printer {}. Kindly verify the report type in the selected report."
                    ).format("HTML", printer.name)
                )
            return True
        return UserError(
            _("The printer or document necessary to print this report cannot be found.")
        )

    def direct_document_print(self, report_ref, res_ids, data=None, **kwargs):
        # Generate the document and its format in PDF
        document, doc_format = self.with_context(
            force_stop_printing=True
        )._render_qweb_pdf(report_ref, res_ids, data=data)

        # Get printing details and the printer from context
        printing_details = self.print_action()
        printer = printing_details.pop("printer", None)

        # Raise an exception if no printer is configured
        if not printer:
            raise warnings(_("No printer configured to print this report."))
        # Validate the report for printing
        self.print_report_validation(printing_details, printer, document)

        if res_ids:
            # Fetch objects based on res_ids
            obj = self.env[self.model].browse(res_ids)
            title = self.name
            if self.print_report_name and len(obj) <= 1:
                title = safe_eval(
                    self.print_report_name,
                    {"object": obj, "time": datetime.datetime.now().time()},
                )
            for ac in range(
                0, int(data.get("value_number")) if data.get("value_number") else 1
            ):
                printer.print_document(self, title, document, printing_details)
        return True

    def document_sent_to_printer(self, printing_details, printer, document):
        if self.env.context.get("force_stop_printing"):
            return False
        return bool(printing_details["action"] in ["user_default",'server'] and printer and document)

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        document, doc_format = super(ActionsReport, self)._render_qweb_pdf(
            report_ref, res_ids=res_ids, data=data
        )
        if self.id:
            printing_details = self.print_action()
            printer = printing_details.pop("printer", None)
            if direct_print := self.document_sent_to_printer(
                printing_details, printer, document
            ):
                self.print_report_validation(printing_details, printer, document)
                title = self.name
                if res_ids:
                    obj = self.env["ir.actions.report"].browse(res_ids)
                    if self.print_report_name and len(obj) <= 1:
                        title = safe_eval(
                            self.print_report_name, {"object": obj, "time": time}
                        )
                printer.print_document(self, title, document, printing_details)
        return document, doc_format


class UserWisePrint(models.Model):
    _name = "user.wise.print"
    _description = "Userwise Print Action"

    report_id = fields.Many2one(
        "ir.actions.report", string="Report", required=True, ondelete="cascade"
    )
    print_action_type = fields.Selection(
        [
            ("server", "Send to Printer"),
            ("client", "Send to Client"),
            ("user_default", "Print Copies"),
        ],
        string="Default Action",
        default="client",
        required=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        domain=lambda self: [
            ("all_group_ids", "=", self.env.ref("tus_printnode.printnode_group_user").id)
        ],
        ondelete="cascade",
    )
    node_printer_id = fields.Many2one(
        "node.printer", string="Printer", ondelete="cascade"
    )
    printnode_paper_id = fields.Many2one(
        "printnode.paper",
        string="Paper",
    )
    print_type = fields.Selection(
        selection=[("print", "Print"), ("download", "Download"), ("open", "Open")],
        string="Default printing option",
    )

    @api.onchange("user_id")
    def product_id_change(self):
        filter_product_ids = [
            data.user_id.id for data in self.report_id.printing_action_ids
        ]
        return {
            "domain": {
                "user_id": [
                    (
                        "all_group_ids",
                        "=",
                        self.env.ref("tus_printnode.printnode_group_user").id,
                    ),
                    ("id", "not in", filter_product_ids),
                ]
            }
        }

    def _get_readable_fields(self):
        data = super()._get_readable_fields()
        data.add("print_type")
        return data

    def report_action(self, docids, data=None, config=True):
        data = super(UserWisePrint, self).report_action(docids, data, config)
        data["id"] = self.id
        data["print_type"] = self.print_type
        return data

    def print_action(self):
        if not self:
            return {}
        return {
            "action": self.print_action_type,
            "printer": self.node_printer_id,
            "paper": self.printnode_paper_id.name if self.printnode_paper_id else False,
        }
