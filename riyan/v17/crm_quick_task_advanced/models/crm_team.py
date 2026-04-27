# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    quick_task_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Quick Task Default Project',
        help='Default project used when creating a Quick Task from a Lead/Opportunity of this Sales Team.',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )
