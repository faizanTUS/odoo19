# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    attendance_status_id = fields.Many2one(
        'hr.attendance.status',
        string='Attendance Status',
        help='Status of this attendance record (Present, Absent, Leave, etc.)'
    )
    break_time = fields.Float(
        string='Break Time (Hours)',
        help='Break time taken during this attendance period'
    )

