# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import models, fields, api
class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _check_loyalty_birthday_rewards(self, customer_id, coupon_code):
        """Validate birthday reward redemption."""
        if not customer_id or not coupon_code:
            return False

        coupon = self.env['loyalty.card'].search([
            ('code', '=', coupon_code),
            ('partner_id', '=', customer_id),
            ('program_id.is_birthday_program', '=', True)
        ], limit=1)

        if not coupon:
            return False

        # Check if coupon is still valid
        if coupon.expiration_date and coupon.expiration_date < fields.Date.today():
            return False

        return True