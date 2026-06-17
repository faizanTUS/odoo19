# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, api, fields, _
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging

try:
    import pytz
except ImportError:
    pytz = None

_logger = logging.getLogger(__name__)

# Module-level debug counters (AbstractModel cannot set arbitrary self attributes)
_att_debug = {'employee': None, 'no_match': 0, 'match': 0}


class HRAttendanceReport(models.AbstractModel):
    _name = 'report.hr_attendance_report_advanced.attendance_report_template'
    _description = 'Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Get report_data from context (passed from wizard) or from data parameter
        from_ctx = self.env.context.get('report_data')
        from_data = (data or {}).get('report_data') if data else None
        report_data = from_ctx or from_data or data or {}
        # Fallback: if no report_data but we have wizard docids, build from wizard (e.g. when PDF is from Print/email and data was lost)
        if (not report_data or not report_data.get('grouped_data')) and docids:
            wizards = self.env['attendance.report.wizard'].browse(docids).exists()
            if len(wizards) == 1 and hasattr(wizards, '_prepare_report_data'):
                report_data = wizards._prepare_report_data()
                _logger.info('[PDF Step 3b] _get_report_values: fallback built report_data from wizard, len(grouped_data)=%s', len(report_data.get('grouped_data') or {}))
        _logger.info(
            '[PDF Step 3] _get_report_values: docids=%s, data keys=%s, has report_data from context=%s, from data=%s',
            docids, list((data or {}).keys()), from_ctx is not None, from_data is not None
        )
        # Extract parameters
        params = report_data.get('params', {})
        grouped_data = report_data.get('grouped_data', {})
        statistics = report_data.get('statistics', {})
        _logger.info(
            '[PDF Step 4] _get_report_values: report_data keys=%s, len(grouped_data)=%s, params keys=%s',
            list(report_data.keys()) if isinstance(report_data, dict) else 'not-dict',
            len(grouped_data) if isinstance(grouped_data, dict) else 0,
            list(params.keys()) if params else []
        )
        # Ensure docids is a list
        if not docids:
            docids = []
        if isinstance(docids, (int, str)):
            docids = [docids]

        # Get attendance statuses for color coding
        statuses = self.env['hr.attendance.status'].search([])
        status_colors = {status.id: status.color for status in statuses}

        # Prepare date range
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        date_list = self._generate_date_range(date_from, date_to)

        # web.internal_layout expects company to be a res.company record, not a string
        company = self.env.company
        if params.get('company_id'):
            company = self.env['res.company'].browse(params['company_id']).exists() or company

        # Build detailed_lines: same structure as Excel (one row per attendance)
        config = self.env['hr.attendance.report.config'].get_config()
        detailed_lines = self._build_detailed_lines(grouped_data, config, params)

        # Report type: detailed = only detailed table; summary = only matrix; combined = both
        report_type = params.get('report_type', 'combined')
        report_type_labels = {'detailed': 'Detailed Report', 'summary': 'Summary Report', 'combined': 'Combined Report'}
        report_type_label = report_type_labels.get(report_type, report_type)

        # Prepare report data structure (template expects date_from, date_to, company, show_hours, show_overtime, report_type at top level)
        report_data = {
            'params': params,
            'report_type': report_type,
            'report_type_label': report_type_label,
            'date_from': params.get('date_from'),
            'date_to': params.get('date_to'),
            'company': company,  # Record for layout; use company.name in template for display
            'show_hours': params.get('show_hours', True),
            'show_overtime': params.get('show_overtime', True),
            'date_list': date_list,
            'status_colors': status_colors,
            'employees_data': [],
            'detailed_lines': detailed_lines,
            'statistics': statistics,
            'summary': self._prepare_summary(grouped_data, date_list),
        }

        # Process grouped data for the report
        params = report_data.get('params', {})
        date_from = params.get('date_from')
        date_to = params.get('date_to')

        for employee_id, data in grouped_data.items():
            employee = self._ensure_employee_record(data.get('employee'))
            if not employee or not employee.exists():
                # Print/Download path: employee from context can be from another env; re-browse by id in current env
                try:
                    employee = self.env['hr.employee'].browse(int(employee_id)).exists()
                except (TypeError, ValueError):
                    employee = self.env['hr.employee']
            if not employee or not employee.exists():
                continue

            # Always re-fetch attendances from DB when we have date range: context passes serialized data
            # (no real records), so _attendance_record_or_dict returns None and all show as (invalid).
            if date_from and date_to:
                domain = [
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', date_from),
                    ('check_in', '<=', date_to),
                ]
                attendances_list = self.env['hr.attendance'].search(domain, order='check_in')
            else:
                attendances_list = data.get('attendances', []) or []

            # Reset debug counters for this employee (for Step 2c no-match / match logs)
            _att_debug['employee'] = employee.name
            _att_debug['no_match'] = 0
            _att_debug['match'] = 0

            # --- [ATT_REPORT] Step 2b: Show attendance check_in dates (in employee TZ) and worked_hours ---
            att_dates_in_tz = []
            for idx, att in enumerate(attendances_list[:15]):
                rec = self._attendance_record_or_dict(att)
                if rec is None:
                    att_dates_in_tz.append('(invalid)')
                    continue
                ci = rec.check_in if hasattr(rec, 'check_in') else (rec.get('check_in') if isinstance(rec, dict) else None)
                emp = getattr(rec, 'employee_id', None) if hasattr(rec, 'employee_id') else None
                ad = self._check_in_to_date(ci, emp) if ci else None
                wh = self._attendance_worked_hours(rec)
                att_dates_in_tz.append('%s->%s h=%.2f' % (ci, ad, wh))

            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'department': employee.department_id.name if employee.department_id else '',
                'job_title': employee.job_title or '',
                'attendance_days': [],
                'summary': {
                    'total_days': 0,
                    'total_hours': 0,
                    'status_count': {'present': 0, 'half_day': 0, 'absent': 0, 'on_leave': 0, 'week_off': 0},
                    # 'overtime_hours': 0,
                }
            }

            # Process each day's attendance (use re-fetched list so present days show P, not A)
            for date in date_list:
                day_attendance = self._get_attendance_for_date(attendances_list, date, _debug_employee=employee.name)
                employee_data['attendance_days'].append(day_attendance)

            # --- [ATT_REPORT] Step 3: Sample of attendance_days (first 5 weekdays, first 2 weekend) ---
            sample_days = []
            for i, day in enumerate(employee_data['attendance_days']):
                if len(sample_days) >= 7:
                    break
                d = day.get('date')
                code = (day.get('status_code') or '').strip()
                h = day.get('hours', 0)
                sample_days.append('%s->%s h=%.1f' % (d, code, h))

            # Fill Present, Half Day, Absent, On Leave, Week Off, Overtime from computed attendance_days
            total_hours = 0
            # overtime_hours = 0
            for day in employee_data['attendance_days']:
                code = (day.get('status_code') or '').strip().upper()
                if code in ('P',):
                    employee_data['summary']['status_count']['present'] += 1
                elif code in ('H/F', 'H'):
                    employee_data['summary']['status_count']['half_day'] += 1
                elif code == 'A':
                    employee_data['summary']['status_count']['absent'] += 1
                elif code == 'L':
                    employee_data['summary']['status_count']['on_leave'] += 1
                elif code == 'WO':
                    employee_data['summary']['status_count']['week_off'] += 1
                total_hours += day.get('hours', 0) or 0
                # overtime_hours += day.get('overtime', 0) or 0
            employee_data['summary']['total_days'] = len(attendances_list)
            employee_data['summary']['total_hours'] = total_hours or data.get('total_hours', 0) or sum(self._attendance_worked_hours(a) for a in attendances_list)
            # employee_data['summary']['overtime_hours'] = overtime_hours or self._calculate_overtime(attendances_list, employee)

            report_data['employees_data'].append(employee_data)

        # Add status totals to summary (Present, Half Day, Absent, On Leave, Week Off) from employees_data
        for emp in report_data['employees_data']:
            sc = emp.get('summary', {}).get('status_count', {})
            report_data['summary']['total_present'] = report_data['summary'].get('total_present', 0) + sc.get('present', 0)
            report_data['summary']['total_half_day'] = report_data['summary'].get('total_half_day', 0) + sc.get('half_day', 0)
            report_data['summary']['total_absent'] = report_data['summary'].get('total_absent', 0) + sc.get('absent', 0)
            report_data['summary']['total_on_leave'] = report_data['summary'].get('total_on_leave', 0) + sc.get('on_leave', 0)
            report_data['summary']['total_week_off'] = report_data['summary'].get('total_week_off', 0) + sc.get('week_off', 0)
        th = sum(e.get('summary', {}).get('total_hours', 0) for e in report_data['employees_data'])
        # to = sum(e.get('summary', {}).get('overtime_hours', 0) for e in report_data['employees_data'])
        if th > 0 :
            report_data['summary']['total_hours'] = th
            # report_data['summary']['total_overtime'] = to

        _logger.info(
            '[PDF Step 5] _get_report_values: employees_data len=%s',
            len(report_data['employees_data'])
        )
        # Ensure wizard records exist and are accessible
        if docids:
            docs = self.env['attendance.report.wizard'].browse(docids).exists()
            if not docs:
                # If wizard records don't exist, create a dummy recordset for template
                docs = self.env['attendance.report.wizard']
        else:
            docs = self.env['attendance.report.wizard']
        report_data['docs'] = docs

        # --- [ATT_REPORT] Step 5: Final report data ---
        return report_data

    def _generate_date_range(self, date_from, date_to):
        date_list = []
        current_date = fields.Date.from_string(date_from)
        end_date = fields.Date.from_string(date_to)

        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        return date_list

    def _check_in_to_date(self, check_in, employee=None):
        """Return the calendar date of check_in in employee (or company) timezone.
        check_in is stored in UTC; without TZ conversion, .date() can be wrong for other timezones.
        """
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
            # Odoo stores datetimes naive UTC
            if check_in.tzinfo is None:
                check_in_utc = pytz.utc.localize(check_in)
            else:
                check_in_utc = check_in
            check_in_local = check_in_utc.astimezone(tz)
            return check_in_local.date()
        except Exception:
            return check_in.date()

    def _get_attendance_for_date(self, attendances, date, _debug_employee=None):
        # Find attendance for specific date (attendances can be records, dicts, or ids from serialized context)
        # check_in is stored in UTC -> convert to employee TZ to get calendar date so we match report dates
        _match_found = False
        _match_info = None
        for att in attendances or []:
            attendance = self._attendance_record_or_dict(att)
            if attendance is None:
                continue
            check_in = attendance.check_in if hasattr(attendance, 'check_in') else (attendance.get('check_in') if isinstance(attendance, dict) else None)
            if not check_in:
                continue
            employee = getattr(attendance, 'employee_id', None) if hasattr(attendance, 'employee_id') else None
            att_date = self._check_in_to_date(check_in, employee)
            if att_date is None:
                if hasattr(check_in, 'date'):
                    att_date = check_in.date()
                elif isinstance(check_in, str) and len(check_in) >= 10:
                    att_date = fields.Date.from_string(check_in[:10])
                else:
                    att_date = fields.Date.from_string(str(check_in))
            # Compare date part only
            if hasattr(date, 'day') and hasattr(att_date, 'day'):
                if (att_date.year, att_date.month, att_date.day) != (date.year, date.month, date.day):
                    continue
            elif att_date != date:
                continue
            _match_found = True
            status = None
            if hasattr(attendance, 'attendance_status_id') and attendance.attendance_status_id:
                status = attendance.attendance_status_id
            # Only use record status for Leave/Week Off; else derive from worked hours so we show P / H/F not A
            hours = self._attendance_worked_hours(attendance)
            if status and (getattr(status, 'is_leave', False) or getattr(status, 'is_weekoff', False)):
                pass  # keep Leave / Week Off
            else:
                config = self.env['hr.attendance.report.config'].get_config()
                half_day = getattr(config, 'half_day_threshold', None) or 4.0
                if hours >= half_day:
                    status = self.env.ref('hr_attendance_report_advanced.status_present')
                elif hours > 0:
                    status = self.env.ref('hr_attendance_report_advanced.status_half_day')
                else:
                    status = status or self.env.ref('hr_attendance_report_advanced.status_absent')
            status_code = getattr(status, 'code', None) or ''
            _match_info = (date, att_date, hours, status_code)
            # --- [ATT_REPORT] Step 2c: Log when we MATCH (first 3 per employee) ---
            if _debug_employee and _debug_employee == _att_debug.get('employee'):
                _att_debug['match'] = _att_debug.get('match', 0) + 1
            # overtime = getattr(attendance, 'overtime_hours', None) or (attendance.get('overtime_hours', 0) if isinstance(attendance, dict) else 0)
            breaks = getattr(attendance, 'break_time', None) or (attendance.get('break_time', 0) if isinstance(attendance, dict) else 0)
            check_out = attendance.check_out if hasattr(attendance, 'check_out') else (attendance.get('check_out') if isinstance(attendance, dict) else None)
            return {
                'date': date,
                'status': status,
                'status_code': status_code,
                'color': getattr(status, 'color', None) or '#6c757d',
                'check_in': check_in,
                'check_out': check_out,
                'hours': hours,
                # 'overtime': overtime,
                'breaks': breaks,
            }

        # No attendance found for this date
        default_status = self._get_default_status_for_date(date)
        default_code = getattr(default_status, 'code', None) or ''
        # --- [ATT_REPORT] Step 2c: Log when we miss (first 3 weekdays only to avoid spam) ---
        if _debug_employee and _debug_employee == _att_debug.get('employee') and date.weekday() < 5 and not _match_found:
            _att_debug['no_match'] = _att_debug.get('no_match', 0) + 1
        return {
            'date': date,
            'status': default_status,
            'status_code': default_code,
            'color': getattr(default_status, 'color', None) or '#6c757d',
            'check_in': None,
            'check_out': None,
            'hours': 0,
            # 'overtime': 0,
            'breaks': 0,
        }

    def _get_default_status_for_date(self, date):
        # Determine default status (weekend, holiday, absent)
        if date.weekday() >= 5:  # Weekend
            return self.env.ref('hr_attendance_report_advanced.status_weekoff')
        # Check if it's a holiday
        # This would require integration with hr_holidays
        return self.env.ref('hr_attendance_report_advanced.status_absent')

    def _ensure_employee_record(self, employee):
        """Ensure employee is a record, not a string/dict (handles serialization)."""
        if employee is None:
            return self.env['hr.employee']  # Empty recordset
        if isinstance(employee, models.Model) and employee._name == 'hr.employee':
            # Already a record
            return employee
        if isinstance(employee, str):
            # If it's a string, try to parse as ID
            try:
                emp_id = int(employee)
                return self.env['hr.employee'].browse(emp_id)
            except (ValueError, TypeError):
                # If not a valid ID, search by name
                emp = self.env['hr.employee'].search([('name', '=', employee)], limit=1)
                return emp if emp else self.env['hr.employee']
        if isinstance(employee, dict):
            # If it's a dict (serialized), browse by ID
            emp_id = employee.get('id') or employee.get('employee_id')
            if emp_id:
                return self.env['hr.employee'].browse(emp_id)
        # Fallback: try to browse by assuming it's an ID
        try:
            return self.env['hr.employee'].browse(employee)
        except (TypeError, ValueError):
            return self.env['hr.employee']  # Return empty recordset

    def _attendance_worked_hours(self, attendance):
        """Get worked_hours from attendance (record, dict, or id from serialized context)."""
        if hasattr(attendance, 'worked_hours'):
            return float(attendance.worked_hours or 0)
        if isinstance(attendance, dict):
            return float(attendance.get('worked_hours') or 0)
        if isinstance(attendance, (int, str)):
            try:
                rec = self.env['hr.attendance'].browse(int(attendance)).exists()
                return float(rec.worked_hours or 0) if rec else 0.0
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    def _attendance_record_or_dict(self, attendance):
        """Return attendance as a record if possible, else keep as dict. For iteration over mixed list."""
        if hasattr(attendance, 'check_in'):
            return attendance
        if isinstance(attendance, (int, str)):
            try:
                return self.env['hr.attendance'].browse(int(attendance)).exists()
            except (TypeError, ValueError):
                return None
        return attendance if isinstance(attendance, dict) else None

    def _calculate_overtime(self, attendances, employee):
        # Calculate overtime based on employee contract and attendance
        employee = self._ensure_employee_record(employee)
        total_overtime = 0
        # Handle empty recordset or missing standard_hours
        if not employee or not employee.exists():
            standard_hours = 8.0  # Default to 8 hours
        else:
            standard_hours = employee.standard_hours or 8.0  # Default to 8 hours

        for attendance in attendances or []:
            worked_hours = self._attendance_worked_hours(attendance)
            if worked_hours > standard_hours:
                total_overtime += worked_hours - standard_hours

        return total_overtime

    def _prepare_summary(self, grouped_data, date_list):
        summary = {
            'total_employees': len(grouped_data),
            'total_days': len(date_list) * len(grouped_data),
            'total_hours': 0,
            'total_overtime': 0,
            'status_summary': defaultdict(int),
            'department_summary': defaultdict(lambda: defaultdict(int)),
        }

        for employee_id, data in grouped_data.items():
            employee = self._ensure_employee_record(data.get('employee'))
            if not employee or not employee.exists():
                try:
                    employee = self.env['hr.employee'].browse(int(employee_id)).exists()
                except (TypeError, ValueError):
                    employee = self.env['hr.employee']
            if not employee or not employee.exists():
                continue
            summary['total_hours'] += data.get('total_hours', 0)
            summary['total_overtime'] += self._calculate_overtime(data.get('attendances', []), employee)

            # Department summary
            dept_name = employee.department_id.name if employee.department_id else 'No Department'
            summary['department_summary'][dept_name]['employees'] += 1
            summary['department_summary'][dept_name]['hours'] += data['total_hours']

            # Status summary
            for status_id, count in data['status_count'].items():
                summary['status_summary'][status_id] += count

        return summary

    def _build_detailed_lines(self, grouped_data, config, params=None):
        """Build a flat list of lines (one per attendance) matching Excel Detailed Report.
        Each line: employee_name, department, date, check_in, check_out, hours, overtime, status.
        When attendances are missing (e.g. after context serialization), re-fetch from DB.
        """
        detailed_lines = []
        params = params or {}
        standard_hours = getattr(config, 'standard_working_hours', None) or 8.0
        half_day_threshold = getattr(config, 'half_day_threshold', None) or 4.0
        date_from = params.get('date_from')
        date_to = params.get('date_to')

        for employee_id, data in grouped_data.items():
            employee = self._ensure_employee_record(data.get('employee'))
            if not employee or not employee.exists():
                try:
                    employee = self.env['hr.employee'].browse(int(employee_id)).exists()
                except (TypeError, ValueError):
                    employee = self.env['hr.employee']
            if not employee or not employee.exists():
                continue
            emp_name = employee.name
            dept_name = employee.department_id.name if employee.department_id else ''

            # Always re-fetch from DB when we have date range (context passes serialized data, not real records)
            if date_from and date_to:
                domain = [
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', date_from),
                    ('check_in', '<=', date_to),
                ]
                attendances_list = self.env['hr.attendance'].search(domain, order='check_in')
            else:
                attendances_list = data.get('attendances', []) or []

            for att in attendances_list:
                attendance = self._attendance_record_or_dict(att)
                if attendance is None:
                    continue
                check_in = None
                if hasattr(attendance, 'check_in'):
                    check_in = attendance.check_in
                elif isinstance(attendance, dict):
                    check_in = attendance.get('check_in')
                if not check_in:
                    continue
                check_out = None
                if hasattr(attendance, 'check_out'):
                    check_out = attendance.check_out
                elif isinstance(attendance, dict):
                    check_out = attendance.get('check_out')
                worked_hours = self._attendance_worked_hours(attendance)
                # overtime = max(0.0, worked_hours - standard_hours)
                # Calendar date in employee TZ (check_in is UTC)
                att_date = self._check_in_to_date(check_in, employee)
                if att_date is None and check_in:
                    if hasattr(check_in, 'date'):
                        att_date = check_in.date()
                    elif isinstance(check_in, str) and len(check_in) >= 10:
                        att_date = fields.Date.from_string(check_in[:10])
                    else:
                        att_date = fields.Date.from_string(str(check_in))
                # Status: derive from worked_hours so we show P / H/F / A (not only A)
                status_record = None
                if hasattr(attendance, 'attendance_status_id') and attendance.attendance_status_id:
                    status_record = attendance.attendance_status_id
                elif isinstance(attendance, dict) and attendance.get('attendance_status_id'):
                    sid = attendance['attendance_status_id']
                    if isinstance(sid, (list, tuple)) and len(sid) >= 1:
                        sid = sid[0] if sid else None
                    if sid:
                        status_record = self.env['hr.attendance.status'].browse(sid).exists()
                # Use status from record only if it's Leave/Week Off/Holiday; else derive from hours so we show P / H/F / A
                if status_record and (getattr(status_record, 'is_leave', False) or getattr(status_record, 'is_weekoff', False)):
                    status_text = status_record.name
                    status_code = getattr(status_record, 'code', None) or status_text[:1]
                else:
                    # Derive from worked_hours: Present (P), Half Day (H/F), Absent (A)
                    if worked_hours >= half_day_threshold:
                        status_text = 'Present'
                        status_code = 'P'
                    elif worked_hours > 0:
                        status_text = 'Half Day'
                        status_code = 'H/F'
                    else:
                        status_text = 'Absent'
                        status_code = 'A'
                check_in_str = check_in.strftime('%H:%M') if hasattr(check_in, 'strftime') else str(check_in)
                check_out_str = check_out.strftime('%H:%M') if check_out and hasattr(check_out, 'strftime') else (str(check_out) if check_out else '')
                date_str = att_date.strftime('%Y-%m-%d') if att_date and hasattr(att_date, 'strftime') else (str(att_date) if att_date else '')
                detailed_lines.append({
                    'employee': emp_name,
                    'department': dept_name,
                    'date': att_date,
                    'date_str': date_str,
                    'check_in': check_in_str,
                    'check_out': check_out_str,
                    'hours': round(worked_hours, 2),
                    # 'overtime': round(overtime, 2),
                    'status': status_text,
                    'status_code': status_code,
                })
        return detailed_lines