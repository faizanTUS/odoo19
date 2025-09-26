# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    referral_reward_points = fields.Integer(string='Referral Reward Points')