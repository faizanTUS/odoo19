# Part of Odoo.See COPYRIGHT & LICENSE files for full copyright and licensing details.

from . import models
from odoo import api, SUPERUSER_ID

def _generate_referral_code(env):
    partners = env['res.partner'].search([])
    for partner in partners:
        partner.generate_unique_ref_code = env['res.partner']._generate_unique_random_sequence()

