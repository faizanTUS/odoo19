# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class MultiApprovalTypeLine(models.Model):
    _inherit = 'multi.approval.type.line'

    special_user = fields.Selection([
        ('manager','Manager'),
        ('department','Department Manager')
    ])

    def get_user(self):
        if self.special_user == 'manager':
            employee = self.env.user.employee_ids[:1] if hasattr(self.env.user, 'employee_ids') else False
            if employee and employee.parent_id and employee.parent_id.user_id:
                return employee.parent_id.user_id.id
        return super().get_user()
