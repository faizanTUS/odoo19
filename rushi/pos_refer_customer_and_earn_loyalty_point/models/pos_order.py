# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _process_order(self, order, existing_order):
        customer_id = order.get('partner_id')
        if not customer_id:
            return super(PosOrder, self)._process_order(order, existing_order)
        customer = self.env['res.partner'].browse(customer_id)
        if not customer:
            return super(PosOrder, self)._process_order(order, existing_order)

        referrer = customer.ref_by_partner_id
        if referrer:
            referrer_card = self.env['loyalty.card'].search([('partner_id', '=', referrer.id)], limit=1)
            if referrer_card:
                existing_referral = self.env['loyalty.referral'].search([
                    ('referral_card_id', '=', referrer_card.id),
                    ('referred_partner_id', '=', customer.id)
                ], limit=1)

                reward_points = self.env.company.referral_reward_points
                if not existing_referral:
                    referrer_card.points += reward_points

                    self.env['loyalty.referral'].create({
                        'referral_card_id': referrer_card.id,
                        'referred_partner_id': customer.id,
                        'points_earned': reward_points,
                    })
                    if customer.referral_by_code == referrer.generate_unique_ref_code:
                        customer.write({'points': reward_points})
                    template = self.env.ref('pos_refer_customer_and_earn_loyalty_point.email_template_earn_loyalty_points',
                                            raise_if_not_found=False)
                    if template:
                        template.sudo().with_context(referrer=referrer.name, points_earned=reward_points,
                                                     total_points=referrer_card.points).send_mail(self.id, force_send=True,
                                                                                                  email_values={
                                                                                                  'email_to': referrer.email})
            if not referrer_card:
                loyalty_program = self.env['loyalty.program'].search([
                    ('program_type', '=', 'loyalty')
                ])
                # points added
                reward_points = self.env.company.referral_reward_points
                referrer.total_loyalty_point += reward_points
                total_loyalty_points = referrer.total_loyalty_point
                # create loyalty card
                self.env['loyalty.card'].create({
                    'partner_id': referrer.id,
                    'program_id': loyalty_program.id,
                    'points_display': referrer.total_loyalty_point,
                    'points': total_loyalty_points,
                })
                if customer.referral_by_code == referrer.generate_unique_ref_code:
                    customer.write({'points': reward_points})
                # send email
                template = self.env.ref('pos_refer_customer_and_earn_loyalty_point.email_template_earn_loyalty_points',
                                        raise_if_not_found=False)
                if template:
                    template.sudo().with_context(referrer=referrer.name, points_earned=reward_points,
                                                 total_points=total_loyalty_points).send_mail(self.id, force_send=True,
                                                                                              email_values={
                                                                                                  'email_to': referrer.email})
        return super(PosOrder, self)._process_order(order, existing_order)
