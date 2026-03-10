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

    # def _process_order(self, order, draft, existing_order):
    #     customer = order['data']['partner_id']
    #     if customer:
    #         loyalty_card = self.env['loyalty.card'].search([('partner_id', '=', customer)])
    #         if loyalty_card:
    #             total_points = 0
    #             for line in order['data']['lines']:
    #                 product = self.env['product.product'].browse(line[2]['product_id'])
    #                 if product.pos_categ_ids.is_beverage:
    #                     total_points += 1
    #                 else:
    #                     total_points += line[2]['price_unit'] / average_main_product_price
    #             loyalty_card.write({'points': loyalty_card.points + total_points})
    #
    #     return super()._process_order(order, draft, existing_order)



    # def _process_order(self, order, draft, existing_order):
    #     customer = order['data']['partner_id']
    #     if customer:
    #         loyalty_card = self.env['loyalty.card'].search([('partner_id', '=', customer)], limit=1)
    #         if loyalty_card:
    #             total_points = 0
    #             for line in order['data']['lines']:
    #                 product = self.env['product.product'].browse(line[2]['product_id'])
    #                 # Ensure only one category is considered for beverage check
    #                 beverage_category = product.pos_categ_ids.filtered(lambda c: c.is_beverage == True)
    #                 if beverage_category:
    #                     total_points += 1
    #                 else:
    #                     total_points += line[2]['price_unit'] / average_main_product_price
    #             loyalty_card.write({'points': loyalty_card.points + total_points})
    #
    #     return super()._process_order(order, draft, existing_order)