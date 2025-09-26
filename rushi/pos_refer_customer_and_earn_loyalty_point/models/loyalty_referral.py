# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api

class LoyaltyReferral(models.Model):
    _name = 'loyalty.referral'
    _description = 'Loyalty Referral'

    referral_card_id = fields.Many2one('loyalty.card', string='Referring Card')
    referred_card_id = fields.Many2one('loyalty.card', string='Referred Card')
    points_earned = fields.Integer(string='Points Earned')
    referred_partner_id = fields.Many2one('res.partner', string="Referred Customer", required=True)
