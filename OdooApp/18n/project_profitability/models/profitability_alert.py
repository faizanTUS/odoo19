# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProfitabilityAlert(models.Model):
    _name = 'profitability.alert'
    _description = 'Profitability Alert Rules'

    name = fields.Char(string='Alert Name', required=True)
    alert_type = fields.Selection([
        ('margin_low', 'Low Margin'),
        ('over_budget', 'Over Budget'),
        ('cost_spike', 'Cost Spike'),
        ('revenue_delay', 'Revenue Delay'),
    ], required=True)

    threshold_value = fields.Float(string='Threshold Value')
    threshold_percentage = fields.Float(string='Threshold %')

    notification_users = fields.Many2many('res.users', string='Notify Users')
    send_email = fields.Boolean(string='Send Email', default=True)

    active = fields.Boolean(default=True)

    @api.model
    def check_alerts(self):
        """Check all active alerts"""
        alerts = self.search([('active', '=', True)])

        for alert in alerts:
            projects = self.env['project.project'].search([
                ('active', '=', True),
                ('current_profitability_id', '!=', False)
            ])

            triggered_projects = []

            for project in projects:
                prof = project.current_profitability_id
                if not prof:
                    continue

                if alert.alert_type == 'margin_low':
                    if prof.margin_percentage < alert.threshold_percentage:
                        triggered_projects.append(project)

                elif alert.alert_type == 'over_budget':
                    if prof.budget_status == 'over':
                        triggered_projects.append(project)

                elif alert.alert_type == 'cost_spike':
                    # Check if cost increased more than threshold % from last snapshot
                    previous = self.env['project.profitability'].search([
                        ('project_id', '=', project.id),
                        ('date', '<', prof.date)
                    ], order='date desc', limit=1)

                    if previous and previous.total_cost > 0:
                        increase_pct = (
                            (prof.total_cost - previous.total_cost) /
                            previous.total_cost * 100
                        )
                        if increase_pct > alert.threshold_percentage:
                            triggered_projects.append(project)

                elif alert.alert_type == 'revenue_delay':
                    # Check if invoiced amount is significantly less than budgeted
                    if prof.budget_revenue > 0:
                        invoiced_pct = (prof.invoiced_amount / prof.budget_revenue * 100)
                        if invoiced_pct < alert.threshold_percentage:
                            triggered_projects.append(project)

            # Send notifications
            if triggered_projects and alert.send_email and alert.notification_users:
                alert._send_alert_email(triggered_projects)

    def _send_alert_email(self, projects):
        """Send alert emails"""
        template = self.env.ref(
            'project_profitability.email_template_alert',
            raise_if_not_found=False
        )
        if not template:
            return

        for user in self.notification_users:
            ctx = {
                'alert_name': self.name,
                'alert_type': dict(self._fields['alert_type'].selection)[self.alert_type],
                'projects': projects,
                'recipient_name': user.name,
            }

            template.with_context(ctx).send_mail(user.id, force_send=True)
