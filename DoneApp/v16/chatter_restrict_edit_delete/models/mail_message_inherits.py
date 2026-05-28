# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models,api,_

class MessageInherited(models.Model):
    _inherit='mail.message'

    def _message_format(self, fnames, format_reply=True, legacy=False):
        """Override to remove email_from and to return the livechat username if applicable.
        A third param is added to the author_id tuple in this case to be able to differentiate it
        from the normal name in client code.

        In addition, if we are currently running a chatbot.script, we include the information about
        the chatbot.message related to this mail.message.
        This allows the frontend display to include the additional features
        (e.g: Show additional buttons with the available answers for this step). """

        vals_list = super()._message_format(fnames=fnames, format_reply=format_reply, legacy=legacy)
        for vals in vals_list:
            vals.update({
                'showbtn': False if self.env.user.has_group('chatter_restrict_edit_delete.chatter_restrict_edit_delete_group_user') else True
            })
        return vals_list

