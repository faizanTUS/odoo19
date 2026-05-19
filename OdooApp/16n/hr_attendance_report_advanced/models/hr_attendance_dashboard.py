# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime, timedelta
from collections import defaultdict


class HRAttendanceDashboard(models.AbstractModel):
    _name = 'hr.attendance.dashboard'
    _description = 'Attendance Dashboard Analytics'

    @api.model
    def get_dashboard_data(self, date_from=None, date_to=None, employee_ids=None, department_ids=None):
        """Get comprehensive dashboard data"""
        if not date_from:
            date_from = fields.Date.today() - timedelta(days=30)
        if not date_to:
            date_to = fields.Date.today()
        # Ensure we have date types (accept string from RPC)
        if isinstance(date_from, str):
            date_from = fields.Date.from_string(date_from)
        if isinstance(date_to, str):
            date_to = fields.Date.from_string(date_to)

        # Get configuration
        config = self.env['hr.attendance.report.config'].get_config()

        # Build domain - convert dates to datetime for check_in comparison
        date_from_dt = fields.Datetime.to_datetime(date_from) if date_from else None
        date_to_dt = fields.Datetime.to_datetime(date_to) + timedelta(days=1) - timedelta(seconds=1) if date_to else None
        
        domain = []
        if date_from_dt:
            domain.append(('check_in', '>=', date_from_dt))
        if date_to_dt:
            domain.append(('check_in', '<=', date_to_dt))
        
        if employee_ids:
            domain.append(('employee_id', 'in', employee_ids))
        if department_ids:
            domain.append(('employee_id.department_id', 'in', department_ids))
        
        # Fetch attendance records
        attendances = self.env['hr.attendance'].search(domain)
        
        # Get all employees
        employee_domain = [('active', '=', True)]
        if department_ids:
            employee_domain.append(('department_id', 'in', department_ids))
        if employee_ids:
            employee_domain.append(('id', 'in', employee_ids))
        
        all_employees = self.env['hr.employee'].search(employee_domain)
        
        # Calculate KPIs
        kpis = self._calculate_kpis(attendances, all_employees, date_from, date_to, config)
        
        # Calculate trends
        trends = self._calculate_trends(attendances, date_from, date_to)
        
        # Department comparison
        department_stats = self._calculate_department_stats(attendances, all_employees)
        
        # Punctuality analysis
        punctuality = self._calculate_punctuality(attendances, config)
        
        # Overtime analysis
        overtime = self._calculate_overtime_stats(attendances, config)
        
        # Current status
        current_status = self._get_current_status(all_employees)
        
        return {
            'kpis': kpis,
            'trends': trends,
            'department_stats': department_stats,
            'punctuality': punctuality,
            'overtime': overtime,
            'current_status': current_status,
            'config': {
                'standard_hours': config.standard_working_hours,
                'colors': config.get_status_colors(),
            }
        }

    def _calculate_kpis(self, attendances, employees, date_from, date_to, config):
        """Calculate Key Performance Indicators"""
        total_employees = len(employees)
        
        # Calculate present today
        today = fields.Date.today()
        today_attendances = attendances.filtered(
            lambda a: fields.Date.from_string(a.check_in) == today
        )
        present_today = len(set(today_attendances.mapped('employee_id.id')))
        
        # Calculate total hours
        total_hours = sum(attendances.mapped('worked_hours') or [0])
        
        # Calculate attendance rate
        total_days = (date_to - date_from).days + 1
        expected_attendance_days = total_employees * total_days
        actual_attendance_days = len(attendances)
        attendance_rate = (actual_attendance_days / expected_attendance_days * 100) if expected_attendance_days > 0 else 0
        
        # Average hours per employee
        avg_hours_per_employee = total_hours / total_employees if total_employees > 0 else 0
        
        return {
            'total_employees': total_employees,
            'present_today': present_today,
            'attendance_rate': round(attendance_rate, 2),
            'total_hours': round(total_hours, 2),
            'avg_hours_per_employee': round(avg_hours_per_employee, 2),
        }

    def _calculate_trends(self, attendances, date_from, date_to):
        """Calculate daily attendance trends"""
        trends = []
        current_date = date_from
        
        while current_date <= date_to:
            day_attendances = attendances.filtered(
                lambda a: fields.Date.from_string(a.check_in) == current_date
            )
            trends.append({
                'date': fields.Date.to_string(current_date),
                'count': len(day_attendances),
                'hours': sum(day_attendances.mapped('worked_hours') or [0]),
            })
            current_date += timedelta(days=1)
        
        return trends

    def _calculate_department_stats(self, attendances, employees):
        """Calculate department-wise statistics"""
        dept_stats = defaultdict(lambda: {
            'employees': 0,
            'attendances': 0,
            'total_hours': 0,
            'attendance_rate': 0,
        })
        
        # Count employees per department
        for emp in employees:
            dept_name = emp.department_id.name if emp.department_id else 'No Department'
            dept_stats[dept_name]['employees'] += 1
        
        # Count attendances per department
        for att in attendances:
            dept_name = att.employee_id.department_id.name if att.employee_id.department_id else 'No Department'
            dept_stats[dept_name]['attendances'] += 1
            dept_stats[dept_name]['total_hours'] += att.worked_hours or 0
        
        # Calculate attendance rates
        for dept_name, stats in dept_stats.items():
            if stats['employees'] > 0:
                stats['attendance_rate'] = round((stats['attendances'] / stats['employees']) * 100, 2)
        
        return dict(dept_stats)

    def _calculate_punctuality(self, attendances, config):
        """Calculate punctuality metrics"""
        on_time = 0
        late = 0
        early = 0
        total = len(attendances)
        
        for att in attendances:
            if att.check_in:
                check_in_time = fields.Datetime.from_string(att.check_in).time()
                # Assuming standard start time is 9:00 AM - this should be configurable
                standard_start = datetime.strptime('09:00:00', '%H:%M:%S').time()
                
                if check_in_time <= standard_start:
                    on_time += 1
                else:
                    late += 1
                
                if att.check_out:
                    check_out_time = fields.Datetime.from_string(att.check_out).time()
                    standard_end = datetime.strptime('17:00:00', '%H:%M:%S').time()
                    if check_out_time < standard_end:
                        early += 1
        
        return {
            'on_time': on_time,
            'late': late,
            'early': early,
            'total': total,
            'punctuality_rate': round((on_time / total * 100) if total > 0 else 0, 2),
        }

    def _calculate_overtime_stats(self, attendances, config):
        """Calculate overtime statistics"""
        total_overtime = 0
        overtime_days = 0
        standard_hours = config.standard_working_hours
        
        for att in attendances:
            worked_hours = att.worked_hours or 0
            if worked_hours > standard_hours:
                total_overtime += worked_hours - standard_hours
                overtime_days += 1
        
        return {
            'total_overtime': round(total_overtime, 2),
            'overtime_days': overtime_days,
            'avg_overtime_per_day': round(total_overtime / overtime_days if overtime_days > 0 else 0, 2),
        }

    def _get_current_status(self, employees):
        """Get current employee status (checked in/out)"""
        current_time = fields.Datetime.now()
        today = fields.Date.today()
        
        # Get today's attendances
        today_attendances = self.env['hr.attendance'].search([
            ('employee_id', 'in', employees.ids),
            ('check_in', '>=', fields.Datetime.to_string(today)),
        ])
        
        checked_in = []
        checked_out = []
        
        for emp in employees:
            emp_attendances = today_attendances.filtered(lambda a: a.employee_id.id == emp.id)
            if emp_attendances:
                last_attendance = emp_attendances.sorted('check_in', reverse=True)[0]
                if last_attendance.check_out:
                    checked_out.append({
                        'id': emp.id,
                        'name': emp.name,
                        'check_out': str(last_attendance.check_out) if last_attendance.check_out else None,
                    })
                else:
                    checked_in.append({
                        'id': emp.id,
                        'name': emp.name,
                        'check_in': str(last_attendance.check_in) if last_attendance.check_in else None,
                    })
            else:
                checked_out.append({
                    'id': emp.id,
                    'name': emp.name,
                    'status': 'not_checked_in',
                })
        
        return {
            'checked_in': checked_in,
            'checked_out': checked_out,
        }

