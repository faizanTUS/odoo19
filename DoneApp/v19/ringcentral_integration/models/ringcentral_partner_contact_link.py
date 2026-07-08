# -*- coding: utf-8 -*-
from odoo import fields, models


class RingCentralPartnerContactLink(models.Model):
    _name = 'ringcentral.partner.contact.link'
    _description = 'RingCentral Partner Contact Link'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        required=True,
        ondelete='cascade',
        index=True,
    )
    config_id = fields.Many2one(
        'ringcentral.config',
        string='RingCentral Configuration',
        required=True,
        ondelete='cascade',
        index=True,
    )
    ringcentral_contact_id = fields.Char(
        string='RingCentral Contact ID',
        required=True,
        index=True,
    )

    _partner_config_unique = models.Constraint(
        'unique(partner_id, config_id)',
        'Each contact may only be linked once per RingCentral configuration.',
    )
