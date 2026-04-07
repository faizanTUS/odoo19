# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_post(self, *, body='', message_type='notification', **kwargs):
        """
        When a global default font family is configured in Settings → Emails,
        wrap the message body with that font-family style so that both the
        chatter display and the received email render in the configured font.

        Applied to 'comment' (Send Message / Log Note) and 'email_outgoing'
        (Send Email popup dialog) message types.
        System notifications and auto-emails are not affected.

        Note: If the user manually selected a font via the editor toolbar
        (FontFamilyPlugin), the body already contains font-family inline styles
        on the selected text; the outer wrapper simply provides a fallback for
        any un-styled text in the same message.

        Implementation note — f-string instead of Markup.format():
        Markup.format() HTML-escapes string arguments, so CSS single-quotes
        like  'Courier New'  become  &#39;Courier New&#39;  which many
        email-client CSS parsers reject.  font_family comes from
        ir.config_parameter (admin-controlled, trusted), so direct embedding
        via f-string is safe here.
        """
        if message_type in ('comment', 'email_outgoing') and body:
            font_family = (
                self.env['ir.config_parameter'].sudo().get_param('mail_font_config.font_family', '')
            )
            if font_family:
                # Always wrap — do NOT check for existing font-family in body.
                # The popup email body includes the user's signature which often
                # contains font-family styles; the old check caused the wrap to
                # be skipped entirely, so the chatter showed regular font.
                # Wrapping unconditionally is safe: inner elements that already
                # have explicit font-family (signature, toolbar selection) keep
                # their own font via CSS specificity — the outer div just sets
                # the default for bare text.
                body_markup = body if isinstance(body, Markup) else Markup(str(body))
                body = Markup(
                    f'<div style="font-family:{font_family};">'
                    f'{body_markup}'
                    f'</div>'
                )

        return super().message_post(body=body, message_type=message_type, **kwargs)
