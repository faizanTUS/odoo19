# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    task_stage_duration_enabled = fields.Boolean(
        string='Project Task Stage Duration',
        default=False,
    )
    stage_history_enabled = fields.Boolean(
        string='Project Stage Duration History',
        default=False,
    )
    stage_template_id = fields.Many2one(
        'project.stage.template',
        string='Stage Template',
        help='Select a stage template to apply predefined stages to this project.',
    )

    @api.model
    def _get_global_duration_settings(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        duration = ICPSudo.get_param('project_task_stage_duration.global_task_stage_duration_enabled', 'False') == 'True'
        history = ICPSudo.get_param('project_task_stage_duration.global_stage_history_enabled', 'False') == 'True'
        return duration, history

    def _get_template_line_for_stage(self, stage_id):
        """Get the template line for a given stage in this project's template."""
        if not self.stage_template_id:
            return None
        return self.env['project.stage.template.line'].search([
            ('template_id', '=', self.stage_template_id.id),
            ('stage_id', '=', stage_id),
        ], limit=1)