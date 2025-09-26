# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import random
import string
import logging

_logger = logging.getLogger(__name__)


class PosCategory(models.Model):
    _inherit = 'res.partner'

    membership_level = fields.Selection(selection=[('silver','Silver'),('gold','Gold'),('platinum','Platinum')], string='Membership Level')
    member_loyalty_point = fields.Float(string='Member Loyalty Point')
    total_loyalty_point = fields.Float(compute='total_loyalty_point_cal')
    partner_loyalty_ids = fields.One2many('loyalty.card', 'partner_id',
                                          domain=[('program_id.program_type', '=', 'loyalty'), '|',
                                                  ('expiration_date', '>=', fields.Date.today()),
                                                  ('expiration_date', '=', False)])
    # partner_ids = fields.Many2many('res.partner')
    # ref_code = fields.Char(string='Referral Code',readonly=True, tracking=True, copy=False,
    #                    default=lambda self: self.env['ir.sequence'].next_by_code('loyalty.card.referral'))

    generate_unique_ref_code = fields.Char(string="Referral Code", readonly=True, copy=False)
    ref_by_code = fields.Char(string="Referral By")
    ref_by_partner_id = fields.Many2one('res.partner', string="Referral By")
    points = fields.Integer(string='Points')
    referral_by_code = fields.Char(string="Referral By Code")

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)

        template = self.env.ref(
            'pos_refer_customer_and_earn_loyalty_point.email_template_generate_referral_code',
            raise_if_not_found=False
        )

        for vals, partner in zip(vals_list, partners):
            # Referral code check
            if vals.get('referral_by_code'):
                referrer = self.env['res.partner'].search(
                    [('generate_unique_ref_code', '=', vals.get('referral_by_code'))],
                    limit=1
                )
                if referrer:
                    partner.ref_by_partner_id = referrer.id

            # Generate unique referral code if not set
            if not partner.generate_unique_ref_code:
                partner.generate_unique_ref_code = partner._generate_unique_random_sequence()

            # Send referral email
            if template and partner.email:
                template.sudo().send_mail(
                    partner.id,
                    force_send=True,
                    email_values={'email_to': partner.email}
                )

        return partners

    def _generate_unique_random_sequence(self, length=8):
        while True:
            random_sequence = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not self.env['res.partner'].search([('generate_unique_ref_code', '=', random_sequence)]):
                return random_sequence

    @api.constrains('phone', 'email')
    def _check_mobile_and_email_is_exists(self):
        for partner in self:
            # all_mobile_no = self.search([('mobile', '=', partner.mobile),('email', '=', partner.email)])
            all_mobile_no = self.search([('phone', '=', partner.phone)])
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
    # def _send_generate_referral_code_notifications(self):
    #     """Send referral code greeting emails with referral code."""
    #     template = self.env.ref('pos_refer_customer_and_earn_loyalty_point.email_template_generate_referral_code',
    #                             raise_if_not_found=False)
    #     if template:
    #         template.sudo().send_mail(self.id, force_send=True, )
    #
    # @api.model
    # def _cron_generate_unique_referral_code(self):
    #     domain = [
    #         ('generate_unique_ref_code', '=', False),
    #     ]
    #     partners = self.env['res.partner'].search(domain)
    #     for partner in partners:
    #         partner.generate_unique_ref_code = self._generate_unique_random_sequence()