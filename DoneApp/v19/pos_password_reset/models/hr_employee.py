import hashlib

from odoo import models, _
from odoo.exceptions import UserError, AccessError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def pos_reset_pin(self, new_pin):
        """Reset an employee POS PIN from the POS cashier selection screen.

        Returns the SHA1 hash used by POS for local PIN checks.
        """
        self.ensure_one()
        if not self.env.user.has_group("point_of_sale.group_pos_user"):
            raise AccessError(_("You are not allowed to reset POS PINs."))
        if not new_pin or not str(new_pin).isdigit():
            raise UserError(_("PIN must only contain digits."))

        pin = str(new_pin)
        self.sudo().write({"pin": pin})
        return hashlib.sha1(pin.encode("utf8")).hexdigest()
