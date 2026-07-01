# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from calendar import monthrange


class LoyaltyGenerateWizard(models.TransientModel):
    _inherit = 'loyalty.generate.wizard'

    generate_birthday_rewards = fields.Boolean(
        string='Generate Birthday Rewards',
        help='Generate birthday reward coupons for eligible customers'
    )

    @api.model
    def _cron_generate_birthday_rewards(self):
        """Monthly cron job to generate birthday rewards."""
        # Find all birthday reward programs

        date = fields.Date.today()

        domain = [
            ('birthdate', '!=', False),
            ('email', '!=', False),
            ('active', '=', True)
        ]

        partners = self.env['res.partner'].search(domain)

        # Filter partners with birthdays in the given month
        birthday_partners = partners.filtered(lambda p:
                                              fields.Date.from_string(p.birthdate).month == date.month)
        birthday_programs = self.env['loyalty.program'].search([
            ('is_birthday_program', '=', True),
            ('active', '=', True)
        ],limit=1)

        for partner in birthday_partners:
            for program in birthday_programs:
                # Create wizard for each program
                loyalty_program = self.env['loyalty.card'].search([('partner_id','=',partner.id),('program_id','=',program.id)])
                lp = loyalty_program.filtered(lambda p:fields.Date.from_string(p.partner_id.birthdate).month == date.month and fields.Date.from_string(p.create_date).year == date.year)
                if not lp:
                    wizard = self.create({
                        'program_id': program.id,
                        'mode': 'selected',
                        'generate_birthday_rewards': True,
                        'points_granted': 1,
                        'customer_ids': partner.ids,
                        'valid_until': (datetime.now() + relativedelta(day=31)).date(),
                    })

                # Generate coupons
                    wizard.generate_coupons()

    def action_view_birthday_rewards(self):
        """Action to view generated birthday rewards."""
        self.ensure_one()
        return {
            'name': 'Birthday Rewards',
            'type': 'ir.actions.act_window',
            'res_model': 'loyalty.card',
            'view_mode': 'tree,form',
            'domain': [
                ('program_id', '=', self.program_id.id),
                ('create_date', '>=', fields.Date.today()),
                ('partner_id', '!=', False)
            ],
            'context': {'create': False}
        }


    @api.depends('generate_birthday_rewards', 'customer_ids', 'customer_tag_ids', 'mode')
    def _compute_coupon_qty(self):
        super()._compute_coupon_qty()
        for wizard in self:
            if wizard.generate_birthday_rewards:
                eligible_partners = wizard._get_birthday_eligible_partners()
                wizard.coupon_qty = len(eligible_partners)

    def _get_birthday_eligible_partners(self):
        """Get partners whose birthdays fall in the current month."""
        self.ensure_one()
        current_date = fields.Date.today()
        domain = [
            ('birthdate', '!=', False),
            ('birthdate', '!=', None),
            ('email', '!=', False),  # Ensure we can send email notifications
        ]

        # Add customer filters if specified
        if self.customer_ids:
            domain.append(('id', 'in', self.customer_ids.ids))
        if self.customer_tag_ids:
            domain.append(('category_id', 'in', self.customer_tag_ids.ids))

        partners = self.env['res.partner'].search(domain)

        # Filter partners whose birthday is in the current month
        return partners.filtered(lambda p:
                                 fields.Date.from_string(p.birthdate).month == current_date.month)

    def _get_coupon_values(self, partner):
        values = super()._get_coupon_values(partner)
        if self.generate_birthday_rewards:
            current_year = fields.Date.today().year
            birthday_this_year = fields.Date.from_string(partner.birthdate).replace(year=current_year)
            expiration_date = birthday_this_year + relativedelta(days=30)
            values.update({
                'expiration_date':expiration_date,
                'partner_id': partner.id,
            })
        return values

    def _generate_birthday_code(self, partner):
        """Generate a unique birthday reward code."""
        prefix = 'BDAY'
        year = fields.Date.today().year
        sequence = self.env['ir.sequence'].next_by_code('loyalty.birthday.code')
        return f"{prefix}{year}{sequence}"

    def generate_coupons(self):
        res = super(LoyaltyGenerateWizard,self).generate_coupons()
        if self.generate_birthday_rewards:
            self._send_birthday_notifications()
        return res

    def _send_birthday_notifications(self):
        """Send birthday greeting emails with coupon codes."""
        template = self.env.ref('pos_loyalty_birthday_reward.email_template_birthday_reward', raise_if_not_found=False)
        if not template:
            return

        coupons = self.env['loyalty.card'].search([
            ('program_id', '=', self.program_id.id),
            ('create_date', '>=', fields.Datetime.now().replace(hour=0, minute=0, second=0)),
            ('partner_id', '!=', False)
        ])

        for coupon in coupons:
            template.send_mail(
                coupon.id,
                force_send=True,
                email_values={'email_to': coupon.partner_id.email}
            )