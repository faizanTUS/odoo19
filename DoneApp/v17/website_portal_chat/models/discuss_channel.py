# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    @api.model
    @api.returns('self', lambda channel: channel._channel_info()[0])
    def channel_get(self, partners_to, pin=True):
        return super(DiscussChannel, self.sudo()).channel_get(partners_to, pin)





