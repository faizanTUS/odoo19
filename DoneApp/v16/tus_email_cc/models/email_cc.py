# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import logging
import threading

from odoo import SUPERUSER_ID,_ , api, fields, models, registry
from odoo.tools.misc import clean_context, split_every

_logger = logging.getLogger(__name__)


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    email_cc = fields.Char(string="Email CC")

    def _send_email(self):
        if self.is_email:
            # with_context : we don't want to reimport the file we just exported.
            self.composer_id.with_context(no_new_invoice=True,
                                          email_cc = self.email_cc,
                                          mail_notify_author=self.env.user.partner_id in self.composer_id.partner_ids,
                                          mailing_document_based=True,
                                          )._action_send_mail()
            if self.env.context.get('mark_invoice_as_sent'):
                #Salesman send posted invoice, without the right to write
                #but they should have the right to change this flag
                self.mapped('invoice_ids').sudo().write({'is_move_sent': True})



class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    email_cc = fields.Char(string="Email CC")

    def get_mail_values(self, res_ids):
        """Override method to link mail automation activity with mail statistics"""
        res = super(MailComposeMessage, self).get_mail_values(res_ids)
        for r in res.keys():
            rec = self.filtered(lambda x: x.res_id == r)
            if rec:
                res[r].update({
                    "email_cc": rec.email_cc or  self._context.get('email_cc') or "",
                })
        return res


