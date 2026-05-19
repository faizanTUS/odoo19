# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from datetime import datetime, timedelta, time
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class AttendanceReportWizard(models.TransientModel):
    _name = 'attendance.report.wizard'
    _description = 'Attendance Report Wizard'

    report_type = fields.Selection([
        ('detailed', 'Detailed Report'),
        ('summary', 'Summary Report'),
        ('combined', 'Combined Report'),
        ('analytics', 'Analytics Dashboard'),
        ('matrix', 'Matrix View'),
    ], string='Report Type', default='detailed', required=True)

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

    group_by = fields.Selection([
        ('none', 'None'),
        ('employee', 'Employee'),
        ('department', 'Department'),
        ('week', 'Week'),
        ('month', 'Month'),
    ], string='Group By', default='employee')

    @api.depends('company_id')
    def _compute_partner_id(self):
        for rec in self:
            rec.partner_id = rec.company_id.partner_id if rec.company_id and rec.company_id.partner_id else rec.env.user.partner_id

    show_hours = fields.Boolean(string='Show Hours', default=True)
    show_overtime = fields.Boolean(string='Show Overtime', default=True)
    show_breaks = fields.Boolean(string='Show Break Time', default=False)
    include_inactive = fields.Boolean(string='Include Inactive Employees', default=False)

    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ], string='Output Format', default='pdf')

    # Advanced filters
    filter_status_ids = fields.Many2many('hr.attendance.status', string='Filter by Status')
    min_hours = fields.Float(string='Minimum Hours', help="Filter employees with at least these hours")
    max_hours = fields.Float(string='Maximum Hours', help="Filter employees with at most these hours")
    include_weekends = fields.Boolean(string='Include Weekends', default=True)
    include_holidays = fields.Boolean(string='Include Holidays', default=True)

    # Notification options
    send_email = fields.Boolean(string='Send Report via Email')
    email_template_id = fields.Many2one('mail.template', string='Email Template',
                                        domain="[('model', '=', 'attendance.report.wizard')]")
    recipient_ids = fields.Many2many('res.partner', string='Recipients')

    @api.onchange('department_ids')
    def _onchange_department_ids(self):
        if self.department_ids:
            return {'domain': {'employee_ids': [('department_id', 'in', self.department_ids.ids)]}}
        return {}

    @api.onchange('report_type')
    def _onchange_report_type(self):
        if self.report_type == 'analytics':
            self.group_by = 'department'
            self.show_hours = True
            self.show_overtime = True

    def action_generate_report(self):
        self.ensure_one()
        # Validate dates
        if self.date_from > self.date_to:
            raise UserError(_('From Date must be before To Date'))

        # Prepare report data
        report_data = self._prepare_report_data()

        # Send email if requested
        if self.send_email and self.recipient_ids:
            self._send_report_email(report_data)

        # Return report action based on report type and output format
        if self.report_type == 'matrix':
            return self._open_matrix_view()
        elif self.report_type == 'analytics':
            return self.action_open_analytics_dashboard()
        elif self.output_format == 'pdf':
            return self._generate_pdf_report(report_data)
        elif self.output_format == 'excel':
            return self._generate_excel_report(report_data)
        else:
            return self._generate_html_report(report_data)
    
    def _open_matrix_view(self):
        """Open matrix view"""
        matrix = self.env['hr.attendance.matrix'].create({
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_ids': [(6, 0, self.employee_ids.ids)],
            'department_ids': [(6, 0, self.department_ids.ids)],
        })
        return matrix.action_open_matrix_view()

    def _prepare_report_data(self):
        # Complex data preparation logic
        # Convert date fields to datetime for check_in comparison
        date_from_dt = fields.Datetime.to_datetime(self.date_from)
        date_to_dt = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1) - timedelta(seconds=1)
        
        domain = [
            ('check_in', '>=', date_from_dt),
            ('check_in', '<=', date_to_dt),
        ]

        # Add employee filter
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))

        # Add department filter
        if self.department_ids and not self.employee_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))

        # Add status filter
        if self.filter_status_ids:
            domain.append(('attendance_status_id', 'in', self.filter_status_ids.ids))

        # Fetch attendance records
        attendance_obj = self.env['hr.attendance']
        attendances = attendance_obj.search(domain)

        # Group data based on selection
        grouped_data = self._group_attendance_data(attendances)

        # Calculate statistics
        statistics = self._calculate_statistics(grouped_data)

        report_data = {
            'grouped_data': grouped_data,
            'statistics': statistics,
            'params': self._get_report_parameters(),
        }
        _logger.info(
            '[PDF Step 1] _prepare_report_data: attendances=%s, grouped_data keys=%s, len(grouped_data)=%s',
            len(attendances), list(grouped_data.keys())[:5], len(grouped_data)
        )
        return report_data

    def _group_attendance_data(self, attendances):
        # Implementation of complex grouping logic
        # Based on group_by field (employee, department, week, month)
        grouped_data = {}

        if self.group_by == 'employee':
            for attendance in attendances:
                employee_id = attendance.employee_id.id
                if employee_id not in grouped_data:
                    grouped_data[employee_id] = {
                        'employee': attendance.employee_id,
                        'attendances': [],
                        'total_hours': 0,
                        'status_count': {},
                    }
                grouped_data[employee_id]['attendances'].append(attendance)
                grouped_data[employee_id]['total_hours'] += attendance.worked_hours or 0

                # Count status occurrences
                status_id = attendance.attendance_status_id.id or 'default'
                if status_id not in grouped_data[employee_id]['status_count']:
                    grouped_data[employee_id]['status_count'][status_id] = 0
                grouped_data[employee_id]['status_count'][status_id] += 1

        # Similar logic for other grouping options
        # ...

        return grouped_data

    def _calculate_statistics(self, grouped_data):
        # Calculate various statistics for the report
        stats = {
            'total_employees': len(grouped_data),
            'total_hours': sum(data['total_hours'] for data in grouped_data.values()),
            'average_hours': 0,
            'status_distribution': {},
            'department_stats': {},
        }

        if stats['total_employees'] > 0:
            stats['average_hours'] = stats['total_hours'] / stats['total_employees']

        # Calculate status distribution
        for data in grouped_data.values():
            for status_id, count in data['status_count'].items():
                if status_id not in stats['status_distribution']:
                    stats['status_distribution'][status_id] = 0
                stats['status_distribution'][status_id] += count

        return stats

    def _get_report_parameters(self):
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_type': self.report_type,
            'group_by': self.group_by,
            'show_hours': self.show_hours,
            'show_overtime': self.show_overtime,
            'company': self.company_id.name,
            'company_id': self.company_id.id if self.company_id else None,
        }

    def _generate_pdf_report(self, report_data):
        """Generate PDF report"""
        Report = self.env['ir.actions.report']
        try:
            # Use _get_report which handles multiple lookup methods (report_name, XML ID, etc.)
            report = Report._get_report('hr_attendance_report_advanced.attendance_report_template')
        except ValueError:
            try:
                # Fallback: try by XML ID
                report = self.env.ref('hr_attendance_report_advanced.action_attendance_report')
            except ValueError:
                # Last resort: search by model and report_type
                report = Report.search([
                    ('model', '=', 'attendance.report.wizard'),
                    ('report_type', '=', 'qweb-pdf'),
                ], limit=1)
                if not report:
                    raise UserError(_(
                        'PDF report template not found. Please upgrade the module or use Excel output instead. '
                        'To fix: Go to Apps → Advanced Employee Attendance Report → Upgrade.'
                    ))
        try:
            # For QWeb reports, pass report_data through context so _get_report_values can access it
            return report.with_context(report_data=report_data).report_action(self)
        except Exception as e:
            raise UserError(_('Could not generate PDF: %s. Try another output.') % str(e))

    def _generate_excel_report(self, report_data):
        """Generate Excel report using xlsxwriter"""
        try:
            import xlsxwriter
            import io
        except ImportError:
            raise UserError(_('xlsxwriter package is required for Excel export. Please install it: pip install xlsxwriter'))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Get configuration
        config = self.env['hr.attendance.report.config'].get_config()
        
        # Create worksheets
        if self.report_type in ['detailed', 'combined']:
            self._create_detailed_sheet(workbook, report_data, config)
        
        if self.report_type in ['summary', 'combined']:
            self._create_summary_sheet(workbook, report_data, config)
        
        if self.report_type == 'combined':
            self._create_statistics_sheet(workbook, report_data, config)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f'attendance_report_{self.date_from}_{self.date_to}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'attendance.report.wizard',
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def _create_detailed_sheet(self, workbook, report_data, config):
        """Create detailed attendance sheet"""
        worksheet = workbook.add_worksheet('Detailed Report')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
        })
        
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        time_format = workbook.add_format({'num_format': 'hh:mm:ss'})
        
        # Write headers
        headers = ['Employee', 'Department', 'Date', 'Check In', 'Check Out', 'Hours', 'Overtime', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        grouped_data = report_data.get('grouped_data', {})
        
        for employee_id, data in grouped_data.items():
            employee = data['employee']
            for attendance in data['attendances']:
                worksheet.write(row, 0, employee.name)
                worksheet.write(row, 1, employee.department_id.name if employee.department_id else '')
                worksheet.write(row, 2, attendance.check_in, date_format)
                worksheet.write(row, 3, attendance.check_in, time_format)
                worksheet.write(row, 4, attendance.check_out or '', time_format if attendance.check_out else None)
                worksheet.write(row, 5, attendance.worked_hours or 0)
                worksheet.write(row, 6, max(0, (attendance.worked_hours or 0) - config.standard_working_hours))
                # Status: use attendance_status_id if set, else derive from worked_hours
                status_text = ''
                if getattr(attendance, 'attendance_status_id', None) and attendance.attendance_status_id:
                    status_text = attendance.attendance_status_id.name
                elif (attendance.worked_hours or 0) >= config.half_day_threshold:
                    status_text = 'Present'
                elif (attendance.worked_hours or 0) > 0:
                    status_text = 'Half Day'
                else:
                    status_text = 'Absent'
                worksheet.write(row, 7, status_text)
                row += 1
        
        # Auto-adjust column widths
        worksheet.set_column(0, 0, 25)  # Employee
        worksheet.set_column(1, 1, 20)  # Department
        worksheet.set_column(2, 2, 12)  # Date
        worksheet.set_column(3, 4, 12)  # Times
        worksheet.set_column(5, 6, 10)  # Hours
        worksheet.set_column(7, 7, 15)  # Status
    
    def _create_summary_sheet(self, workbook, report_data, config):
        """Create summary statistics sheet"""
        worksheet = workbook.add_worksheet('Summary Report')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
        })
        
        # Write headers
        headers = ['Employee', 'Department', 'Total Days', 'Total Hours', 'Overtime Hours', 'Attendance Rate %']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        grouped_data = report_data.get('grouped_data', {})
        statistics = report_data.get('statistics', {})
        
        for employee_id, data in grouped_data.items():
            employee = data['employee']
            total_days = len(data['attendances'])
            total_hours = data['total_hours']
            overtime = self._calculate_overtime(data['attendances'], employee)
            attendance_rate = (total_days / statistics.get('total_days', 1)) * 100 if statistics.get('total_days') else 0
            
            worksheet.write(row, 0, employee.name)
            worksheet.write(row, 1, employee.department_id.name if employee.department_id else '')
            worksheet.write(row, 2, total_days)
            worksheet.write(row, 3, total_hours)
            worksheet.write(row, 4, overtime)
            worksheet.write(row, 5, attendance_rate)
            row += 1
        
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 5, 15)
    
    def _create_statistics_sheet(self, workbook, report_data, config):
        """Create statistics overview sheet"""
        worksheet = workbook.add_worksheet('Statistics')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
        })
        
        statistics = report_data.get('statistics', {})
        
        row = 0
        worksheet.write(row, 0, 'Metric', header_format)
        worksheet.write(row, 1, 'Value', header_format)
        row += 1
        
        metrics = [
            ('Total Employees', statistics.get('total_employees', 0)),
            ('Total Hours', statistics.get('total_hours', 0)),
            ('Average Hours per Employee', statistics.get('average_hours', 0)),
        ]
        
        for metric, value in metrics:
            worksheet.write(row, 0, metric)
            worksheet.write(row, 1, value)
            row += 1

    def _send_report_email(self, report_data):
        """Send report via email with attachment using proper template rendering"""
        if not self.recipient_ids:
            raise UserError(_('Please select at least one recipient.'))

        # ───────────────────────────────────────────────
        # 1. Generate the attachment (PDF or Excel)
        # ───────────────────────────────────────────────
        attachment = None
        filename = f'attendance_report_{self.date_from}_{self.date_to}'

        if self.output_format == 'excel':
            try:
                import xlsxwriter
                import io
            except ImportError:
                raise UserError(
                    _('xlsxwriter package is required for Excel export. Install it: pip install xlsxwriter'))

            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            config = self.env['hr.attendance.report.config'].get_config()

            if self.report_type in ['detailed', 'combined']:
                self._create_detailed_sheet(workbook, report_data, config)
            if self.report_type in ['summary', 'combined']:
                self._create_summary_sheet(workbook, report_data, config)
            if self.report_type == 'combined':
                self._create_statistics_sheet(workbook, report_data, config)

            workbook.close()
            output.seek(0)

            attachment = self.env['ir.attachment'].create({
                'name': f'{filename}.xlsx',
                'type': 'binary',
                'datas': base64.b64encode(output.read()),
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'res_model': self._name,
                'res_id': self.id,
            })

        elif self.output_format == 'pdf':
            report_name = 'hr_attendance_report_advanced.attendance_report_template'
            Report = self.env['ir.actions.report'].sudo()

            try:
                Report._get_report(report_name)  # verify report exists
            except ValueError:
                raise UserError(_(
                    'PDF report template not found. Upgrade the module or switch to Excel.\n'
                    'Fix: Apps → Advanced Employee Attendance Report → Upgrade'
                ))

            try:
                pdf_content, _fmt = Report.with_context(report_data=report_data)._render_qweb_pdf(
                    report_name,
                    res_ids=[self.id],
                    data={'report_data': report_data}
                )

                attachment = self.env['ir.attachment'].create({
                    'name': f'{filename}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'mimetype': 'application/pdf',
                    'res_model': self._name,
                    'res_id': self.id,
                })
            except Exception as e:
                raise UserError(_('Failed to generate PDF attachment: %s') % str(e))

        if not attachment:
            raise UserError(_('Could not generate report attachment. Check your report settings.'))

        # ───────────────────────────────────────────────
        # 2. Get the email template (only once)
        # ───────────────────────────────────────────────
        template = self.email_template_id
        if not template:
            try:
                template = self.env.ref('hr_attendance_report_advanced.email_template_attendance_report')
            except ValueError:
                raise UserError(_(
                    'Email template "Attendance Report" not found.\n'
                    'ID: hr_attendance_report_advanced.email_template_attendance_report\n'
                    'Please make sure the template exists in your module data.'
                ))

        # ───────────────────────────────────────────────
        # 3. Send email to each recipient
        # ───────────────────────────────────────────────
        sent_count = 0
        for recipient in self.recipient_ids:
            if not recipient.email:
                continue

            email_values = {
                'email_to': recipient.email,
                # Optional: you can override subject / from / etc. here if needed
                # 'subject': f'Attendance Report - {self.date_from} to {self.date_to}',
                'attachment_ids': [(4, attachment.id)],
            }

            try:
                template.send_mail(
                    self.id,
                    force_send=True,
                    raise_exception=True,
                    email_values=email_values,
                )
                sent_count += 1
            except Exception as e:
                _logger.warning(
                    "Failed to send attendance report to %s (%s): %s",
                    recipient.name, recipient.email, str(e)
                )
                # You may want to collect failed recipients and show warning at the end

        # Optional: clean up temporary attachment
        # attachment.unlink()

        # Optional: return info to user
        if sent_count == 0:
            raise UserError(_('No emails were sent. Check recipient email addresses.'))
        elif sent_count < len(self.recipient_ids):
            return {
                'warning': {
                    'title': _('Partial Success'),
                    'message': f'Sent to {sent_count} of {len(self.recipient_ids)} recipients.'
                }
            }

    def action_open_analytics_dashboard(self):
        """Open analytics dashboard by creating an analytics wizard with same filters"""
        self.ensure_one()
        # Create an analytics wizard with the same filters
        analytics_wizard = self.env['attendance.analytics.wizard'].create({
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_ids': [(6, 0, self.employee_ids.ids)],
            'department_ids': [(6, 0, self.department_ids.ids)],
            'company_id': self.company_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Analytics Dashboard',
            'res_model': 'attendance.analytics.wizard',
            'res_id': analytics_wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'views': [(self.env.ref('hr_attendance_report_advanced.view_attendance_dashboard').id, 'form')],
        }