# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import csv
from datetime import datetime, timedelta


class AttendanceImportWizard(models.TransientModel):
    _name = 'attendance.import.wizard'
    _description = 'Attendance Import Wizard'

    import_file = fields.Binary(string='Import File', required=True)
    file_name = fields.Char(string='File Name')
    import_type = fields.Selection([
        ('csv', 'CSV File'),
        ('xlsx', 'Excel File'),
    ], string='File Type', default='csv')

    date_format = fields.Selection([
        ('%Y-%m-%d', 'YYYY-MM-DD'),
        ('%d/%m/%Y', 'DD/MM/YYYY'),
        ('%m/%d/%Y', 'MM/DD/YYYY'),
        ('%d-%m-%Y', 'DD-MM-YYYY'),
        ('%m-%d-%Y', 'MM-DD-YYYY'),
    ], string='Date Format', default='%Y-%m-%d')

    time_format = fields.Selection([
        ('%H:%M:%S', 'HH:MM:SS (24-hour)'),
        ('%I:%M:%S %p', 'HH:MM:SS AM/PM (12-hour)'),
    ], string='Time Format', default='%H:%M:%S')

    # Mapping fields
    map_employee = fields.Selection([
        ('id', 'Employee ID'),
        ('badge_id', 'Badge ID'),
        ('name', 'Employee Name'),
    ], string='Employee Identifier', default='badge_id')

    map_date = fields.Char(string='Date Column', default='date')
    map_check_in = fields.Char(string='Check-in Column', default='check_in')
    map_check_out = fields.Char(string='Check-out Column', default='check_out')
    map_status = fields.Char(string='Status Column', default='status')

    # Options
    create_missing_employees = fields.Boolean(string='Create Missing Employees', default=False)
    update_existing = fields.Boolean(string='Update Existing Records', default=False)
    send_notifications = fields.Boolean(string='Send Import Notifications', default=False)

    import_result = fields.Text(string='Import Result', readonly=True)

    def action_import(self):
        self.ensure_one()
        try:
            if not self.import_file:
                raise UserError(_('Please select a file to import'))

            # Decode the file
            file_content = base64.b64decode(self.import_file)

            if self.import_type == 'csv':
                result = self._import_csv(file_content)
            else:
                raise UserError(_('Excel import not yet implemented'))

            # Store result
            self.import_result = result

            # Send notifications if enabled
            if self.send_notifications:
                self._send_import_notification(result)

            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

        except Exception as e:
            raise UserError(_('Error during import: %s') % str(e))

    def _import_csv(self, file_content):
        # Convert bytes to string
        content = file_content.decode('utf-8')
        lines = content.splitlines()

        # Parse CSV
        reader = csv.DictReader(lines)
        success_count = 0
        error_count = 0
        errors = []

        for i, row in enumerate(reader, 2):  # Start from line 2 (header is line 1)
            try:
                # Process each row
                result = self._process_attendance_row(row)
                if result:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"Line {i}: Failed to process row")
            except Exception as e:
                error_count += 1
                errors.append(f"Line {i}: {str(e)}")

        # Prepare result message
        result = f"Import completed:\n"
        result += f"Successfully imported: {success_count} records\n"
        result += f"Failed: {error_count} records\n"

        if errors:
            result += "\nErrors:\n" + "\n".join(errors[:10])  # Show first 10 errors
            if len(errors) > 10:
                result += f"\n... and {len(errors) - 10} more errors"

        return result

    def _process_attendance_row(self, row):
        # Get employee
        employee_identifier = row.get(self.map_employee)
        if not employee_identifier:
            raise ValueError('Employee identifier not found')

        employee = self._get_employee(employee_identifier)
        if not employee:
            if self.create_missing_employees:
                employee = self._create_employee(row)
            else:
                raise ValueError(f'Employee not found: {employee_identifier}')

        # Parse date and time
        date_str = row.get(self.map_date)
        check_in_str = row.get(self.map_check_in)
        check_out_str = row.get(self.map_check_out)

        if not all([date_str, check_in_str]):
            raise ValueError('Missing required fields (date or check_in)')

        # Parse datetime
        check_in_dt = self._parse_datetime(date_str, check_in_str)
        check_out_dt = self._parse_datetime(date_str, check_out_str) if check_out_str else None

        # Get or create attendance status
        status_code = row.get(self.map_status, 'P')  # Default to Present
        status = self.env['hr.attendance.status'].search([('code', '=', status_code)], limit=1)
        if not status:
            status = self.env.ref('hr_attendance_report_advanced.status_present')

        # Check if attendance already exists
        existing_attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', check_in_dt.date()),
            ('check_in', '<', (check_in_dt.date() + timedelta(days=1))),
        ])

        if existing_attendance:
            if self.update_existing:
                # Update existing record
                existing_attendance.write({
                    'check_in': check_in_dt,
                    'check_out': check_out_dt,
                    'attendance_status_id': status.id,
                })
                return True
            else:
                raise ValueError('Attendance already exists for this date')
        else:
            # Create new attendance record
            self.env['hr.attendance'].create({
                'employee_id': employee.id,
                'check_in': check_in_dt,
                'check_out': check_out_dt,
                'attendance_status_id': status.id,
            })
            return True

    def _get_employee(self, identifier):
        if self.map_employee == 'id':
            return self.env['hr.employee'].browse(int(identifier))
        elif self.map_employee == 'badge_id':
            return self.env['hr.employee'].search([('barcode', '=', identifier)], limit=1)
        else:  # name
            return self.env['hr.employee'].search([('name', '=', identifier)], limit=1)

    def _create_employee(self, row):
        # Create a new employee (simplified implementation)
        return self.env['hr.employee'].create({
            'name': row.get('employee_name', 'Unknown Employee'),
            'barcode': row.get('badge_id', f"IMP{datetime.now().strftime('%Y%m%d%H%M%S')}"),
        })

    def _parse_datetime(self, date_str, time_str):
        try:
            date_obj = datetime.strptime(date_str, self.date_format)
            time_obj = datetime.strptime(time_str, self.time_format)
            return datetime.combine(date_obj.date(), time_obj.time())
        except ValueError as e:
            raise ValueError(f'Invalid date/time format: {date_str} {time_str} - {str(e)}')

    def _send_import_notification(self, result):
        # Send email notification about import results
        template = self.env.ref('hr_attendance_report_advanced.email_template_import_result')
        template.send_mail(self.id, force_send=True)