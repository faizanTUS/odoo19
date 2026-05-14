# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-

from odoo import fields, models


class EmployeeImageExportLog(models.Model):
    _name = "employee.image.export.log"
    _description = "Employee Image Export Log"
    _order = "create_date desc"

    name = fields.Char(string="Description", required=True)
    user_id = fields.Many2one("res.users", string="Exported By", default=lambda self: self.env.user, readonly=True)
    export_datetime = fields.Datetime(string="Export Datetime", default=fields.Datetime.now, readonly=True)
    employee_count = fields.Integer(string="Employees Exported", readonly=True)
    file_size = fields.Integer(string="Zip Size (bytes)", readonly=True)
    params_summary = fields.Text(string="Parameters Summary", readonly=True)
