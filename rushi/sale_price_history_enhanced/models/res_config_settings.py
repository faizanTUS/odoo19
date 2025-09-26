# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    item_limit = fields.Integer(string='Sales Price History Limit', default=10, config_parameter='sale_price_history.item_limit')
    filter_confirmed = fields.Boolean(string='Show Confirm Sales Orders', config_parameter='sale_price_history.filter_confirmed')
    filter_sent = fields.Boolean(string='Show Quotation sent Sales Orders', config_parameter='sale_price_history.filter_sent')
    filter_draft = fields.Boolean(string='Show Draft Sales Orders', config_parameter='sale_price_history.filter_draft')