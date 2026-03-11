# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    stage_history_ids = fields.One2many(
        'project.task.stage.history',
        'task_id',
        string='Task Stage History',
        readonly=True,
    )

    def _project_tracking_enabled(self):
        """True if stage duration/history tracking is enabled for this task's project or globally."""
        if not self.project_id:
            return False
        global_duration, global_history = self.env['project.project']._get_global_duration_settings()
        return (
            self.project_id.task_stage_duration_enabled or global_duration or
            self.project_id.stage_history_enabled or global_history
        )

    def _should_track_stage(self, stage_id):
        """
        Priority order:
        1. If project has a template → check template line's is_project_stage
        2. If no template -> check if any stage has is_project_stage flagged
           - If some flagged -> only track flagged stages
           - If none flagged > track all
        """
        # Priority 1: Template is set → template rules take full priority
        if self.project_id.stage_template_id:
            # Check if any line in template has is_project_stage = True
            any_template_stage_flagged = any(
                line.is_project_stage
                for line in self.project_id.stage_template_id.stage_line_ids
            )
            template_line = self.project_id._get_template_line_for_stage(stage_id)

            if not template_line:
                return False  # stage not in template = don't track

            if not any_template_stage_flagged:
                return True  # no line flagged in template = track all template stages

            return template_line.is_project_stage  # follow template line setting

        # Priority 2: No template → check stage-level is_project_stage
        any_stage_flagged = self.env['project.task.type'].search_count([
            ('is_project_stage', '=', True)
        ]) > 0

        if not any_stage_flagged:
            return True  # nothing configured anywhere = track everything

        stage = self.env['project.task.type'].browse(stage_id)
        return stage.is_project_stage

    def write(self, vals):
        if 'stage_id' in vals and vals.get('stage_id') is not False:
            now = fields.Datetime.now()
            History = self.env['project.task.stage.history'].sudo()
            for task in self:
                if not task._project_tracking_enabled():
                    continue
                old_stage_id = task.stage_id.id if task.stage_id else None
                new_stage_id = vals['stage_id']
                if old_stage_id == new_stage_id:
                    continue

                global_duration, global_history = self.env['project.project']._get_global_duration_settings()
                duration_on = task.project_id.task_stage_duration_enabled or global_duration
                history_on = task.project_id.stage_history_enabled or global_history

                # Close current open history line
                open_history = History.search([
                    ('task_id', '=', task.id),
                    ('stage_out', '=', False),
                ], limit=1)
                if open_history:
                    if history_on:
                        open_history.write({'stage_out': now})

                # Only create new record if new stage should be tracked
                if new_stage_id and task._should_track_stage(new_stage_id):
                    History.create({
                        'task_id': task.id,
                        'stage_id': new_stage_id,
                        'from_stage_id': old_stage_id if duration_on else False,
                        'stage_in': now,
                        'user_id': self.env.user.id,
                    })
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        History = self.env['project.task.stage.history'].sudo()
        for task in tasks:
            if not task.stage_id or not task._project_tracking_enabled():
                continue
            if not task._should_track_stage(task.stage_id.id):
                continue
            History.create({
                'task_id': task.id,
                'stage_id': task.stage_id.id,
                'from_stage_id': False,
                'stage_in': fields.Datetime.now(),
                'user_id': self.env.user.id,
            })
        return tasks