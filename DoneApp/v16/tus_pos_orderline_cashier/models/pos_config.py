# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    allow_orderline_user = fields.Boolean()
    cashier_ids = fields.Many2many(
        "hr.employee", "pos_config_hr_employee_rel", string="Cashier"
    )
