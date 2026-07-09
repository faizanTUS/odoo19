from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_orderline_user = fields.Boolean()
    cashier_ids = fields.Many2many("hr.employee", "pos_config_hr_employee_rel", string="Cashier")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allow_orderline_user = fields.Boolean(related='pos_config_id.allow_orderline_user')
    cashier_ids = fields.Many2many("hr.employee",related='pos_config_id.cashier_ids', string="Cashier")
