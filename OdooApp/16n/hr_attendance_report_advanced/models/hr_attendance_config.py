# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HRAttendanceReportConfig(models.Model):
    _name = 'hr.attendance.report.config'
    _description = 'Attendance Report Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                  default=lambda self: self.env.company)
    
    # Working Hours Configuration
    standard_working_hours = fields.Float(string='Standard Working Hours per Day', 
                                           default=8.0, required=True,
                                           help='Default working hours per day for overtime calculation')
    half_day_threshold = fields.Float(string='Half Day Threshold (Hours)', 
                                      default=4.0, required=True,
                                      help='Minimum hours to count as half day')
    
    # Status Colors Configuration
    color_present = fields.Char(string='Present Color', default='#28a745',
                                help='Hex color code for present status')
    color_absent = fields.Char(string='Absent Color', default='#dc3545',
                                help='Hex color code for absent status')
    color_half_day = fields.Char(string='Half Day Color', default='#007bff',
                                  help='Hex color code for half day status')
    color_leave = fields.Char(string='Leave Color', default='#fd7e14',
                               help='Hex color code for leave status')
    color_work_on = fields.Char(string='Work On Color', default='#6c757d',
                                 help='Hex color code for weekend/holiday status')
    
    # Display Configuration
    default_date_range_days = fields.Integer(string='Default Date Range (Days)', 
                                             default=30,
                                             help='Default number of days for report date range')
    show_break_time = fields.Boolean(string='Show Break Time by Default', default=False)
    show_overtime = fields.Boolean(string='Show Overtime by Default', default=True)
    show_punctuality = fields.Boolean(string='Show Punctuality Analysis', default=True)
    
    # Dashboard Configuration
    dashboard_refresh_interval = fields.Integer(string='Dashboard Refresh Interval (seconds)', 
                                                default=300,
                                                help='Auto-refresh interval for dashboard (0 to disable)')
    show_live_status = fields.Boolean(string='Show Live Employee Status', default=True)
    enable_alerts = fields.Boolean(string='Enable Attendance Alerts', default=True)
    
    # Export Configuration
    excel_template_id = fields.Many2one('ir.attachment', string='Excel Template',
                                        domain=[('mimetype', '=', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')])
    pdf_template_id = fields.Many2one('ir.attachment', string='PDF Template',
                                      domain=[('mimetype', '=', 'application/pdf')])
    
    # Punctuality Configuration
    late_arrival_threshold = fields.Float(string='Late Arrival Threshold (minutes)', 
                                          default=15.0,
                                          help='Minutes after scheduled time to count as late')
    early_departure_threshold = fields.Float(string='Early Departure Threshold (minutes)', 
                                             default=15.0,
                                             help='Minutes before scheduled time to count as early departure')
    
    # Advanced Settings
    include_weekends = fields.Boolean(string='Include Weekends in Reports by Default', default=True)
    include_holidays = fields.Boolean(string='Include Holidays in Reports by Default', default=True)
    auto_calculate_overtime = fields.Boolean(string='Auto Calculate Overtime', default=True)
    round_hours = fields.Boolean(string='Round Hours to Nearest Quarter', default=False)
    
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Configuration already exists for this company!'),
    ]

    @api.model
    def get_config(self, company_id=None):
        """Get configuration for company, create default if not exists"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        if not config:
            config = self.create({
                'company_id': company_id,
            })
        return config

    @api.constrains('standard_working_hours', 'half_day_threshold')
    def _check_hours(self):
        for record in self:
            if record.standard_working_hours <= 0:
                raise UserError(_('Standard working hours must be greater than 0'))
            if record.half_day_threshold <= 0:
                raise UserError(_('Half day threshold must be greater than 0'))
            if record.half_day_threshold >= record.standard_working_hours:
                raise UserError(_('Half day threshold must be less than standard working hours'))

    def get_status_colors(self):
        """Return dictionary of status colors"""
        return {
            'present': self.color_present,
            'absent': self.color_absent,
            'half_day': self.color_half_day,
            'leave': self.color_leave,
            'work_on': self.color_work_on,
        }

