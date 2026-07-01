from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_mail_thread_data(self, request_list):
        res = super(MailThread, self)._get_mail_thread_data(request_list)
        res[
            "not_send_msgs_btn_in_chatter"
        ] = self.env.user.not_send_msgs_btn_in_chatter.mapped("model")
        return res
