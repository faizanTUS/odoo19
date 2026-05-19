# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime, timedelta


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    # Attendance-related fields
    attendance_alert_recipients = fields.Many2many(
        'res.partner',
        'hr_attendance_dept_alert_recipient_rel',
        'dept_alert_id',
        'partner_alert_id',
        string='Attendance Alert Recipients',
        help='People who will receive attendance alerts for this department'
    )

    attendance_report_recipients = fields.Many2many(
        'res.partner',
        'hr_attendance_dept_report_recipient_rel',
        'dept_report_id',
        'partner_report_id',
        string='Report Recipients',
        help='People who will receive regular attendance reports for this department'
    )

    standard_hours = fields.Float(
        string='Standard Working Hours',
        default=8.0,
        help='Standard working hours per day for this department'
    )

    overtime_threshold = fields.Float(
        string='Overtime Threshold',
        default=1.0,
        help='Hours after which overtime is calculated (e.g., 1.0 = anything over standard hours)'
    )

    attendance_summary = fields.Text(
        string='Attendance Summary',
        compute='_compute_attendance_summary',
        help='Summary of attendance for the current month'
    )

    def _compute_attendance_summary(self):
        for department in self:
            # Calculate summary for the current month
            today = fields.Date.today()
            first_day = today.replace(day=1)
            last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Get department employees
            employees = self.env['hr.employee'].search([('department_id', '=', department.id)])

            if not employees:
                department.attendance_summary = "No employees in this department"
                continue

            # Get attendance records for department employees
            attendances = self.env['hr.attendance'].search([
                ('employee_id', 'in', employees.ids),
                ('check_in', '>=', first_day),
                ('check_in', '<=', last_day),
            ])

            # Calculate statistics
            present_count = len([a for a in attendances if a.attendance_status_id.is_working])
            absent_count = len([a for a in attendances if a.attendance_status_id.is_absent])
            leave_count = len([a for a in attendances if a.attendance_status_id.is_leave])
            total_hours = sum(a.worked_hours for a in attendances if a.worked_hours)

            department.attendance_summary = (
                f"Employees: {len(employees)}\n"
                f"Present: {present_count} days\n"
                f"Absent: {absent_count} days\n"
                f"Leave: {leave_count} days\n"
                f"Total Hours: {round(total_hours, 1)}"
            )

    def action_view_department_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Attendance Report - {self.name}',
            'res_model': 'attendance.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_department_ids': [(6, 0, [self.id])],
                'default_date_from': fields.Date.to_string(fields.Date.today().replace(day=1)),
                'default_date_to': fields.Date.to_string(
                    (fields.Date.today().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)),
            },
        }

    def action_send_department_report(self):
        """Action to send attendance report for this department"""
        self.ensure_one()
        # This would typically open a wizard to configure and send the report
        return {
            'type': 'ir.actions.act_window',
            'name': f'Send Attendance Report - {self.name}',
            'res_model': 'attendance.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_department_ids': [(6, 0, [self.id])],
                'default_send_email': True,
                'default_recipient_ids': [(6, 0, self.attendance_report_recipients.ids)],
            },
        }