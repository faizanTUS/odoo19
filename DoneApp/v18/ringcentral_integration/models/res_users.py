# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    ringcentral_extension = fields.Char(
        string='RingCentral Extension',
        help='Your personal RingCentral extension number. Leave empty to use the default extension from configuration.',
        groups='base.group_user'
    )

    @property
    def SELF_READABLE_FIELDS(self):
        """Add ringcentral_extension to self-readable fields"""
        return super().SELF_READABLE_FIELDS + ['ringcentral_extension']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Add ringcentral_extension to self-writable fields"""
        return super().SELF_WRITEABLE_FIELDS + ['ringcentral_extension']

    def get_ringcentral_extension(self):
        """Get the extension for this user"""
        self.ensure_one()
        return self.ringcentral_extension or ''

