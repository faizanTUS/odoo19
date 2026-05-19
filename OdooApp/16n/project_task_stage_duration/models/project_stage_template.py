# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectStageTemplate(models.Model):
    _name = 'project.stage.template'
    _description = 'Stage Template'
    _order = 'sequence, id'

    name = fields.Char(
        string='Stage Template Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    stage_line_ids = fields.One2many(
        'project.stage.template.line',
        'template_id',
        string='Project Stages',
        copy=True,
    )


class ProjectStageTemplateLine(models.Model):
    _name = 'project.stage.template.line'
    _description = 'Stage Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'project.stage.template',
        string='Template',
        required=True,
        ondelete='cascade',
    )
    stage_id = fields.Many2one(
        'project.task.type',
        string='Stage',
        required=True,
        ondelete='restrict',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    is_project_stage = fields.Boolean(
        string='Project Stage',
        default=True,
        help='Include this stage in project stage duration tracking.',
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
