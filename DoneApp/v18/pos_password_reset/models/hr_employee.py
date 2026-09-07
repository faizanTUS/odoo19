from odoo import models


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    def custom_method(self, values):
        current_user_id = values.get('employeeId')
        if current_user_id:
            employee_id = self.browse(int(current_user_id))
            employee_id.pin = values.get('pin')
            return True
        else:
            return False