class MailThreadInherit(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_thread_by_email(
        self,
        message,
        recipients_data,
        msg_vals=False,
        mail_auto_delete=True,  # mail.mail
        model_description=False,
        force_email_company=False,
        force_email_lang=False,  # rendering
        resend_existing=False,
        force_send=True,
        send_after_commit=True,  # email send
        subtitles=None,
        **kwargs
    ):
        """Method to send email linked to notified messages.

        :param message: ``mail.message`` record to notify;
        :param recipients_data: list of recipients information (based on res.partner
          records), formatted like
            [{'active': partner.active;
              'id': id of the res.partner being recipient to notify;
              'groups': res.group IDs if linked to a user;
              'notif': 'inbox', 'email', 'sms' (SMS App);
              'share': partner.partner_share;
              'type': 'customer', 'portal', 'user;'
             }, {...}].
          See ``MailThread._notify_get_recipients``;
        :param msg_vals: dictionary of values used to create the message. If given it
          may be used to access values related to ``message`` without accessing it
          directly. It lessens query count in some optimized use cases by avoiding
          access message content in db;

        :param mail_auto_delete: delete notification emails once sent;

        :param model_description: model description used in email notification process
          (computed if not given);
        :param force_email_company: see ``_notify_by_email_prepare_rendering_context``;
        :param force_email_lang: see ``_notify_by_email_prepare_rendering_context``;

        :param resend_existing: check for existing notifications to update based on
          mailed recipient, otherwise create new notifications;
        :param force_send: send emails directly instead of using queue;
        :param send_after_commit: if force_send, tells whether to send emails after
          the transaction has been committed using a post-commit hook;
        :param subtitles: optional list that will be set as template value "subtitles"
        """
        partners_data = [r for r in recipients_data if r["notif"] == "email"]
        if not partners_data:
            return True

        model = msg_vals.get("model") if msg_vals else message.model
        model_name = model_description or (
            self.env["ir.model"]._get(model).display_name if model else False
        )  # one query for display name
        recipients_groups_data = self._notify_get_recipients_classify(
            partners_data, model_name, msg_vals=msg_vals
        )

        if not recipients_groups_data:
            return True
        force_send = self.env.context.get("mail_notify_force_send", force_send)

        template_values = self._notify_by_email_prepare_rendering_context(
            message,
            msg_vals=msg_vals,
            model_description=model_description,
            force_email_company=force_email_company,
            force_email_lang=force_email_lang,
        )  # 10 queries
        if subtitles:
            template_values["subtitles"] = subtitles
        email_cc = kwargs.get("email_cc")
        email_to = kwargs.get("email_to")
        if email_cc:
            msg_vals.update({"email_cc": email_cc})
        if email_to:
            msg_vals.update({"email_to": email_to})

        email_layout_xmlid = (
            msg_vals.get("email_layout_xmlid")
            if msg_vals
            else message.email_layout_xmlid
        )
        template_xmlid = (
            email_layout_xmlid
            if email_layout_xmlid
            else "mail.mail_notification_layout"
        )
        base_mail_values = self._notify_by_email_get_base_mail_values(
            message, additional_values={"auto_delete": mail_auto_delete}
        )

        # Clean the context to get rid of residual default_* keys that could cause issues during
        # the mail.mail creation.
        # Example: 'default_state' would refer to the default state of a previously created record
        # from another model that in turns triggers an assignation notification that ends up here.
        # This will lead to a traceback when trying to create a mail.mail with this state value that
        # doesn't exist.
        SafeMail = (
            self.env["mail.mail"].sudo().with_context(clean_context(self._context))
        )
        SafeNotification = (
            self.env["mail.notification"]
            .sudo()
            .with_context(clean_context(self._context))
        )
        emails = self.env["mail.mail"].sudo()

        # loop on groups (customer, portal, user,  ... + model specific like group_sale_salesman)
        notif_create_values = []
        recipients_max = 50
        add_additional_email = False
        add_additional_cc = False

        for recipients_group_data in recipients_groups_data:
            # generate notification email content
            recipients_ids = recipients_group_data.pop("recipients")
            render_values = {**template_values, **recipients_group_data}
            # {company, is_discussion, lang, message, model_description, record, record_name, signature, subtype, tracking_values, website_url}
            # {actions, button_access, has_button_access, recipients}

            mail_body = self.env["ir.qweb"]._render(
                template_xmlid,
                render_values,
                minimal_qcontext=True,
                raise_if_not_found=False,
                lang=template_values["lang"],
            )
            if not mail_body:
                _logger.warning(
                    "QWeb template %s not found or is empty when sending notification emails. Sending without layouting.",
                    template_xmlid,
                )
                mail_body = message.body
            mail_body = self.env["mail.render.mixin"]._replace_local_links(mail_body)

            # create email
            for recipients_ids_chunk in split_every(recipients_max, recipients_ids):
                mail_values = self._notify_by_email_get_final_mail_values(
                    recipients_ids_chunk,
                    base_mail_values,
                    additional_values={"body_html": mail_body},
                )
                if msg_vals and msg_vals.get("email_to") and not add_additional_email:
                    add_additional_email = True
                    mail_values.update(
                        {"additional_email_to": msg_vals.get("email_to")}
                    )
                if msg_vals and msg_vals.get("email_cc") and not add_additional_cc:
                    add_additional_cc = True
                    mail_values.update({"email_cc": msg_vals.get("email_cc")})
                new_email = SafeMail.create(mail_values)
                if new_email and recipients_ids_chunk:
                    tocreate_recipient_ids = list(recipients_ids_chunk)

                    if resend_existing:
                        existing_notifications = (
                            self.env["mail.notification"]
                            .sudo()
                            .search(
                                [
                                    ("mail_message_id", "=", message.id),
                                    ("notification_type", "=", "email"),
                                    ("res_partner_id", "in", tocreate_recipient_ids),
                                ]
                            )
                        )
                        if existing_notifications:
                            tocreate_recipient_ids = [
                                rid
                                for rid in recipients_ids_chunk
                                if rid
                                not in existing_notifications.mapped(
                                    "res_partner_id.id"
                                )
                            ]
                            existing_notifications.write(
                                {
                                    "notification_status": "ready",
                                    "mail_mail_id": new_email.id,
                                }
                            )
                    notif_create_values += [
                        {
                            "author_id": message.author_id.id,
                            "mail_message_id": message.id,
                            "res_partner_id": recipient_id,
                            "notification_type": "email",
                            "mail_mail_id": new_email.id,
                            "is_read": True,  # discard Inbox notification
                            "notification_status": "ready",
                        }
                        for recipient_id in tocreate_recipient_ids
                    ]
                emails += new_email

        if notif_create_values:
            SafeNotification.create(notif_create_values)

        # NOTE:
        #   1. for more than 50 followers, use the queue system
        #   2. do not send emails immediately if the registry is not loaded,
        #      to prevent sending email during a simple update of the database
        #      using the command-line.
        test_mode = getattr(threading.current_thread(), "testing", False)
        if (
            force_send
            and len(emails) < recipients_max
            and (not self.pool._init or test_mode)
        ):
            # unless asked specifically, send emails after the transaction to
            # avoid side effects due to emails being sent while the transaction fails
            if not test_mode and send_after_commit:
                email_ids = emails.ids
                dbname = self.env.cr.dbname
                _context = self._context

                @self.env.cr.postcommit.add
                def send_notifications():
                    db_registry = registry(dbname)
                    with db_registry.cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, _context)
                        env["mail.mail"].browse(email_ids).send()

            else:
                emails.send()

        return True
