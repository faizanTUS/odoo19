# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    ringcentral_extension = fields.Char(
        string='RingCentral Extension Number',
        help='Your RingCentral desk phone or softphone extension (e.g. 101). '
             'Required to map inbound/outbound calls to your Odoo user in call history.',
        groups='base.group_user'
    )
    ringcentral_extension_id = fields.Char(
        string='RingCentral Extension ID',
        help='Numeric RingCentral extension ID from webhook payloads (optional).',
        groups='base.group_user'
    )

    @property
    def SELF_READABLE_FIELDS(self):
        """Add ringcentral_extension to self-readable fields"""
        return super().SELF_READABLE_FIELDS + ['ringcentral_extension', 'ringcentral_extension_id']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Add ringcentral_extension to self-writable fields"""
        return super().SELF_WRITEABLE_FIELDS + ['ringcentral_extension', 'ringcentral_extension_id']

    def get_ringcentral_extension(self):
        """Get the extension for this user"""
        self.ensure_one()
        return self.ringcentral_extension or ''

    def has_ringcentral_access(self):
        """Return True when the user belongs to a RingCentral security group."""
        self.ensure_one()
        return self.has_group('ringcentral_integration.group_ringcentral_admin') or self.has_group(
            'ringcentral_integration.group_ringcentral_user'
        )

    def is_ringcentral_admin(self):
        """Return True when the user is a RingCentral administrator."""
        self.ensure_one()
        return self.has_group('ringcentral_integration.group_ringcentral_admin') or self.has_group(
            'base.group_system'
        )

    @api.model
    def get_ringcentral_session_info(self):
        """Session payload for frontend access gating."""
        user = self.env.user
        has_access = user.has_ringcentral_access()
        is_admin = user.is_ringcentral_admin()
        company = self.env.company
        config = self.env['ringcentral.config'].sudo()._get_company_active_config(company)
        is_connected = bool(config and config.access_token)
        has_config = bool(config and config.client_id)
        return {
            'has_access': has_access,
            'is_admin': is_admin,
            'is_connected': is_connected,
            'has_config': has_config,
            'company_id': company.id,
            'config_id': config.id if config else False,
        }

