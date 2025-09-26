# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)


class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    last_activity_date = fields.Date(string='Last Activity Date')
    referral_code = fields.Char(related='partner_id.generate_unique_ref_code',string='Referral Code')
    ref_by_partner_id = fields.Many2one(related='partner_id.ref_by_partner_id', string="Referral By")
    loyalty_referral_id = fields.Many2one('loyalty.referral')
    referral_count = fields.Integer(string='Referral Count', compute='_compute_referral_count')


    def _compute_referral_count(self):
        for record in self:
            record.referral_count = self.env['res.partner'].search_count(
                [('ref_by_partner_id', '=', record.partner_id.id)])

    def loyalty_referral(self):
        return {
            'name': 'Loyalty Referral',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list',
            'target': 'current',
            'domain': [('ref_by_partner_id', '=', self.partner_id.id)],
        }
