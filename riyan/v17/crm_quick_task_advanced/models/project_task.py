# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Lead/Opportunity',
        index=True,
        copy=False,
        help='Lead or Opportunity from which this task was created (Quick Task).',
    )

    @api.model
    def create(self, vals):
        task = super(ProjectTask, self).create(vals)
        if task.lead_id:
            task.lead_id.message_post(
                body='Task created: <a href="#" data-oe-model="project.task" data-oe-id="%s">%s</a>'
                % (task.id, task.display_name),
            )
        return task
