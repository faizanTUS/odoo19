# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models


class ProjectTaskStageHistory(models.Model):
    _name = 'project.task.stage.history'
    _description = 'Task Stage History / Lifetime'
    _order = 'stage_in desc, id desc'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade',
        index=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='task_id.project_id',
        store=True,
        readonly=True,
    )
    stage_id = fields.Many2one(
        'project.task.type',
        string='Stage',
        required=True,
        ondelete='restrict',
        index=True,
    )
    from_stage_id = fields.Many2one(
        'project.task.type',
        string='From Stage',
        ondelete='set null',
        index=True,
    )
    stage_in = fields.Datetime(
        string='Stage In',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    stage_out = fields.Datetime(
        string='Stage Out',
        readonly=True,
    )
    duration = fields.Float(
        string='Duration',
        compute='_compute_duration',
        store=True,
        help='Time spent in this stage in seconds.',
    )
    duration_display = fields.Char(
        string='Duration',
        compute='_compute_duration_display',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
    )

    @api.depends('stage_in', 'stage_out')
    def _compute_duration(self):
        for rec in self:
            if rec.stage_out:
                delta = rec.stage_out - rec.stage_in
                rec.duration = delta.total_seconds()
            else:
                rec.duration = 0.0

    @api.depends('duration', 'stage_in', 'stage_out')
    def _compute_duration_display(self):
        for rec in self:
            if rec.stage_out and rec.duration:
                total_seconds = int(rec.duration)
                days = total_seconds // 86400
                remainder = total_seconds % 86400
                hours = remainder // 3600
                minutes = (remainder % 3600) // 60
                secs = remainder % 60
                if days > 0:
                    rec.duration_display = f'{days} Days' if days == 1 else f'{days} Days'
                    if hours or minutes or secs:
                        rec.duration_display += f', {hours:02d}:{minutes:02d}:{secs:02d}'
                else:
                    rec.duration_display = f'{hours:02d}:{minutes:02d}:{secs:02d}'
            elif not rec.stage_out:
                rec.duration_display = ''
            else:
                rec.duration_display = '0:00:00'

    def _format_duration_seconds(self, seconds):
        """Format seconds as 'X Days' or 'HH:MM:SS' for display."""
        if not seconds:
            return '0:00:00'
        total_seconds = int(seconds)
        days = total_seconds // 86400
        remainder = total_seconds % 86400
        hours = remainder // 3600
        minutes = (remainder % 3600) // 60
        secs = remainder % 60
        if days > 0:
            s = f'{days} Day{"s" if days != 1 else ""}'
            if hours or minutes or secs:
                s += f', {hours:02d}:{minutes:02d}:{secs:02d}'
            return s
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
