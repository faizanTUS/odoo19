# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import json
import base64


def _json_serial(obj):
    """JSON serializer for objects not serializable by default (date, datetime)."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class AttendanceAnalyticsWizard(models.TransientModel):
    _name = 'attendance.analytics.wizard'
    _description = 'Attendance Analytics Wizard'

    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: fields.Date.to_string(
                                datetime.now().replace(day=1)))
    date_to = fields.Date(string='To Date', required=True,
                          default=lambda self: fields.Date.to_string(
                              datetime.now().replace(day=1) + timedelta(days=32)))

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    department_ids = fields.Many2many('hr.department', string='Departments')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner', compute='_compute_partner_id', store=False,
                                 help='Used by PDF report for language (company or user partner).')

    # Server-side dashboard data (populated when user clicks Refresh Dashboard)
    dashboard_data_json = fields.Text(string='Dashboard Data', readonly=True)
    kpi_total_employees = fields.Integer(string='Total Employees', readonly=True)
    kpi_present_today = fields.Integer(string='Present Today', readonly=True)
    kpi_attendance_rate = fields.Float(string='Attendance Rate %', readonly=True)
    kpi_total_hours = fields.Float(string='Total Hours', readonly=True)
    kpi_avg_hours = fields.Float(string='Avg Hours/Employee', readonly=True)
    # Server-rendered sections (no JavaScript required)
    trends_html = fields.Html(string='Trends', readonly=True, sanitize=False)
    department_stats_html = fields.Html(string='Department Stats', readonly=True, sanitize=False)
    punctuality_html = fields.Html(string='Punctuality', readonly=True, sanitize=False)
    overtime_html = fields.Html(string='Overtime', readonly=True, sanitize=False)
    current_status_html = fields.Html(string='Current Status', readonly=True, sanitize=False)

    chart_type = fields.Selection([
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('radar', 'Radar Chart'),
    ], string='Chart Type', default='bar')

    metric = fields.Selection([
        ('attendance_count', 'Attendance Count'),
        ('working_hours', 'Working Hours'),
        ('overtime_hours', 'Overtime Hours'),
        ('absent_days', 'Absent Days'),
        ('leave_days', 'Leave Days'),
    ], string='Metric', default='working_hours')

    group_by = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('employee', 'Employee'),
        ('department', 'Department'),
        ('status', 'Status'),
    ], string='Group By', default='department')

    compare_with_previous = fields.Boolean(string='Compare with Previous Period', default=False)
    previous_period = fields.Selection([
        ('week', 'Previous Week'),
        ('month', 'Previous Month'),
        ('quarter', 'Previous Quarter'),
        ('year', 'Previous Year'),
    ], string='Previous Period', default='month')

    @api.depends('company_id')
    def _compute_partner_id(self):
        for rec in self:
            rec.partner_id = rec.company_id.partner_id if rec.company_id and rec.company_id.partner_id else rec.env.user.partner_id

    def action_generate_analytics(self):
        """Refresh dashboard: fetch data from backend and display KPIs + store JSON for charts."""
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError(_('From Date must be before To Date'))

        try:
            dashboard_model = self.env['hr.attendance.dashboard']
            data = dashboard_model.get_dashboard_data(
                date_from=self.date_from,
                date_to=self.date_to,
                employee_ids=self.employee_ids.ids or None,
                department_ids=self.department_ids.ids or None,
            )
        except Exception as e:
            raise UserError(_('Could not load dashboard data: %s') % str(e))

        kpis = data.get('kpis') or {}
        try:
            data_str = json.dumps(data, default=_json_serial)
        except (TypeError, ValueError):
            data_str = json.dumps({
                'kpis': kpis,
                'trends': data.get('trends', []),
                'department_stats': data.get('department_stats', {}),
                'punctuality': data.get('punctuality', {}),
                'overtime': data.get('overtime', {}),
                'current_status': data.get('current_status', {}),
            }, default=_json_serial)

        # Build server-side HTML for all sections (no JavaScript needed)
        trends_html = self._build_trends_html(data.get('trends') or [])
        department_stats_html = self._build_department_stats_html(data.get('department_stats') or {})
        punctuality_html = self._build_punctuality_html(data.get('punctuality') or {})
        overtime_html = self._build_overtime_html(data.get('overtime') or {})
        current_status_html = self._build_current_status_html(data.get('current_status') or {})

        self.write({
            'dashboard_data_json': data_str,
            'kpi_total_employees': kpis.get('total_employees', 0),
            'kpi_present_today': kpis.get('present_today', 0),
            'kpi_attendance_rate': kpis.get('attendance_rate', 0),
            'kpi_total_hours': kpis.get('total_hours', 0),
            'kpi_avg_hours': kpis.get('avg_hours_per_employee', 0),
            'trends_html': trends_html,
            'department_stats_html': department_stats_html,
            'punctuality_html': punctuality_html,
            'overtime_html': overtime_html,
            'current_status_html': current_status_html,
        })

        # Reopen form so it refetches and shows updated KPIs (current = main area, new = dialog)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Analytics Dashboard',
            'res_model': 'attendance.analytics.wizard',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id,
            'views': [(self.env.ref('hr_attendance_report_advanced.view_attendance_dashboard').id, 'form')],
        }

    def _build_trends_html(self, trends):
        if not trends:
            return '<p class="text-muted">No trend data for the selected period.</p>'
        rows = ''.join(
            '<tr><td>%s</td><td>%s</td><td>%.1f</td></tr>' % (t.get('date', ''), t.get('count', 0), t.get('hours', 0))
            for t in trends[:31]
        )
        return '''
        <table class="table table-sm table-bordered">
            <thead><tr><th>Date</th><th>Count</th><th>Hours</th></tr></thead>
            <tbody>%s</tbody>
        </table>
        ''' % rows

    def _build_department_stats_html(self, department_stats):
        if not department_stats:
            return '<p class="text-muted">No department data.</p>'
        rows = ''.join(
            '<tr><td>%s</td><td>%s</td><td>%.1f</td><td>%.1f%%</td></tr>' % (
                self._escape_html(str(dept)),
                stats.get('employees', 0),
                stats.get('total_hours', 0),
                stats.get('attendance_rate', 0),
            )
            for dept, stats in department_stats.items()
        )
        return '''
        <table class="table table-sm table-bordered">
            <thead><tr><th>Department</th><th>Employees</th><th>Total Hours</th><th>Rate %%</th></tr></thead>
            <tbody>%s</tbody>
        </table>
        ''' % rows

    def _build_punctuality_html(self, punctuality):
        if not punctuality:
            return '<p class="text-muted">No punctuality data.</p>'
        return '''
        <ul class="list-unstyled mb-0">
            <li><strong>On time:</strong> %s</li>
            <li><strong>Late:</strong> %s</li>
            <li><strong>Early departure:</strong> %s</li>
            <li><strong>Total:</strong> %s</li>
        </ul>
        ''' % (
            punctuality.get('on_time', 0),
            punctuality.get('late', 0),
            punctuality.get('early', 0),
            punctuality.get('total', 0),
        )

    def _build_overtime_html(self, overtime):
        if not overtime:
            return '<p class="text-muted">No overtime data.</p>'
        return '''
        <ul class="list-unstyled mb-0">
            <li><strong>Total overtime hours:</strong> %.1f</li>
            <li><strong>Overtime days:</strong> %s</li>
            <li><strong>Avg overtime/day:</strong> %.1f</li>
        </ul>
        ''' % (
            overtime.get('total_overtime', 0),
            overtime.get('overtime_days', 0),
            overtime.get('avg_overtime_per_day', 0),
        )

    def _build_current_status_html(self, current_status):
        if not current_status:
            return '<p class="text-muted">No status data.</p>'
        checked_in = current_status.get('checked_in') or []
        checked_out = current_status.get('checked_out') or []
        html = ''
        if checked_in:
            html += '<p><strong>Checked in:</strong></p><ul>'
            for emp in checked_in:
                html += '<li>%s (since %s)</li>' % (self._escape_html(emp.get('name', '')), emp.get('check_in', ''))
            html += '</ul>'
        if checked_out:
            html += '<p><strong>Checked out:</strong></p><ul>'
            for emp in checked_out[:10]:
                html += '<li>%s</li>' % self._escape_html(emp.get('name', ''))
            if len(checked_out) > 10:
                html += '<li><em>... and %s more</em></li>' % (len(checked_out) - 10)
            html += '</ul>'
        if not html:
            html = '<p class="text-muted">No one currently checked in.</p>'
        return html or '<p class="text-muted">No status data.</p>'

    def _escape_html(self, text):
        if not text:
            return ''
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    def _prepare_analytics_data(self):
        # Prepare data for analytics charts
        domain = [
            ('check_in', '>=', self.date_from),
            ('check_in', '<=', self.date_to),
        ]

        # Add filters
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        if self.department_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))

        # Fetch attendance records
        attendances = self.env['hr.attendance'].search(domain)

        # Prepare data based on group_by selection
        if self.group_by == 'department':
            data = self._prepare_department_data(attendances)
        elif self.group_by == 'employee':
            data = self._prepare_employee_data(attendances)
        elif self.group_by == 'status':
            data = self._prepare_status_data(attendances)
        else:
            data = self._prepare_temporal_data(attendances)

        # Prepare comparison data if requested
        comparison_data = None
        if self.compare_with_previous:
            comparison_data = self._prepare_comparison_data()

        return {
            'main_data': data,
            'comparison_data': comparison_data,
            'chart_type': self.chart_type,
            'metric': self.metric,
            'group_by': self.group_by,
            'params': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'employee_count': len(self.employee_ids) if self.employee_ids else 'All',
                'department_count': len(self.department_ids) if self.department_ids else 'All',
            }
        }

    def _prepare_department_data(self, attendances):
        # Group data by department
        department_data = {}
        for attendance in attendances:
            dept_name = attendance.employee_id.department_id.name if attendance.employee_id.department_id else 'No Department'
            if dept_name not in department_data:
                department_data[dept_name] = {
                    'attendance_count': 0,
                    'working_hours': 0,
                    'overtime_hours': 0,
                    'absent_days': 0,
                    'leave_days': 0,
                }

            department_data[dept_name]['attendance_count'] += 1
            department_data[dept_name]['working_hours'] += attendance.worked_hours or 0

            # Calculate overtime (assuming standard 8-hour day)
            if attendance.worked_hours > 8:
                department_data[dept_name]['overtime_hours'] += attendance.worked_hours - 8

            # Count absences and leaves based on status (if status is set)
            if attendance.attendance_status_id:
                if getattr(attendance.attendance_status_id, 'is_absent', False):
                    department_data[dept_name]['absent_days'] += 1
                elif getattr(attendance.attendance_status_id, 'is_leave', False):
                    department_data[dept_name]['leave_days'] += 1

        return department_data

    def _prepare_employee_data(self, attendances):
        # Similar implementation for employee grouping
        pass

    def _prepare_status_data(self, attendances):
        # Similar implementation for status grouping
        pass

    def _prepare_temporal_data(self, attendances):
        # Similar implementation for temporal grouping
        pass

    def _prepare_comparison_data(self):
        # Prepare data for comparison with previous period
        pass

    def action_print_dashboard_pdf(self):
        """Print / download the current dashboard as PDF (Analytics Report)."""
        self.ensure_one()
        # Ensure dashboard data is loaded so PDF has content
        if not self.dashboard_data_json:
            self.action_generate_analytics()
        try:
            report = self.env.ref('hr_attendance_report_advanced.action_analytics_report')
        except ValueError:
            raise UserError(_('Analytics Report not found. Upgrade the module.'))
        return report.report_action(self)

    def action_export_data(self):
        """Export analytics data to Excel"""
        self.ensure_one()
        try:
            import xlsxwriter
            import io
        except ImportError:
            raise UserError(_('xlsxwriter package is required for Excel export. Please install it: pip install xlsxwriter'))
        
        # Prepare analytics data
        analytics_data = self._prepare_analytics_data()
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Create summary sheet
        worksheet = workbook.add_worksheet('Analytics Summary')
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
        })
        
        # Write headers
        headers = ['Metric', 'Value']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        main_data = analytics_data.get('main_data', {})
        if isinstance(main_data, dict):
            for key, value in main_data.items():
                worksheet.write(row, 0, str(key))
                if isinstance(value, dict):
                    worksheet.write(row, 1, str(value))
                else:
                    worksheet.write(row, 1, value)
                row += 1
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f'analytics_export_{self.date_from}_{self.date_to}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'attendance.analytics.wizard',
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }