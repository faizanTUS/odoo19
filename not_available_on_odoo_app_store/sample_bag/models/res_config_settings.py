# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    sample_bag_buffer_qty = fields.Integer("Sample Bag Buffer Qty")

    def set_values(self):
        """
        set_values method to set the Buffer Qty in the configuration
        """
        res = super(ResConfigSettingsInherit, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "sample_bag.sample_bag_buffer_qty", self.sample_bag_buffer_qty
        )
        return res

    @api.model
    def get_values(self):
        """
        get_values method to get the Buffer Qty from configuration
        """
        res = super(ResConfigSettingsInherit, self).get_values()
        res.update(
            {
                "sample_bag_buffer_qty": int(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("sample_bag.sample_bag_buffer_qty")
                )
            }
        )
        return res
