# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, models


def _config_param_truthy(icp, key, default='False'):
    """Interpret ir.config_parameter values as booleans (stored as strings)."""
    return str(icp.get_param(key, default) or default).lower() in ('1', 'true', 'yes')


def _routing_user(record_model_self):
    if 'uid' in record_model_self._context:
        return record_model_self.env['res.users'].browse(record_model_self._context.get('uid'))
    if record_model_self.env.user:
        return record_model_self.env.user
    return False


class Mail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, vals_list):
        icp = self.env['ir.config_parameter'].sudo()
        smtp_by_company = _config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_company')
        smtp_by_user = _config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_user')

        if not (smtp_by_company or smtp_by_user):
            return super().create(vals_list)

        for vals in vals_list:
            user = _routing_user(self)
            active_company_id = self.env.company.id if self.env.company else 0

            out_mail_server = False
            if smtp_by_company and smtp_by_user and user:
                out_mail_server = self.env['ir.mail_server'].search(
                    [('company_ids', '=', active_company_id), ('user_ids', 'in', [user.id])],
                    limit=1,
                )
            elif smtp_by_company and active_company_id:
                out_mail_server = self.env['ir.mail_server'].search(
                    [('company_ids', '=', active_company_id)],
                    limit=1,
                )
            elif smtp_by_user and user:
                out_mail_server = self.env['ir.mail_server'].search(
                    [('user_ids', 'in', [user.id])],
                    limit=1,
                )

            if not out_mail_server:
                continue

            vals['mail_server_id'] = out_mail_server.id

            active_u_user = out_mail_server.smtp_user or ''
            if active_u_user and user:
                partner = user.partner_id
                active_u_name = partner.name or ''
                active_u_email = partner.email or ''
                email_from = '%s <%s>' % (active_u_name, active_u_user)
                reply_addr = active_u_email or active_u_user
                reply_to = '%s <%s>' % (active_u_name, reply_addr) if reply_addr else email_from
                vals.update({'email_from': email_from, 'reply_to': reply_to})

        return super().create(vals_list)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        icp = self.env['ir.config_parameter'].sudo()
        smtp_by_company = _config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_company')
        smtp_by_user = _config_param_truthy(icp, 'send_mail_company_wish_ext.smtp_by_user')

        for vals in vals_list:
            user = _routing_user(self)
            if not user:
                continue

            active_company_id = self.env.company.id if self.env.company else 0

            if smtp_by_company and smtp_by_user:
                mail_server = self.env['ir.mail_server'].sudo().search(
                    [
                        ('user_ids', 'in', [user.id]),
                        ('company_ids', 'in', [active_company_id]),
                    ],
                    limit=1,
                )
                if mail_server:
                    vals['mail_server_id'] = mail_server.id
            elif smtp_by_company:
                mail_server = self.env['ir.mail_server'].sudo().search(
                    [('is_smtp_by_company', '=', True)],
                    limit=1,
                )
                if mail_server:
                    candidates = self.env['ir.mail_server'].sudo().search([])
                    for candidate in candidates:
                        if active_company_id in candidate.company_ids.ids:
                            vals['mail_server_id'] = candidate.id
                            break
            else:
                out_mail_server = self.env['ir.mail_server'].sudo().search(
                    [('user_ids', 'in', [user.id])],
                    limit=1,
                )
                if out_mail_server:
                    vals['mail_server_id'] = out_mail_server.id

        return super().create(vals_list)
