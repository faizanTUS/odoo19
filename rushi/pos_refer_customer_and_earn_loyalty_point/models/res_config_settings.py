# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    referral_reward_points = fields.Integer(related='company_id.referral_reward_points', readonly=False,string='Referral Reward Points')
