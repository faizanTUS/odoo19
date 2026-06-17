# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api


class HRAttendanceStatus(models.Model):
    _name = 'hr.attendance.status'
    _description = 'Attendance Status'
    _order = 'sequence, name'

    name = fields.Char(string='Status Name', required=True, translate=True)
    code = fields.Char(string='Short Code', required=True, size=5)
    color = fields.Char(string='Color Code', default='#6c757d', help='Hex color code for display')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    is_working = fields.Boolean(string='Counts as Working', default=True,
                                help='If checked, this status counts towards working hours')
    is_absent = fields.Boolean(string='Counts as Absent', default=False,
                               help='If checked, this status counts as absence')
    is_leave = fields.Boolean(string='Counts as Leave', default=False,
                              help='If checked, this status counts as leave')
    is_weekoff = fields.Boolean(string='Counts as Week Off', default=False,
                                help='If checked, this status counts as week off/holiday')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The status code must be unique!'),
    ]