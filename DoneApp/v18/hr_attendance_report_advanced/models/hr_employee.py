# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime, timedelta


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    attendance_status_ids = fields.One2many('hr.attendance', 'employee_id',
                                            string='Attendance Records')
    standard_hours = fields.Float(string='Standard Working Hours', default=8.0,
                                  help='Standard working hours per day for overtime calculation')
    attendance_summary = fields.Text(string='Attendance Summary', compute='_compute_attendance_summary')

    def _compute_attendance_summary(self):
        for employee in self:
            # Calculate summary for the current month
            today = fields.Date.today()
            first_day = today.replace(day=1)
            last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', first_day),
                ('check_in', '<=', last_day),
            ])

            present_days = len([a for a in attendances if a.attendance_status_id.is_working])
            absent_days = len([a for a in attendances if a.attendance_status_id.is_absent])
            leave_days = len([a for a in attendances if a.attendance_status_id.is_leave])

            employee.attendance_summary = f"Present: {present_days} days, Absent: {absent_days} days, Leave: {leave_days} days"

    def action_view_attendance_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Attendance Report - {self.name}',
            'res_model': 'attendance.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_ids': [(6, 0, [self.id])],
                'default_date_from': fields.Date.to_string(fields.Date.today().replace(day=1)),
                'default_date_to': fields.Date.to_string(
                    (fields.Date.today().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)),
            },
        }
    
    def action_view_attendance_records(self):
        """Open attendance records using our custom action without gantt"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Attendance Records - {self.name}',
            'res_model': 'hr.attendance',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'search_default_employee_id': self.id,
            },
        }