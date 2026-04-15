# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='lead_id',
        string='Tasks',
        help='Tasks created from this Lead/Opportunity (Quick Task).',
    )
    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
        store=False,
    )
    quick_task_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Quick Task Default Project',
        help='Override the default project when creating a Quick Task from this lead. '
             'If empty, the Sales Team default or company default is used.',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        for lead in self:
            lead.task_count = len(lead.task_ids)

    def _get_quick_task_project(self):
        """Resolve project for Quick Task: lead override > team default > company default."""
        self.ensure_one()
        if self.quick_task_project_id:
            return self.quick_task_project_id
        if self.team_id and self.team_id.quick_task_project_id:
            return self.team_id.quick_task_project_id
        company = self.company_id or self.env.company
        return self.env['res.config.settings'].sudo().get_quick_task_default_project(company)

    def _get_quick_task_project_tags(self, project=None):
        """Map CRM tags to Project tags by name (find or create by name)."""
        self.ensure_one()
        if not self.tag_ids:
            return self.env['project.tags']
        ProjectTags = self.env['project.tags'].sudo()
        project_tag_ids = []
        for crm_tag in self.tag_ids:
            existing = ProjectTags.search([('name', '=ilike', crm_tag.name)], limit=1)
            if existing:
                project_tag_ids.append(existing.id)
            else:
                tag_id, _ = ProjectTags.name_create(crm_tag.name)
                project_tag_ids.append(tag_id)
        return ProjectTags.browse(project_tag_ids)

    def action_open_quick_task(self):
        """Open Create Task form with defaults from this lead/opportunity."""
        self.ensure_one()
        project = self._get_quick_task_project()
        if not project:
            raise UserError(_(
                'No default project set for Quick Task. '
                'Please set a default project in Sales & CRM settings, '
                'or on the Sales Team, or on this Lead/Opportunity.'
            ))
        project_tags = self._get_quick_task_project_tags(project)
        return {
            'name': _('Create Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_project_id': project.id,
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_user_ids': [(6, 0, (self.user_id.ids if self.user_id else []))],
                'default_tag_ids': [(6, 0, project_tags.ids)],
                'default_description': self.description if self.description else False,
                'form_view_initial_mode': 'edit',
            },
        }

    def action_view_tasks(self):
        """Open list of tasks linked to this lead."""
        self.ensure_one()
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id, 'default_project_id': self._get_quick_task_project().id},
        }
