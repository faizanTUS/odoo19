# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    global_task_stage_duration_enabled = fields.Boolean(
        string='Project Task Stage Duration (Global)',
        config_parameter='project_task_stage_duration.global_task_stage_duration_enabled',
        help='Enable task stage duration tracking for all projects (unless overridden per project).',
    )
    global_stage_history_enabled = fields.Boolean(
        string='Project Stage Duration History (Global)',
        config_parameter='project_task_stage_duration.global_stage_history_enabled',
        help='Enable stage history (Stage In, Stage Out, Duration) for all projects (unless overridden per project).',
    )
