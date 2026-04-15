# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_quick_task_project_id = fields.Many2one(
        comodel_name='project.project',
        string='Quick Task Default Project',
        help='Default project for Quick Tasks when no project is set on the Sales Team or Lead/Opportunity.',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_crm_quick_task_project',
        inverse='_inverse_crm_quick_task_project',
    )

    @api.depends('company_id')
    def _compute_crm_quick_task_project(self):
        for setting in self:
            param = self.env['ir.config_parameter'].sudo().get_param(
                'crm_quick_task_advanced.default_project_id', ''
            )
            if param:
                try:
                    setting.crm_quick_task_project_id = int(param)
                except (ValueError, TypeError):
                    setting.crm_quick_task_project_id = False
            else:
                setting.crm_quick_task_project_id = False

    def _inverse_crm_quick_task_project(self):
        for setting in self:
            self.env['ir.config_parameter'].sudo().set_param(
                'crm_quick_task_advanced.default_project_id',
                str(setting.crm_quick_task_project_id.id) if setting.crm_quick_task_project_id else '',
            )

    @api.model
    def get_quick_task_default_project(self, company):
        """Return the default project for Quick Task for the given company (from settings or first available)."""
        param = self.env['ir.config_parameter'].sudo().get_param('crm_quick_task_advanced.default_project_id', '')
        if param:
            try:
                project_id = int(param)
                project = self.env['project.project'].sudo().browse(project_id).exists()
                if project and (not project.company_id or project.company_id == company):
                    return project
            except (ValueError, TypeError):
                pass
        # Fallback: first project of the company
        return self.env['project.project'].sudo().search([
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
