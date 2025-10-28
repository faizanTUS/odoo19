import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PrintNodeSystem(models.Model):
    _name = "printnode.system"
    _description = "PrintNode system"

    name = fields.Char("Name", required=True, help="Name of Computer")
    state = fields.Char("State", help="Current Status of Computer")
    inet = fields.Char("IPv4")
    inet6 = fields.Char("IPv6")
    hostname = fields.Char("Host Name")
    printnode_id = fields.Char("PrintNode ID", copy=False)
    config_id = fields.Many2one(
        "printnode.config",
        string="Configration",
        copy=False,
        help="Account associated with this computer.",
        ondelete="cascade",
    )
    printer_ids = fields.One2many("node.printer", "system_id", string="Printers")

    _sql_constraints = [
        (
            "unique_printnode_id_key",
            "unique(printnode_id)",
            "Computer already available!",
        ),
    ]

    def _create_or_update_system(self, system_dict, config_id):
        for unwanted_data in ["createTimestamp", "jre", "version"]:
            if (
                system_dict.get(unwanted_data, False)
                or system_dict.get(unwanted_data, False) is None
            ):
                del system_dict[unwanted_data]
        printnode_id = system_dict.get("id")
        system_dict.update(
            {"printnode_id": str(printnode_id), "config_id": config_id.id}
        )
        system = self.search(
            [("printnode_id", "=", printnode_id), ("config_id", "=", config_id.id)],
            limit=1,
        )
        if system:
            system.write(system_dict)
        else:
            system = system.create(system_dict)
        return system
