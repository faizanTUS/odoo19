# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.mail.tools.discuss import Store

class MailThreadExt(models.AbstractModel):
    _inherit = "mail.thread"

    def _thread_to_store(self, store: Store, /, *, request_list=None, **kwargs):
        super()._thread_to_store(store, request_list=request_list, **kwargs)
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)], limit=1).id
        DisableSendMessageBtn = False if model_id in self.env.user.not_send_msgs_btn_in_chatter.mapped('id') else True
        if request_list:
            store.add(
                self,
                {"DisableSendMessageBtn": DisableSendMessageBtn},
                as_thread=True,
            )
