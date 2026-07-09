# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, _


class ProjectTaskWorksheet(models.Model):
    _name = 'project.task.worksheet'
    _description = 'Project Task Worksheet'

    name = fields.Char(string="Name")
    task_id = fields.Many2one('project.task', string='Task')
    manufacturer = fields.Many2one('res.partner', string="Manufacturer")
    model = fields.Many2one('product.product', string="Model")
    serial_number = fields.Char(string="Serial Number")
    intervention_type = fields.Selection([
        ('first_installation', 'First Installation'), 
        ('technical_maintenance', 'Technical Maintenance')], 
        string="Serial Number")
    description = fields.Text(string="Description")
    checkbox = fields.Boolean(string="I hereby certify that this device meets the \
        requirements of an acceptable device at the time of testing.")
    date = fields.Date(string="Date")
    worker_signature = fields.Binary(string="Worker Signature")


class Task(models.Model):
    _inherit = 'project.task'

    project_task_worksheet_ids = fields.One2many('project.task.worksheet', 'task_id', string="Worksheet")
