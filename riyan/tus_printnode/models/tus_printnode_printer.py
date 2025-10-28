import base64
import logging
from datetime import datetime

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class NodePrinter(models.Model):
    _name = "node.printer"
    _description = "PrintNode Printer"

    name = fields.Char("Name", required=True, help="Printer Name")
    description = fields.Text("Description")
    state = fields.Char("State", help="Current Status of Printer")

    @api.depends("state", "system_id.state")
    def _get_printer_status(self):
        for rec in self:
            rec.is_online = rec.state == "online" and rec.system_id.state == "connected"

    default = fields.Boolean("Default Printer?")
    is_color_printer = fields.Boolean("Color Printer")
    system_id = fields.Many2one("printnode.system", "System", help="Related System")
    config_id = fields.Many2one(
        "printnode.config",
        related="system_id.config_id",
        readonly=True,
        store=True,
        string="Configuration",
    )
    printnode_id = fields.Char("PrintNode Identification", copy=False)
    printnode_role_ids = fields.One2many(
        "printnode.role", "node_printer_id", string="Roles"
    )
    is_online = fields.Boolean(
        compute="_get_printer_status", string="Online", store=True
    )
    paper_ids = fields.Many2many("printnode.paper", string="Papers")

    def name_get(self):
        res = []
        for printer in self:
            name = (
                f"{printer.name} - {printer.printnode_id} on {printer.system_id.name}"
            )
            res.append((printer.id, name))
        return res

    def create_print_role(self, title, printnode_role_id):
        role_obj = self.env["printnode.role"]
        res = self.config_id._send_api_key_request(
            "printjobs/{}".format(printnode_role_id)
        )

        role_detail = res[0] if isinstance(res, list) else res

        def covert_date(value):
            ts = (
                f"{value.partition('T')[0]} {value.partition('T')[2].partition('.')[0]}"
            )
            value = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            return value

        role = role_obj.create(
            {
                "name": title,
                "printnode_id": printnode_role_id,
                "node_printer_id": self.id,
                "state": role_detail.get("state"),
                "created_at": covert_date(role_detail.get("createTimestamp")),
            }
        )

        return role

    def get_default(self):
        return self.search([("default", "=", True)], limit=1)

    def _check_printer_status(self):
        if not self:
            return False
        response = self.config_id._send_api_key_request(f"printers/{self.printnode_id}")

        printer_dict = (
            response[0] if response and isinstance(response, list) else response
        )

        if printer_dict:
            system_state = printer_dict["computer"]["state"]
            self.system_id.sudo().write({"state": system_state})
            self.sudo().write(
                {
                    "state": printer_dict["state"]
                    if system_state == "connected"
                    else "offline"
                }
            )

        return self.is_online

    def print_document_from_attachments(self, title, document, type="pdf_base64"):
        self.ensure_one()
        request_data = {
            "printerId": self.printnode_id,
            "title": title,
            "source": "Odoo",
            "contentType": type,
            "content": document.decode("ascii"),
            "options": {},
        }

        if printnode_role_id := self.config_id._send_api_key_request(
            "printjobs", request_data=request_data, method="POST"
        ):
            return self.create_print_role(title, printnode_role_id)
        else:
            raise warnings(_("Printing of document is failed!"))

    def print_document(self, report, title, document, printing_details):
        # self.ensure_one()
        request_data = {
            "printerId": self.printnode_id,
            "title": title,
            "source": "Odoo",
            "contentType": "pdf_base64"
            if report.report_type in ["qweb-pdf"]
            else "raw_base64",
            "content": base64.b64encode(document).decode("ascii"),
            "options": {},
        }

        if printing_details.get("paper"):
            request_data["options"].update({"paper": printing_details.get("paper")})

        if print_node_role_id := self.config_id._send_api_key_request(
            "printjobs", request_data=request_data, method="POST"
        ):
            return self.create_print_role(title, print_node_role_id)
        else:
            raise warnings(_("Printing of document is failed!"))

    def open_role_from_printer(self):
        self.ensure_one()
        [action] = self.env.ref("tus_printnode.action_printnode_role").read()
        action["domain"] = [("node_printer_id", "=", self.id)]
        return action

    def _create_update_vals(self, printer_dict, capabilities_directory, config):
        for unwanted_data in ["createTimestamp"]:
            if (
                printer_dict.get(unwanted_data, False)
                or printer_dict.get(unwanted_data, False) is None
            ):
                del printer_dict[unwanted_data]
        paper_ids = self.env["printnode.paper"].add_or_modify_printer_papers(
            capabilities_directory
        )
        system_dict = printer_dict.pop("computer", False)
        system_id = self.env["printnode.system"]._create_or_update_system(
            system_dict, config
        )
        printer_dict.update(
            {
                "printnode_id": printer_dict.pop("id", False),
                "system_id": system_id.id,
                "paper_ids": [(6, 0, paper_ids)],
            }
        )
        return printer_dict


class PrintNodePaper(models.Model):
    _name = "printnode.paper"
    _description = "PrintNode Paper"
    _order = "name asc"

    name = fields.Char("Name", required=True, help="Name of Paper")
    width = fields.Integer("Width")
    height = fields.Integer("Height")

    def add_or_modify_printer_papers(self, capabilities_directory):
        if capabilities_directory is None:
            return []
        papers_dict = capabilities_directory.get("papers")
        paper_ids = []
        for paper_name, sizes in papers_dict.items():
            paper = self.search([("name", "=", paper_name)], limit=1)
            vals = {
                "name": paper_name,
                "width": sizes[0],
                "height": sizes[1],
            }
            if paper:
                paper.write(vals)
            else:
                paper = paper.create(vals)
            paper_ids.append(paper.id)
        return paper_ids


class PrintnodeRole(models.Model):
    _name = "printnode.role"
    _description = "Printed Document Details"
    _order = "id desc"

    name = fields.Char("Name", required=True)
    printnode_id = fields.Char("PrintNode Identification")
    node_printer_id = fields.Many2one(
        "node.printer", "Printer", required=True, ondelete="cascade"
    )
    state = fields.Selection(
        selection=[
            ("pending_confirmation", "Pending Confirmation"),
            ("new", "New"),
            ("sent_to_client", "Sent to client"),
            ("queued", "Queued"),
            ("in_progress", "In Progress"),
            ("disappeared", "Disappeared"),
            ("received", "Received"),
            ("downloading", "Downloading"),
            ("downloaded", "Downloaded"),
            ("preparing_to_print", "Preparing to Print"),
            ("queued_to_print", "Queued to Print"),
            ("expired", "Expired"),
            ("done", "Done"),
            ("error", "Error"),
            ("deleted", "Deleted"),
        ],
        string="State",
        default="new",
    )
    printnode_state = fields.Char(
        compute="_printnode_state", string="State in PrintNode"
    )
    created_at = fields.Datetime("Created At")
    message = fields.Text("Message")

    def _printnode_state(self):
        for rec in self:
            if rec.state in ["done", "error", "deleted", "expired", "disappeared"]:
                rec.printnode_state = rec.printnode_state
            else:
                response = rec.node_printer_id.config_id._send_api_key_request(
                    f"printjobs/{rec.printnode_id}"
                )

                role_detail = response[0] if isinstance(response, list) else response
                rec.state = role_detail.get("state")
                rec.printnode_state = role_detail.get("state")
