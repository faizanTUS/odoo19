# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.mail.tools.discuss import add_guest_to_context
from odoo.addons.mail.tools.discuss import Store
from odoo.addons.mail.controllers.webclient import WebclientController
from odoo.osv import expression
from odoo import fields

class DiscussChannelWebclientController(WebclientController):
    def _process_request_for_all(self, store: Store, name, **kwargs):
        if "init_messaging" in kwargs:
            if not request.env.user._is_public():
                user = request.env.user.sudo(False)
                user._init_messaging(store)
            member_domain = [
                ("is_self", "=", True),
                "|",
                ("fold_state", "in", ("open", "folded")),
                ("rtc_inviting_session_id", "!=", False),
            ]
            channels_domain = [("channel_member_ids", "any", member_domain)]
            channel_types = kwargs["init_messaging"].get("channel_types")
            if channel_types:
                channels_domain = expression.AND(
                    [channels_domain, [("channel_type", "in", channel_types)]]
                )
            store.add(request.env["discuss.channel"].search(channels_domain))

WebclientController._process_request_for_all = DiscussChannelWebclientController._process_request_for_all

class WebsitePortalChatController(http.Controller):

    # @http.route('/website_portal_chat/init', type='json', auth="public")
    # @add_guest_to_context
    # def livechat_init(self):
    #     store = Store()
    #     request.env["res.users"]._init_store_data(store)
    #     return {
    #         'storeData': store.get_result(),
    #     }

    @http.route('/website_portal_chat/init', type='json', auth="public")
    @add_guest_to_context
    def livechat_init(self):
        store = Store()
        request.env["res.users"]._init_store_data(store)

        if not request.env.user._is_public():
            member_domain = [
                ('is_self', '=', True),
            ]
            channels_domain = [('channel_member_ids', 'any', member_domain)]
            channels = request.env['discuss.channel'].search(channels_domain)
            store.add(channels)

        return {
            'storeData': store.get_result(),
        }

    @http.route('/website_portal_chat/search_partners', type='json', auth="user")
    def search_partners(self, term):
        is_portal_viewer = request.env.user.share

        base_domain = [
            ('id', '!=', request.env.user.id),
            ('name', 'ilike', term),
            ('active', '=', True),
        ]

        if is_portal_viewer:
            user_domain = base_domain + ['|',
                                         ('share', '=', True),  # portal ↔ portal
                                         '&',
                                         ('share', '=', False),  # internal user
                                         ('can_message', '=', True), ]
        else:
            user_domain = base_domain + ([
                '|',
                ('share', '=', False),
                ('can_message', '=', True)
            ])
        users = request.env['res.users'].sudo().search(user_domain, limit=20)

        partners_data = []
        for user in users:
            partner = user.partner_id
            partners_data.append({
                'id': partner.id,
                'name': partner.name,
                'im_status': partner.im_status,
                'avatar_url': f"/web/image/res.partner/{partner.id}/avatar_128"
            })
        return partners_data

    # @http.route('/website_portal_chat/get_thread_with_partner', type='json', auth="user")
    # def get_thread_with_partner(self, partner_id):
    #     partner = request.env['res.partner'].browse(partner_id)
    #     if not partner.exists():
    #         return False
    #     channel = request.env['discuss.channel'].sudo(False)._get_or_create_chat([partner_id])
    #     store = Store()
    #     store.add(channel)
    #     return store.get_result()

    @http.route('/website_portal_chat/get_thread_with_partner', type='json', auth="user")
    def get_thread_with_partner(self, partner_id):
        partner = request.env['res.partner'].browse(partner_id)
        if not partner.exists():
            return False

        channel = request.env['discuss.channel'].sudo(False)._get_or_create_chat([partner_id])

        target_member = channel.sudo().channel_member_ids.filtered(
            lambda m: m.partner_id.id == partner_id
        )
        if target_member:
            store = Store()
            store.add(channel)
            channel_data = store.get_result()

            request.env['bus.bus'].sudo()._sendone(
                partner,
                'mail.record/insert',
                channel_data,
            )

            request.env['bus.bus'].sudo()._sendone(
                partner,
                'discuss.channel/joined',
                {
                    'channel': {
                        'id': channel.id,
                        'model': 'discuss.channel',
                    },
                    'invited_by_user_id': request.env.user.id,
                }
            )

        store = Store()
        store.add(channel)
        return store.get_result()

