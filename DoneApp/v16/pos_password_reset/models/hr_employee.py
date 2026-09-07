# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"

    def custom_method(self, values):
        current_user_id = values.get("currentId")
        if current_user_id:
            employee_id = self.browse(int(current_user_id))
            employee_id.pin = values.get("pin")
            return True
