# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import random
import string


class PosCategory(models.Model):
    _inherit = 'res.partner'

    membership_level = fields.Selection(selection=[('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum')], string='Membership Level')
    member_loyalty_point = fields.Float(string='Member Loyalty Point')
    total_loyalty_point = fields.Float(compute='total_loyalty_point_cal')
    partner_loyalty_ids = fields.One2many('loyalty.card', 'partner_id',
                                          domain=[('program_id.program_type', '=', 'loyalty'), '|',
                                                  ('expiration_date', '>=', fields.Date.today()),
                                                  ('expiration_date', '=', False)])

    generate_unique_ref_code = fields.Char(string="Referral Code", readonly=True, copy=False)
    ref_by_code = fields.Char(string="Referral By")
    ref_by_partner_id = fields.Many2one('res.partner', string="Referral By")
    points = fields.Integer(string='Points')
    referral_by_code = fields.Char(string="Referral By Code")

    def _get_referrer_from_code(self, referral_code):
        if not referral_code:
            return self.env['res.partner']
        return self.env['res.partner'].search(
            [('generate_unique_ref_code', '=', referral_code)],
            limit=1
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('referral_by_code') and not vals.get('ref_by_partner_id'):
                referrer = self._get_referrer_from_code(vals.get('referral_by_code'))
                if referrer:
                    vals['ref_by_partner_id'] = referrer.id

        partners = super().create(vals_list)

        template = self.env.ref(
            'pos_refer_customer_and_earn_loyalty_point.email_template_generate_referral_code',
            raise_if_not_found=False
        )

        for vals, partner in zip(vals_list, partners):
            if not partner.generate_unique_ref_code:
                partner.generate_unique_ref_code = partner._generate_unique_random_sequence()

            if template and partner.email:
                template.sudo().send_mail(
                    partner.id,
                    force_send=True,
                    email_values={'email_to': partner.email}
                )

        return partners

    def write(self, vals):
        if vals.get('referral_by_code') and not vals.get('ref_by_partner_id'):
            referrer = self._get_referrer_from_code(vals.get('referral_by_code'))
            vals['ref_by_partner_id'] = referrer.id if referrer else False
        elif 'referral_by_code' in vals and not vals.get('referral_by_code'):
            vals['ref_by_partner_id'] = False
        return super().write(vals)

    def _generate_unique_random_sequence(self, length=8):
        while True:
            random_sequence = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not self.env['res.partner'].search([('generate_unique_ref_code', '=', random_sequence)]):
                return random_sequence

    @api.constrains('mobile', 'email')
    def _check_mobile_and_email_is_exists(self):
        for partner in self:
            all_mobile_no = self.search([('mobile', '=', partner.mobile)])
            print(all_mobile_no)
            all_email_add = self.search([('email', '=', partner.email)])
            if len(all_mobile_no) > 1:
                raise ValidationError(
                    _("This Mobile Number is already registered , Please use a different Mobile Number"))
            if len(all_email_add) > 1:
                raise ValidationError(_("This Email is already registered , Please use a different Email Address"))

    @api.depends("partner_loyalty_ids", "partner_loyalty_ids.points")
    def total_loyalty_point_cal(self):
        for rec in self:
            rec.total_loyalty_point = sum(rec.partner_loyalty_ids.mapped('points'))
