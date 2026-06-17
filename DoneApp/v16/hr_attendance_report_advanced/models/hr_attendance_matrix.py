# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from collections import defaultdict
import html
import json

try:
    import pytz
except ImportError:
    pytz = None


def _json_serial(obj):
    """Convert datetime/date to string for JSON; pass through others."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError('Object of type %s is not JSON serializable' % type(obj).__name__)


class HRAttendanceMatrix(models.TransientModel):
    _name = 'hr.attendance.matrix'
    _description = 'Attendance Matrix View'

    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: fields.Date.today() - timedelta(days=30))
    date_to = fields.Date(string='To Date', required=True,
                          default=lambda self: fields.Date.today())
    
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    department_ids = fields.Many2many('hr.department', string='Departments')
    
    matrix_data = fields.Text(string='Matrix Data', compute='_compute_matrix_data')
    matrix_html = fields.Html(string='Matrix Table', compute='_compute_matrix_html', sanitize=False)

    @api.depends('date_from', 'date_to', 'employee_ids', 'department_ids')
    def _compute_matrix_data(self):
        """Compute matrix data for visual display"""
        for record in self:
            data = record._get_matrix_data()
            record.matrix_data = json.dumps(data, default=_json_serial)

    @api.depends('date_from', 'date_to', 'employee_ids', 'department_ids')
    def _compute_matrix_html(self):
        """Compute matrix as HTML for form display (field must exist for views that reference it)."""
        for record in self:
            try:
                record.matrix_html = record._build_matrix_html()
            except Exception:
                record.matrix_html = '<p class="text-muted">Set dates and filters, then click View Matrix or refresh.</p>'
    
    def _get_matrix_data(self):
        """Get matrix data structure"""
        # Build domain - convert dates to datetime for check_in comparison
        date_from_dt = fields.Datetime.to_datetime(self.date_from)
        date_to_dt = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1) - timedelta(seconds=1)
        
        domain = [
            ('check_in', '>=', date_from_dt),
            ('check_in', '<=', date_to_dt),
        ]
        
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        elif self.department_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))
        
        # Fetch attendance records
        attendances = self.env['hr.attendance'].search(domain)
        
        # Get employees
        employee_domain = [('active', '=', True)]
        if self.employee_ids:
            employee_domain.append(('id', 'in', self.employee_ids.ids))
        elif self.department_ids:
            employee_domain.append(('department_id', 'in', self.department_ids.ids))
        
        employees = self.env['hr.employee'].search(employee_domain)
        
        # Use same config as PDF for half_day threshold; colors come from hr.attendance.status (match PDF)
        config = self.env['hr.attendance.report.config'].get_config()
        
        # Generate date range
        date_list = []
        current_date = self.date_from
        while current_date <= self.date_to:
            date_list.append(fields.Date.to_string(current_date))
            current_date += timedelta(days=1)
        
        # Build matrix
        matrix = []
        for employee in employees:
            employee_row = {
                'employee_id': employee.id,
                'employee_name': employee.name,
                'department': employee.department_id.name if employee.department_id else '',
                'dates': {},
            }
            
            for date_str in date_list:
                date_obj = fields.Date.from_string(date_str)
                emp_id = employee.id
                day_attendance = attendances.filtered(
                    lambda a, eid=emp_id, d=date_obj: a.employee_id.id == eid
                    and self._check_in_to_date(a.check_in, a.employee_id) == d
                )
                
                if day_attendance:
                    att = day_attendance[0]
                    status_record = self._get_status_record_for_attendance(att, config)
                    check_in = att.check_in
                    check_out = att.check_out
                    color = getattr(status_record, 'color', None) or '#6c757d'
                    employee_row['dates'][date_str] = {
                        'status': getattr(status_record, 'code', None) or '',
                        'color': color,
                        'hours': att.worked_hours or 0,
                        'check_in': check_in.isoformat() if hasattr(check_in, 'isoformat') else str(check_in) if check_in else None,
                        'check_out': check_out.isoformat() if hasattr(check_out, 'isoformat') else str(check_out) if check_out else None,
                    }
                else:
                    # Weekend/holiday -> Week Off; weekday no attendance -> Absent (same as PDF)
                    status_record = self._get_default_status_record_for_date(date_obj)
                    color = getattr(status_record, 'color', None) or '#6c757d'
                    employee_row['dates'][date_str] = {
                        'status': getattr(status_record, 'code', None) or '',
                        'color': color,
                        'hours': 0,
                        'check_in': None,
                        'check_out': None,
                    }
            
            matrix.append(employee_row)
        
        return {
            'dates': date_list,
            'employees': matrix,
        }

    def _build_matrix_html(self):
        """Build matrix table HTML from _get_matrix_data()."""
        data = self._get_matrix_data()
        dates = data.get('dates', [])
        employees = data.get('employees', [])
        if not dates or not employees:
            return '<p class="text-muted">No data available for the selected period.</p>'
        parts = [
            '<table class="matrix-table table table-sm table-bordered table-responsive">'
            '<thead><tr><th>Employee</th><th>Department</th>'
        ]
        for date_str in dates:
            try:
                dt = fields.Date.from_string(date_str)
                day_name = dt.strftime('%a')
                day_num = dt.day
            except Exception:
                day_name = date_str[:3] if len(date_str) >= 3 else ''
                day_num = date_str.split('-')[-1] if '-' in date_str else date_str
            parts.append('<th title="%s">%s<br/>%s</th>' % (
                html.escape(date_str), html.escape(day_name), day_num
            ))
        parts.append('</tr></thead><tbody>')
        for emp in employees:
            name = html.escape(emp.get('employee_name') or '')
            dept = html.escape(emp.get('department') or '')
            parts.append('<tr><td>%s</td><td>%s</td>' % (name, dept))
            emp_dates = emp.get('dates') or {}
            for date_str in dates:
                day = emp_dates.get(date_str) or {}
                color = day.get('color') or '#6c757d'
                hours = day.get('hours') or 0
                check_in = day.get('check_in') or 'N/A'
                check_out = day.get('check_out') or 'N/A'
                if isinstance(check_in, str) and len(check_in) > 19:
                    check_in = check_in[:19]
                if isinstance(check_out, str) and len(check_out) > 19:
                    check_out = check_out[:19]
                title = 'Status: %s | Hours: %s | Check In: %s | Check Out: %s' % (
                    html.escape(str(day.get('status', ''))),
                    hours,
                    html.escape(str(check_in)),
                    html.escape(str(check_out)),
                )
                parts.append(
                    '<td class="matrix-cell" style="background-color:%s" title="%s">' % (
                        html.escape(color), title
                    )
                )
                if hours > 0:
                    parts.append('<span class="hours-badge">%.1fh</span>' % hours)
                parts.append('</td>')
            parts.append('</tr>')
        parts.append('</tbody></table>')
        return ''.join(parts)
    
    def _get_status_record_for_attendance(self, attendance, config):
        """Return hr.attendance.status record (same logic as PDF report for color match)."""
        worked_hours = attendance.worked_hours or 0
        status = attendance.attendance_status_id
        # Use record status for Leave/Week Off; else derive from worked hours (P / H/F / A)
        if status and (getattr(status, 'is_leave', False) or getattr(status, 'is_weekoff', False)):
            return status
        half_day = getattr(config, 'half_day_threshold', None) or 4.0
        standard_hours = getattr(config, 'standard_working_hours', None) or 8.0
        if worked_hours >= standard_hours:
            return self.env.ref('hr_attendance_report_advanced.status_present')
        if worked_hours >= half_day:
            return self.env.ref('hr_attendance_report_advanced.status_half_day')
        if status:
            return status
        return self.env.ref('hr_attendance_report_advanced.status_absent')
    
    def _get_default_status_record_for_date(self, date_obj):
        """Return hr.attendance.status record for date with no attendance (same as PDF)."""
        if date_obj.weekday() >= 5:  # Weekend -> Week Off
            return self.env.ref('hr_attendance_report_advanced.status_weekoff')
        # Weekday, no attendance -> Absent
        return self.env.ref('hr_attendance_report_advanced.status_absent')

    def _check_in_to_date(self, check_in, employee=None):
        """Return the calendar date of check_in in employee (or company) timezone."""
        if not check_in:
            return None
        if isinstance(check_in, str):
            return fields.Date.from_string(check_in[:10]) if len(check_in) >= 10 else None
        if not hasattr(check_in, 'date'):
            return None
        if not pytz:
            return check_in.date()
        tz_name = 'UTC'
        if employee and hasattr(employee, '_get_tz'):
            try:
                name = employee._get_tz()
                if name:
                    tz_name = name
            except Exception:
                pass
        try:
            tz = pytz.timezone(tz_name or 'UTC')
            if check_in.tzinfo is None:
                check_in_utc = pytz.utc.localize(check_in)
            else:
                check_in_utc = check_in
            check_in_local = check_in_utc.astimezone(tz)
            return check_in_local.date()
        except Exception:
            return check_in.date()

    def get_matrix_data_json(self):
        """Return matrix data as dict for the current record (for RPC/frontend)."""
        self.ensure_one()
        if not self.matrix_data:
            return self._get_matrix_data()
        try:
            return json.loads(self.matrix_data)
        except (TypeError, ValueError):
            return self._get_matrix_data()
    
    def action_view_matrix_page(self):
        """Open matrix table in a new tab (avoids form field dependency)."""
        self.ensure_one()
        base_url = self.get_base_url()
        url = '%s/attendance/matrix/view?matrix_id=%s' % (base_url.rstrip('/'), self.id)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
            'name': 'Attendance Matrix',
        }

    def action_open_matrix_view(self):
        """Open matrix view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Matrix',
            'res_model': 'hr.attendance.matrix',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
            'views': [(self.env.ref('hr_attendance_report_advanced.view_attendance_matrix').id, 'form')],
        }

