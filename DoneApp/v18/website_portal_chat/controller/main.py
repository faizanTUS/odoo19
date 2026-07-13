# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.addons.mail.tools.discuss import Store
from odoo.addons.mail.controllers.webclient import WebclientController
from odoo.osv import expression

class DiscussChannelWebclientController(WebclientController):
    def _process_request_for_all(self, store, **kwargs):
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

    @http.route('/website_portal_chat/init', type='json', auth="public")
    @add_guest_to_context
    def livechat_init(self):
        store = Store()
        request.env["res.users"]._init_store_data(store)
        return {
            'storeData': store.get_result(),
        }