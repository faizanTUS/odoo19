# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

RINGCENTRAL_PARTNER_PUSH_FIELDS = frozenset({
    'name', 'email', 'phone', 'function', 'comment', 'street', 'city', 'zip',
    'state_id', 'country_id', 'company_name', 'parent_id', 'ringcentral_config_id',
})


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
    ringcentral_config_id = fields.Many2one(
        'ringcentral.config',
        string='RingCentral Account',
        domain="[('id', 'in', ringcentral_available_config_ids)]",
        help='RingCentral account for this contact when multiple accounts are configured '
             'for the company.',
    )
    ringcentral_available_config_ids = fields.Many2many(
        'ringcentral.config',
        string='Available RingCentral Accounts',
        compute='_compute_ringcentral_available_configs',
        help='Technical field: RingCentral accounts available for this contact, '
             'falling back to the active company when the contact has no company set.',
    )
    ringcentral_multi_config = fields.Boolean(
        string='Multiple RingCentral Accounts',
        compute='_compute_ringcentral_available_configs',
        help='Technical field: true when more than one RingCentral account applies to this contact.',
    )

    @api.depends('company_id')
    def _compute_ringcentral_available_configs(self):
        Config = self.env['ringcentral.config'].sudo()
        for partner in self:
            configs = partner._get_partner_ringcentral_configs()
            partner.ringcentral_available_config_ids = configs
            partner.ringcentral_multi_config = len(configs) > 1

    def _get_partner_ringcentral_companies(self):
        """Companies used to resolve RingCentral configs for this contact.

        Contacts frequently have no ``company_id`` (single-company DBs, public
        contacts, etc.), so fall back to the active companies of the request.
        """
        self.ensure_one()
        if self.company_id:
            return self.company_id
        return self.env.companies or self.env.company

    def _get_partner_ringcentral_configs(self):
        """All active RingCentral configs available for this contact."""
        self.ensure_one()
        Config = self.env['ringcentral.config'].sudo()
        configs = Config.browse()
        for company in self._get_partner_ringcentral_companies():
            configs |= Config._get_company_configs(company)
        return configs

    def _get_partner_ringcentral_config(self):
        """Resolve the RingCentral configuration used to push this contact."""
        self.ensure_one()
        if self.ringcentral_config_id:
            return self.ringcentral_config_id
        configs = self._get_partner_ringcentral_configs()
        if len(configs) == 1:
            return configs
        return self.env['ringcentral.config'].sudo().browse()

    def _ringcentral_push_if_enabled(self):
        if self.env.context.get('ringcentral_skip_push'):
            return
        Sync = self.env['ringcentral.contact.sync'].sudo()
        for partner in self:
            if partner.is_company or not partner.phone:
                continue
            Sync.push_partner_if_enabled(partner)

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._ringcentral_push_if_enabled()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('ringcentral_skip_push'):
            if RINGCENTRAL_PARTNER_PUSH_FIELDS & set(vals):
                self._ringcentral_push_if_enabled()
        return res

    def _compute_ringcentral_calls(self):
        CallHistory = self.env['ringcentral.call.history'].sudo()
        for partner in self:
            partner_ids = self.env['res.partner'].search([('id', 'child_of', partner.id)]).ids
            calls = CallHistory.search([
                '|',
                ('from_partner_id', 'in', partner_ids),
                ('to_partner_id', 'in', partner_ids),
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
        """View all calls for this partner (and children if parent contact)"""
        self.ensure_one()
        partner_ids = self.env['res.partner'].search([('id', 'child_of', self.id)]).ids
        domain = ['|', ('from_partner_id', 'in', partner_ids), ('to_partner_id', 'in', partner_ids)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Call History'),
            'res_model': 'ringcentral.call.history',
            'domain': domain,
            'view_mode': 'list,form',
            'target': 'current',
        }
