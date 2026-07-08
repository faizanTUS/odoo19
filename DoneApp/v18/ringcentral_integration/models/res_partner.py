# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ringcentral_call_count = fields.Integer(string='Call Count', compute='_compute_ringcentral_calls', compute_sudo=True)
    ringcentral_last_call = fields.Datetime(string='Last Call', compute='_compute_ringcentral_calls', compute_sudo=True)
    ringcentral_last_call_direction = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string='Last Call Direction', compute='_compute_ringcentral_calls', compute_sudo=True)
    ringcentral_linked_call_ids = fields.Many2many(
        'ringcentral.call.history',
        string='RingCentral Calls',
        compute='_compute_ringcentral_calls',
        compute_sudo=True,
    )

    def _compute_ringcentral_calls(self):
        CallHistory = self.env['ringcentral.call.history'].sudo()
        for partner in self:
            calls = CallHistory.search([
                '|',
                ('from_partner_id', '=', partner.id),
                ('to_partner_id', '=', partner.id),
            ], order='start_time desc')
            partner.ringcentral_linked_call_ids = calls
            partner.ringcentral_call_count = len(calls)
            if calls:
                latest = calls[0]
                partner.ringcentral_last_call = latest.start_time
                partner.ringcentral_last_call_direction = latest.direction
            else:
                partner.ringcentral_last_call = False
                partner.ringcentral_last_call_direction = False

    def action_view_ringcentral_calls(self):
        """View all calls for this partner"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Call History'),
            'res_model': 'ringcentral.call.history',
            'domain': ['|', ('from_partner_id', '=', self.id), ('to_partner_id', '=', self.id)],
            'view_mode': 'list,form',
            'target': 'current',
        }
