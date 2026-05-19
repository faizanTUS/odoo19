# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, api


class AnalyticsReportTemplate(models.AbstractModel):
    _name = 'report.hr_attendance_report_advanced.analytics_report_template'
    _description = 'Attendance Analytics Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Return report values for the analytics PDF. docids are attendance.analytics.wizard ids."""
        wizards = self.env['attendance.analytics.wizard'].browse(docids)
        if not wizards:
            return {'docs': self.env['attendance.analytics.wizard'], 'date_from': '', 'date_to': '', 'analytics_content': ''}
        doc = wizards[0]
        # Build analytics content from stored HTML sections (no recursion)
        parts = []
        if doc.trends_html:
            parts.append(doc.trends_html)
        if doc.department_stats_html:
            parts.append(doc.department_stats_html)
        if doc.punctuality_html:
            parts.append(doc.punctuality_html)
        if doc.overtime_html:
            parts.append(doc.overtime_html)
        if doc.current_status_html:
            parts.append(doc.current_status_html)
        if not parts:
            parts.append(
                '<p>Refresh the Analytics Dashboard first (click "Refresh Dashboard") to see KPIs and summaries here.</p>'
                '<p>Total Employees: %s | Present Today: %s | Attendance Rate: %s%% | Total Hours: %s</p>' % (
                    doc.kpi_total_employees or 0,
                    doc.kpi_present_today or 0,
                    round(doc.kpi_attendance_rate or 0, 1),
                    round(doc.kpi_total_hours or 0, 1),
                )
            )
        analytics_content = ''.join(parts)
        # web.internal_layout expects company to be a res.company record
        company = doc.company_id if doc.company_id else self.env.company
        return {
            'docs': wizards,
            'date_from': doc.date_from,
            'date_to': doc.date_to,
            'analytics_content': analytics_content,
            'company': company,
        }
