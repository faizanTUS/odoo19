# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MaterialRequisitionConfig(models.TransientModel):
    _name = 'material.requisition.config'
    _description = 'Material Requisition Configuration'
    _inherit = 'res.config.settings'

    module_material_requisition_advanced = fields.Boolean(
        string='Material Requisition',
        config_parameter='material_requisition_advanced.module_material_requisition_advanced'
    )
    set_email_notification = fields.Boolean(
        string='Send Email Notifications for Approval',
        config_parameter='material_requisition_advanced.set_email_notification',
        default=True,
    )
    set_department_manager_approval = fields.Boolean(
        string='Require Department Manager Approval',
        config_parameter='material_requisition_advanced.set_department_manager_approval',
        default=True,
    )
    set_requisition_officer_approval = fields.Boolean(
        string='Require Requisition Officer Approval',
        config_parameter='material_requisition_advanced.set_requisition_officer_approval',
        default=True,
    )
