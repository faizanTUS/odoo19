# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo import fields
import json
import base64
from datetime import datetime, timedelta


class AttendanceReportController(http.Controller):

    @http.route('/attendance/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, date_from=None, date_to=None, employee_ids=None, department_ids=None, **kwargs):
        """Get dashboard data via JSON API"""
        try:
            # Parse string dates from frontend (e.g. "2025-12-01" or "01/12/2025")
            if date_from and isinstance(date_from, str):
                date_from = fields.Date.from_string(date_from)
            if date_to and isinstance(date_to, str):
                date_to = fields.Date.from_string(date_to)
            if employee_ids and not isinstance(employee_ids, list):
                employee_ids = [employee_ids] if employee_ids else None
            if department_ids and not isinstance(department_ids, list):
                department_ids = [department_ids] if department_ids else None

            dashboard_model = request.env['hr.attendance.dashboard']
            data = dashboard_model.get_dashboard_data(
                date_from=date_from,
                date_to=date_to,
                employee_ids=employee_ids,
                department_ids=department_ids,
            )
            return {
                'status': 'success',
                'data': data,
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/attendance/dashboard/export', type='http', auth='user')
    def export_dashboard_excel(self, **kwargs):
        """Export dashboard data to Excel"""
        try:
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            employee_ids = kwargs.get('employee_ids')
            department_ids = kwargs.get('department_ids')
            
            if employee_ids:
                employee_ids = [int(x) for x in employee_ids.split(',') if x]
            if department_ids:
                department_ids = [int(x) for x in department_ids.split(',') if x]
            
            # Get dashboard data
            dashboard_model = request.env['hr.attendance.dashboard']
            data = dashboard_model.get_dashboard_data(
                date_from=date_from,
                date_to=date_to,
                employee_ids=employee_ids,
                department_ids=department_ids,
            )
            
            # Generate Excel (would use xlsxwriter)
            # For now, return JSON
            return request.make_response(
                json.dumps(data),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Content-Disposition', 'attachment; filename="dashboard_export.json"'),
                ]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/attendance/employee/status', type='json', auth='user')
    def get_employee_status(self, employee_id=None, **kwargs):
        """Get current status of employee"""
        try:
            if not employee_id:
                return {'status': 'error', 'message': 'Employee ID required'}
            
            employee = request.env['hr.employee'].browse(employee_id)
            if not employee.exists():
                return {'status': 'error', 'message': 'Employee not found'}
            
            today = fields.Date.today()
            attendance = request.env['hr.attendance'].search([
                ('employee_id', '=', employee_id),
                ('check_in', '>=', fields.Datetime.to_string(today)),
            ], order='check_in desc', limit=1)
            
            status = {
                'employee_id': employee.id,
                'employee_name': employee.name,
                'checked_in': False,
                'checked_out': False,
                'check_in': None,
                'check_out': None,
                'current_hours': 0,
            }
            
            if attendance:
                status['checked_in'] = True
                status['check_in'] = attendance.check_in
                if attendance.check_out:
                    status['checked_out'] = True
                    status['check_out'] = attendance.check_out
                else:
                    # Calculate current hours
                    check_in_time = fields.Datetime.from_string(attendance.check_in)
                    current_time = fields.Datetime.now()
                    status['current_hours'] = (current_time - check_in_time).total_seconds() / 3600
            
            return {
                'status': 'success',
                'data': status,
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/attendance/trends/weekly', type='json', auth='user')
    def get_weekly_trends(self, weeks=4, **kwargs):
        """Get weekly attendance trends"""
        try:
            end_date = fields.Date.today()
            start_date = end_date - timedelta(days=weeks * 7)
            
            dashboard_model = request.env['hr.attendance.dashboard']
            data = dashboard_model.get_dashboard_data(
                date_from=start_date,
                date_to=end_date,
            )
            
            # Process trends into weekly buckets
            trends = data.get('trends', [])
            weekly_data = {}
            
            for trend in trends:
                date_obj = fields.Date.from_string(trend['date'])
                week_start = date_obj - timedelta(days=date_obj.weekday())
                week_key = fields.Date.to_string(week_start)
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = {
                        'week_start': week_key,
                        'count': 0,
                        'hours': 0,
                        'days': 0,
                    }
                
                weekly_data[week_key]['count'] += trend['count']
                weekly_data[week_key]['hours'] += trend['hours']
                weekly_data[week_key]['days'] += 1
            
            return {
                'status': 'success',
                'data': list(weekly_data.values()),
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/attendance/alerts', type='json', auth='user')
    def get_attendance_alerts(self, **kwargs):
        """Get attendance alerts and anomalies"""
        try:
            alerts = []
            
            # Check for employees with low attendance
            today = fields.Date.today()
            week_start = today - timedelta(days=today.weekday())
            
            employees = request.env['hr.employee'].search([('active', '=', True)])
            
            for employee in employees:
                week_attendances = request.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', fields.Datetime.to_string(week_start)),
                ])
                
                if len(week_attendances) < 3:  # Less than 3 days this week
                    alerts.append({
                        'type': 'low_attendance',
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'message': f'Low attendance this week: {len(week_attendances)} days',
                        'severity': 'warning',
                    })
            
            return {
                'status': 'success',
                'data': alerts,
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/attendance/matrix/data', type='json', auth='user')
    def get_matrix_data(self, matrix_id=None, date_from=None, date_to=None, employee_ids=None, department_ids=None, **kwargs):
        """Get matrix view data. If matrix_id is provided, use that record; else create from params."""
        try:
            if matrix_id:
                record = request.env['hr.attendance.matrix'].browse(int(matrix_id)).exists()
                if record:
                    data = record.get_matrix_data_json()
                    return {'status': 'success', 'data': data}
            if date_from and isinstance(date_from, str):
                date_from = fields.Date.from_string(date_from)
            if date_to and isinstance(date_to, str):
                date_to = fields.Date.from_string(date_to)
            if employee_ids and not isinstance(employee_ids, list):
                employee_ids = [employee_ids] if employee_ids else None
            if department_ids and not isinstance(department_ids, list):
                department_ids = [department_ids] if department_ids else None
            matrix = request.env['hr.attendance.matrix'].create({
                'date_from': date_from or (fields.Date.today() - timedelta(days=30)),
                'date_to': date_to or fields.Date.today(),
                'employee_ids': [(6, 0, employee_ids or [])],
                'department_ids': [(6, 0, department_ids or [])],
            })
            data = matrix.get_matrix_data_json()
            matrix.unlink()
            return {'status': 'success', 'data': data}
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

    @http.route('/attendance/matrix/view', type='http', auth='user')
    def matrix_view_page(self, matrix_id=None, **kwargs):
        """Render the attendance matrix as a full HTML page (no form field required)."""
        if not matrix_id:
            html = '<html><body><p>No matrix selected.</p></body></html>'
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        record = request.env['hr.attendance.matrix'].browse(int(matrix_id)).exists()
        if not record:
            html = '<html><body><p>Matrix not found.</p></body></html>'
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        matrix_html = record._build_matrix_html()
        style = """
        body { font-family: Arial, sans-serif; margin: 16px; }
        .matrix-table { border-collapse: collapse; width: 100%%; }
        .matrix-table th, .matrix-table td { border: 1px solid #ddd; padding: 6px 8px; text-align: center; }
        .matrix-table th { background: #f5f5f5; }
        .matrix-cell { min-width: 32px; }
        .hours-badge { font-size: 0.85em; font-weight: bold; }
        """
        html = '<!DOCTYPE html><html><head><meta charset="utf-8"/><title>Attendance Matrix</title><style>%s</style></head><body><h2>Attendance Matrix View</h2>%s</body></html>' % (style, matrix_html)
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])

