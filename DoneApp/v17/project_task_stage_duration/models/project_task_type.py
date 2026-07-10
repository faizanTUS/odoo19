# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_project_stage = fields.Boolean(
        string='Project Stage',
        default=False,
        help='Include this stage in project task stage duration and history tracking.',
    )
    track_duration_start = fields.Boolean(
        string='Start',
        default=False,
        help='When a task enters this stage, start counting duration.',
    )
    track_duration_stop = fields.Boolean(
        string='Stop',
        default=False,
        help='When a task enters this stage, stop counting duration.',
    )
