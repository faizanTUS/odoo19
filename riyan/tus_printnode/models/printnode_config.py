import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
import warnings

_logger = logging.getLogger(__name__)


class printnodeconfig(models.Model):
    _name = "printnode.config"
    _description = "PrintNode Configration"

    def _compute_printer_count(self):
        for rec in self:
            rec.printer_count = len(self.printer_ids)
            rec.system_count = len(self.system_ids)

    name = fields.Char("Name", required=True, help="PrintNode Account Name")
    api_url = fields.Char(
        string="API URL", required=True, default="https://api.printnode.com"
    )
    api_key = fields.Char(string="API KEY", required=True, copy=False)
    state = fields.Selection(
        selection=[("draft", "Draft"), ("confirmed", "Confirmed")], default="draft"
    )
    printnode_id = fields.Integer("PrintNode ID", copy=False)
    printer_ids = fields.One2many("node.printer", "config_id", string="Printers")
    system_ids = fields.One2many("printnode.system", "config_id", string="Computers")
    printer_count = fields.Integer(
        compute="_compute_printer_count", string="Printer Count"
    )
    system_count = fields.Integer(
        compute="_compute_printer_count", string="System Count"
    )

    def _send_api_key_request(
        self, request_url, request_data=None, method="GET", params=None
    ):
        if request_data is None:
            # request_data = {}
            request_data = {'test':'test',}
        if params is None:
            params = {}
        if not self.api_key:
            raise ValidationError(_("The PrintNode API key could not be found.!"))
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(request_data)
        api_url = "{api_url}/{url}".format(api_url=self.api_url, url=request_url)
        try:
            request_id = requests.request(
                method,
                api_url,
                auth=HTTPBasicAuth(self.api_key, ""),
                data=json_data,
                headers=headers,
                params=params,
            )

            request_id.raise_for_status()
            api_response_text = request_id.text
            _logger.info("PrintNode API Response: %s", api_response_text)
        except requests.HTTPError as e:
            _logger.error("PrintNode API Error: %s", request_id.text)
            raise UserError(f"{request_id.text}") from e
        return json.loads(api_response_text) if api_response_text else {}

    def verify_the_connection(self):
        try:
            self._send_api_key_request("whoami")
        except Exception as e:
            raise warnings(e) from e
        self.write({"state": "confirmed"})
        self.action_update_printers_list()
        return {
            "effect": {
                "fadeout": "slow",
                "message": "Success! PrintNode account has been linked!",
                "img_url": "/web/static/img/smile.svg",
                "type": "rainbow_man",
            }
        }

    def update_printers_list(self, domain=None, raise_on_error=False):
        if domain is None:
            domain = []
        configration = self
        if not self:
            configration = self.search(domain)
        res = True
        for conf in configration:
            limit = 50
            printers = []
            params = {"limit": limit, "dir": "asc"}
            while 1:
                printers_list = self._send_api_key_request("printers", params=params)
                if isinstance(printers_list, dict):
                    printers += [printers_list]
                    list_id = [printers_list][-1:] and [printers_list][-1:][0]["id"]
                else:
                    list_id = printers_list[-1:] and printers_list[-1:][0]["id"]
                    printers += printers_list
                if not printers_list or len(printers_list) != limit:
                    break
                params.update({"after": list_id})

            if not printers:
                continue
            installed_printers = {
                printer.printnode_id: printer for printer in conf.printer_ids
            }
            updated_printers_list = []
            for printer_directory in printers:
                printer = self.env["node.printer"]
                printnode_id = str(printer_directory.get("id"))
                if printnode_id in installed_printers:
                    printer = installed_printers[printnode_id]
                capabilities_directory = printer_directory.pop("capabilities")
                printer_values = printer._create_update_vals(
                    printer_directory, capabilities_directory, conf
                )
                updated_printers_list.append(printnode_id)
                if not printer:
                    printer = printer.create(printer_values)
                else:
                    printer.write(printer_values)

            conf.printer_ids.filtered(
                lambda record: record.printnode_id not in updated_printers_list
            ).write({"state": "deleted"})

        return res

    def action_update_printers_list(self):
        return self.update_printers_list()

    def re_establish_connection(self):
        self.write({"state": "draft"})

    def open_printer_from_config(self):
        [action] = self.env.ref("tus_printnode.action_node_printer").read()
        action["domain"] = [("config_id", "=", self.id)]
        return action

    def open_system_from_config(self):
        [action] = self.env.ref("tus_printnode.action_printnode_system").read()
        action["domain"] = [("config_id", "=", self.id)]
        return action
